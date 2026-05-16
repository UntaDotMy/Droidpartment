# Platform packages

These directories are populated and published by `.github/workflows/release.yml` on tag push.

Each platform package looks like:

```
platform-packages/cli-<os>-<arch>/
  package.json     # generated at release time
  bin/dpt(.exe)    # built Rust binary copied from cargo target
```

Published as `@droidpartment/cli-<os>-<arch>` on npm. The main `droidpartment`
package lists them under `optionalDependencies`, so npm picks the right one
based on the host's `os` and `cpu` constraints.

Supported targets:

- `@droidpartment/cli-darwin-arm64`
- `@droidpartment/cli-darwin-x64`
- `@droidpartment/cli-linux-arm64`
- `@droidpartment/cli-linux-x64`
- `@droidpartment/cli-win32-x64`

You can also build locally:

```bash
cd rust
cargo build --release
```

The installer (`bin/install.js`) finds the binary in this order:

1. Resolved optional dependency (released to npm)
2. Local Rust build (`rust/target/release/dpt[.exe]`)

If neither is available it prints a helpful error.
