# Accessibility: WCAG 2.2 AA

Baseline is **WCAG 2.2 Level AA**, including the criteria newest to 2.2: Focus Not Obscured, Focus Appearance, and the 24×24px minimum target size. Radix (the primitives underneath every shadcn component in this stack) satisfies most of this for free. The skill's job is mostly *don't break what's already correct* — plus a short list of things Radix cannot verify for you.

## What Radix gives for free

- **Focus management** — focus moves into dialogs/menus/popovers on open and returns to the trigger on close; focus is trapped within modal surfaces while open.
- **Keyboard navigation** — arrow keys, Home/End, Escape, Tab/Shift+Tab all behave per the relevant ARIA authoring pattern (menu, listbox, dialog, tabs, etc.) without extra code.
- **Correct ARIA roles and states** — `role`, `aria-expanded`, `aria-selected`, `aria-controls`, `aria-modal`, and similar attributes are wired automatically and kept in sync with component state.
- **Focus Appearance / Focus Not Obscured (WCAG 2.2)** — floating and popover primitives position themselves so the focused element isn't hidden behind another surface. shadcn's components add a visible `focus-visible` ring (`ring-ring/50`, 3px); keep it, and check its contrast against the surface in both themes.

**Never remove the `outline` or `:focus-visible` ring.** A `outline: none` or a custom low-contrast focus ring is the single most common way this stack's accessibility baseline regresses. If a focus ring visually clashes with a design, adjust its color via a token (still visible, still meeting contrast) — never remove it.

## What you must still verify manually

- [ ] **Color contrast** — check every text/background and icon/background pairing from the token palette (`design-tokens.md`) against WCAG AA thresholds (4.5:1 normal text, 3:1 large text/UI components), for both light and dark theme. Token values are chosen to be reasonable, but a specific pairing (e.g. `text-muted` on `surface-variant`) can still fail depending on combination — verify the actual pairing you're using, don't assume all token combinations pass.
- [ ] **24×24px minimum target size** — any interactive element (icon button, close button, checkbox) needs at least a 24×24px hit area, even if the visible glyph is smaller; pad with token spacing (`space-*`) rather than a one-off pixel value.
- [ ] **Non-text content** — icons used as the sole indicator of meaning (status dots, icon-only buttons) need an accessible name (`aria-label` or visually-hidden text); Radix doesn't invent one for you.
- [ ] **Reduced motion** — respect `prefers-reduced-motion`; motion tokens (`duration-*`, `easing-*`) should be skipped or shortened when the user has that preference set, since animations don't disable themselves (Tailwind's `motion-reduce:` variant helps).
- [ ] **Content structure** — heading order, landmark regions, and page `lang` are page-level concerns the primitives can't see.

## Verification checklist per UI task

- [ ] Tab through the whole surface with keyboard only — every interactive element reachable, focus order matches visual order.
- [ ] Trigger the component in both light and dark theme — focus ring and text remain visible and high-contrast in both.
- [ ] Run a contrast check on any new color pairing introduced (don't assume; check).
- [ ] Confirm icon-only controls have an accessible name.
- [ ] Confirm hit targets meet 24×24px, especially on dense/compact layouts.
