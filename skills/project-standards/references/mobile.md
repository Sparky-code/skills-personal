# Mobile (Expo)

| Layer | Standard |
|---|---|
| Platform | **Expo** (managed; `npx expo prebuild` only when native code is needed). Firm. |
| SDK policy | Stay **within one SDK of the latest**; upgrade every release. Firm. |
| Routing | **expo-router** (file-based, typed routes) |
| Styling | `StyleSheet` + `design/tokens.ts`, which mirrors `tokens.css`, checked by `node design/check-tokens.ts` (in CI) |
| Server data / state | TanStack Query; Zustand when needed; built-in `fetch` (no axios) |
| On-device data | expo-sqlite + **Drizzle** (drizzle-kit migrations), the one exception to "Prisma for TS" |
| Tests | **jest-expo** + React Native Testing Library; Maestro end-to-end only once the app ships |
| Builds | EAS Build for store builds, EAS Update for over-the-air fixes; `npx expo run:ios` locally |
| Lint/format | Biome + eslint-config-expo |
| TypeScript | stay on the TS version Expo's tooling supports (6.x until Expo supports 7) |

## Starting an app

```bash
pnpm create expo-app my-app
~/code/templates/bin/new-project expo my-app
```

The baseline adds hooks, CI, docs, and `design/` (`tokens.css`, `tokens.ts`,
`check-tokens.ts`).

## Why

- SDK upgrades are easy one step at a time and painful several at once; two
  apps on different SDKs is where drift starts.
- React Native has no CSS variables or `oklch()`, so the tokens are mirrored
  as hex in `tokens.ts`; the drift check converts and compares so the two
  files can't silently diverge.
- Expo's testing story assumes Jest; fighting that isn't worth it.

## Sharing code with a web app

Pure TypeScript logic (types, calculations, validation) goes in
`packages/core` in a pnpm workspace; the web and mobile apps both import it.
UI code isn't shared.
