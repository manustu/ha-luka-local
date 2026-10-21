# Observed light protocol

Confirmed with an Android Luka app capture and physical tests on 21 October 2026.

Transport: direct TCP port 8899. No authentication exchange was needed for the
tested commands. This does not establish whether every firmware version behaves
the same or whether the mirror's other functions require internet access.

Each frame contains a 20-byte header followed by ASCII payload:

| Offset | Length | Meaning |
| --- | --- | --- |
| 0 | 4 | Magic bytes `18 96 18 20` |
| 4 | 4 | Little-endian payload byte count |
| 8 | 12 | Zero in captured requests; response metadata not interpreted |

Responses contain nonzero bytes at offset 8, consistent with a payload byte sum;
the client currently ignores this metadata. TCP may split or combine frames, so
the client reads the full header and then the exact declared payload length.
Responses above 4096 bytes are rejected; exchanges have a five-second deadline.

Commands:

```text
MCU+PAS+GetStatus&
MCU+PAS+{"light_power":"ON"}&
MCU+PAS+{"light_power":"OFF"}&
MCU+PAS+{"percentage": 25}&
MCU+PAS+{"colorTemperature":2200}&
```

The space after the colon in `percentage` is required on the tested device.
Compact JSON for brightness produced no acknowledgement and no state change.
The other setters use the compact formatting observed in the app.

Status returns three separate frames with `light_power`, `percentage` and
`colorTemperature`. Setters echo the updated field. The client waits for each
echo and obtains a complete status after a control transaction.

Observed white codes: 2200, 2700, 5500, 7000. These are exposed as Warmest, Warm,
Cool and Coolest rather than claimed physical Kelvin temperatures. No continuous
temperature support is claimed. Brightness 25%, 45%, 85% and all four white codes
were acknowledged; the user confirmed physical changes. Other brightness values
occurred in the app capture; exact endpoint behaviour still needs HA testing.

No night-light command was present in the supplied capture. Do not guess MCU
commands. Future support should be based on a separate capture or documentation.
