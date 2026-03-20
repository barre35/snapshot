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

class SnapshotOptionsFlow(config_entries.OptionsFlow):

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
        
            new_data = {**self.config_entry.data, **user_input}
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, 
                title=f"{user_input['name']}",
                data=new_data
            )
            
            return self.async_create_entry(title="", data={})
            
        # --------------------------
        # Formulaire de modification         
        # --------------------------
        
        data = self.config_entry.data
        
        return self.async_show_form(
            step_id="init", 
            data_schema=vol.Schema({
                vol.Required("name", default=data.get("name")): str,
                vol.Required("url", default=data.get("url")): str,
                vol.Required("delay", default=data.get("delay")): vol.Coerce(int),
            }),
            errors=errors
        )
                
# ============================
# Config flow pour la création
# ============================

class SnapshotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    # ===================
    # Option flow handler
    # ===================
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):    
        return SnapshotOptionsFlow()
        
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
                data = user_input
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
        
