# MeriAwaaz AI — Frontend Architecture Document

**Version:** 1.0  
**Date:** 2026-07-07  
**Status:** Source of Truth — Do Not Modify Without Review  
**Author:** Generated from full codebase + Google Stitch export analysis  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Design System — Sovereign Modernism](#2-design-system--sovereign-modernism)
3. [Complete Page Inventory](#3-complete-page-inventory)
4. [Routing Map](#4-routing-map)
5. [Navigation Flow](#5-navigation-flow)
6. [Detailed Page Breakdown](#6-detailed-page-breakdown)
   - 6.1 [MP Dashboard — Overview](#61-mp-dashboard--overview)
   - 6.2 [MP Dashboard — Heatmap](#62-mp-dashboard--heatmap)
   - 6.3 [MP Dashboard — Citizen Issues](#63-mp-dashboard--citizen-issues)
   - 6.4 [Citizen Submission Portal](#64-citizen-submission-portal)
7. [Component Hierarchy](#7-component-hierarchy)
8. [Shared Component Inventory](#8-shared-component-inventory)
9. [Backend API Integration Map](#9-backend-api-integration-map)
10. [Request/Response Mapping per Page](#10-requestresponse-mapping-per-page)
11. [TypeScript Type Reference](#11-typescript-type-reference)
12. [State Management](#12-state-management)
13. [Folder Mapping](#13-folder-mapping)
14. [Reusable Component Recommendations](#14-reusable-component-recommendations)
15. [Redundancy Analysis](#15-redundancy-analysis)
16. [Known Issues and Ambiguities](#16-known-issues-and-ambiguities)
17. [Future Extensibility](#17-future-extensibility)
18. [Developer Handoff](#18-developer-handoff)

---

## 1. Project Overview

**MeriAwaaz AI** ("My Voice AI") is a constituency development decision-support system for Members of Parliament in India. It collects citizen feedback through multiple channels (text, voice, photo, video), processes that feedback through a 5-agent LangGraph AI pipeline, clusters related issues, and surfaces prioritized project recommendations to the MP.

### System Architecture Summary

| Layer | Technology | Status |
|---|---|---|
| Frontend | Next.js 16.2.10, React 19.2.4, TypeScript 5, Tailwind CSS v4 | Default template only — not built |
| Backend | FastAPI (Python), LangGraph 5-agent pipeline | Complete and functional |
| Database | SQLite (sqlite3, no ORM) | Schema: submissions, clusters, recommendations, agent_log |
| Vector DB | ChromaDB with Gemini embeddings | Operational |
| In-memory store | Python singleton `STORE` | Primary source for recommendations, keyed by project_id |
| LLM | Google Gemini (via LangChain) | Required for pipeline |

### User Personas

**MP (Member of Parliament)** — Admin-level user who views the AI-generated dashboard, reviews recommendations, drills into supporting evidence, and monitors citizen issues by location and category.

**Citizen** — Public user who submits a constituency issue via text, voice recording, or photo. The submission portal is channel-agnostic.

### Pipeline Summary (for frontend context)

When a citizen submits an issue, the backend runs 5 agents inline (synchronously):
1. **Citizen Intelligence** — Parses raw input, extracts category/location/summary
2. **Demand Intelligence** — Clusters the submission with similar past issues
3. **Knowledge Fusion** — Retrieves scheme/policy context from vector DB
4. **Policy Recommendation** — Scores the issue and merges it into a project recommendation
5. **Explainability** — Generates supporting evidence for the recommendation

This pipeline takes 20–60 seconds depending on LLM latency. The frontend **must poll** for results rather than waiting on the initial POST.

---

## 2. Design System — Sovereign Modernism

Source: `stitch_meriawaaz_ai_constituency_platform/.../sovereign_modernism/DESIGN.md`

### 2.1 Color Palette

| Token | Hex | Usage |
|---|---|---|
| `primary` | `#000000` | Primary text, structural headers |
| `primary-container` | `#0b1d2a` | Sidebar background, card header strips, deep navy surfaces |
| `on-primary-container` | `#748696` | Muted text on dark backgrounds |
| `secondary` | `#455f87` | Interactive elements, primary action buttons, links |
| `secondary-container` | `#b5d0fd` | Soft blue chips, category filter backgrounds |
| `tertiary-fixed` | `#ffdea9` | Saffron — high-value accents, Voice FAB, active sidebar indicator |
| `tertiary-fixed-dim` | `#ffba27` | Saffron medium — priority badges (High) |
| `background` | `#f7f9fc` | Page background |
| `surface-container-lowest` | `#ffffff` | Card surfaces, modal backgrounds |
| `surface-container-low` | `#f2f4f7` | Table row alternates, chip backgrounds |
| `surface-container` | `#eceef1` | Dividers, subtle backgrounds |
| `outline` | `#74777c` | Border default |
| `outline-variant` | `#c3c7cc` | Subtle borders, input borders |
| `on-surface` | `#191c1e` | Default body text |
| `on-surface-variant` | `#43474b` | Secondary text, metadata |
| `error` | `#ba1a1a` | Error states, destructive badges |
| `error-container` | `#ffdad6` | Error backgrounds |

**India Green** (for "Resolved" status): `#4CAF50` — mentioned in DESIGN.md but not in the token map. Use `#4CAF50` / `#2E7D32` for success indicators.

### 2.2 Typography

| Scale | Font | Size | Weight | Line Height | Letter Spacing |
|---|---|---|---|---|---|
| `display-lg` | Inter | 48px | 700 | 56px | -0.02em |
| `display-lg-mobile` | Inter | 32px | 700 | 40px | -0.01em |
| `headline-lg` | Inter | 32px | 600 | 40px | -0.01em |
| `headline-md` | Inter | 24px | 600 | 32px | — |
| `body-lg` | Inter | 18px | 400 | 28px | — |
| `body-md` | Inter | 16px | 400 | 24px | — |
| `label-md` | Inter | 14px | 500 | 20px | 0.01em |
| `label-sm` | Inter | 12px | 600 | 16px | 0.05em |

Inter must be loaded via `next/font/google` in `layout.tsx`, weights 300–800.

### 2.3 Spacing

- Base unit: 4px
- Gutter: 24px
- Desktop margin: 40px
- Mobile margin: 16px
- Container max-width: 1280px
- All spacing values must be multiples of 4px.

### 2.4 Border Radius

| Token | Value | Usage |
|---|---|---|
| `sm` | 0.25rem (4px) | Tiny elements |
| `DEFAULT` | 0.5rem (8px) | Cards, inputs |
| `md` | 0.75rem (12px) | Large inputs |
| `lg` | 1rem (16px) | Main dashboard containers |
| `xl` | 1.5rem (24px) | Modals, floating panels |
| `full` | 9999px | Pill buttons, badges |

### 2.5 Elevation

- **Level 0 (Background):** `#f5f7fa`
- **Level 1 (Cards):** White, 1px border `#e6edf3`, no shadow
- **Level 2 (Interactive/Floating):** White, `box-shadow: 0px 4px 20px rgba(0,0,0,0.05)`
- **Backdrop Blur:** `backdrop-filter: blur(20px)` on navbars and FABs

### 2.6 Icons

All icons use **Material Symbols Outlined** via Google Fonts CDN:
```html
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
```
Icon names referenced in Stitch: `dashboard`, `map`, `people`, `bar_chart`, `mic`, `search`, `filter_list`, `chevron_right`, `add`, `notifications`, `info`, `close`, `check_circle`, `warning`, `error`, `arrow_upward`, `arrow_downward`, `location_on`, `school`, `local_hospital`, `directions_car`, `water_drop`, `bolt`, `work`, `recycling`.

### 2.7 Component Style Rules

**Primary Button:** `#0b1d2a` background, white text, pill radius (9999px)  
**Secondary Button:** `#455f87` outline 1px, white background  
**Ghost Button:** No border/background, `#455f87` text  
**Voice FAB:** `#FF9933` circle, microphone icon, 2-second pulse keyframe animation  
**Active sidebar item:** Saffron (`#FF9933`) 3px left-edge vertical bar  
**Card hover:** 2px `#455f87` border  
**Input focus:** 2px `#455f87` ring, white background  

---

## 3. Complete Page Inventory

| # | Page | Route | Stitch Design? | Primary User |
|---|---|---|---|---|
| 1 | MP Dashboard — Overview | `/dashboard` | Yes (Screen 1) | MP |
| 2 | MP Dashboard — Heatmap | `/dashboard/heatmap` | Yes (Screen 2) | MP |
| 3 | MP Dashboard — Citizen Issues | `/dashboard/issues` | Yes (Screen 3) | MP |
| 4 | Citizen Submission Portal | `/submit` | **No** — design from spec only | Citizen |

**Note:** No login/authentication screen exists in either the Stitch export or the backend. Authentication is out of scope for v1. If added later, it will precede `/dashboard` and `/submit`.

---

## 4. Routing Map

Next.js App Router. All routes are under `frontend/app/`.

```
app/
├── layout.tsx                    ← Root layout: Inter font, global CSS, sidebar wrapper
├── page.tsx                      ← Redirect to /dashboard (or /submit for citizens)
├── dashboard/
│   ├── layout.tsx                ← Shared sidebar + top navbar for MP views
│   ├── page.tsx                  ← MP Dashboard Overview (Screen 1)
│   ├── heatmap/
│   │   └── page.tsx              ← MP Heatmap (Screen 2)
│   └── issues/
│       └── page.tsx              ← MP Citizen Issues Table (Screen 3)
└── submit/
    └── page.tsx                  ← Citizen Submission Portal (Screen 4)
```

### Route Behaviour

| Route | On Load | Auth Required |
|---|---|---|
| `/` | Redirect to `/dashboard` | No |
| `/dashboard` | Fetch `GET /api/dashboard` | No (v1) |
| `/dashboard/heatmap` | Fetch `GET /api/dashboard` (heatmap field) | No (v1) |
| `/dashboard/issues` | Fetch `GET /api/dashboard` (projects field) | No (v1) |
| `/submit` | Static form, no initial fetch | No |

---

## 5. Navigation Flow

```
[ Root / ] ──► [ /dashboard (Overview) ]
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
   [ /dashboard ]  [ /dashboard  [ /dashboard
    (Overview)      /heatmap ]    /issues ]
          │                           │
          │ Click project card         │ Click issue row
          ▼                           ▼
   [ Evidence Panel ]          [ Issue Detail Panel ]
   (slide-in, same page)       (slide-in, same page)
          │
          │ Click "View Detailed Analysis" 
          ▼
   [ Calls GET /api/explain/{project_id} ]
   (inline panel expansion — same page)

[ /submit ] ── is standalone, no sidebar nav
               Citizen submits → polls for result → shows recommendation card
```

### Sidebar Navigation (MP views)

Fixed left sidebar, 280px wide, deep navy (`#0b1d2a`) background.

| Item | Icon | Route | Active Indicator |
|---|---|---|---|
| Dashboard | `dashboard` | `/dashboard` | Saffron left bar |
| Heatmap | `map` | `/dashboard/heatmap` | Saffron left bar |
| Issues | `people` | `/dashboard/issues` | Saffron left bar |
| Analytics | `bar_chart` | (future — not built) | — |

Top of sidebar: National Emblem (monochrome white), "MeriAwaaz AI" wordmark.  
Bottom of sidebar: MP profile avatar placeholder.

### Mobile Navigation (Citizen view — `/submit`)

Fixed bottom navigation bar, 4 items:
| Item | Icon | Route |
|---|---|---|
| Home | `home` | `/submit` |
| New Issue | `add` | `/submit` (scrolls to form) |
| My Feedback | `notifications` | (future — not built) |
| Profile | `person` | (future — not built) |

---

## 6. Detailed Page Breakdown

### 6.1 MP Dashboard — Overview

**Route:** `/dashboard`  
**Stitch file:** `mp_dashboard_overview/code.html`  
**API call on load:** `GET /api/dashboard`

#### 6.1.1 Layout

```
┌────────────────────────────────────────────────────────────┐
│ SIDEBAR (280px fixed)  │  MAIN CONTENT (fluid)             │
│  Logo + Nav            │  ┌──────────────────────────────┐ │
│                        │  │  TOP BAR: Title + Search     │ │
│                        │  ├──────────────────────────────┤ │
│                        │  │  BENTO GRID (12-col)         │ │
│                        │  │  Row 1: 4 Stat Cards         │ │
│                        │  │  Row 2: AI Summary | Quick   │ │
│                        │  │         Card       | Nav     │ │
│                        │  │  Row 3: Top Recs   | Urgent  │ │
│                        │  │         List       | Issues  │ │
│                        │  │  Row 4: Bar Chart (full width)│ │
│                        │  └──────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

#### 6.1.2 Widgets / Sections

**A. Stat Cards (Row 1) — 4 cards, each 3-cols wide**

Each card: white surface, 1px border, `border-radius: 1rem`, `padding: 24px`

| Card | Metric | Data Source |
|---|---|---|
| Total Submissions | `DashboardData.total_submissions` | `GET /api/dashboard` |
| Active Projects | `DashboardData.projects.length` (derived) | `GET /api/dashboard` |
| High Priority | Count of projects where `priority_score >= 70` (derived) | `GET /api/dashboard` |
| Last Updated | `DashboardData.last_updated` | `GET /api/dashboard` |

Each stat card contains:
- Large number (display-lg, `#0b1d2a`)
- Label text (label-md, `#43474b`)
- Trend indicator icon (arrow_upward / arrow_downward in green/red — **no backend field for this; UI-only placeholder**)

**AMBIGUITY A:** Trend indicators (up/down arrows with percentage change) appear in the Stitch design but the backend returns no historical comparison data. These must be rendered as static placeholder UI or omitted in v1. Do not invent a delta calculation.

**B. AI Summary Card (Row 2, cols 1–7)**

- Deep navy header strip (`#0b1d2a`) with "AI Constituency Summary" title and robot/sparkle icon
- Body: Auto-generated summary text
- **AMBIGUITY B:** No backend endpoint returns an AI-generated constituency summary. The `GET /api/dashboard` response does not include a summary string. This panel cannot be populated in v1. Options: (1) Leave as a static placeholder with lorem text, (2) derive summary from the top-3 recommendations. Ask the product owner before building.

**C. Quick Navigation Card (Row 2, cols 8–12)**

Three action buttons, each navigating to a dashboard sub-page:
- "View Heatmap" → `/dashboard/heatmap`
- "All Issues" → `/dashboard/issues`
- "Export Report" → (not backed; placeholder button in v1)

**D. Top Recommendations List (Row 3, cols 1–8)**

- Section header: "Top Priority Projects"
- Ordered list of `ProjectCard` items from `DashboardData.projects`, sorted by `priority_score` descending, showing top 5
- Each row:
  - Project title (`body-md`, bold)
  - Category badge (colored chip, see badge mapping in §8)
  - Priority score bar (thin 4px progress bar)
  - Priority score number (label-md)
  - `is_existing_plan_project` indicator: if true, show a small "Plan" badge in secondary blue
  - Chevron right icon → clicking opens Evidence Panel (slide-in, same page)

**E. Urgent Issues Feed (Row 3, cols 9–12)**

- Section header: "Urgent Issues"
- Derived from `DashboardData.projects` where `priority_score >= 80`, showing latest 3–4
- Each item: title, category icon, score badge
- **AMBIGUITY C:** "Urgency" threshold is undefined in the backend. A reasonable default is `priority_score >= 80`. Confirm with product owner.

**F. Priority Bar Chart (Row 4, full width)**

- Horizontal bar chart: X-axis = category names, Y-axis = average `priority_score` per category
- Data derived client-side from `DashboardData.projects` by grouping on `category` and averaging scores
- No dedicated backend endpoint for chart data
- Library: Recharts (`BarChart` component)
- Bars colored by category (see §8.4 category color map)

#### 6.1.3 Interactions

| Interaction | Trigger | Outcome |
|---|---|---|
| Click project row in Top Recs | Left click | Opens Evidence Panel slide-in |
| Click "View Heatmap" | Button click | Navigate to `/dashboard/heatmap` |
| Click "All Issues" | Button click | Navigate to `/dashboard/issues` |
| Click "Export Report" | Button click | v1: no-op / toast "Coming soon" |
| Search input | Type | v1: filter projects list client-side by title |

#### 6.1.4 States

| State | Trigger | UI |
|---|---|---|
| Loading | Initial mount, awaiting `GET /api/dashboard` | Skeleton loaders in each card slot |
| Empty | `projects: []` returned | "No recommendations yet. Submit citizen issues to get started." |
| Error | Network error or 500 from backend | Error banner at top with retry button |
| Success | Data returned | Full bento grid rendered |
| Evidence Panel open | Project row clicked | Slide-in panel from right, backdrop dimmed |

#### 6.1.5 Evidence Panel (Slide-in)

Triggered by clicking any project in the Top Recs list or anywhere on the dashboard.

**Panel structure:**
- Header: Project title + Close (×) button
- Score breakdown table:
  - Citizen Demand: `breakdown.citizen_demand` / 40
  - Severity: `breakdown.severity` / 30
  - Population Impact: `breakdown.population_impact` / 20
  - Cost Feasibility: `breakdown.cost_feasibility` / 10
  - Total: `priority_score` / 100
- "View Detailed Analysis" button → triggers `GET /api/explain/{project_id}`
- Explanation section (conditionally shown after explain call):
  - Summary text (`explanation.summary`)
  - Evidence list (`explanation.evidence` as bullet list)
  - Confidence score (`explanation.confidence_score` as percentage)

**Explain endpoint states:**
- Loading: spinner inside panel
- Success: display explanation fields
- Error (500 from Bug A): Display "Analysis temporarily unavailable. Please try again later." — do NOT show raw error.

---

### 6.2 MP Dashboard — Heatmap

**Route:** `/dashboard/heatmap`  
**Stitch file:** `mp_dashboard_heatmap/code.html`  
**API call on load:** `GET /api/dashboard` (for heatmap and projects fields)

#### 6.2.1 Layout

```
┌────────────────────────────────────────────────────────────┐
│ SIDEBAR (280px)  │  ┌──────────────────────────────────┐   │
│                  │  │  TOP BAR                         │   │
│                  │  ├──────┬──────────────────┬────────┤   │
│                  │  │      │                  │        │   │
│                  │  │ LEFT │   MAP CANVAS     │ RIGHT  │   │
│                  │  │FILTER│   (full-bleed)   │ DRILL  │   │
│                  │  │PANEL │   SVG overlay    │ DOWN   │   │
│                  │  │(280px│                  │ PANEL  │   │
│                  │  │glass)│                  │(320px, │   │
│                  │  │      │                  │slide-in│   │
│                  │  │      │                  │)       │   │
│                  │  └──────┴──────────────────┴────────┘   │
│                  │  MAP CONTROLS (zoom ±, locate)           │
└────────────────────────────────────────────────────────────┘
```

#### 6.2.2 Widgets

**A. Filter Sidebar (Left, 280px glass panel)**

- `backdrop-filter: blur(20px)`, white with 60% opacity
- Filters:
  - Category multi-select checkboxes (Education, Healthcare, Roads, Water, Sanitation, Electricity, Vocational, Other)
  - Priority range slider (0–100)
  - Date range picker (start/end — **AMBIGUITY D:** no date filter in `GET /api/dashboard` response; filter would be client-side only)
- "Apply Filters" primary button
- "Clear All" ghost button
- All filtering is client-side on the `projects` array.

**B. Map Canvas (Center, full-bleed)**

- Full-page SVG or Leaflet map of the MP's constituency
- **CRITICAL — AMBIGUITY E:** `GET /api/dashboard` always returns `heatmap: []`. The heatmap data is hardcoded empty in the backend (`dashboard.py`). This screen is aspirational and cannot show real heat data in v1.
- Fallback for empty heatmap: Render the map canvas with constituency outline only and a banner: "Heatmap data is being generated. Check back soon."
- If/when `heatmap` is populated, each `HeatmapPoint` has fields: see `backend/app/schemas/dashboard.py` for structure.
- Map library: Leaflet + react-leaflet (must be installed — not in `package.json` yet).
- SVG overlay: Render colored circles at lat/lng positions, radius proportional to intensity.

**C. Drill-Down Panel (Right, 320px slide-in)**

Appears when a map region/cluster is clicked.

- Panel header: Location name + Close button
- List of projects in that location
- Each project: title, priority badge, category icon
- Clicking a project opens the Evidence Panel (same as Dashboard Overview)

**D. Map Controls**

- Zoom in (`+`) button
- Zoom out (`-`) button
- "Locate constituency" button (resets map to constituency bounds)

#### 6.2.3 States

| State | Trigger | UI |
|---|---|---|
| Loading | `GET /api/dashboard` in progress | Map canvas shows skeleton, filter sidebar shows loading state |
| Empty heatmap | `heatmap: []` (always in v1) | "Heatmap data being generated" banner over map |
| Populated heatmap | When backend provides data | Colored circles rendered on map |
| Filter active | User has applied filters | Active filter chips shown above map |
| Drill-down open | Region clicked | Right panel slides in |

---

### 6.3 MP Dashboard — Citizen Issues

**Route:** `/dashboard/issues`  
**Stitch file:** `mp_dashboard_citizen_issues/code.html`  
**API call on load:** `GET /api/dashboard` (projects field)

#### 6.3.1 Layout

```
┌────────────────────────────────────────────────────────────┐
│ SIDEBAR (280px)  │  ┌──────────────────────────────────┐   │
│                  │  │  PAGE TITLE + AI Prediction Banner│  │
│                  │  ├──────────────────────────────────┤   │
│                  │  │  SEARCH BAR + FILTER CHIPS       │   │
│                  │  ├──────────────────────────────────┤   │
│                  │  │  ISSUES TABLE                    │   │
│                  │  │  (paginated, 10 rows per page)   │   │
│                  │  ├──────────────────────────────────┤   │
│                  │  │  PAGINATION CONTROLS             │   │
│                  │  └──────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

#### 6.3.2 Widgets

**A. AI Prediction Banner**

- Full-width banner at the top with a saffron left-border accent
- Icon: sparkle/robot
- Text: "AI has identified [N] emerging clusters in [top-category] requiring attention."
- **AMBIGUITY F:** This is a derived UI metric. Compute client-side: count unique categories where `priority_score >= 60`. No dedicated backend field.

**B. Search Bar**

- Text input, full-width on mobile, 400px on desktop
- Icon: `search` (Material Symbols)
- Placeholder: "Search issues by title, category, or location..."
- Filtering: client-side on `projects` array by title string match
- `border-radius: 0.5rem`, `border: 1px solid #e6edf3`, focus ring `#455f87`

**C. Category Filter Chips**

Horizontal scrollable row of pill-shaped filter chips:
- All (default active)
- Education
- Healthcare
- Roads
- Water
- Sanitation
- Electricity
- Vocational
- Other

Active chip: `background: #0b1d2a`, white text  
Inactive chip: `background: #f2f4f7`, `#43474b` text  
Clicking a chip filters the table client-side.

**D. Status Checkboxes**

Three checkboxes for status filter:
- Not Started
- In Progress
- Completed

**CRITICAL — AMBIGUITY G:** These status values (`Not Started`, `In Progress`, `Completed`) do not exist anywhere in the backend schema. `ProjectCard` has no `status` field. `Recommendation` has no `status` field. The Stitch design shows these but the backend cannot support them in v1.

**Options (ask product owner):**
1. Remove status filters entirely in v1
2. Derive a pseudo-status: `priority_score < 40` = "Not Started", `40-70` = "In Progress", `> 70` = "Completed" (arbitrary, misleading)
3. Add a `status` field to the backend schema (requires backend change)

Until resolved: **render the checkbox UI but disable interaction with a "Coming soon" tooltip.**

**E. Issues Table**

Columns:
| Column | Data Source | Notes |
|---|---|---|
| # | Row index (1-based) | Client-derived |
| Project Title | `ProjectCard.title` | — |
| Category | `ProjectCard.category` | Rendered as colored badge |
| Priority Score | `ProjectCard.priority_score` | Progress bar + number |
| Priority Level | Derived from score | High/Medium/Low badge (see §8.3) |
| Plan Project | `ProjectCard.is_existing_plan_project` | Checkmark icon if true |
| Status | **No backend field** | See AMBIGUITY G above |
| Actions | — | "View Details" button |

Row behaviour:
- Clicking anywhere on a row opens the Evidence Panel (same slide-in as Overview page)
- "View Details" button = same as row click
- Hover: row background shifts to `#f2f4f7`, 2px `#455f87` left border
- Alternating row background: odd rows `#ffffff`, even rows `#f9fafb`

**F. Pagination Controls**

- 10 rows per page (client-side pagination)
- Previous / Next buttons (ghost style)
- Page indicator: "Showing 1–10 of N"
- Direct page number buttons (up to 5 visible)

#### 6.3.3 Interactions

| Interaction | Trigger | Outcome |
|---|---|---|
| Type in search | Keypress | Filter table client-side, reset to page 1 |
| Click category chip | Click | Filter table by category, reset to page 1 |
| Click column header | Click | Sort table by that column (client-side) |
| Click table row | Click | Open Evidence Panel slide-in |
| Click pagination | Click | Change page |
| Click "View Details" | Button click | Open Evidence Panel slide-in |

#### 6.3.4 States

| State | Trigger | UI |
|---|---|---|
| Loading | `GET /api/dashboard` in progress | Table rows replaced with skeleton lines |
| Empty table | `projects: []` | "No issues found. Citizen submissions will appear here." |
| Filtered empty | Search/filter yields no results | "No issues match your filters." + "Clear filters" link |
| Error | API failure | Error banner + retry button |
| Evidence Panel open | Row clicked | Slide-in from right |

---

### 6.4 Citizen Submission Portal

**Route:** `/submit`  
**Stitch design:** **None** — this screen was not designed in the Stitch export. Design from backend spec and DESIGN.md only.

**IMPORTANT:** The entire citizen portal UI must be designed from scratch aligned with the Sovereign Modernism system. No Stitch reference exists.

#### 6.4.1 Layout

```
┌────────────────────────────────────────────────────────────┐
│  MOBILE (4-col fluid, 16px margins)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TOP BAR: Logo + "Report an Issue"                   │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  HERO: "Your voice shapes your constituency"         │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  CHANNEL SELECTOR (horizontal tab row)               │  │
│  │  [Text] [Voice] [Photo]                              │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  SUBMISSION FORM (dynamic per channel)               │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  SUBMIT BUTTON                                       │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  RESULT PANEL (shown after submission)               │  │
│  └──────────────────────────────────────────────────────┘  │
│  BOTTOM NAV (fixed)                                        │
└────────────────────────────────────────────────────────────┘
```

#### 6.4.2 Channel Selector

Three tabs: Text, Voice, Photo  
Active tab: `#0b1d2a` background, white text, pill radius  
Inactive tab: `#f2f4f7` background, `#43474b` text

Selecting a tab shows the relevant input form section below.

#### 6.4.3 Text Channel Form

```
Field: "Describe your issue"
  Type: <textarea>
  Placeholder: "Describe the problem in your area in any language..."
  Min height: 120px
  Max length: 2000 characters
  Character counter shown below
  Backend field: text (multipart)
  Backend channel value: "text"
```

#### 6.4.4 Voice Channel Form

```
Field: Voice Recording
  UI: Large circular Voice FAB (Saffron #FF9933, 80px diameter)
      Pulse animation (2s keyframe) when idle
      Recording animation (red pulse, waveform) when active
  States:
    - Idle: Microphone icon, "Tap to record"
    - Recording: Red pulse, "Recording... tap to stop", timer
    - Recorded: Waveform preview, "Tap to re-record" ghost link
  Backend field: audio (multipart, .webm/.mp3 file)
  Backend channel value: "voice"
  Note: Uses Web API MediaRecorder. Output format: audio/webm.
  AMBIGUITY H: Backend expects audio URL field. Confirm whether
  the audio file should be uploaded as multipart binary or as a
  pre-uploaded URL. Current code in submissions.py accepts both.
```

#### 6.4.5 Photo Channel Form

```
Field: Photo Upload
  UI: Dashed border upload box, 200px height
      "Click to upload or drag and drop"
      Accept: image/jpeg, image/png, image/webp
      Max: 10MB
  Preview: Shows thumbnail after selection
  Backend field: photo (multipart, image file)
  Backend channel value: "photo"
  CORS note: Requires backend to serve /uploads static files.
```

#### 6.4.6 Location Field (all channels)

```
Field: "Your location / village"
  Type: <input type="text">
  Placeholder: "Village, block, or landmark name"
  Optional for citizens but helps AI clustering
  Not a separate backend field — included in text description
  or parsed by agent from context.
  AMBIGUITY I: No explicit location field in multipart schema.
  The backend parses location from raw_text. Advise citizens to
  include location in their description.
```

#### 6.4.7 Submit Button

- Label: "Submit Issue"
- Style: Primary button (Deep Navy `#0b1d2a`, white text, pill)
- Width: Full-width on mobile
- Disabled state: grayed out until channel-appropriate input provided

#### 6.4.8 Submission Flow

The backend pipeline runs synchronously and takes 20–60 seconds. The frontend **must not block** the UI waiting for the POST response.

**Recommended polling approach:**

1. `POST /api/submissions` (multipart) — returns immediately with `{status, submission_id, photo_url, audio_url, recommendation}`
2. **If `recommendation` is null in the response:** Begin polling `GET /api/dashboard` every 5 seconds to detect when the new project appears
3. **AMBIGUITY J:** There is no `GET /api/submissions/{submission_id}` endpoint in the current backend. Polling must use the dashboard endpoint or the trace endpoint. Confirm with backend team. The implementation checklist mentions polling but no dedicated status endpoint exists.
4. After receiving recommendation: display Result Panel

**Polling strategy:**
- Poll interval: 5 seconds
- Max polls: 24 (2 minutes total)
- On timeout: "Your submission was received. Check back later for AI analysis results."
- Cancel polling when component unmounts

#### 6.4.9 Result Panel

Shown below the form after successful submission + AI processing:

- Success icon (checkmark, India Green)
- "Your issue has been recorded!" heading
- Submission ID displayed (for reference)
- Recommendation card (if available):
  - Project title
  - Category badge
  - Priority score (progress bar)
  - One-sentence explanation summary (from `recommendation.explanation.summary`)
- "Submit another issue" link → resets form

#### 6.4.10 States

| State | UI |
|---|---|
| Idle / empty form | Default form, submit button disabled |
| Input provided | Submit button enabled |
| Submitting | Button shows spinner, "Submitting...", form locked |
| Submission received, AI processing | Progress indicator: "AI is analyzing your submission..." with animated pulse. Polling active. |
| AI complete, result available | Result Panel shown with recommendation card |
| AI timeout (>2 min) | "Received, results pending. Check the dashboard." |
| Network error | Error toast: "Submission failed. Please try again." |
| File too large | Inline validation error on upload field |

---

## 7. Component Hierarchy

```
app/
├── layout.tsx
│   └── RootLayout
│       ├── <html lang="hi">  (bilingual support: Hindi + English)
│       ├── <body>
│       │   ├── [MP routes: /dashboard/**]
│       │   │   └── MPLayout
│       │   │       ├── Sidebar
│       │   │       │   ├── GovernmentEmblem
│       │   │       │   ├── SidebarNavItem (×4)
│       │   │       │   └── MPProfileAvatar
│       │   │       ├── TopBar
│       │   │       │   ├── PageTitle
│       │   │       │   └── SearchInput
│       │   │       └── <main> {page content}
│       │   │
│       │   └── [Citizen route: /submit]
│       │       └── CitizenLayout
│       │           ├── CitizenTopBar
│       │           ├── <main> {page content}
│       │           └── MobileBottomNav
│
├── dashboard/page.tsx
│   └── DashboardOverviewPage
│       ├── StatCard (×4)
│       ├── AISummaryCard
│       ├── QuickNavCard
│       ├── TopRecommendationsList
│       │   └── ProjectRow (×N)
│       │       ├── CategoryBadge
│       │       ├── PriorityScoreBar
│       │       └── PriorityBadge
│       ├── UrgentIssuesFeed
│       │   └── UrgentIssueItem (×3-4)
│       ├── PriorityBarChart
│       └── EvidencePanel (conditional, slide-in)
│           ├── ScoreBreakdownTable
│           ├── ExplainButton
│           └── ExplanationSection (conditional)
│               ├── ExplanationSummary
│               └── EvidenceList
│
├── dashboard/heatmap/page.tsx
│   └── HeatmapPage
│       ├── FilterSidebar
│       │   ├── CategoryCheckboxGroup
│       │   ├── PriorityRangeSlider
│       │   └── DateRangePicker
│       ├── MapCanvas
│       │   ├── LeafletMap
│       │   ├── HeatmapOverlay (conditonal — data always empty in v1)
│       │   └── EmptyHeatmapBanner
│       ├── MapControls
│       └── DrillDownPanel (conditional, slide-in)
│           └── LocationProjectList
│               └── ProjectRow
│
├── dashboard/issues/page.tsx
│   └── CitizenIssuesPage
│       ├── AIPredictionBanner
│       ├── SearchBar
│       ├── CategoryFilterChips
│       ├── StatusCheckboxes (disabled in v1)
│       ├── IssuesTable
│       │   ├── TableHeader (sortable columns)
│       │   └── TableRow (×N per page)
│       │       ├── CategoryBadge
│       │       ├── PriorityScoreBar
│       │       ├── PriorityBadge
│       │       └── ViewDetailsButton
│       ├── PaginationControls
│       └── EvidencePanel (shared — same as Overview)
│
└── submit/page.tsx
    └── CitizenSubmissionPage
        ├── HeroSection
        ├── ChannelSelector
        │   └── ChannelTab (×3: Text, Voice, Photo)
        ├── TextInputForm (conditional)
        │   └── TextAreaInput
        ├── VoiceInputForm (conditional)
        │   ├── VoiceFAB
        │   ├── RecordingIndicator
        │   └── AudioWaveform
        ├── PhotoInputForm (conditional)
        │   ├── FileUploadBox
        │   └── ImagePreview
        ├── SubmitButton
        ├── SubmissionProgressIndicator (conditional)
        └── ResultPanel (conditional)
            ├── SuccessIcon
            ├── SubmissionIdDisplay
            └── RecommendationCard
```

---

## 8. Shared Component Inventory

### 8.1 CategoryBadge

Renders a pill-shaped badge with icon and label for each issue category.

| Category | Icon (Material Symbols) | Background | Text Color |
|---|---|---|---|
| Education | `school` | `#dbeafe` | `#1d4ed8` |
| Healthcare | `local_hospital` | `#dcfce7` | `#166534` |
| Roads | `directions_car` | `#fef9c3` | `#854d0e` |
| Water | `water_drop` | `#cffafe` | `#155e75` |
| Sanitation | `recycling` | `#f3e8ff` | `#6b21a8` |
| Electricity | `bolt` | `#fef3c7` | `#92400e` |
| Vocational | `work` | `#ffe4e6` | `#9f1239` |
| Other | `info` | `#f1f5f9` | `#475569` |

Props: `category: string`

### 8.2 PriorityScoreBar

Thin (4px) horizontal progress bar showing `priority_score / 100`.

Color gradient:
- 0–39: `#ba1a1a` (error red)
- 40–69: `#455f87` (royal blue)
- 70–100: `#FF9933` (saffron / high priority)

Props: `score: number` (0–100)

### 8.3 PriorityBadge

Pill badge, `label-sm` typography (12px, 600 weight, uppercase).

| Level | Score Range | Background | Text |
|---|---|---|---|
| HIGH | 70–100 | `#ffdea9` | `#5e4100` |
| MEDIUM | 40–69 | `#b5d0fd` | `#001c3b` |
| LOW | 0–39 | `#e0e3e6` | `#43474b` |

Props: `score: number`

### 8.4 LoadingSpinner

Circular spinner, `#455f87` stroke color. Sizes: `sm` (16px), `md` (32px), `lg` (48px).

### 8.5 SkeletonLoader

Pulsing grey rectangle placeholder. Takes `width` and `height` props. Used during API loading states.

### 8.6 ErrorBanner

Full-width banner, `#ffdad6` background, `#ba1a1a` border-left 4px.  
Contains: error icon, message text, optional retry button.

Props: `message: string`, `onRetry?: () => void`

### 8.7 EvidencePanel

Right-side slide-in panel (320px wide, full viewport height).  
Used on Overview, Issues, and Heatmap drill-down.

Props: `project: ProjectCard | null`, `onClose: () => void`

Internal state: `explainLoading`, `explanation: Explanation | null`, `explainError: string | null`

On "View Detailed Analysis" click: calls `GET /api/explain/{project_id}`.

### 8.8 ProjectRow

Single row representing a project/recommendation. Used in multiple lists and tables.

Props: `project: ProjectCard`, `onClick: (id: string) => void`, `showIndex?: boolean`

### 8.9 RecommendationCard

Standalone card for displaying a single recommendation result. Used in citizen result panel.

Props: `recommendation: Recommendation`

### 8.10 VoiceFAB

Circular Saffron button with microphone icon and pulse animation.

States: `idle`, `recording`, `recorded`

Props: `onRecordingComplete: (audioBlob: Blob) => void`

### 8.11 StatusBadge (from implementation checklist)

Generic status indicator. Values: `processing`, `complete`, `failed`, `pending`

| Status | Background | Text |
|---|---|---|
| processing | `#b5d0fd` | `#001c3b` |
| complete | `#dcfce7` | `#166534` |
| failed | `#ffdad6` | `#93000a` |
| pending | `#e0e3e6` | `#43474b` |

---

## 9. Backend API Integration Map

**Base URL (development):** `http://localhost:8000`  
**CORS:** Backend is currently configured for `http://localhost:5173` — **must be updated to `http://localhost:3000` before frontend can communicate with backend.** See `backend/app/main.py`, line with `allow_origins`.

All endpoints are REST/JSON unless noted as multipart.

| Endpoint | Method | Used By | Content-Type | Auth |
|---|---|---|---|---|
| `/api/submissions` | POST | Citizen Submission Portal | multipart/form-data | None |
| `/api/submissions/video` | POST | Citizen Submission Portal (video) | multipart/form-data | None |
| `/api/dashboard` | GET | All MP Dashboard pages | application/json | None |
| `/api/dashboard-refresh` | POST | (not used in v1 UI — broken) | application/json | None |
| `/api/explain/{project_id}` | GET | Evidence Panel | application/json | None |
| `/api/trace/{submission_id}` | GET | (debug only — not in UI) | application/json | None |
| `/api/trace` | GET | (debug only — not in UI) | application/json | None |

### 9.1 Known Backend Issues

**CORS Mismatch (Must Fix Before Frontend Build):**  
`backend/app/main.py` — `allow_origins=["http://localhost:5173"]`  
Change to: `allow_origins=["http://localhost:3000"]`

**Bug A — explain.py MessagesState mismatch:**  
`GET /api/explain/{project_id}` may return 500 errors due to incorrect invocation of the explainability agent. The frontend Evidence Panel must handle 500 from this endpoint gracefully with "Analysis temporarily unavailable."

**Dashboard-Refresh no-op:**  
`POST /api/dashboard-refresh` has a `pass` loop and does nothing. Do not call this from the frontend.

**Heatmap always empty:**  
`GET /api/dashboard` always returns `heatmap: []`. The HeatmapPage must handle this with an empty-state banner.

---

## 10. Request/Response Mapping per Page

### 10.1 `GET /api/dashboard`

**Called by:** DashboardOverviewPage, HeatmapPage, CitizenIssuesPage

**Response schema:**
```
DashboardData:
  projects: List[ProjectCard]
  heatmap: List[HeatmapPoint]   ← always [] in v1
  total_submissions: int
  last_updated: str             ← ISO 8601 datetime string

ProjectCard:
  id: str
  title: str
  category: str                 ← one of 8 Category literals
  priority_score: float         ← 0–100
  breakdown: ScoreBreakdown
    citizen_demand: float       ← 0–40
    severity: float             ← 0–30
    population_impact: float    ← 0–20
    cost_feasibility: float     ← 0–10
  is_existing_plan_project: bool
```

**Frontend derivations from this response:**
- `Active Projects` stat = `projects.length`
- `High Priority` stat = count where `priority_score >= 70`
- Category chart data = group by `category`, average `priority_score`
- Urgency feed = filter where `priority_score >= 80`
- Issues table = full `projects` array (paginated, filtered)

### 10.2 `POST /api/submissions`

**Called by:** CitizenSubmissionPage (Text and Voice and Photo channels)

**Request (multipart/form-data):**
```
channel: "text" | "voice" | "photo" | "image"
text: string (optional, for text channel)
photo: File (optional, for photo channel, image/*)
audio: File (optional, for voice channel, audio/*)
```

**Response:**
```
status: "received"
submission_id: str
photo_url: str | null     ← relative path under /uploads/
audio_url: str | null     ← relative path under /uploads/
recommendation: Recommendation | null   ← may be null if pipeline not yet complete
```

**Recommendation object (if present):**
```
project_id: str
title: str
priority_score: float    ← 0–100
breakdown: ScoreBreakdown
is_existing_plan_project: bool
explanation: Explanation | null
  evidence: List[str]
  summary: str
  confidence_score: float  ← 0–1
```

### 10.3 `POST /api/submissions/video`

**Called by:** CitizenSubmissionPage (video channel — not in current Stitch design)

**Request (multipart/form-data):**
```
video: File (max 50MB, .mp4/.mov/.avi/.mkv/.webm)
```

**Response:** same as `/api/submissions`

### 10.4 `GET /api/explain/{project_id}`

**Called by:** EvidencePanel (on "View Detailed Analysis" click)

**Path param:** `project_id: str` — from `ProjectCard.id`

**Response (success):**
```
project_id: str
explanation:
  evidence: List[str]
  summary: str
  confidence_score: float
```

**Response (500 — Bug A):** Raw FastAPI error. Frontend must catch and display fallback message.

### 10.5 `GET /api/trace/{submission_id}` and `GET /api/trace`

For developer/debug use only. Not shown in any UI in v1.

---

## 11. TypeScript Type Reference

These types should be defined in `frontend/types/api.ts`. Derived directly from `backend/app/schemas/models.py` and `backend/app/schemas/dashboard.py`.

```typescript
// frontend/types/api.ts

export type Category =
  | "Education"
  | "Healthcare"
  | "Roads"
  | "Water"
  | "Sanitation"
  | "Electricity"
  | "Vocational"
  | "Other";

export type InputType = "text" | "voice" | "image" | "video" | "dashboard_refresh";

export interface ScoreBreakdown {
  citizen_demand: number;   // 0–40
  severity: number;         // 0–30
  population_impact: number; // 0–20
  cost_feasibility: number; // 0–10
}

export interface Explanation {
  evidence: string[];
  summary: string;
  confidence_score: number; // 0–1
}

export interface Recommendation {
  project_id: string;
  title: string;
  priority_score: number;   // 0–100
  breakdown: ScoreBreakdown;
  is_existing_plan_project: boolean;
  explanation: Explanation | null;
}

export interface ProjectCard {
  id: string;
  title: string;
  category: Category;
  priority_score: number;   // 0–100
  breakdown: ScoreBreakdown;
  is_existing_plan_project: boolean;
}

export interface HeatmapPoint {
  // Structure TBD — always empty in v1. Confirm with backend team.
  lat: number;
  lng: number;
  intensity: number;
  category?: Category;
}

export interface DashboardData {
  projects: ProjectCard[];
  heatmap: HeatmapPoint[];
  total_submissions: number;
  last_updated: string;     // ISO 8601
}

export interface SubmissionResponse {
  status: "received";
  submission_id: string;
  photo_url: string | null;
  audio_url: string | null;
  recommendation: Recommendation | null;
}

export interface ExplainResponse {
  project_id: string;
  explanation: Explanation;
}
```

---

## 12. State Management

No global state library is required for v1. Use React's built-in `useState` + `useEffect` + `useCallback` + server-component data fetching (Next.js App Router).

### 12.1 Dashboard State (shared across `/dashboard/**`)

The dashboard data (`DashboardData`) is fetched once per navigation to any `/dashboard` route. Use a React Context (`DashboardContext`) or Next.js server component to share it across:
- `/dashboard` (Overview)
- `/dashboard/heatmap`
- `/dashboard/issues`

This avoids triple-fetching the same API on tab navigation.

**Recommended:** Create `app/dashboard/layout.tsx` that fetches `GET /api/dashboard` once on server-render (or client via `SWR`/`useEffect`) and passes data down via context.

### 12.2 Evidence Panel State

Local to each page that uses `EvidencePanel`:
- `selectedProject: ProjectCard | null`
- `isPanelOpen: boolean`
- `explanation: Explanation | null`
- `explainLoading: boolean`
- `explainError: string | null`

### 12.3 Citizen Submission State

Local to `CitizenSubmissionPage`:
- `activeChannel: "text" | "voice" | "photo"`
- `textInput: string`
- `audioBlob: Blob | null`
- `photoFile: File | null`
- `isSubmitting: boolean`
- `submissionId: string | null`
- `pollingActive: boolean`
- `pollingCount: number`
- `result: Recommendation | null`
- `error: string | null`

### 12.4 Issues Table State

Local to `CitizenIssuesPage`:
- `searchQuery: string`
- `activeCategory: Category | "All"`
- `currentPage: number`
- `sortColumn: keyof ProjectCard | null`
- `sortDirection: "asc" | "desc"`

---

## 13. Folder Mapping

Aligned with Next.js App Router conventions. All frontend code lives in `frontend/`.

```
frontend/
├── app/
│   ├── layout.tsx               ← Root layout: Inter font, html/body
│   ├── globals.css              ← Tailwind base + Sovereign Modernism custom props
│   ├── page.tsx                 ← Redirect to /dashboard
│   ├── dashboard/
│   │   ├── layout.tsx           ← MPLayout: Sidebar + TopBar + main
│   │   ├── page.tsx             ← DashboardOverviewPage
│   │   ├── heatmap/
│   │   │   └── page.tsx         ← HeatmapPage
│   │   └── issues/
│   │       └── page.tsx         ← CitizenIssuesPage
│   └── submit/
│       └── page.tsx             ← CitizenSubmissionPage
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── SidebarNavItem.tsx
│   │   ├── TopBar.tsx
│   │   ├── MPLayout.tsx
│   │   ├── CitizenLayout.tsx
│   │   └── MobileBottomNav.tsx
│   │
│   ├── shared/
│   │   ├── CategoryBadge.tsx
│   │   ├── PriorityScoreBar.tsx
│   │   ├── PriorityBadge.tsx
│   │   ├── StatusBadge.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── SkeletonLoader.tsx
│   │   ├── ErrorBanner.tsx
│   │   ├── ProjectRow.tsx
│   │   └── RecommendationCard.tsx
│   │
│   ├── dashboard/
│   │   ├── StatCard.tsx
│   │   ├── AISummaryCard.tsx
│   │   ├── QuickNavCard.tsx
│   │   ├── TopRecommendationsList.tsx
│   │   ├── UrgentIssuesFeed.tsx
│   │   ├── PriorityBarChart.tsx
│   │   └── EvidencePanel.tsx
│   │
│   ├── heatmap/
│   │   ├── FilterSidebar.tsx
│   │   ├── MapCanvas.tsx
│   │   ├── HeatmapOverlay.tsx
│   │   ├── EmptyHeatmapBanner.tsx
│   │   ├── MapControls.tsx
│   │   └── DrillDownPanel.tsx
│   │
│   ├── issues/
│   │   ├── AIPredictionBanner.tsx
│   │   ├── SearchBar.tsx
│   │   ├── CategoryFilterChips.tsx
│   │   ├── StatusCheckboxes.tsx
│   │   ├── IssuesTable.tsx
│   │   └── PaginationControls.tsx
│   │
│   └── submit/
│       ├── ChannelSelector.tsx
│       ├── TextInputForm.tsx
│       ├── VoiceInputForm.tsx
│       ├── VoiceFAB.tsx
│       ├── PhotoInputForm.tsx
│       ├── SubmitButton.tsx
│       ├── SubmissionProgressIndicator.tsx
│       └── ResultPanel.tsx
│
├── hooks/
│   ├── useDashboard.ts          ← Fetches GET /api/dashboard, returns data + loading + error
│   ├── useExplain.ts            ← Fetches GET /api/explain/{id} on demand
│   ├── useSubmission.ts         ← Handles POST /api/submissions + polling
│   └── useEvidencePanel.ts      ← Panel open/close + explain state
│
├── lib/
│   ├── api.ts                   ← Axios instance with base URL, error handling
│   ├── constants.ts             ← POLLING_INTERVAL, MAX_POLLS, BASE_URL
│   └── utils.ts                 ← getPriorityLevel(), getCategoryColor(), formatScore()
│
├── types/
│   └── api.ts                   ← All TypeScript interfaces (see §11)
│
└── public/
    ├── emblem-white.svg         ← National Emblem (monochrome white for sidebar)
    └── emblem-navy.svg          ← National Emblem (deep navy for light backgrounds)
```

---

## 14. Reusable Component Recommendations

### 14.1 EvidencePanel — used in 3 pages

The same `EvidencePanel` is needed on `/dashboard`, `/dashboard/heatmap` (drill-down), and `/dashboard/issues`. Build it once in `components/dashboard/EvidencePanel.tsx` and import it in all three page components. Do not duplicate the explain-call logic.

### 14.2 ProjectRow — used in 2+ lists

`TopRecommendationsList` and `IssuesTable` both render per-project rows with the same fields. Extract a single `ProjectRow` component with optional `showIndex` and `showStatus` props.

### 14.3 CategoryBadge + PriorityBadge — used everywhere

These two badge components are referenced in 3 pages, 2 list components, 1 table, and 1 result panel. Keep them in `components/shared/` and never inline the badge logic.

### 14.4 useDashboard hook — shared state

All three MP dashboard pages fetch the same `GET /api/dashboard`. Centralize this in a single `useDashboard` hook (or React Context in `dashboard/layout.tsx`) to avoid three separate requests firing on tab navigation.

### 14.5 API client (`lib/api.ts`)

Centralize all `axios` calls here. This is where the base URL, default headers, and error interceptors live. No component should call `axios` directly.

---

## 15. Redundancy Analysis

| Redundancy | Location | Recommendation |
|---|---|---|
| Priority level calculation (High/Medium/Low) | Used in PriorityBadge, PriorityScoreBar, IssuesTable | Extract to `lib/utils.ts: getPriorityLevel(score)` |
| Category icon/color mapping | CategoryBadge, bar chart colors, filter chips | Extract to `lib/constants.ts: CATEGORY_CONFIG` |
| EvidencePanel code | Would be duplicated across 3 pages if not extracted | Single shared component (see §14.1) |
| Skeleton loader shapes | Multiple pages show loading skeletons | Single `SkeletonLoader` with `width`/`height` props |
| `GET /api/dashboard` fetch | Would fire 3× without shared state | Single `useDashboard` hook or context |

---

## 16. Known Issues and Ambiguities

This section documents every gap found between the design (Stitch), the backend implementation, and the product spec. Each item must be resolved before the feature is built.

### CRITICAL — Must Fix Before Frontend Development

**C1. CORS Mismatch**  
Backend `main.py` allows only `http://localhost:5173`. Next.js runs on `http://localhost:3000`. Every API call will fail with CORS error until this is fixed.  
Fix: Change `allow_origins` in `backend/app/main.py` from `["http://localhost:5173"]` to `["http://localhost:3000"]`.  
Status: **Not fixed.**

**C2. Missing npm dependencies**  
`frontend/package.json` is missing required packages:
- `axios` — HTTP client
- `recharts` — bar chart (PriorityBarChart)
- `leaflet` — map library
- `@types/leaflet` — Leaflet TypeScript types
- `react-leaflet` — React wrapper for Leaflet  
These must be installed (`npm install axios recharts leaflet @types/leaflet react-leaflet`) before frontend build begins.

### HIGH — Impacts Feature Delivery

**H1. Heatmap always empty**  
`GET /api/dashboard` returns `heatmap: []` always. The `HeatmapPage` cannot display real heat data in v1. The page must include a visible "Data not yet available" banner and not crash.

**H2. Bug A — explain endpoint unreliable**  
`GET /api/explain/{project_id}` may return 500 due to MessagesState mismatch in `backend/app/api/explain.py`. The `EvidencePanel` must gracefully handle 500s with a user-friendly message. Do not surface raw error details.

**H3. No citizen submission status endpoint**  
There is no `GET /api/submissions/{submission_id}` endpoint for polling submission status. The citizen portal cannot poll individual submission status. Workaround: poll `GET /api/dashboard` and check if a new project_id has appeared. This is fragile. Backend team should add a `/api/submissions/{submission_id}/status` endpoint.

**H4. Status field missing from backend schema**  
The Stitch citizen issues table shows "Not Started / In Progress / Completed" status per project. No such field exists in `ProjectCard`, `Recommendation`, or any backend schema. The `StatusCheckboxes` filter component must be disabled/greyed out in v1.

### MEDIUM — Requires Product Owner Decision

**M1. AI Summary Card (Dashboard Overview)**  
The Stitch design shows an AI-generated constituency summary card. No backend endpoint provides this. Decision needed: (a) omit the card, (b) use static placeholder, or (c) derive from top-3 recommendation titles client-side.

**M2. Trend indicators on Stat Cards**  
Up/down arrows with percentage change appear on stat cards. No historical data is returned by the backend. Decision needed: omit or show as static UI.

**M3. Urgency threshold**  
The "Urgent Issues Feed" needs a threshold to filter high-priority projects. Recommend `priority_score >= 80` but must be confirmed.

**M4. Date filter on Heatmap**  
The Stitch heatmap filter sidebar shows a date range picker. `GET /api/dashboard` has no date filter parameter. The filter would be client-side only (on `last_updated` string). Decision needed: implement client-side date filter or omit.

**M5. HeatmapPoint schema**  
The `HeatmapPoint` type in `backend/app/schemas/dashboard.py` must be read and documented before the Leaflet integration is built. The document currently notes this as TBD.

### LOW — Design Gaps

**L1. No Stitch design for Citizen Submission Portal**  
The `/submit` page has no Stitch reference. All design decisions for this page are inferred from DESIGN.md and the backend schema. The product owner should review the proposed layout before implementation.

**L2. Video submission channel**  
The backend has `POST /api/submissions/video` for video submissions. The Stitch design shows only Text/Voice/Photo. Decision needed: add a Video tab to the channel selector or omit in v1.

**L3. "Export Report" button**  
The Stitch Quick Nav card includes an "Export Report" button. No backend endpoint supports export. Build as a disabled/placeholder button in v1.

**L4. National Emblem assets**  
The sidebar requires the National Emblem SVG in monochrome white. This asset is not in the repository. Source from official Government of India guidelines before use.

---

## 17. Future Extensibility

### 17.1 Authentication

The v1 has no auth. When added:
- MP login will be before `/dashboard` (redirect from `/`)
- Citizen login/phone OTP will be optional on `/submit`
- Add a `middleware.ts` in `frontend/` for route protection
- The sidebar should conditionally show MP name/avatar from auth context

### 17.2 Real-time Updates

The current backend is fully synchronous. When real-time is needed:
- Replace polling on `/submit` with a WebSocket or Server-Sent Events endpoint (`/api/submissions/{id}/stream`)
- Replace polling on `/dashboard` with a WebSocket for live project updates

### 17.3 Multilingual Support

The product description implies Hindi/English bilingual support. Structure text strings in `lib/i18n.ts` from the start, even if only English is implemented initially. This avoids a costly refactor later.

### 17.4 Heatmap Data

When the backend populates `heatmap: [...]`:
- The `MapCanvas` and `HeatmapOverlay` components are already structured to receive data
- Only the `EmptyHeatmapBanner` needs to be hidden
- No page-level restructure required

### 17.5 MP Analytics Page

The Stitch sidebar shows an "Analytics" nav item (bar_chart icon). No screen design exists. When built, it will be a new route `app/dashboard/analytics/page.tsx` inside the existing `MPLayout`.

### 17.6 Citizen Issue Status Tracking

When the backend adds a `status` field to `ProjectCard`:
- `StatusCheckboxes` component (currently disabled) can be enabled
- `IssuesTable` status column becomes live
- Progress bars in DESIGN.md (Success Green = completed, Saffron = in progress) apply automatically

---

## 18. Developer Handoff

### 18.1 Setup Checklist

Before writing any frontend code:

- [ ] Fix CORS in `backend/app/main.py`: change port 5173 → 3000
- [ ] Run `npm install axios recharts leaflet @types/leaflet react-leaflet` in `frontend/`
- [ ] Verify backend is running on `http://localhost:8000`
- [ ] Verify `GET http://localhost:8000/api/dashboard` returns valid JSON
- [ ] Test `POST http://localhost:8000/api/submissions` with a multipart text submission
- [ ] Source or create National Emblem SVG assets

### 18.2 Development Sequence (Recommended)

1. **Globals first:** `globals.css` (CSS custom properties for design tokens), `layout.tsx` (Inter font)
2. **Types:** `frontend/types/api.ts` — define all TypeScript types from §11
3. **API client:** `frontend/lib/api.ts` — axios instance
4. **Shared components:** CategoryBadge, PriorityBadge, PriorityScoreBar, LoadingSpinner, SkeletonLoader, ErrorBanner
5. **Layout:** Sidebar, TopBar, MPLayout, CitizenLayout
6. **Dashboard Overview:** `useDashboard` hook → StatCards → TopRecommendationsList → EvidencePanel → PriorityBarChart
7. **Citizen Issues:** IssuesTable → SearchBar → CategoryFilterChips → Pagination
8. **Heatmap:** MapCanvas (empty state) → FilterSidebar → DrillDownPanel
9. **Citizen Portal:** ChannelSelector → TextInputForm → VoiceInputForm → PhotoInputForm → Polling → ResultPanel

### 18.3 Backend Coordination Required

The following items require backend changes or confirmation before frontend implementation can be completed:

| Item | Needed For | Status |
|---|---|---|
| Change CORS port 5173 → 3000 | All API calls | Not done |
| Add `GET /api/submissions/{id}/status` endpoint | Citizen polling | Not done |
| Confirm `HeatmapPoint` schema fields | Heatmap integration | TBD |
| Fix Bug A in explain.py | Reliable EvidencePanel | Not done |
| Add `status` field to ProjectCard | Issues table status filter | Not done — product decision needed |
| Confirm AI Summary endpoint or decision | AI Summary Card | TBD |

### 18.4 Design Assets Needed

| Asset | Usage | Status |
|---|---|---|
| National Emblem SVG (white) | Sidebar header | Not in repo |
| National Emblem SVG (navy) | Citizen portal header | Not in repo |
| MeriAwaaz AI wordmark/logo | Sidebar, mobile top bar | Not in repo |

### 18.5 Testing Approach

- **Unit tests:** Shared components (CategoryBadge, PriorityBadge, PriorityScoreBar) — test all input ranges and edge cases
- **Integration tests:** `useDashboard` hook with mocked API responses — test loading, empty, error, and success states
- **E2E tests:** Citizen submission flow (text channel) — submit → polling → result display
- **Manual testing:** Heatmap empty state, Evidence Panel 500 error handling, mobile layout on 375px viewport

### 18.6 Environment Variables

```
# frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_POLLING_INTERVAL_MS=5000
NEXT_PUBLIC_MAX_POLLING_ATTEMPTS=24
```

### 18.7 Known Seed Data (for development testing)

The backend pre-loads 8 plan projects at startup from `backend/app/data/local_plans.json`:

| ID | Category | Location |
|---|---|---|
| plan_001 | Education | Rampur |
| plan_002 | Healthcare | Kesarpur |
| plan_003 | Roads | Sultanpur |
| plan_004 | Water | Bhelupur |
| plan_005 | Sanitation | Rampur |
| plan_006 | Electricity | Kesarpur |
| plan_007 | Vocational | Sultanpur |
| plan_008 | Other | Bhelupur |

`GET /api/dashboard` will return these 8 projects on a fresh backend start. Use them for dashboard UI testing before any citizen submissions are made.

---

*End of FRONTEND_ARCHITECTURE.md*  
*Generated from: full backend codebase analysis + Google Stitch export (3 screens + DESIGN.md) + docs/API_CONTRACTS.md + docs/IMPLEMENTATION_CHECKLIST.md + docs/PROJECT_SPECIFICATION_V1.0.md*
