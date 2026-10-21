"""Exercise the real client against an emulated TCP mirror."""
import asyncio
import importlib.util
import json
from pathlib import Path
import struct
import sys
import unittest

spec = importlib.util.spec_from_file_location(
    "luka_protocol", Path(__file__).parents[1] / "custom_components/luka_mirror/protocol.py")
p = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = p
spec.loader.exec_module(p)


class ProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.state = {"light_power": "OFF", "percentage": 45, "colorTemperature": 7000}
        self.commands = []
        self.mode = "normal"
        self.tasks = set()
        self.server = await asyncio.start_server(self.handle, "127.0.0.1", 0)
        self.client = p.LukaClient("127.0.0.1", self.server.sockets[0].getsockname()[1], .3)

    async def asyncTearDown(self):
        self.server.close()
        await self.server.wait_closed()
        for task in list(self.tasks):
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)

    async def handle(self, reader, writer):
        task = asyncio.current_task()
        self.tasks.add(task)
        try:
            header = await reader.readexactly(20)
            command = (await reader.readexactly(struct.unpack_from("<I", header, 4)[0])).decode()
            self.commands.append(command)
            if self.mode == "timeout":
                await asyncio.sleep(5)
                return
            if self.mode == "bad_header":
                writer.write(b"XXXX" + struct.pack("<I", 50000) + bytes(12))
                await writer.drain()
                return
            if command == "MCU+PAS+GetStatus&":
                values = self.state
            else:
                values = json.loads(command[8:-1])
                if "percentage" in values and '": ' not in command:
                    return
                if self.mode != "reject":
                    self.state.update(values)
                values = {key: self.state[key] for key in values}
            if self.mode == "incomplete":
                values = {"light_power": "OFF"}
            frames = b"".join(p.encode("MCU+PAS+" + json.dumps({key: value}) + "&")
                              for key, value in values.items())
            # Fragment both headers and bodies, including across frame boundaries.
            for offset in range(0, len(frames), 7):
                writer.write(frames[offset:offset + 7])
                await writer.drain()
                await asyncio.sleep(0)
        finally:
            writer.close()
            await writer.wait_closed()
            self.tasks.discard(task)

    async def test_fragmented_status(self):
        self.assertEqual(await self.client.get_state(), p.LightState(False, 45, 7000))

    async def test_controls_and_exact_brightness_spacing(self):
        state = await self.client.set_state(power=True, brightness=25, temperature=2200)
        self.assertEqual(state, p.LightState(True, 25, 2200))
        self.assertIn('MCU+PAS+{"percentage": 25}&', self.commands)
        self.assertEqual((await self.client.set_state(power=False)).power, False)

    async def test_all_presets(self):
        for value in p.PRESETS.values():
            self.assertEqual((await self.client.set_state(temperature=value)).temperature, value)

    async def test_white_labels_follow_observed_device_order(self):
        for name, code in (("Warmest", 7000), ("Warm", 5500),
                           ("Cool", 2700), ("Coolest", 2200)):
            state = await self.client.set_state(temperature=p.PRESETS[name])
            self.assertEqual(state.temperature, code)

    async def test_validate_before_mutation(self):
        for value in (-1, 101, True, 1.5):
            with self.assertRaises(ValueError):
                await self.client.set_state(power=True, brightness=value)
        self.assertEqual(self.commands, [])

    async def test_timeout_recovers(self):
        self.mode = "timeout"
        with self.assertRaises(p.LukaError):
            await self.client.get_state()
        self.mode = "normal"
        self.assertEqual((await self.client.get_state()).brightness, 45)

    async def test_invalid_frame(self):
        self.mode = "bad_header"
        with self.assertRaises(p.LukaError):
            await self.client.get_state()

    async def test_partial_state_is_not_success(self):
        self.mode = "incomplete"
        with self.assertRaises(p.LukaError):
            await self.client.get_state()

    async def test_rejected_command(self):
        self.mode = "reject"
        with self.assertRaises(p.LukaError):
            await self.client.set_state(power=True)

    async def test_concurrent_control_and_poll(self):
        result, state = await asyncio.gather(
            self.client.set_state(power=True, brightness=85), self.client.get_state())
        self.assertEqual(result, state)
        self.assertEqual(state.brightness, 85)

    async def test_disconnect(self):
        self.server.close()
        await self.server.wait_closed()
        with self.assertRaises(p.LukaError):
            await self.client.get_state()

    def test_invalid_state(self):
        with self.assertRaises(p.LukaError):
            p.parse_state({"light_power": "ON", "percentage": 200, "colorTemperature": 2700})

    def test_captured_query_frame(self):
        self.assertEqual(p.encode("MCU+PAS+GetStatus&"),
                         bytes.fromhex("1896182012000000000000000000000000000000")
                         + b"MCU+PAS+GetStatus&")


if __name__ == "__main__":
    unittest.main()
