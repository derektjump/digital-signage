# UI Element Style Guide - Detailed Breakdowns

This document provides exact specifications for key UI elements in The Grid ecosystem. Use these details to replicate the styling in other applications.

---

## 1. L-Shaped Connector with Cyan Triangle (Grid Badge)

The connector creates an L-shape that goes **down** from "The Grid" text, then turns **right** toward the app name, ending with a small cyan triangle arrow.

### Visual Layout
```
[Icon] The Grid
       │
       └──▸ Prompted
```

### HTML Structure
```html
<div class="grid-badge__app-row">
  <!-- L-Shaped Connector -->
  <span class="grid-badge__connector" aria-hidden="true">
    <span class="grid-badge__connector-dot"></span>
  </span>
  <!-- App Name -->
  <span class="grid-badge__app-name">Prompted</span>
</div>
```

### CSS - Connector Container
```css
.grid-badge__connector {
  position: relative;
  width: 20px;              /* Total width of the L-shape */
  height: 18px;             /* Total height of the L-shape */
  flex-shrink: 0;
}
```

### CSS - Vertical Line (going down)
```css
.grid-badge__connector::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 1px;               /* Line thickness */
  height: 10px;             /* How far down the line goes */
  background: rgba(255, 255, 255, 0.25);  /* Subtle white line */
}
```

### CSS - Horizontal Line (turning right)
```css
.grid-badge__connector::after {
  content: '';
  position: absolute;
  top: 9px;                 /* Position at bottom of vertical line */
  left: 0;
  width: 100%;              /* Full width of container (20px) */
  height: 1px;              /* Line thickness */
  background: rgba(255, 255, 255, 0.25);
}
```

### CSS - Cyan Triangle Arrow
```css
.grid-badge__connector-dot {
  position: absolute;
  top: 9px;                 /* Aligned with horizontal line */
  right: 0;                 /* At the end of horizontal line */
  width: 0;
  height: 0;

  /* CSS Triangle pointing right */
  border-top: 3px solid transparent;
  border-bottom: 3px solid transparent;
  border-left: 4px solid #01ffff;  /* Cyan color, 4px wide */

  background: transparent;
  border-radius: 0;
  transform: translateY(-50%);     /* Center on the line */

  /* Subtle glow effect */
  filter: drop-shadow(0 0 2px #01ffff);
}
```

### CSS - App Row Container (positions the L-connector)
```css
.grid-badge__app-row {
  display: flex;
  align-items: center;
  margin-top: 4px;

  /* Align with where "The Grid" text starts */
  /* Icon width (26px) + gap (8px) = 34px from left edge */
  margin-left: 34px;

  overflow: hidden;
  max-height: 30px;

  transition:
    opacity 200ms ease-out,
    max-height 200ms ease-out,
    margin 200ms ease-out;
}
```

---

## 2. Text Styling - "The Grid" vs "Prompted"

### "The Grid" Title Text
```css
.grid-badge__title {
  font-family: 'Oxanium', sans-serif;   /* Display font */
  font-size: 14px;
  font-weight: 500;                      /* Medium weight */
  letter-spacing: 0.02em;                /* Slight letter spacing */
  color: #e4e8ec;                        /* Light gray text */
  white-space: nowrap;
}
```

### "Prompted" App Name Text
```css
.grid-badge__app-name {
  font-family: 'Onest', sans-serif;     /* Body font */
  font-size: 11px;                       /* Smaller than title */
  font-weight: 400;                      /* Normal weight */
  letter-spacing: 0.04em;                /* More letter spacing */
  color: #8b929a;                        /* Muted gray (dimmer) */
  white-space: nowrap;

  /* Positioning relative to connector */
  line-height: 1;
  margin-top: 1px;                       /* Fine-tune vertical alignment */
  margin-left: 6px;                      /* Space from triangle */
}
```

### Grid Badge Icon (Waffle Icon)
```css
.grid-badge__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  color: #01ffff;                        /* Cyan accent */
  transition: transform 150ms ease;
}

/* Hover effect - slight scale */
.grid-badge:hover .grid-badge__icon {
  transform: scale(1.08);
}
```

---

## 3. Navigation Item Hover - Cyan Underline Effect

The nav items have a sliding cyan underline that animates from left to right on hover.

### HTML Structure
```html
<a href="/home/" class="main-nav-link">
  <span class="material-symbols-outlined">home</span>
  <span class="nav-text-light">Home</span>
</a>
```

### CSS - Base Nav Link Style
```css
.main-nav-link {
  font-family: 'Onest', sans-serif !important;
  font-size: 14px !important;
  letter-spacing: 0.01em;
  transition: color 0.18s;
  position: relative;                    /* Required for ::after pseudo-element */
}

.main-nav-link:hover,
.main-nav-link:focus-visible {
  /* No background or color change on hover */
  color: #fff !important;
}
```

### CSS - Nav Link Text (when expanded)
```css
.nav-text-light {
  font-family: 'Oxanium', sans-serif !important;
  font-weight: 200;                      /* Extra light weight */
  letter-spacing: 0.05em;
  font-size: 15px;
}
```

### CSS - Underline Animation (Expanded Navbar)
```css
/* The underline pseudo-element - hidden by default */
.main-nav-link:not(.flex-col)::after {
  content: '';
  position: absolute;
  bottom: -2px;                          /* Below the text */
  left: 0;
  width: 0;                              /* Starts at 0 width */
  height: 0.5px;                         /* Very thin line */
  background-color: #00f0ff;             /* Cyan color */
  transition: width 0.3s ease;           /* Smooth animation */
}

/* On hover - expand to full width */
.main-nav-link:not(.flex-col):hover::after,
.main-nav-link:not(.flex-col):focus-visible::after {
  width: 100%;
}
```

### CSS - Underline Animation (Collapsed Navbar - Icon Only)
```css
/* Centered underline for collapsed state */
.main-nav-link.flex-col::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;                             /* Center horizontally */
  transform: translateX(-50%);
  width: 0;
  height: 0.5px;
  background-color: #00f0ff;
  transition: width 0.3s ease;
}

/* On hover - expand to 60% width (centered under icon) */
.main-nav-link.flex-col:hover::after,
.main-nav-link.flex-col:focus-visible::after {
  width: 60%;
}
```

### CSS - Icon Styling (Material Symbols)
```css
/* Ultra-thin icon variant */
.ultra-thin-icon {
  font-variation-settings: 'FILL' 0, 'wght' 200, 'GRAD' 0, 'opsz' 24;
}

/* Standard thin icon */
.material-icon-thin {
  font-variation-settings: 'FILL' 0, 'wght' 200, 'GRAD' 0, 'opsz' 24;
}

/* Navbar specific thin icons */
.navbar-icon-thin {
  font-variation-settings: 'FILL' 0, 'wght' 200, 'GRAD' 0, 'opsz' 24 !important;
}
```

### Alpine.js Classes for Responsive Behavior
```html
<!-- Expanded state -->
<a :class="'block py-2 px-3 rounded-md text-white font-medium transition flex items-center main-nav-link'">
  <span class="material-symbols-outlined mr-3 text-xl">home</span>
  <span class="nav-text-light">Home</span>
</a>

<!-- Collapsed state (icon stacked above text, if shown) -->
<a :class="'flex flex-col items-center justify-center py-3 w-full main-nav-link'">
  <span class="material-symbols-outlined text-2xl mb-1">home</span>
</a>
```

---

## 4. Collapse/Expand Button - Vertically Centered

The collapse button sits on the right edge of the navbar, perfectly centered vertically on the screen.

### HTML Structure
```html
<button
  @click="miniNav = !miniNav"
  class="collapse-expand-btn absolute top-1/2 right-[-24px] transform -translate-y-1/2 z-40 items-center justify-center w-12 h-12 rounded-full transition-colors duration-200 shadow-lg border-2 border-gray-800 hidden md:flex">

  <!-- Icon changes based on state -->
  <template x-if="!miniNav">
    <span class="material-symbols-outlined" style="font-size: 1.3rem; color: white;">
      keyboard_double_arrow_left
    </span>
  </template>
  <template x-if="miniNav">
    <span class="material-symbols-outlined" style="font-size: 1.3rem; color: white;">
      keyboard_double_arrow_right
    </span>
  </template>
</button>
```

### Key CSS Classes Breakdown

| Class | Purpose |
|-------|---------|
| `absolute` | Positions relative to the navbar container |
| `top-1/2` | Places top edge at 50% of parent height |
| `-translate-y-1/2` | Shifts up by 50% of own height (centers vertically) |
| `right-[-24px]` | Positions 24px outside the right edge (overlaps navbar edge) |
| `w-12 h-12` | 48px × 48px size (3rem) |
| `rounded-full` | Circular shape |
| `z-40` | High z-index to stay above other content |
| `hidden md:flex` | Hidden on mobile, visible on desktop |
| `shadow-lg` | Large shadow for depth |
| `border-2 border-gray-800` | 2px dark gray border |

### CSS - Button Background
```css
.collapse-expand-btn {
  background: #181818;                   /* Matches navbar background */
  transition: background 0.18s;
}

.collapse-expand-btn:hover {
  /* No background change on hover (removed for cleaner look) */
}
```

### Icon Specifications
```css
/* Material Symbols icon */
font-size: 1.3rem;                       /* ~20.8px */
color: white;

/* Icon names */
/* Expanded state: keyboard_double_arrow_left (<<) */
/* Collapsed state: keyboard_double_arrow_right (>>) */
```

### Vertical Centering Technique
```
The vertical centering uses a two-step CSS transform:

1. `top: 50%` - Moves the TOP edge of the button to the vertical center

   ┌─────────────────────┐
   │                     │
   │                     │
   │        ─────────────┼──[Button Top Edge]
   │                     │
   │                     │
   └─────────────────────┘

2. `transform: translateY(-50%)` - Shifts the button UP by half its own height

   ┌─────────────────────┐
   │                     │
   │                     │
   │        ─────────────┼──[●]  (Button center now aligned)
   │                     │
   │                     │
   └─────────────────────┘
```

### Full Button Positioning CSS (Tailwind equivalent)
```css
.collapse-expand-btn {
  position: absolute;
  top: 50%;
  right: -24px;                          /* Negative = outside parent */
  transform: translateY(-50%);
  z-index: 40;

  display: flex;                         /* Hidden on mobile via media query */
  align-items: center;
  justify-content: center;

  width: 48px;                           /* w-12 */
  height: 48px;                          /* h-12 */
  border-radius: 9999px;                 /* rounded-full */

  background: #181818;
  border: 2px solid #1f2937;             /* border-gray-800 */
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
              0 4px 6px -2px rgba(0, 0, 0, 0.05);  /* shadow-lg */

  transition: background-color 200ms, color 200ms;
}

/* Hide on mobile, show on desktop */
@media (min-width: 768px) {
  .collapse-expand-btn {
    display: flex;
  }
}
@media (max-width: 767px) {
  .collapse-expand-btn {
    display: none;
  }
}
```

---

## Quick Reference - Color Values

| Element | Color | Hex/RGBA |
|---------|-------|----------|
| Cyan accent | Primary brand | `#01ffff` |
| Cyan (alternate) | Hover/glow | `#00f0ff` |
| Text light | Primary text | `#e4e8ec` |
| Text muted | Secondary text | `#8b929a` |
| Nav background | Dark | `#181818` |
| Border subtle | Transparent white | `rgba(255,255,255,0.08)` |
| Line color | L-connector | `rgba(255,255,255,0.25)` |
| Border gray | Button borders | `#1f2937` (gray-800) |

## Quick Reference - Fonts

| Usage | Font Family | Weight | Size |
|-------|-------------|--------|------|
| Display/Headers | Oxanium | 500-600 | 14-18px |
| Body/UI | Onest | 400-500 | 11-14px |
| Nav items | Oxanium | 200 | 14-15px |
| Labels/Badges | Onest | 500 | 9-11px |

---

*Use this guide to maintain visual consistency across The Grid ecosystem applications.*
