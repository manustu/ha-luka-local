"""Direct percentage brightness control in the device controls."""
from homeassistant.components.number import NumberEntity, NumberMode

from .const import DOMAIN
from .entity import LukaEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([LukaBrightness(hass.data[DOMAIN][entry.entry_id], entry)])


class LukaBrightness(LukaEntity, NumberEntity):
    _attr_name = "Brightness"
    _attr_icon = "mdi:brightness-6"
    _attr_native_min_value = 1
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "brightness")

    @property
    def native_value(self):
        return self.coordinator.data.brightness

    async def async_set_native_value(self, value):
        # Like the app, adjusting brightness switches the main light on.
        await self.coordinator.async_control(power=True, brightness=round(value))
