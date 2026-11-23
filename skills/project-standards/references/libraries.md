# Libraries

Template: `ts-library`. The shape below is firm.

## Package shape

- ESM only, `"type": "module"`.
- `exports` with a subpath per module (`".": …`, `"./geometry": …`), each with
  `types` and `default`; consumers import only what they use.
- `"sideEffects": false`, a `files` allowlist (`["dist"]`), emitted `.d.ts`,
  `engines`.
- **No runtime dependencies by default.** Anything environment-specific (a
  `fetch`, a clock, `sleep`, a logger) is passed in as an option with a
  sensible default. The library then runs in the browser, in Node and
  unbundled, and tests can substitute the environment.
- Build with `tsc -p tsconfig.build.json` (source imports use `.ts`;
  `rewriteRelativeImportExtensions` emits `.js`). A bundler adds value only
  when publishing dual CommonJS/ESM to npm.

## Distribution

- **While private: vendor it.** `pnpm run vendor -- <app>/vendor/<name>` builds
  and copies the compiled files, a trimmed package.json and a `VENDORED.md`
  (version, tag, commit) into the app, which commits the copy. Apps with a
  bundler depend on it as `"<name>": "file:vendor/<name>"`; apps without a
  build import the files directly. No registry, no tokens in CI, each app pins
  and reviews its copy. Never edit a vendored copy; change the library and
  vendor again.
- **When public: publish to npm** from CI with provenance, and keep the vendor
  script for no-build apps.
- A library and its only app in the same repo: a pnpm workspace instead.

## Versioning

- Semver with git tags (`v0.3.1`); 0.x until the public 1.0 (a 0.x minor may break).
- `CHANGELOG.md` by hand, in Keep a Changelog format; every release has an entry.
- A breaking change is a major bump (minor while 0.x) with a changelog entry
  saying what to change.
- Release automation (release-please, changesets) only once releases are frequent.
- With npm, change versions with `npm version <x> --no-git-tag-version` or by
  hand; regenerating a lockfile with `--package-lock-only` on macOS can drop
  other platforms' optional binaries and break CI.

## Quality bar

- Every export has tests (Vitest) and is documented in the README: what it
  takes, what it returns, edge cases.
- CI: typecheck, test, build on every PR.
- Before changing an algorithm, check old vs new on generated inputs
  (differential testing) and record intended differences.

## Licence and name

- MIT for anything that may go public.
- Before going public, check the name on npm and GitHub.

## Python libraries

Same principles: `uv init --lib`, `src/` layout, no runtime dependencies by
default, `uv build`, publish to PyPI from CI when public.
