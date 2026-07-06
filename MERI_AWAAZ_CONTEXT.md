# MeriAwaaz AI — Complete Project Context

**Purpose of this file:** Complete handoff context for a new session. Contains every file, every known bug, full architecture, and next steps. Do NOT need to read any other doc files.

---

## 1. What This Project Is

**MeriAwaaz AI** ("My Voice AI") is a constituency development decision-support system for Indian Members of Parliament. Citizens submit complaints/requests (text, voice, photo, video) → a 5-agent LangGraph pipeline processes each submission → the MP sees a ranked dashboard of development projects prioritized by citizen demand + infrastructure data.

**Hackathon project.** The goal is a working demo where an MP can see submissions clustered and ranked into actionable project cards.

---

## 2. Team Structure

| Person | Role | Branch |
|--------|------|--------|
| Kartik | Tech Lead — wrote LangGraph agent skeleton + models.py | `kartik` |
| Adhisha | Data — wrote dataset scripts, need_scoring, local_plans.json | `adhisha` |
| Shreshtha / Arvind | Backend integration — M4 layer, all tools, all APIs, pipeline wiring | `shreshtha/backend` → merged to `main` |

**Current branch: `main`** (shreshtha/backend merged in via commit `091de75`). The `adhisha` and `kartik` branches are NOT merged — their useful files have already been copied in.

---

## 3. Repository Structure

```
MeriAwaaz-AI/
├── backend/
│   ├── .env                         ← API keys (see Section 4)
│   ├── requirements.txt
│   └── app/
│       ├── main.py                  ← FastAPI app entry point
│       ├── config.py                ← CONSTITUENCY + CATEGORY_CONFIG
│       ├── supervisor.py            ← LangGraph StateGraph + wrapper nodes
│       ├── core/
│       │   └── llm.py               ← get_model() factory
│       ├── schemas/
│       │   ├── models.py            ← ALL Pydantic models (single source of truth)
│       │   ├── dashboard.py         ← DashboardData, ProjectCard, HeatmapPoint
│       │   └── settings.py          ← Settings (pydantic-settings, reads .env)
│       ├── agents/
│       │   ├── __init__.py          ← (empty)
│       │   ├── citizen_intelligence_agent.py
│       │   ├── demand_intelligence_agent.py
│       │   ├── knowledge_fusion_agent.py
│       │   ├── policy_recommendation_agent.py
│       │   ├── explainability_agent.py
│       │   ├── vision_processing.py ← image + video via Gemini File API
│       │   └── speech_processing.py ← audio via Gemini File API
│       ├── tools/
│       │   ├── citizen_tools.py     ← extract_issue_details, detect_language
│       │   ├── demand_tools.py      ← search_similar_submissions, cluster_submissions
│       │   ├── knowledge_tools.py   ← lookup_infrastructure, lookup_plan_projects
│       │   ├── policy_tools.py      ← compute_priority_score, rank_projects
│       │   └── explainability_tools.py ← build_evidence_bullets, compute_confidence_score
│       ├── api/
│       │   ├── health.py            ← GET /health
│       │   ├── submissions.py       ← POST /api/submissions, GET /api/submissions/{id}
│       │   ├── video.py             ← POST /api/submissions/video
│       │   ├── dashboard.py         ← GET /api/dashboard, POST /api/dashboard-refresh
│       │   ├── recommendations.py   ← GET /api/recommendations
│       │   └── explain.py           ← GET /api/explain/{project_id}
│       ├── services/
│       │   ├── database.py          ← SQLite (raw sqlite3, no ORM)
│       │   ├── chroma_client.py     ← ChromaDB + Gemini text-embedding-004
│       │   ├── store.py             ← In-memory Store singleton
│       │   └── need_scoring.py      ← load_json, match_by_location, normalize
│       └── data/
│           ├── local_plans.json     ← 8 seed plan projects
│           ├── healthcare_need.json
│           ├── education_need.json
│           ├── digital_connectivity_need.json
│           └── uploads/             ← saved photos/videos/audio (served at /uploads)
├── docs/
│   └── API_CONTRACTS.md
└── prompts/                         ← markdown prompt files (reference only, not used at runtime)
```

---

## 4. Environment / .env

File at `backend/.env`:
```
GEMINI_API_KEY=<key is already set — do not change>
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.0-flash
DATABASE_URL=sqlite:///./data/meri_awaaz.db
CHROMA_PATH=./data/chroma_db
ENV=development
```

⚠️ **BUG IN CURRENT .env:** `GEMINI_MODEL=gemini-3.5-flash` — this model does not exist. It must be `gemini-2.0-flash`. Fix the .env before starting the server.

---

## 5. How to Run the Server

```bash
# Windows — inside backend/ folder with venv active
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

Server starts at `http://localhost:8000`. Swagger UI at `http://localhost:8000/docs`.

At startup:
1. Loads `.env`
2. Aborts if `GEMINI_API_KEY` is missing
3. Runs `init_db()` → creates SQLite tables + auto-migrates missing columns
4. Loads `local_plans.json` → seeds STORE with 8 plan projects (Education/Healthcare/Roads/Water/Sanitation/Electricity/Vocational/Other)
5. Serves `app/data/uploads/` at `/uploads`

---

## 6. Architecture: The 5-Agent Pipeline

```
POST /api/submissions
        │
        ▼
   AgentState (Pydantic BaseModel)
        │
        ├─ input_type = "voice"  ──→ speech_processing.run()  ──┐
        ├─ input_type = "image"  ──→ vision_processing.run()  ──┤
        ├─ input_type = "video"  ──→ vision_processing.run()  ──┤
        └─ input_type = "text"   ──────────────────────────────┘
                                                                │
                    ┌───────────────────────────────────────────┘
                    ▼
        citizen_intelligence_agent   → fills state.parsed_issue
                    │                  (category, location, summary, confidence, language)
                    ▼
        demand_intelligence_agent    → fills state.cluster
                    │                  (cluster_id, cluster_name, cluster_size, center_location)
                    ▼
        knowledge_fusion_agent       → fills state.knowledge_context
                    │                  (infrastructure_gap, population, facility_count, etc.)
                    ▼
        policy_recommendation_agent  → fills state.recommendation
                    │                  (project_id, title, priority_score, breakdown)
                    ▼
        explainability_agent         → fills state.recommendation.explanation
                                       (evidence bullets, summary, confidence_score)
```

### AgentState (shared across all nodes)
```python
class AgentState(BaseModel):
    submission_id: str
    input_type: Literal["text", "voice", "image", "video", "dashboard_refresh"]
    raw_text: str = ""
    media_file_path: Optional[str] = None   # path to uploaded file on disk
    audio_url: Optional[str] = None         # set by speech_processing; /uploads/{file}
    parsed_issue: Optional[ParsedIssue] = None
    cluster: Optional[ClusterResult] = None
    knowledge_context: Optional[FusedContext] = None
    recommendation: Optional[Recommendation] = None
    error: Optional[str] = None
```

### Priority Score Formula (fixed weights, policy_tools.py)
```
score = 0.40 × citizen_demand
      + 0.30 × infrastructure_gap
      + 0.20 × population_impact
      + 0.10 × cost_feasibility
```
All inputs are 0.0–1.0. Final `priority_score` is ×100 (0–100 scale). ScoreBreakdown fields: citizen_demand (0–40), severity (0–30), population_impact (0–20), cost_feasibility (0–10).

---

## 7. Known Bugs & Their Status

### FIXED (already in main)
1. **supervisor.py — MessagesState mismatch** ← THE MAIN 500 ERROR
   - Root cause: `create_react_agent` returns a `CompiledStateGraph` using `MessagesState` internally (needs `{"messages": [...]}`). Outer graph was passing `AgentState` directly.
   - Fix: Replaced direct node assignment with wrapper functions that translate `AgentState` → `{"messages": [HumanMessage(...)]}` → parse response back into state updates.

2. **requirements.txt** — `fastapi==0.111.0` conflicted with chromadb requiring `>=0.115.9`. Fixed to `fastapi>=0.115.9`.

3. **store.py** — was truncated at line 62. Completed.

4. **ScoreBreakdown field mismatch** — policy_tools returns `infrastructure_gap` but model has field `severity`. Fixed with explicit mapping + ×100 scaling in store.py.

5. **video.py FileNotFoundError** — `dest.stat().st_size` called after `dest.unlink()`. Fixed by capturing size before deleting.

6. **chroma_client.py wipes on every restart** — Fixed with sentinel document pattern.

7. **supervisor.py `langgraph 0.1.x`** — `.run` doesn't exist on `CompiledStateGraph`. Fixed.

### STILL BROKEN — needs fixing

**BUG A: `explain.py` — same MessagesState mismatch**
File: `backend/app/api/explain.py`, function `_invoke_explainability`
```python
# BROKEN — same problem as old supervisor.py
result = explainability_agent.invoke(state.model_dump())
```
Fix: Import and call the wrapper function from supervisor.py instead:
```python
from app.supervisor import explainability_node
result_dict = explainability_node(state)
explanation = result_dict.get("recommendation", state.recommendation)
if explanation and explanation.explanation:
    return explanation.explanation
raise ValueError("Explainability Agent produced no explanation.")
```

**BUG B: `.env` wrong model name**
`GEMINI_MODEL=gemini-3.5-flash` → must be `GEMINI_MODEL=gemini-2.0-flash`
Change in `backend/.env`.

**BUG C: chroma_client `query_similar` fails if only sentinel in collection**
When the collection has only the sentinel document, `col.count()` returns 1 but filtering by `where={"category": ...}` on the sentinel will fail because it has no `category` metadata. The `count == 0` guard doesn't catch this.
Fix in `chroma_client.py`:
```python
def query_similar(text: str, category: str, top_k: int = 10) -> list[dict]:
    col = get_collection()
    real_count = col.count() - 1  # subtract sentinel
    if real_count <= 0:
        return []
    ...
    results = col.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, real_count),
        where={"category": category},
    )
```

**BUG D: `dashboard-refresh` endpoint does nothing**
`POST /api/dashboard-refresh` has a `pass` loop — it iterates contexts but doesn't re-score them. For the hackathon demo this is fine (scores update on every new submission anyway), but it should at least trigger a re-score.

---

## 8. Complete File Listing (All Source Code)

### `backend/requirements.txt`
```
fastapi>=0.115.9
uvicorn[standard]>=0.29.0
pydantic>=2.7.1
pydantic-settings>=2.2.1
python-dotenv==1.0.1
langgraph>=0.2.0
langchain>=0.2.5
langchain-openai>=0.1.8
langchain-google-genai>=1.0.0
langchain-anthropic>=0.1.0
google-generativeai>=0.7.0
chromadb>=0.5.0
Pillow>=10.3.0
python-multipart>=0.0.9
aiofiles>=23.2.1
httpx>=0.27.0
```

---

### `backend/app/main.py`
```python
import logging
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    print("ERROR: GEMINI_API_KEY is not set. Add it to backend/.env before starting.")
    sys.exit(1)

from pathlib import Path

from app.api.health import router as health_router
from app.api.submissions import router as submissions_router
from app.api.video import router as video_router
from app.api.recommendations import router as recommendations_router
from app.api.explain import router as explain_router
from app.api.dashboard import router as dashboard_router
from app.services.database import init_db
from app.services.store import STORE

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MeriAwaaz AI",
    version="1.0.0",
    description="Backend API for the MeriAwaaz AI Hackathon Project",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info("%s %s → %s", request.method, request.url.path, response.status_code)
    return response


UPLOADS_DIR = Path(__file__).parent / "data" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


@app.on_event("startup")
def on_startup():
    init_db()
    plans_path = str(Path(__file__).parent / "data" / "local_plans.json")
    STORE.load_local_plans(plans_path)
    logger.info("Startup complete.")


app.include_router(health_router)
app.include_router(submissions_router)
app.include_router(video_router)
app.include_router(recommendations_router)
app.include_router(explain_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {"message": "MeriAwaaz AI Backend is running"}
```

---

### `backend/app/config.py`
```python
CONSTITUENCY = {
    "state": "Maharashtra",
    "district": "Nagpur",
}

CATEGORY_CONFIG = {
    "Healthcare": {
        "dataset": "data/healthcare_need.json",
        "location_level": "district",
        "location_field": "district",
        "need_field": "medicine_shortage_ratio",
        "direction": "higher_is_more_need",
    },
    "Education": {
        "dataset": "data/education_need.json",
        "location_level": "state",
        "location_field": "state",
        "need_field": "large_school_pct",
        "direction": "higher_is_more_need",
    },
    "Other": {
        "dataset": "data/digital_connectivity_need.json",
        "location_level": "state",
        "location_field": "state",
        "need_field": "rural_teledensity",
        "direction": "lower_is_more_need",
    },
    # Roads, Water, Sanitation, Electricity, Vocational: no dataset yet — returns estimated 0.5
}

__all__ = ["CATEGORY_CONFIG", "CONSTITUENCY"]
```

---

### `backend/app/schemas/models.py`
```python
from pydantic import BaseModel, Field
from typing import Optional, Literal, List

Category = Literal[
    "Education", "Healthcare", "Roads", "Water",
    "Sanitation", "Electricity", "Vocational", "Other"
]
DataConfidence = Literal["real_data", "estimated", "synthetic"]

class ParsedIssue(BaseModel):
    category: Category
    location: str = Field(description="Ward, village, or area name. 'unspecified' if unclear.")
    summary: str = Field(description="One-sentence summary of the citizen's request.")
    confidence: float = Field(ge=0.0, le=1.0)
    language: str = Field(description="ISO 639-1 language code, e.g. 'en', 'hi'.")

class ClusterResult(BaseModel):
    cluster_id: str
    cluster_name: str
    cluster_size: int = Field(ge=1)
    center_location: str

class FusedContext(BaseModel):
    category: Category
    location: str
    demand_count: int
    population_affected: int
    estimated_cost_inr: Optional[float] = Field(default=None, ge=0)
    data_confidence: DataConfidence
    severity_score: float = Field(ge=0.0, le=1.0)
    category_specific_data: dict[str, int | float | str] = Field(default_factory=dict)
    is_existing_plan_project: bool = Field(default=False)

class ScoreBreakdown(BaseModel):
    citizen_demand: float = Field(ge=0.0, le=40.0)
    severity: float = Field(ge=0.0, le=30.0)
    population_impact: float = Field(ge=0.0, le=20.0)
    cost_feasibility: float = Field(ge=0.0, le=10.0)

class Explanation(BaseModel):
    evidence: List[str]
    summary: str
    confidence_score: float = Field(ge=0.0, le=1.0)

class Recommendation(BaseModel):
    project_id: str
    title: str
    priority_score: float = Field(ge=0.0, le=100.0)
    breakdown: ScoreBreakdown
    is_existing_plan_project: bool = False
    explanation: Optional[Explanation] = None

class AgentState(BaseModel):
    submission_id: str
    input_type: Literal["text", "voice", "image", "video", "dashboard_refresh"]
    raw_text: str = ""
    media_file_path: Optional[str] = None
    audio_url: Optional[str] = None
    parsed_issue: Optional[ParsedIssue] = None
    cluster: Optional[ClusterResult] = None
    knowledge_context: Optional[FusedContext] = None
    recommendation: Optional[Recommendation] = None
    error: Optional[str] = None
```

---

### `backend/app/schemas/settings.py`
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    llm_provider: str = "gemini"
    gemini_model: str = "gemini-2.0-flash"
    database_url: str = "sqlite:///./data/meri_awaaz.db"
    chroma_path: str = "./data/chroma_db"
    env: str = "development"
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

---

### `backend/app/schemas/dashboard.py`
```python
from typing import List
from pydantic import BaseModel
from app.schemas.models import ScoreBreakdown

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
    breakdown: ScoreBreakdown
    is_existing_plan_project: bool

class DashboardData(BaseModel):
    projects: List[ProjectCard]
    heatmap: List[HeatmapPoint]
    total_submissions: int
    last_updated: str
```

---

### `backend/app/core/llm.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

_PROVIDER_MAP = {
    "gemini": ("GEMINI_API_KEY", "GEMINI_MODEL", "gemini-2.0-flash"),
    "openai": ("OPENAI_API_KEY", "OPENAI_MODEL", "gpt-4o-mini"),
    "claude": ("ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "claude-3-5-haiku-20241022"),
}

def get_model():
    if _PROVIDER not in _PROVIDER_MAP:
        raise ValueError(f"Unsupported LLM_PROVIDER '{_PROVIDER}'. Choose: gemini | openai | claude")
    key_env, model_env, default_model = _PROVIDER_MAP[_PROVIDER]
    model_name = os.getenv(model_env, default_model)
    api_key = os.getenv(key_env)
    if _PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model_name, api_key=api_key, temperature=0)
    if _PROVIDER == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model_name, api_key=api_key, temperature=0)
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=0)
```

---

### `backend/app/supervisor.py`  ← MOST IMPORTANT — recently fixed
```python
"""
LangGraph supervisor for MeriAwaaz AI.

Each create_react_agent uses MessagesState internally. This module wraps every
agent in a plain Python function that:
  1. Receives AgentState from the outer graph
  2. Formats it into {"messages": [HumanMessage(...)]} for the sub-agent
  3. Parses the agent's final response back into AgentState fields
"""
import json
import re

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.schemas.models import (
    AgentState, ParsedIssue, ClusterResult, FusedContext,
    Recommendation, ScoreBreakdown, Explanation,
)
from app.agents import (
    citizen_intelligence_agent, demand_intelligence_agent,
    knowledge_fusion_agent, policy_recommendation_agent,
    explainability_agent, vision_processing, speech_processing,
)


def _strip_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    return json.loads(text)

def _last_message_content(result: dict) -> str:
    msgs = result.get("messages", [])
    if not msgs:
        return ""
    last = msgs[-1]
    return last.content if hasattr(last, "content") else str(last)


def route_intake(state: AgentState) -> str:
    return {
        "voice":             "speech_processing_agent",
        "image":             "vision_processing_agent",
        "video":             "vision_processing_agent",
        "dashboard_refresh": "demand_intelligence_agent",
    }.get(state.input_type, "citizen_intelligence_agent")


def citizen_intelligence_node(state: AgentState) -> dict:
    text = state.raw_text or ""
    try:
        result = citizen_intelligence_agent.invoke({
            "messages": [HumanMessage(content=text)]
        })
        data = _strip_json(_last_message_content(result))
        return {"parsed_issue": ParsedIssue(
            category=data.get("category", "Other"),
            location=data.get("location", "unspecified"),
            summary=data.get("summary", text[:120]),
            confidence=float(data.get("confidence", 0.5)),
            language=data.get("language", "en"),
        )}
    except Exception as exc:
        print(f"[citizen_intelligence_node] error: {exc}")
        return {"parsed_issue": ParsedIssue(
            category="Other", location="unspecified",
            summary=text[:120], confidence=0.3, language="en",
        )}


def demand_intelligence_node(state: AgentState) -> dict:
    pi = state.parsed_issue
    if pi is None:
        return {}
    prompt = (
        f"Category: {pi.category}\nLocation: {pi.location}\nSummary: {pi.summary}\n\n"
        "Search for similar submissions and cluster them. "
        "Return JSON with keys: cluster_id, cluster_name, cluster_size, center_location."
    )
    try:
        result = demand_intelligence_agent.invoke({"messages": [HumanMessage(content=prompt)]})
        data = _strip_json(_last_message_content(result))
        return {"cluster": ClusterResult(
            cluster_id=data.get("cluster_id", f"cluster_{state.submission_id[:8]}"),
            cluster_name=data.get("cluster_name", pi.category),
            cluster_size=int(data.get("cluster_size", 1)),
            center_location=data.get("center_location", pi.location),
        )}
    except Exception as exc:
        print(f"[demand_intelligence_node] error: {exc}")
        return {"cluster": ClusterResult(
            cluster_id=f"cluster_{state.submission_id[:8]}",
            cluster_name=pi.category, cluster_size=1, center_location=pi.location,
        )}


def knowledge_fusion_node(state: AgentState) -> dict:
    pi = state.parsed_issue
    if pi is None:
        return {}
    cluster = state.cluster
    location = cluster.center_location if cluster else pi.location
    prompt = (
        f"Category: {pi.category}\nLocation: {location}\n\n"
        "Look up infrastructure data and existing development plans. "
        "Return JSON with keys: population, facility_count, nearest_facility_km, "
        "road_quality, infrastructure_gap (0-1), proposal_context."
    )
    try:
        result = knowledge_fusion_agent.invoke({"messages": [HumanMessage(content=prompt)]})
        data = _strip_json(_last_message_content(result))
        ctx = FusedContext(
            category=pi.category, location=location,
            demand_count=cluster.cluster_size if cluster else 1,
            population_affected=int(data.get("population", 0)),
            estimated_cost_inr=None, data_confidence="estimated",
            severity_score=float(data.get("infrastructure_gap", 0.5)),
            category_specific_data={k: v for k, v in data.items()
                                     if isinstance(v, (int, float, str))},
            is_existing_plan_project=False,
        )
        return {"knowledge_context": ctx}
    except Exception as exc:
        print(f"[knowledge_fusion_node] error: {exc}")
        if pi:
            return {"knowledge_context": FusedContext(
                category=pi.category, location=location, demand_count=1,
                population_affected=0, data_confidence="estimated",
                severity_score=0.5, is_existing_plan_project=False,
            )}
        return {}


def policy_recommendation_node(state: AgentState) -> dict:
    pi = state.parsed_issue
    cluster = state.cluster
    ctx = state.knowledge_context
    if pi is None:
        return {}
    cluster_size = cluster.cluster_size if cluster else 1
    location = cluster.center_location if cluster else pi.location
    infra_gap = ctx.severity_score if ctx else 0.5
    pop = ctx.population_affected if ctx else 0
    prompt = (
        f"Category: {pi.category}\nLocation: {location}\n"
        f"Citizen demand (cluster_size): {cluster_size}\n"
        f"Infrastructure gap (0-1): {infra_gap}\nPopulation affected: {pop}\n\n"
        "Use compute_priority_score and rank_projects tools to compute scores. "
        "Return JSON with keys: project_id, title, priority_score, breakdown "
        "(citizen_demand, severity, population_impact, cost_feasibility — all 0-100), reason."
    )
    try:
        result = policy_recommendation_agent.invoke({"messages": [HumanMessage(content=prompt)]})
        data = _strip_json(_last_message_content(result))
        bd = data.get("breakdown", {})
        project_id = data.get("project_id", f"proj_{state.submission_id[:8]}")
        rec = Recommendation(
            project_id=project_id,
            title=data.get("title", pi.summary[:80]),
            priority_score=float(data.get("priority_score", 50.0)),
            breakdown=ScoreBreakdown(
                citizen_demand=float(bd.get("citizen_demand", 0.0)),
                severity=float(bd.get("severity", 0.0)),
                population_impact=float(bd.get("population_impact", 0.0)),
                cost_feasibility=float(bd.get("cost_feasibility", 0.0)),
            ),
            is_existing_plan_project=False,
            explanation=None,
        )
        from app.services.store import STORE
        if ctx:
            STORE.upsert_context(project_id, ctx)
        STORE.upsert_recommendation(rec)
        return {"recommendation": rec}
    except Exception as exc:
        print(f"[policy_recommendation_node] error: {exc}")
        return {}


def explainability_node(state: AgentState) -> dict:
    rec = state.recommendation
    cluster = state.cluster
    ctx = state.knowledge_context
    if rec is None:
        return {}
    prompt = (
        f"Project: {rec.title}\nPriority score: {rec.priority_score}/100\n"
        f"Citizen demand score: {rec.breakdown.citizen_demand}\n"
        f"Infrastructure severity score: {rec.breakdown.severity}\n"
        f"Population impact score: {rec.breakdown.population_impact}\n"
        f"Cost feasibility score: {rec.breakdown.cost_feasibility}\n"
        f"Cluster size: {cluster.cluster_size if cluster else 'unknown'}\n"
        f"Infrastructure gap: {ctx.severity_score if ctx else 'unknown'}\n\n"
        "Generate evidence bullets and explanation for an MP. "
        "Return JSON with keys: evidence (list of 2-3 strings), summary (string), confidence_score (0-1)."
    )
    try:
        result = explainability_agent.invoke({"messages": [HumanMessage(content=prompt)]})
        data = _strip_json(_last_message_content(result))
        explanation = Explanation(
            evidence=data.get("evidence", []),
            summary=data.get("summary", ""),
            confidence_score=float(data.get("confidence_score", 0.7)),
        )
        updated_rec = rec.model_copy(update={"explanation": explanation})
        from app.services.store import STORE
        STORE.upsert_recommendation(updated_rec)
        return {"recommendation": updated_rec}
    except Exception as exc:
        print(f"[explainability_node] error: {exc}")
        return {}


def build_workflow(checkpointer=None):
    graph = StateGraph(AgentState)
    graph.add_node("citizen_intelligence_agent",  citizen_intelligence_node)
    graph.add_node("demand_intelligence_agent",   demand_intelligence_node)
    graph.add_node("knowledge_fusion_agent",      knowledge_fusion_node)
    graph.add_node("policy_recommendation_agent", policy_recommendation_node)
    graph.add_node("explainability_agent",        explainability_node)
    graph.add_node("vision_processing_agent",     vision_processing.run)
    graph.add_node("speech_processing_agent",     speech_processing.run)

    graph.add_conditional_edges(START, route_intake)
    for intake_node in ["speech_processing_agent", "vision_processing_agent"]:
        graph.add_edge(intake_node, "citizen_intelligence_agent")
    graph.add_edge("citizen_intelligence_agent",  "demand_intelligence_agent")
    graph.add_edge("demand_intelligence_agent",   "knowledge_fusion_agent")
    graph.add_edge("knowledge_fusion_agent",      "policy_recommendation_agent")
    graph.add_edge("policy_recommendation_agent", "explainability_agent")
    graph.add_edge("explainability_agent",        END)

    return graph.compile(checkpointer=checkpointer or MemorySaver())
```

---

### `backend/app/agents/citizen_intelligence_agent.py`
```python
from langgraph.prebuilt import create_react_agent
from app.core.llm import get_model
from app.tools.citizen_tools import extract_issue_details, detect_language

SYSTEM_PROMPT = """
You are the Citizen Intelligence Agent for MeriAwaaz AI.
Your job is to understand ONE citizen's submission and extract structured information from it.
The input may be in any language (English, Hindi, Tamil, etc.).

Always follow this sequence:
1. Call detect_language to identify the language.
2. Call extract_issue_details to parse the submission into structured fields.
3. Return a final structured JSON with: category, location, urgency, summary, confidence, language.

Never guess. If location is unclear, set it to "unspecified".
If category is unclear, choose the closest match from:
[Education, Healthcare, Roads, Water, Sanitation, Electricity, Vocational, Other]
"""

citizen_intelligence_agent = create_react_agent(
    model=get_model(),
    tools=[extract_issue_details, detect_language],
    prompt=SYSTEM_PROMPT,
    name="citizen_intelligence_agent",
)
```

---

### `backend/app/agents/demand_intelligence_agent.py`
```python
from langgraph.prebuilt import create_react_agent
from app.core.llm import get_model
from app.tools.demand_tools import search_similar_submissions, cluster_submissions

SYSTEM_PROMPT = """
You are the Demand Intelligence Agent for MeriAwaaz AI.
Your job is to analyse patterns across ALL citizen submissions — not just one.
You answer the question: "What are people repeatedly asking for?"

Always follow this sequence:
1. Call search_similar_submissions using the summary and category from the previous agent.
2. Call cluster_submissions on the results to identify the dominant demand cluster.
3. Return a structured JSON with: cluster_name, cluster_size, center_location.

Focus only on citizen demand patterns.
"""

demand_intelligence_agent = create_react_agent(
    model=get_model(),
    tools=[search_similar_submissions, cluster_submissions],
    prompt=SYSTEM_PROMPT,
    name="demand_intelligence_agent",
)
```

---

### `backend/app/agents/knowledge_fusion_agent.py`
```python
from langgraph.prebuilt import create_react_agent
from app.core.llm import get_model
from app.tools.knowledge_tools import lookup_infrastructure, lookup_plan_projects

SYSTEM_PROMPT = """
You are the Knowledge Fusion Agent for MeriAwaaz AI.
Your job is to answer: "What does public data say about reality in this area?"

Always follow this sequence:
1. Call lookup_infrastructure using the center_location and category from the demand cluster.
2. Call lookup_plan_projects to find existing development proposals for that area and category.
3. Return a structured JSON with: population, facility_count, nearest_facility_km,
   road_quality, infrastructure_gap, proposal_context.

Be factual. Do not invent numbers.
"""

knowledge_fusion_agent = create_react_agent(
    model=get_model(),
    tools=[lookup_infrastructure, lookup_plan_projects],
    prompt=SYSTEM_PROMPT,
    name="knowledge_fusion_agent",
)
```

---

### `backend/app/agents/policy_recommendation_agent.py`
```python
from langgraph.prebuilt import create_react_agent
from app.core.llm import get_model
from app.tools.policy_tools import compute_priority_score, rank_projects

SYSTEM_PROMPT = """
You are the Policy Recommendation Agent for MeriAwaaz AI.
You MUST use the compute_priority_score tool — never invent scores yourself.

Always follow this sequence:
1. For each candidate project, call compute_priority_score with the four normalised inputs:
   - citizen_demand: cluster_size / max_expected (cap at 1.0)
   - infrastructure_gap: from knowledge_fusion output
   - population_impact: population normalised against constituency average
   - cost_feasibility: 1.0 minus normalised estimated cost
2. Call rank_projects to sort them.
3. Return the top-ranked project as JSON with:
   project_id, title, priority_score, breakdown, reason.
"""

policy_recommendation_agent = create_react_agent(
    model=get_model(),
    tools=[compute_priority_score, rank_projects],
    prompt=SYSTEM_PROMPT,
    name="policy_recommendation_agent",
)
```

---

### `backend/app/agents/explainability_agent.py`
```python
from langgraph.prebuilt import create_react_agent
from app.core.llm import get_model
from app.tools.explainability_tools import build_evidence_bullets, compute_confidence_score

SYSTEM_PROMPT = """
You are the Explainability Agent for MeriAwaaz AI.
Your job is to explain WHY a project was recommended in plain, judge-facing language.
You never change scores — you only explain them.

Always follow this sequence:
1. Call build_evidence_bullets using the cluster and infrastructure data.
2. Call compute_confidence_score using the priority_score, cluster_size, and data_completeness.
3. Write a short human-readable summary (2-3 sentences).
4. Return JSON with: evidence (list of bullets), summary, confidence_score.
"""

explainability_agent = create_react_agent(
    model=get_model(),
    tools=[build_evidence_bullets, compute_confidence_score],
    prompt=SYSTEM_PROMPT,
    name="explainability_agent",
)
```

---

### `backend/app/agents/vision_processing.py`
```python
"""
Handles input_type == "image" or "video".
IMAGE: base64 inline → Gemini Vision
VIDEO: Gemini File API upload → visual+audio analysis
Result written into state.raw_text for the rest of the pipeline.
Hard limit: 50MB. Always deletes uploaded files.
"""
import base64, os, time
from pathlib import Path
import google.generativeai as genai
from langchain_core.messages import HumanMessage
from app.schemas.models import AgentState

MAX_FILE_BYTES = 50 * 1024 * 1024

IMAGE_MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
              ".png": "image/png", ".webp": "image/webp"}
VIDEO_MIME = {".mp4": "video/mp4", ".mov": "video/quicktime",
              ".avi": "video/x-msvideo", ".mkv": "video/x-matroska", ".webm": "video/webm"}

_IMAGE_PROMPT = (
    "Analyze this photo submitted by a citizen to their Member of Parliament in India.\n\n"
    "Return ONLY the following three lines — no markdown, no headers, no extra text:\n\n"
    "VISUAL: [2-3 sentences describing exactly what infrastructure problem is visible.]\n\n"
    "LOCATION: [Any visible location clues. Write 'No location clues visible' if none.]\n\n"
    "COMPLAINT: [One sentence written as the citizen's own words describing their request to the MP.]"
)

_VIDEO_PROMPT = (
    "Analyze this video submitted by a citizen to their Member of Parliament in India.\n\n"
    "Return ONLY the following four lines — no markdown, no headers, no extra text:\n\n"
    "VISUAL: [2-3 sentences describing what infrastructure problem is visible in the footage.]\n\n"
    "AUDIO: [Exact transcription of everything spoken. Write 'No speech detected' if silent.]\n\n"
    "LOCATION: [Any visible or spoken location clues. Write 'No location clues' if none.]\n\n"
    "COMPLAINT: [One sentence combining visual + audio into the citizen's complaint to the MP.]"
)

def _file_size_ok(path): return os.path.getsize(path) <= MAX_FILE_BYTES

def _process_image(file_path):
    ext = Path(file_path).suffix.lower()
    mime = IMAGE_MIME.get(ext, "image/jpeg")
    b64 = base64.standard_b64encode(Path(file_path).read_bytes()).decode("utf-8")
    from app.core.llm import get_model
    response = get_model().invoke([HumanMessage(content=[
        {"type": "text", "text": _IMAGE_PROMPT},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
    ])])
    return response.content if hasattr(response, "content") else str(response)

def _process_video(file_path):
    ext = Path(file_path).suffix.lower()
    mime = VIDEO_MIME.get(ext, "video/mp4")
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    video_file = genai.upload_file(path=file_path, mime_type=mime)
    max_wait, waited = 90, 0
    while video_file.state.name == "PROCESSING" and waited < max_wait:
        time.sleep(3); waited += 3
        video_file = genai.get_file(video_file.name)
    if video_file.state.name != "ACTIVE":
        genai.delete_file(video_file.name)
        raise RuntimeError(f"Gemini file ended in state: {video_file.state.name}")
    try:
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content([video_file, _VIDEO_PROMPT])
        return response.text
    finally:
        genai.delete_file(video_file.name)

def run(state: AgentState) -> dict:
    file_path = state.media_file_path
    input_type = state.input_type
    if not file_path or not Path(file_path).exists():
        return {"raw_text": f"A citizen submitted a {input_type} showing a civic problem.",
                "error": f"Media file not found: {file_path}"}
    if not _file_size_ok(file_path):
        size_mb = os.path.getsize(file_path) / (1024*1024)
        return {"raw_text": f"A citizen submitted a {input_type} showing a civic problem.",
                "error": f"File rejected: {size_mb:.1f} MB exceeds 50 MB limit."}
    ext = Path(file_path).suffix.lower()
    if input_type == "image" and ext not in IMAGE_MIME:
        return {"raw_text": "A citizen submitted a photo showing a civic problem.",
                "error": f"Unsupported image format: {ext}"}
    if input_type == "video" and ext not in VIDEO_MIME:
        return {"raw_text": "A citizen submitted a video showing a civic problem.",
                "error": f"Unsupported video format: {ext}"}
    try:
        raw = _process_video(file_path) if input_type == "video" else _process_image(file_path)
        return {"raw_text": raw.strip()}
    except Exception as e:
        return {"raw_text": f"A citizen submitted a {input_type} showing a civic problem.",
                "error": f"Vision processing failed: {str(e)}"}
```

---

### `backend/app/agents/speech_processing.py`
```python
"""
Handles input_type == "voice".
Uploads audio to Gemini File API, gets exact transcript,
sets state.raw_text and state.audio_url.
Hard limit: 50MB.
"""
import os, time
from pathlib import Path
import google.generativeai as genai
from app.schemas.models import AgentState

MAX_FILE_BYTES = 50 * 1024 * 1024
AUDIO_MIME = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4",
              ".ogg": "audio/ogg", ".flac": "audio/flac", ".aac": "audio/aac",
              ".webm": "audio/webm"}

_TRANSCRIBE_PROMPT = (
    "Transcribe every word spoken in this audio recording exactly as said. "
    "Do NOT summarize, paraphrase, or add any commentary. "
    "If the speaker is using Hindi, Marathi, or any other Indian language, "
    "transcribe in that language using its native script. "
    "If the audio is silent or unintelligible, write only: [No speech detected]"
)

def run(state: AgentState) -> dict:
    file_path = state.media_file_path
    if not file_path or not Path(file_path).exists():
        return {"raw_text": "", "error": f"Audio file not found: {file_path}"}
    if os.path.getsize(file_path) > MAX_FILE_BYTES:
        size_mb = os.path.getsize(file_path) / (1024*1024)
        return {"raw_text": "", "error": f"Audio rejected: {size_mb:.1f} MB > 50 MB limit."}
    ext = Path(file_path).suffix.lower()
    if ext not in AUDIO_MIME:
        return {"raw_text": "", "error": f"Unsupported audio format: {ext}"}
    filename = Path(file_path).name
    audio_url = f"/uploads/{filename}"
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        audio_file = genai.upload_file(path=file_path, mime_type=AUDIO_MIME[ext])
        max_wait, waited = 60, 0
        while audio_file.state.name == "PROCESSING" and waited < max_wait:
            time.sleep(2); waited += 2
            audio_file = genai.get_file(audio_file.name)
        if audio_file.state.name != "ACTIVE":
            genai.delete_file(audio_file.name)
            return {"raw_text": "", "audio_url": audio_url,
                    "error": f"Gemini audio failed: {audio_file.state.name}"}
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content([audio_file, _TRANSCRIBE_PROMPT])
        genai.delete_file(audio_file.name)
        return {"raw_text": response.text.strip(), "audio_url": audio_url}
    except Exception as e:
        return {"raw_text": "", "audio_url": audio_url,
                "error": f"Speech processing failed: {str(e)}"}
```

---

### `backend/app/tools/citizen_tools.py`
```python
import json, re
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

_CATEGORIES = ["Education", "Healthcare", "Roads", "Water",
               "Sanitation", "Electricity", "Vocational", "Other"]

def _parse_json(text):
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    return json.loads(text)

@tool
def extract_issue_details(text: str) -> dict:
    """Extract category, location, summary, confidence from raw citizen text."""
    from app.core.llm import get_model
    prompt = (
        "You are analyzing a citizen complaint submitted to an Indian MP.\n\n"
        "Return ONLY valid JSON:\n"
        f'{{"category": one of {_CATEGORIES}, "location": "ward/village or unspecified", '
        '"summary": "one-sentence summary", "confidence": 0.0-1.0}}\n\n'
        f'Citizen submission:\n"""{text}"""'
    )
    response = get_model().invoke([HumanMessage(content=prompt)])
    content = response.content if hasattr(response, "content") else str(response)
    try:
        result = _parse_json(content)
        if result.get("category") not in _CATEGORIES:
            result["category"] = "Other"
        result["confidence"] = float(result.get("confidence", 0.7))
        result.setdefault("location", "unspecified")
        result.setdefault("summary", text[:120])
        return result
    except Exception:
        return {"category": "Other", "location": "unspecified",
                "summary": text[:120], "confidence": 0.3}

@tool
def detect_language(text: str) -> str:
    """Detect ISO 639-1 language code from text."""
    from app.core.llm import get_model
    prompt = (
        "Detect the language of the text below.\n"
        "Return ONLY the ISO 639-1 two-letter code (e.g. en, hi, mr, ta, te, bn).\n"
        "No punctuation, no explanation — just the code.\n\n"
        f'Text: """{text[:300]}"""'
    )
    response = get_model().invoke([HumanMessage(content=prompt)])
    content = response.content if hasattr(response, "content") else str(response)
    code = content.strip().lower().replace('"', "").replace("'", "").split()[0]
    return code[:3] if (2 <= len(code) <= 3 and code.isalpha()) else "en"
```

---

### `backend/app/tools/demand_tools.py`
```python
import json, uuid
from langchain_core.tools import tool
from app.services import chroma_client
from app.services.store import STORE
from app.schemas.models import ClusterResult
from app.core.llm import get_model

_llm = None
def _get_llm():
    global _llm
    if _llm is None: _llm = get_model()
    return _llm

@tool
def search_similar_submissions(summary: str, category: str, top_k: int = 10) -> list[dict]:
    """Search ChromaDB for citizen submissions similar to the current one."""
    return chroma_client.query_similar(text=summary, category=category, top_k=top_k)

@tool
def cluster_submissions(submissions: list[dict], current_summary: str,
                        category: str, location: str) -> dict:
    """Use Gemini to cluster submissions. Returns cluster_id, cluster_name, cluster_size, center_location."""
    existing_clusters = [
        {"cluster_id": cid, "cluster_name": c.cluster_name,
         "center_location": c.center_location, "cluster_size": c.cluster_size}
        for cid, c in STORE.clusters.items()
        if c.cluster_name.lower() == category.lower()
    ]
    similar_texts = [s.get("summary", "") for s in submissions if s.get("summary")]
    prompt = f"""You are a demand clustering agent.

Current submission:
  Category: {category}, Location: {location}, Summary: {current_summary}

Similar past submissions ({len(similar_texts)} found):
{json.dumps(similar_texts, indent=2) if similar_texts else "None yet."}

Existing clusters: {json.dumps(existing_clusters, indent=2) if existing_clusters else "None yet."}

Return ONLY valid JSON:
{{"cluster_id": "existing_id_or_new", "cluster_name": "short name", "center_location": "location"}}"""

    response = _get_llm().invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)
    content = content.strip().strip("```json").strip("```").strip()
    try:
        gemini_result = json.loads(content)
    except Exception:
        gemini_result = {"cluster_id": "new", "cluster_name": category, "center_location": location}

    chosen_id = gemini_result.get("cluster_id", "new")
    cluster_name = gemini_result.get("cluster_name", category)
    center_location = gemini_result.get("center_location", location)

    if chosen_id != "new" and chosen_id in STORE.clusters:
        STORE.clusters[chosen_id].cluster_size += 1
        cluster = STORE.clusters[chosen_id]
    else:
        new_id = f"cluster_{uuid.uuid4().hex[:8]}"
        STORE.clusters[new_id] = ClusterResult(
            cluster_id=new_id, cluster_name=cluster_name,
            cluster_size=len(submissions) + 1, center_location=center_location,
        )
        cluster = STORE.clusters[new_id]

    return {"cluster_id": cluster.cluster_id, "cluster_name": cluster.cluster_name,
            "cluster_size": cluster.cluster_size, "center_location": cluster.center_location}
```

---

### `backend/app/tools/knowledge_tools.py`
```python
from langchain_core.tools import tool
from app.config import CATEGORY_CONFIG, CONSTITUENCY
from app.services import need_scoring

@tool
def lookup_infrastructure(location: str, category: str) -> dict:
    """Look up infrastructure gap score for category using government datasets. Returns 0-1 infrastructure_gap."""
    config = CATEGORY_CONFIG.get(category)
    if config is None:
        return {"population": 0, "facility_count": 0, "nearest_facility_km": 0.0,
                "road_quality": "unknown", "infrastructure_gap": 0.5, "data_confidence": "estimated"}
    records = need_scoring.load_json(config["dataset"])
    lookup_value = CONSTITUENCY["state"] if config["location_level"] == "state" else CONSTITUENCY["district"]
    record = need_scoring.match_by_location(lookup_value, records, config["location_field"])
    if record is None:
        return {"population": 0, "facility_count": 0, "nearest_facility_km": 0.0,
                "road_quality": "unknown", "infrastructure_gap": 0.5, "data_confidence": "estimated"}
    all_values = [r.get(config["need_field"]) for r in records]
    raw_value = float(record.get(config["need_field"]) or 0.0)
    gap = need_scoring.normalize(raw_value, all_values, config["direction"])
    facility_count = int(record.get("dispensary_count") or record.get("total_schools") or 0)
    return {"population": 0, "facility_count": facility_count, "nearest_facility_km": 0.0,
            "road_quality": "unknown", "infrastructure_gap": round(gap, 4), "data_confidence": "real_data"}

@tool
def lookup_plan_projects(location: str, category: str) -> list[dict]:
    """Look up existing development plan proposals for a location and category."""
    from app.services.store import STORE
    results = []
    location_lower = location.strip().lower()
    for project_id, ctx in STORE._contexts.items():
        if ctx.category != category:
            continue
        ctx_loc = ctx.location.strip().lower()
        if location_lower != "unspecified" and location_lower not in ctx_loc and ctx_loc not in location_lower:
            continue
        rec = STORE.get_recommendation(project_id)
        results.append({
            "project_id": project_id,
            "title": ctx.category_specific_data.get("title", project_id),
            "estimated_cost": ctx.estimated_cost_inr or 0,
            "status": "planned" if ctx.is_existing_plan_project else "proposed",
            "priority_score": rec.priority_score if rec else 0.0,
        })
    return results
```

---

### `backend/app/tools/policy_tools.py`
```python
from langchain_core.tools import tool

@tool
def compute_priority_score(citizen_demand: float, infrastructure_gap: float,
                           population_impact: float, cost_feasibility: float) -> dict:
    """Compute deterministic priority score. All inputs 0.0-1.0. Returns priority_score + breakdown."""
    score = (0.40 * citizen_demand + 0.30 * infrastructure_gap
             + 0.20 * population_impact + 0.10 * cost_feasibility)
    return {
        "priority_score": round(score, 4),
        "breakdown": {
            "citizen_demand": round(0.40 * citizen_demand, 4),
            "infrastructure_gap": round(0.30 * infrastructure_gap, 4),
            "population_impact": round(0.20 * population_impact, 4),
            "cost_feasibility": round(0.10 * cost_feasibility, 4),
        },
    }

@tool
def rank_projects(projects: list[dict]) -> list[dict]:
    """Sort projects by priority_score descending."""
    return sorted(projects, key=lambda p: p.get("priority_score", 0), reverse=True)
```

---

### `backend/app/tools/explainability_tools.py`
```python
from langchain_core.tools import tool

@tool
def build_evidence_bullets(cluster_size: int, infrastructure_gap: float,
                           population: int, facility_count: int, category: str) -> list[str]:
    """Build 2-3 evidence bullets for a recommendation."""
    return [
        f"{cluster_size} citizens submitted {category.lower()} related requests.",
        f"Only {facility_count} existing {category.lower()} facilit{'y' if facility_count == 1 else 'ies'} serving a population of {population:,}.",
        f"Infrastructure gap score: {infrastructure_gap:.0%}.",
    ]

@tool
def compute_confidence_score(priority_score: float, cluster_size: int, data_completeness: float) -> float:
    """Compute confidence in recommendation (0-1). Caps at 50 submissions for full signal."""
    demand_signal = min(cluster_size / 50, 1.0)
    return round(0.50 * priority_score + 0.30 * demand_signal + 0.20 * data_completeness, 4)
```

---

### `backend/app/services/store.py`
```python
import json, os
from typing import Optional
from app.schemas.models import FusedContext, Recommendation, ScoreBreakdown, ClusterResult

class _Store:
    def __init__(self):
        self._contexts: dict[str, FusedContext] = {}
        self._recommendations: dict[str, Recommendation] = {}
        self.clusters: dict[str, ClusterResult] = {}
        self.cluster_submissions: dict[str, list[dict]] = {}

    def upsert_context(self, project_id, ctx): self._contexts[project_id] = ctx
    def get_context(self, project_id): return self._contexts.get(project_id)
    def all_contexts(self): return list(self._contexts.values())
    def upsert_recommendation(self, rec): self._recommendations[rec.project_id] = rec
    def get_recommendation(self, project_id): return self._recommendations.get(project_id)
    def all_recommendations_sorted(self):
        return sorted(self._recommendations.values(), key=lambda r: r.priority_score, reverse=True)

    def load_local_plans(self, json_path: str) -> None:
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
                category=plan["category"], location=location, demand_count=0,
                population_affected=pop, estimated_cost_inr=cost, data_confidence="synthetic",
                severity_score=0.5, category_specific_data={"title": plan["title"], "source": plan.get("source", "handbuilt")},
                is_existing_plan_project=True,
            )
            self.upsert_context(plan["plan_id"], ctx)
            from app.tools.policy_tools import compute_priority_score
            result = compute_priority_score.invoke({
                "citizen_demand": 0.0, "infrastructure_gap": 0.5,
                "population_impact": min(pop / 15000, 1.0),
                "cost_feasibility": max(0.0, 1.0 - cost / 10_000_000),
            })
            bd = result["breakdown"]
            rec = Recommendation(
                project_id=plan["plan_id"], title=plan["title"],
                priority_score=round(result["priority_score"] * 100, 2),
                breakdown=ScoreBreakdown(
                    citizen_demand=round(bd["citizen_demand"] * 100, 2),
                    severity=round(bd["infrastructure_gap"] * 100, 2),
                    population_impact=round(bd["population_impact"] * 100, 2),
                    cost_feasibility=round(bd["cost_feasibility"] * 100, 2),
                ),
                is_existing_plan_project=True, explanation=None,
            )
            self.upsert_recommendation(rec)
        print(f"Store: loaded {len(plans)} local plan projects.")

STORE = _Store()
```

---

### `backend/app/services/chroma_client.py`
```python
"""ChromaDB with Gemini text-embedding-004 (768 dims). Sentinel pattern prevents wipe on restart."""
import os
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
import google.generativeai as genai
from app.schemas.settings import settings

COLLECTION_NAME = "citizen_submissions"
EMBEDDING_MODEL = "models/text-embedding-004"

class _GeminiEmbeddings(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        return [genai.embed_content(model=EMBEDDING_MODEL, content=text,
                                    task_type="retrieval_document")["embedding"]
                for text in input]

_embed_fn = _GeminiEmbeddings()
_collection = None
_SENTINEL_ID = "__embedding_model__"
_SENTINEL_VALUE = EMBEDDING_MODEL

def get_collection():
    global _collection
    if _collection is not None: return _collection
    client = chromadb.PersistentClient(path=settings.chroma_path)
    needs_reset = False
    try:
        existing = client.get_collection(name=COLLECTION_NAME, embedding_function=_embed_fn)
        sentinel = existing.get(ids=[_SENTINEL_ID])
        if not sentinel["ids"] or sentinel["metadatas"][0].get("model") != _SENTINEL_VALUE:
            needs_reset = True
        else:
            _collection = existing
    except Exception:
        needs_reset = True
    if needs_reset:
        try: client.delete_collection(name=COLLECTION_NAME)
        except Exception: pass
        _collection = client.create_collection(name=COLLECTION_NAME, embedding_function=_embed_fn,
                                               metadata={"hnsw:space": "cosine"})
        _collection.add(ids=[_SENTINEL_ID], documents=["sentinel"],
                        metadatas=[{"model": _SENTINEL_VALUE}])
    return _collection

def add_submission(submission_id: str, text: str, metadata: dict) -> None:
    get_collection().add(ids=[submission_id], documents=[text], metadatas=[metadata])

def query_similar(text: str, category: str, top_k: int = 10) -> list[dict]:
    col = get_collection()
    real_count = col.count() - 1  # subtract sentinel
    if real_count <= 0: return []
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    query_embedding = genai.embed_content(model=EMBEDDING_MODEL, content=text,
                                          task_type="retrieval_query")["embedding"]
    results = col.query(query_embeddings=[query_embedding],
                        n_results=min(top_k, real_count),
                        where={"category": category})
    return [{"submission_id": doc_id, "summary": results["documents"][0][i],
             "location": results["metadatas"][0][i].get("location", "unspecified"),
             "similarity_score": 1.0 - results["distances"][0][i]}
            for i, doc_id in enumerate(results["ids"][0])]
```

---

### `backend/app/services/database.py`
```python
import os, sqlite3
from datetime import datetime
from app.schemas.settings import settings

def _get_db_path():
    path = settings.database_url.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    return path

def _connect():
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _connect()
    conn.cursor().executescript("""
        CREATE TABLE IF NOT EXISTS submissions (
            id TEXT PRIMARY KEY, created_at TEXT NOT NULL, input_type TEXT NOT NULL,
            raw_text TEXT NOT NULL, category TEXT, location TEXT, summary TEXT,
            confidence REAL, language TEXT, cluster_id TEXT,
            photo_url TEXT, video_url TEXT, audio_url TEXT
        );
        CREATE TABLE IF NOT EXISTS clusters (
            cluster_id TEXT PRIMARY KEY, cluster_name TEXT NOT NULL, category TEXT NOT NULL,
            center_location TEXT NOT NULL, cluster_size INTEGER NOT NULL, last_updated TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS recommendations (
            project_id TEXT PRIMARY KEY, title TEXT NOT NULL, category TEXT NOT NULL,
            location TEXT NOT NULL, priority_score REAL NOT NULL, citizen_demand REAL NOT NULL,
            severity REAL NOT NULL, population_impact REAL NOT NULL, cost_feasibility REAL NOT NULL,
            is_existing_plan_project INTEGER NOT NULL DEFAULT 0, data_confidence TEXT NOT NULL,
            last_updated TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS agent_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, submission_id TEXT NOT NULL,
            agent_name TEXT NOT NULL, status TEXT NOT NULL, duration_ms INTEGER, created_at TEXT NOT NULL
        );
    """)
    # Auto-migrate older DBs missing columns
    for col_sql in ["ALTER TABLE submissions ADD COLUMN photo_url TEXT",
                    "ALTER TABLE submissions ADD COLUMN video_url TEXT",
                    "ALTER TABLE submissions ADD COLUMN audio_url TEXT"]:
        try: conn.execute(col_sql); conn.commit()
        except Exception: pass
    conn.close()

def insert_submission(sub: dict):
    conn = _connect()
    conn.execute("""
        INSERT OR IGNORE INTO submissions
        (id, created_at, input_type, raw_text, category, location, summary,
         confidence, language, cluster_id, photo_url, video_url, audio_url)
        VALUES (:id, :created_at, :input_type, :raw_text, :category, :location, :summary,
                :confidence, :language, :cluster_id, :photo_url, :video_url, :audio_url)
    """, sub); conn.commit(); conn.close()

def get_submission(submission_id):
    conn = _connect()
    row = conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()
    conn.close(); return dict(row) if row else None

def count_all_submissions():
    conn = _connect()
    row = conn.execute("SELECT COUNT(*) as total FROM submissions").fetchone()
    conn.close(); return row["total"] if row else 0

def get_last_updated():
    conn = _connect()
    row = conn.execute("SELECT MAX(last_updated) as last_updated FROM recommendations").fetchone()
    conn.close()
    result = dict(row) if row else None
    return result.get("last_updated") if result else None
```

---

### `backend/app/api/submissions.py`
```python
import shutil, uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from app.schemas.models import AgentState, ParsedIssue, Recommendation, ScoreBreakdown
from app.services import database, chroma_client
from app.services.store import STORE

UPLOADS_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"

try:
    from app.supervisor import build_workflow
    _pipeline = build_workflow()
    _PIPELINE_AVAILABLE = True
except Exception:
    _PIPELINE_AVAILABLE = False

router = APIRouter()

class SubmissionResponse(BaseModel):
    id: str; created_at: str; input_type: str; raw_text: str
    category: Optional[str] = None; location: Optional[str] = None
    summary: Optional[str] = None; confidence: Optional[float] = None
    language: Optional[str] = None; cluster_id: Optional[str] = None
    photo_url: Optional[str] = None; video_url: Optional[str] = None
    audio_url: Optional[str] = None
    parsed_issue: Optional[ParsedIssue] = None
    recommendation: Optional[Recommendation] = None

@router.post("/api/submissions")
async def create_submission(
    channel: str = Form("text"),
    text: str = Form(""),
    photo: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
):
    sid = str(uuid.uuid4())
    channel_map = {"text": "text", "voice": "voice", "photo": "image", "image": "image"}
    input_type = channel_map.get(channel, "text")
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    photo_url = saved_path = None
    if photo and photo.filename:
        ext = Path(photo.filename).suffix.lower() or ".jpg"
        filename = f"{sid}{ext}"
        dest = UPLOADS_DIR / filename
        with dest.open("wb") as f: shutil.copyfileobj(photo.file, f)
        photo_url = f"/uploads/{filename}"; saved_path = str(dest)

    audio_url = None
    if audio and audio.filename and input_type == "voice":
        ext = Path(audio.filename).suffix.lower() or ".mp3"
        audio_filename = f"{sid}_audio{ext}"
        audio_dest = UPLOADS_DIR / audio_filename
        with audio_dest.open("wb") as f: shutil.copyfileobj(audio.file, f)
        audio_url = f"/uploads/{audio_filename}"; saved_path = str(audio_dest)

    recommendation = parsed_issue = None
    if _PIPELINE_AVAILABLE:
        state = AgentState(submission_id=sid, input_type=input_type,
                           raw_text=text, media_file_path=saved_path)
        result = _pipeline.invoke(state, config={"configurable": {"thread_id": sid}})
        if isinstance(result, dict):
            pi = result.get("parsed_issue")
            parsed_issue = pi if isinstance(pi, ParsedIssue) else None
            rec = result.get("recommendation")
            recommendation = rec if isinstance(rec, Recommendation) else None
            if not audio_url: audio_url = result.get("audio_url")
        else:
            parsed_issue = getattr(result, "parsed_issue", None)
            recommendation = getattr(result, "recommendation", None)
            if not audio_url: audio_url = getattr(result, "audio_url", None)

    effective_text = text or (parsed_issue.summary if parsed_issue else "")
    database.insert_submission({
        "id": sid, "created_at": datetime.utcnow().isoformat(),
        "input_type": input_type, "raw_text": effective_text,
        "category": parsed_issue.category if parsed_issue else None,
        "location": parsed_issue.location if parsed_issue else None,
        "summary": parsed_issue.summary if parsed_issue else None,
        "confidence": parsed_issue.confidence if parsed_issue else None,
        "language": parsed_issue.language if parsed_issue else None,
        "cluster_id": recommendation.project_id if recommendation else None,
        "photo_url": photo_url, "video_url": None, "audio_url": audio_url,
    })
    chroma_client.add_submission(
        submission_id=sid, text=effective_text or "photo submission",
        metadata={"category": parsed_issue.category if parsed_issue else "Other",
                  "location": parsed_issue.location if parsed_issue else "unspecified"},
    )
    return {
        "status": "processed" if _PIPELINE_AVAILABLE else "stored",
        "submission_id": sid, "photo_url": photo_url, "audio_url": audio_url,
        "recommendation": recommendation.model_dump() if recommendation else None,
    }

@router.get("/api/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: str):
    sub = database.get_submission(submission_id)
    if sub is None:
        raise HTTPException(status_code=404, detail=f"Submission '{submission_id}' not found.")
    cluster_id = sub.get("cluster_id")
    recommendation = None
    if cluster_id:
        rec = STORE.get_recommendation(cluster_id)
        recommendation = rec.model_copy(update={"explanation": None}) if rec else None
    try:
        parsed_issue = ParsedIssue(category=sub["category"], location=sub["location"],
            summary=sub["summary"], confidence=sub["confidence"], language=sub["language"])
    except Exception:
        parsed_issue = None
    return SubmissionResponse(
        id=sub["id"], created_at=sub["created_at"], input_type=sub["input_type"],
        raw_text=sub["raw_text"], category=sub.get("category"), location=sub.get("location"),
        summary=sub.get("summary"), confidence=sub.get("confidence"), language=sub.get("language"),
        cluster_id=cluster_id, photo_url=sub.get("photo_url"), video_url=sub.get("video_url"),
        audio_url=sub.get("audio_url"), parsed_issue=parsed_issue, recommendation=recommendation,
    )
```

---

### `backend/app/api/video.py`
```python
"""POST /api/submissions/video — separate endpoint for video submissions."""
import shutil, uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.schemas.models import AgentState, ParsedIssue, Recommendation
from app.services import database, chroma_client

UPLOADS_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"
MAX_FILE_BYTES = 50 * 1024 * 1024
SUPPORTED_VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

try:
    from app.supervisor import build_workflow
    _pipeline = build_workflow()
    _PIPELINE_AVAILABLE = True
except Exception:
    _PIPELINE_AVAILABLE = False

router = APIRouter()

@router.post("/api/submissions/video")
async def create_video_submission(channel: str = Form("video"), video: UploadFile = File(...)):
    sid = str(uuid.uuid4())
    ext = Path(video.filename or "").suffix.lower()
    if ext not in SUPPORTED_VIDEO_EXT:
        raise HTTPException(status_code=415, detail=f"Unsupported format '{ext}'.")
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{sid}{ext}"; dest = UPLOADS_DIR / filename
    with dest.open("wb") as f: shutil.copyfileobj(video.file, f)
    file_size = dest.stat().st_size
    if file_size > MAX_FILE_BYTES:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=413, detail=f"Video exceeds 50 MB ({file_size/1024/1024:.1f} MB).")
    video_url = f"/uploads/{filename}"; saved_path = str(dest)
    recommendation = parsed_issue = None
    if _PIPELINE_AVAILABLE:
        state = AgentState(submission_id=sid, input_type="video",
                           raw_text="", media_file_path=saved_path)
        result = _pipeline.invoke(state, config={"configurable": {"thread_id": sid}})
        if isinstance(result, dict):
            pi = result.get("parsed_issue")
            parsed_issue = pi if isinstance(pi, ParsedIssue) else None
            rec = result.get("recommendation")
            recommendation = rec if isinstance(rec, Recommendation) else None
        else:
            parsed_issue = getattr(result, "parsed_issue", None)
            recommendation = getattr(result, "recommendation", None)
    effective_text = parsed_issue.summary if parsed_issue else "video submission"
    database.insert_submission({
        "id": sid, "created_at": datetime.utcnow().isoformat(), "input_type": "video",
        "raw_text": effective_text,
        "category": parsed_issue.category if parsed_issue else None,
        "location": parsed_issue.location if parsed_issue else None,
        "summary": parsed_issue.summary if parsed_issue else None,
        "confidence": parsed_issue.confidence if parsed_issue else None,
        "language": parsed_issue.language if parsed_issue else None,
        "cluster_id": recommendation.project_id if recommendation else None,
        "photo_url": None, "video_url": video_url, "audio_url": None,
    })
    chroma_client.add_submission(submission_id=sid, text=effective_text,
        metadata={"category": parsed_issue.category if parsed_issue else "Other",
                  "location": parsed_issue.location if parsed_issue else "unspecified"})
    return {"status": "processed" if _PIPELINE_AVAILABLE else "stored",
            "submission_id": sid, "video_url": video_url,
            "recommendation": recommendation.model_dump() if recommendation else None}
```

---

### `backend/app/api/dashboard.py`
```python
from datetime import datetime
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.dashboard import DashboardData, HeatmapPoint, ProjectCard
from app.services import database
from app.services.store import STORE

router = APIRouter()

class DashboardRefreshResponse(BaseModel):
    count: int

@router.get("/api/dashboard", response_model=DashboardData)
def get_dashboard():
    recs = STORE.all_recommendations_sorted()
    projects = []
    for rec in recs:
        ctx = STORE.get_context(rec.project_id)
        category = ctx.category if ctx else "Other"
        projects.append(ProjectCard(id=rec.project_id, title=rec.title, category=category,
            priority_score=rec.priority_score, breakdown=rec.breakdown,
            is_existing_plan_project=rec.is_existing_plan_project))
    total_submissions = database.count_all_submissions()
    last_updated_raw = database.get_last_updated()
    last_updated = last_updated_raw if last_updated_raw else datetime.utcnow().isoformat()
    return DashboardData(projects=projects, heatmap=[], total_submissions=total_submissions,
                         last_updated=last_updated)

@router.post("/api/dashboard-refresh", response_model=DashboardRefreshResponse)
def dashboard_refresh():
    contexts = STORE.all_contexts()
    for ctx in contexts:
        pass  # TODO: re-score with Policy Agent
    return DashboardRefreshResponse(count=len(contexts))
```

---

### `backend/app/api/recommendations.py`
```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.models import Recommendation
from app.services.store import STORE

router = APIRouter()

class RecommendationsResponse(BaseModel):
    items: list[Recommendation]

@router.get("/api/recommendations", response_model=RecommendationsResponse)
def get_recommendations():
    return RecommendationsResponse(items=STORE.all_recommendations_sorted())
```

---

### `backend/app/api/explain.py`  ← HAS BUG (see Bug A above)
```python
from fastapi import APIRouter, HTTPException
from app.schemas.models import AgentState, Explanation
from app.services.store import STORE

# This endpoint has a bug: _invoke_explainability passes state.model_dump() to
# the raw create_react_agent which expects {"messages": [...]}. 
# Fix: replace _invoke_explainability with a call to explainability_node from supervisor.py
try:
    from app.agents.explainability_agent import explainability_agent
    _AGENT_AVAILABLE = True
except ImportError:
    _AGENT_AVAILABLE = False

router = APIRouter()

def _invoke_explainability(state: AgentState) -> Explanation:
    # BROKEN — same MessagesState mismatch. Use explainability_node from supervisor instead.
    result = explainability_agent.invoke(state.model_dump())
    rec_result = result.get("recommendation") or {}
    explanation_data = (rec_result.get("explanation") if isinstance(rec_result, dict)
                        else getattr(rec_result, "explanation", None))
    if not explanation_data:
        raise ValueError("No explanation produced.")
    return explanation_data if isinstance(explanation_data, Explanation) else Explanation(**explanation_data)

@router.get("/api/explain/{project_id}", response_model=Explanation)
def explain_project(project_id: str):
    if not _AGENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Explainability Agent unavailable.")
    rec = STORE.get_recommendation(project_id)
    if rec is None:
        raise HTTPException(status_code=404, detail=f"No recommendation for '{project_id}'.")
    ctx = STORE.get_context(project_id)
    if ctx is None:
        raise HTTPException(status_code=404, detail=f"No context for '{project_id}'.")
    state = AgentState(submission_id=f"explain__{project_id}", input_type="text",
                       recommendation=rec, knowledge_context=ctx)
    try:
        return _invoke_explainability(state)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Agent produced no output: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent failed: {e}")
```

---

## 9. Seed Data: `local_plans.json` — 8 Projects

| plan_id | category | title | location |
|---------|----------|-------|----------|
| plan_001 | Education | Additional classroom block - Rampur Govt Primary School | Rampur |
| plan_002 | Healthcare | Upgrade of Primary Health Sub-Centre - Kesarpur | Kesarpur |
| plan_003 | Roads | Repair and widening of main village road - Sultanpur | Sultanpur |
| plan_004 | Water | Overhead water tank and pipeline - Bhelupur | Bhelupur |
| plan_005 | Sanitation | Community toilet complex - Rampur | Rampur |
| plan_006 | Electricity | Solar street lighting - Kesarpur main road | Kesarpur |
| plan_007 | Vocational | ITI skill development centre - Sultanpur | Sultanpur |
| plan_008 | Other | Community hall and digital kiosk - Bhelupur | Bhelupur |

All 8 load at startup into STORE with `citizen_demand=0.0` and `infrastructure_gap=0.5` (no real data for Roads/Water/Sanitation/Electricity/Vocational — those return estimated 0.5).

---

## 10. API Endpoints Summary

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check → `{"status": "ok"}` |
| POST | `/api/submissions` | Submit text/voice/photo → runs pipeline |
| GET | `/api/submissions/{id}` | Get single submission record |
| POST | `/api/submissions/video` | Submit video → runs pipeline |
| GET | `/api/dashboard` | Full dashboard: ranked projects + stats |
| POST | `/api/dashboard-refresh` | Re-score all contexts (TODO) |
| GET | `/api/recommendations` | All recommendations sorted by score |
| GET | `/api/explain/{project_id}` | On-demand explanation (BUG — see Bug A) |
| GET | `/uploads/{filename}` | Serve uploaded media files (static) |

---

## 11. Current Status & What's Left

### Working (after last session)
- Server starts and loads 8 seed projects ✓
- SQLite stores submissions correctly ✓
- ChromaDB uses Gemini text-embedding-004 with sentinel ✓
- GET /api/dashboard returns projects ✓
- Pipeline builds successfully (supervisor.py fixed) ✓
- vision_processing.py and speech_processing.py both implemented ✓
- POST /api/submissions/video endpoint exists ✓

### Needs verification
- **500 error on POST /api/submissions** — the supervisor.py fix was applied at end of last session but NOT YET TESTED. This is the first thing to verify.
- Whether `_PIPELINE_AVAILABLE = True` after the supervisor fix (check by looking at server startup logs — if no crash on build_workflow(), the pipeline is available)

### Still broken (unfixed bugs)
- **Bug A**: `explain.py` — MessagesState mismatch (same fix as supervisor.py)
- **Bug B**: `.env` has `GEMINI_MODEL=gemini-3.5-flash` → change to `gemini-2.0-flash`
- **Bug C**: `chroma_client.query_similar` sentinel count issue (already shown as fixed code above — apply to file)
- **Bug D**: `dashboard-refresh` does nothing (low priority for hackathon)

### Pending work for hackathon
1. Fix Bug A (explain.py) and Bug B (.env)
2. Test a real submission end-to-end via /docs
3. Load 15-20 demo submissions covering all 8 categories
4. Frontend team: connect to all API endpoints (frontend runs at localhost:5173, CORS already configured)
5. The `heatmap` in dashboard is always empty — would need lat/lon coordinates per ward to populate

---

## 12. Critical Rules (User's Instructions)

**"From now on dont make any changes by yourself and tell me whats wrong and where and give me the fixed code and where it needs to be."**

Always: identify the bug → show which file and line → provide the fixed code block. Do not silently edit files.
