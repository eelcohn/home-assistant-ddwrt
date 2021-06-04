"""DD-WRT camera (usage statistics) - Eelco Huininga 2019-2020."""

import logging

from homeassistant.components.camera import Camera

from . import (
    ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME,
    ATTR_ICON,
    ATTR_NAME,
    ATTRIBUTION,
    CAMERAS,
    CONF_RESOURCES,
    CONF_HOST,
    CONF_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the DD-WRT camera."""

    _LOGGER.debug("async_setup_entry: called")

    cameras = []
    for camera_type in config_entry.data[CONF_RESOURCES]:
        if camera_type in CAMERAS:
            _LOGGER.debug("async_setup_entry: host=%s setup for %s", config_entry.data[CONF_HOST], camera_type)
            cameras.append(DdwrtCamera(
                hass.data[DOMAIN][config_entry.data[CONF_HOST]]['entity'],
                config_entry.data[CONF_NAME],
                camera_type,
            )
    )

    async_add_entities(cameras, True)


class DdwrtCamera(Camera):
    """Representation of a ddwrt camera (usage statistics)."""

    def __init__(self, api, routername, camera_type):
        """Initialize the camera."""

        _LOGGER.debug("DdwrtCamera::__init__")

        super().__init__()

        self._api = api
        self._camera_type = camera_type
        self._host = self._api._host
        self._icon = CAMERAS[self._camera_type][ATTR_ICON]
        self._friendly_name = CAMERAS[self._camera_type][ATTR_NAME]
        self._routername = routername
        self._unique_id = '{}_{}'.format(self._host, self._camera_type)
 
    async def async_update(self):
        """Fetch status from DD-WRT."""

#        _LOGGER.debug("DdwrtSensor::async_update for %s", self._camera_type)

    async def async_added_to_hass(self):
        """Client entity created."""

        _LOGGER.debug("DdwrtCamera::async_added_to_hass camera_type=%s", self._camera_type)

    async def async_camera_image(self):
        return self._api.results[self._camera_type]

    @property
    def brand(self):
        """Return the camera brand."""
        return self._api.results["router_manufacturer"]

    @property
    def device_info(self):
        """Return the device info."""
        result = {
            ATTR_FRIENDLY_NAME: self._friendly_name,
            "identifiers": {(DOMAIN, self._host.lower())},
            "manufacturer": self._api.results["router_manufacturer"],
            "model": self._api.results["router_model"],
            ATTR_NAME: self._routername,
            "via_device": (DOMAIN),
        }
        _LOGGER.debug("DdwrtBinarySensor::device_info result=%s", result)
        return result

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attr = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "video_url": self._api.results[self._camera_type],
        }
        return attr

    @property
    def icon(self):
        """Return the mdi icon of the sensor."""
        return self._icon

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._camera_type

    @property
    def state(self):
        """Return the state of the binary sensor."""
        return self._api.results[self._camera_type]

    @property
    def type(self):
        """Return the camera brand."""
        return self._api.results["router_model"]

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

