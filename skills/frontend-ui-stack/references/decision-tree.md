# Decision Tree (expanded)

Five branches. Pick the first one that matches; don't skip straight to a default without checking whether an SSR/SEO need or an existing-stack conflict applies.

## 1. React + Vite (the default)

**Trigger phrases**: "start a new frontend project", "scaffold a web app", "build a new app/tool/dashboard", "set up a React project", any new-project request with no mention of SEO, server rendering, or an existing stack.

Choose this unless branch 2, 3, 4 or 5 clearly applies. Scaffold with the templates repo's `react-web` shape (`project-scaffold.md`).

## 2. Next.js (the SSR/SEO exception)

**Trigger phrases**: "needs to be crawlable/indexed by Google", "server-side rendering", "SSR", "SEO from day one", "public marketing site", "needs meta tags per page for social sharing", "static site generation" for content that must be pre-rendered.

This is a fork made **at project start**, not a cheap upgrade path added later. If SSR/SEO isn't explicitly stated as a day-one requirement, default to React + Vite instead — don't pre-emptively choose Next "in case it's needed later." Switching after the fact means:
- Routing: React Router → Next's file-based/App Router.
- Data-fetching: TanStack Query typically gives way to (or is supplemented by) loaders/Server Components.
- Any browser-only code needs SSR-safe guards it didn't need before.
- The Vite build config is discarded outright.

What *does* port cleanly regardless of when the decision is made: the design tokens, the Tailwind theme, and the shadcn components — all framework-agnostic.

## 3. Plain TypeScript + CSS (map-first or single-tool UI)

**Trigger phrases**: "map app", "map with a side panel", "show these places on a map", "single-screen tool", "canvas/visualisation tool".

When a map library (MapLibre GL) or a canvas draws most of the screen, React adds weight for little gain. Use Vite with plain TypeScript and CSS, still importing the shared `tokens.css` and using token variables for every value. Keep custom interactive widgets (dialogs, menus, comboboxes) few: their focus, keyboard and ARIA behavior is now yours to get right (`accessibility.md`). If the UI grows real forms, settings screens or many dialogs, move to React + shadcn.

Maps: MapLibre GL by default (vector tiles, PMTiles, self-hosted tiles, styling); Leaflet only for a simple raster overlay.

## 4. Plain-HTML fallback

**Trigger phrases**: "quick prototype", "single-file demo", "throwaway mockup", "just show me a login form", "HTML artifact", "no build step", "static demo I can open in a browser", "quick visualization/dashboard I can share as one file".

No framework, no build step — but still imports the shared `tokens.css` so it's visually consistent with every React project. See `plain-html-fallback.md`. If a "quick demo" is later going to become a real, maintained feature, migrate it into the React scaffold rather than continuing to grow it as hand-rolled HTML/JS.

## 5. Existing-project conflict — do not impose this skill

**Trigger phrases/context clues**: the project already has its own component library, its own token file, its own CSS approach (SCSS Modules, styled-components, plain CSS, a different Tailwind version or config style), or the user references an existing design system by name that isn't this one.

Do not silently introduce Tailwind v4 / shadcn / this token set into a project that has already committed to a different stack — that creates exactly the kind of drift this skill exists to prevent (independent badge-color systems, unreconciled "danger red" values). Instead:
1. Say explicitly that the project has an established stack that differs from the default.
2. Ask whether to follow the existing stack's conventions for this task, or whether the user actually wants to migrate the project onto this stack (a bigger, separate decision they should make deliberately, not one this skill should trigger unprompted).
