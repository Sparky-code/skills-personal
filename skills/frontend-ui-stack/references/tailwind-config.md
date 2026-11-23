# Tailwind CSS v4 configuration

Tailwind v4 is configured in CSS: no `tailwind.config.js`. The tokens are
mapped into Tailwind's theme with an `@theme inline` block in
`src/styles/globals.css` (already present in the react-web template).

## How it fits together

1. `src/styles/tokens.css` (vendored) defines the variables: `--primary`,
   `--space-4`, `--rounded-lg`, `--elevation-3`, …
2. `globals.css` imports Tailwind, Inter and the tokens, then maps them onto
   Tailwind theme variables and the role names shadcn/ui components expect:

```css
@import "tailwindcss";
@import "@fontsource-variable/inter";
@import "./tokens.css";

@theme inline {
  --font-sans: var(--font-sans);

  --color-background: var(--background);
  --color-foreground: var(--text);
  --color-card: var(--surface);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--on-primary);
  --color-muted: var(--surface-variant);
  --color-muted-foreground: var(--text-muted);
  --color-destructive: var(--danger);
  --color-border: var(--border);
  --color-input: var(--border);
  --color-ring: var(--primary);
  /* …surface, popover, secondary, accent, success, warning (see the template) */

  --spacing-4: var(--space-4);   /* one line per step, 0–9 */
  --radius-lg: var(--rounded-lg); /* sm, md, lg, full */
  --shadow-3: var(--elevation-3); /* 1–5 */
  --text-body: var(--type-body-large-size);
  --text-body--line-height: var(--type-body-large-line);
  --ease-standard: var(--easing-standard);
}
```

3. Utilities then resolve to token values: `bg-background`, `bg-surface`,
   `text-muted-foreground`, `bg-primary text-primary-foreground`,
   `border-border`, `p-4`, `gap-2`, `rounded-lg`, `shadow-3`, `text-body`.

`inline` makes utilities reference the token variables directly, so the
values follow the active theme.

## Light / dark

The color roles in `tokens.css` switch by themselves: dark follows the OS
setting, and `<html data-theme="light|dark">` forces either. Components use
roles (`bg-background`, `text-foreground`), never `dark:` utility pairs, so
one class repaints in both themes. A theme toggle only sets
`document.documentElement.dataset.theme`.

## The rule

Never write a raw hex or px value in a class or style. Every color, spacing,
radius, shadow or font size resolves through a mapped utility or, when no
utility fits, `var(--token)` in a style. If a value you need doesn't exist,
add a token (`design-tokens.md`) rather than a one-off literal.

## Utility → token mapping

| Need | Use | Never |
|---|---|---|
| Page / panel background | `bg-background`, `bg-surface`, `bg-muted` | `bg-white`, `bg-[#fff]` |
| Text | `text-foreground`, `text-muted-foreground` | `text-gray-500` |
| Brand color | `bg-primary`, `text-primary`, `text-primary-foreground` | `bg-blue-600` |
| Status | `text-destructive`, `bg-success`, `bg-warning` | `text-red-600` |
| Spacing | `p-4`, `gap-2`, `m-6` (mapped to `--space-*`) | `p-[17px]` |
| Corner radius | `rounded-md`, `rounded-lg` | `rounded-[10px]` |
| Shadow | `shadow-1` … `shadow-5` | a raw `box-shadow` |
| Font size | `text-display`, `text-headline`, `text-title`, `text-body`, `text-label` | `text-[15px]` |

## Biome

Enable Tailwind syntax in Biome's CSS parser (the template does):
`"css": { "parser": { "tailwindDirectives": true } }`.
