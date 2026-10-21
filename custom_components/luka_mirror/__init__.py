"""Unofficial local control of Luka mirror lights."""
from homeassistant.const import CONF_HOST, Platform

from .const import DOMAIN
from .coordinator import LukaCoordinator
from .protocol import LukaClient

PLATFORMS = [Platform.LIGHT, Platform.NUMBER, Platform.SELECT]


async def async_setup_entry(hass, entry):
    coordinator = LukaCoordinator(hass, LukaClient(entry.data[CONF_HOST]))
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        return True
    return False
