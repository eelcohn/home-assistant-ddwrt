"""DD-WRT device tracker - Eelco Huininga 2019-2020."""

from datetime import datetime
import logging
from typing import Dict

from homeassistant.components.device_tracker import SOURCE_TYPE_ROUTER
from homeassistant.components.device_tracker.config_entry import ScannerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.typing import HomeAssistantType

from . import (
    ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME,
    ATTR_ICON,
    ATTR_WIRED,
    ATTRIBUTION,
    CONF_HOST,
    DEFAULT_DEVICE_NAME,
    DEVICE_TRACKERS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the DD-WRT device tracker."""

    _LOGGER.debug("device_tracker::async_setup_entry start")
    router = hass.data[DOMAIN][config_entry.unique_id]
    tracked = set()

    @callback
    def update_router():
        """Update the values of the router."""
        _LOGGER.debug("device_tracker::async_setup_entry::update_router")
        add_entities(
            hass.data[DOMAIN][config_entry.data[CONF_HOST]]['entity'],
            async_add_entities,
            tracked
        )

#    router.listeners.append(
#        async_dispatcher_connect(hass, router.signal_device_new, update_router)
#    )

    update_router()


@callback
def add_entities(router, async_add_entities, tracked):
    """Add new tracker entities from the router."""
    _LOGGER.debug("device_tracker::add_entities start")
    new_tracked = []

    _LOGGER.debug("device_tracker::add_entities router=%s", router)
    for mac, details in router.devices.items():
        _LOGGER.debug("device_tracker::add_entities mac=%s details=%s", mac, details)
        if mac in tracked:
            continue

        new_tracked.append(DdwrtDevice(router, mac, details))
        tracked.add(mac)

    if new_tracked:
        async_add_entities(new_tracked, True)


class DdwrtDevice(ScannerEntity):
    """Representation of a DD-WRT client device."""

    def __init__(self, router, mac, details):
        """Initialize a DD-WRT client device."""

        _LOGGER.debug("DdwrtDevice::__init__")

        self._router = router
        self._details = details
        self._friendly_name = details["name"] or DEFAULT_DEVICE_NAME
        self._mac = mac
        self._manufacturer = None
        self._model = None
        self._icon = None
        self._is_wired = None
        self._active = False
        self._attrs = {}

        self._unsub_dispatcher = None

    def update(self) -> None:
        """Update the DD-WRT device."""

        _LOGGER.debug("DdwrtDevice::update details=%s", self._details)

        self._icon = DEVICE_TRACKERS[self._details["type"]][ATTR_ICON]
        self._is_wired = DEVICE_TRACKERS[self._details["type"]][ATTR_WIRED]

#        device = self._router.devices[self._mac]
#        self._active = device["active"]
#        if device.get("attrs") is None:
#            # device
#            self._attrs = {
#                "last_time_reachable": datetime.fromtimestamp(
#                    device["last_time_reachable"]
#                ),
#                "last_time_activity": datetime.fromtimestamp(device["last_activity"]),
#            }
#        else:
#            # router
#            self._attrs = device["attrs"]

    @property
    def device_info(self):
        """Return the device info."""
        result = {
            "connections": {(CONNECTION_NETWORK_MAC, self._mac)},
            ATTR_FRIENDLY_NAME: self._friendly_name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": self._manufacturer,
            "model": self._model,
            "name": self._friendly_name,
            "via_device": (DOMAIN),
        }
        _LOGGER.debug("DdwrtSensor::device_info result=%s", result)
        return result

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""

        _LOGGER.debug("DdwrtDevice::unique_id mac=%s", self._mac)

        return self._mac

    @property
    def name(self) -> str:
        """Return the name."""

        _LOGGER.debug("DdwrtDevice::name mac=%s", self._mac)

        return self._mac

    @property
    def is_connected(self):
        """Return true if the device is connected to the network."""

        _LOGGER.debug("DdwrtDevice::is_connected mac=%s", self._mac)

        return self._active

    @property
    def source_type(self) -> str:
        """Return the source type."""

        _LOGGER.debug("DdwrtDevice::source_type mac=%s", self._mac)

        return SOURCE_TYPE_ROUTER

    @property
    def icon(self) -> str:
        """Return the icon."""

        _LOGGER.debug("DdwrtDevice::icon mac=%s", self._mac)

        return self._icon

    @property
    def device_state_attributes(self) -> Dict[str, any]:
        """Return the attributes."""

        _LOGGER.debug("DdwrtDevice::attributes mac=%s", self._mac)

        attributes = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "is_wired": self._is_wired,
        }
        attributes.update(self._details)

        return attributes

    @property
    def should_poll(self) -> bool:
        """No polling needed."""

        _LOGGER.debug("DdwrtDevice::should_poll mac=%s", self._mac)

        return False

    async def async_on_demand_update(self):
        """Update state."""

        _LOGGER.debug("DdwrtDevice::async_on_demand_update mac=%s", self._mac)

        self.async_schedule_update_ha_state(True)

    async def async_added_to_hass(self):
        """Register state update callback."""

        _LOGGER.debug("DdwrtDevice::async_added_to_hass mac=%s", self._mac)

#        self._unsub_dispatcher = async_dispatcher_connect(
#            self.hass, self._router.signal_device_update, self.async_on_demand_update
#        )

    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""

        _LOGGER.debug("DdwrtDevice::async_will_remove_from_hass mac=%s", self._mac)

#        self._unsub_dispatcher()


def icon_for_freebox_device(device) -> str:
    """Return a host icon from his type."""
    return DEVICE_ICONS.get(device["host_type"], "mdi:help-network")

