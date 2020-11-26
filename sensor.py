"""DD-WRT sensor - Eelco Huininga 2019-2020."""

import logging

from homeassistant.helpers.entity import Entity
from statistics import mean

from . import (
    ATTR_ATTRIBUTION,
    ATTR_DEVICE_CLASS,
    ATTR_FRIENDLY_NAME,
    ATTR_ICON,
    ATTR_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    ATTRIBUTION,
    CONF_RESOURCES,
    CONF_HOST,
    CONF_NAME,
    DOMAIN,
    SENSORS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the DD-WRT sensor."""

    _LOGGER.debug("async_setup_entry: called")

    sensors = []
    for sensor_type in config_entry.data[CONF_RESOURCES]:
        if sensor_type in SENSORS:
            _LOGGER.debug("async_setup_entry: host=%s setup for %s", config_entry.data[CONF_HOST], sensor_type)
            sensors.append(DdwrtSensor(
                hass.data[DOMAIN][config_entry.data[CONF_HOST]]['entity'],
                config_entry.data[CONF_NAME],
                sensor_type,
            )
    )

    async_add_entities(sensors, True)


class DdwrtSensor(Entity):
    """Representation of a ddwrt sensor."""

    def __init__(self, api, routername, sensor_type):
        """Initialize the sensor."""

        _LOGGER.debug("DdwrtSensor::__init__")

        self._api = api
        self._sensor_type = sensor_type

        self._device_class = SENSORS[self._sensor_type][ATTR_DEVICE_CLASS]
        self._host = self._api._host
        self._icon = SENSORS[self._sensor_type][ATTR_ICON]
        self._friendly_name = SENSORS[self._sensor_type][ATTR_NAME]
        self._routername = routername
        self._sw_version = f"{self._api.results['sw_version']}.{self._api.results['sw_build']}"
        self._unique_id = '{}_{}'.format(self._host, self._sensor_type)
        self._unit_of_measurement = SENSORS[self._sensor_type][ATTR_UNIT_OF_MEASUREMENT]

    async def async_update(self):
        """Fetch status from DD-WRT."""

#        _LOGGER.debug("DdwrtSensor::async_update for %s", self._sensor_type)

    async def async_added_to_hass(self):
        """Client entity created."""

        _LOGGER.debug("DdwrtSensor::async_added_to_hass %s", self._sensor_type)

    @property
    def device_info(self):
        """Return the device info."""
        result = {
            "identifiers": {(DOMAIN, self._host)},
            ATTR_FRIENDLY_NAME: self._friendly_name,
            "manufacturer": self._api.results["router_manufacturer"],
            "model": self._api.results["router_model"],
            ATTR_NAME: self._routername,
            "sw_version": self._sw_version,
            "via_device": (DOMAIN),
        }
        _LOGGER.debug("DdwrtSensor::device_info result=%s", result)
        return result

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._sensor_type

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
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

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

