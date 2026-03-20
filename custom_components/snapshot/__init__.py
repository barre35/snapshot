import logging
import uuid
import voluptuous as vol
import json
import os
import shutil

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import label_registry as lr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.service import async_set_service_schema
from homeassistant.helpers.storage import Store
from homeassistant.helpers.network import get_url
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from datetime import datetime, timedelta

from .coordinator import SnapshotDataUpdateCoordinator
from .const import DOMAIN, PLATFORM, STORAGE_VERSION, STORAGE_KEY

_LOGGER = logging.getLogger(__name__)

# =================
# Setup integration
# =================

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    
    _LOGGER.debug(f"Setup {DOMAIN} integration.")
    
    # Gestion du stockage local
    store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry.entry_id}")
    stored_data = await store.async_load() or {}
    
    # Création du Coordinateur
    coordinator = SnapshotDataUpdateCoordinator( hass, entry)
           
    # Premier rafraîchissement   
    await coordinator.async_config_entry_first_refresh()
    
    # Stockage centralisé dans hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "store": store,
        "data": stored_data
    }

    # Enregistrement du listener pour les modifications d'options
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    # Chargement des plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORM)

    return True

# ==========================
# Modification d'integration
# ==========================

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    coordinator.config_entry = entry
    
    new_delay = entry.data.get("delay", 5)    
    coordinator.update_interval = timedelta(seconds=new_delay)
    
    _LOGGER.info("Update scheduler timer with %s seconds", new_delay)
    
    await coordinator.async_refresh()
    
# ==================
# Unload integration
# ==================

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    _LOGGER.debug(f"Unload {DOMAIN} integration.")
    
    # Déchargement des plateformes
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORM)
    
    if unload_ok:
    
        # Arrête le coordinator
        if hass.data[DOMAIN].get(entry.entry_id) and "coordinator" in hass.data[DOMAIN].get(entry.entry_id):
        
            hass.data[DOMAIN].get(entry.entry_id)["coordinator"] = None
        
        # Netoyage du domaine
        if not hass.data[DOMAIN]:
   
            hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
    
