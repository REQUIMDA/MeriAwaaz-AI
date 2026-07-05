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

from app.api.health import router as health_router

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


app.include_router(health_router)


@app.get("/")
def root():
    return {"message": "MeriAwaaz AI Backend is running"}
