# Web apps

Web frameworks are the layer where a mandated stack helps least: the right
choice depends on the app. So this is a **decision guide plus firm rules**.
Whatever you pick, stay close to standard, well-known packages, and write the
choice and reason in `CLAUDE.md` under "Stack choice".

## Decision guide

| Need | Choose | Template |
|---|---|---|
| Client-only app (all logic in the browser) | Vite + React | `react-web --data with_api=false` |
| App with a small API, no SEO need | Vite + React + Hono API in the same repo | `react-web` |
| Pages must be crawlable or server-rendered from day one | Next.js (App Router) | `create-next-app` + baseline |
| UI is mostly a map or a single tool view | Plain TypeScript + CSS on Vite (still on the tokens) | `react-web`, then drop React, or Vite vanilla-ts + baseline |

Notes on the options:

- **Vite + React + Hono**: the fewest moving parts, each standard. Hono runs on
  standard Request/Response, so the same server code runs on Node, Vercel,
  Cloudflare or in Docker. In development `@hono/vite-dev-server` serves
  `/api/*` inside Vite; in production `src/server/index.ts` serves the API and
  the built client. The typed client (`hono/client`) gives the front end the
  API's types without tRPC. Costs: no SSR; you own the dev/prod wiring (the
  template does it).
- **Next.js**: the most standard full-stack React option and well supported
  on Vercel, but heavy and fast-moving (routing, caching and rendering models
  keep shifting), and harder to host elsewhere. Choose it for SSR/SEO, not "in
  case".
- Considered, not defaults: React Router v7 framework mode (formerly Remix),
  and TanStack Start (promising, younger).

## Firm rules

- **zod at every boundary**: validate API inputs (`@hono/zod-validator`),
  environment variables at startup, and external data. Put schemas in
  `src/shared/` so the client uses the same ones for types and forms.
- **Auth through a maintained library; never hand-rolled session code.**
  Better Auth is the suggested default (framework-agnostic; OAuth providers
  including generic OAuth2, magic links, sessions; Prisma/Drizzle adapters).
  Small OAuth helpers such as arctic are fine inside a library-backed setup,
  not as a home-made session system.
- **Email through Resend** (transactional and magic links).
- **One package until there is a second app**, then a pnpm workspace:
  `apps/web`, `apps/mobile`, `packages/core` (shared pure-TS logic: types,
  calculations, validation).
- **Hosting is recorded, not mandated**: Vercel suits public apps; Docker
  Compose suits self-hosted ones. Write the target and any constraint in
  `CLAUDE.md` (for example "OCR uses macOS Vision, so it can't run on Vercel").

## UI

All UI work follows `frontend-ui-stack`: shared design tokens, Tailwind v4 +
shadcn/ui on Radix for React apps, MapLibre for maps, dark and light themes
checked.

## Client data and state (guidance)

- Server data: TanStack Query.
- Routing in a single-page app: React Router.
- Shared client state: Zustand, only when component state and Query aren't enough.
- `fetch`, not axios.
