"""DD-WRT device tracker - Eelco Huininga 2019-2020."""

import logging

from homeassistant.components.device_tracker import DeviceScanner
from homeassistant.components.device_tracker.const import SOURCE_TYPE_ROUTER

from . import DATA_KEY

DEVICE_ATTRIBUTES = [
    "essid",
    "hostname",
    "ip",
    "mac",
    "radio",
    "radio_proto",
]

_LOGGER = logging.getLogger(__name__)


async def async_get_scanner(hass, config):
    """Set up the ddwrt device tracker."""

    scanners = []

    _LOGGER.debug("device_tracker::async_get_scanner start")
    for router in hass.data[DATA_KEY]:
        _LOGGER.debug("device_tracker::async_get_scanner for router %s", router._host)
        scanner = DdwrtDeviceTracker(router)
        await scanner.async_connect()

        if scanner.success_init:
            _LOGGER.debug("device_tracker::async_get_scanner setup succesfully for %s", router._host)
            scanners.append(scanner)
        else:
            _LOGGER.debug("device_tracker::async_get_scanner setup failed for %s", router._host)

    if scanners:
        return scanner
    else:
        return None


class DdwrtDeviceTracker(DeviceScanner):
    """Representation of a DD-WRT device tracker."""

    def __init__(self, api):
        """Initialize the scanner."""

        _LOGGER.debug("DdwrtDeviceTracker::__init__ for router %s", api._host)

        self._api = api
        self.attributes = {}
        self.is_wired = None
        self.success_init = None

    async def async_connect(self):
        """Initialize connection to the router."""

        # Test the router is accessible.
        self.success_init = await self.async_update_info()
        _LOGGER.debug("DdwrtDeviceTracker::async_connect success_init=%s", self.success_init)

    async def async_scan_devices(self):
        """Scan for new devices and return a list with found device IDs."""

        await self.async_update_info()
        _LOGGER.debug("DdwrtDeviceTracker::async_scan_devices clients=%s", self._api.clients)
        return list(self._api.clients)

    async def async_get_device_name(self, device):
        """Return the name of the given device or None if we don't know."""

        if device in self._api.clients:
            result = self._api.clients[device]['name']
        else:
            result = None

        _LOGGER.debug("DdwrtDeviceTracker::async_get_device_name device=%s name=%s", device, result)
        return result

    async def async_update_info(self):
        """Fetch status from DD-WRT."""

        _LOGGER.debug("DdwrtDeviceTracker::async_update_info")
        return self._api.update_sensor_data()

    async def async_added_to_hass(self):
        """Client entity created."""

        _LOGGER.debug("DdwrtDeviceTracker::async_added_to_hass %s", self)

    @property
    def source_type(self):
        """Return the source type of the device."""

        _LOGGER.debug("DdwrtDeviceTracker::source_type")
        return SOURCE_TYPE_ROUTER

    @property
    def device_state_attributes(self):
        """Return the client state attributes."""

        _LOGGER.debug("DdwrtDeviceTracker::device_state_attributes")

        self.attributes = {}
        for variable in DEVICE_ATTRIBUTES:
#            if variable in self.client[self._api.device]:
#                attributes[variable] = self.client.raw[variable]
                self.attributes.update({variable: "Testvalue"})

        self.attributes.update({"is_wired": self.is_wired})

        return self.attributes

