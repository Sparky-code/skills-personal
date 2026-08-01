# Tailwind CSS v4 Configuration

Tailwind v4 uses **CSS-first configuration** — no `tailwind.config.js`. Theme values live in an `@theme` block inside a CSS file, and that block is where the compiled design tokens get wired in.

## How it fits together

1. Style Dictionary compiles `design-tokens.json` into `src/styles/tokens.css` — plain CSS custom properties like `--color-primary`, `--space-4`, `--radius-lg`. This file is generated; never hand-edit it (see `design-tokens.md`).
2. `src/styles/globals.css` imports Tailwind and the compiled tokens, then maps them into Tailwind's namespace via `@theme`:

```css
@import "tailwindcss";
@import "./tokens.css";

@theme {
  --color-background: var(--color-background);
  --color-surface: var(--color-surface);
  --color-primary: var(--color-primary);
  --color-on-primary: var(--color-on-primary);
  --color-danger: var(--color-danger);

  --spacing-1: var(--space-1);
  --spacing-4: var(--space-4);
  --spacing-6: var(--space-6);

  --radius-sm: var(--radius-sm);
  --radius-lg: var(--radius-lg);

  --shadow-1: var(--elevation-1);
  --shadow-3: var(--elevation-3);
}
```

3. Once mapped, ordinary Tailwind utilities resolve to token values automatically: `bg-primary`, `text-on-primary`, `border-border`, `p-4`, `rounded-lg`, `shadow-3`. No utility ever needs an arbitrary-value bracket (`bg-[#3355ff]`) because every value that matters already has a token and therefore a utility class.

## Light / dark mode strategy

Tokens are compiled with light and dark variants (see `design-tokens.md`). The compiled `tokens.css` defines both sets scoped under a `[data-theme="light"]` / `[data-theme="dark"]` attribute (or `:root` + `.dark` class — whichever the template's `use-theme` hook toggles). Tailwind's `dark:` variant is not the mechanism here — the CSS custom properties themselves swap value depending on the active theme attribute, so a single `bg-background` class automatically repaints for both themes without a `dark:bg-*` utility pair. This keeps components theme-agnostic: they reference roles (`background`, `surface`, `primary`), never light/dark-specific values directly.

## The rule

**Never define a raw hex or px value inline in a class or style.** Every color, spacing, radius, shadow, or font-size in JSX/CSS must resolve through a `--color-*`, `--spacing-*`, `--radius-*`, `--shadow-*`, or type-scale token — either via a mapped Tailwind utility or, in the rare case no utility fits, `var(--token-name)` directly in a style attribute. If a value you need doesn't exist as a token yet, add it to `design-tokens.json` and recompile — don't work around it with a one-off literal.

## Common utility → token mapping

| Need | Use | Never |
|---|---|---|
| Background color | `bg-background` / `bg-surface` | `bg-white`, `bg-[#fff]` |
| Brand color | `bg-primary`, `text-primary` | `bg-blue-600` |
| Spacing | `p-4`, `gap-2`, `m-6` (mapped to `space-*`) | `p-[17px]` |
| Corner radius | `rounded-md`, `rounded-lg` | `rounded-[10px]` |
| Shadow | `shadow-1`...`shadow-5` (mapped to `elevation-*`) | a raw `box-shadow` value |
| Font size | Typography utility classes mapped from the type scale | `text-[15px]` |
