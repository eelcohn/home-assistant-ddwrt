"""DD-WRT sensor - Eelco Huininga 2019-2020."""

import logging

from homeassistant.helpers.entity import Entity
from statistics import mean

from . import (
    ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME,
    ATTRIBUTION,
    DATA_KEY,
    SENSORS,
    _NAME,
    _CLASS,
    _ICON,
    _UNIT,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the DDWRT sensors."""

    _LOGGER.debug("sensor::async_setup_platform")

    if discovery_info is None:
        return

    sensors = []

    for router in hass.data[DATA_KEY]:
        for sensor_type in discovery_info:
            sensors.append(DdwrtSensor(router, sensor_type))
            _LOGGER.debug("DD-WRT: added sensor %s", sensor_type)

    async_add_entities(sensors)


class DdwrtSensor(Entity):
    """Representation of a ddwrt sensor."""

    def __init__(self, api, sensor_type):
        """Initialize the sensor."""

        _LOGGER.debug("DdwrtSensor::__init__")

        self._api = api
        self._sensor_type = sensor_type

        self._name = '{} {}'.format(self._api._name, self._sensor_type)
        self._device_class = SENSORS[self._sensor_type][_CLASS]
        self._friendly_name = SENSORS[self._sensor_type][_NAME]
        self._icon = SENSORS[self._sensor_type][_ICON]
        self._unit_of_measurement = SENSORS[self._sensor_type][_UNIT]

    async def async_update(self):
        """Fetch status from asuswrt."""

        _LOGGER.debug("DdwrtSensor::async_update")

        self._api.update_sensor_data()

    async def async_added_to_hass(self):
        """Client entity created."""

        _LOGGER.debug("DdwrtSensor::async_added_to_hass %s", self._name)

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

        # Set default attribution
        attr = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_FRIENDLY_NAME: self._friendly_name,
        }

        # Set attributes for all individual temperature sensor in the router
        if self._sensor_type == 'cpu_temp':
            if self._api.results[self._sensor_type]:
                for key, value in self._api.results[self._sensor_type].items():
                    attr.update({key.lower(): "{} {}".format(value, self._unit_of_measurement)})

        return attr

    @property
    def icon(self):
        """Return the mdi icon of the sensor."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._sensor_type == 'cpu_temp':
            if self._api.results[self._sensor_type]:
                return round(mean(self._api.results[self._sensor_type].values()), 1)
        else:
            return self._api.results[self._sensor_type]

