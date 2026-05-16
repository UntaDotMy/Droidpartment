# Droidpartment plugin source

This directory is the source layout for distributing Droidpartment as a
Factory plugin via the plugin marketplace, as documented at
[Plugins](https://docs.factory.ai/cli/configuration/plugins).

## Layout

```
templates/plugin/
  .factory-plugin/
    plugin.json     # plugin manifest
  hooks/
    hooks.json      # plugin hook registrations using ${DROID_PLUGIN_ROOT}
  bin/dpt(.exe)     # populated by the release pipeline
  droids/           # symlinked or copied at publish time
  skills/           # symlinked or copied at publish time
```

## Use the npm install path instead

If you installed via `npx droidpartment install`, you already have:

- `~/.factory/bin/dpt(.exe)`
- `~/.factory/droids/dpt-*.md`
- `~/.factory/skills/droidpartment/SKILL.md`
- Hooks registered in `~/.factory/settings.json`

The plugin source here exists for marketplace distribution only and is **not**
auto-installed by the npm path to avoid duplicate hook registrations.

## Future: marketplace install

When the marketplace is published, users will be able to do:

```bash
droid plugin marketplace add https://github.com/UntaDotMy/Droidpartment
droid plugin install droidpartment@droidpartment
```

That path skips the `npx` step entirely.
