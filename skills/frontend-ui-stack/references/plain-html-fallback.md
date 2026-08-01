# Plain-HTML Fallback

For a quick single-file prototype, demo, or throwaway artifact where a full Vite/React scaffold is overkill, use plain HTML/CSS/vanilla JS — but it still shares the exact same visual language as every React project, because it imports the same compiled `tokens.css`.

**Reference fixture**: `/Users/sparky/Code/templates/plain-html-fallback/` (a sibling build task provisions this — if the path doesn't exist yet, treat the pattern below as the spec).

```
templates/plain-html-fallback/
├── index.html      # single file, links the same compiled tokens.css
├── tokens.css      # copy of the generated file — same source of truth
└── README.md
```

## The rule

A plain-HTML prototype must **never invent its own colors, spacing, or type values.** It links (or inlines) the identical `tokens.css` that Style Dictionary compiled for the React tier. This is the entire point of the fallback: a five-minute mockup and the production app render pixel-identical spacing, color, and type, because both read from one file.

## Minimal pattern

```html
<!doctype html>
<html data-theme="light">
<head>
  <meta charset="utf-8" />
  <title>Prototype</title>
  <link rel="stylesheet" href="./tokens.css" />
  <style>
    body {
      background: var(--color-background);
      color: var(--color-text);
      font-family: "Inter", system-ui, sans-serif;
      margin: 0;
      padding: var(--space-6);
    }
    .card {
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      box-shadow: var(--elevation-2);
      padding: var(--space-5);
    }
    .btn-primary {
      background: var(--color-primary);
      color: var(--color-on-primary);
      border: none;
      border-radius: var(--radius-md);
      padding: var(--space-2) var(--space-4);
      font-size: 14px; /* body-medium / label-large scale */
      cursor: pointer;
      transition: background var(--duration-fast) var(--easing-standard);
    }
    .btn-primary:hover {
      background: var(--color-primary-hover);
    }
  </style>
</head>
<body>
  <div class="card">
    <button class="btn-primary">Continue</button>
  </div>
  <script>
    // Theme toggle: flips the data-theme attribute the same way
    // the React template's use-theme hook does, so both tiers
    // stay behaviorally consistent, not just visually consistent.
    function toggleTheme() {
      const root = document.documentElement;
      root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
    }
  </script>
</body>
</html>
```

## What this buys you

- No build step, no `npm install` — open the file directly in a browser.
- Still zero token drift from the React app, because both consume the exact same generated CSS file, not a hand-copied approximation.
- A prototype validated here (colors, spacing, contrast) ports directly into the React tier later — swap raw CSS classes for Tailwind utilities that map to the same underlying variables, and swap hand-written markup for shadcn components; no visual rework needed.

## What this does not replace

This fallback is for prototypes and demos, not for a real application: no component behavior (focus trapping, keyboard nav, ARIA) is provided for free the way Base UI provides it in the React tier. If the "quick demo" grows into a real feature, migrate it into the Vite/React scaffold (`project-scaffold.md`) rather than continuing to hand-roll interaction logic in vanilla JS.
