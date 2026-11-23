# Components: shadcn/ui on Radix

UI primitives (buttons, dialogs, inputs, cards, menus) come from the
**shadcn/ui CLI** on **Radix** primitives, shadcn's default.

## Why shadcn on Radix

- **Owned code.** The CLI copies component source into `src/components/ui/`;
  it's yours to read and edit, with no upstream package to track for the
  visual layer.
- **Proven behavior.** Radix supplies focus management, keyboard navigation
  and ARIA for each pattern, and it's the most-used, best-documented shadcn path.
- **Token-styled.** Components use role classes (`bg-primary`,
  `text-muted-foreground`, `border-input`, `ring-ring`) that the `@theme`
  mapping points at the tokens (`tailwind-config.md`), so they follow the
  design system and both themes without edits.

## Setup

Already done in the react-web template (`components.json`: style `new-york`,
`cssVariables: true`, aliases `@/components`, `@/lib/utils`). For a project
without the template:

```bash
pnpm dlx shadcn@latest init
```

## Adding a component

```bash
pnpm dlx shadcn@latest add dialog
pnpm dlx shadcn@latest add input card dropdown-menu badge
```

Each lands in `src/components/ui/<name>.tsx` and is now project code: edit it
there for any change, and commit it. Never patch anything in `node_modules`.
Biome skips `src/components/ui/` so shadcn's upstream formatting and literal
sizes stay as generated.

## Before adding one

Check `src/components/ui/` first and extend or compose what's there. Never
hand-roll a component shadcn provides.

## Icons

Lucide (`lucide-react`), which shadcn components already use.
