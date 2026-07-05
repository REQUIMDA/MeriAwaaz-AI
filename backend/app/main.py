import logging
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    print("ERROR: GEMINI_API_KEY is not set. Add it to backend/.env before starting.")
    sys.exit(1)

from pathlib import Path

from app.api.health import router as health_router
from app.api.submissions import router as submissions_router
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


@app.on_event("startup")
def on_startup():
    init_db()
    plans_path = str(Path(__file__).parent / "data" / "local_plans.json")
    STORE.load_local_plans(plans_path)
    logger.info("Startup complete.")


app.include_router(health_router)
app.include_router(submissions_router)
app.include_router(recommendations_router)
app.include_router(explain_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {"message": "MeriAwaaz AI Backend is running"}
