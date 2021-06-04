"""Support for DD-WRT devices."""

from functools import partial
import logging
import voluptuous as vol
from datetime import (
    datetime,
    timedelta,
)

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME,
    ATTR_NAME,
    CONF_HOST,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SSL,
    CONF_VERIFY_SSL,
    CONF_RESOURCES,
)
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import Throttle

from .const import (
    ATTRIBUTION,
    BINARY_SENSORS,
    BINARY_SENSOR_DEFAULTS,
    CAMERAS,
    CAMERA_DEFAULTS,
    COMPONENTS,
    CONF_BINARY_SENSOR,
    CONF_CAMERA,
    CONF_DEVICE_TRACKER,
    CONF_SENSOR,
    CONF_TRACK_ARP,
    CONF_TRACK_DHCP,
    CONF_TRACK_PPPOE,
    CONF_TRACK_PPTP,
    CONF_TRACK_WDS,
    CONF_TRACK_WIRELESS,
    DATA_LISTENER,
    DDWRT_UPNP_MANUFACTURER_URL,
    DEFAULT_DEVICE_NAME,
    DEFAULT_SSL,
    DEFAULT_VERIFY_SSL,
    DEFAULT_WIRELESS_ONLY,
    DEVICE_TRACKERS,
    DEVICE_TRACKER_DEFAULTS,
    DOMAIN,
    MIN_SCAN_INTERVAL,
    RESOURCES,
    RESOURCES_DEFAULTS,
    SCAN_INTERVAL_ABOUT,
    SCAN_INTERVAL_DATA,
    SENSORS,
    SENSOR_DEFAULTS,
    SERVICE_REBOOT,
    SERVICE_RUN_COMMAND,
    SERVICE_UPNP_DELETE,
    SERVICE_WAKE_ON_LAN,
    SERVICE_WAN_DHCP_RELEASE,
    SERVICE_WAN_DHCP_RENEW,
    SERVICE_WAN_PPPOE_CONNECT,
    SERVICE_WAN_PPPOE_DISCONNECT,
    SERVICES,
    TOPIC_DATA_UPDATE,
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_ICON_OFF,
    ATTR_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    ATTR_WIRED,
)
from .pyddwrt import DDWrt

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Optional(CONF_NAME, default=None): vol.Any(cv.string, None),
                        vol.Required(CONF_HOST): cv.string,
                        vol.Optional(CONF_USERNAME, default=""): cv.string,
                        vol.Optional(CONF_PASSWORD, default=""): cv.string,
                        vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
                        vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): cv.boolean,
                        vol.Optional(CONF_RESOURCES, default=RESOURCES_DEFAULTS): vol.All(
                            cv.ensure_list, [vol.In(
                                list(RESOURCES),
                            )]
                        ),
                        vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL_DATA): vol.All(
                            cv.time_period, vol.Clamp(min=MIN_SCAN_INTERVAL)
                        ),
                    },
                ),
            ],
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_SCHEMA = vol.Schema({vol.Optional(CONF_HOST): cv.string})


async def async_setup(hass, config):
    """Set up the DD-WRT component from configuration.yaml: redirect to config_flow.async_import_step"""

    _LOGGER.debug("__init__::async_setup config=%s", config)

    if DOMAIN not in config:
        return True

    # Initiate the config_flow::async_step_import() for each instance
    for router in config[DOMAIN]:
        _LOGGER.debug("__init__::async_setup router=%s", router)
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=dict(router),
            )
        )

    return True

async def async_setup_entry(hass, config_entry):
    """Set up the DD-WRT component from the entity registry or the config_flow"""

    _LOGGER.debug("__init__::async_setup_entry config_entry.data=%s", config_entry.data)

    async def service_handler(service) -> None:
        """Apply a service."""
        host = service.data.get(CONF_HOST)
        routers = hass.data[DOMAIN]
        if host:
            router = routers.get(host)
        elif not routers:
            _LOGGER.error("%s: no routers configured", service.service)
            return
        elif len(routers) == 1:
            router = next(iter(routers.values()))
        else:
            _LOGGER.error(
                "%s: more than one router configured, must specify one of URLs %s",
                service.service,
                sorted(routers),
            )
            return
        if not router:
            _LOGGER.error("%s: router %s unavailable", service.service, host)
            return

        if service.service == SERVICE_WAN_PPPOE_CONNECT:
            result = await router['entity'].wan_pppoe_connect()
            _LOGGER.debug("__init__::async_setup::service_handler %s: %s", service.service, result)
        elif service.service == SERVICE_WAN_PPPOE_DISCONNECT:
            result = await router['entity'].wan_pppoe_disconnect()
            _LOGGER.debug("__init__::async_setup::service_handler %s: %s", service.service, result)
        elif service.service == SERVICE_REBOOT:
            result = await router['entity'].reboot()
            _LOGGER.debug("__init__::async_setup::service_handler %s: %s", service.service, result)
        else:
            _LOGGER.error("%s: unsupported service", service.service)

    for service in SERVICES:
        _LOGGER.debug("__init__::async_setup_entry registering service %s", service)
        hass.helpers.service.async_register_admin_service(
            DOMAIN,
            service,
            service_handler,
            schema=SERVICE_SCHEMA,
        )

    router = DDWrtEntity(hass, config_entry)
    if not await router.async_update_about_data():
        raise PlatformNotReady
    if not await router.async_update_sensor_data():
        raise PlatformNotReady

    # Make sure there's a RDW entry in hass.data in case this is the first RDW entity
    if DOMAIN not in hass.data:
        hass.data.update({DOMAIN: {}})

    hass.data[DOMAIN].update({
        config_entry.data[CONF_HOST]: {
            'entity': router
        }
    })

    for component in (COMPONENTS):
        _LOGGER.debug("__init__::async_setup_entry adding router %s", config_entry.data.get(CONF_HOST))
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(
                config_entry,
                component,
            )
        )

    async def async_track_time_interval_about_update(event_time):
        """Update the entity's about data and all it's components."""

        _LOGGER.debug("__init__::async_setup_entry::async_track_time_interval_about_update called")

        if not await router.async_update_about_data():
            _LOGGER.warning("Failed to update about data")
        else:
            async_dispatcher_send(hass, TOPIC_DATA_UPDATE)

    async def async_track_time_interval_sensor_update(event_time):
        """Update the entity's sensor data and all it's components."""

        _LOGGER.debug("__init__::async_setup_entry::async_track_time_interval_sensor_update called")

        if not await router.async_update_sensor_data():
            _LOGGER.warning("Failed to update sensor data")
        else:
            async_dispatcher_send(hass, TOPIC_DATA_UPDATE)

    hass.data[DOMAIN][config_entry.data[CONF_HOST]].update({
        DATA_LISTENER: {
            config_entry.entry_id: async_track_time_interval(
                hass,
                async_track_time_interval_sensor_update,
                SCAN_INTERVAL_DATA,
            )
        }
    })

    return True

async def async_unload_entry(hass, config_entry):
    """Unload a DD-WRT config entry."""

    _LOGGER.debug("__init__::async_unload_entry config=%s", config_entry)

    cancel = hass.data[DOMAIN][config_entry.data[CONF_HOST]][DATA_LISTENER].pop(config_entry.entry_id)
    cancel()

    for component in (COMPONENTS):
        await hass.config_entries.async_forward_entry_unload(config_entry, component)

    return True


class DDWrtEntity:
    """This class queries a wireless router running DD-WRT firmware."""

    def __init__(self, hass, config):
        """Initialize the DD-WRT entity."""

        _LOGGER.debug("DDWrtEntity.__init__")

        self._hass = hass
        self._name = config.data[CONF_NAME]
        self._host = config.data[CONF_HOST]
        self._username = config.data[CONF_USERNAME]
        self._password = config.data[CONF_PASSWORD]
        self._protocol = "https" if config.data[CONF_SSL] else "http"
        self._verify_ssl = config.data[CONF_VERIFY_SSL]

        # Determine what type of clients need to be listed
        self._track_arp = True if CONF_TRACK_ARP in config.data[CONF_RESOURCES] else False
        self._track_dhcp = True if CONF_TRACK_DHCP in config.data[CONF_RESOURCES] else False
        self._track_pppoe = True if CONF_TRACK_PPPOE in config.data[CONF_RESOURCES] else False
        self._track_pptp = True if CONF_TRACK_PPTP in config.data[CONF_RESOURCES] else False
        self._track_wds = True if CONF_TRACK_WDS in config.data[CONF_RESOURCES] else False
        self._track_wireless = True if CONF_TRACK_WIRELESS in config.data[CONF_RESOURCES] else False

        # Guard against undefined sensor types
        self._sensor_type = "undefined"
        self._binary_sensor_type = "undefined"

        # Set default values for sensors and binary sensors
        self.results = {}
        self.results.update({self._binary_sensor_type: None})
        self.results.update({self._sensor_type: None})
        for binary_sensor_type in BINARY_SENSORS:
            self.results.update({binary_sensor_type: False})
        for sensor_type in SENSORS:
            self.results.update({sensor_type: None})

        # Get session
        session = async_get_clientsession(self._hass, verify_ssl=self._verify_ssl)

        # Clear the clients list of MAC addresses
        self.devices = {}

        # Initialize the DDWrt object
        self._router = DDWrt(
            aio_session = session,
            host = self._host,
            username = self._username,
            password = self._password,
            protocol = self._protocol,
            verify_ssl = self._verify_ssl,
        )

    async def async_update_about_data(self):
        """Get about information from the DD-WRT router."""

        _LOGGER.debug("DDWrtEntity.update_about_data")

        try:
            result = await self._hass.async_add_executor_job(
                partial(
                    self._router.update_about_data
                )
            )
        except DDWrt.ExceptionSelfSigned:
            _LOGGER.warning("Can't verify self-signed certificate for %s. Please add 'ssl_verify: false' to your config.", self._host)
            return None
        except Exception as e:
            _LOGGER.warning("Unable to update about data: %s", e)
            return None

#        return self._router.update_about_data()
        _LOGGER.debug("_router.results=%s", self._router.results)
        return result

    async def async_update_sensor_data(self):
        """Get information from the DD-WRT router."""

        _LOGGER.debug("DDWrtEntity.update_sensor_data")

        success = True

        # Update LAN data
        try:
            result = await self._hass.async_add_executor_job(self._router.update_lan_data)
        except KeyError as e:
            _LOGGER.warning("Missing key in LAN data, please report this error to the developer. (%s)", e)
            success = False
        except Exception as e:
            _LOGGER.warning("Unable to update LAN data: %s", e)
            success = False

        # Update networking data
        try:
            result = await self._hass.async_add_executor_job(self._router.update_network_data)
        except KeyError as e:
            _LOGGER.warning("Missing key in network data, please report this error to the developer. (%s)", e)
            success = False
        except Exception as e:
            _LOGGER.warning("Unable to update network data: %s", e)
            success = False

        # Update router data
        try:
            result = await self._hass.async_add_executor_job(self._router.update_router_data)
        except KeyError as e:
            _LOGGER.warning("Missing key in router data, please report this error to the developer. (%s)", e)
            success = False
        except Exception as e:
            _LOGGER.warning("Unable to update router data: %s", e)
            success = False

        # Update WAN data
        try:
            result = await self._hass.async_add_executor_job(self._router.update_wan_data)
        except KeyError as e:
            _LOGGER.warning("Missing key in WAN data, please report this error to the developer. (%s)", e)
            success = False
        except Exception as e:
            _LOGGER.warning("Unable to update WAN data: %s", e)
            success = False

#        try:
        result = await self._hass.async_add_executor_job(self._router.update_wireless_data)
#        except KeyError as e:
#            _LOGGER.warning("Missing key in wireless data, please report this error to the developer. (%s)", e)
#            success = False
#        except Exception as e:
#            _LOGGER.warning("Unable to update wireless data: %s", e)
#            success = False

        # Update UPNP data
        try:
            result = await self._hass.async_add_executor_job(self._router.update_upnp_data)
        except KeyError as e:
            _LOGGER.warning("Missing key in UPNP data, please report this error to the developer. (%s)", e)
            success = False
        except Exception as e:
            _LOGGER.warning("Unable to update UPNP data: %s", e)
            success = False

        _LOGGER.debug("self._router.results = %s", self._router.results)
        for key, value in self._router.results.items():
            self.results.update({key: value})

        # Update device tracker data
        self.devices = {}
        if self._track_arp:
            self.devices.update(self._router.clients_arp)
        if self._track_dhcp:
            self.devices.update(self._router.clients_dhcp)
        if self._track_pppoe:
            self.devices.update(self._router.clients_pppoe)
        if self._track_pptp:
            self.devices.update(self._router.clients_pptp)
        if self._track_wds:
            self.devices.update(self._router.clients_wds)
        if self._track_wireless:
            self.devices.update(self._router.clients_wireless)

        # Update traffic graphs
        self.results.update({
            "traffic": self._router.traffic_graph_url(False)
        })

        return success


    async def wan_pppoe_connect(self):
        return self._router.wan_pppoe_connect


    async def wan_pppoe_disconnect(self):
        return self._router.wan_pppoe_disconnect


    async def reboot(self):
        return self._router.reboot

