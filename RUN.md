# MeriAwaaz AI — Run the full stack (demo)

Two processes: the **FastAPI backend** (AI pipeline + APIs + the Leaflet heatmap
page) and the **Next.js frontend** (citizen + MP portals). The frontend talks to
the backend over HTTP.

## 1. Backend  →  http://localhost:8000

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows   (mac/linux: source venv/bin/activate)
pip install -r requirements.txt
# backend/.env must have the LLM key (LLM_PROVIDER=openai + OPENAI_API_KEY, plus
# GEMINI_API_KEY for embeddings/voice/video). See CONTEXT.md §9.
python -m uvicorn app.main:app --reload
```

Check: http://localhost:8000/docs (Swagger) and http://localhost:8000/heatmap
(the interactive map). Startup seeds 8 plan projects, so the dashboard/heatmap
have data even before any citizen submits.

## 2. Frontend  →  http://localhost:3000

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 and pick a role:

- **Citizen** → Dashboard → "Report Issue" → describe the problem, add a
  location, optionally attach a photo/voice note → Review → **Submit**. This
  calls `POST /api/submissions`, runs the AI pipeline, and the success screen
  shows the AI-matched project(s) and priority score.
- **MP** → Dashboard (live metrics + ranked projects from `/api/dashboard`),
  Citizen Issues (live list from `/api/submissions`), Heatmap (embeds the
  backend Leaflet map, one marker per town, auto-syncing).

### Pointing the frontend at a different backend

The API base defaults to `http://localhost:8000`. To override (e.g. a deployed
backend), create `frontend/.env.local`:

```
NEXT_PUBLIC_API_BASE=https://your-backend.example.com
```

## How it's wired

| Frontend surface | Backend endpoint |
|---|---|
| Citizen submit (Review page) | `POST /api/submissions` (multipart) |
| Citizen video (if used) | `POST /api/submissions/video` |
| Success screen AI result | response of the submit call |
| MP Dashboard | `GET /api/dashboard` |
| MP Citizen Issues | `GET /api/submissions?limit=` |
| MP Heatmap (iframe) | `GET /heatmap` → `GET /api/heatmap` |

CORS on the backend allows `localhost:3000` and `localhost:5173`. The heatmap
iframe loads from the backend origin, so its `/api/heatmap` fetch is same-origin
(no CORS needed).

## Notes for the demo

- On a fresh database the 8 seed plans all have equal severity, so heatmap
  markers share a colour and submission counts read 0 until citizens submit —
  submit a few issues (including a multi-topic one like *"Kesarpur has road
  potholes and its health centre has a medicine shortage"*) to see clusters
  grow, colours diverge, and the dashboard/heatmap update.
- If the LLM key is missing or rate-limited, submissions still succeed and
  degrade to deterministic scoring (status `degraded`); the UI handles this.
