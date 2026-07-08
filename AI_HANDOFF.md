# MeriAwaaz AI — Complete Project Handoff

> **Read this one file to understand the whole system.** It is written for an AI
> model (or engineer) taking over the project cold. It describes what the project
> is, every backend module and endpoint, the full frontend, the AI pipeline, the
> data model, how to run it, and where the sharp edges are. Companion docs:
> `ARCHITECTURE.md` (deep agent tables), `RUN.md` (quick run), `BUGFIX_LOG.md`
> (fix history). Where they disagree with this file, **this file wins.**
>
> Last updated: 2026-07-08.

---

## 1. What the project is

**MeriAwaaz AI** ("My Voice AI") is a **constituency development decision-support
platform for an Indian Member of Parliament (MP)**. It has two sides:

- **Citizen side** — citizens submit civic complaints (text, voice, photo, or
  video, in any Indian language), optionally pinning the exact location on a map.
- **MP side** — an AI pipeline turns each submission into a **ranked development
  project**. The MP sees a dashboard of scored projects, a searchable/actionable
  list of citizen issues, and an interactive **heatmap** of the constituency.

It began as a hackathon project (Nagpur, Maharashtra constituency). The backend
(FastAPI + LangGraph) is complete; the frontend (Next.js) is fully wired to it.

**The central design rule — never violate it:**
> **LLMs contribute only language. Python computes every number.**
Scores, rankings, cluster sizes, infrastructure gaps and populations are all
deterministic Python. The LLM only transcribes speech, describes images, parses
complaints, splits multi-topic messages, names clusters, and writes titles /
explanations. This makes results reproducible and auditable, and lets the system
**degrade gracefully**: if the LLM is unavailable, every stage falls back to
pure-Python logic and the pipeline still returns a valid answer (never a 500).

---

## 2. Technology stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Agent framework | LangGraph `StateGraph` + `create_react_agent` |
| LLM (agents) | Configurable via `LLM_PROVIDER`; **currently OpenAI `gpt-5.5`**. Also supports `gemini`, `claude`. |
| LLM (media + embeddings) | Google Gemini directly (voice/video transcription via File API; ChromaDB embeddings) |
| Vector DB | ChromaDB (HNSW, cosine) |
| Structured storage | SQLite (raw `sqlite3`, no ORM) |
| In-memory read layer | `STORE` singleton (Python dicts) |
| Frontend | Next.js 16 (App Router) + React 19 + TypeScript + Tailwind 4 + zustand + MUI/lucide |
| Maps | Leaflet 1.9.4 + OpenStreetMap tiles + Nominatim geocoder — all free, loaded from CDN, **no API key** |

> **Doc-drift warning:** `ARCHITECTURE.md` says "Gemini 2.0 Flash" — that is
> outdated. Agents run on **OpenAI** (`backend/.env`: `LLM_PROVIDER=openai`,
> `OPENAI_MODEL=gpt-5.5`). Gemini is only used for embeddings + voice/video.

---

## 3. Repository layout

```
MeriAwaaz-AI/
├── AI_HANDOFF.md              ← THIS FILE (master transfer doc)
├── CONTEXT.md                 ← earlier handoff (session-layered)
├── ARCHITECTURE.md            ← deep agent tables (LLM provider is stale)
├── BUGFIX_LOG.md              ← every bug fixed, with root cause
├── RUN.md                     ← quick run steps
├── MERI_AWAAZ_CONTEXT.md      ← original handoff (partly stale)
├── PROJECT_ANALYSIS.md        ← original team/branch notes
├── docs/                      ← spec, API contracts, checklist
├── datasets/demo/             ← raw source government CSVs
├── scripts/prepare_nfhs5_healthcare.py
├── prompts/                   ← EMPTY stub .md files (NOT used at runtime)
├── backend/
│   ├── .env                   ← provider + keys + paths
│   ├── requirements.txt
│   └── app/
│       ├── main.py            ← FastAPI app, routers, startup, /heatmap page
│       ├── config.py          ← CONSTITUENCY, CATEGORY_CONFIG, cost anchors
│       ├── supervisor.py      ← LangGraph graph + node wrappers + fallbacks
│       ├── core/llm.py        ← get_model() provider factory + content_to_text()
│       ├── schemas/           ← models.py (all Pydantic), dashboard.py, settings.py
│       ├── agents/            ← 5 ReAct agents + speech_processing + vision_processing
│       ├── tools/             ← citizen/demand/knowledge/policy/explainability tools
│       ├── services/          ← database, chroma_client, store, need_scoring, trace, decompose
│       ├── api/               ← health, submissions, video, dashboard, recommendations, explain, trace, heatmap
│       ├── static/heatmap.html← the interactive Leaflet heatmap page (served at /heatmap)
│       └── data/              ← local_plans.json, *_need.json, priors, village_coordinates.json, uploads/
└── frontend/
    ├── package.json           ← next dev (port 3000)
    ├── app/                   ← App Router pages (see §7)
    ├── components/            ← UI components (see §7)
    ├── services/api.ts        ← typed backend client
    ├── types/api.ts           ← response types
    ├── store/issueStore.ts    ← citizen submission state (zustand)
    └── public/images/logo.svg ← brand mark (fist / speech bubble)
```

---

## 4. Backend — the AI pipeline

### 4.1 Shared state
`backend/app/schemas/models.py` defines Pydantic models. The pipeline threads a
single `AgentState`:

```
AgentState:
  submission_id, input_type ∈ {text,voice,image,video,dashboard_refresh},
  raw_text, media_file_path, audio_url,
  parsed_issue: ParsedIssue?      (category, location, summary, confidence, language)
  cluster: ClusterResult?         (cluster_id, cluster_name, cluster_size, center_location)
  knowledge_context: FusedContext?(category, location, demand_count, population_affected,
                                    estimated_cost_inr, data_confidence, severity_score,
                                    category_specific_data, is_existing_plan_project)
  recommendation: Recommendation? (project_id, title, priority_score, breakdown,
                                    is_existing_plan_project, reason, explanation)
  error
```

`Recommendation.breakdown` is `ScoreBreakdown{citizen_demand 0-40, severity 0-30,
population_impact 0-20, cost_feasibility 0-10}`. `Recommendation.explanation` is
`Explanation{evidence[], summary, confidence_score}`.

### 4.2 Graph (`supervisor.py`)
```
route_intake  ──voice──►  speech_processing ─┐
              ──image───► vision_processing ─┤ (media → raw_text)
              ──video───► vision_processing ─┤
              ──text────────────────────────┘
                     ▼
  citizen_intelligence  → parsed_issue
                     ▼
  demand_intelligence   → cluster           (ChromaDB search + LLM clustering)
                     ▼
  knowledge_fusion      → knowledge_context (govt JSON, deterministic-first)
                     ▼
  policy_recommendation → recommendation     (pure-Python relative scoring; LLM writes title+reason)
                     ▼
  explainability        → recommendation.explanation
```
Each node is a plain Python wrapper that: reads `AgentState`, builds a
`{"messages":[HumanMessage(...)]}` for the `create_react_agent` sub-agent, calls
`.invoke()`, parses the final message (`_strip_json`), and returns `AgentState`
field updates. Every node is wrapped with `traced("name")` (logs + `agent_log`
table). Every node checks `_llm_unavailable(state)` first — once any node records
a quota/429/503/"api key" error, downstream nodes skip the LLM and use
deterministic fallbacks. Safe numeric coercion helpers `_as_int`/`_as_float`
tolerate LLM values like `"1,450"` or `"unknown"`.

### 4.3 Multi-topic fan-out (important)
A single message can raise several problems (e.g. *"Kesarpur has road potholes AND
its health centre has a medicine shortage"*). This is handled **at the API layer**,
not inside the graph:
1. `services/decompose.py::decompose_text(text)` asks the LLM to split the message
   into a list of self-contained single-topic complaints (falls back to `[text]`
   if the LLM is unavailable).
2. For media, the API first runs the preprocessing node function
   (`speech_processing.run` / `vision_processing.run`) directly to get `raw_text`,
   then decomposes it.
3. For each topic, the API invokes the compiled pipeline once as `input_type="text"`.
   Each topic therefore updates or creates its **own** cluster / project.
4. Row ids: first topic = `{sid}`, extra topics = `{sid}#1`, `{sid}#2`, … Each is
   indexed separately in ChromaDB so future submissions cluster per-topic.

### 4.4 Scoring (deterministic — `tools/policy_tools.py::compute_relative_breakdown`)
```
citizen_demand    = 40 × min(demand_count / max_demand_in_store, 1)     (denominator floored at 5)
severity          = 30 × severity_score            (0–1 from Knowledge Fusion, incl. complaint boost)
population_impact = 20 × min(population / max_pop_in_store, 1)
cost_feasibility  = 10 × (1 − min(1, cost / (2 × ₹50L)))   [5.0 if cost unknown]
priority_score    = sum of the four (0–100)
```
Normalising against the strongest competitor (not a fixed cap) makes rankings
move as complaints cluster. `severity_score` = infrastructure gap (percentile-rank
normalised from govt datasets) + `apply_complaint_boost` (up to +0.15 for demand).

### 4.5 Agents & tools
- **Citizen Intelligence** (`agents/citizen_intelligence_agent.py`, tools
  `citizen_tools.py`): parse category/location/summary/confidence/language.
- **Demand Intelligence** (`demand_tools.py`): `search_similar_submissions`
  (ChromaDB, filtered by category) + `cluster_submissions` (LLM decides new vs
  existing cluster; updates `STORE.clusters`). `cluster_size` drives demand.
- **Knowledge Fusion** (`knowledge_tools.py`): `lookup_infrastructure` reads
  govt JSON → authoritative `infrastructure_gap` + `data_confidence`;
  `lookup_plan_projects` matches an existing plan (demand then *validates* the
  plan instead of duplicating it).
- **Policy Recommendation** (`policy_tools.py`): pure-Python score; LLM writes
  only `title` + `reason`. Project identity: plan match → `plan_id`; else one
  project **per cluster** (`proj_{cluster_id}`), never per submission.
- **Explainability** (`explainability_tools.py`): pure-Python evidence bullets +
  confidence; LLM writes a 2–3 sentence MP-facing summary.
- **Media**: `speech_processing.py` (Gemini File API transcription, ≤20 MB
  inline else File API, 50 MB cap) and `vision_processing.py` (image = inline
  base64 to the configured model; video = Gemini analyses visual + audio). Both
  preserve the citizen's typed caption.

### 4.6 Storage
- **SQLite** (`services/database.py`, file `backend/app/data/meri_awaaz.db`).
  Tables: `submissions`, `clusters`, `recommendations`, `agent_log`. `init_db()`
  creates them and runs idempotent `ALTER TABLE` migrations. The `submissions`
  table has been migrated to include `photo_url, video_url, audio_url, lat, lng,
  resolved`.
- **`STORE`** (`services/store.py`): in-RAM dicts of `FusedContext` and
  `Recommendation` keyed by `project_id`, plus `clusters`. Dashboard/heatmap read
  STORE for instant responses. Seeded at startup with **8 plan projects** from
  `local_plans.json` (villages Rampur, Kesarpur, Sultanpur, Bhelupur).
- **ChromaDB** (`services/chroma_client.py`): vector index of submission text.
  Sentinel-document pattern rebuilds the collection only when the embedding model
  name changes (not every restart). Queries filtered by `category`.

### 4.7 Resolve model (drives what shows on the dashboard/map)
- `submissions.resolved` column (0/1). `POST /api/submissions/resolve {ids:[…]}`
  marks submissions resolved.
- `database.resolved_cluster_ids()` returns cluster_ids (= project_ids) whose
  **every** feeding submission is resolved (projects with zero feeding
  submissions — e.g. seed plans — are never included).
- `GET /api/dashboard`, `GET /api/recommendations`, and `GET /api/heatmap`
  **exclude** those project_ids. So when all complaints of a cluster are
  resolved, the project disappears from the dashboard, the recommendations, and
  the map, and the project count drops.

### 4.8 Data files (`backend/app/data/`)
- `local_plans.json` — 8 seed plan projects (one per category, Nagpur villages).
- `healthcare_need.json` (district: OPD load + medicine shortage, blended),
  `education_need.json` (state: UDISE school-size %), `digital_connectivity_need.json`
  (state: rural teledensity, category "Other").
- `synthetic_category_priors.json` — labelled-synthetic gaps for categories with
  no real dataset (Roads/Water/Sanitation/Electricity/Vocational).
- `village_coordinates.json` — gazetteer: lowercased place → `[lat, lng]` (used
  by the heatmap endpoint).
- `uploads/` — saved photos/videos/audio, served at `/uploads/{file}`.
Normalisation is **percentile-rank** (`services/need_scoring.py`), chosen because
77% of districts share medicine-shortage 0.0 and outliers (Kerala teledensity
210) broke min-max. Constituency is hard-coded to Maharashtra/Nagpur in
`config.py::CONSTITUENCY`.

---

## 5. Backend — API reference

Base URL (dev): `http://localhost:8000`. CORS allows `localhost:3000` and
`localhost:5173` (+127.0.0.1).

| Method | Path | Purpose / notable fields |
|---|---|---|
| GET | `/health` | `{status:"ok"}` |
| POST | `/api/submissions` | multipart: `channel` (text/voice/image), `text`, `lat`, `lng`, `photo`, `audio`. Runs decomposition + pipeline. Returns `{status, submission_id, photo_url, audio_url, error, topics, recommendation, recommendations[]}`. |
| GET | `/api/submissions?limit&offset` | Recent submissions, newest first. Each item: `{id, created_at, input_type, category, location, summary, raw_text, cluster_id, priority_score, photo_url, audio_url, video_url, lat, lng, resolved}`. Plus `total`. |
| POST | `/api/submissions/resolve` | Body `{ids:[...]}`. Marks resolved → returns `{resolved:n}`. |
| GET | `/api/submissions/{id}` | Single stored submission + its recommendation. |
| POST | `/api/submissions/video` | multipart: `channel="video"`, `video`, `text`. Same fan-out. |
| GET | `/api/dashboard` | `{projects[ProjectCard], heatmap[], total_submissions, last_updated}` — **excludes resolved clusters**. |
| POST | `/api/dashboard-refresh` | Re-scores STORE with the relative scorer. |
| GET | `/api/recommendations` | `{items:[Recommendation]}` — **excludes resolved**. |
| GET | `/api/explain/{project_id}` | On-demand `Explanation`. |
| GET | `/api/trace/{id}` / `/api/trace` | Pipeline trace(s) from `agent_log`. |
| GET | `/api/heatmap` | `{towns:[{name, state, lat, lng, projects:[{id, title, category, description, explanation, submission_count, population_affected, priority_score, breakdown, is_existing_plan_project}]}]}` — one town per location; **excludes resolved clusters**. |
| GET | `/heatmap` | Serves `app/static/heatmap.html` same-origin. |
| GET | `/uploads/{file}` | Static media. |

---

## 6. The interactive heatmap (`backend/app/static/heatmap.html`)

Self-contained single HTML file (Leaflet + OSM + Nominatim, from CDN). Served at
`/heatmap`, fetches `/api/heatmap` **same-origin** (no CORS). Features:
- Whole-India map on load; "India view" / "Zoom to constituency" buttons; scroll
  + button zoom.
- **One marker per town** (all categories clustered behind it); the number in the
  dot = clustered project count.
- Marker colour ∝ **severity** (green→yellow→red), scale auto-adapts.
- Click → popup widget: page through each project (tabs + Prev/Next) showing
  summary, **submission count**, **affected population**, priority score, and the
  four breakdown bars. The widget is a real DOM element with a delegated,
  propagation-stopped click handler and in-place `innerHTML` updates, so it never
  closes while browsing (this was a hard bug — see BUGFIX_LOG #1).
- Auto-refreshes every 12 s (+ manual ↻) so new/resolved submissions appear
  without a reload. Has an embedded offline fallback dataset (the real Nagpur
  seed data) so it also works over `file://`.

The frontend MP heatmap page embeds this via an `<iframe src={API_BASE}/heatmap>`.
**Keep this file mostly as-is** (project owner's request).

---

## 7. Frontend (Next.js, `frontend/`)

Runs on `http://localhost:3000` (`npm run dev`). Path alias `@/* → ./*`. The
frontend is UI + a typed API client; all real data comes from the backend.

### 7.1 Routing / pages (`app/`)
- `/` (`app/page.tsx`) — landing; `RoleSelection` routes to `/citizen/dashboard`
  or `/mp/dashboard`.
- **Citizen**: `/citizen/dashboard` (marketing home), `/citizen/about`,
  `/citizen/new-issue` (StepOne → StepTwo; address is **required** to continue),
  `/citizen/review` (StepThree preview → **real submit**), `/citizen/success`
  (shows the AI-matched project(s) + priority from the response), `/citizen/login`
  (stub).
- **MP** (wrapped by `app/mp/layout.tsx` = Sidebar + content): `/mp/dashboard`,
  `/mp/citizen-issues`, `/mp/heatmap`, `/mp/login` (stub).

### 7.2 State (`store/issueStore.ts`, zustand)
Holds the in-progress citizen submission: `category, description, location,
locationLat, locationLng, photo, audio, submissionId, status, response` + setters
+ `reset()`.

### 7.3 API client (`services/api.ts`)
`API_BASE = NEXT_PUBLIC_API_BASE || "http://localhost:8000"`. Functions:
`getDashboard`, `getRecommendations`, `getHeatmap`, `listSubmissions`,
`explainProject`, `submitIssue` (multipart; infers channel; folds location into
text; sends lat/lng), `submitVideo`, `resolveSubmissions(ids)`. `HEATMAP_URL =
${API_BASE}/heatmap`. Types in `types/api.ts`.

### 7.4 Citizen submit flow
`StepOne` (category, description, photo, audio → store) → `StepTwo` (interactive
`LocationPicker` + required address box) → `StepThree` (review shows the store
values) → `review/page.tsx::handleSubmit` calls `submitIssue({text, category,
location, lat, lng, photo, audio})` → success page renders `response.recommendations`.

### 7.5 MP Dashboard (`app/mp/dashboard/page.tsx`)
Client component; `getDashboard()` on mount. Stat cards (total submissions,
high-priority clusters ≥40, ranked projects, top score), an AI summary derived
from the top project, quick-nav, top recommendations, a priority feed. (The old
mock "Ranked Projects by Category" chart was removed.)

### 7.6 MP Citizen Issues (`app/mp/citizen-issues/page.tsx`)
`listSubmissions(200)` → maps each `SubmissionListItem` to a `CitizenIssue`:
- **Ward canonicalisation** (`canonicalWard`): merges spelling/case/Hindi variants
  to one ward using a Hindi→English map + Levenshtein snap to known villages
  (kesarpur/kesarput/`केसरपुर` → "Kesarpur"). This is **frontend-only** (the
  heatmap still groups by raw location).
- Backend category → UI `IssueCategory`; priority band from `priority_score`.
- **Status**: `resolved` (from backend) → "Resolved"; else assigned
  (localStorage set `mp_assigned_ids`) → "Assigned"; else "Open".
- Filters (search, category, ward, status, priority, sort) all work; options for
  category/ward derived from live data; layout is a full-width search + five equal
  dropdowns (`SearchFilters.tsx`).
- **Actions**: Assign = client-side marker (localStorage). Resolve =
  `resolveSubmissions([rawId])` (optimistic hide + refetch) — a resolved cluster
  leaves the dashboard/map. **"Resolve all shown"** bulk-resolves the current
  filter.
- `IssueDrawer` shows the issue; the attached **image** and **voice note** appear
  only when present; a **Complaint Location** map (read-only `LocationPicker`)
  appears only when the submission has lat/lng.

### 7.7 MP Heatmap (`app/mp/heatmap/page.tsx`)
Just a header + `<iframe src={HEATMAP_URL}>` inside the MP shell (Sidebar comes
from the layout). The mock React heatmap components were deleted.

### 7.8 LocationPicker (`components/common/LocationPicker.tsx`)
Reusable Leaflet map loaded from CDN (module-level promise; no npm dep). Props:
`initialLat, initialLng, interactive, showRemove, height, onChange(lat,lng,address),
onRemove`. Interactive: click drops/moves a red pin, reverse-geocodes (Nominatim)
and calls `onChange`; "Remove marker" clears it. Read-only: fixed marker, still
zoomable (used in the drawer).

### 7.9 Branding
Logo is `public/images/logo.svg` (a fist / speech-bubble mark), used in
`components/layout/Header.tsx` (landing), `components/citizen/Navbar.tsx`, and
`components/mp/Sidebar.tsx`. To use an exact raster, overwrite `logo.svg` or drop
a PNG and repoint the three `src="/images/logo.svg"` references. The citizen-side
voice FAB was removed.

---

## 8. Environment & run

`backend/.env`:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=...          OPENAI_MODEL=gpt-5.5
GEMINI_API_KEY=...          GEMINI_MODEL=gemini-3.5-flash   # embeddings + voice/video
DATABASE_URL=sqlite:///./data/meri_awaaz.db
CHROMA_PATH=./data/chroma_db
ENV=development
```
Frontend override (optional): `frontend/.env.local` → `NEXT_PUBLIC_API_BASE=...`.

Run (two terminals):
```bash
# 1) backend  → http://localhost:8000
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# 2) frontend → http://localhost:3000
cd frontend && npm install && npm run dev
```
Startup seeds 8 plan projects, so the dashboard/heatmap show data before any
submission. Open `/`, pick a role. For a full demo, submit a couple of issues
(include a multi-topic one and a map pin) then view the MP dashboard, issues list
and heatmap.

---

## 9. Known limitations & gotchas

1. **LLM/embedding model names are config.** Voice/video + ChromaDB embeddings
   call Gemini directly with the names in `.env` / `chroma_client.py`
   (`models/gemini-embedding-2`). If those aren't valid current models, media +
   similarity search fail (text agents still work on OpenAI). Verify against
   current Google docs; do not guess.
2. **Fresh-DB severity is uniform.** All 8 seed plans have severity 0.5 → every
   heatmap marker shares a colour and submission counts read 0 until citizens
   submit. This is by design.
3. **Ward canonicalisation is frontend-only** (Citizen Issues). The heatmap still
   groups by the raw stored location, so typo/Hindi variants can create separate
   markers there. Porting `canonicalWard` into `api/heatmap.py` grouping (and/or
   normalising at submit time) would unify them — a small, optional change.
4. **Assign is client-side only** (localStorage `mp_assigned_ids`); it does not
   affect the map/count. Resolve is a real backend state.
5. **Maps need internet at runtime** (Leaflet CDN + OSM tiles + Nominatim), same
   as the heatmap.
6. **`cluster_size` can over-count** when similar results span multiple clusters
   (`demand_tools.cluster_submissions` uses `len(similar)+1`) — intentional
   simplification.
7. **`prompts/*.md` are empty stubs**; real prompts live inline in the agent/tool
   Python files.
8. Older docs (`ARCHITECTURE.md`, `MERI_AWAAZ_CONTEXT.md`) predate the OpenAI
   switch and some fixes — trust this file.

---

## 10. Where to change common things

| Want to change… | Edit |
|---|---|
| Constituency / district | `backend/app/config.py::CONSTITUENCY` |
| Category → dataset / need field | `config.py::CATEGORY_CONFIG` |
| Cost anchors | `config.py::CATEGORY_COST_ESTIMATES` |
| Scoring weights / normalisation | `tools/policy_tools.py`, `services/need_scoring.py` |
| A town's coordinates | `data/village_coordinates.json` |
| LLM provider / model | `backend/.env` |
| Heatmap look/behaviour | `backend/app/static/heatmap.html` |
| Heatmap data grouping / resolve exclusion | `backend/app/api/heatmap.py` |
| Backend API base for the frontend | `frontend/.env.local` (`NEXT_PUBLIC_API_BASE`) |
| Logo | `frontend/public/images/logo.svg` (+ 3 refs) |
| Location picker behaviour | `frontend/components/common/LocationPicker.tsx` |
| Citizen Issues mapping / filters / resolve | `frontend/app/mp/citizen-issues/page.tsx` |

---

## 11. End-to-end data flow (mental model)

1. Citizen submits via `frontend .../review` → `POST /api/submissions` (multipart,
   with optional lat/lng + media).
2. Backend transcribes/describes media → `decompose_text` splits topics → runs the
   LangGraph pipeline per topic → writes to SQLite (record), ChromaDB (search),
   STORE (fast reads). Returns the recommendation(s).
3. MP surfaces read STORE/SQLite: `/api/dashboard`, `/api/recommendations`,
   `/api/submissions` (issues list), and the map via `/heatmap` + `/api/heatmap`.
   All three read endpoints exclude fully-resolved clusters.
4. MP resolves complaints → `POST /api/submissions/resolve` → fully-resolved
   clusters drop off the dashboard and map.

Every number comes from Python; every piece of language comes from the LLM. Keep
it that way.
