"""Support for DD-WRT devices."""

import logging
import voluptuous as vol

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME,
    CONF_DEVICES,
    CONF_HOST,
    CONF_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SSL,
    CONF_VERIFY_SSL,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.util import Throttle

from .const import (
    ATTRIBUTION,
    BINARY_SENSORS,
    BINARY_SENSOR_DEFAULTS,
    CONF_BINARY_SENSOR,
    CONF_DEVICE_TRACKER,
    CONF_SENSOR,
    CONF_TRACK_ARP,
    CONF_TRACK_DHCP,
    CONF_TRACK_PPPOE,
    CONF_TRACK_PPTP,
    CONF_TRACK_WDS,
    CONF_TRACK_WIRELESS,
    DATA_KEY,
    DEFAULT_NAME,
    DEFAULT_SSL,
    DEFAULT_VERIFY_SSL,
    DEFAULT_WIRELESS_ONLY,
    DEVICE_TRACKERS,
    DEVICE_TRACKER_DEFAULTS,
    DOMAIN,
    SCAN_INTERVAL_ABOUT,
    SCAN_INTERVAL_DATA,
    SENSORS,
    SENSOR_DEFAULTS,
    _CLASS,
    _ICON,
    _ICON_OFF,
    _NAME,
    _UNIT,
)
from .pyddwrt import DDWrt

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DEVICES): vol.All(
                    cv.ensure_list,
                    [
                        vol.Schema(
                            {
                                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                                vol.Required(CONF_HOST): cv.string,
                                vol.Optional(CONF_USERNAME, default=""): cv.string,
                                vol.Optional(CONF_PASSWORD, default=""): cv.string,
                                vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
                                vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): cv.boolean,
                                vol.Optional(CONF_BINARY_SENSOR, default=BINARY_SENSOR_DEFAULTS): vol.All(
                                    cv.ensure_list, [vol.In(list(BINARY_SENSORS))]
                                ),
                                vol.Optional(CONF_SENSOR, default=SENSOR_DEFAULTS): vol.All(
                                    cv.ensure_list, [vol.In(list(SENSORS))]
                                ),
                                vol.Optional(CONF_DEVICE_TRACKER, default=DEVICE_TRACKER_DEFAULTS): vol.All(
                                    cv.ensure_list, [vol.In(list(DEVICE_TRACKERS))]
                                ),
                            },
                        ),
                    ],
                ),
            },
        ),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the DD-WRT component."""

    _LOGGER.debug("__init__::async_setup")

    router_list = []
    for router in config[DOMAIN].get(CONF_DEVICES):
        api = DDWrtEntity(router)

        # Test the router is accessible and get firmware version data
        if api.update_about_data():
            _LOGGER.debug("__init__::async_setup Successfully added router %s", router.get(CONF_HOST))
            router_list.append(api)

            hass.async_create_task(
                async_load_platform(
                    hass,
                    CONF_BINARY_SENSOR,
                    DOMAIN,
                    router.get(CONF_BINARY_SENSOR),
                    config
                )
            )

            hass.async_create_task(
                async_load_platform(
                    hass,
                    CONF_SENSOR,
                    DOMAIN,
                    router.get(CONF_SENSOR),
                    config
                )
            )

            hass.async_create_task(
                async_load_platform(
                    hass,
                    CONF_DEVICE_TRACKER,
                    DOMAIN,
                    router.get(CONF_DEVICE_TRACKER),
                    config
                )
            )
        else:
            _LOGGER.warning("Can't setup DD-WRT router %s", router.get(CONF_HOST))

    if not router_list:
        _LOGGER.warning("No DD-WRT routers configured.")
        return False

    hass.data[DOMAIN] = router_list

    return True


class DDWrtEntity:
    """This class queries a wireless router running DD-WRT firmware."""

    def __init__(self, config):
        """Initialize the DD-WRT entity."""

        _LOGGER.debug("DDWrtEntity::__init__")

        self._name = config[CONF_NAME]
        self._host = config[CONF_HOST]
        self._username = config[CONF_USERNAME]
        self._password = config[CONF_PASSWORD]
        self._protocol = "https" if config[CONF_SSL] else "http"
        self._verify_ssl = config[CONF_VERIFY_SSL]

        # Determine what type of clients need to be listed
        self._track_arp = True if CONF_TRACK_ARP in config[CONF_DEVICE_TRACKER] else False
        self._track_dhcp = True if CONF_TRACK_DHCP in config[CONF_DEVICE_TRACKER] else False
        self._track_pppoe = True if CONF_TRACK_PPPOE in config[CONF_DEVICE_TRACKER] else False
        self._track_pptp = True if CONF_TRACK_PPTP in config[CONF_DEVICE_TRACKER] else False
        self._track_wds = True if CONF_TRACK_WDS in config[CONF_DEVICE_TRACKER] else False
        self._track_wireless = True if CONF_TRACK_WIRELESS in config[CONF_DEVICE_TRACKER] else False

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

        # Clear the clients list of MAC addresses
        self.clients = []

        # Initialize the DDWrt object
        self._router = DDWrt(
            host = self._host,
            username = self._username,
            password = self._password,
            protocol = self._protocol,
            verify_ssl = self._verify_ssl,
        )

    @Throttle(SCAN_INTERVAL_ABOUT)
    def update_about_data(self):
        """Get about information from the DD-WRT router."""

        _LOGGER.debug("DDWrtEntity::update_about_data")

        try:
            result = self._router.update_about_data()
        except DDWrt.ExceptionSelfSigned:
            _LOGGER.warning("Can't verify self-signed certificate for %s. Please add 'ssl_verify: false' to your config.", self._host)
            return None
        except Exception as e:
            _LOGGER.warning("Unable to update about data: %s", e)
            return None

        return self._router.update_about_data()

    @Throttle(SCAN_INTERVAL_DATA)
    def update_sensor_data(self):
        """Get information from the DD-WRT router."""

        _LOGGER.debug("DDWrtEntity::update_sensor_data")

        success = True

        try:
            result = self._router.update_lan_data()
        except Exception as e:
            _LOGGER.warning("Unable to update LAN data: %s", e)
            success = False

        try:
            result = self._router.update_network_data()
        except Exception as e:
            _LOGGER.warning("Unable to update network data: %s", e)
            success = False

        try:
            result = self._router.update_router_data()
        except Exception as e:
            _LOGGER.warning("Unable to update router data: %s", e)
            success = False

        try:
            result = self._router.update_wan_data()
        except Exception as e:
            _LOGGER.warning("Unable to update WAN data: %s", e)
            success = False

        try:
            result = self._router.update_wireless_data()
        except Exception as e:
            _LOGGER.warning("Unable to update wireless data: %s", e)
            success = False

        for key, value in self._router.results.items():
            self.results.update({key: value})

        self.clients = {}
        if self._track_arp:
            self.clients.update(self._router.clients_arp)
        if self._track_arp:
            self.clients.update(self._router.clients_wireless)
        if self._track_dhcp:
            self.clients.update(self._router.clients_dhcp)
        if self._track_pppoe:
            self.client.update(self._router.clients_pppoe)
        if self._track_pptp:
            self.clients.update(self._router.clients_pptp)
        if self._track_wds:
            self.clients.update(self._router.clients_wds)

        return success

