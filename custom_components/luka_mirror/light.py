"""Main light power and brightness."""
from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity

from .const import DOMAIN
from .entity import LukaEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([LukaLight(hass.data[DOMAIN][entry.entry_id], entry)])


class LukaLight(LukaEntity, LightEntity):
    _attr_name = None
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "light")

    @property
    def is_on(self):
        return self.coordinator.data.power

    @property
    def brightness(self):
        return round(self.coordinator.data.brightness * 255 / 100)

    async def async_turn_on(self, **kwargs):
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness == 0:
            await self.async_turn_off()
            return
        await self.coordinator.async_control(
            power=True,
            brightness=max(1, round(brightness * 100 / 255)) if brightness is not None else None,
        )

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_control(power=False)
