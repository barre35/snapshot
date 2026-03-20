import logging
import os
import json
import shutil
import aiohttp

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

    async_add_entities([AvailabilitySensor(coordinator, entry)])
    
class AvailabilitySensor(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
    
        self._entry = entry
        
        self._attr_unique_id = f"{entry.entry_id}_availability"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        #self._attr_name = f"{entry.title} Availability"
        self.translation_key = "camera_availability"
        self._attr_has_entity_name = True
        
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": f"{ self._entry.title }",
            "manufacturer": "@barre35",
            "model": "Camera Snapshot",
        }
    
    async def async_update(self):
        _LOGGER.error(f"Update { self.platform.config_entry.data.get('url','') }")
        self._attr_native_value = True
      
    @property
    def icon(self):
        if self.is_on:
            return "mdi:shield-check"
        return "mdi:shield-alert"
    
    @property
    def is_on(self):
        if self.coordinator.data:
            return self.coordinator.data.get("availability", False)
        return False

    @property
    def extra_state_attributes(self):
        if self.coordinator.data:
            return {
                "status_code": self.coordinator.data.get("status_code"),
                "url": self.coordinator.data.get("url"),                
            }
        return {}
    

