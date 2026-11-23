# Project scaffolding

## Use the template (preferred)

```bash
git clone https://github.com/Sparky-code/templates ~/code/templates   # once
~/code/templates/bin/new-project react-web ~/code/my-app                       # app + Hono API
~/code/templates/bin/new-project react-web ~/code/my-app --data with_api=false # client only
```

You get Vite + React + TypeScript, Tailwind v4 with the `@theme` token
mapping, `src/styles/tokens.css`, shadcn on Radix (`components.json`, a sample
`Button`, `cn()`), Inter, a light/dark toggle, Vitest + Testing Library, Biome,
and the baseline (hooks, CI, docs). See the `project-standards` skill for the
rest of the shape.

## Manual setup (only when the template can't be used)

```bash
pnpm create vite my-app --template react-ts
cd my-app
pnpm add -D tailwindcss @tailwindcss/vite @biomejs/biome vitest
pnpm add @fontsource-variable/inter lucide-react
pnpm dlx shadcn@latest init
pnpm dlx shadcn@latest add button
```

Then copy `tokens.css` from the templates repo (`shared/tokens.css`) to
`src/styles/tokens.css`, and the `@theme inline` block from the react-web
template's `src/styles/globals.css` (`tailwind-config.md`). Wire the tokens
before writing any component.

## Maps

```bash
pnpm add maplibre-gl            # + pmtiles for single-file vector tiles
```

Style the map's UI (controls, popups, side panels) with tokens like any other
surface. For map-first apps without React, see branch 3 in `decision-tree.md`.

## When to add routing

- Skip it for a single view, a focused tool or a demo.
- Add React Router (`pnpm add react-router`) once there's more than one real
  view or URL-addressable state (deep links, back/forward).

## When to add TanStack Query

As soon as the app talks to a real API: more than one component needs the
same server data, or you're about to hand-roll loading/error/cache logic in
`useEffect`. With the react-web API, call the typed client (`hono/client`)
inside query functions.

## Next.js (the SSR/SEO exception)

```bash
pnpm create next-app my-site --ts --tailwind --eslint --app --src-dir --use-pnpm
~/code/templates/bin/new-project next my-site
cd my-site && pnpm dlx shadcn@latest init
```

The baseline adds `design/tokens.css`; import it from the global stylesheet
and add the same `@theme inline` mapping. Tokens, theme mapping and shadcn
components are framework-agnostic; browser-only code (a theme toggle reading
`localStorage`) needs a client component. Read the generated `AGENTS.md`:
Next's own rules for its current version.

## Verifying a scaffold

1. `pnpm dev`: the app boots.
2. In DevTools, `:root` has the `--primary`, `--space-*` variables, and
   `bg-primary` resolves to the token value, not Tailwind's default palette.
3. The theme toggle repaints everything; the OS dark setting is followed when
   no theme is forced.
4. `pnpm run lint`, `pnpm run typecheck`, `pnpm run test`, `pnpm run build` all pass.
