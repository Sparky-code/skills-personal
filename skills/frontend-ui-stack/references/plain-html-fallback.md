# Plain-HTML fallback

For a single-file prototype, demo or throwaway artifact where a Vite/React
scaffold is overkill: plain HTML, CSS and a little vanilla JS, using the same
`tokens.css` as every app so it looks like the same product.

Sketches live in the `sketches` repo, a folder each (`project-standards`:
`static-prototypes-homelab.md`), with a copy of `tokens.css` from the
templates repo (`shared/tokens.css`) next to the HTML file.

## The rule

A prototype never invents its own colors, spacing or type values. It links (or
inlines) the shared `tokens.css` and uses its variables.

## Minimal pattern

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Prototype</title>
  <link rel="stylesheet" href="./tokens.css" />
  <style>
    body {
      background: var(--background);
      color: var(--text);
      font-family: var(--font-sans);
      font-size: var(--type-body-large-size);
      line-height: var(--type-body-large-line);
      margin: 0;
      padding: var(--space-6);
    }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--rounded-lg);
      box-shadow: var(--elevation-2);
      padding: var(--space-5);
    }
    .btn-primary {
      background: var(--primary);
      color: var(--on-primary);
      border: none;
      border-radius: var(--rounded-md);
      padding: var(--space-2) var(--space-4);
      font: inherit;
      font-size: var(--type-label-large-size);
      font-weight: var(--type-label-large-weight);
      min-height: 24px;
      cursor: pointer;
      transition: background var(--duration-fast) var(--easing-standard);
    }
    .btn-primary:hover { background: var(--primary-hover); }
    .btn-primary:focus-visible { outline: 3px solid var(--primary); outline-offset: 2px; }
  </style>
</head>
<body>
  <div class="card">
    <button class="btn-primary" onclick="toggleTheme()">Toggle theme</button>
  </div>
  <script>
    // Same mechanism as the React template: data-theme on <html> overrides
    // the OS setting.
    function toggleTheme() {
      const root = document.documentElement;
      const dark = root.dataset.theme
        ? root.dataset.theme === "dark"
        : matchMedia("(prefers-color-scheme: dark)").matches;
      root.dataset.theme = dark ? "light" : "dark";
    }
  </script>
</body>
</html>
```

## What this buys you

- No build, no install: open the file in a browser.
- No token drift from the apps: the same file, not an approximation.
- A validated prototype ports straight into the React tier: swap the CSS for
  the mapped Tailwind utilities and the markup for shadcn components.

## What it doesn't replace

No component behavior (focus trapping, keyboard navigation, ARIA) comes for
free here. When a sketch needs a build, a second module of logic, or real
data, promote it to a proper project (React + shadcn, or plain TS for
map-first UIs) instead of growing hand-rolled interaction code.
