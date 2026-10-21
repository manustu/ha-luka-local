# Before publishing 0.1.0

- Repository metadata targets `manustu/ha-luka-local`, maintained by `@manustu`.
  The public repository has been created; validation and HA testing remain.
- Confirm the user's HA version and test installation there. Verify the declared
  minimum version, or raise it to the oldest version actually tested.
- Run protocol tests, HACS validation and hassfest. GitHub workflows are included,
  but have not yet run remotely. Fix all failures before release.
- Test HA UI setup, duplicate-address prevention, entity availability, brightness,
  white selection, restart, unload/reload and address reconfiguration.
- Check that app/button changes update HA within about 10 seconds. Unplug or
  disconnect the mirror to check unavailable/recovery behaviour.
- Verify that changing settings while the app is open remains reliable.
- Record model and firmware. Only claim support for tested hardware.
- Provide required brand assets/registration for the target HACS/catalog process.
- Review the MIT license and README; replace development status with verified facts.
- Publish a GitHub release after checks pass. Users can initially install via a
  custom repository URL. Submit to `hacs/default` separately when ready.

Do not include the user's packet capture, private network configuration or
credentials in the repository or release archive.
