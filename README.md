# Luka Mirror for Home Assistant

Unofficial local control of Luka LED mirrors with Alexa built-in. No Alexa login,
cloud token, MQTT broker or additional container is required by this integration.

**Development build:** verified against one physical mirror. Home Assistant
installation testing is still pending. This is
not yet listed in the HACS default catalog and has no affiliation with Luka, Sensio or Amazon.

## Features

- Main light: on/off and brightness.
- Separate Brightness slider (1-100%) in the device controls. Adjusting it turns
  the main light on. Use the main light toggle to turn it off.
- White preset selector: Warmest, Warm, Cool and Coolest.
- State polling every 10 seconds, including changes made using the app or buttons.
- Unavailable state on connection failures and automatic retry on the next poll.
- UI setup and address reconfiguration.

Selecting a white preset turns the main light on, matching the Luka app. The
selector intentionally does not present calibrated Kelvin values: the four
protocol codes differ from the manufacturer's advertised colour temperatures.

Night light, demister, audio and Alexa controls are not included. Compatibility
with other Luka models, cabinets and firmware versions has not been verified.

## Manual installation (including Home Assistant Container on Unraid)

1. Copy `custom_components/luka_mirror` into your HA configuration directory's
   `custom_components` folder. Inside the container the result must be
   `/config/custom_components/luka_mirror/manifest.json`.
2. On Unraid, use the host folder mapped to the HA container's `/config` path.
   Do not copy into the container's temporary filesystem.
3. Restart Home Assistant.
4. Open **Settings > Devices & services > Add integration > Luka Mirror**.
5. Enter your mirror's IP address or hostname.

The proposed minimum HA version is 2025.1; this must be verified before release.
HA must be able to connect to TCP port 8899 on the mirror. Discovery multicast
and Docker host networking are not required by this integration.

Reserve the mirror's address in your router if possible. If it changes, use the
integration's Reconfigure action. This preserves the existing entity IDs. Without
a verified hardware identifier, duplicate prevention uses the entered address;
do not add the same mirror again using a different hostname or alias.

## HACS custom repository installation

Add `https://github.com/manustu/ha-luka-local` as a custom repository of category
**Integration**, download Luka Mirror, restart HA and follow UI setup above.
Catalog listing is a separate reviewed submission; no catalog listing is claimed.

## Development

Run `python -m unittest discover -s tests -v`. The protocol module is standard
library only. Tests use a local emulated mirror and do not change real devices.
See [protocol notes](docs/protocol.md) and [release checklist](docs/release.md).

The included raw-traffic analysis is represented only by documented commands;
personal packet captures must not be committed. Contributions should include
model/firmware information and sanitized protocol examples.

## License

MIT. Brand and product names belong to their respective owners.
