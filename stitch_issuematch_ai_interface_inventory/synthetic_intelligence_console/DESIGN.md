---
name: Synthetic Intelligence Console
colors:
  surface: '#111318'
  surface-dim: '#111318'
  surface-bright: '#37393f'
  surface-container-lowest: '#0c0e13'
  surface-container-low: '#1a1b21'
  surface-container: '#1e1f25'
  surface-container-high: '#282a2f'
  surface-container-highest: '#33353a'
  on-surface: '#e2e2e9'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#e2e2e9'
  inverse-on-surface: '#2e3036'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#ddb7ff'
  on-secondary: '#490080'
  secondary-container: '#6f00be'
  on-secondary-container: '#d6a9ff'
  tertiary: '#4cd7f6'
  on-tertiary: '#003640'
  tertiary-container: '#009eb9'
  on-tertiary-container: '#002f38'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#f0dbff'
  secondary-fixed-dim: '#ddb7ff'
  on-secondary-fixed: '#2c0051'
  on-secondary-fixed-variant: '#6900b3'
  tertiary-fixed: '#acedff'
  tertiary-fixed-dim: '#4cd7f6'
  on-tertiary-fixed: '#001f26'
  on-tertiary-fixed-variant: '#004e5c'
  background: '#111318'
  on-background: '#e2e2e9'
  surface-variant: '#33353a'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  body-base:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  mono-label:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  mono-data:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  mono-code:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  container-max: 1440px
  gutter: 20px
---

## Brand & Style

The design system is engineered for technical rigor and high-density information architecture. It moves away from the ethereal "AI magic" aesthetic, instead adopting a **Technical Minimalism** style that prioritizes "calculated certainty." The interface functions as a professional-grade instrument, evoking the feel of a high-end developer IDE or an advanced aerospace telemetry dashboard.

The aesthetic is characterized by deep, layered dark surfaces, high-contrast typography, and purposeful use of color to indicate system status and data confidence. Motion should be instantaneous and functional, reinforcing the sense of performance and reliability.

## Colors

The palette is anchored in a "Deep Dark" foundation to minimize eye strain during long-duration technical analysis. 

- **Primary Accents:** Indigo and Violet are used for interactive states and primary actions. Cyan is reserved for purely analytical data points and system-generated insights.
- **Surface Strategy:** We utilize a three-tier surface system. `#0A0C11` is the application canvas, while `#1A1E2A` is used for elevated interactive cards and containers.
- **Status Semanticism:** Colors like Emerald and Rose are never used for decoration; they are strictly reserved for conveying "Safe" or "Danger" states in code quality and matching confidence.

## Typography

This design system utilizes a dual-font strategy to differentiate between UI navigation and technical data.

1.  **Inter (Sans-serif):** Used for all structural UI elements, headings, and explanatory text. It provides a clean, neutral backbone that ensures the interface feels modern and accessible.
2.  **JetBrains Mono (Monospace):** Used for all "computed" output. This includes confidence scores, file paths, git hashes, and the "Signals" metrics. The monospace font signals to the user that the information is precise and system-generated.

For mobile devices, `display-lg` scales down to 24px and `headline-md` scales to 20px to maintain legibility within constrained viewports.

## Layout & Spacing

The layout is built on a **4px baseline grid** to ensure mathematical precision in alignment. 

- **Desktop:** A 12-column fluid grid with 20px gutters. Content is typically organized into a sidebar for navigation (fixed 260px) and a main stage for analysis.
- **Sectioning:** Use `lg` (24px) spacing for major component grouping and `md` (16px) for internal card padding.
- **Data Density:** In analytical views, use `sm` (8px) spacing to increase information density, allowing developers to see more context without scrolling.

## Elevation & Depth

Hierarchy is established through **Tonal Layering** and **Subtle Outlines** rather than heavy shadows.

- **Level 0 (Base):** `#0A0C11` - The background.
- **Level 1 (Cards):** `#1A1E2A` - Used for primary content containers. These should have a 1px solid border of `#2D3343`.
- **Level 2 (Popovers/Modals):** `#242938` - Used for floating elements. These receive a subtle 8px ambient shadow with a 20% opacity black tint to separate them from the background.
- **Interactive States:** On hover, card borders should transition to the Primary Indigo (`#6366F1`) at 40% opacity to indicate focus.

## Shapes

The shape language reflects the "Rounded Square" aesthetic common in modern developer tools.

- **Standard Elements:** Buttons, Input fields, and Cards use a base radius of `0.5rem` (8px).
- **Large Containers:** Modals or main layout areas use `rounded-xl` (24px) to soften the overall technical appearance.
- **Tags/Chips:** Use `rounded-lg` (16px) for a distinct visual departure from square action buttons.

## Components

### Signals (3-Bar Metric)
The "fan-in," "complexity," and "churn" signals are represented by a vertical 3-bar histogram. 
- **Inactive bar:** `#2D3343`.
- **Active bar:** Uses the semantic status colors (Emerald, Amber, Rose) based on the severity of the metric.
- **Labeling:** Always accompanied by a `mono-label` value.

### Readiness Gauge (Circular)
A circular progress ring representing matching confidence.
- **Track:** Transparent with a 1px border.
- **Fill:** A conic gradient from Indigo to Violet.
- **Center:** The percentage value rendered in `mono-data` at a larger scale.

### Buttons & Inputs
- **Primary Action:** Solid Indigo background with white text.
- **Ghost Action:** Transparent background with `#2D3343` border. Hover state adds a subtle background tint of `#1A1E2A`.
- **Inputs:** Darker background than the card surface (`#0A0C11`) to create an "etched" look, with JetBrains Mono for the input text.

### Cards
Cards are the primary vehicle for "Issue Matches." They must feature a header with the repository path in `mono-label` and a footer containing the Signals and Readiness components for quick scanning.