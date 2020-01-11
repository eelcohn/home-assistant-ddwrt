"""DD-WRT binary sensor - Eelco Huininga 2019-2020."""

import logging

from homeassistant.components.binary_sensor import BinarySensorDevice

from . import (
    ATTR_ATTRIBUTION,
    ATTRIBUTION,
    DATA_KEY,
    BINARY_SENSORS,
    _NAME,
    _ICON,
    _ICON_OFF,
    _CLASS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the ddwrt binary sensors."""

    _LOGGER.debug("binary_sensor::async_setup_platform")

    if discovery_info is None:
        return

    binary_sensors = []

    for router in hass.data[DATA_KEY]:
        for sensor_type in discovery_info:
            binary_sensors.append(DdwrtBinarySensor(router, sensor_type))
            _LOGGER.debug("DD-WRT: added binary sensor %s", sensor_type)

    async_add_entities(binary_sensors)


class DdwrtBinarySensor(BinarySensorDevice):
    """Representation of a ddwrt binary sensor."""

    def __init__(self, api, sensor_type):
        """Initialize the binary sensor."""

        _LOGGER.debug("DdwrtBinarySensor::__init__")

        self._api = api
        self._sensor_type = sensor_type

        self._name = '{} {}'.format(self._api._name, self._sensor_type)
        self._device_class = BINARY_SENSORS[self._sensor_type][_CLASS]
        self._icon = BINARY_SENSORS[self._sensor_type][_ICON]
        self._icon_off = BINARY_SENSORS[self._sensor_type][_ICON_OFF]
 
    async def async_update(self):
        """Fetch status from asuswrt."""

        _LOGGER.debug("DdwrtBinarySensor::async_update")

        self._api.update_sensor_data()

    async def async_added_to_hass(self):
        """Client entity created."""

        _LOGGER.debug("DdwrtBinarySensor::async_added_to_hass %s", self._sensor_type)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class
 
    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attr = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }
        return attr

    @property
    def icon(self):
        """Return the mdi icon of the sensor."""
        if self._api.results[self._sensor_type]:
            return self._icon
        else:
            return self._icon_off

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._api.results[self._sensor_type]

    @property
    def state(self):
        """Return the state of the binary sensor."""
        return self._api.results[self._sensor_type]

