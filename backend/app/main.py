from fastapi import FastAPI

app = FastAPI(
    title="MeriAwaaz AI Backend",
    version="1.0.0",
    description="Backend API for the MeriAwaaz AI Hackathon Project",
)


@app.get("/")
def root():
    return {
        "message": "MeriAwaaz AI Backend is running"
    }