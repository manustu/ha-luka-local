"""Poll the mirror and serialize light controls."""
from datetime import timedelta
import logging

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .protocol import LukaClient, LukaError

_LOGGER = logging.getLogger(__name__)


class LukaCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client: LukaClient) -> None:
        super().__init__(hass, _LOGGER, name="Luka Mirror",
                         update_interval=timedelta(seconds=10), always_update=False)
        self.client = client

    async def _async_update_data(self):
        try:
            return await self.client.get_state()
        except LukaError as err:
            raise UpdateFailed(str(err)) from err

    async def async_control(self, **kwargs):
        try:
            state = await self.client.set_state(**kwargs)
        except LukaError as err:
            self.async_set_update_error(UpdateFailed(str(err)))
            raise HomeAssistantError(str(err)) from err
        self.async_set_updated_data(state)
