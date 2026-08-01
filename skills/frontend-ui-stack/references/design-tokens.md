# Design Tokens

All visual constants — color, spacing, type, elevation, radius, motion — live in one DTCG-format (Design Tokens Community Group) JSON file. This is the single source of truth: nothing downstream (Tailwind theme, compiled CSS, plain-HTML fallback) defines its own values, it only consumes these.

**Canonical source**: `/Users/sparky/Code/templates/react-vite-material/tokens/design-tokens.json`. A sibling build task provisions this file and the Style Dictionary config that compiles it — if the path doesn't exist yet when you read this, treat the values below as the authoritative spec to implement, byte-for-byte, when that template is built.

Style Dictionary v4 compiles this JSON into two outputs consumed by both tiers of the stack:
1. **CSS custom properties** (`tokens.css`) — plain `--color-primary: oklch(...)` declarations, imported by the React app's `globals.css` and directly by the plain-HTML fallback.
2. **A Tailwind v4 `@theme` mapping** — so `bg-primary`, `text-on-primary`, `p-4`, `rounded-lg`, etc. resolve to these exact values instead of Tailwind's default palette. See `tailwind-config.md`.

Never hand-edit generated CSS — edit `design-tokens.json` and recompile.

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

`space-1` (4px) is the one half-step off the 8px grid, for tight cases (icon padding, borders). Everything else is a clean multiple of 8.

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

## `design-tokens.json` (DTCG format)

This is the **real, canonical file** — a live copy of `/Users/sparky/Code/templates/react-vite-material/tokens/design-tokens.json`, not a hypothetical example. If it ever looks out of date against that path, the template file wins; re-sync this doc, not the other way around.

```json
{
  "space": {
    "0": { "$value": "0px", "$type": "dimension" },
    "1": { "$value": "4px", "$type": "dimension" },
    "2": { "$value": "8px", "$type": "dimension" },
    "3": { "$value": "12px", "$type": "dimension" },
    "4": { "$value": "16px", "$type": "dimension" },
    "5": { "$value": "24px", "$type": "dimension" },
    "6": { "$value": "32px", "$type": "dimension" },
    "7": { "$value": "48px", "$type": "dimension" },
    "8": { "$value": "64px", "$type": "dimension" },
    "9": { "$value": "96px", "$type": "dimension" }
  },
  "type": {
    "display-large": {
      "size": { "$value": "57px", "$type": "dimension" },
      "line-height": { "$value": "64px", "$type": "dimension" },
      "weight": { "$value": 400, "$type": "number" }
    },
    "headline-large": {
      "size": { "$value": "32px", "$type": "dimension" },
      "line-height": { "$value": "40px", "$type": "dimension" },
      "weight": { "$value": 400, "$type": "number" }
    },
    "headline-medium": {
      "size": { "$value": "28px", "$type": "dimension" },
      "line-height": { "$value": "36px", "$type": "dimension" },
      "weight": { "$value": 400, "$type": "number" }
    },
    "title-large": {
      "size": { "$value": "22px", "$type": "dimension" },
      "line-height": { "$value": "28px", "$type": "dimension" },
      "weight": { "$value": 500, "$type": "number" }
    },
    "title-medium": {
      "size": { "$value": "16px", "$type": "dimension" },
      "line-height": { "$value": "24px", "$type": "dimension" },
      "weight": { "$value": 500, "$type": "number" }
    },
    "body-large": {
      "size": { "$value": "16px", "$type": "dimension" },
      "line-height": { "$value": "24px", "$type": "dimension" },
      "weight": { "$value": 400, "$type": "number" }
    },
    "body-medium": {
      "size": { "$value": "14px", "$type": "dimension" },
      "line-height": { "$value": "20px", "$type": "dimension" },
      "weight": { "$value": 400, "$type": "number" }
    },
    "label-large": {
      "size": { "$value": "14px", "$type": "dimension" },
      "line-height": { "$value": "20px", "$type": "dimension" },
      "weight": { "$value": 500, "$type": "number" }
    },
    "label-medium": {
      "size": { "$value": "12px", "$type": "dimension" },
      "line-height": { "$value": "16px", "$type": "dimension" },
      "weight": { "$value": 500, "$type": "number" }
    }
  },
  "color": {
    "$description": "Semantic color roles in OKLCH. Restrained/desaturated, minimalist — deliberately not literal Material blue/purple. Each role has a light and dark value; the Style Dictionary custom format compiles both into a single tokens.css with a [data-theme] split.",
    "light": {
      "background": { "$value": "oklch(0.98 0.003 90)", "$type": "color" },
      "surface": { "$value": "oklch(0.995 0.002 90)", "$type": "color" },
      "surface-variant": { "$value": "oklch(0.95 0.004 90)", "$type": "color" },
      "border": { "$value": "oklch(0.88 0.005 90)", "$type": "color" },
      "text": { "$value": "oklch(0.20 0.01 285)", "$type": "color" },
      "text-muted": { "$value": "oklch(0.50 0.01 285)", "$type": "color" },
      "primary": { "$value": "oklch(0.45 0.09 260)", "$type": "color" },
      "primary-hover": { "$value": "oklch(0.38 0.09 260)", "$type": "color" },
      "on-primary": { "$value": "oklch(0.98 0.005 260)", "$type": "color" },
      "success": { "$value": "oklch(0.55 0.10 145)", "$type": "color" },
      "warning": { "$value": "oklch(0.72 0.13 80)", "$type": "color" },
      "danger": { "$value": "oklch(0.55 0.18 25)", "$type": "color" }
    },
    "dark": {
      "background": { "$value": "oklch(0.16 0.004 285)", "$type": "color" },
      "surface": { "$value": "oklch(0.20 0.005 285)", "$type": "color" },
      "surface-variant": { "$value": "oklch(0.24 0.006 285)", "$type": "color" },
      "border": { "$value": "oklch(0.32 0.006 285)", "$type": "color" },
      "text": { "$value": "oklch(0.93 0.005 90)", "$type": "color" },
      "text-muted": { "$value": "oklch(0.68 0.01 285)", "$type": "color" },
      "primary": { "$value": "oklch(0.72 0.11 260)", "$type": "color" },
      "primary-hover": { "$value": "oklch(0.78 0.11 260)", "$type": "color" },
      "on-primary": { "$value": "oklch(0.14 0.01 260)", "$type": "color" },
      "success": { "$value": "oklch(0.75 0.12 145)", "$type": "color" },
      "warning": { "$value": "oklch(0.80 0.13 80)", "$type": "color" },
      "danger": { "$value": "oklch(0.72 0.16 25)", "$type": "color" }
    }
  },
  "elevation": {
    "$description": "Material-inspired but flatter/subtler box-shadow scale (minimalist, not skeuomorphic).",
    "0": { "$value": "none", "$type": "shadow" },
    "1": { "$value": "0 1px 2px 0 rgb(0 0 0 / 0.05)", "$type": "shadow" },
    "2": { "$value": "0 1px 3px 0 rgb(0 0 0 / 0.08), 0 1px 2px -1px rgb(0 0 0 / 0.06)", "$type": "shadow" },
    "3": { "$value": "0 2px 6px -1px rgb(0 0 0 / 0.10), 0 1px 3px -1px rgb(0 0 0 / 0.08)", "$type": "shadow" },
    "4": { "$value": "0 4px 10px -2px rgb(0 0 0 / 0.12), 0 2px 4px -2px rgb(0 0 0 / 0.08)", "$type": "shadow" },
    "5": { "$value": "0 8px 20px -4px rgb(0 0 0 / 0.14), 0 4px 8px -4px rgb(0 0 0 / 0.10)", "$type": "shadow" }
  },
  "radius": {
    "sm": { "$value": "6px", "$type": "dimension" },
    "md": { "$value": "10px", "$type": "dimension" },
    "lg": { "$value": "16px", "$type": "dimension" },
    "full": { "$value": "9999px", "$type": "dimension" }
  },
  "motion": {
    "duration": {
      "fast": { "$value": "150ms", "$type": "duration" },
      "normal": { "$value": "200ms", "$type": "duration" },
      "slow": { "$value": "300ms", "$type": "duration" }
    },
    "easing": {
      "standard": { "$value": "cubic-bezier(0.2, 0, 0, 1)", "$type": "cubicBezier" },
      "emphasized": { "$value": "cubic-bezier(0.3, 0, 0.8, 0.15)", "$type": "cubicBezier" }
    }
  }
}
```

Note the nesting doesn't literally spell out `space-4`/`elevation-1`/`duration-fast` as top-level keys — it's grouped (`space.4`, `elevation.1`, `motion.duration.fast`) and the Style Dictionary custom format in `style-dictionary.config.js` flattens each group into the `--space-4`, `--elevation-1`, `--duration-fast` custom-property names used throughout this skill and in Tailwind's `@theme` block. Read the JSON structure above for editing `design-tokens.json` itself; use the flat `--token-name` form everywhere else (CSS, Tailwind classes, this skill's other docs).
