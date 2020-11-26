"""DD-WRT binary sensor - Eelco Huininga 2019-2020."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity

from . import (
    ATTR_ATTRIBUTION,
    ATTR_DEVICE_CLASS,
    ATTR_FRIENDLY_NAME,
    ATTR_ICON,
    ATTR_ICON_OFF,
    ATTR_NAME,
    ATTRIBUTION,
    BINARY_SENSORS,
    CONF_RESOURCES,
    CONF_HOST,
    CONF_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the DD-WRT binary sensor."""

    _LOGGER.debug("async_setup_entry: called")

    binary_sensors = []
    for binary_sensor_type in config_entry.data[CONF_RESOURCES]:
        if binary_sensor_type in BINARY_SENSORS:
            _LOGGER.debug("async_setup_entry: host=%s setup for %s", config_entry.data[CONF_HOST], binary_sensor_type)
            binary_sensors.append(DdwrtBinarySensor(
                hass.data[DOMAIN][config_entry.data[CONF_HOST]]['entity'],
                config_entry.data[CONF_NAME],
                binary_sensor_type,
            )
    )

    async_add_entities(binary_sensors, True)
    

class DdwrtBinarySensor(BinarySensorEntity):
    """Representation of a ddwrt binary sensor."""

    def __init__(self, api, routername, binary_sensor_type):
        """Initialize the binary sensor."""

        _LOGGER.debug("DdwrtBinarySensor::__init__")

        self._api = api
        self._binary_sensor_type = binary_sensor_type

        self._device_class = BINARY_SENSORS[self._binary_sensor_type][ATTR_DEVICE_CLASS]
        self._host = self._api._host
        self._icon = BINARY_SENSORS[self._binary_sensor_type][ATTR_ICON]
        self._icon_off = BINARY_SENSORS[self._binary_sensor_type][ATTR_ICON_OFF]
        self._friendly_name = BINARY_SENSORS[self._binary_sensor_type][ATTR_NAME]
        self._routername = routername
        self._unique_id = '{}_{}'.format(self._host, self._binary_sensor_type)
 
    async def async_update(self):
        """Fetch status from DD-WRT."""

#        _LOGGER.debug("DdwrtSensor::async_update for %s", self._binary_sensor_type)

    async def async_added_to_hass(self):
        """Client entity created."""

        _LOGGER.debug("DdwrtBinarySensor::async_added_to_hass %s", self._binary_sensor_type)

    @property
    def device_info(self):
        """Return the device info."""
        result = {
            ATTR_FRIENDLY_NAME: self._friendly_name,
            "identifiers": {(DOMAIN, self._host)},
            "manufacturer": self._api.results["router_manufacturer"],
            "model": self._api.results["router_model"],
            ATTR_NAME: self._routername,
            "via_device": (DOMAIN),
        }
        _LOGGER.debug("DdwrtBinarySensor::device_info result=%s", result)
        return result

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._binary_sensor_type

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
        if self._api.results[self._binary_sensor_type]:
            return self._icon
        else:
            return self._icon_off

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._api.results[self._binary_sensor_type]

    @property
    def state(self):
        """Return the state of the binary sensor."""
        return self._api.results[self._binary_sensor_type]

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

