---
name: frontend-ui-stack
description: Use whenever starting a new frontend project, scaffolding a web app, adding or styling any UI component, choosing colors/spacing/fonts/type sizes, building a map UI, building a quick single-file HTML prototype or demo, or when the user says "our design system" or wants a "Material-style UI". Defines the one default frontend stack and the shared design tokens.
---

# Frontend UI Stack

The default stack for new UI work, unless a project explicitly overrides it.
It sits inside the wider project standards (see the `project-standards` skill
for toolchain, web-app shape and data rules).

The stack: **Vite + React** by default (**Next.js** only when SSR/SEO is needed
from day one; **plain TypeScript + CSS** for UIs that are mostly a map or a
single tool view), **Tailwind CSS v4**, **shadcn/ui on Radix** primitives, one
shared **`tokens.css`** of design tokens, **MapLibre GL** for maps, and
Material Design *principles* (grid, type scale, elevation, color roles), never
the literal MUI component library.

Every new frontend starts from the same tokens and the same primitives so that
colors, spacing, type and component behavior stay consistent across projects
instead of each one improvising its own. This fixes an observed failure:
independent projects separately reinvented badge-color systems and "danger
red" values that didn't agree. One token file, reused everywhere, prevents
that drift, which is why the checklist treats a hard-coded value as a defect.

## Why each layer was picked

- **Vite**: fast dev server and build with no framework lock-in; the right default until SSR/SEO forces Next.js.
- **Tailwind CSS v4**: CSS-first `@theme` config maps directly onto the token variables, so utility classes and tokens are the same values.
- **shadcn/ui on Radix**: component code is copied into the repo (owned, editable, no runtime package for the visual layer); Radix supplies proven, accessible behavior (focus, keyboard, ARIA). Radix is shadcn's default and its most-used path.
- **One hand-written `tokens.css`**: CSS custom properties, vendored into each project from the templates repo (`shared/tokens.css`) and updated with `copier update`. No token compiler to maintain. React Native gets a hex mirror (`tokens.ts`) with a drift check.
- **MapLibre GL**: vector tiles, PMTiles, styling, terrain; works with self-hosted tiles. Leaflet is acceptable for simple raster overlays.
- **Material *principles*, not MUI**: the grid, type scale, elevation and color-role vocabulary are a proven system; MUI's components and look are not used.
- **WCAG 2.2 AA** as the accessibility baseline, mostly satisfied by Radix; see `references/accessibility.md` for what still needs manual checks.

## Canonical sources

- Tokens: `shared/tokens.css` in the templates repo (`gh:Sparky-code/templates`); the values are listed in `references/design-tokens.md`.
- React app scaffold: the templates repo's `react-web` shape (`bin/new-project react-web <dir>`), with Tailwind, shadcn on Radix and the tokens already wired.
- Plain-HTML pattern: `references/plain-html-fallback.md`.

## Defaults beyond the core stack

- **Typography**: Inter as a variable font (`@fontsource-variable/inter`). Don't add a second UI typeface without a stated reason.
- **Icons**: Lucide (shadcn's icon set). Don't mix icon libraries.
- **Client data and state** (guidance): TanStack Query for server data, React Router for single-page routing, Zustand only when shared client state is needed, `fetch` not axios.

## Decision tree

- **New project, no stated SSR/SEO need** → React + Vite (template `react-web`; `--data with_api=false` for client-only).
  Triggers: "start a new frontend project", "scaffold a web app", "build a dashboard/tool/internal app".
- **SSR/SEO explicitly required from day one** → Next.js (`create-next-app`, then the baseline).
  A fork made at project start, not a cheap upgrade later. Don't default to Next "just in case".
  Triggers: "needs to be crawlable/indexed", "server-side rendering", "public marketing site", "per-page meta tags".
- **UI is mostly a map or a single tool view** → plain TypeScript + CSS on Vite, still on `tokens.css`.
  React adds little when the map library draws most of the screen. Accessibility for any dialogs, menus and forms is then on you: keep them few.
  Triggers: "map app", "map with a side panel", "single-screen tool".
- **Single-file prototype, demo, or throwaway** → plain-HTML fallback, importing `tokens.css`.
  Triggers: "quick prototype", "single-file demo", "HTML artifact I can open in a browser".
- **Existing project with its own established frontend stack** → don't impose this skill.
  Flag the conflict and ask how to proceed.

Full trigger phrases and rationale: `references/decision-tree.md`.

## Mandatory checklist for every UI task

- [ ] Never hard-code a color, spacing, radius, shadow, or font-size value; use a token.
  The one exemption: literal sizing values that shadcn's CLI ships inside vendored `src/components/ui/*.tsx` (`ring-[3px]`, `h-9`) stay as-is; normalizing them forks the components away from what `shadcn add` produces. Everything you write is held to the rule.
- [ ] New primitives come from the shadcn CLI (`pnpm dlx shadcn@latest add <name>`); never hand-roll a component shadcn provides.
- [ ] Never override Radix's focus, keyboard, or ARIA behavior (`outline: none`, custom low-contrast focus rings).
- [ ] Verify both dark AND light themes before calling UI work done.
- [ ] Plain-HTML and plain-TS work imports the shared `tokens.css`; it never invents its own colors or spacing.

## Scaffolding

Use the template rather than assembling the stack by hand:

```bash
~/code/templates/bin/new-project react-web <dir>
```

It ships `src/styles/tokens.css`, the `@theme` mapping in `globals.css`, shadcn
configured for Radix (`components.json`), a sample `Button`, Inter, and a
theme toggle. Manual steps, for a project that can't use the template:
`references/project-scaffold.md`.

## Reference index

- `references/design-tokens.md` — every token value (color roles, spacing, type, elevation, radius, motion) and how `tokens.css` is organised. Open before picking any value.
- `references/components.md` — shadcn/ui on Radix: adding and editing components.
- `references/tailwind-config.md` — the `@theme` mapping from tokens to Tailwind utilities and shadcn role names; light/dark strategy; utility-to-token table.
- `references/plain-html-fallback.md` — the zero-build single-file pattern.
- `references/accessibility.md` — WCAG 2.2 AA: what Radix gives for free vs. what to verify.
- `references/project-scaffold.md` — template use, manual setup, maps, routing and data-fetching additions, Next.js.
- `references/decision-tree.md` — the decision tree with trigger phrases.

## Scope

New UI work only. Existing projects that picked a different stack before this
skill keep it unless someone deliberately decides to migrate them; that's a
separate decision this skill should never trigger on its own.

## Worked examples

**"Add a modal to this page."**
1. Check `src/components/ui/` for a `dialog`; if missing, run `pnpm dlx shadcn@latest add dialog` (`references/components.md`).
2. Style with token utilities only: `bg-surface`, `rounded-lg`, `shadow-3`, `p-6`; never a raw hex or px value (`references/tailwind-config.md`).
3. Leave Radix's focus trap, `Escape`-to-close and `aria-modal` wiring alone.
4. Check the dialog in light and dark themes (`references/accessibility.md`).
5. Done when it's keyboard-navigable end to end, every value traces to a token, and both themes are checked.

**"Make the button blue."**
Don't inline `#0000ff` or Tailwind's `bg-blue-600`. Check whether an existing
role fits (usually `primary`) and use its utility. If no role fits, add a new
named role to `tokens.css` in the templates repo (light and dark values), map
it in `@theme`, and update projects with `copier update`.

## Anti-patterns

- Hand-rolling a component shadcn already provides.
- Hard-coding a hex or px value instead of a token.
- Overriding Radix's focus, keyboard or ARIA behavior.
- Shipping UI checked in only one theme.
- Inventing a color/spacing/type value outside the token set, or editing a project's vendored `tokens.css` instead of the templates repo's.
- Imposing this stack on an existing project with its own; flag the conflict instead.
- Reaching for `tailwind.config.js`: Tailwind v4 config lives in the CSS `@theme` block.
- Using MUI or another component library alongside shadcn.
- Patching a shadcn component via `node_modules`: it's copied into the repo; edit it in `src/components/ui/`.
- Defaulting to Next.js "just in case".
