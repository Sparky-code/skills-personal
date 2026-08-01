---
name: frontend-ui-stack
description: Use whenever starting a new frontend project, scaffolding a web app, adding or styling any UI component, choosing colors/spacing/fonts/type sizes, building a quick single-file HTML prototype or demo, or when the user says "our design system" or wants a "Material-style UI". Defines the one default frontend stack for /Users/sparky/Code.
---

# Frontend UI Stack

This is the default, non-negotiable stack for new UI work anywhere under `/Users/sparky/Code`, unless a project explicitly overrides it.

The stack: **Vite + React** by default (**Next.js** only when SSR/SEO is needed from day one), **Tailwind CSS v4**, **shadcn/ui** on **Base UI** headless primitives, **DTCG design tokens** compiled with **Style Dictionary**, and Material Design *principles* — grid, type scale, elevation, color roles — never the literal MUI component library.

Every new frontend project starts from the same tokens and the same primitives so that colors, spacing, type, and component behavior stay consistent across every project in this workspace instead of each one improvising its own. This isn't a stylistic preference — it's the fix for a real, already-observed failure mode: independent projects in this workspace have separately reinvented badge-color systems and "danger red" hex values that don't agree with each other. One token set, reused everywhere, is what prevents that drift from recurring, and it's why the checklist below treats a hardcoded value as a defect rather than a shortcut.

## Why each layer was picked

- **Vite** — fast dev server and build with no framework lock-in; the right default until SSR/SEO forces Next.js.
- **Tailwind CSS v4** — CSS-first `@theme` config maps directly onto compiled token variables, so utility classes and tokens are the same values, not two systems to keep in sync.
- **shadcn/ui on Base UI** — component code is copied into the repo (owned, editable, no runtime dependency to version-track) while Base UI supplies Material-grade accessibility behavior without MUI's visual opinions.
- **DTCG tokens + Style Dictionary** — one machine-readable source of truth compiles to both the React/Tailwind tier and the plain-HTML tier, so neither can silently drift from the other.
- **Material *principles*, not MUI** — the grid, type scale, elevation, and color-role vocabulary are borrowed because they're a proven, well-documented system; the literal component library and its visual identity are not.
- **WCAG 2.2 AA as the accessibility baseline** — including the newer Focus Not Obscured, Focus Appearance, and 24×24px target-size criteria, mostly satisfied for free by Base UI; see `references/accessibility.md` for what still needs manual verification.

## Canonical paths

- `/Users/sparky/Code/templates/react-vite-material/` — the boilerplate template to copy from.
- `/Users/sparky/Code/templates/react-vite-material/tokens/design-tokens.json` — the compiled source of truth for every token value.
- `/Users/sparky/Code/templates/plain-html-fallback/` — the reference fixture for the zero-build tier.

These are provisioned by a companion build task; if a path doesn't exist yet, treat the values documented in `references/design-tokens.md` as the spec to implement against, not as an optional detail to improvise.

## Defaults beyond the core stack

- **Typography**: Inter (or Geist) as the default UI sans font, loaded as a variable font (`@fontsource-variable/inter`). Don't introduce a second UI typeface without a stated reason.
- **Icons**: Lucide — shadcn/ui's built-in icon set. Use it before reaching for a second icon library; mixing icon sets is a visible inconsistency the same way mixing token systems is an invisible one.

## Decision tree

- **New project, no stated SSR/SEO need** → React + Vite.
  This is the default; pick it unless one of the branches below clearly applies.
  Triggers: "start a new frontend project", "scaffold a web app", "set up a React project", "build a dashboard/tool/internal app" with no mention of SEO or an existing stack.

- **SSR/SEO explicitly required from day one** → Next.js.
  The one exception, and it's a fork made at project start, not a cheap upgrade later — switching after the fact means rewriting routing (React Router → Next's file-based router), data-fetching (TanStack Query → loaders/Server Components), and discarding the Vite build config outright. Decide this up front; don't default into Next "just in case" a project might someday need SEO.
  Triggers: "needs to be crawlable/indexed by Google", "server-side rendering", "public marketing site", "needs per-page meta tags for social sharing".

- **Single-file prototype, demo, or throwaway artifact** → plain-HTML fallback.
  No framework, no build step — but it still shares the compiled token file, so it never looks or feels like a different product from the real app.
  Triggers: "quick prototype", "single-file demo", "just show me a login form", "HTML artifact I can open in a browser".

- **Adding to an existing project that already has its own established frontend stack** → do not impose this skill.
  Flag the conflict to the user and ask how to proceed instead of silently introducing a second, competing stack into a codebase that already picked one.
  Triggers: the project already has its own component library, CSS approach, or token file, or the user references an existing design system by a different name.

Full trigger phrases and rationale per branch: `references/decision-tree.md`.

## Mandatory checklist for every UI task

- [ ] Never hardcode a color, spacing, radius, shadow, or font-size value — always reference a token.
  A hardcoded value is exactly how the badge-color and "danger red" drift happened elsewhere in this workspace; a token is the only thing that keeps every project's palette provably identical.
  One exemption: the literal sizing values shadcn's CLI ships inside vendored `src/components/ui/*.tsx` (`ring-[3px]`, `h-6`, `text-[0.8rem]`) stay as-is — they're upstream defaults, not authored choices, and normalizing them forks the components away from what `npx shadcn add` produces. Everything you write is still held to the rule. See "About the vendored shadcn components" in the template README.

- [ ] New primitives come from the shadcn CLI (`npx shadcn@latest add <name>`) — never hand-roll a component shadcn already provides.
  Hand-rolling throws away Base UI's tested focus/keyboard/ARIA behavior in exchange for a bespoke reimplementation of the same problem, usually a worse one.

- [ ] Never override Base UI's focus, keyboard, or ARIA behavior.
  It's already WCAG-2.2-grade out of the box; overriding it (e.g. `outline: none`, a custom low-contrast focus ring) is how accessibility regresses, not how it improves.

- [ ] Verify both dark AND light themes before calling any UI work done.
  A component checked in only one theme is unverified in the other, not merely "probably fine" — token values that pair well in one theme can fail contrast in the other.

- [ ] Plain-HTML work still imports the shared compiled `tokens.css` — never invents its own colors or spacing.
  This is what keeps a five-minute mockup and the production app pixel-consistent; skipping it defeats the entire point of having a fallback tier at all.

## Scaffolding

Provisioning a fresh project (or copying the boilerplate template) is a fixed set of commands — see `references/project-scaffold.md` rather than reconstructing it from memory or guessing package names.

Preferred: copy `/Users/sparky/Code/templates/react-vite-material/` directly, since it ships with tokens, Tailwind wiring, and shadcn/Base UI already configured and verified. Only scaffold fresh with `npm create vite@latest` when the template isn't available or doesn't fit. Either path, don't skip wiring the design tokens before writing any component — everything downstream depends on them existing first.

## Reference index

- `references/design-tokens.md` — the full DTCG token set (color roles, spacing, type scale, elevation, radius, motion) and how Style Dictionary compiles it. Open before picking any color, spacing, or font-size value.
  Contains the exact, canonical values — copy them rather than approximating.
- `references/components.md` — shadcn/ui CLI usage on Base UI primitives; how to add a new component. Open before adding or modifying any UI component.
  Also covers the Radix fallback path if Base UI isn't a real CLI option at build time.
- `references/tailwind-config.md` — Tailwind v4's CSS-first `@theme` wiring to the compiled tokens; light/dark strategy. Open when touching Tailwind config or writing utility classes.
  Includes the common utility-to-token mapping table (what to use instead of an arbitrary-value bracket).
- `references/plain-html-fallback.md` — the zero-build single-file HTML pattern. Open for quick prototypes, demos, or artifacts.
  Includes a minimal working example wired entirely to token custom properties.
- `references/accessibility.md` — WCAG 2.2 AA checklist: what Base UI gives for free vs. what to verify manually. Open before calling any UI accessible.
  Covers the newer 2.2 criteria specifically: Focus Not Obscured, Focus Appearance, 24×24px target size.
- `references/project-scaffold.md` — exact commands to provision a new project or copy the template. Open at project start.
  Also covers when to add routing and when TanStack Query is warranted.
- `references/decision-tree.md` — expanded decision tree with concrete trigger phrases per branch. Open when it's unclear which branch applies.

## Scope

This skill governs new UI work under `/Users/sparky/Code` only. It does not retroactively apply to existing projects that already picked a different stack before this skill existed — those stay as they are unless someone deliberately decides to migrate them, which is a separate, larger decision than anything this skill should trigger on its own. Within scope, treat this file as the index: it holds only what every branch needs (the decision tree, the checklist, the anti-patterns); anything deeper lives in `references/` and is loaded only when the task actually reaches that branch.

## Worked examples

**"Add a modal to this page."**
1. Check `src/components/ui/` for an existing `dialog`; if it's not there yet, run `npx shadcn@latest add dialog` (`references/components.md`) instead of writing a custom overlay.
2. Style the modal surface with token utilities only — `bg-surface`, `rounded-lg`, `shadow-3`, `p-6` — never a raw hex or px value (`references/tailwind-config.md`).
3. Leave Base UI's focus trap, `Escape`-to-close, and `aria-modal` wiring untouched; that behavior is the entire reason to use the primitive instead of a hand-rolled `<div>` overlay.
4. Open the page in both light and dark theme and confirm the surface, border, and focus ring are all visible and correctly contrasted in both (`references/accessibility.md`).
5. Done when: the dialog is keyboard-navigable end to end, every value traces back to a token, and both themes have been visually checked — not before.

**"Make the button blue."**
The checklist stops a hardcoded hex here: open `references/design-tokens.md`, check whether an existing role fits (usually `primary`), and use that role's utility class. If no existing role genuinely fits, extend the token set with a new named role and recompile — don't inline `#0000ff` or reach for Tailwind's default `bg-blue-600` directly in the component.

## Anti-patterns

- Don't hand-roll a component shadcn already provides.
- Don't hardcode a hex or px value — use a token.
- Don't override Base UI's focus, keyboard, or ARIA behavior.
- Don't ship UI checked in only one theme — dark and light both, every time.
- Don't invent a new color/spacing/type value outside the token set — extend the token set instead.
- Don't impose this stack on an existing project that already has its own frontend stack — flag the conflict instead.
- Don't reach for `tailwind.config.js` — Tailwind v4 config lives in the CSS `@theme` block.
- Don't let a plain-HTML prototype drift from the compiled `tokens.css`.
- Don't patch a shadcn component via `node_modules` — it's copied into the repo; edit it directly in `src/components/ui/`.
- Don't default to Next.js "just in case" — it's the documented exception, not the baseline.
