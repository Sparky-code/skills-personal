# Project Scaffolding

Two ways to start a new project: scaffold fresh with the commands below, or copy the boilerplate template directly once it exists.

## Option A — copy the template (preferred once it exists)

```bash
cp -r /Users/sparky/Code/templates/react-vite-material /Users/sparky/Code/<new-project-name>
cd /Users/sparky/Code/<new-project-name>
npm install
npm run dev
```

This gets you the compiled tokens, Tailwind `@theme` wiring, shadcn/Base UI already configured, and the `use-theme` light/dark hook — all pre-verified. Prefer this over scaffolding fresh whenever the template is available.

## Option B — scaffold fresh

```bash
mkdir -p /Users/sparky/Code/templates   # only if provisioning the template itself
cd /Users/sparky/Code
npm create vite@latest <project-name> -- --template react-ts
cd <project-name>
npm install tailwindcss @tailwindcss/vite
npx shadcn@latest init          # configure for Base UI, not the Radix default — see components.md
npx shadcn@latest add button input card dialog badge
npm install -D style-dictionary
npm install lucide-react @fontsource-variable/inter
```

Then wire up `tokens/design-tokens.json` (`design-tokens.md`) and the Style Dictionary config to generate `src/styles/tokens.css`, and add the `@theme` mapping in `src/styles/globals.css` (`tailwind-config.md`).

## When to add routing

- **Skip routing** if the project is a single view/page, a focused tool, or a demo — added complexity isn't earning its keep yet.
- **Add React Router v7** (`npm install react-router`) once there's more than one real navigable view/route, or the project needs URL-addressable state (deep links, back/forward behavior).
- **Consider TanStack Router instead** if the project wants type-safe route params/search-params checked at compile time and the team is comfortable with its file-based conventions — equally valid, pick one and stay consistent within a given project rather than mixing.

## When to add TanStack Query

Add `@tanstack/react-query` as soon as the project touches a real API — any network request beyond a static asset. It's not warranted for a purely local-state prototype or a plain-HTML demo. Signs it's time: more than one component needs the same server data, you're about to hand-roll a loading/error/cache dance with `useEffect`, or requests need retries/dedup/background refetch.

## Next.js scaffold (the SSR/SEO exception)

Only when SSR/SEO is an explicit day-one requirement (see `decision-tree.md`):

```bash
npx create-next-app@latest <project-name> --typescript --tailwind --app
cd <project-name>
npx shadcn@latest init          # configure for Base UI, not the Radix default
npx shadcn@latest add button input card dialog badge
npm install -D style-dictionary
npm install lucide-react @fontsource-variable/inter
```

The design tokens, Tailwind theme, and shadcn/Base UI components port over unchanged — those are framework-agnostic. What does not port: the Vite build config (discarded), and any browser-only code (e.g. `use-theme`'s `localStorage` access) needs SSR-safe guards (check `typeof window !== "undefined"` or defer to a client component) since it now runs somewhere without a `window` on first render.

## Verifying a fresh scaffold works

1. `npm install && npm run dev` — dev server boots clean.
2. DevTools → confirm `--color-*` / `--space-*` custom properties are present on `:root`, and a Tailwind utility like `bg-primary` resolves to the token value, not Tailwind's default palette.
3. Render a shadcn `Button` and `Card` — confirm visible Base UI focus/keyboard behavior (see `accessibility.md`).
4. Toggle the `use-theme` hook — tokens swap live, and the choice persists across a reload.
5. `npx tsc --noEmit` and `npm run build` — both succeed with no errors.
