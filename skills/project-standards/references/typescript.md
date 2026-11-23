# TypeScript toolchain

Applies to every TS/JS project: web apps, CLIs, libraries, mobile.

| Layer | Standard |
|---|---|
| Package manager | **pnpm**, version pinned in `packageManager`; `corepack enable pnpm` |
| Runtime | **Node 24** LTS (`.nvmrc`, `engines`) |
| Language | **TypeScript 7** (native compiler); **6.x** only where a tool needs the TS JS API (typescript-eslint, some framework type-check steps) |
| Modules | ESM only (`"type": "module"`) |
| Lint + format | **Biome** (one binary); add a framework's ESLint config only where its rules matter (eslint-config-expo, eslint-config-next) |
| Tests | **Vitest**; **jest-expo** for Expo apps only |
| Type checking | `tsc --noEmit` (pre-push and CI) |

## tsconfig (strict)

```jsonc
{
  "compilerOptions": {
    "target": "es2024",
    "module": "nodenext",            // "esnext" + "moduleResolution": "bundler" for Vite/Expo
    "moduleResolution": "nodenext",
    "strict": true,
    "noUncheckedIndexedAccess": true, // arr[i] and obj[key] may be undefined
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "verbatimModuleSyntax": true,     // type-only imports say `import type`
    "erasableSyntaxOnly": true,       // no enums/namespaces/parameter properties
    "isolatedModules": true,
    "allowImportingTsExtensions": true,
    "skipLibCheck": true,
    "noEmit": true
  }
}
```

- `noUncheckedIndexedAccess` forces a decision for the missing case: empty
  arrays, absent keys, lookups that miss.
- `erasableSyntaxOnly` keeps the code "JavaScript with types", so Node can
  run it directly. Use `as const` objects or union types instead of enums.
- Relative imports use the `.ts` extension (`import { x } from './x.ts'`).
  Libraries add `"rewriteRelativeImportExtensions": true` so the build emits `.js`.

## Running TypeScript

- Servers, CLIs and scripts: Node runs the source directly (`node src/cli.ts`),
  with no build step and no tsx. The same command runs in development and
  production.
- Path aliases (`@/…`) only in bundled code (Vite, Next, Expo); Node ignores
  tsconfig `paths`.
- tsx only as a fallback, when something truly needs non-erasable syntax.

## Builds

| Shape | Build |
|---|---|
| Library | `tsc -p tsconfig.build.json` → `dist/` with `.d.ts` |
| Front end | Vite |
| Next / Expo | the framework's own build |
| Server / CLI | none (Node runs the source); typecheck separately |

## pnpm notes

- pnpm blocks dependency install scripts unless allowed. Allow only what needs
  them, in `pnpm-workspace.yaml`:
  ```yaml
  allowBuilds:
    prisma: true
    "@prisma/engines": true
  ```
- Dev tooling belongs in `devDependencies`. pnpm's strictness means an
  undeclared import fails instead of working by accident.
- Workspaces (`apps/*`, `packages/*`) once a repo has a second app.

## Scripts every package.json has

`lint` (`biome check .`), `format` (`biome check --write .`), `typecheck`
(`tsc --noEmit`), `test` (`vitest run`), plus `build`/`dev`/`start` as the
shape needs. Hooks and CI call these names, so keep them.

## Biome

Shared config (from the templates): 2-space indent, 100 columns, single
quotes, recommended rules, organize imports, git-ignore aware. Exclude
generated code (`src/generated`), vendored shadcn components
(`src/components/ui`) and Copier answer files. For Tailwind projects enable
`"css": { "parser": { "tailwindDirectives": true } }`.
