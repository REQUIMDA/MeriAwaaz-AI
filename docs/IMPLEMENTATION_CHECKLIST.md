# MeriAwaaz AI — Implementation Checklist
**Version:** 2.1 | **Status:** Active Execution Document | **Last Updated:** 2026-07-03

> This is the team's daily execution document. Every task is atomic (15–45 min), owner-assigned, dependency-ordered, and has clear acceptance criteria. Work directly from this list. Do not ask for clarification — everything is specified here.

---

## Priority Legend
- **P0** — Must Build. Demo breaks without it.
- **P1** — Nice to Have. Improves demo quality.
- **P2** — Future Work. Cut if behind schedule.

## Owner Legend
- **TL** — Team Lead (LangGraph, Agents, Prompts)
- **M2** — Member 2 (Frontend, Dashboard, UI)
- **M3** — Member 3 (Backend, APIs, Workflow)
- **M4** — Member 4 (Database, Data, Integration)

---

## Day-by-Day Goals

| Day | Goal | End-of-Day Milestone |
|-----|------|----------------------|
| 1 | Foundation | Repo live, folders created, contracts agreed, DB schema created, health endpoint returns 200, React app loads |
| 2 | Core Intelligence | Submission endpoint works, full agent pipeline runs, SQLite writes succeed, ChromaDB similarity works |
| 3 | Dashboard + Explainability | Dashboard loads real data, heatmap renders, ranked cards show, evidence cards show |
| 4 | Integration + Polish | Full end-to-end happy path works from chat to dashboard, no manual steps needed |
| 5 | Demo Prep | Prompts tuned, fallbacks verified, rehearsal done, demo story locked |

---

## Integration Checkpoints

| Checkpoint | When | Verified By |
|-----------|------|-------------|
| IC-1: API ↔ Frontend | End of Day 2 | M3 + M2: POST /api/submissions returns 200 in browser |
| IC-2: Agent Pipeline ↔ DB | End of Day 2 | TL + M4: submission row appears in SQLite after POST |
| IC-3: Dashboard ↔ API | End of Day 3 | M2 + M3: GET /api/dashboard returns ranked projects displayed on screen |
| IC-4: Full Happy Path | End of Day 4 | All: submit text → see result on dashboard in under 20s |
| IC-5: Demo Run | Day 5 AM | All: complete demo story twice without error |

---

## Daily Sanity Checks

Run these every morning before starting new work:

```
□ Backend starts without errors: uvicorn app.main:app --reload
□ Frontend starts without errors: npm run dev
□ SQLite file exists at backend/app/data/meri_awaaz.db
□ Health endpoint returns 200: GET http://localhost:8000/health
□ No merge conflicts on main branch
```

---

---

# SECTION 1 — Repository Setup

**Priority:** P0 | **Day:** 1 | **Owner:** TL

---

### 1.1 Create GitHub Repository
- [ ] **Task:** Create a new GitHub repository named `MeriAwaaz-AI` with a public or team-private visibility setting.
  - **Owner:** TL
  - **Dependencies:** None
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** Repository exists at github.com. Default branch is `main`. README.md is present.

### 1.2 Add All Team Members as Collaborators
- [ ] **Task:** Invite M2, M3, M4 as collaborators with Write access.
  - **Owner:** TL
  - **Dependencies:** 1.1
  - **Estimated Time:** 5 min
  - **Acceptance Criteria:** All four members can push to the repository.

### 1.3 Create Root .gitignore
- [ ] **Task:** Create `.gitignore` at repo root. Include: `__pycache__/`, `*.pyc`, `.env`, `node_modules/`, `dist/`, `.venv/`, `*.db`, `*.sqlite`, `chroma_db/`, `.DS_Store`, `*.log`.
  - **Owner:** TL
  - **Dependencies:** 1.1
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** `.gitignore` committed. Running `git status` after adding ignored files shows them as untracked and ignored.

### 1.4 Create Root README.md
- [ ] **Task:** Write a short `README.md` with: project name, one-line description, how to run backend, how to run frontend, team names.
  - **Owner:** TL
  - **Dependencies:** 1.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** README renders correctly on GitHub. All commands in the README work on a clean clone.

### 1.5 Push Initial Commit
- [ ] **Task:** Push `.gitignore`, `README.md`, and empty `docs/` folder as the first commit to `main`.
  - **Owner:** TL
  - **Dependencies:** 1.3, 1.4
  - **Estimated Time:** 5 min
  - **Acceptance Criteria:** `main` branch has at least one commit. All team members can `git pull` successfully.

**Section 1 — Definition of Done:**
- [ ] Repository is live on GitHub
- [ ] All four members have push access
- [ ] `.gitignore` is committed and working
- [ ] README exists with run instructions
- [ ] First commit is on `main`

---

# SECTION 2 — Environment Setup

**Priority:** P0 | **Day:** 1

---

### 2.1 Create Python Virtual Environment (Backend)
- [ ] **Task:** Inside `backend/`, run `python -m venv .venv`. Document activation command in README.
  - **Owner:** M3
  - **Dependencies:** 1.5
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** `.venv/` directory exists. `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows) activates the environment. `python --version` returns 3.10+.

### 2.2 Create Backend requirements.txt
- [ ] **Task:** Create `backend/requirements.txt` with the following packages:
  ```
  fastapi==0.111.0
  uvicorn[standard]==0.29.0
  pydantic==2.7.1
  python-dotenv==1.0.1
  langgraph==0.1.19
  langchain==0.2.5
  langchain-openai==0.1.8
  chromadb==0.5.0
  sentence-transformers==3.0.1
  Pillow==10.3.0
  SpeechRecognition==3.10.4
  aiofiles==23.2.1
  httpx==0.27.0
  ```
  - **Owner:** M3
  - **Dependencies:** 2.1
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** `pip install -r requirements.txt` completes without errors.

### 2.3 Install Backend Dependencies
- [ ] **Task:** With `.venv` active, run `pip install -r requirements.txt`. Fix any version conflicts.
  - **Owner:** M3
  - **Dependencies:** 2.2
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** `pip list` shows all packages installed. No import errors when running `python -c "import fastapi, langgraph, chromadb"`.

### 2.4 Create Backend .env File
- [ ] **Task:** Create `backend/.env` with: `OPENAI_API_KEY=your_key_here`, `DATABASE_URL=sqlite:///./data/meri_awaaz.db`, `CHROMA_PATH=./data/chroma_db`, `ENV=development`.
  - **Owner:** M3
  - **Dependencies:** 2.1
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** `.env` file exists. It is listed in `.gitignore`. The app can read `OPENAI_API_KEY` via `python-dotenv`.

### 2.5 Create Frontend Node Environment
- [ ] **Task:** Inside `frontend/`, run `npm create vite@latest . -- --template react-ts`. Accept overwrite prompt.
  - **Owner:** M2
  - **Dependencies:** 1.5
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** `package.json` exists in `frontend/`. `npm install` completes. `npm run dev` starts a dev server on port 5173.

### 2.6 Install Frontend Dependencies
- [ ] **Task:** In `frontend/`, run: `npm install axios react-router-dom @types/react-router-dom tailwindcss postcss autoprefixer recharts leaflet @types/leaflet`.
  - **Owner:** M2
  - **Dependencies:** 2.5
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** `node_modules/` exists. `npm run dev` still starts without errors. All packages appear in `package.json`.

### 2.7 Configure Tailwind CSS
- [ ] **Task:** Run `npx tailwindcss init -p`. Update `tailwind.config.js` content array to include `./src/**/*.{js,ts,jsx,tsx}`. Add Tailwind directives to `src/index.css`.
  - **Owner:** M2
  - **Dependencies:** 2.6
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** A component with `className="bg-blue-500 text-white p-4"` renders with correct styling in the browser.

### 2.8 Create Frontend .env File
- [ ] **Task:** Create `frontend/.env` with: `VITE_API_BASE_URL=http://localhost:8000`.
  - **Owner:** M2
  - **Dependencies:** 2.5
  - **Estimated Time:** 5 min
  - **Acceptance Criteria:** `import.meta.env.VITE_API_BASE_URL` returns `http://localhost:8000` in the browser console.

**Section 2 — Definition of Done:**
- [ ] Backend venv activates and all packages install without errors
- [ ] Frontend dev server starts on port 5173
- [ ] Both `.env` files exist and are gitignored
- [ ] Tailwind styles render correctly in browser

---

# SECTION 3 — Git Branch Setup

**Priority:** P0 | **Day:** 1 | **Owner:** TL

---

### 3.1 Define Branch Naming Convention
- [ ] **Task:** Document branch naming in README: `feature/<section>-<short-description>`. Example: `feature/backend-health-endpoint`.
  - **Owner:** TL
  - **Dependencies:** 1.5
  - **Estimated Time:** 5 min
  - **Acceptance Criteria:** Convention is written in README. All team members confirm they read it.

### 3.2 Create Day 1 Feature Branches
- [ ] **Task:** Each member creates their Day 1 branch from `main`: TL → `feature/agents-scaffold`, M2 → `feature/frontend-scaffold`, M3 → `feature/backend-scaffold`, M4 → `feature/database-scaffold`.
  - **Owner:** All
  - **Dependencies:** 3.1
  - **Estimated Time:** 5 min
  - **Acceptance Criteria:** All four branches exist on GitHub remote.

### 3.3 Set Merge Rule
- [ ] **Task:** Agree and document: no direct push to `main`. All changes go through a branch. Merge only after local test passes. One other member must eyeball the PR before merge (no formal review required — just a quick read).
  - **Owner:** TL
  - **Dependencies:** 3.1
  - **Estimated Time:** 5 min
  - **Acceptance Criteria:** Rule is in README. All members confirm.

**Section 3 — Definition of Done:**
- [ ] Branch naming convention documented
- [ ] All Day 1 branches created
- [ ] Merge rule agreed and documented

---

# SECTION 4 — Folder Structure

**Priority:** P0 | **Day:** 1 | **Owner:** M3

---

### 4.1 Create Backend Folder Structure
- [ ] **Task:** Create the following directories inside `backend/`:
  ```
  backend/
  ├── app/
  │   ├── api/
  │   ├── agents/
  │   ├── schemas/
  │   ├── services/
  │   └── data/
  ├── tests/
  └── requirements.txt
  ```
  Add a `__init__.py` to each Python package folder.
  - **Owner:** M3
  - **Dependencies:** 1.5
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** All directories exist. Each Python folder has `__init__.py`. `ls backend/app/` lists: `api/`, `agents/`, `schemas/`, `services/`, `data/`.

### 4.2 Create Frontend Folder Structure
- [ ] **Task:** Inside `frontend/src/`, create: `components/`, `pages/`, `services/`, `styles/`, `types/`.
  - **Owner:** M2
  - **Dependencies:** 2.5
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** All five folders exist under `frontend/src/`.

### 4.3 Create Root-Level Folders
- [ ] **Task:** Create at repo root: `datasets/demo/`, `prompts/`, `scripts/`, `tests/`, `assets/`.
  - **Owner:** TL
  - **Dependencies:** 1.5
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** All five folders exist at repo root. Each has a `.gitkeep` file so they are tracked by git.

### 4.4 Create Prompt Placeholder Files
- [ ] **Task:** In `prompts/`, create empty files: `supervisor_prompt.md`, `citizen_prompt.md`, `demand_prompt.md`, `fusion_prompt.md`, `policy_prompt.md`, `explainability_prompt.md`.
  - **Owner:** TL
  - **Dependencies:** 4.3
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** Six prompt files exist in `prompts/`. Each has at least a `# Title` heading as placeholder.

**Section 4 — Definition of Done:**
- [ ] Full backend folder structure exists with `__init__.py` in every package
- [ ] Full frontend folder structure exists
- [ ] Root-level folders exist and are tracked in git
- [ ] All six prompt placeholder files exist

---

# SECTION 5 — Backend Setup

**Priority:** P0 | **Day:** 1 | **Owner:** M3

---

### 5.1 Create FastAPI Application Entry Point
- [ ] **Task:** Create `backend/app/main.py`. Initialize `FastAPI(title="MeriAwaaz AI", version="1.0.0")`. Add startup log message. Import and include routers (stub for now).
  - **Owner:** M3
  - **Dependencies:** 4.1, 2.3
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** `uvicorn app.main:app --reload` starts without errors from the `backend/` directory. Swagger UI is accessible at `http://localhost:8000/docs`.

### 5.2 Configure CORS
- [ ] **Task:** In `main.py`, add `CORSMiddleware` with `allow_origins=["http://localhost:5173"]`, `allow_methods=["*"]`, `allow_headers=["*"]`.
  - **Owner:** M3
  - **Dependencies:** 5.1
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** A `fetch("http://localhost:8000/health")` call from the browser console at `http://localhost:5173` does not produce a CORS error.

### 5.3 Create Health Endpoint
- [ ] **Task:** In `backend/app/api/health.py`, create a router with `GET /health` that returns `{"status": "ok", "service": "MeriAwaaz AI"}`.
  - **Owner:** M3
  - **Dependencies:** 5.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** `GET http://localhost:8000/health` returns HTTP 200 with the correct JSON body. Visible in Swagger UI.

### 5.4 Load Environment Variables on Startup
- [ ] **Task:** In `main.py`, use `python-dotenv` to load `.env`. Validate that `OPENAI_API_KEY` is set; raise a startup error if it is missing.
  - **Owner:** M3
  - **Dependencies:** 5.1, 2.4
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Starting the app without `.env` prints a clear error. Starting with `.env` present starts cleanly.

### 5.5 Create Pydantic Settings Model
- [ ] **Task:** Create `backend/app/schemas/settings.py` with a Pydantic `Settings` model reading from environment variables: `openai_api_key`, `database_url`, `chroma_path`, `env`.
  - **Owner:** M3
  - **Dependencies:** 5.4
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** `from app.schemas.settings import Settings; s = Settings()` resolves without errors and `s.openai_api_key` returns a non-empty string.

**Section 5 — Definition of Done:**
- [ ] `uvicorn app.main:app --reload` starts cleanly
- [ ] `GET /health` returns 200
- [ ] CORS allows requests from `localhost:5173`
- [ ] App fails loudly if `OPENAI_API_KEY` is missing
- [ ] Swagger UI is accessible at `/docs`

---

# SECTION 6 — Frontend Setup

**Priority:** P0 | **Day:** 1 | **Owner:** M2

---

### 6.1 Clean Vite Boilerplate
- [ ] **Task:** Remove default Vite/React boilerplate from `App.tsx`, `App.css`. Clear `index.css` except Tailwind directives. Remove the Vite logo SVG files.
  - **Owner:** M2
  - **Dependencies:** 2.6, 2.7
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** `npm run dev` loads a blank white page with no errors in the console.

### 6.2 Create App Router
- [ ] **Task:** In `App.tsx`, set up `react-router-dom` with two routes: `/` → `<ChatPage />` (placeholder), `/dashboard` → `<DashboardPage />` (placeholder).
  - **Owner:** M2
  - **Dependencies:** 6.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Navigating to `http://localhost:5173/` renders "Chat Page" text. Navigating to `/dashboard` renders "Dashboard Page" text.

### 6.3 Create API Service Module
- [ ] **Task:** Create `frontend/src/services/api.ts` with an Axios instance using `baseURL: import.meta.env.VITE_API_BASE_URL`. Export four typed functions: `submitRequest(text, locationHint)`, `getSubmission(id)`, `getDashboard()`, `getExplanation(projectId)` (calls `GET /api/explain/{projectId}`).
  - **Owner:** M2
  - **Dependencies:** 6.2, 2.8
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** Calling `getDashboard()` from the browser console does not throw a network error (it may return 404 — that is fine at this stage).

### 6.4 Create Shared TypeScript Types
- [ ] **Task:** Create `frontend/src/types/index.ts`. Define interfaces: `Submission`, `ParsedIssue`, `Recommendation`, `DashboardData`, `HeatmapPoint`, `Project`.
  - **Owner:** M2
  - **Dependencies:** 6.2
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** No TypeScript compilation errors in `npm run build`. All interfaces match the JSON contracts in Section 14 of the spec.

### 6.5 Create Navigation Bar Component
- [ ] **Task:** Create `frontend/src/components/NavBar.tsx` with links to `/` (Citizen Portal) and `/dashboard` (MP Dashboard). Style with Tailwind.
  - **Owner:** M2
  - **Dependencies:** 6.2
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** NavBar renders on all pages. Links navigate correctly without full page reload.

**Section 6 — Definition of Done:**
- [ ] App loads on `localhost:5173` with no console errors
- [ ] Router works for `/` and `/dashboard`
- [ ] API service module exists with three typed functions
- [ ] TypeScript types match JSON contracts
- [ ] NavBar renders on both pages

---

# SECTION 7 — SQLite Setup

**Priority:** P0 | **Day:** 1 | **Owner:** M4

---

### 7.1 Create Database Initialization Module
- [ ] **Task:** Create `backend/app/services/database.py`. Use Python's built-in `sqlite3`. Implement `init_db()` that creates the database file at the path from `Settings.database_url` and runs the schema DDL.
  - **Owner:** M4
  - **Dependencies:** 5.5, 4.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Calling `init_db()` creates the `.db` file. Calling it a second time does not raise an error (idempotent).

### 7.2 Create submissions Table
- [ ] **Task:** In `database.py`, write the DDL for `submissions`:
  ```sql
  CREATE TABLE IF NOT EXISTS submissions (
    id TEXT PRIMARY KEY,
    created_at TEXT,
    source TEXT,
    text TEXT,
    location_hint TEXT,
    issue_category TEXT,
    urgency TEXT,
    summary TEXT,
    confidence REAL,
    cluster_id TEXT
  );
  ```
  `cluster_id` is written by the Demand Intelligence Agent after clustering. Dashboard reads it directly — no re-clustering on refresh.
  - **Owner:** M4
  - **Dependencies:** 7.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** After `init_db()`, running `sqlite3 meri_awaaz.db ".tables"` shows `submissions`. Schema has 10 columns including `cluster_id`.

### 7.3 Create clusters Table
- [ ] **Task:** Add DDL for `clusters`:
  ```sql
  CREATE TABLE IF NOT EXISTS clusters (
    id TEXT PRIMARY KEY,
    name TEXT,
    size INTEGER,
    hotspot TEXT
  );
  ```
  - **Owner:** M4
  - **Dependencies:** 7.2
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** `clusters` table appears in `.tables` output.

### 7.4 Create projects Table
- [ ] **Task:** Add DDL for `projects`:
  ```sql
  CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    title TEXT,
    category TEXT,
    location TEXT,
    estimated_cost REAL,
    priority_score REAL,
    confidence REAL,
    summary TEXT
  );
  ```
  - **Owner:** M4
  - **Dependencies:** 7.2
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** `projects` table appears in `.tables` output.

### 7.5 Create recommendations Table
- [ ] **Task:** Add DDL for `recommendations`:
  ```sql
  CREATE TABLE IF NOT EXISTS recommendations (
    id TEXT PRIMARY KEY,
    submission_id TEXT,
    project_id TEXT,
    priority_score REAL,
    confidence REAL,
    created_at TEXT
  );
  ```
  `reason` and `evidence` are NOT stored. They are generated on demand by the Explainability Agent when a user selects a project card. This prevents a live LLM call on every dashboard refresh.
  - **Owner:** M4
  - **Dependencies:** 7.3, 7.4
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** `recommendations` table appears in `.tables` output. Schema has exactly 6 columns — no `reason` or `evidence` columns.

### 7.6 Create agent_logs Table
- [ ] **Task:** Add DDL for `agent_logs`:
  ```sql
  CREATE TABLE IF NOT EXISTS agent_logs (
    id TEXT PRIMARY KEY,
    agent_name TEXT,
    status TEXT,
    execution_time_ms INTEGER,
    created_at TEXT
  );
  ```
  - **Owner:** M4
  - **Dependencies:** 7.1
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** `agent_logs` table appears in `.tables` output.

### 7.7 Call init_db on App Startup
- [ ] **Task:** In `main.py`, add a FastAPI `startup` event that calls `init_db()`.
  - **Owner:** M4
  - **Dependencies:** 7.1 – 7.6, 5.1
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** Starting the app creates the database file and all five tables automatically. No manual SQL step needed.

### 7.8 Create DB Helper Functions
- [ ] **Task:** In `database.py`, implement:
  - `insert_submission(data: dict)` — inserts a new row; `cluster_id` may be None initially
  - `update_submission_cluster(id: str, cluster_id: str)` — called by Demand Agent after clustering
  - `get_submission(id: str) -> dict`
  - `insert_recommendation(data: dict)` — stores `priority_score` + `confidence`, no reason/evidence
  - `get_recommendation_by_submission(submission_id: str) -> dict`
  - `get_all_projects() -> list`
  - `get_ranked_projects() -> list` — ordered by `priority_score DESC`
  - **Owner:** M4
  - **Dependencies:** 7.7
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Each function can be imported and called in a Python REPL. `insert_submission` + `get_submission` round-trip correctly.

**Section 7 — Definition of Done:**
- [ ] All five tables are created on app startup
- [ ] All DB helper functions are importable and tested in a REPL
- [ ] `init_db()` is idempotent (safe to call multiple times)
- [ ] Database file is gitignored

---

# SECTION 8 — ChromaDB Setup

**Priority:** P0 | **Day:** 1–2 | **Owner:** M4

---

### 8.1 Create ChromaDB Client Module
- [ ] **Task:** Create `backend/app/services/chroma_client.py`. Initialize a persistent Chroma client pointing to `Settings.chroma_path`. Export a `get_collection()` function that returns or creates the `demo_documents` collection.
  - **Owner:** M4
  - **Dependencies:** 5.5, 2.3
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** `get_collection()` returns a Chroma collection object without errors. The `chroma_db/` directory is created at the configured path.

### 8.2 Define Collection Schema
- [ ] **Task:** Document in a comment inside `chroma_client.py` the expected document structure:
  - `documents`: short text (submission summary or project title)
  - `metadatas`: `{"type": "submission"|"project", "category": str, "location": str, "ref_id": str}`
  - `ids`: unique string ID
  - **Owner:** M4
  - **Dependencies:** 8.1
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** Comment exists in the file. Structure matches the spec.

### 8.3 Implement add_document Function
- [ ] **Task:** In `chroma_client.py`, implement `add_document(doc_id, text, metadata)` that calls `collection.add(ids=[doc_id], documents=[text], metadatas=[metadata])`.
  - **Owner:** M4
  - **Dependencies:** 8.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Calling `add_document("test_1", "broken roads", {"type":"submission","category":"roads","location":"Ward 12","ref_id":"sub_001"})` adds a document. `collection.count()` returns 1.

### 8.4 Implement query_similar Function
- [ ] **Task:** In `chroma_client.py`, implement `query_similar(text, n_results=3)` that calls `collection.query(query_texts=[text], n_results=n_results)` and returns a list of `{"id", "text", "metadata", "distance"}` dicts.
  - **Owner:** M4
  - **Dependencies:** 8.3
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** After adding 3+ documents, `query_similar("road damage")` returns up to 3 results sorted by similarity. No crash if the collection has fewer than `n_results` documents.

### 8.5 Initialize ChromaDB on App Startup
- [ ] **Task:** In `main.py` startup event, call `get_collection()` to ensure the collection exists.
  - **Owner:** M4
  - **Dependencies:** 8.1, 7.7
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** App starts and logs a message confirming ChromaDB collection is ready.

**Section 8 — Definition of Done:**
- [ ] `get_collection()` works on app startup
- [ ] `add_document()` and `query_similar()` are tested and working
- [ ] `chroma_db/` path is gitignored
- [ ] Collection schema is documented in code

---

# SECTION 9 — Dataset Preparation

**Priority:** P0 | **Day:** 1 | **Owner:** M4

---

### 9.1 Create Synthetic Citizen Requests File
- [ ] **Task:** Create `datasets/demo/citizen_requests.json` — a list of 20 synthetic citizen submissions. Each entry: `{"id", "text", "location_hint", "issue_category", "urgency"}`. Use 5 locations (Ward 1–5), 4 categories (roads, water, electricity, health). Make 5–6 entries about roads to create a clear cluster.
  - **Owner:** M4
  - **Dependencies:** 4.3
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** File has exactly 20 entries. Valid JSON (`python -m json.tool` passes). At least 5 entries have `issue_category = "roads"`. Locations are distributed across all 5 wards.

### 9.2 Create Demo Projects File
- [ ] **Task:** Create `datasets/demo/projects.json` — a list of 8 development project proposals. Each entry: `{"id", "title", "category", "location", "estimated_cost", "summary"}`. Include at least 2 road projects, 2 water projects, 1 health, 1 electricity, 2 others.
  - **Owner:** M4
  - **Dependencies:** 4.3
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** File has exactly 8 entries. Valid JSON. Categories match those in citizen requests. All cost values are realistic (in INR, e.g., 500000–5000000).

### 9.3 Create Static Infrastructure Context File
- [ ] **Task:** Create `datasets/demo/infrastructure_context.json` — a dict keyed by ward name with fields: `{"population": int, "road_coverage_pct": float, "water_access_pct": float, "electricity_access_pct": float, "health_centers": int}` for Wards 1–5.
  - **Owner:** M4
  - **Dependencies:** 4.3
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** File has 5 ward entries. Valid JSON. Values are plausible (e.g., population 5000–15000, coverage 30–90%).

### 9.4 Create GeoJSON File for Heatmap
- [ ] **Task:** Create `datasets/demo/constituency_geo.json` — a GeoJSON FeatureCollection with 5 point features, one per ward. Each feature: `{"type":"Feature","geometry":{"type":"Point","coordinates":[lon,lat]},"properties":{"ward":"Ward N","name":"Ward Name"}}`. Use real-ish coordinates for a city (e.g., Lucknow, UP).
  - **Owner:** M4
  - **Dependencies:** 4.3
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Valid GeoJSON (paste into geojson.io to verify). 5 point features. Coordinates are plausible (not 0,0).

### 9.5 Create Dataset Loader Script
- [ ] **Task:** Create `scripts/load_demo_data.py`. On run: reads all four dataset files, inserts projects into SQLite `projects` table, adds all citizen requests as documents into ChromaDB `demo_documents`.
  - **Owner:** M4
  - **Dependencies:** 7.8, 8.3, 9.1, 9.2, 9.3, 9.4
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Running `python scripts/load_demo_data.py` prints "Loaded N projects" and "Loaded N documents". SQLite `projects` table has 8 rows. ChromaDB collection has 20+ documents. Script is idempotent (safe to run twice).

**Section 9 — Definition of Done:**
- [ ] All four dataset files exist and contain valid JSON
- [ ] Loader script runs without errors
- [ ] After loader runs: 8 projects in SQLite, 20+ docs in ChromaDB
- [ ] Loader is idempotent

---

# SECTION 10 — Shared JSON Models

**Priority:** P0 | **Day:** 1 | **Owner:** TL + M3

---

### 10.1 Create Pydantic Schema: SubmissionRequest
- [ ] **Task:** In `backend/app/schemas/submission.py`, define:
  ```python
  class SubmissionRequest(BaseModel):
      text: str
      location_hint: Optional[str] = None
  ```
  - **Owner:** M3
  - **Dependencies:** 5.5
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Class imports without error. Instantiating with `text="test"` works. Instantiating without `text` raises a validation error.

### 10.2 Create Pydantic Schema: ParsedIssue
- [ ] **Task:** In `backend/app/schemas/submission.py`, add:
  ```python
  class ParsedIssue(BaseModel):
      category: str
      urgency: str
      location: str
      summary: str
      confidence: float
  ```
  - **Owner:** M3
  - **Dependencies:** 10.1
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** Class imports. All fields are typed. `confidence` rejects non-float.

### 10.3 Create Pydantic Schema: Recommendation
- [ ] **Task:** In `backend/app/schemas/recommendation.py`, define:
  ```python
  class Recommendation(BaseModel):
      project_id: str
      priority_score: float
      confidence: float
      reason: str
      evidence: List[str]
  ```
  - **Owner:** M3
  - **Dependencies:** 5.5
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Class imports. `evidence` is a list of strings. Instantiation with valid data works.

### 10.4 Create Pydantic Schema: DashboardData
- [ ] **Task:** In `backend/app/schemas/dashboard.py`, define:
  ```python
  class HeatmapPoint(BaseModel):
      ward: str
      lat: float
      lon: float
      intensity: int

  class ProjectCard(BaseModel):
      id: str
      title: str
      category: str
      priority_score: float
      confidence: float
      reason: str
      evidence: List[str]

  class DashboardData(BaseModel):
      projects: List[ProjectCard]
      heatmap: List[HeatmapPoint]
      total_submissions: int
      last_updated: str
  ```
  - **Owner:** M3
  - **Dependencies:** 10.3
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** All classes import. `DashboardData` can be instantiated and serialized to JSON.

### 10.5 Create Pydantic Schema: LangGraphState
- [ ] **Task:** In `backend/app/schemas/state.py`, define:
  ```python
  class LangGraphState(TypedDict):
      submission_id: str
      input_type: str
      raw_text: str
      parsed_issue: Optional[dict]
      cluster: Optional[dict]
      knowledge_context: Optional[dict]
      recommendation: Optional[dict]
      explanation: Optional[dict]
      error: Optional[str]
  ```
  - **Owner:** TL
  - **Dependencies:** 5.5
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Class imports from `typing_extensions`. Can be used as LangGraph state annotation.

**Section 10 — Definition of Done:**
- [ ] All five Pydantic schemas exist and import without error
- [ ] All schemas match the JSON contracts in the spec
- [ ] `LangGraphState` is a valid `TypedDict`

---

# SECTION 11 — API Contracts

**Priority:** P0 | **Day:** 1 | **Owner:** M3 + TL

---

### 11.1 Document API Contract: POST /api/submissions
- [ ] **Task:** In `docs/API_CONTRACTS.md`, write the full contract for `POST /api/submissions`:
  - Request body: `SubmissionRequest`
  - Response: `{"submission_id": str, "status": "processing"}`
  - Error cases: 422 (invalid body), 500 (agent failure)
  - **Owner:** M3
  - **Dependencies:** 10.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Contract doc exists. M2 confirms they can implement the frontend call from it without asking questions.

### 11.2 Document API Contract: GET /api/submissions/{id}
- [ ] **Task:** In `docs/API_CONTRACTS.md`, write the contract for `GET /api/submissions/{submission_id}`:
  - Response: full submission row + `parsed_issue` + `recommendation`
  - Error: 404 if not found
  - **Owner:** M3
  - **Dependencies:** 11.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Contract doc updated. Frontend can implement polling from it.

### 11.3 Document API Contract: GET /api/dashboard
- [ ] **Task:** In `docs/API_CONTRACTS.md`, write the contract for `GET /api/dashboard`:
  - Response: `DashboardData` schema
  - No request parameters required
  - **Owner:** M3
  - **Dependencies:** 11.1, 10.4
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Contract doc updated. M2 confirms they can build the dashboard data-fetching layer from it.

### 11.4 Team Contract Review
- [ ] **Task:** TL, M2, M3, M4 all read `docs/API_CONTRACTS.md` and sign off. Any disagreement resolved before Day 2 begins.
  - **Owner:** TL
  - **Dependencies:** 11.1 – 11.3
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** All four members have read the contracts. Any open questions are resolved and documented in the file.

**Section 11 — Definition of Done:**
- [ ] `docs/API_CONTRACTS.md` has all three endpoint contracts
- [ ] All team members have reviewed and agreed on the contracts
- [ ] No ambiguity about request/response shapes

---

# SECTION 12 — FastAPI Endpoints

**Priority:** P0 | **Day:** 2 | **Owner:** M3

---

### 12.1 Create Submissions Router
- [ ] **Task:** Create `backend/app/api/submissions.py`. Create an `APIRouter` with prefix `/api/submissions`. Import `SubmissionRequest`. Stub out the `POST /` and `GET /{id}` routes returning placeholder data.
  - **Owner:** M3
  - **Dependencies:** 10.1, 10.2, 5.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Both routes appear in Swagger UI. `POST /api/submissions` accepts a JSON body. `GET /api/submissions/test` returns placeholder JSON.

### 12.2 Implement POST /api/submissions
- [ ] **Task:** In the POST route: validate request body, generate a UUID `submission_id`, call the LangGraph workflow (stub at this stage), save the submission to SQLite, return `{"submission_id": ..., "status": "processing"}`.
  - **Owner:** M3
  - **Dependencies:** 12.1, 7.8, 13.1
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Sending `{"text": "broken roads", "location_hint": "Ward 1"}` returns HTTP 200 with a `submission_id`. A row appears in the `submissions` table.

### 12.3 Implement GET /api/submissions/{id}
- [ ] **Task:** Fetch the submission from SQLite by ID. If not found, raise `HTTPException(404)`. Return the full submission row.
  - **Owner:** M3
  - **Dependencies:** 12.2, 7.8
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** After a POST, `GET /api/submissions/{returned_id}` returns the submission data. A fake ID returns HTTP 404.

### 12.4 Create Dashboard Router
- [ ] **Task:** Create `backend/app/api/dashboard.py`. Create an `APIRouter` with prefix `/api`. Implement `GET /dashboard` that calls `get_ranked_projects()`, builds heatmap data from `infrastructure_context.json` + cluster sizes, and returns `DashboardData`.
  - **Owner:** M3
  - **Dependencies:** 10.4, 7.8, 9.3
  - **Estimated Time:** 35 min
  - **Acceptance Criteria:** `GET /api/dashboard` returns HTTP 200 with a valid `DashboardData` JSON body. `projects` is a non-empty list if the demo data has been loaded. `heatmap` has 5 points.

### 12.5 Register All Routers in main.py
- [ ] **Task:** In `main.py`, import and include the submissions router and dashboard router using `app.include_router(...)`.
  - **Owner:** M3
  - **Dependencies:** 5.1, 12.1, 12.4
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** Swagger UI shows all routes: `/health`, `/api/submissions`, `/api/submissions/{id}`, `/api/dashboard`.

### 12.6 Add Request Logging Middleware
- [ ] **Task:** Add a simple middleware to `main.py` that logs `METHOD /path → status_code` for every request using Python's `logging` module.
  - **Owner:** M3
  - **Dependencies:** 5.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Every API call prints a log line to the terminal. Format: `INFO: POST /api/submissions → 200`.

**Section 12 — Definition of Done:**
- [ ] All three API endpoints are implemented and return correct data
- [ ] Swagger UI shows all routes
- [ ] POST creates a SQLite row
- [ ] GET /dashboard returns real projects from DB
- [ ] 404 is returned for unknown submission IDs

---

# SECTION 13 — LangGraph Setup

**Priority:** P0 | **Day:** 2 | **Owner:** TL

---

### 13.1 Create LangGraph Workflow Module
- [ ] **Task:** Create `backend/app/agents/workflow.py`. Import `StateGraph` from `langgraph`. Define the graph using `LangGraphState` as the state type. Import placeholder node functions (stubs).
  - **Owner:** TL
  - **Dependencies:** 10.5, 2.3
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** Module imports without error. `StateGraph` is instantiated without exceptions.

### 13.2 Define Graph Nodes (Stubs)
- [ ] **Task:** In `workflow.py`, add stub functions for all nodes. Each returns state unchanged with a print statement:
  - **P0:** `supervisor_node`, `citizen_intelligence_node`, `demand_intelligence_node`, `knowledge_fusion_node`, `policy_recommendation_node`, `explainability_node`
  - **P2:** `speech_processing_node`, `vision_processing_node` (stubs only — do not implement until P0 is complete)
  - **Owner:** TL
  - **Dependencies:** 13.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** All P0 nodes added via `graph.add_node(...)`. No import errors.

### 13.3 Define Graph Edges
- [ ] **Task:** Wire the graph edges in `workflow.py`. The supervisor fires **once** via a single conditional edge. All downstream edges are static — no further routing:
  ```python
  # One conditional edge — the only routing decision in the entire graph
  def route_fn(state):
      return state["route"]  # set by supervisor_node

  graph.add_conditional_edges("supervisor", route_fn, {
      "citizen_intelligence": "citizen_intelligence",
      "speech_processing":    "speech_processing",     # P2
      "vision_processing":    "vision_processing",      # P2
      "demand_intelligence":  "demand_intelligence",    # dashboard_refresh path
  })

  # Fixed pipeline — no decisions, no supervisor re-involvement
  graph.add_edge(START,                  "supervisor")
  graph.add_edge("speech_processing",    "citizen_intelligence")   # P2
  graph.add_edge("vision_processing",    "citizen_intelligence")   # P2
  graph.add_edge("citizen_intelligence", "demand_intelligence")
  graph.add_edge("demand_intelligence",  "knowledge_fusion")
  graph.add_edge("knowledge_fusion",     "policy_recommendation")
  graph.add_edge("policy_recommendation","explainability")
  graph.add_edge("explainability",        END)
  ```
  - **Owner:** TL
  - **Dependencies:** 13.2
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** `graph.compile()` executes without errors. Text path visits 6 nodes (supervisor + 5 pipeline). Dashboard refresh path visits 5 nodes (supervisor + 4 pipeline, skips citizen).

### 13.4 Create run_workflow Function
- [ ] **Task:** In `workflow.py`, implement `run_workflow(submission_id, input_type, raw_text) -> dict` that initializes the state, invokes the compiled graph, and returns the final state.
  - **Owner:** TL
  - **Dependencies:** 13.3
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** Calling `run_workflow("sub_001", "text", "broken roads")` returns a dict with all state keys. All stub nodes execute (visible via print statements).

### 13.5 Integrate run_workflow into POST /api/submissions
- [ ] **Task:** Replace the stub call in `POST /api/submissions` with:
  ```python
  state = run_workflow(submission_id, input_type, raw_text)

  # All persistence happens HERE in the service layer — not inside agent nodes
  db.update_submission(submission_id, state["parsed_issue"])
  db.update_submission_cluster(submission_id, state["cluster"]["name"])
  db.upsert_cluster(state["cluster"])
  db.insert_recommendation(submission_id, state["recommendation"])
  db.update_project_score(state["recommendation"]["project_id"], state["recommendation"]["priority_score"])
  chroma.add_document(submission_id, state["parsed_issue"]["summary"], metadata)
  ```
  Wrap the entire block in try/except. On any exception return HTTP 500 `{"error": "agent_failure"}`.
  - **Owner:** TL + M3
  - **Dependencies:** 13.4, 12.2, 7.8, 8.3
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** POST triggers workflow. All six DB/Chroma writes execute after `run_workflow` returns. Agents themselves contain zero `db.*` or `chroma.*` calls. On exception, 500 is returned and no partial writes remain.

**Section 13 — Definition of Done:**
- [ ] LangGraph workflow compiles without errors
- [ ] All six nodes are wired in correct order
- [ ] `run_workflow()` is callable and returns state
- [ ] Workflow is integrated into the POST endpoint
- [ ] Exception handling prevents unhandled 500s

---

# SECTION 14 — Supervisor Agent

**Priority:** P0 | **Day:** 2 | **Owner:** TL

---

### 14.1 ~~Write supervisor_prompt.md~~ — REMOVED
> **Decision:** The supervisor is implemented as pure Python rule-based logic. No LLM call. Reason: each LLM call adds ~2–4s latency. The routing decision is deterministic (check `input_type` field) and does not require language understanding. Using an LLM here wastes budget and latency with zero quality gain.
> `prompts/supervisor_prompt.md` remains a placeholder — no content needed.

### 14.2 Implement Supervisor Node (Rule-Based, No LLM)
- [ ] **Task:** Replace the `supervisor_node` stub with a pure Python function:
  ```python
  def supervisor_node(state: LangGraphState) -> LangGraphState:
      t = state["input_type"]
      if t == "dashboard_refresh":
          state["route"] = "dashboard_refresh"
      else:
          state["route"] = "citizen_intelligence"
      return state
  ```
  Log execution time to `agent_logs`. No OpenAI call.
  - **Owner:** TL
  - **Dependencies:** 13.2, 7.8
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** `run_workflow(..., input_type="text", ...)` sets `state["route"] = "citizen_intelligence"`. `run_workflow(..., input_type="dashboard_refresh", ...)` sets route to `"dashboard_refresh"`. Execution time < 5ms (no network call).

### 14.3 Add Conditional Routing Edges
- [ ] **Task:** In `workflow.py`, replace the static `supervisor → citizen_intelligence` edge with a conditional edge:
  - `"citizen_intelligence"` route → `citizen_intelligence_node`
  - `"dashboard_refresh"` route → `demand_intelligence_node` (skips citizen intake; demand re-evaluates clusters from existing submissions, then continues through fusion → policy → explainability)
  - **Owner:** TL
  - **Dependencies:** 13.3, 14.2
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Graph compiles. Text submissions execute all 5 downstream nodes. Dashboard refresh submissions skip `citizen_intelligence` and start at `demand_intelligence`.

**Section 14 — Definition of Done:**
- [ ] Supervisor is pure Python — zero LLM calls
- [ ] `"text"` input routes to `citizen_intelligence`
- [ ] `"dashboard_refresh"` input routes to `demand_intelligence` (skips citizen intake)
- [ ] Execution time logged to `agent_logs`
- [ ] Conditional edge compiles and routes correctly

---

# SECTION 15 — Citizen Intelligence Agent

**Priority:** P0 | **Day:** 2 | **Owner:** TL

---

### 15.1 Write citizen_prompt.md
- [ ] **Task:** Write `prompts/citizen_prompt.md`. Prompt instructs the LLM to extract from citizen text: `category` (one of: roads, water, electricity, health, other), `urgency` (low/medium/high), `location` (from text or use `location_hint`), `summary` (one sentence), `confidence` (0.0–1.0). Must return valid JSON only.
  - **Owner:** TL
  - **Dependencies:** 4.4
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** Prompt tested manually. Returns valid JSON for: "Roads are broken near the school in Ward 12". Returns valid JSON for a vague input with low confidence.

### 15.2 Implement Citizen Intelligence Node
- [ ] **Task:** Replace the `citizen_intelligence_node` stub. Load `citizen_prompt.md`. Call OpenAI with `raw_text` and `location_hint`. Parse response into `ParsedIssue`. Update `state["parsed_issue"]` only. **No DB writes inside this node** — persistence happens in the FastAPI layer after `run_workflow()` returns (Section 13.5).
  - **Owner:** TL
  - **Dependencies:** 15.1, 13.2, 10.2
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** After running the workflow, `state["parsed_issue"]` is a populated dict with all five fields. Zero `db.*` calls inside this function.

### 15.3 Add Fallback for Missing Location
- [ ] **Task:** In the citizen intelligence node, if `location` in the parsed output is empty or null, set it to `location_hint` from the state. If `location_hint` is also empty, set it to `"Constituency"` as the default.
  - **Owner:** TL
  - **Dependencies:** 15.2
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Submitting text with no location and no location hint results in `location = "Constituency"` in `parsed_issue`. No KeyError.

**Section 15 — Definition of Done:**
- [ ] Citizen prompt returns valid JSON
- [ ] Node updates `state["parsed_issue"]` only — no DB writes
- [ ] Location fallback handles all edge cases

---

# SECTION 16 — Demand Intelligence Agent

**Priority:** P0 | **Day:** 2 | **Owner:** TL + M4

---

### 16.1 Write demand_prompt.md
- [ ] **Task:** Write `prompts/demand_prompt.md`. Prompt instructs the LLM to: given a list of similar submissions (from ChromaDB results), identify the cluster name and hotspot. Return: `{"cluster_name": str, "cluster_size": int, "hotspot": str}`.
  - **Owner:** TL
  - **Dependencies:** 4.4
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Prompt tested manually with 3 similar road submissions. Returns sensible cluster name like "Road Infrastructure Demand".

### 16.2 Implement Demand Intelligence Node
- [ ] **Task:** Replace the `demand_intelligence_node` stub. Call `query_similar(parsed_issue["summary"])` to get top 3 similar submissions. Call OpenAI with the similar texts to identify the cluster. Update `state["cluster"]` only. **No DB or ChromaDB writes inside this node** — those happen in 13.5.
  - **Owner:** TL + M4
  - **Dependencies:** 16.1, 8.4, 13.2
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** `state["cluster"]` is populated after the node runs. ChromaDB query returns at least 1 result when demo data is loaded. Zero `db.*` or `chroma.*` calls inside this function.

**Section 16 — Definition of Done:**
- [ ] Demand prompt returns valid cluster JSON
- [ ] Node runs ChromaDB query and LLM call
- [ ] `state["cluster"]` is populated — no DB writes inside the node

---

# SECTION 17 — Knowledge Fusion Agent

**Priority:** P0 | **Day:** 2 | **Owner:** TL + M4

---

### 17.1 Write fusion_prompt.md
- [ ] **Task:** Write `prompts/fusion_prompt.md`. Prompt instructs the LLM to: given the parsed issue and the static infrastructure context for the relevant ward, output: `{"population": int, "infrastructure_gap": str, "proposal_context": str}`. Return JSON only.
  - **Owner:** TL
  - **Dependencies:** 4.4
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Prompt tested manually with Ward 1 context and a roads issue. Returns sensible output.

### 17.2 Create Knowledge Lookup Helper
- [ ] **Task:** In `backend/app/services/knowledge_service.py`, implement `get_ward_context(ward_name: str) -> dict` that loads `infrastructure_context.json` and returns the matching ward dict. Returns a default empty dict if the ward is not found.
  - **Owner:** M4
  - **Dependencies:** 9.3
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** `get_ward_context("Ward 1")` returns the correct dict. `get_ward_context("Unknown")` returns `{}` without error.

### 17.3 Implement Knowledge Fusion Node
- [ ] **Task:** Replace the `knowledge_fusion_node` stub. Call `get_ward_context(parsed_issue["location"])`. Call OpenAI with the context and the parsed issue. Update `state["knowledge_context"]` with the LLM output.
  - **Owner:** TL + M4
  - **Dependencies:** 17.1, 17.2, 13.2
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** `state["knowledge_context"]` is populated. `infrastructure_gap` is a readable string. No crash when ward is not found.

**Section 17 — Definition of Done:**
- [ ] Fusion prompt returns valid JSON
- [ ] `get_ward_context` handles all ward names + unknown fallback
- [ ] State is updated with knowledge context

---

# SECTION 18 — Policy Recommendation Agent

**Priority:** P0 | **Day:** 2–3 | **Owner:** TL + M4

---

### 18.1 Write policy_prompt.md
- [ ] **Task:** Write `prompts/policy_prompt.md`. Prompt provides the deterministic score to the LLM and instructs it to return: `{"project_id": str, "priority_score": float, "confidence": float, "reason": str}`. The score is computed in code — the LLM only explains it.
  - **Owner:** TL
  - **Dependencies:** 4.4
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Prompt clearly communicates that the score is fixed. LLM only writes the `reason` field. Tested manually.

### 18.2 Implement Deterministic Scoring Function
- [ ] **Task:** In `backend/app/services/scoring_service.py`, implement `compute_priority_score(citizen_demand, infrastructure_gap, population_impact, cost_feasibility) -> float`. Use the spec's four-component formula with fixed weights:
  ```python
  score = (0.40 * citizen_demand) + (0.30 * infrastructure_gap) + (0.20 * population_impact) + (0.10 * cost_feasibility)
  return min(score, 1.0)
  ```
  All four inputs are normalized floats (0.0–1.0) before being passed in. Caller is responsible for normalization:
  - `citizen_demand`: `min(cluster_size / 10, 1.0)`
  - `infrastructure_gap`: from `infrastructure_context.json` for the ward (e.g., `1 - road_coverage_pct`)
  - `population_impact`: `min(ward_population / 15000, 1.0)` (15000 = max demo ward population)
  - `cost_feasibility`: `1 - min(estimated_cost / 5000000, 1.0)` (lower cost = higher feasibility)
  - **Owner:** M4
  - **Dependencies:** 4.1
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Same inputs always return the same output. Score never exceeds 1.0. High cluster + poor infrastructure + large population + low cost produces score > 0.7.

### 18.3 Implement Policy Recommendation Node
- [ ] **Task:** Replace the `policy_recommendation_node` stub. Read `get_all_projects()` from SQLite (read-only — no write). For each project, compute `priority_score` using normalized inputs from `state["cluster"]`, `state["knowledge_context"]`, and the project's own data. Select the top-scoring project. Update `state["recommendation"]` with `project_id`, `priority_score`, `confidence`. **No DB writes inside this node** — persistence happens in 13.5. No LLM call.
  - **Owner:** TL + M4
  - **Dependencies:** 18.1, 18.2, 7.8, 13.2
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** `state["recommendation"]` has `project_id`, `priority_score`, `confidence`. Score matches `compute_priority_score` output. Zero `db.*` write calls inside this function. No OpenAI call occurs in this node.

**Section 18 — Definition of Done:**
- [ ] Scoring function is deterministic, uses spec's 4-component formula, capped at 1.0
- [ ] Policy node selects top project using score only — no LLM, no DB writes
- [ ] `state["recommendation"]` is populated with score + confidence

---

# SECTION 19 — Explainability Agent

**Priority:** P0 | **Day:** 3 | **Owner:** TL

---

### 19.1 Write explainability_prompt.md
- [ ] **Task:** Write `prompts/explainability_prompt.md`. Prompt instructs the LLM to: given the recommendation, cluster, and knowledge context, generate exactly 3 evidence bullets and one short summary sentence. Return JSON: `{"evidence": [str, str, str], "summary": str}`.
  - **Owner:** TL
  - **Dependencies:** 4.4
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Tested manually. Returns exactly 3 bullets. Bullets are factual (referencing cluster size, ward data, project cost). Summary is one sentence.

### 19.2 Implement Explainability Node
- [ ] **Task:** Replace the `explainability_node` stub. Call OpenAI with the full recommendation context (project, cluster, knowledge context, score). Parse the response. Update `state["explanation"]` with `evidence` and `summary`. **Zero DB writes inside this node.** All persistence (including `update_project_score`) happens in the FastAPI layer (Section 13.5) after `run_workflow()` returns.
  - **Owner:** TL
  - **Dependencies:** 19.1, 13.2
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** `state["explanation"]["evidence"]` is a list of 3 strings. `state["explanation"]["summary"]` is a non-empty string. Zero `db.*` calls inside this function.

### 19.3 Create On-Demand Explainability Endpoint
- [ ] **Task:** Add `GET /api/explain/{project_id}` to the dashboard router. Fetches the project + its latest recommendation row from SQLite. Calls a standalone `explain(project, recommendation) -> dict` helper (not the full workflow) using `explainability_prompt.md`. Returns `{"evidence": [...], "summary": str, "reason": str}`. Called only when the user clicks a project card — never on dashboard load.
  - **Owner:** M3 + TL
  - **Dependencies:** 19.2, 12.4, 7.8
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** `GET /api/explain/proj_001` returns valid JSON with `evidence` and `summary`. Response time < 5s. Dashboard page does not call this endpoint automatically on load.

**Section 19 — Definition of Done:**
- [ ] Explainability node updates `state["explanation"]` only — zero DB writes inside the node
- [ ] On-demand `/api/explain/{project_id}` endpoint returns evidence + summary + reason
- [ ] Full pipeline runs end-to-end with zero DB side-effects inside any agent node

---

# SECTION 20 — Prompt Files

**Priority:** P0 | **Day:** 2–3 | **Owner:** TL

---

### 20.1 Finalize All Six Prompt Files
- [ ] **Task:** Review all six prompts after the agent nodes are implemented. Ensure each prompt: returns only JSON when JSON is required, has a clear role statement, handles edge cases (vague location, unknown category), uses a consistent tone.
  - **Owner:** TL
  - **Dependencies:** 14.1, 15.1, 16.1, 17.1, 18.1, 19.1
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** All six prompts tested manually against the OpenAI API. Each returns valid, parseable JSON. No prompt returns markdown fences around JSON.

### 20.2 Add JSON Parsing Safety to All Nodes
- [ ] **Task:** Wrap all LLM JSON parsing in try/except in every agent node. On parse failure, log the raw response and return a sensible fallback dict.
  - **Owner:** TL
  - **Dependencies:** 20.1
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** Deliberately providing a bad prompt causes the node to log the error and continue with fallback values instead of crashing.

### 20.3 Add Prompt Loading Utility
- [ ] **Task:** Create `backend/app/services/prompt_loader.py` with `load_prompt(filename: str) -> str` that reads from the `prompts/` directory. Caches the content in memory on first load.
  - **Owner:** TL
  - **Dependencies:** 4.4
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** `load_prompt("citizen_prompt.md")` returns the full file content. Second call returns the cached version without disk I/O.

**Section 20 — Definition of Done:**
- [ ] All six prompts finalized and tested manually
- [ ] All agent nodes have JSON parse error handling
- [ ] Prompt loader utility is used by all nodes

---

# SECTION 21 — Frontend Components

**Priority:** P0 | **Day:** 2–3 | **Owner:** M2

---

### 21.1 Create LoadingSpinner Component
- [ ] **Task:** Create `frontend/src/components/LoadingSpinner.tsx`. A simple animated spinner using Tailwind's `animate-spin`. Accepts an optional `label` prop.
  - **Owner:** M2
  - **Dependencies:** 6.1, 2.7
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Component renders visually. `<LoadingSpinner label="Processing..." />` shows spinner and text. No TypeScript errors.

### 21.2 Create StatusBadge Component
- [ ] **Task:** Create `frontend/src/components/StatusBadge.tsx`. Accepts `status: "processing" | "complete" | "error"`. Renders a colored badge: processing=yellow, complete=green, error=red.
  - **Owner:** M2
  - **Dependencies:** 6.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** All three states render with correct colors.

### 21.3 Create UrgencyBadge Component
- [ ] **Task:** Create `frontend/src/components/UrgencyBadge.tsx`. Accepts `urgency: "low" | "medium" | "high"`. Renders a colored label badge.
  - **Owner:** M2
  - **Dependencies:** 6.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Three urgency levels render with distinct colors.

### 21.4 Create CategoryIcon Component
- [ ] **Task:** Create `frontend/src/components/CategoryIcon.tsx`. Maps categories (`roads`, `water`, `electricity`, `health`, `other`) to emoji or simple SVG icon with a label.
  - **Owner:** M2
  - **Dependencies:** 6.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Each of the 5 categories renders a distinct visual. Unknown category falls back to a generic icon.

**Section 21 — Definition of Done:**
- [ ] All four shared components render correctly
- [ ] No TypeScript errors
- [ ] Components are usable in chat and dashboard pages

---

# SECTION 22 — Citizen Chat UI

**Priority:** P0 | **Day:** 3 | **Owner:** M2

---

### 22.1 Create ChatPage Layout
- [ ] **Task:** Create `frontend/src/pages/ChatPage.tsx`. Full-page layout: title "Submit a Development Request", a message thread area, an input area at the bottom. Use Tailwind for layout (flex column, scroll on messages area).
  - **Owner:** M2
  - **Dependencies:** 6.2, 6.5
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** Page renders at `/`. Layout fills the screen height. Input box is at the bottom.

### 22.2 Create ChatMessage Component
- [ ] **Task:** Create `frontend/src/components/ChatMessage.tsx`. Accepts `role: "user" | "system"`, `text: string`. User messages are right-aligned with a blue bubble. System messages are left-aligned with a gray bubble.
  - **Owner:** M2
  - **Dependencies:** 22.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** User and system messages render with correct alignment and colors. Long text wraps correctly.

### 22.3 Implement Chat State Management
- [ ] **Task:** In `ChatPage.tsx`, manage state: `messages: ChatMessage[]`, `inputText: string`, `isLoading: boolean`, `submissionId: string | null`. Handle the user typing and pressing Enter or clicking Send.
  - **Owner:** M2
  - **Dependencies:** 22.2
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** Typing in the input and pressing Enter appends a user message to the thread. Input clears after send. Loading state prevents double-submit.

### 22.4 Wire Chat to API: Submit Request
- [ ] **Task:** When user submits text, call `submitRequest(text, locationHint)` from the API service. Append a system "processing" message. Set `submissionId` on success. Handle network errors with a system error message.
  - **Owner:** M2
  - **Dependencies:** 22.3, 6.3
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Submitting "broken roads in Ward 1" calls `POST /api/submissions` and displays a processing message. Network error shows "Something went wrong" message.

### 22.5 Implement Submission Result Polling
- [ ] **Task:** After getting a `submissionId`, poll `GET /api/submissions/{id}` every 2 seconds for up to 30 seconds. When the result has `parsed_issue` populated, stop polling and display the result card.
  - **Owner:** M2
  - **Dependencies:** 22.4, 6.3
  - **Estimated Time:** 35 min
  - **Acceptance Criteria:** After submitting, the chat shows a loading indicator. When the agent pipeline completes, the result appears automatically. Polling stops after the result arrives.

### 22.6 Create Parsed Issue Result Card
- [ ] **Task:** Create `frontend/src/components/ParsedIssueCard.tsx`. Displays the result of the citizen agent: category (with icon), urgency (with badge), location, summary, confidence as a percentage.
  - **Owner:** M2
  - **Dependencies:** 21.3, 21.4, 22.5
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** Card displays all five fields. Confidence shows as "90% confidence". No TypeScript errors.

### 22.7 Add Location Hint Input
- [ ] **Task:** Add an optional "Location (Ward)" text field below the main chat input. Value is passed as `location_hint` on submission.
  - **Owner:** M2
  - **Dependencies:** 22.3
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Location field appears below chat input. Value is included in API call. Field is optional — blank location works.

**Section 22 — Definition of Done:**
- [ ] Chat page renders and accepts text input
- [ ] Submission calls API and shows processing state
- [ ] Polling detects completion and shows result card
- [ ] Error states are handled and displayed
- [ ] Location hint is included in submission

---

# SECTION 23 — Dashboard UI

**Priority:** P0 | **Day:** 3 | **Owner:** M2

---

### 23.1 Create DashboardPage Layout
- [ ] **Task:** Create `frontend/src/pages/DashboardPage.tsx`. Layout: header bar with title "MP Constituency Dashboard", left panel (40%) for project list, right panel (60%) for heatmap + evidence. Use CSS Grid or Tailwind flex.
  - **Owner:** M2
  - **Dependencies:** 6.2, 6.5
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Page renders at `/dashboard`. Two-column layout is visible. Placeholder content fills both panels. Layout is responsive above 768px wide.

### 23.2 Wire Dashboard to API
- [ ] **Task:** In `DashboardPage.tsx`, call `getDashboard()` on mount. Store result in state. Show a `LoadingSpinner` while loading. Show an error message on failure.
  - **Owner:** M2
  - **Dependencies:** 23.1, 6.3
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Dashboard loads data from `GET /api/dashboard`. Loading spinner shows then disappears. Project list renders with real project titles.

### 23.3 Add Dashboard Auto-Refresh
- [ ] **Task:** In `DashboardPage.tsx`, set up a `setInterval` to call `getDashboard()` every 10 seconds. Clear interval on component unmount.
  - **Owner:** M2
  - **Dependencies:** 23.2
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Submitting a new citizen request and waiting 10 seconds causes the dashboard to reflect the new data without a page refresh.

**Section 23 — Definition of Done:**
- [ ] Dashboard page renders in two-column layout
- [ ] Real data loads from API on mount
- [ ] Auto-refresh updates data every 10 seconds
- [ ] Loading and error states are handled

---

# SECTION 24 — Heatmap

**Priority:** P0 | **Day:** 3 | **Owner:** M2

---

### 24.1 Create HeatmapPanel Component
- [ ] **Task:** Create `frontend/src/components/HeatmapPanel.tsx`. Uses `Leaflet` (react-leaflet) to render a map centered on the constituency. Accepts `heatmap: HeatmapPoint[]` as props.
  - **Owner:** M2
  - **Dependencies:** 2.6, 10.4, 23.1
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** A Leaflet map renders in the right panel of the dashboard. Map tiles load. No console errors about missing CSS.

### 24.2 Render Ward Markers with Intensity
- [ ] **Task:** For each `HeatmapPoint` in props, add a `CircleMarker` to the map. Radius and fill color should scale with `intensity`: low=green, medium=yellow, high=red.
  - **Owner:** M2
  - **Dependencies:** 24.1
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** 5 markers appear on the map, one per ward. Color varies by intensity. Marker radius is visually distinct.

### 24.3 Add Tooltip on Marker Hover
- [ ] **Task:** Each marker has a Leaflet `Tooltip` showing the ward name and intensity count on hover.
  - **Owner:** M2
  - **Dependencies:** 24.2
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Hovering a marker shows a tooltip with "Ward N — X submissions". No crash on hover.

**Section 24 — Definition of Done:**
- [ ] Leaflet map renders with 5 ward markers
- [ ] Marker colors reflect intensity
- [ ] Tooltips show on hover
- [ ] Heatmap uses real data from `GET /api/dashboard`

---

# SECTION 25 — Recommendation Cards

**Priority:** P0 | **Day:** 3 | **Owner:** M2

---

### 25.1 Create ProjectCard Component
- [ ] **Task:** Create `frontend/src/components/ProjectCard.tsx`. Displays: project title, category icon, priority score as a progress bar (0–100%), confidence badge, one-line summary. Accepts `onClick` prop to select the project.
  - **Owner:** M2
  - **Dependencies:** 21.4, 10.4
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Card renders correctly. Progress bar width matches priority score. Click handler fires. Selected card has a highlighted border.

### 25.2 Create ProjectList Component
- [ ] **Task:** Create `frontend/src/components/ProjectList.tsx`. Renders a scrollable list of `ProjectCard` components sorted by `priority_score` descending. Accepts `projects: ProjectCard[]` and `selectedId: string`.
  - **Owner:** M2
  - **Dependencies:** 25.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** List renders up to 8 projects. Highest-scored project is at the top. Selected project card has a visible highlight.

### 25.3 Add Score Bar Chart (Optional Enhancement)
- [ ] **Task:** In the dashboard header area, add a small horizontal bar chart using Recharts showing the top 5 projects by priority score.
  - **Owner:** M2
  - **Dependencies:** 23.2, 2.6
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** Bar chart renders with correct values. Labels show project titles (truncated). **P1 — skip if behind schedule.**

**Section 25 — Definition of Done:**
- [ ] Project cards render with correct data
- [ ] List is sorted by priority score
- [ ] Selected card is visually highlighted
- [ ] Click on card updates selected project

---

# SECTION 26 — Evidence Cards

**Priority:** P0 | **Day:** 3 | **Owner:** M2

---

### 26.1 Create EvidencePanel Component
- [ ] **Task:** Create `frontend/src/components/EvidencePanel.tsx`. Has two states: (1) `loading` — shows a spinner with "Generating explanation…", (2) `loaded` — shows project title, reason paragraph, 3 evidence bullets with checkmark icons, confidence badge. Accepts `projectId: string | null` as prop. When `projectId` changes, calls `GET /api/explain/{projectId}` to fetch fresh evidence.
  - **Owner:** M2
  - **Dependencies:** 25.1, 19.4
  - **Estimated Time:** 35 min
  - **Acceptance Criteria:** Panel shows spinner while fetching. Evidence renders after response. Confidence shows as "X% confidence". Re-fetches when a new project is selected.

### 26.2 Wire Evidence Panel to Selected Project
- [ ] **Task:** In `DashboardPage.tsx`, track `selectedProjectId: string | null` state. Default to the top-ranked project's ID on load. When a `ProjectCard` is clicked, update `selectedProjectId`. Pass `selectedProjectId` to `EvidencePanel` which triggers the `/api/explain` fetch.
  - **Owner:** M2
  - **Dependencies:** 26.1, 25.2
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** On dashboard load, the top project's explanation auto-fetches. Clicking a different project fetches its explanation. Loading spinner shows during fetch.

### 26.3 Add Cluster Demand Summary
- [ ] **Task:** Below the evidence panel, add a small section showing the cluster name, cluster size, and hotspot. Source this from the `demand_summary` field in the `GET /api/dashboard` response (already loaded — no extra fetch needed).
  - **Owner:** M2
  - **Dependencies:** 26.2, 27.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Cluster info renders below evidence. Shows "N similar requests" and the hotspot ward.

**Section 26 — Definition of Done:**
- [ ] Evidence panel fetches explanation on-demand from `/api/explain/{id}` — NOT from dashboard response
- [ ] Loading spinner shows while fetching explanation
- [ ] Panel updates when a new project is selected
- [ ] Default selection auto-fetches the top-ranked project's explanation
- [ ] Cluster summary uses dashboard response data (no extra call)

---

# SECTION 27 — Backend Integration

**Priority:** P0 | **Day:** 3 | **Owner:** M3 + M4

---

### 27.1 Update GET /api/dashboard to Include Cluster Data
- [ ] **Task:** Modify the dashboard endpoint to query the `clusters` table and include a `demand_summary` object in the response: `{"top_cluster": str, "cluster_size": int, "hotspot": str}`.
  - **Owner:** M3
  - **Dependencies:** 12.4, 7.8
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** `GET /api/dashboard` response includes `demand_summary`. Fields are populated after the agent pipeline runs.

### 27.2 Update GET /api/submissions/{id} to Include Full Result
- [ ] **Task:** Modify the submissions endpoint to join and return: the submission row, its parsed issue fields, and the latest recommendation for that submission (from the `recommendations` table).
  - **Owner:** M3
  - **Dependencies:** 12.3, 7.8
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** After a full pipeline run, `GET /api/submissions/{id}` returns `submission`, `parsed_issue`, and `recommendation` as nested objects.

### 27.3 Compute Heatmap Intensity from Real Data
- [ ] **Task:** In the dashboard endpoint, count submissions per ward from the `submissions` table. Map ward name to coordinates from `constituency_geo.json`. Build the `HeatmapPoint` list with real submission counts as intensity.
  - **Owner:** M4
  - **Dependencies:** 12.4, 7.8, 9.4
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** After loading demo data and submitting 2+ requests for Ward 1, Ward 1's heatmap point has higher intensity than empty wards.

**Section 27 — Definition of Done:**
- [ ] Dashboard response includes cluster summary
- [ ] Submission GET includes parsed issue + recommendation
- [ ] Heatmap intensity reflects real submission counts

---

# SECTION 28 — Frontend Integration

**Priority:** P0 | **Day:** 3–4 | **Owner:** M2

---

### 28.1 Update API Service to Use Updated Response Shapes
- [ ] **Task:** Update `api.ts` to handle the updated `GET /api/submissions/{id}` response with nested `parsed_issue` and `recommendation`.
  - **Owner:** M2
  - **Dependencies:** 27.2, 6.3
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** `getSubmission(id)` returns a typed object with `submission`, `parsed_issue`, `recommendation` keys. TypeScript types match.

### 28.2 Display Recommendation in Chat After Processing
- [ ] **Task:** When polling detects the submission is complete and has a `recommendation`, append a second result card to the chat showing the recommended project title, score, and reason.
  - **Owner:** M2
  - **Dependencies:** 22.5, 28.1, 25.1
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** After submission completes, the chat shows: (1) the parsed issue card, (2) a recommendation card with project title and reason.

### 28.3 Add "View on Dashboard" Button
- [ ] **Task:** In the recommendation card in the chat, add a "View on Dashboard →" button that navigates to `/dashboard`.
  - **Owner:** M2
  - **Dependencies:** 28.2
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** Button is visible and navigates to `/dashboard` on click. Dashboard shows the updated ranking.

**Section 28 — Definition of Done:**
- [ ] Chat displays both parsed issue and recommendation
- [ ] Types are updated to match backend response
- [ ] Navigation to dashboard works from chat

---

# SECTION 29 — Database Integration

**Priority:** P0 | **Day:** 3 | **Owner:** M4

---

### 29.1 Run Loader Script as Part of App Startup
- [ ] **Task:** Modify app startup in `main.py` to call the dataset loader if the `projects` table is empty. This ensures demo data is available without a manual step.
  - **Owner:** M4
  - **Dependencies:** 9.5, 7.7
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Starting the app with an empty database automatically loads the demo data. Starting with existing data does not duplicate entries.

### 29.2 Test All DB Helper Functions End-to-End
- [ ] **Task:** Write a quick test script `tests/test_db.py` that: calls `insert_submission`, `get_submission`, `insert_recommendation`, `get_all_projects`, `get_ranked_projects` in sequence and asserts correct data.
  - **Owner:** M4
  - **Dependencies:** 7.8
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** `python tests/test_db.py` runs without errors and prints "All DB tests passed".

### 29.3 Verify Foreign Key Consistency
- [ ] **Task:** Ensure `recommendations` rows always reference valid `submission_id` and `project_id`. Add a check in `insert_recommendation` that both IDs exist before inserting.
  - **Owner:** M4
  - **Dependencies:** 7.8
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Calling `insert_recommendation` with a non-existent `project_id` raises a descriptive ValueError, not a SQLite constraint error.

**Section 29 — Definition of Done:**
- [ ] Demo data loads automatically on first startup
- [ ] All DB functions pass the test script
- [ ] Referential integrity is enforced in code

---

# SECTION 30 — Agent Integration

**Priority:** P0 | **Day:** 3–4 | **Owner:** TL

---

### 30.1 Run Full Pipeline with Demo Data
- [ ] **Task:** With demo data loaded, submit "water supply is poor near the health center in Ward 3" via the API. Trace the full state through all six agents. Verify each agent updates the state correctly.
  - **Owner:** TL
  - **Dependencies:** 13.5, 15.2, 16.2, 17.3, 18.3, 19.2
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** `state["parsed_issue"]`, `state["cluster"]`, `state["knowledge_context"]`, `state["recommendation"]`, `state["explanation"]` are all populated. No agent raises an unhandled exception.

### 30.2 Verify agent_logs Table Captures All Agents
- [ ] **Task:** After a full pipeline run, query `agent_logs`. Verify there are rows for all six agents with `status = "success"` and non-zero `execution_time_ms`.
  - **Owner:** TL
  - **Dependencies:** 30.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** `SELECT agent_name, status FROM agent_logs` shows all six agents with "success" status.

### 30.3 Test Pipeline with Missing Location
- [ ] **Task:** Submit a request with no `location_hint` and no location in the text. Verify the fallback kicks in and the pipeline completes with `location = "Constituency"`.
  - **Owner:** TL
  - **Dependencies:** 15.3, 30.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Pipeline completes without error. `state["parsed_issue"]["location"]` equals `"Constituency"`. A recommendation is still produced.

**Section 30 — Definition of Done:**
- [ ] Full pipeline runs end-to-end with demo data
- [ ] All six agent logs appear in DB
- [ ] Missing location fallback works correctly

---

# SECTION 31 — End-to-End Workflow

**Priority:** P0 | **Day:** 4 | **Owner:** All

---

### 31.1 Run Full Demo Path: Text → Dashboard
- [ ] **Task:** Starting from a clean DB (reload demo data), open the browser. Submit "roads are broken near the school in Ward 2". Wait for the chat to show the result. Navigate to the dashboard. Verify the project and heatmap updated.
  - **Owner:** All
  - **Dependencies:** 28.2, 23.2, 24.2, 30.1
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Chat shows parsed issue card with category=roads, urgency=high/medium, location=Ward 2. Chat shows recommendation card. Dashboard shows updated project ranking. Ward 2 marker is brighter. Total time under 20 seconds.

### 31.2 Run Repeat Submission to Test Clustering
- [ ] **Task:** Submit 3 more road-related requests in different wards. Verify cluster size increases and the roads project priority score increases.
  - **Owner:** All
  - **Dependencies:** 31.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** After 4 road submissions, the roads project is at the top of the dashboard. Cluster size in the demand summary shows 4+.

### 31.3 Test Dashboard Refresh Without New Submission
- [ ] **Task:** Wait 10 seconds on the dashboard without submitting. Verify no errors occur and the data remains stable.
  - **Owner:** M2
  - **Dependencies:** 23.3
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** No console errors during auto-refresh. Data does not change if no new submission was made.

**Section 31 — Definition of Done:**
- [ ] Full demo path completes in under 20 seconds
- [ ] Repeat submissions increase cluster size and update score
- [ ] Dashboard auto-refresh works without errors
- [ ] All agent logs show success

---

# SECTION 32 — Testing

**Priority:** P0 | **Day:** 4 | **Owner:** M3 + M4

---

### 32.1 Test Happy Path: Submission → Dashboard
- [ ] **Task:** Manually verify the core demo path 3 times with different inputs. Document any inconsistent behavior.
  - **Owner:** M3
  - **Dependencies:** 31.1
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** All 3 runs complete without error. Results are consistently structured (may vary in LLM text, but structure is always correct).

### 32.2 Test Fallback Path: Vague Input
- [ ] **Task:** Submit "there is a problem in my area". Verify the pipeline completes. Parsed issue should have low confidence and category="other". A recommendation is still produced.
  - **Owner:** M3
  - **Dependencies:** 30.3
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** No 500 error. `confidence < 0.5`. Dashboard still updates. Error states are not triggered.

### 32.3 Test Scoring Function Unit
- [ ] **Task:** In `tests/test_scoring.py`, write 5 test cases for `compute_priority_score`. Include: high urgency + big cluster, low urgency + small cluster, boundary (score exactly 1.0), score order (high urgency scores higher than low urgency with same cluster).
  - **Owner:** M4
  - **Dependencies:** 18.2
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** All 5 assertions pass. Score never exceeds 1.0. Higher urgency always produces higher score, all else equal.

### 32.4 Test API Endpoints with curl
- [ ] **Task:** Document and test all three endpoints using curl commands. Save the commands in `tests/api_test_commands.sh`.
  - **Owner:** M3
  - **Dependencies:** 12.5
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** All three curl commands return expected responses. Commands are documented in the test file.

### 32.5 Test Frontend Chat UI
- [ ] **Task:** Manually test the chat UI: (1) submit text, (2) check loading state shows, (3) check result card appears, (4) check recommendation card appears, (5) click "View on Dashboard".
  - **Owner:** M2
  - **Dependencies:** 28.3
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** All 5 steps complete without error. No console errors in browser dev tools.

**Section 32 — Definition of Done:**
- [ ] Happy path tested 3 times with consistent results
- [ ] Fallback path tested and handled gracefully
- [ ] Scoring unit tests pass
- [ ] API curl commands documented and working
- [ ] Chat UI manually tested

---

# SECTION 33 — Bug Fixes

**Priority:** P0 | **Day:** 4 | **Owner:** All

---

### 33.1 Fix Any 500 Errors in Full Pipeline Run
- [ ] **Task:** After running the full pipeline 5 times, document and fix any unhandled exceptions. Prioritize: JSON parse failures, missing state keys, ChromaDB empty collection errors.
  - **Owner:** TL + M3
  - **Dependencies:** 31.1
  - **Estimated Time:** 45 min
  - **Acceptance Criteria:** 5 consecutive pipeline runs produce no 500 errors.

### 33.2 Fix Any Frontend Console Errors
- [ ] **Task:** Open browser dev tools and run the full demo path. Fix all red console errors. Yellow warnings are acceptable if they do not affect functionality.
  - **Owner:** M2
  - **Dependencies:** 28.3
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Zero red errors in the browser console during the full demo path.

### 33.3 Fix Any TypeScript Build Errors
- [ ] **Task:** Run `npm run build` in the frontend. Fix all TypeScript errors until the build succeeds.
  - **Owner:** M2
  - **Dependencies:** 6.4
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** `npm run build` completes with exit code 0. No TypeScript errors in the output.

**Section 33 — Definition of Done:**
- [ ] 5 consecutive pipeline runs with no 500 errors
- [ ] Zero red console errors in browser
- [ ] Frontend build succeeds

---

# SECTION 34 — Performance Improvements

**Priority:** P1 | **Day:** 4 | **Owner:** TL + M3

---

### 34.1 Measure Full Pipeline Time
- [ ] **Task:** Time the full pipeline from POST to final state. Log the total time in the response from `GET /api/submissions/{id}` as `processing_time_ms`.
  - **Owner:** M3
  - **Dependencies:** 30.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Total time is under 20 seconds. If over 20 seconds, identify the slowest agent from `agent_logs`.

### 34.2 Reduce LLM Calls if Over Budget
- [ ] **Task:** If pipeline is over 20 seconds: consider combining the citizen + demand prompts into one call, or replacing the supervisor with a simple rule-based router (just check `input_type`).
  - **Owner:** TL
  - **Dependencies:** 34.1
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Pipeline completes in under 20 seconds. **P1 — only execute if 34.1 shows > 20s.**

**Section 34 — Definition of Done:**
- [ ] Pipeline time measured and logged
- [ ] Pipeline completes in under 20 seconds

---

# SECTION 35 — Deployment

**Priority:** P1 | **Day:** 5 (Morning) | **Owner:** M3

---

### 35.1 Verify App Runs on Demo Machine
- [ ] **Task:** On the machine that will be used for the demo: clone the repo, activate the venv, install dependencies, run `python scripts/load_demo_data.py`, start backend, start frontend. Verify the full demo path works.
  - **Owner:** M3
  - **Dependencies:** 31.1
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Full demo path completes on the demo machine. No "it works on my machine" failures.

### 35.2 Create One-Command Start Script
- [ ] **Task:** Create `scripts/start_demo.sh` (and `start_demo.bat` for Windows). The script: activates venv, starts the backend in the background, starts the frontend in the background, opens the browser.
  - **Owner:** M3
  - **Dependencies:** 35.1
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Running `./scripts/start_demo.sh` brings up both servers and opens the browser in one step.

**Section 35 — Definition of Done:**
- [ ] App runs cleanly on the demo machine
- [ ] One-command start script works

---

# SECTION 36 — Demo Preparation

**Priority:** P0 | **Day:** 5 | **Owner:** TL

---

### 36.1 Define the Demo Script
- [ ] **Task:** Write a step-by-step demo script in `docs/DEMO_SCRIPT.md`. Cover: (1) intro sentence, (2) submit the road request, (3) point to the parsed result, (4) point to the recommendation, (5) navigate to dashboard, (6) point to heatmap, (7) select a project for evidence, (8) closing sentence.
  - **Owner:** TL
  - **Dependencies:** 31.1
  - **Estimated Time:** 25 min
  - **Acceptance Criteria:** Script is under 300 words. Anyone on the team can present from it. Timing is under 5 minutes.

### 36.2 Prepare Seed Data for Demo
- [ ] **Task:** Reset the database. Run the loader. Pre-submit 5 requests to create visible clusters and a meaningful heatmap. Take a screenshot of the resulting dashboard to confirm it looks good.
  - **Owner:** M4
  - **Dependencies:** 9.5, 24.2
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Dashboard shows at least 3 projects with distinct scores. Heatmap has at least 2–3 hot wards. Screenshot saved to `assets/demo_screenshot.png`.

### 36.3 Full Demo Rehearsal (Run 1)
- [ ] **Task:** All four members present the demo from scratch. Time it. Identify any awkward moments, slow transitions, or unclear explanations.
  - **Owner:** All
  - **Dependencies:** 36.1, 36.2
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Demo runs from start to finish without crashing. Total time is under 6 minutes. All members know which part they present.

### 36.4 Fix Issues Found in Rehearsal
- [ ] **Task:** Address the top 3 issues found in rehearsal. Focus on: loading time, visual clarity, and confusing copy.
  - **Owner:** All
  - **Dependencies:** 36.3
  - **Estimated Time:** 45 min
  - **Acceptance Criteria:** The three identified issues are fixed. Second rehearsal runs smoother.

### 36.5 Full Demo Rehearsal (Run 2)
- [ ] **Task:** Run the demo a second time. Confirm it runs in under 5 minutes, no crashes, all visuals are clear.
  - **Owner:** All
  - **Dependencies:** 36.4
  - **Estimated Time:** 20 min
  - **Acceptance Criteria:** Under 5 minutes. No crashes. Team is confident presenting.

**Section 36 — Definition of Done:**
- [ ] Demo script is written and under 300 words
- [ ] Seed data creates a compelling dashboard state
- [ ] Two full rehearsals completed
- [ ] Top issues from rehearsal 1 are fixed

---

# SECTION 37 — Judge Questions

**Priority:** P0 | **Day:** 5 | **Owner:** TL

---

### 37.1 Prepare Answer: Why not just a chatbot?
- [ ] **Task:** Write a 30-second answer: "MeriAwaaz AI is not a chatbot — it transforms citizen submissions into ranked, evidence-based development priorities. The output is a prioritized project list an MP can act on, not just a conversation."
  - **Owner:** TL
  - **Dependencies:** 36.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Answer is rehearsed and under 30 seconds.

### 37.2 Prepare Answer: Why is the ranking deterministic?
- [ ] **Task:** Write a 30-second answer: "The score is computed from fixed weights in code: urgency, cluster size, and infrastructure gap. The LLM only writes the explanation. This means the ranking is auditable and repeatable — you get the same result for the same inputs every time."
  - **Owner:** TL
  - **Dependencies:** 36.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Answer is rehearsed and clearly distinguishes code-computed score from LLM explanation.

### 37.3 Prepare Answer: How does it scale?
- [ ] **Task:** Write a 30-second answer: "This is a prototype, but the architecture supports scale. ChromaDB handles large vector collections, the agent pipeline can process requests asynchronously, and the scoring function is O(n) in the number of projects."
  - **Owner:** TL
  - **Dependencies:** 36.1
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Answer is rehearsed. Does not over-promise production readiness.

### 37.4 Prepare Answer: What is the tech stack?
- [ ] **Task:** Write a concise stack summary for judges: React + TypeScript (frontend), FastAPI + Python (backend), LangGraph (agent orchestration), OpenAI (LLM), ChromaDB (similarity search), SQLite (persistence), Leaflet (maps).
  - **Owner:** TL
  - **Dependencies:** None
  - **Estimated Time:** 10 min
  - **Acceptance Criteria:** Stack summary fits on one slide or one sentence.

### 37.5 Prepare Answer: How does multimodal input work?
- [ ] **Task:** Write a 30-second answer: "Text input is the primary path. Voice input uses the Web Speech API to transcribe to text before processing. Image input uses OpenAI's vision capability to extract a text description, then the same pipeline runs. All three paths converge at the same parsing step."
  - **Owner:** TL
  - **Dependencies:** None
  - **Estimated Time:** 15 min
  - **Acceptance Criteria:** Answer is rehearsed. Honest about what is prototyped vs. fully wired.

**Section 37 — Definition of Done:**
- [ ] All five judge answers are written and rehearsed
- [ ] No judge question catches the team off-guard

---

# SECTION 38 — Stretch Goals

**Priority:** P2 — Cut if behind schedule | **Day:** 5 (Only if ahead of schedule)

---

### 38.1 Voice Input via Web Speech API
- [ ] **Task:** Add a microphone button to the chat UI. Use the browser's `SpeechRecognition` API to transcribe speech to text. Insert the transcription into the chat input field. Submit as a normal text request.
  - **Owner:** M2
  - **Dependencies:** 22.3
  - **Estimated Time:** 45 min
  - **Acceptance Criteria:** Microphone button appears. Clicking it prompts for mic permission. Speech is transcribed and placed in the input field. **P2.**

### 38.2 Image Upload Input
- [ ] **Task:** Add an image upload button to the chat UI. On upload, send the image to a new `POST /api/submissions/image` endpoint that uses OpenAI vision to extract a text description, then routes through the normal pipeline.
  - **Owner:** M2 + M3
  - **Dependencies:** 22.3
  - **Estimated Time:** 60 min
  - **Acceptance Criteria:** Image can be uploaded. Pipeline processes it. Result appears in chat. **P2.**

### 38.3 Weight Adjustment Sliders on Dashboard
- [ ] **Task:** Add three sliders on the dashboard for `urgency_weight`, `cluster_weight`, `gap_weight`. When sliders change, re-call `GET /api/dashboard?urgency_weight=0.5&...` and update rankings.
  - **Owner:** M2 + M4
  - **Dependencies:** 23.2, 18.2
  - **Estimated Time:** 60 min
  - **Acceptance Criteria:** Sliders render. Moving a slider re-fetches and re-renders the project list with updated scores. **P2.**

### 38.4 Hindi Language Support
- [ ] **Task:** Add a language toggle to the chat UI. When Hindi is selected, prepend "Respond in Hindi JSON:" to the citizen prompt. Verify the LLM returns Hindi text in the summary field.
  - **Owner:** TL
  - **Dependencies:** 15.1
  - **Estimated Time:** 30 min
  - **Acceptance Criteria:** Submitting Hindi text returns a Hindi summary. **P2.**

**Section 38 — Definition of Done:**
- [ ] Stretch goals are only started if all P0 tasks are complete
- [ ] Each implemented stretch goal works end-to-end before demo
- [ ] Broken stretch goals are rolled back before the demo

---

# Final Demo Checklist

Run this on the morning of the demo.

**Environment**
- [ ] Demo machine is charged and plugged in
- [ ] Browser is open to `http://localhost:5173`
- [ ] Backend is running: `uvicorn app.main:app --reload` with no errors
- [ ] Frontend is running: `npm run dev` with no errors
- [ ] `GET http://localhost:8000/health` returns 200
- [ ] `GET http://localhost:8000/api/dashboard` returns populated project list

**Data**
- [ ] Database is reset to a clean seed state (pre-submitted 5 requests)
- [ ] Dashboard shows at least 3 ranked projects
- [ ] Heatmap shows at least 2–3 hot wards
- [ ] All evidence cards have content

**Demo Flow (Verify Once)**
- [ ] Submit "Roads near the primary school in Ward 2 are broken and dangerous for children"
- [ ] Parsed issue card appears: category=roads, urgency=high
- [ ] Recommendation card appears with a project title and reason
- [ ] Navigate to dashboard — Ward 2 marker is visible
- [ ] Click the top project — evidence panel shows 3 bullets
- [ ] Cluster summary shows 2+ similar requests

**Backup**
- [ ] Screenshots of the working dashboard saved to `assets/`
- [ ] Static fallback HTML file exists if live demo fails
- [ ] Team member can narrate over screenshots if needed

**Presentation**
- [ ] All five judge answers are rehearsed
- [ ] Each team member knows their presentation segment
- [ ] Demo runs in under 5 minutes in rehearsal

---

*End of MeriAwaaz AI Implementation Checklist v2.0*
