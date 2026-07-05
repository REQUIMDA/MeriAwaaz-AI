import sys
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form  # type: ignore[import]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import]
import uuid

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.agents.graph import pipeline
from app.schemas.schema import AgentState
from app.services.store import STORE
from app.agents.refresh import refresh_all_recommendations

app = FastAPI(title="Constituency Priorities API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    STORE.load_local_plans_as_contexts("data/local_plans.json")

@app.post("/api/submissions")
async def submit(channel: str = Form(...), text: str = Form(None), file: UploadFile = File(None)):
    state = AgentState(
        submission_id=str(uuid.uuid4()),
        input_type="voice" if channel == "voice" else ("photo" if channel == "photo" else "text"),
        raw_text=text or "",
    )
    result = pipeline.invoke(state)
    return {"status": "processed", "recommendation": result["recommendation"]}

@app.post("/api/dashboard-refresh")
async def dashboard_refresh():
    recs = refresh_all_recommendations()
    return {"count": len(recs)}

@app.get("/api/recommendations")
async def get_recommendations():
    return {"items": [r.model_dump() for r in STORE.all_recommendations_sorted()]}

@app.get("/health")
async def health():
    return {"status": "ok"}
