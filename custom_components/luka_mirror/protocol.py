"""Local Luka light protocol, observed on TCP port 8899.

This module deliberately has no Home Assistant dependencies.
"""
from __future__ import annotations

import asyncio
import json
import struct
from dataclasses import dataclass

MAGIC = bytes.fromhex("18961820")
PORT = 8899
# Device codes run opposite to Kelvin ordering, confirmed on the physical mirror.
PRESETS = {"Warmest": 7000, "Warm": 5500, "Cool": 2700, "Coolest": 2200}
FIELDS = {"light_power", "percentage", "colorTemperature"}


class LukaError(Exception):
    """Communication failed or the device returned invalid data."""


@dataclass(frozen=True)
class LightState:
    power: bool
    brightness: int
    temperature: int


def encode(command: str) -> bytes:
    payload = command.encode("ascii")
    return MAGIC + struct.pack("<I", len(payload)) + bytes(12) + payload


def command_for(key: str, value: object) -> str:
    if key == "light_power" and value in ("ON", "OFF"):
        return f'MCU+PAS+{{"light_power":"{value}"}}&'
    if key == "percentage" and type(value) is int and 0 <= value <= 100:
        # The device ignores this command without the space after the colon.
        return f'MCU+PAS+{{"percentage": {value}}}&'
    if key == "colorTemperature" and type(value) is int and value in PRESETS.values():
        return f'MCU+PAS+{{"colorTemperature":{value}}}&'
    raise ValueError(f"Unsupported value for {key}")


def parse_state(data: dict) -> LightState:
    power = data.get("light_power")
    brightness = data.get("percentage")
    temperature = data.get("colorTemperature")
    if (power not in ("ON", "OFF") or type(brightness) is not int
            or not 0 <= brightness <= 100 or type(temperature) is not int
            or temperature <= 0):
        raise LukaError("Invalid or incomplete light state")
    return LightState(power == "ON", brightness, temperature)


class LukaClient:
    def __init__(self, host: str, port: int = PORT, timeout: float = 5) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._lock = asyncio.Lock()

    async def _exchange(self, command: str, expected: set[str]) -> dict:
        writer = None
        try:
            async with asyncio.timeout(self.timeout):
                reader, writer = await asyncio.open_connection(self.host, self.port)
                writer.write(encode(command))
                await writer.drain()
                result = {}
                for _ in range(32):
                    header = await reader.readexactly(20)
                    length = struct.unpack_from("<I", header, 4)[0]
                    if header[:4] != MAGIC or not 1 <= length <= 4096:
                        raise LukaError("Invalid response frame")
                    payload = await reader.readexactly(length)
                    if not payload.startswith(b"MCU+PAS+{") or not payload.endswith(b"&"):
                        continue
                    value = json.loads(payload[8:-1])
                    if not isinstance(value, dict):
                        raise LukaError("Invalid response object")
                    result.update({k: v for k, v in value.items() if k in FIELDS})
                    if expected <= result.keys():
                        return result
                raise LukaError("Too many unrelated response frames")
        except (OSError, TimeoutError, asyncio.IncompleteReadError,
                ValueError, UnicodeError) as err:
            raise LukaError("Unable to communicate with the mirror") from err
        finally:
            if writer is not None:
                writer.close()
                try:
                    async with asyncio.timeout(1):
                        await writer.wait_closed()
                except (OSError, TimeoutError):
                    pass

    async def get_state(self) -> LightState:
        async with self._lock:
            return parse_state(await self._exchange("MCU+PAS+GetStatus&", FIELDS))

    async def set_state(self, *, power: bool | None = None,
                        brightness: int | None = None,
                        temperature: int | None = None) -> LightState:
        # Validate the entire request before making any changes.
        commands = []
        if power is not None:
            if type(power) is not bool:
                raise ValueError("Power must be boolean")
            commands.append(("light_power", "ON" if power else "OFF"))
        if brightness is not None:
            commands.append(("percentage", brightness))
        if temperature is not None:
            commands.append(("colorTemperature", temperature))
        encoded = [(key, value, command_for(key, value)) for key, value in commands]
        async with self._lock:
            for key, value, command in encoded:
                reply = await self._exchange(command, {key})
                if reply[key] != value:
                    raise LukaError(f"Mirror did not confirm {key}")
            return parse_state(await self._exchange("MCU+PAS+GetStatus&", FIELDS))
