import logging
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

# Require the API key for whichever LLM provider is configured
_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
_REQUIRED_KEY = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
}.get(_PROVIDER, "GEMINI_API_KEY")

if not os.getenv(_REQUIRED_KEY):
    print(f"ERROR: {_REQUIRED_KEY} is not set (LLM_PROVIDER={_PROVIDER}). "
          f"Add it to backend/.env before starting.")
    sys.exit(1)

# Gemini is still used for ChromaDB embeddings + voice/video File API
if not os.getenv("GEMINI_API_KEY"):
    print("WARNING: GEMINI_API_KEY is not set — similarity search (embeddings) "
          "and voice/video submissions will fail. Text agents will still work.")

from pathlib import Path

from app.api.health import router as health_router
from app.api.submissions import router as submissions_router
from app.api.video import router as video_router
from app.api.recommendations import router as recommendations_router
from app.api.explain import router as explain_router
from app.api.dashboard import router as dashboard_router
from app.api.trace import router as trace_router
from app.api.heatmap import router as heatmap_router
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
    # Next.js dev server defaults to :3000; Vite/other used :5173. Allow both
    # (and 127.0.0.1 variants) so the frontend can call the API in dev.
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:5173", "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info("%s %s → %s", request.method, request.url.path, response.status_code)
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Log the full traceback and, in development, return it in the response
    so 500s are debuggable from /docs instead of a bare 'Internal Server Error'."""
    import traceback
    tb = traceback.format_exc()
    logger.error("Unhandled error on %s %s\n%s", request.method, request.url.path, tb)
    if os.getenv("ENV", "development") == "development":
        return JSONResponse(status_code=500,
                            content={"detail": f"{type(exc).__name__}: {exc}",
                                     "traceback": tb.splitlines()[-15:]})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


UPLOADS_DIR = Path(__file__).parent / "data" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


@app.on_event("startup")
def on_startup():
    init_db()
    plans_path = str(Path(__file__).parent / "data" / "local_plans.json")
    STORE.load_local_plans(plans_path)
    # Re-score seed plans with the same relative scorer the pipeline uses, so
    # plan projects and citizen projects are always on comparable math.
    try:
        from app.api.dashboard import dashboard_refresh
        dashboard_refresh()
    except Exception as exc:
        logger.warning("Startup re-score failed (non-fatal): %s", exc)
    logger.info("Startup complete.")


app.include_router(health_router)
app.include_router(submissions_router)
app.include_router(video_router)
app.include_router(recommendations_router)
app.include_router(explain_router)
app.include_router(dashboard_router)
app.include_router(trace_router)
app.include_router(heatmap_router)


# Serve the constituency heatmap page same-origin so its fetch('/api/heatmap')
# needs no CORS exception. Open http://localhost:8000/heatmap after starting.
from fastapi.responses import FileResponse  # noqa: E402

_HEATMAP_PAGE = Path(__file__).parent / "static" / "heatmap.html"


@app.get("/heatmap", include_in_schema=False)
def heatmap_page():
    if _HEATMAP_PAGE.exists():
        return FileResponse(str(_HEATMAP_PAGE))
    return JSONResponse(status_code=404, content={"detail": "heatmap.html not found"})


@app.get("/")
def root():
    return {"message": "MeriAwaaz AI Backend is running"}
