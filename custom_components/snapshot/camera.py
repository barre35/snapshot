import logging
import os
import json
import shutil
import aiohttp
import async_timeout

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.helpers.aiohttp_client import async_get_clientsession       
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.core import HomeAssistant
from datetime import timedelta
from homeassistant.util import Throttle
from pathlib import Path

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([SnapshotCamera(coordinator, entry)])
    
class SnapshotCamera(CoordinatorEntity, Camera):

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        Camera.__init__(self)

        self._entry = entry

        self._attr_unique_id = f"{entry.entry_id}_camera"
        #self._attr_device_class = ???
        self._attr_name = f"{entry.title} Snaphot Camera"
        
        self._attr_supported_features = CameraEntityFeature.ON_OFF
        
    @property
    def name(self):
        return f"{ self._entry.title } Snaphot Image"
        
    @property
    def is_on(self) -> bool:
        if self.coordinator.data:
            return self.coordinator.last_update_success
        return None
        
    @property
    def is_streaming(self) -> bool:
        if self.coordinator.data:
            return self.coordinator.last_update_success
        return None
    
    @property
    def icon(self):
        if self.coordinator.last_update_success:
            return "mdi:cctv"
        return "mdi:cctv-off"
        
    @property
    def image_url(self):
        if self.coordinator.data:
            return self.coordinator.data.get("url")
        return None

    async def async_turn_on(self) -> None:
        await self.coordinator.async_set_update_interval(True)
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        await self.coordinator.async_set_update_interval(False)
        self.async_write_ha_state()
        
    async def async_camera_image(self, width=None, height=None) -> bytes | None:
        if self.coordinator.data and "content" in self.coordinator.data:
            return self.coordinator.data["content"]
        return None
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": f"{ self._entry.title } Snapshot",
            "manufacturer": "Snapshot",
            "model": "Snapshot Camera",
        }
    
    @property
    def extra_state_attributes(self):
        if self.coordinator.data:
            return {
                "status_code": self.coordinator.data.get("status_code"),
                "url": self.coordinator.data.get("url"),
            }
        return {}  
