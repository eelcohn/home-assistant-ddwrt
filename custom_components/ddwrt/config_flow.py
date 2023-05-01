"""Config flow to configure the DD-WRT component."""

import logging
import voluptuous as vol
from datetime import timedelta
from urllib.parse import urlparse

from homeassistant import config_entries
from homeassistant.components.ssdp import (
    ATTR_UPNP_MANUFACTURER_URL,
    ATTR_UPNP_PRESENTATION_URL,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import (
    ATTR_NAME,
    BINARY_SENSORS,
    CAMERAS,
    CONF_DEVICE_TRACKER,
    CONF_HOST,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_RESOURCES,
    CONF_SSL,
    CONF_VERIFY_SSL,
    CONF_SENSOR,
    CONF_BINARY_SENSOR,
    DDWRT_UPNP_MANUFACTURER_URL,
    DEFAULT_SSL,
    DEFAULT_VERIFY_SSL,
    DEVICE_TRACKERS,
    DOMAIN,
    MIN_SCAN_INTERVAL,
    SCAN_INTERVAL_DATA,
    SENSORS,
)
from .pyddwrt import (
    DDWrt
)

_LOGGER = logging.getLogger(__name__)

_LOGGER.debug("config_flow called")


def _resource_schema_base(selected_resources):
    """Resource selection schema."""

    available_resources = {}

    available_resources.update(BINARY_SENSORS.items())
    available_resources.update(CAMERAS.items())
    available_resources.update(DEVICE_TRACKERS.items())
    available_resources.update(SENSORS.items())

    known_available_resources = {
        sensor_id: sensor[ATTR_NAME]
        for sensor_id, sensor in BINARY_SENSORS.items()
        if sensor_id in available_resources
    }
    known_available_resources.update({
        sensor_id: sensor[ATTR_NAME]
        for sensor_id, sensor in CAMERAS.items()
        if sensor_id in available_resources
    })
    known_available_resources.update({
        sensor_id: sensor[ATTR_NAME]
        for sensor_id, sensor in DEVICE_TRACKERS.items()
        if sensor_id in available_resources
    })
    known_available_resources.update({
        sensor_id: sensor[ATTR_NAME]
        for sensor_id, sensor in SENSORS.items()
        if sensor_id in available_resources
    })

    return {
        vol.Required(CONF_RESOURCES, default=selected_resources): cv.multi_select(
            known_available_resources
        )
    }


@config_entries.HANDLERS.register(DOMAIN)
class DDWRTFlowHandler(config_entries.ConfigFlow):
    """Handle a DD-WRT config flow."""

    _LOGGER.debug("DDWRTFlowHandler called")

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    _hassio_discovery = None

    def __init__(self):
        """Initialize the config flow."""

        _LOGGER.debug("DDWRTFlowHandler::__init__ called")

        self.ddwrt_config = {}
        self.discovery_info = {}

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""

        _LOGGER.debug("DDWRTFlowHandler::async_step_import called %s", import_config)

        # Check if already configured
        await self.async_set_unique_id(import_config[CONF_HOST], raise_on_progress=False)
        self._abort_if_unique_id_configured()

        title = '{} (configuration.yaml)'.format(import_config[CONF_HOST])

        if import_config[CONF_NAME] is None:
            import_config.update({CONF_NAME: import_config[CONF_HOST]})

        return self.async_create_entry(title=title, data=import_config)


    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""

        _LOGGER.debug("DDWRTFlowHandler::async_step_user called %s", user_input)

        errors = {}

        if user_input is not None:

            # Check if already configured
            await self.async_set_unique_id(user_input[CONF_HOST], raise_on_progress=False)
            self._abort_if_unique_id_configured()

            self.ddwrt_config.update(user_input)

            if CONF_NAME not in self.ddwrt_config:
                self.ddwrt_config.update({CONF_NAME: self.ddwrt_config[CONF_HOST]})

            session = async_get_clientsession(self.hass, verify_ssl=self.ddwrt_config[CONF_VERIFY_SSL])

            router = DDWrt(
                aio_session = session,
                host = self.ddwrt_config[CONF_HOST],
                username = self.ddwrt_config[CONF_USERNAME],
                password = self.ddwrt_config[CONF_PASSWORD],
                protocol = "https" if self.ddwrt_config[CONF_SSL] else "http",
                verify_ssl = self.ddwrt_config[CONF_VERIFY_SSL],
            )

            try:
                 valid_router = await self.hass.async_add_executor_job(router.update_about_data)
#            except SSLError:
#                return await self._show_setup_form({CONF_HOST: 'ssl_error'})
            except DDWrt.ExceptionSelfSigned:
                _LOGGER.error("DDWRTFlowHandler::async_step_user SelfSigned")
                errors["base"] = "ssl_selfsigned"
            except ConnectionRefusedError:
                _LOGGER.error("DDWRTFlowHandler::async_step_user ConnectionRefusedError")
                errors["base"] = "connection_refused_error"
#            except CannotConnect:
#                _LOGGER.debug("DDWRTFlowHandler::async_step_user ConnectionError")
#                errors["base"] = "connection_error"
            except DDWrt.ExceptionAuthenticationError:
                _LOGGER.error("DDWRTFlowHandler::async_step_user AuthenticationError")
                errors["base"] = "invalid_credentials"
            except DDWrt.ExceptionTimeout:
                _LOGGER.error("DDWRTFlowHandler::async_step_user Timeout")
                errors["base"] = "timeout"
            except Exception as e:
                _LOGGER.error("DDWRTFlowHandler::async_step_user update_about_data exception unknown_error: %s", str(e))
                errors["base"] = "unknown_error"
            else:
                _LOGGER.debug("DDWRTFlowHandler::async_step_user update_about_data returned %s", valid_router)

                self.user_step_input = self.ddwrt_config
                return await self.async_step_resources()

        _LOGGER.debug("DDWRTFlowHandler::async_step_user show setup form")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_USERNAME): str,
                    vol.Optional(CONF_PASSWORD): str,
                    vol.Required(CONF_SSL, default=DEFAULT_SSL): bool,
                    vol.Required(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
                }
            ),
            errors=errors,
        )


    async def async_step_resources(self, user_input=None):
        """Handle the picking the resources."""

        _LOGGER.debug("DDWRTFlowHandler::async_step_resources called %s", user_input)

        if user_input is None:
            return self.async_show_form(
                step_id="resources",
                data_schema=vol.Schema(
                    _resource_schema_base([])
                ),
            )

        self.ddwrt_config.update(user_input)

        return self.async_create_entry(
            title=self.ddwrt_config[CONF_NAME],
            data=self.ddwrt_config
        )


    async def async_step_ssdp(self, discovery_info):
        """Handle SSDP initiated config flow."""

        _LOGGER.debug("DDWRTFlowHandler::async_step_ssdp called. discoveryinfo=%s", discovery_info)

        if discovery_info[ATTR_UPNP_MANUFACTURER_URL] != DDWRT_UPNP_MANUFACTURER_URL:
            return self.async_abort(reason="not_ddwrt")

        url = urlparse(discovery_info[ATTR_UPNP_PRESENTATION_URL])
        host = url.netloc
        ssl = True if url.scheme == "https" else False

        # Check if already configured
        await self.async_set_unique_id(user_input[CONF_HOST], raise_on_progress=False)
        self._abort_if_unique_id_configured()

        model = discovery_info[ATTR_MODEL_NAME]

        user_input = {
            CONF_HOST: host,
            CONF_SSL: ssl,
        }

        return await self._async_show_user_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for dd-wrt."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""

        _LOGGER.debug("OptionsFlowHandler::__init__ called. config_entry.options=%s data=%s", config_entry.options, config_entry.data)

        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.data.get(
                        CONF_SCAN_INTERVAL,
                        SCAN_INTERVAL_DATA,
                    ),
#                ): int,
                ): cv.time_period,
#                _resource_schema_base(
#                    self.config_entry.data['resources']
#                )
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema
        )

