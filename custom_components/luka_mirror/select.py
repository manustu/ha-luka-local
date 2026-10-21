"""Expose discrete whites without asserting unverified Kelvin calibration."""
from homeassistant.components.select import SelectEntity

from .const import DOMAIN
from .entity import LukaEntity
from .protocol import PRESETS


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([LukaWhitePreset(hass.data[DOMAIN][entry.entry_id], entry)])


class LukaWhitePreset(LukaEntity, SelectEntity):
    _attr_name = "White preset"
    _attr_icon = "mdi:thermometer"
    _attr_options = list(PRESETS)

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "white_preset")

    @property
    def current_option(self):
        return next((name for name, value in PRESETS.items()
                     if value == self.coordinator.data.temperature), None)

    async def async_select_option(self, option):
        # Match the app: switching white preset also turns the main light on.
        await self.coordinator.async_control(power=True, temperature=PRESETS[option])
