import voluptuous as vol
import logging

from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from awesomeversion import AwesomeVersion
from homeassistant.const import __version__ as HAVERSION

_LOGGER = logging.getLogger(__name__)
        
# ================================
# Config flow pour la modification
# ================================

class SnapshotOptionsFlowHandler(config_entries.OptionsFlow):

    VERSION = 1

    # =========
    # Main flow
    # =========
    
    async def async_step_init(self, user_input=None):    
        
        _LOGGER.info("Update instance '%s'", user_input)
        errors = {}
        
        # =======================
        # Mise à jour des données
        # =======================

        if user_input is not None:
        
            return self.async_create_entry(title="", data=user_input)
            
        # --------------------------
        # Formulaire de modification         
        # --------------------------
        
        return self.async_show_form(
            step_id="init", 
            data_schema=vol.Schema({
                vol.Required("url", default=self.config_entry.options.get("url")): str,
                vol.Required("delay", default=self.config_entry.options.get("delay")): vol.Coerce(int),
            }),
            errors=errors
        )
                
# ============================
# Config flow pour la création
# ============================

class SnapshotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    # =========
    # Main flow
    # =========
    
    async def async_step_user(self, user_input=None):
        
        _LOGGER.info("Create instance '%s'", user_input)
        errors = {}
        
        # ====================
        # Création des données
        # ====================
        
        if user_input is not None:
       
            return self.async_create_entry(
                title=f"{user_input['name']}",
                data = {
                },
                options={
                    "url": user_input["url"],
                    "delay": user_input["delay"], 
                }
            )
            
        # ====================
        # Formulaire de saisie
        # ====================
        
        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required("name", default=""): str,
                vol.Required("url", default=""): str,
                vol.Required("delay", default=60): vol.Coerce(int),
            }),
            errors=errors
        )
        
    # =======================
    # Allow modification flow
    # =======================
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> SnapshotOptionsFlowHandler:
    
        return SnapshotOptionsFlowHandler() # Retirez 'config_entry' ici
        
