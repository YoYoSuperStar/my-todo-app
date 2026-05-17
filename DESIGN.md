# Design Style Guide

## Colour Palette

| Role | Hex | Usage |
|---|---|---|
| **Blue accent** | `#5bb8f5` | Progress bar gradient end, donut fill |
| **Title blue-gray** | `#7a8fa6` | App title ("My Tasks") |
| **Purple primary** | `#8b7fd4` | Buttons, selected states, active stat, calendar fill, progress bar |
| **Purple hover** | `#7a6ec3` | Hover state for purple buttons |
| **Purple light** | `#f0eeff` | Calendar day hover background |
| **Pink accent** | `#f472a8` | Task dot (colour 3 in rotation) |
| **Page background** | `#f0f0f5` | Body, section dividers |
| **Card background** | `#fff` | Sidebar, top bar, task cards, analytics card, calendar popup |
| **Input background** | `#f4f4f8` | Text inputs, textarea, date trigger, nav buttons |
| **Border** | `#ebebf0` | Top bar, sidebar, calendar time input, edit form inputs |
| **Text primary** | `#333` | Task titles, body text, calendar days |
| **Text secondary** | `#888` | Task descriptions |
| **Text muted** | `#aaa` | Due dates, section labels' body, calendar day labels |
| **Icon default** | `#ccc` | Action icon buttons at rest |
| **Icon hover** | `#999` | Action icon buttons on hover |
| **Label grey** | `#999` | Section labels (ACTIVE TASKS, ADD NEW, etc.) |

---

## Typography

**Font:** Roboto (Google Fonts) — weights 400, 500, 700, 900

| Element | Size | Weight | Colour |
|---|---|---|---|
| App title ("My Tasks") | 22px | 400 | `#7a8fa6` |
| Section label | 11px | 700 | `#999` |
| Task title | 15px | 500 | `#333` |
| Task description | 13px | 400 | `#888` |
| Task due date | 12px | 400 | `#aaa` |
| Calendar link | 12px | 400 | `#8b7fd4` |
| Stat value | 28px | 800 | varies by type |
| Stat label | 11px | 700 | `#aaa` |
| Button text | 14–15px | 600 | `#fff` |

Section labels are always **uppercase**, **letter-spacing: 1.2px**.

App title has no letter-spacing (0) and no negative tracking — intentionally light and understated.

---

## Spacing & Sizing

| Token | Value | Usage |
|---|---|---|
| Card padding | `28px 24px` | Sidebar |
| Task area padding | `28px 32px` | Main content |
| Top bar padding | `18px 32px` | Header |
| Task card padding | `14px 18px` | Task row |
| Gap between tasks | `10px` | Task list |
| Gap between columns | `20px` | Task columns grid |
| Sidebar width | `300px` | Fixed |

---

## Border Radius

| Component | Radius |
|---|---|
| Analytics card, calendar popup | `20px` |
| Task cards | `14px` |
| Inputs, textarea, primary button | `12px` |
| Edit form inputs | `10px` |
| Save / cancel buttons | `10px` |
| Calendar nav buttons | `10px` |
| Progress bar | `99px` (pill) |
| Dot indicators | `50%` (circle) |

---

## Icons

All action icons are **plain Unicode characters** (not emoji) so they inherit `color` from CSS. Emoji render in fixed colour and ignore CSS `color`.

| Icon | Unicode | Usage | Tooltip |
|---|---|---|---|
| `✓` | U+2713 | Mark task as done | "Mark as done" |
| `↩` | U+21A9 | Recover completed task | "Recover task" |
| `✎` | U+270E | Edit active task | "Edit task" |
| `🗑` | emoji | Delete task | "Delete permanently" |
| inline SVG | — | Date picker trigger | — |

**Icon button style:** `color: #ccc` at rest → `color: #999` on hover. No background, no border.

> Note: `🗑` is currently an emoji and renders in its native colour. To keep full consistency, consider replacing it with `␡` (U+2421) or a similar plain character in a future iteration.

---

## Components

### Buttons

**Primary (purple):** background `#8b7fd4`, hover `#7a6ec3`, white text, `border-radius: 12px`, padding `13px`, font-weight 600.

**Save (edit form):** same purple, but `border-radius: 10px`, padding `8px 18px`, font-size 13px.

**Cancel (edit form):** background `#f4f4f8`, text `#888`, hover `#e8e8f0`, same sizing as Save.

**Calendar Confirm:** background `#8b7fd4`, `border-radius: 10px`, padding `10px 18px`, font-size 14px.

**Icon button:** no background or border, `font-size: 16px`, `color: #ccc` → `#999` on hover.

### Inputs & Textarea

Background `#f4f4f8`, no border, `border-radius: 12px`, padding `12px 16px`, font-size 14px, placeholder colour `#bbb`. Edit-form inputs use a `1px solid #ebebf0` border instead of the filled background.

### Task Card

White background (`#fff`), `border-radius: 14px`, `box-shadow: 0 1px 4px rgba(0,0,0,0.05)`. Flex row: coloured dot → content area → action buttons.

**Dot colours** rotate across tasks: `#8b7fd4` → `#5bb8f5` → `#f472a8` (index % 3).

Completed tasks have `text-decoration: line-through` and `color: #bbb` on the title.

### Analytics Card

White card, `border-radius: 16px`, `box-shadow: 0 1px 4px rgba(0,0,0,0.05)`. Three regions: donut SVG + stat numbers (left), progress bar (right).

**Donut:** SVG circle, track colour `#f0f0f5`, fill colour `#8b7fd4`, animates with CSS `transition: stroke-dasharray 0.4s ease`.

**Progress bar:** track `#f0f0f5`, fill `linear-gradient(90deg, #8b7fd4, #5bb8f5)`, `border-radius: 99px`, `transition: width 0.4s ease`.

### Calendar Popup

White card, `border-radius: 20px`, `box-shadow: 0 8px 32px rgba(0,0,0,0.13)`. Opens downward from the date trigger (`top: calc(100% + 8px)`). Selected day: filled `#8b7fd4` circle with white text.

**Default state:** Today's date is pre-selected when the popup opens (highlighted + shown in footer). The hidden `#new-due` input is only populated when the user clicks "Confirm", keeping the field genuinely optional. After a task is added, the picker resets to today.

### Date Trigger — Optional Badge

The date trigger button contains an `optional` pill badge (`<span class="optional-badge">`) between the display text and the calendar icon. Badge style: 10px, weight 600, color `#bbb`, background `#ebebf0`, `border-radius: 99px`. The badge is hidden via `.date-trigger.has-date .optional-badge { display: none }` once a date is confirmed.

### Drag-and-Drop (Active Tasks)

Active task cards have `draggable="true"` and a `cursor: grab` style. While dragging over a target card it receives `.drag-over`: `border: 2px dashed #8b7fd4` and `background: #f8f6ff`. Dropping calls `PUT /tasks/reorder` to persist the new order. Done tasks are not draggable.

### Completion Animation

When an active task is ticked:
1. The checkbox immediately shows `.checked` (purple fill) and plays the `celebrate` keyframe — a scale pulse with a fading purple ring shadow (0.55s).
2. 18 confetti dots (`<div class="confetti-dot">`) burst radially from the checkbox center, each flying to a random distance (28–56px) over 0.7s, then are removed from the DOM.
3. The task stays in the active list for ~900ms before `loadTasks()` re-renders it into the completed column.
4. Confetti dot colors: `#8b7fd4`, `#5bb8f5`, `#f5a623`, `#7ed321`, `#ff6b6b`. Dots are `position: fixed`, `z-index: 9999`, 7×7px circles.

---

## Layout

```
┌─────────────────────────────────────────────────┐
│  TOPBAR: title (left) + search (right)          │  white, border-bottom
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
