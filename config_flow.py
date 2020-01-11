"""Config flow to configure the DD-WRT component."""

import logging
import voluptuous as vol
from datetime import timedelta
from urllib.parse import urlparse

from homeassistant import config_entries
from homeassistant.components.ssdp import (
    ATTR_MANUFACTURERURL,
    ATTR_PRESENTATIONURL,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SSL,
    CONF_VERIFY_SSL,
    CONF_SENSORS,
    CONF_BINARY_SENSORS,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_DEVICE_TRACKER,
    DDWRT_MANUFACTURERURL,
    DATA_KEY,
    DEFAULT_NAME,
    DOMAIN,
    SCAN_INTERVAL_DATA,
)
from .pyddwrt import (
    DDWrt
)

_LOGGER = logging.getLogger(__name__)

_LOGGER.debug("config_flow called")


@callback
def configured_instances(hass):
    """Return a set of configured DD-WRT instances."""

    if DATA_KEY in hass.data:
        _LOGGER.debug("config_flow::configured_instances called - returned configured instances")
        return set(
            '{0}'.format(
                entry._host,
            )
            for entry in hass.data[DATA_KEY])
    else:
        _LOGGER.debug("config_flow::configured_instances called - no instances found")
        return {}


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
        pass

    async def _show_integrations_form(self, errors=None):
        """Show the setup form to the user."""

        _LOGGER.debug("DDWRTFlowHandler::_show_integrations_form called")

        return self.async_show_form(
            step_id="integrations",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BINARY_SENSORS, default=True): bool,
                    vol.Required(CONF_SENSORS, default=True): bool,
                    vol.Required(CONF_DEVICE_TRACKER, default=True): bool,
                }
            ),
            errors=errors or {},
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""

        _LOGGER.debug("DDWRTFlowHandler::async_step_import called %s", import_config)

        return await self.async_step_user(import_config)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""

        _LOGGER.debug("DDWRTFlowHandler::async_step_user called %s", user_input)

        errors = {}

        if user_input is not None:

            if user_input[CONF_HOST] in configured_instances(self.hass):
                return self.async_abort(reason="already_configured")

            router = DDWrt(
                host = user_input[CONF_HOST],
                username = user_input[CONF_USERNAME],
                password = user_input[CONF_PASSWORD],
                protocol = "https" if user_input[CONF_SSL] else "http",
                verify_ssl = user_input[CONF_VERIFY_SSL],
            )

            try:
                valid_router = router.update_about_data()
#            except SSLError:
#                return await self._show_setup_form({CONF_HOST: 'ssl_error'})
            except DDWrt.ExceptionSelfSigned:
                _LOGGER.debug("DDWRTFlowHandler::async_step_user SelfSigned")
                errors["base"] = "ssl_selfsigned"
            except DDWrt.ExceptionConnectionError:
                _LOGGER.debug("DDWRTFlowHandler::async_step_user ConnectionError")
                errors["base"] = "connection_error"
            except DDWrt.ExceptionAuthenticationError:
                _LOGGER.debug("DDWRTFlowHandler::async_step_user AuthenticationError")
                errors["base"] = "invalid_credentials"
            except DDWrt.ExceptionTimeout:
                _LOGGER.debug("DDWRTFlowHandler::async_step_user Timeout")
                errors["base"] = "timeout"
            except Exception as e:
                _LOGGER.debug("DDWRTFlowHandler::async_step_user update_about_data exception unknown_error: %s", str(e))
                errors["base"] = "unknown_error"
            else:
                _LOGGER.debug("DDWRTFlowHandler::async_step_user update_about_data returned %s", valid_router)

                self.user_step_inpuit = user_input
                return await self.async_step_integrations(None)

        _LOGGER.debug("DDWRTFlowHandler::async_step_user show setup form")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_USERNAME): str,
                    vol.Optional(CONF_PASSWORD): str,
                    vol.Required(CONF_SSL, default=True): bool,
                    vol.Required(CONF_VERIFY_SSL, default=True): bool,
                }
            ),
            errors=errors,
        )


    async def async_step_integrations(self, user_input=None):
        """Handle the start of the config flow."""

        _LOGGER.debug("DDWRTFlowHandler::async_step_integrations called %s", user_input)

        if not user_input:
            return await self._show_integrations_form(user_input)

        return self.async_create_entry(title=DEFAULT_NAME, data=user_input)


    async def async_step_ssdp(self, discovery_info):
        """Handle SSDP initiated config flow."""

        _LOGGER.debug("DDWRTFlowHandler::async_step_ssdp called. discoveryinfo=%s", discovery_info)

        if discovery_info[ATTR_MANUFACTURERURL] != DDWRT_MANUFACTURERURL:
            return self.async_abort(reason="not_ddwrt")

        url = urlparse(discovery_info[ATTR_PRESENTATIONURL])
        host = url.netloc
        ssl = True if url.scheme == "https" else False

        if host in configured_instances(self.hass):
            return self.async_abort(reason="already_configured")

        model = discovery_info[ATTR_MODEL_NAME]

        user_input = {
            CONF_HOST: host,
            CONF_SSL: ssl,
        }

        return await self._async_show_user_form(user_input)

