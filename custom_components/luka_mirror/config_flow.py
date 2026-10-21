"""Manual setup; the protocol has not exposed a stable hardware ID."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST

from .const import DOMAIN
from .protocol import LukaClient, LukaError


class LukaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return await self._form("user", user_input)

    async def async_step_reconfigure(self, user_input=None):
        return await self._form("reconfigure", user_input)

    async def _form(self, step, user_input):
        errors = {}
        entry = self._get_reconfigure_entry() if step == "reconfigure" else None
        if user_input is not None:
            host = user_input[CONF_HOST].strip().lower()
            if not host or any(c.isspace() for c in host) or "://" in host or "/" in host:
                errors["host"] = "invalid_host"
            elif any(e.data[CONF_HOST] == host and e != entry
                     for e in self._async_current_entries()):
                return self.async_abort(reason="already_configured")
            else:
                try:
                    await LukaClient(host).get_state()
                except LukaError:
                    errors["base"] = "cannot_connect"
                else:
                    if entry is not None:
                        return self.async_update_reload_and_abort(
                            entry, data_updates={CONF_HOST: host})
                    return self.async_create_entry(title="Luka Mirror", data={CONF_HOST: host})
        default = user_input.get(CONF_HOST, "") if user_input else (
            entry.data[CONF_HOST] if entry else "")
        return self.async_show_form(step_id=step, data_schema=vol.Schema({
            vol.Required(CONF_HOST, default=default): str,
        }), errors=errors)
