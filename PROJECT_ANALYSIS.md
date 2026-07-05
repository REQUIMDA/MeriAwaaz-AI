# MeriAwaaz AI — Project Analysis & Integration Guide

**Last updated:** 2026-07-05 after pulling all teammate branches  
**Author:** M4 (Arvind) — owns services/, tools/, api/, data files

---

## Team Ownership

| Person    | Branch               | Owns                                                                  |
|-----------|----------------------|-----------------------------------------------------------------------|
| Kartik    | `kartik`             | agents/, supervisor.py, tools/ (stubs), core/llm.py, prompts/        |
| Adhisha   | `adhisha`            | Full alternative pipeline, processed data JSONs, scripts/             |
| Shreshtha | `shreshtha/backend`  | main.py scaffold, requirements.txt, api/health.py, schemas/settings.py, schemas/dashboard.py |
| Arvind    | `shres`              | services/database.py, services/chroma_client.py, services/store.py, tools/ implementations, api/ endpoints |

---

## Branch-by-Branch Status

### Kartik (`origin/kartik`) — Agent Architecture

**Done:**
- `schemas/models.py` — canonical Pydantic v2 models. **This is the source of truth for all schemas.**
- `supervisor.py` — LangGraph `StateGraph` wiring all 5 agents with conditional routing (text/voice/image/dashboard_refresh)
- `agents/citizen_intelligence_agent.py` — `create_react_agent` with Gemini + citizen_tools
- `agents/demand_intelligence_agent.py` — `create_react_agent` with Gemini + demand_tools
- `agents/knowledge_fusion_agent.py` — `create_react_agent` with Gemini + knowledge_tools
- `agents/policy_recommendation_agent.py` — `create_react_agent` with Gemini + policy_tools
- `agents/explainability_agent.py` — `create_react_agent` with Gemini + explainability_tools
- `tools/policy_tools.py` — **REAL implementation**: `compute_priority_score` (0–100 output, takes 0–1 inputs) + `rank_projects`
- `tools/explainability_tools.py` — **PARTIAL real**: `build_evidence_bullets` + `compute_confidence_score` (logic correct)
- `tools/citizen_tools.py` — **STUB** (returns empty dict, no Gemini call)
- `tools/demand_tools.py` — **STUB** (returns empty list, no ChromaDB call)
- `tools/knowledge_tools.py` — **STUB** (returns zeros, no JSON lookup)
- `core/llm.py` — Gemini model setup
- All 5 prompts in `prompts/`

**Problems in Kartik's branch:**
- `models.py` uses `input_type: Literal["text", "voice", "image", "dashboard_refresh"]` — uses `"image"` but Shreshtha + Adhisha both use `"photo"`. **Must fix to `"photo"`.**
- No `main.py`, no `requirements.txt`, no `.env`
- All tools except `policy_tools` are stubs — pipeline won't produce real output until implemented

---

### Adhisha (`origin/adhisha`) — Complete Alternative Pipeline

Adhisha built a **full working end-to-end pipeline** independently. Very valuable for data files and scoring logic, but uses different file names and Store API than the rest of the team.

**Done:**
- `agents/graph.py` — LangGraph pipeline: intake→clustering→fusion→policy→explainability (sequential, deterministic)
- `agents/intake_agent.py` — keyword-based classification stub (no Gemini, functional for demo)
- `agents/clustering_agent.py` — groups submissions by category+location into STORE.clusters
- `agents/fusion_agent.py` — **REAL**: reads preprocessed JSON, normalizes severity, applies complaint boost, sets `state.knowledge_context`
- `agents/policy_agent.py` — **REAL**: scoring formula (40/30/20/10 weights), saves to STORE
- `agents/explainability_agent.py` — functional stub, generates evidence bullets + summary
- `agents/refresh.py` — rescores all STORE contexts on demand (for dashboard-refresh)
- `services/need_scoring.py` — `load_json`, `match_by_location`, `normalize`, `apply_complaint_boost`
- `services/store.py` — Store class with public `clusters`, `fused_contexts`, `recommendations` dicts
- `services/clean_utils.py` — path/column normalization utilities
- `config.py` — `CONSTITUENCY = {"state": "Maharashtra", "district": "Nagpur"}` + `CATEGORY_CONFIG`
- `data/education_need.json` — **PREPROCESSED**, all 37 states, `large_school_pct` field
- `data/healthcare_need.json` — **PREPROCESSED**, all districts, `medicine_shortage_ratio` field
- `data/digital_connectivity_need.json` — **PREPROCESSED**, 22 states, `rural_teledensity` field
- `data/local_plans.json` — **only 2 entries** (Rampur Education, Kesarpur Healthcare)
- `main.py` — full FastAPI with `/api/submissions`, `/api/dashboard-refresh`, `/api/recommendations`
- All preprocessing scripts in `scripts/`

**Problems in Adhisha's branch:**
- Uses `schema.py` (imports from `app.schemas.schema`) — everyone else uses `models.py`. Easy rename fix.
- `Store` uses direct dict access (`STORE.fused_contexts[key] = ctx`) — incompatible with Shreshtha's private-dict Store.
- `intake_agent` is keyword-based, not Gemini-powered. Fine for demo but Kartik's architecture uses LLM.
- `local_plans.json` has only 2 entries — needs 8 for a convincing demo covering all categories.

---

### Shreshtha (`shreshtha/backend`) — Backend Scaffold + Services

**Done (on this branch, which Arvind builds off):**
- `schemas/models.py` — synced from Kartik
- `schemas/settings.py` — Pydantic settings, reads `.env` for `GEMINI_API_KEY`, `database_url`, `chroma_path`
- `schemas/dashboard.py` — `HeatmapPoint`, `ProjectCard`, `DashboardData` response schemas
- `services/database.py` — SQLite service: `init_db`, `insert_submission`, `get_submission`, `update_submission_cluster`, `upsert_cluster`, `upsert_recommendation`, `get_all_recommendations`, `count_submissions_by_ward`, `log_agent`
- `services/chroma_client.py` — ChromaDB singleton: `get_collection`, `add_submission`, `query_similar`
- `services/store.py` — `_Store` class with method-based API: `upsert_context`, `get_context`, `all_contexts`, `upsert_recommendation`, `get_recommendation`, `all_recommendations_sorted`, `load_local_plans()`
- `api/health.py` — GET `/health` → `{"status": "ok"}`
- `main.py` — FastAPI app with CORS + logging, only `/health` and `/` wired up
- `requirements.txt` — full dependencies

**Problems in Shreshtha's branch (= Arvind's current working branch):**
- `store.py` `load_local_plans()` calls `from app.services.need_scoring import score_plan_project` — **this function does not exist anywhere** → ImportError on startup
- No `/api/submissions`, `/api/recommendations`, `/api/dashboard` endpoints
- `main.py` has no startup event (no `init_db()`, no `load_local_plans()`)
- No `.env` or `.env.example` file
- None of Adhisha's processed data files (`education_need.json`, etc.) are present on this branch
- No `config.py` (CONSTITUENCY + CATEGORY_CONFIG)
- Kartik's `agents/`, `supervisor.py`, `core/` are not on this branch at all

---

## Critical Conflicts to Resolve

### Conflict 1 — `score_plan_project` Does Not Exist (BLOCKS STARTUP)

Shreshtha's `store.py` `load_local_plans()` does:
```python
from app.services.need_scoring import score_plan_project
```
This function does not exist in `need_scoring.py` (Adhisha's) or anywhere. Server crashes on import.

**Fix (Block A):** Rewrite `load_local_plans()` without that import.

---

### Conflict 2 — Two Incompatible Store APIs

Adhisha's agents directly write:
```python
STORE.fused_contexts[cluster.cluster_id] = context
STORE.clusters[existing_id].cluster_size += 1
```

Shreshtha's Store has private dicts and method-only access:
```python
STORE.upsert_context(project_id, ctx)
STORE.get_context(project_id)
```
No public `fused_contexts` or `clusters` attribute exists.

**Fix (Block A):** Add public `clusters` and `cluster_submissions` dicts to `_Store.__init__` so both APIs co-exist.

---

### Conflict 3 — Two Pipeline Implementations

- **Kartik's** `supervisor.py`: LangGraph with `create_react_agent`, Gemini-driven per agent
- **Adhisha's** `agents/graph.py`: LangGraph with plain deterministic functions

**Decision: Use Kartik's architecture (he is TL).** Port Adhisha's scoring logic into Arvind's tool implementations (knowledge_tools, demand_tools). Do NOT wire Adhisha's graph.py.

---

### Conflict 4 — Schema File Name

Adhisha imports from `app.schemas.schema`. Everyone else imports from `app.schemas.models`.

**Fix:** When copying any of Adhisha's agent files, change the import at the top. Not needed if we use Kartik's agents (which already import from models).

---

### Conflict 5 — `input_type` Literal Value

- Kartik's `models.py`: uses `"image"`
- Shreshtha's `models.py` + Adhisha's `schema.py`: use `"photo"`

**Fix:** Tell Kartik to change `"image"` → `"photo"` in his `models.py` on one line. This is Kartik's fix, not Arvind's.

---

## What Arvind Must Build — Complete Task List

Priority order — top items block everything below them.

---

### BLOCK A — Fix Broken Store (server crashes without this)

**File:** `backend/app/services/store.py`

**Change 1 — `__init__`:** Add two public dicts:
```python
def __init__(self):
    self._contexts: dict[str, FusedContext] = {}
    self._recommendations: dict[str, Recommendation] = {}
    self.clusters: dict[str, ClusterResult] = {}           # public — Adhisha/demand_tools compatible
    self.cluster_submissions: dict[str, list[dict]] = {}   # public — Adhisha/demand_tools compatible
```
Also add `ClusterResult` to the import at the top of store.py.

**Change 2 — `load_local_plans`:** Replace the entire method with this (removes the broken `score_plan_project` import):
```python
def load_local_plans(self, json_path: str) -> None:
    import json, os
    if not os.path.exists(json_path):
        print(f"WARNING: {json_path} not found, skipping.")
        return
    with open(json_path) as f:
        plans = json.load(f)
    for plan in plans:
        pop = plan.get("estimated_beneficiaries", 0)
        cost = plan.get("estimated_cost_inr") or 0
        location = plan["location"]["village"] if isinstance(plan["location"], dict) else plan["location"]
        ctx = FusedContext(
            category=plan["category"],
            location=location,
            demand_count=0,
            population_affected=pop,
            estimated_cost_inr=cost,
            data_confidence="synthetic",
            severity_score=0.5,
            category_specific_data={"title": plan["title"], "source": plan.get("source", "handbuilt")},
            is_existing_plan_project=True,
        )
        self.upsert_context(plan["plan_id"], ctx)
        from app.tools.policy_tools import compute_priority_score
        result = compute_priority_score.invoke({
            "citizen_demand": 0.0,
            "infrastructure_gap": 0.5,
            "population_impact": min(pop / 15000, 1.0),
            "cost_feasibility": max(0.0, 1.0 - cost / 10_000_000),
        })
        rec = Recommendation(
            project_id=plan["plan_id"],
            title=plan["title"],
            priority_score=result["priority_score"],
            breakdown=ScoreBreakdown(**result["breakdown"]),
            is_existing_plan_project=True,
            explanation=None,
        )
        self.upsert_recommendation(rec)
    print(f"Store: loaded {len(plans)} local plan projects.")
```

---

### BLOCK B — Create .env Files

**File:** `backend/.env.example` (commit this)
```
GEMINI_API_KEY=your_key_here
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.0-flash
DATABASE_URL=sqlite:///./data/meri_awaaz.db
CHROMA_PATH=./data/chroma_db
ENV=development
```

**File:** `backend/.env` (do NOT commit — gitignored)  
Copy `.env.example` → `.env` and paste the real Gemini API key.

---

### BLOCK C — Port Adhisha's Data Files and Config

Run these git commands to cherry-pick Adhisha's files onto your branch:
```bash
git checkout origin/adhisha -- backend/app/data/education_need.json
git checkout origin/adhisha -- backend/app/data/healthcare_need.json
git checkout origin/adhisha -- backend/app/data/digital_connectivity_need.json
git checkout origin/adhisha -- backend/app/config.py
```

Then create `backend/app/services/need_scoring.py` (copy from Adhisha, with one path fix):
```python
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # points to backend/app/

def load_json(path: str) -> list:
    resolved = BASE_DIR / path
    with resolved.open("r", encoding="utf-8") as f:
        return json.load(f)

def match_by_location(location: str, records: list, key_field: str) -> dict | None:
    target = location.strip().lower()
    for record in records:
        if str(record.get(key_field, "")).strip().lower() == target:
            return record
    return None

def normalize(value: float, all_values: list, direction: str) -> float:
    vals = [v for v in all_values if v is not None]
    if not vals or max(vals) == min(vals):
        return 0.5
    norm = (value - min(vals)) / (max(vals) - min(vals))
    return norm if direction == "higher_is_more_need" else 1 - norm

def apply_complaint_boost(base: float, demand: int, max_demand: int) -> float:
    if max_demand == 0:
        return base
    return min(1.0, base + 0.15 * (demand / max_demand))
```

---

### BLOCK D — Create local_plans.json (8 entries)

**File:** `backend/app/data/local_plans.json`

Needs all 8 categories for a convincing demo:
```json
[
  {
    "plan_id": "plan_001",
    "category": "Education",
    "location": {"village": "Rampur", "block": "Sadar", "district": "Nagpur"},
    "title": "Additional classroom block - Rampur Govt Primary School",
    "estimated_cost_inr": 3500000,
    "estimated_beneficiaries": 210,
    "source": "mplads_pattern_handbuilt"
  },
  {
    "plan_id": "plan_002",
    "category": "Healthcare",
    "location": {"village": "Kesarpur", "block": "North", "district": "Nagpur"},
    "title": "Upgrade of Primary Health Sub-Centre - Kesarpur",
    "estimated_cost_inr": 1800000,
    "estimated_beneficiaries": 1450,
    "source": "mplads_pattern_handbuilt"
  },
  {
    "plan_id": "plan_003",
    "category": "Roads",
    "location": {"village": "Sultanpur", "block": "East", "district": "Nagpur"},
    "title": "Repair and widening of main village road - Sultanpur",
    "estimated_cost_inr": 2200000,
    "estimated_beneficiaries": 980,
    "source": "mplads_pattern_handbuilt"
  },
  {
    "plan_id": "plan_004",
    "category": "Water",
    "location": {"village": "Bhelupur", "block": "West", "district": "Nagpur"},
    "title": "Overhead water tank and pipeline - Bhelupur",
    "estimated_cost_inr": 4100000,
    "estimated_beneficiaries": 1620,
    "source": "mplads_pattern_handbuilt"
  },
  {
    "plan_id": "plan_005",
    "category": "Sanitation",
    "location": {"village": "Rampur", "block": "Sadar", "district": "Nagpur"},
    "title": "Community toilet complex - Rampur",
    "estimated_cost_inr": 900000,
    "estimated_beneficiaries": 420,
    "source": "mplads_pattern_handbuilt"
  },
  {
    "plan_id": "plan_006",
    "category": "Electricity",
    "location": {"village": "Kesarpur", "block": "North", "district": "Nagpur"},
    "title": "Solar street lighting - Kesarpur main road",
    "estimated_cost_inr": 1200000,
    "estimated_beneficiaries": 760,
    "source": "mplads_pattern_handbuilt"
  },
  {
    "plan_id": "plan_007",
    "category": "Vocational",
    "location": {"village": "Sultanpur", "block": "East", "district": "Nagpur"},
    "title": "ITI skill development centre - Sultanpur",
    "estimated_cost_inr": 5000000,
    "estimated_beneficiaries": 300,
    "source": "mplads_pattern_handbuilt"
  },
  {
    "plan_id": "plan_008",
    "category": "Other",
    "location": {"village": "Bhelupur", "block": "West", "district": "Nagpur"},
    "title": "Community hall and digital kiosk - Bhelupur",
    "estimated_cost_inr": 1600000,
    "estimated_beneficiaries": 550,
    "source": "mplads_pattern_handbuilt"
  }
]
```

---

### BLOCK E — Implement citizen_tools.py (Gemini calls)

**File:** `backend/app/tools/citizen_tools.py`  
Replace Kartik's stubs with real Gemini calls:

```python
import json
from langchain_core.tools import tool
from app.core.llm import get_model

_llm = None
def _get_llm():
    global _llm
    if _llm is None:
        _llm = get_model()
    return _llm

@tool
def extract_issue_details(text: str) -> dict:
    """Extract structured issue details from a citizen's raw text submission."""
    prompt = f"""Extract structured data from a citizen complaint. Return ONLY valid JSON with these exact keys:
  category: one of [Education, Healthcare, Roads, Water, Sanitation, Electricity, Vocational, Other]
  location: ward/village name or "unspecified"
  summary: one sentence describing the issue
  confidence: float 0.0-1.0

Citizen submission: {text}

Return only the JSON object, no markdown, no explanation."""
    response = _get_llm().invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)
    content = content.strip().strip("```json").strip("```").strip()
    try:
        return json.loads(content)
    except Exception:
        return {"category": "Other", "location": "unspecified", "summary": text[:100], "confidence": 0.4}

@tool
def detect_language(text: str) -> str:
    """Detect the language of the citizen's submission. Returns ISO 639-1 code."""
    prompt = f"What language is this text? Reply with only the ISO 639-1 code (e.g. en, hi, ta, mr).\n\nText: {text}"
    response = _get_llm().invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)
    return content.strip().lower()[:5]
```

---

### BLOCK F — Implement demand_tools.py (ChromaDB)

**File:** `backend/app/tools/demand_tools.py`

```python
from langchain_core.tools import tool
from app.services import chroma_client
from app.services.store import STORE
from app.schemas.models import ClusterResult
import uuid

@tool
def search_similar_submissions(summary: str, category: str, top_k: int = 10) -> list[dict]:
    """Search ChromaDB for citizen submissions similar to the current one."""
    return chroma_client.query_similar(text=summary, category=category, top_k=top_k)

@tool
def cluster_submissions(submissions: list[dict], category: str, location: str) -> dict:
    """Group similar submissions into a demand cluster and update the in-memory store."""
    match_key = f"{category}::{location}".lower()
    existing_id = None
    for cid, cluster in STORE.clusters.items():
        if f"{cluster.cluster_name}::{cluster.center_location}".lower() == match_key:
            existing_id = cid
            break

    if existing_id:
        STORE.clusters[existing_id].cluster_size += 1
    else:
        existing_id = f"cluster_{uuid.uuid4().hex[:8]}"
        STORE.clusters[existing_id] = ClusterResult(
            cluster_id=existing_id,
            cluster_name=category,
            cluster_size=len(submissions) + 1,
            center_location=location,
        )

    c = STORE.clusters[existing_id]
    return {"cluster_id": c.cluster_id, "cluster_name": c.cluster_name,
            "cluster_size": c.cluster_size, "center_location": c.center_location}
```

---

### BLOCK G — Implement knowledge_tools.py (JSON lookups)

**File:** `backend/app/tools/knowledge_tools.py`

```python
from langchain_core.tools import tool
from app.services.need_scoring import load_json, match_by_location, normalize
from app.config import CATEGORY_CONFIG, CONSTITUENCY
from app.services.store import STORE

@tool
def lookup_infrastructure(location: str, category: str) -> dict:
    """Look up infrastructure severity data for a given location and issue category."""
    cfg = CATEGORY_CONFIG.get(category)
    if not cfg:
        return {"population": 5000, "facility_count": 1, "nearest_facility_km": 5.0,
                "road_quality": "unknown", "infrastructure_gap": 0.5, "data_confidence": "estimated"}
    records = load_json(cfg["dataset"])
    loc_val = CONSTITUENCY[cfg["location_level"]]
    match = match_by_location(loc_val, records, cfg["location_field"])
    if not match:
        return {"population": 5000, "facility_count": 1, "nearest_facility_km": 5.0,
                "road_quality": "unknown", "infrastructure_gap": 0.5, "data_confidence": "estimated"}
    all_vals = [r.get(cfg["need_field"], 0) for r in records if r.get(cfg["need_field"]) is not None]
    gap = normalize(match.get(cfg["need_field"], 0), all_vals, cfg["direction"])
    result = {"population": 5000, "facility_count": 1, "nearest_facility_km": 5.0,
              "road_quality": "fair", "infrastructure_gap": round(gap, 4), "data_confidence": "real_data"}
    result[cfg["need_field"]] = match.get(cfg["need_field"])
    return result

@tool
def lookup_plan_projects(location: str, category: str) -> list[dict]:
    """Look up existing local development plan proposals for a location and category."""
    results = []
    for pid, ctx in STORE._contexts.items():
        if (ctx.category == category and ctx.is_existing_plan_project
                and location.lower() in ctx.location.lower()):
            results.append({"project_id": pid,
                            "title": ctx.category_specific_data.get("title", pid),
                            "estimated_cost": ctx.estimated_cost_inr,
                            "status": "planned"})
    return results
```

---

### BLOCK H — API Endpoints

**File:** `backend/app/api/submissions.py`
```python
import uuid
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.models import AgentState
from app.supervisor import build_workflow
from app.services import database, chroma_client

router = APIRouter(prefix="/api", tags=["submissions"])
_pipeline = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = build_workflow()
    return _pipeline

class SubmissionRequest(BaseModel):
    channel: str = "text"
    text: str = ""

@router.post("/submissions")
async def submit(req: SubmissionRequest):
    sid = str(uuid.uuid4())
    input_type = req.channel if req.channel in ("text", "voice", "photo", "dashboard_refresh") else "text"
    state = AgentState(submission_id=sid, input_type=input_type, raw_text=req.text)
    result = get_pipeline().invoke(state, config={"configurable": {"thread_id": sid}})

    parsed = result.get("parsed_issue") if isinstance(result, dict) else None
    database.insert_submission({
        "id": sid, "created_at": datetime.utcnow().isoformat(),
        "input_type": input_type, "raw_text": req.text,
        "category": parsed.get("category") if parsed else None,
        "location": parsed.get("location") if parsed else None,
        "summary": parsed.get("summary") if parsed else None,
        "confidence": None, "language": None, "cluster_id": None,
    })
    if req.text:
        chroma_client.add_submission(
            submission_id=sid, text=req.text,
            metadata={"category": parsed.get("category", "Other") if parsed else "Other",
                      "location": parsed.get("location", "unspecified") if parsed else "unspecified"},
        )
    return {"status": "processed", "submission_id": sid}
```

**File:** `backend/app/api/recommendations.py`
```python
from fastapi import APIRouter, HTTPException
from app.services.store import STORE

router = APIRouter(prefix="/api", tags=["recommendations"])

@router.get("/recommendations")
def get_recommendations():
    recs = STORE.all_recommendations_sorted()
    return {"items": [r.model_dump() for r in recs], "count": len(recs)}

@router.get("/recommendations/{project_id}")
def get_recommendation(project_id: str):
    rec = STORE.get_recommendation(project_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Not found")
    return rec.model_dump()
```

**File:** `backend/app/api/dashboard.py`
```python
from datetime import datetime
from fastapi import APIRouter
from app.services import database
from app.services.store import STORE
from app.schemas.dashboard import DashboardData, ProjectCard, HeatmapPoint

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/dashboard", response_model=DashboardData)
def get_dashboard():
    recs = STORE.all_recommendations_sorted()
    projects = []
    for r in recs[:10]:
        ctx = STORE.get_context(r.project_id)
        exp = r.explanation
        projects.append(ProjectCard(
            id=r.project_id, title=r.title,
            category=ctx.category if ctx else "Other",
            priority_score=r.priority_score,
            confidence=exp.confidence_score if exp else 0.5,
            reason=exp.summary if exp else "Scored from citizen demand and infrastructure data.",
            evidence=exp.evidence if exp else [],
        ))
    ward_counts = database.count_submissions_by_ward()
    heatmap = [HeatmapPoint(ward=row["location"] or "unspecified",
                             lat=0.0, lon=0.0, intensity=row["count"])
               for row in ward_counts]
    return DashboardData(
        projects=projects, heatmap=heatmap,
        total_submissions=sum(h.intensity for h in heatmap),
        last_updated=datetime.utcnow().isoformat(),
    )
```

---

### BLOCK I — Update main.py (Startup + All Routers)

**File:** `backend/app/main.py` — replace entire file:
```python
import logging, os, sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    print("ERROR: GEMINI_API_KEY is not set. Add it to backend/.env")
    sys.exit(1)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.submissions import router as submissions_router
from app.api.recommendations import router as recommendations_router
from app.api.dashboard import router as dashboard_router
from app.services.database import init_db
from app.services.store import STORE

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="MeriAwaaz AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info("%s %s → %s", request.method, request.url.path, response.status_code)
    return response

@app.on_event("startup")
def startup():
    init_db()
    plans_path = str(Path(__file__).parent / "data" / "local_plans.json")
    STORE.load_local_plans(plans_path)
    logger.info("Startup complete.")

app.include_router(health_router)
app.include_router(submissions_router)
app.include_router(recommendations_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {"message": "MeriAwaaz AI Backend is running"}
```

---

## Master Checklist (Arvind — do in this order)

### Immediate — server won't start without these
- [ ] **A1** Fix `store.py` — replace `load_local_plans()` with Block A code (removes broken import)
- [ ] **A2** Add public `clusters` and `cluster_submissions` dicts to `_Store.__init__`
- [ ] **B1** Create `backend/.env.example`
- [ ] **B2** Create `backend/.env` with real Gemini API key

### Data — needed before tools will return real values
- [ ] **C1** `git checkout origin/adhisha -- backend/app/data/education_need.json`
- [ ] **C2** `git checkout origin/adhisha -- backend/app/data/healthcare_need.json`
- [ ] **C3** `git checkout origin/adhisha -- backend/app/data/digital_connectivity_need.json`
- [ ] **C4** `git checkout origin/adhisha -- backend/app/config.py`
- [ ] **C5** Create `backend/app/services/need_scoring.py` (Block C)
- [ ] **D1** Create `backend/app/data/local_plans.json` with 8 entries (Block D)

### Tools — needed before pipeline produces real output
- [ ] **E1** Implement `backend/app/tools/citizen_tools.py` (Block E)
- [ ] **F1** Implement `backend/app/tools/demand_tools.py` (Block F)
- [ ] **G1** Implement `backend/app/tools/knowledge_tools.py` (Block G)

### API wiring
- [ ] **H1** Create `backend/app/api/submissions.py` (Block H)
- [ ] **H2** Create `backend/app/api/recommendations.py` (Block H)
- [ ] **H3** Create `backend/app/api/dashboard.py` (Block H)
- [ ] **I1** Replace `backend/app/main.py` (Block I)

### Tell teammates
- [ ] **X1** Tell Kartik: change `"image"` → `"photo"` in `models.py` `AgentState.input_type` (one line)
- [ ] **X2** Tell Kartik: share his `agents/`, `tools/`, `supervisor.py`, `core/` so they can be merged into `shres` branch (Arvind needs these files to wire the pipeline)

### After server starts
- [ ] **J1** Test: `uvicorn app.main:app --reload` from `backend/` — should see "Startup complete. Loaded 8 local plan projects."
- [ ] **J2** Test: `GET /api/recommendations` — should return 8 items (the local plans)
- [ ] **J3** Test: `POST /api/submissions` with `{"channel": "text", "text": "school has no toilets in Rampur"}` — should pipeline through all 5 agents
- [ ] **J4** Load 20 demo submissions for ChromaDB seeding

---

## Architecture Diagram (Final Integrated System)

```
POST /api/submissions
        │
        ▼
  Kartik's supervisor.py  (LangGraph StateGraph)
        │
        ├── citizen_intelligence_agent  ← Gemini + citizen_tools.py    [Block E]
        │         extracts: category, location, summary, language
        │
        ├── demand_intelligence_agent   ← Gemini + demand_tools.py     [Block F]
        │         searches ChromaDB → builds/updates cluster in STORE
        │
        ├── knowledge_fusion_agent      ← Gemini + knowledge_tools.py  [Block G]
        │         reads: education/healthcare/connectivity JSON
        │         reads: local_plans.json via STORE
        │
        ├── policy_recommendation_agent ← Gemini + policy_tools.py     [Kartik — DONE]
        │         formula: 40% demand + 30% severity + 20% pop + 10% cost → 0–100
        │
        └── explainability_agent        ← Gemini + explainability_tools.py [Kartik — DONE]
                  writes: evidence bullets + summary + confidence

        Result written to:
          SQLite        (database.py)      ← permanent record, survives restart
          ChromaDB      (chroma_client.py) ← similarity search, survives restart
          STORE         (store.py)         ← fast in-memory for API reads, resets on restart

GET /api/recommendations → reads STORE → sorted by priority_score
GET /api/dashboard       → reads STORE + SQLite → top 10 + heatmap
GET /health              → {"status": "ok"}
```

---

## Files Arvind Must NOT Touch

These belong to Kartik. Only touch if he explicitly asks:
- `backend/app/agents/*.py`
- `backend/app/supervisor.py`
- `backend/app/core/llm.py`
- `backend/app/schemas/models.py`
- `prompts/*.md`
