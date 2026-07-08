# MeriAwaaz AI — Complete Project Context (Transfer Document)

> Single handoff document for another AI model or developer. It explains **what
> the project is, how every part works, how they connect, how to run it, and
> where the known sharp edges are** — including the new Constituency Heatmap
> feature. For the exhaustive per-agent tables, see `ARCHITECTURE.md`; this file
> is the authoritative, up-to-date map of the whole system.
>
> Last updated: 2026-07-08.

---

## 0b. Frontend integration (2026-07-08, session 3)

The Next.js frontend (`frontend/`, Next 16 + React 19 + Tailwind 4 + zustand) is
now wired to the backend end-to-end. See `RUN.md` for how to run both.

- **API layer written** (`frontend/services/api.ts`, `frontend/types/api.ts`) —
  base URL from `NEXT_PUBLIC_API_BASE` (default `http://localhost:8000`).
- **Citizen submit is real** — the Review page calls `POST /api/submissions`
  (multipart; channel inferred from attachments; description + location folded
  into the message text). StepThree shows the citizen's own input; the Success
  page shows the AI-matched project(s) + priority score from the response.
- **MP Dashboard** is a live client component fed by `GET /api/dashboard`
  (stat cards, top recommendations, priority feed, category distribution).
- **MP Citizen Issues** is fed by the new `GET /api/submissions?limit=` list;
  filters/sort are derived from live data. Backend categories are mapped to the
  UI category union; priority is derived from the linked project's score.
- **MP Heatmap** embeds the backend Leaflet map (`GET /heatmap`) in an iframe
  inside the MP shell — the heatmap itself is unchanged. The old mock React
  heatmap components and all `mockData.ts` files were removed. This also fixed a
  pre-existing double-sidebar bug (the page rendered its own Sidebar on top of
  the one from `app/mp/layout.tsx`).
- **Backend additions for the frontend:** `GET /api/submissions` (list, enriched
  with priority from STORE) and CORS widened to `localhost:3000` + `:5173`.

Contract table and run steps are in `RUN.md`.

**Session 4 additions:**
- **Interactive location picker** (`frontend/components/common/LocationPicker.tsx`)
  — Leaflet loaded from CDN (same tech as the heatmap, no npm dep). Used on the
  citizen "Pin the location" step (click to drop/move a red pin, auto reverse-
  geocode to the address box, remove-marker button; address is required) and,
  read-only, in the MP issue drawer as a "Complaint Location" map.
- **Location persistence** — submissions carry `lat`/`lng` (new columns; sent as
  form fields; returned by `GET /api/submissions`).
- **Resolve model** — `POST /api/submissions/resolve {ids:[...]}` marks
  submissions resolved (new `resolved` column). `database.resolved_cluster_ids()`
  returns clusters whose every feeding complaint is resolved; those are excluded
  from `/api/dashboard`, `/api/recommendations`, and `/api/heatmap`, so a fully-
  resolved cluster disappears from the map and the project count drops. The MP
  Citizen Issues page has per-row Resolve and a "Resolve all shown" bulk button;
  Assign stays a client-side (localStorage) marker.
- **Branding/cleanup** — logo replaced everywhere with
  `frontend/public/images/logo.svg` (a fist/speech-bubble mark; overwrite this
  file with a PNG to use an exact asset); the citizen-side voice FAB was removed.
- **Note:** the location picker needs internet at runtime (Leaflet CDN + OSM
  tiles + Nominatim reverse geocoding), same as the heatmap.

---

## 0. Recent changes (2026-07-08, session 2)

- **Multi-topic submissions.** A submission that raises several problems (e.g.
  "Kesarpur has road potholes AND its health centre has a medicine shortage") is
  now split by `services/decompose.py::decompose_text` into one complaint per
  topic; the pipeline runs once per topic, so each updates or creates its OWN
  demand cluster / project. Implemented in `api/submissions.py` and `api/video.py`
  (media is transcribed/analysed first, then decomposed, then fanned out). If the
  LLM is unavailable, decomposition falls back to a single issue — identical to
  the old behaviour. Each topic is indexed separately in ChromaDB so future
  submissions cluster per-topic. The endpoints now return `topics` and a
  `recommendations` list (plus the primary `recommendation`).
- **Heatmap widget content.** The per-project widget now shows the project
  **summary/details**, the **number of submissions** clustered into that project,
  and the **estimated affected population** (replacing the old "existing plan
  project" badge). `GET /api/heatmap` gained `description`, `submission_count`,
  and `population_affected` fields.
- **Heatmap auto-sync.** `app/static/heatmap.html` polls `/api/heatmap` every 12s
  (and has a manual ↻ Refresh button), so new submissions appear on the map
  without a reload. Polling never disrupts an open widget.

---

## 1. What this project is

**MeriAwaaz AI** ("My Voice AI") is a **constituency development decision-support
system for an Indian Member of Parliament (MP)**. Citizens submit grievances in
any format — text, voice, photo, or video, in any Indian language — and a
5-agent AI pipeline turns each submission into a **ranked development project**
the MP can act on. The MP sees a dashboard of scored project cards and an
interactive **map (heatmap)** of the constituency.

It is a **hackathon project**. Backend is complete and runnable; the main
"frontend" that exists today is the standalone **Constituency Heatmap** page
(described in §7). The larger React dashboard is not built (`frontend/` holds
only a `.gitkeep`).

**Core design principle (repeated everywhere, do not violate it):**
> **LLMs produce only language. Python produces every number.**
Scores, rankings, cluster sizes, infrastructure gaps, and populations are all
computed deterministically in Python. The LLM only transcribes speech, describes
images, parses complaints, names clusters, and writes titles/explanations. This
makes results reproducible and auditable, and lets the system **degrade
gracefully** — if the LLM API is unavailable, every node falls back to
pure-Python logic and the pipeline still returns a valid answer (never a 500).

---

## 2. Technology stack

| Layer | Technology |
|---|---|
| API framework | FastAPI (+ Uvicorn) |
| Agent framework | LangGraph `StateGraph` + `create_react_agent` |
| LLM (agents) | Configurable via `LLM_PROVIDER` — **currently OpenAI** (`gpt-5.5`). Also supports `gemini` and `claude`. |
| LLM (media + embeddings) | Google Gemini directly (voice/video transcription via File API; ChromaDB embeddings) |
| Vector DB | ChromaDB (HNSW, cosine) |
| Structured storage | SQLite (raw `sqlite3`, no ORM) |
| In-memory state | `STORE` singleton (Python dicts) |
| Map frontend | Leaflet 1.9.4 + OpenStreetMap tiles + Nominatim geocoder (all free, no API key) |

> **Doc-drift note:** `ARCHITECTURE.md` says "Gemini 2.0 Flash" throughout. That
> is outdated. The **agents actually run on OpenAI** (`LLM_PROVIDER=openai`,
> `OPENAI_MODEL=gpt-5.5` in `backend/.env`). Gemini is retained only for
> embeddings and voice/video. `core/llm.py` is provider-agnostic.

---

## 3. Repository layout

```
MeriAwaaz-AI/
├── ARCHITECTURE.md              ← deep per-agent design (accurate except LLM provider)
├── CONTEXT.md                   ← THIS FILE (master transfer doc)
├── BUGFIX_LOG.md                ← every bug fixed, with root cause + fix
├── MERI_AWAAZ_CONTEXT.md        ← older handoff doc (partly stale re: bug list)
├── PROJECT_ANALYSIS.md          ← original team/branch integration notes
├── docs/                        ← spec, API contracts, implementation checklist
├── datasets/demo/               ← raw source CSVs (govt data)
├── scripts/prepare_nfhs5_healthcare.py  ← dataset prep utility
├── prompts/                     ← EMPTY stub .md files (NOT used at runtime)
└── backend/
    ├── .env                     ← provider + keys + paths
    ├── requirements.txt
    └── app/
        ├── main.py              ← FastAPI app, routers, startup, /heatmap page route
        ├── config.py            ← CONSTITUENCY, CATEGORY_CONFIG, CATEGORY_COST_ESTIMATES
        ├── supervisor.py        ← LangGraph graph + node wrappers + fallbacks
        ├── core/llm.py          ← get_model() provider factory + content_to_text()
        ├── schemas/             ← models.py (all Pydantic), dashboard.py, settings.py
        ├── agents/              ← 5 ReAct agents + speech_processing + vision_processing
        ├── tools/               ← citizen/demand/knowledge/policy/explainability tools
        ├── services/            ← database.py, chroma_client.py, store.py, need_scoring.py, trace.py
        ├── api/                 ← health, submissions, video, dashboard, recommendations,
        │                          explain, trace, **heatmap** (new)
        ├── static/heatmap.html  ← the Constituency Heatmap frontend (new)
        └── data/                ← local_plans.json, *_need.json, synthetic priors,
                                    village_coordinates.json, uploads/
```

---

## 4. The 5-agent pipeline (LangGraph)

A single Pydantic **`AgentState`** flows through the graph, accumulating results.
`route_intake` dispatches on `input_type`:

```
POST /api/submissions (text/voice/photo)  or  POST /api/submissions/video
        │
   route_intake ──► voice → speech_processing ─┐
                    image/video → vision_processing ─┤ (media → raw_text)
                    text ───────────────────────────┘
        ▼
  citizen_intelligence   → parsed_issue {category, location, summary, confidence, language}
        ▼
  demand_intelligence    → cluster {cluster_id, cluster_name, cluster_size, center_location}
        ▼                   (ChromaDB similarity search + LLM clustering)
  knowledge_fusion       → knowledge_context {severity_score, population, cost, data_confidence,
        ▼                   is_existing_plan_project, plan linkage} (govt JSON + deterministic first)
  policy_recommendation  → recommendation {project_id, title, priority_score, breakdown}
        ▼                   (pure-Python relative scoring; LLM writes title + reason)
  explainability         → recommendation.explanation {evidence, summary, confidence_score}
        ▼
  Result → SQLite (permanent) + ChromaDB (indexed) + STORE (fast dashboard reads) → API response
```

**Priority score (deterministic, 0–100):**
```
citizen_demand    = 40 × (demand_count / max_demand_in_store)     # floor of 5 on denominator
severity          = 30 × severity_score                           # 0–1 from Knowledge Fusion
population_impact = 20 × (population / max_pop_in_store)
cost_feasibility  = 10 × (1 − cost / (2 × ₹50L))  [5.0 if cost unknown]
```
Normalising against the strongest competitor (not a fixed cap) means rankings
shift visibly as complaints cluster. Implemented in
`tools/policy_tools.py::compute_relative_breakdown`.

**Fault tolerance:** every node calls `_llm_unavailable(state)` first; if a prior
node recorded a quota/429/503/"api key" error, all downstream nodes skip the LLM
and use deterministic fallbacks. The pipeline never raises to the caller.

**Tracing:** every node is wrapped with `traced("name")` → logs to console and
persists to the `agent_log` SQLite table. Query `GET /api/trace/{submission_id}`.

For full detail on each agent's tools, prompts, and fallbacks, read
`ARCHITECTURE.md` §"The 5-Agent Pipeline".

---

## 5. Storage layers

- **SQLite** (`backend/app/data/meri_awaaz.db`, via `services/database.py`) —
  permanent record: `submissions`, `clusters`, `recommendations`, `agent_log`.
  `init_db()` creates tables and auto-migrates missing columns on startup.
- **`STORE` singleton** (`services/store.py`) — in-RAM dicts of `FusedContext`
  and `Recommendation` keyed by `project_id`, plus `clusters`. Dashboard and
  heatmap reads hit STORE for instant responses. Seeded at startup with **8 plan
  projects** from `local_plans.json`.
- **ChromaDB** (`services/chroma_client.py`) — vector index of submission text
  for similarity search. Uses a **sentinel document** (`__embedding_model__`) so
  the collection is only rebuilt when the embedding model name changes, not on
  every restart. Queries are filtered by `category`.

---

## 6. Data files (`backend/app/data/`)

- `local_plans.json` — 8 seed development-plan projects (one per category),
  located in **Nagpur district villages**: Rampur, Kesarpur, Sultanpur, Bhelupur.
- `healthcare_need.json` — real district data (OPD load + medicine-shortage);
  Healthcare gap blends medicine-shortage with OPD-pressure percentile ranks.
- `education_need.json` — real state data (UDISE school-size %).
- `digital_connectivity_need.json` — real state data (rural teledensity),
  category "Other". City/aggregate rows excluded from normalisation.
- `synthetic_category_priors.json` — clearly-labelled synthetic gaps for
  categories with no real dataset yet (Roads/Water/Sanitation/Electricity/
  Vocational), reported as `data_confidence="synthetic"`.
- `village_coordinates.json` — gazetteer: lowercased place name → `[lat, lng]`.
  Used by the heatmap endpoint for accurate marker placement.
- `uploads/` — saved photos/videos/audio, served at `/uploads/{file}`.

**Normalisation is percentile-rank, not min-max** (`services/need_scoring.py`),
because 77% of districts share medicine-shortage 0.0 and single outliers (Kerala
teledensity 210) broke min-max.

Constituency is hard-coded to **Maharashtra / Nagpur** in `config.py::CONSTITUENCY`.

---

## 7. Constituency Heatmap feature (NEW)

Goal: an India map where **every town is ONE marker** holding all of that town's
projects (all categories); clicking it opens a widget to browse each project.

### 7.1 Backend — `GET /api/heatmap` (`api/heatmap.py`)
- Reads the live `STORE`, groups every recommendation by its town
  (`ctx.location`), and attaches coordinates from `village_coordinates.json`.
- Towns with no known coordinates are returned with `lat/lng = null`; the
  frontend geocodes them via free Nominatim.
- Returns this exact shape (the frontend contract):
  ```json
  { "towns": [ { "name": "Kesarpur", "state": "Maharashtra", "lat": 21.232, "lng": 79.001,
      "projects": [ { "id": "plan_002", "title": "...", "category": "Healthcare",
        "description": "...", "explanation": "...", "priority_score": 41.1,
        "breakdown": {"citizen_demand":0,"severity":15,"population_impact":17.9,"cost_feasibility":8.2},
        "is_existing_plan_project": true } ] } ] }
  ```
- Towns are ordered by their top project's score; projects are highest-first.
- `description` is synthesized honestly (demand + population); `explanation` is
  only present once the Explainability agent has run for that project.

### 7.2 Serving the page — `GET /heatmap` (`main.py`)
`main.py` serves `app/static/heatmap.html` at `/heatmap` so its
`fetch('/api/heatmap')` is **same-origin** — no CORS change needed. Open
`http://localhost:8000/heatmap`.

### 7.3 Frontend — `app/static/heatmap.html` (single file, no build step)
- **Tech (all free, no keys):** Leaflet + OpenStreetMap tiles + Nominatim.
- **Data precedence:** live `/api/heatmap` → embedded `window.HEATMAP_DATA`
  fallback (the real Nagpur constituency, so the page works even over `file://`).
  A header badge shows "● Live data" vs "● Sample data".
- **Requirement mapping:**
  1. India shown on load (`fitBounds(INDIA_BOUNDS)`), plus "India view" /
     "Zoom to constituency" buttons.
  2. **One marker per town**; the number in the dot = clustered project count.
  3. Click → widget with per-project **tabs + Prev/Next**, showing id, category,
     plan/proposed badge, description, explanation, priority score, and four
     breakdown bars.
  4. Marker colour ∝ **severity** (green→yellow→red); scale auto-adapts to data.
  5. Scroll-wheel + button zoom.
  6. Accurate coordinates from the gazetteer (Nominatim fallback otherwise).
  7. Zero paid services.

### 7.4 Popup lifecycle — READ THIS BEFORE EDITING POPUP CODE
The widget is a **real DOM element** (not an HTML string). It uses ONE delegated
click listener guarded by `L.DomEvent.disableClickPropagation` + `L.DomEvent.stop`.
Navigation mutates that element's `innerHTML` **in place** and calls
`popup.update()` — it never calls `setContent()` again while open. The map is
created with `closePopupOnClick: false`. Together these guarantee the widget
opens reliably and **never closes when switching projects**, for any project
count. (See BUGFIX_LOG.md #1 for why the previous string-`onclick`+`setContent`
approach broke.)

---

## 8. API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness `{status:"ok"}` |
| POST | `/api/submissions` | Submit text/voice/photo → runs pipeline |
| GET | `/api/submissions/{id}` | Fetch a stored submission + its recommendation |
| POST | `/api/submissions/video` | Submit video → runs pipeline |
| GET | `/api/dashboard` | Ranked project cards + stats (heatmap array is empty here) |
| POST | `/api/dashboard-refresh` | Re-score all STORE contexts with the relative scorer |
| GET | `/api/recommendations` | All recommendations sorted by score |
| GET | `/api/explain/{project_id}` | On-demand explanation for one project |
| GET | `/api/trace/{id}` / `/api/trace` | Pipeline trace(s) from `agent_log` |
| **GET** | **`/api/heatmap`** | **Town-grouped project data for the map (NEW)** |
| **GET** | **`/heatmap`** | **Serves the heatmap HTML page same-origin (NEW)** |
| GET | `/uploads/{file}` | Static media |

CORS currently allows only `http://localhost:5173` (the future React app). The
heatmap page is served same-origin from `:8000`, so it does not need CORS.

---

## 9. Environment / how to run

`backend/.env` (keys redacted):
```
LLM_PROVIDER=openai
OPENAI_API_KEY=...            # agents run here
OPENAI_MODEL=gpt-5.5
GEMINI_API_KEY=...            # embeddings + voice/video (Gemini File API)
GEMINI_MODEL=gemini-3.5-flash # used by speech/vision + as embedding-context model name
DATABASE_URL=sqlite:///./data/meri_awaaz.db
CHROMA_PATH=./data/chroma_db
ENV=development
```
Run:
```bash
cd backend
python -m venv venv && venv\Scripts\activate      # Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload           # → http://localhost:8000
```
Startup: loads `.env`, requires the provider's API key, `init_db()`, loads the 8
seed plans into STORE, then re-scores them with the relative scorer.
Then open **http://localhost:8000/heatmap** and **http://localhost:8000/docs**.

---

## 10. Known limitations & config to watch (NOT bugs)

1. **Seed severity is uniform.** All 8 plan seeds have `severity_score=0.5` → the
   severity component = 15 for each, so on a fresh DB every heatmap marker is the
   same colour. The green→yellow→red spread appears once **citizen submissions**
   raise severity (the complaint boost) or once real varied data is present.
2. **`GEMINI_MODEL` / `EMBEDDING_MODEL` names.** Voice/video transcription and
   ChromaDB embeddings call Gemini directly with the names in `.env` /
   `chroma_client.py` (`models/gemini-embedding-2`). If those model names are not
   valid for the current Gemini API, media submissions and similarity search
   fail (text agents still work on OpenAI). Verify against current Google docs.
3. **`cluster_size` can over-count.** `tools/demand_tools.cluster_submissions`
   sets a new cluster's size to `len(similar)+1`; if the similar results span
   multiple existing clusters this slightly inflates demand. Intentional
   simplification for the demo.
4. **Dashboard heatmap array is empty** in `GET /api/dashboard` (superseded by
   the dedicated `GET /api/heatmap`).
5. **Doc drift:** `ARCHITECTURE.md` and `MERI_AWAAZ_CONTEXT.md` predate the
   OpenAI switch and list already-fixed bugs; trust THIS file for current state.
6. `prompts/*.md` are empty stubs; real prompts live inline in the agent/tool
   Python files.

---

## 11. Where to change common things

- **Constituency / district:** `config.py::CONSTITUENCY`.
- **Category → dataset mapping / need field:** `config.py::CATEGORY_CONFIG`.
- **Cost anchors:** `config.py::CATEGORY_COST_ESTIMATES`.
- **Scoring weights / normalisation:** `tools/policy_tools.py`.
- **Add a town's coordinates:** `data/village_coordinates.json`.
- **Swap the LLM provider/model:** `.env` (`LLM_PROVIDER`, `*_MODEL`).
- **Heatmap look/behaviour:** `app/static/heatmap.html` (single file).
- **Heatmap data grouping:** `api/heatmap.py`.

---

## 12. Quick mental model for a new AI picking this up

1. A citizen submission enters through `api/submissions.py` (or `video.py`).
2. `supervisor.py` runs the LangGraph pipeline; each node reads/writes
   `AgentState` and has a deterministic fallback.
3. Results land in SQLite (record), ChromaDB (search), and STORE (fast reads).
4. The MP-facing surfaces read STORE: `/api/dashboard`, `/api/recommendations`,
   and the map via `/api/heatmap` + `/heatmap`.
5. Numbers are always Python; language is always the LLM. Keep it that way.
