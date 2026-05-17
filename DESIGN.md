# Design Style Guide

## Colour Palette

CSS custom properties defined in `:root`:

| Variable | Hex | Usage |
|---|---|---|
| `--cream` | `#f5f6ff` | Page background |
| `--cream-dark` | `#eaecfa` | Progress track, optional badge background, cancel button |
| `--sidebar-bg` | `#eef0fb` | Sidebar background |
| `--card` | `#ffffff` | Task cards, analytics card, calendar popup, inputs |
| `--border` | `#d8dcf0` | All borders (topbar, sidebar, cards, inputs) |
| `--text` | `#1a1a2e` | Primary text — titles, body |
| `--text-2` | `#5a5a7a` | Secondary text — descriptions, cancel button text |
| `--text-3` | `#9898b8` | Muted text — placeholders, due dates, labels |
| `--accent` | `#4a6fd4` | Primary accent — buttons, checkboxes, donut, active stat, links |
| `--accent-h` | `#3a5dc0` | Hover state for accent buttons |
| `--accent-s` | `#eef1fc` | Accent surface — calendar day hover, drag-over background |
| `--pink` | `#c94fb5` | Secondary accent — done stat value, calendar link, confetti |

**Gradient:** Title and progress bar use `linear-gradient(90deg, #4a6fd4, #c94fb5)` — blue to pink, inspired by the app's colour identity.

---

## Typography

**Fonts:** Google Fonts
- **Playfair Display** (serif) — title and stat values, weights 400/600, italic for title
- **DM Sans** (sans-serif) — all other text, weights 300/400/500/600

| Element | Font | Size | Weight | Colour |
|---|---|---|---|---|
| App title ("My Tasks") | Playfair Display italic | 24px | 400 | gradient (blue→pink) |
| Stat values | Playfair Display | 30px | 600 | varies (see palette) |
| Section label | DM Sans | 10px | 600 | `--text-3` |
| Task title | DM Sans | 14px | 400 | `--text` |
| Task description | DM Sans | 12px | 400 | `--text-2` |
| Task due date | DM Sans | 11px | 400 | `--text-3` |
| Calendar link | DM Sans | 11px | 400 | `--accent` |
| Button text | DM Sans | 13–14px | 500 | `#fff` |

Section labels are **uppercase**, **letter-spacing: 1.8px**.

---

## Spacing & Sizing

| Token | Value | Usage |
|---|---|---|
| Sidebar padding | `28px 22px` | Sidebar |
| Task area padding | `28px 32px` | Main content |
| Top bar padding | `16px 32px` | Header |
| Task card padding | `13px 16px` | Task row |
| Gap between tasks | `8px` | Task list |
| Gap between columns | `20px` | Task columns grid |
| Sidebar width | `300px` | Fixed |

---

## Border Radius

| Component | Radius |
|---|---|
| Analytics card | `14px` |
| Task cards | `10px` |
| Calendar popup | `14px` |
| Inputs, textarea, primary button | `8px` |
| Edit form inputs, save/cancel buttons | `7px` |
| Calendar nav buttons | `7px` |
| Progress bar | `99px` (pill) |
| Checkbox | `4px` |

**Shadows:** Removed in favour of `1px solid var(--border)` borders throughout. Calendar popup retains a subtle shadow: `0 8px 32px rgba(28,25,23,0.12)`.

---

## Icons

| Icon | Unicode | Usage | Tooltip |
|---|---|---|---|
| `✓` | U+2713 | Mark task as done | "Mark as done" |
| `✎` | U+270E | Edit active task | "Edit task" |
| `🗑` | emoji | Delete task | "Delete permanently" |
| inline SVG | — | Date picker trigger | — |

**Icon button style:** `color: var(--border)` at rest → `color: var(--text-2)` on hover. No background, no border.

---

## Components

### Buttons

**Primary (blue):** background `--accent` (`#4a6fd4`), hover `--accent-h` (`#3a5dc0`), white text, `border-radius: 8px`, padding `12px`, font-weight 500.

**Save (edit form):** same blue, `border-radius: 7px`, padding `7px 16px`, font-size 13px.

**Cancel (edit form):** background `--cream-dark`, text `--text-2`, hover `--border`, same sizing as Save.

**Calendar Confirm:** background `--accent`, `border-radius: 7px`, padding `9px 16px`, font-size 13px.

**Icon button:** no background or border, `font-size: 15px`, `color: --border` → `--text-2` on hover.

### Inputs & Textarea

`1px solid var(--border)` border, `border-radius: 8px`, padding `11px 14px`, background `var(--card)`, font-size 14px, placeholder colour `--text-3`. Border transitions to `--accent` on focus.

### Task Card

White background (`--card`), `border-radius: 10px`, `1px solid var(--border)` border. Subtle border darkens slightly on hover. Flex row: checkbox → content area → action buttons. No box-shadow.

Completed tasks have `text-decoration: line-through` and `color: --text-3` on the title.

### Analytics Card

White card (`--card`), `border-radius: 14px`, `1px solid var(--border)`. Three regions: donut SVG + stat numbers (left), progress bar (right).

**Donut:** SVG circle, track colour `#d8dcf0`, fill colour `#4a6fd4`, animates with CSS `transition: stroke-dasharray 0.4s ease`.

**Progress bar:** track `--cream-dark`, fill `linear-gradient(90deg, #4a6fd4, #c94fb5)`, `border-radius: 99px`, `transition: width 0.4s ease`.

**Stat values:** Total → `--text`, Active → `--accent` (blue), Done → `--pink`.

### Calendar Popup

White card (`--card`), `border-radius: 14px`, `1px solid var(--border)`, `box-shadow: 0 8px 32px rgba(28,25,23,0.12)`. Opens downward from the date trigger. Selected day: filled `--accent` circle with white text. Hover: `--accent-s` background with `--accent` text.

**Default state:** Today's date is pre-selected when the popup opens. The hidden `#new-due` input is only populated on "Confirm" — field remains optional. Resets to today after each task is added.

### Date Trigger — Optional Badge

The date trigger button contains an `optional` pill badge between the display text and the calendar icon. Badge: 10px, weight 500, color `--text-3`, background `--cream-dark`, `border-radius: 99px`. Hidden via `.date-trigger.has-date .optional-badge { display: none }` once a date is confirmed.

### Drag-and-Drop (Active Tasks)

Active task cards have `draggable="true"` and `cursor: grab`. Drag-over state: `border: 2px dashed var(--accent)` and `background: var(--accent-s)`. Dropping calls `PUT /tasks/reorder`. Done tasks are not draggable.

### Completion Animation

When an active task is ticked:
1. Checkbox shows `.checked` (blue fill) and plays the `celebrate` keyframe — scale pulse with fading blue ring shadow (0.55s).
2. 18 confetti dots burst radially from the checkbox, flying 28–56px over 0.7s then removed from the DOM.
3. Task stays visible for ~900ms before moving to the completed column.
4. Confetti colours: `#4a6fd4`, `#c94fb5`, `#7b9de8`, `#e070c8`, `#8faee0`. Dots: `position: fixed`, `z-index: 9999`, 7×7px circles.

---

## Layout

```
┌─────────────────────────────────────────────────┐
│  TOPBAR: title (left) + search (right)          │  --cream bg, border-bottom
├──────────────┬──────────────────────────────────┤
│              │  Analytics card                  │
│   SIDEBAR    │  ─────────────────────────────   │
│   Add New    │  ACTIVE TASKS   COMPLETED TASKS  │
│   form       │  [task cards]   [task cards]     │
│              │                                  │
└──────────────┴──────────────────────────────────┘
  300px fixed    flex: 1, overflow-y: auto
```

**Responsive breakpoint:** `640px` — sidebar stacks above task area, columns collapse to single column.
