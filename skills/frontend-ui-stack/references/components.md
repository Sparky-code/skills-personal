# Components: shadcn/ui on Base UI

New UI primitives (buttons, dialogs, inputs, cards, dropdowns, etc.) come from the **shadcn/ui CLI**, configured to generate on top of **Base UI** — the MUI team's headless primitives engine — instead of the CLI's Radix default.

## Why Base UI instead of the Radix default

- **Material-grade a11y/behavior rigor without MUI's visual opinions.** Base UI is built by the same team that ships MUI, so focus management, keyboard navigation, and ARIA roles get the same rigor MUI is known for — but Base UI ships no CSS, no visual styling, no theme. It's pure behavior.
- **Fully owned, not a runtime dependency.** shadcn's CLI copies component source directly into the repo (`src/components/ui/`) rather than installing a pre-built package. Base UI supplies the unstyled behavioral primitive; the copied component code is yours to read, edit, and restyle with tokens — there's no upstream package version to track for the visual layer.
- Combined with Tailwind + the token set, this gives Material-level interaction quality with a fully custom, minimalist visual identity — the goal of this whole stack.

## Setup (once per project)

```bash
npx shadcn@latest init
```

Configure it to target Base UI as the primitive registry rather than Radix when prompted (or via `components.json` if driving non-interactively). This writes `components.json`, wires up `cn()` in `src/lib/utils.ts`, and points the CLI at the project's Tailwind config and token CSS variables.

## Adding a primitive (per component)

```bash
npx shadcn@latest add button
npx shadcn@latest add input card dialog badge
```

Each `add` drops component source into `src/components/ui/<name>.tsx` (or similar) using the project's existing tokens and Tailwind classes. That file is now yours — edit it directly for any customization. **Never** patch a shadcn-added component by reaching into `node_modules`; there's nothing there to patch. If a component needs different behavior or styling, edit the copied source in `src/components/ui/` and commit the change like any other project file.

## Before reaching for a new primitive

Check `src/components/ui/` first — if an equivalent already exists in the project (or in the shared `templates/react-vite-material/` boilerplate), extend or compose it rather than adding a duplicate or hand-rolling a fresh one. The mandate is: never hand-roll a component shadcn already provides.

## If Base UI isn't actually available

Base UI is the newest, least-settled part of this stack's research (per the plan's own flag). If, at build time, `shadcn@latest init` doesn't actually offer Base UI as a real, current registry option — confirm this explicitly (check the CLI's registry choices or current docs) before assuming:

1. Fall back to the CLI's Radix default.
2. Note the deviation explicitly in the project's README or a comment in `components.json` — something like `# NOTE: using Radix, not Base UI — Base UI was not an available shadcn registry option as of <date>`.
3. Do not silently proceed as if Base UI was used; a future reader (human or agent) needs to know the actual primitive engine in play, since the accessibility guarantees in `accessibility.md` are written assuming Base UI's specific behavior.
