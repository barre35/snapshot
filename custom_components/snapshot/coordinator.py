import logging
import async_timeout

from datetime import datetime
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import datetime, timedelta
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

class SnapshotDataUpdateCoordinator(DataUpdateCoordinator):

    # ============
    # Constructeur
    # ============
    
    def __init__(self, hass, entry):
    
        super().__init__(
            hass,
            _LOGGER,
            name=f"{entry.title} Coordinator",
            update_interval=timedelta(seconds=entry.data.get("delay", 5)),
        )
    
        self.config_entry = entry

    async def async_set_update_interval(self, active: bool):
        if active:
            delay = self.config_entry.data.get("delay", 5)
            self.update_interval = timedelta(seconds=delay)
            _LOGGER.debug("Coordinator updated (%ss)", delay)
            await self.async_request_refresh()
        else:
            self.update_interval = None
            _LOGGER.debug("Coordinator disabled")
            
    async def _async_update_data(self):
    
        now = datetime.now()          
            
        url = self.hass.config_entries.async_get_entry(self.config_entry.entry_id).data.get("url", "")
        
        try:
            session = async_get_clientsession(self.hass)
            
            async with async_timeout.timeout(10):
            
                response = await session.get(url)
            
                if response.status != 200:
                    _LOGGER.error("Snapshot failed with satus %s for %s", response.status, url)
                    raise UpdateFailed(f"Erreur HTTP : {response.status}")
                
                _LOGGER.info("Connection with status %s for %s", response.status, url)
            
                image_bytes = await response.read() if response.status == 200 else None
                        
                return {
                    "availability": response.status < 400,
                    "status_code": response.status,
                    "last_check": now,
                    "url": url,
                    "content": image_bytes,
                }

        except UpdateFailed:
            raise
        
        except Exception as err:
            _LOGGER.error("Connection error %s for %s", err, url)
            raise UpdateFailed(f"Unable to connect {err}")
