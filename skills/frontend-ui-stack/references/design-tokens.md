# Design Tokens

All visual constants (color, spacing, type, elevation, radius, motion) live in
one hand-written CSS file, `tokens.css`, as custom properties. It's the single
source of truth: the Tailwind theme, plain-HTML prototypes, plain-TS apps and
the React Native mirror all consume it; none defines its own values.

**Canonical source**: `shared/tokens.css` in the templates repo
(`gh:Sparky-code/templates`). Projects get a vendored copy (`src/styles/tokens.css`
in React apps, `design/tokens.css` elsewhere) and update it with
`copier update`. Never edit a project's copy: change the templates repo,
release, update.

How it's organised:

- `:root` holds every token and the light color roles.
- `@media (prefers-color-scheme: dark)` swaps the color roles for dark mode,
  unless `<html data-theme="light">` forces light.
- `:root[data-theme="dark"]` forces dark.
- React Native can't read CSS variables or `oklch()`, so Expo apps get
  `design/tokens.ts` (the same values, colors as sRGB hex) and
  `design/check-tokens.ts`, which fails if the two drift.

Variable names (the flat names used everywhere: CSS, Tailwind mapping, docs):

| Group | Variables |
|---|---|
| Spacing | `--space-0` … `--space-9` |
| Type | `--type-<step>-size`, `--type-<step>-line`, `--type-<step>-weight`; `--font-sans` |
| Radius | `--rounded-sm`, `--rounded-md`, `--rounded-lg`, `--rounded-full` |
| Elevation | `--elevation-0` … `--elevation-5` |
| Motion | `--duration-fast/normal/slow`, `--easing-standard`, `--easing-emphasized` |
| Color roles | `--background`, `--surface`, `--surface-variant`, `--border`, `--text`, `--text-muted`, `--primary`, `--primary-hover`, `--on-primary`, `--success`, `--warning`, `--danger` |

Radius uses `--rounded-*` and colors use bare role names so they don't collide
with Tailwind's own `--radius-*` and `--color-*` theme variables;
`tailwind-config.md` maps one onto the other.

## Spacing scale (8px grid, with a half-step)

| Token | Value |
|---|---|
| `space-0` | 0px |
| `space-1` | 4px |
| `space-2` | 8px |
| `space-3` | 12px |
| `space-4` | 16px |
| `space-5` | 24px |
| `space-6` | 32px |
| `space-7` | 48px |
| `space-8` | 64px |
| `space-9` | 96px |

`--space-1` (4px) is the one half-step off the 8px grid, for tight cases (icon padding, borders). Everything else is a clean multiple of 8.

## Type scale (Material-3-inspired, minimalist subset)

| Token | Size / line-height | Weight |
|---|---|---|
| `display-large` | 57px / 64px | 400 |
| `headline-large` | 32px / 40px | 400 |
| `headline-medium` | 28px / 36px | 400 |
| `title-large` | 22px / 28px | 500 |
| `title-medium` | 16px / 24px | 500 |
| `body-large` | 16px / 24px | 400 |
| `body-medium` | 14px / 20px | 400 |
| `label-large` | 14px / 20px | 500 |
| `label-medium` | 12px / 16px | 500 |

This is a deliberately trimmed subset of Material 3's full type scale (no `display-medium/small`, no `headline-small`, no `title-small`, no `body-small`, no `label-small`) — enough range for real UI without a 15-step ladder nobody uses consistently. Extend it only if a project genuinely needs a step in between; don't invent a one-off size outside the scale.

## Color roles (semantic, OKLCH, light + dark)

These are the **canonical values** — reuse them exactly; don't reinvent a palette per project. OKLCH was chosen (over hex/HSL) because it's perceptually uniform, so lightness steps between light/dark variants stay visually consistent, and because Tailwind v4 uses OKLCH natively. Values are restrained and desaturated on purpose — this is a minimalist professional palette, not literal Google Material blue/purple.

**Light theme:**

| Role | Value |
|---|---|
| `background` | `oklch(0.98 0.003 90)` |
| `surface` | `oklch(0.995 0.002 90)` |
| `surface-variant` | `oklch(0.95 0.004 90)` |
| `border` | `oklch(0.88 0.005 90)` |
| `text` | `oklch(0.20 0.01 285)` |
| `text-muted` | `oklch(0.50 0.01 285)` |
| `primary` | `oklch(0.45 0.09 260)` |
| `primary-hover` | `oklch(0.38 0.09 260)` |
| `on-primary` | `oklch(0.98 0.005 260)` |
| `success` | `oklch(0.55 0.10 145)` |
| `warning` | `oklch(0.72 0.13 80)` |
| `danger` | `oklch(0.55 0.18 25)` |

**Dark theme:**

| Role | Value |
|---|---|
| `background` | `oklch(0.16 0.004 285)` |
| `surface` | `oklch(0.20 0.005 285)` |
| `surface-variant` | `oklch(0.24 0.006 285)` |
| `border` | `oklch(0.32 0.006 285)` |
| `text` | `oklch(0.93 0.005 90)` |
| `text-muted` | `oklch(0.68 0.01 285)` |
| `primary` | `oklch(0.72 0.11 260)` |
| `primary-hover` | `oklch(0.78 0.11 260)` |
| `on-primary` | `oklch(0.14 0.01 260)` |
| `success` | `oklch(0.75 0.12 145)` |
| `warning` | `oklch(0.80 0.13 80)` |
| `danger` | `oklch(0.72 0.16 25)` |

Note the dark theme doesn't just invert lightness on a fixed hue/chroma — `primary`, `success`, `warning`, and `danger` get *lighter* (higher L) against the dark background to hold contrast, and `on-primary` flips from near-white to near-black because `primary` itself flipped from mid-dark to mid-light. Verify contrast against the actual background/surface pairing when extending this set (see `accessibility.md`), don't just mirror the light-theme lightness value.

## Elevation / shadow scale

Material-inspired but flatter and subtler — minimalist, not skeuomorphic. No colored shadows.

| Token | Value |
|---|---|
| `elevation-0` | `none` |
| `elevation-1` | `0 1px 2px 0 rgb(0 0 0 / 0.05)` |
| `elevation-2` | `0 1px 3px 0 rgb(0 0 0 / 0.08), 0 1px 2px -1px rgb(0 0 0 / 0.06)` |
| `elevation-3` | `0 2px 6px -1px rgb(0 0 0 / 0.10), 0 1px 3px -1px rgb(0 0 0 / 0.08)` |
| `elevation-4` | `0 4px 10px -2px rgb(0 0 0 / 0.12), 0 2px 4px -2px rgb(0 0 0 / 0.08)` |
| `elevation-5` | `0 8px 20px -4px rgb(0 0 0 / 0.14), 0 4px 8px -4px rgb(0 0 0 / 0.10)` |

## Radius scale

| Token | Value |
|---|---|
| `radius-sm` | 6px |
| `radius-md` | 10px |
| `radius-lg` | 16px |
| `radius-full` | 9999px |

## Motion tokens

| Token | Value |
|---|---|
| `duration-fast` | 150ms |
| `duration-normal` | 200ms |
| `duration-slow` | 300ms |
| `easing-standard` | `cubic-bezier(0.2, 0, 0, 1)` |
| `easing-emphasized` | `cubic-bezier(0.3, 0, 0.8, 0.15)` |

`easing-standard` for ordinary transitions (hover, toggle). `easing-emphasized` for anything drawing attention (a dialog entering, a toast). `duration-fast` for micro-interactions (button press), `duration-normal` for most transitions, `duration-slow` reserved for larger surface changes (a panel sliding in).

## Adding or changing a token

1. Edit `shared/tokens.css` in the templates repo: both light and dark values for a color role.
2. If it is a color, spacing, radius or type value that React Native uses, update `shared/tokens.ts` too; the drift check enforces this.
3. Map it in the Tailwind `@theme` block (react-web template `src/styles/globals.css`) if utilities should use it.
4. Check contrast in both themes (`accessibility.md`), release the templates, and run `copier update` in projects.
