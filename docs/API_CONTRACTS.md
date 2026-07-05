# MeriAwaaz AI — API Contracts

**Version:** 2.0 | **Status:** Updated to Final Schema | **Owner:** M3

> All contracts in this document reflect the **final locked schema** in `backend/app/schemas/models.py`.
> The previous version (1.0) was written against the old schema and has been superseded entirely.

---

## Source of Truth

- Final Pydantic schema: `backend/app/schemas/models.py`
- Classes used: `ParsedIssue`, `ClusterResult`, `FusedContext`, `ScoreBreakdown`, `Explanation`, `Recommendation`, `AgentState`
- `priority_score` is **0–100**, not 0–1
- `Category` values are **capitalized**: `"Roads"`, `"Education"`, `"Healthcare"`, etc.
- `input_type` values: `"text"`, `"voice"`, `"photo"`, `"dashboard_refresh"` — not `"image"`
- `explanation` is `null` until the Explainability Agent runs; it is **never** stored in the database

---

## Endpoint Index

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/submissions` | Submit a citizen request, run the full pipeline |
| GET | `/api/submissions/{submission_id}` | Get submission status + result |
| GET | `/api/recommendations` | Get all ranked recommendations |
| POST | `/api/dashboard-refresh` | Re-score all existing data without re-running intake |
| GET | `/api/explain/{project_id}` | On-demand explanation for a single project (MP clicks a card) |
| GET | `/api/dashboard` | Dashboard data — ranked projects + heatmap |

---

## 1. `GET /health`

**Response — HTTP 200**

```json
{
  "status": "ok",
  "service": "MeriAwaaz AI"
}
```

---

## 2. `POST /api/submissions`

Accepts a citizen submission, runs the full 5-agent pipeline, and returns the final result synchronously.

Supports text, voice (audio file), and photo (image file) via multipart form data.

**Request — `multipart/form-data`**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `channel` | string | Yes | Input type: `"text"`, `"voice"`, or `"photo"` |
| `text` | string | Required if channel is `"text"` | The citizen's submission text |
| `file` | file | Required if channel is `"voice"` or `"photo"` | Audio or image file |

**Example — text submission**

```
POST /api/submissions
Content-Type: multipart/form-data

channel=text
text=Roads are broken near the school in Rampur
```

**Response — HTTP 200**

```json
{
  "submission_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processed",
  "recommendation": {
    "project_id": "cluster_ab12cd34",
    "title": "Roads — Rampur",
    "priority_score": 79.0,
    "breakdown": {
      "citizen_demand": 32.0,
      "severity": 25.0,
      "population_impact": 15.0,
      "cost_feasibility": 7.0
    },
    "is_existing_plan_project": false,
    "explanation": {
      "evidence": [
        "32.0/40 citizen demand — 8 submissions recorded for Roads in Rampur.",
        "25.0/30 severity — 83% infrastructure gap based on real_data.",
        "15.0/20 population impact — approximately 12,400 people affected."
      ],
      "summary": "This Roads issue in Rampur scores 79/100, driven mainly by high citizen demand and a significant infrastructure gap. Eight similar submissions have been recorded, and public data confirms low road connectivity in this area.",
      "confidence_score": 0.9
    }
  }
}
```

**`recommendation` object fields**

| Field | Type | Description |
|-------|------|-------------|
| `project_id` | string | Cluster ID (citizen-sourced) or plan ID (plan-sourced) |
| `title` | string | Human-readable project title |
| `priority_score` | number | **0–100** deterministic score |
| `breakdown.citizen_demand` | number | **0–40** — contribution from citizen demand |
| `breakdown.severity` | number | **0–30** — contribution from infrastructure need |
| `breakdown.population_impact` | number | **0–20** — contribution from affected population |
| `breakdown.cost_feasibility` | number | **0–10** — contribution from project cost |
| `is_existing_plan_project` | boolean | `true` if from local development plan; `false` if citizen-sourced |
| `explanation.evidence` | array of strings | 2–3 grounded evidence bullets citing actual numbers |
| `explanation.summary` | string | 2–3 sentence plain-language explanation for the MP |
| `explanation.confidence_score` | number | 0.9 if `real_data`, 0.6 if `estimated`, 0.4 if `synthetic` |

**Error Responses**

| Code | Condition |
|------|-----------|
| 422 | Missing or invalid form fields |
| 500 | Agent pipeline failure — returns `{"error": "agent_failure", "detail": "..."}` |

---

## 3. `GET /api/submissions/{submission_id}`

Returns the stored record for a submission including the parsed issue and recommendation.

**Path Parameter**

| Parameter | Type | Description |
|-----------|------|-------------|
| `submission_id` | string | UUID returned by `POST /api/submissions` |

**Response — HTTP 200**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "created_at": "2026-07-04T10:00:00",
  "input_type": "text",
  "raw_text": "Roads are broken near the school in Rampur",
  "category": "Roads",
  "location": "Rampur",
  "summary": "Citizen requests road repair near the school in Rampur.",
  "confidence": 0.9,
  "language": "en",
  "cluster_id": "cluster_ab12cd34",
  "parsed_issue": {
    "category": "Roads",
    "location": "Rampur",
    "summary": "Citizen requests road repair near the school in Rampur.",
    "confidence": 0.9,
    "language": "en"
  },
  "recommendation": {
    "project_id": "cluster_ab12cd34",
    "title": "Roads — Rampur",
    "priority_score": 79.0,
    "breakdown": {
      "citizen_demand": 32.0,
      "severity": 25.0,
      "population_impact": 15.0,
      "cost_feasibility": 7.0
    },
    "is_existing_plan_project": false,
    "explanation": null
  }
}
```

> `explanation` is `null` here because it is not stored in the database. Call `GET /api/explain/{project_id}` to generate it on demand.

**`parsed_issue` object fields**

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | One of: `Education`, `Healthcare`, `Roads`, `Water`, `Sanitation`, `Electricity`, `Vocational`, `Other` |
| `location` | string | Ward, village, or area. `"unspecified"` if unclear |
| `summary` | string | One-sentence summary of the citizen's request |
| `confidence` | number | 0.0–1.0 — how well the AI understood the submission |
| `language` | string | ISO 639-1 code, e.g. `"en"`, `"hi"` |

**Submissions table fields**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Submission UUID |
| `created_at` | string | ISO 8601 timestamp |
| `input_type` | string | `"text"`, `"voice"`, or `"photo"` |
| `raw_text` | string | Original submission text |
| `category` | string | Extracted category (capitalized) |
| `location` | string | Extracted location |
| `summary` | string | One-sentence summary |
| `confidence` | number | Extraction confidence 0.0–1.0 |
| `language` | string | ISO 639-1 language code |
| `cluster_id` | string | Cluster assigned by Demand Intelligence Agent |

**Error Responses**

| Code | Condition |
|------|-----------|
| 404 | No submission found for the given ID |

---

## 4. `GET /api/recommendations`

Returns all ranked recommendations from the in-memory store, sorted by `priority_score` descending. Includes both citizen-sourced clusters and existing plan projects.

**Response — HTTP 200**

```json
{
  "items": [
    {
      "project_id": "cluster_ab12cd34",
      "title": "Roads — Rampur",
      "priority_score": 79.0,
      "breakdown": {
        "citizen_demand": 32.0,
        "severity": 25.0,
        "population_impact": 15.0,
        "cost_feasibility": 7.0
      },
      "is_existing_plan_project": false,
      "explanation": null
    },
    {
      "project_id": "plan_001",
      "title": "Construction of 3 classrooms at Govt. Primary School Rampur",
      "priority_score": 61.5,
      "breakdown": {
        "citizen_demand": 0.0,
        "severity": 27.0,
        "population_impact": 18.0,
        "cost_feasibility": 8.5
      },
      "is_existing_plan_project": true,
      "explanation": null
    }
  ]
}
```

> Note: `explanation` is always `null` here. Call `GET /api/explain/{project_id}` for on-demand explanation.

---

## 5. `POST /api/dashboard-refresh`

Re-runs the Policy and Explainability agents over all existing `FusedContext` entries in the store — both citizen clusters and plan-sourced projects. Does **not** re-run intake or clustering. Use this when the MP changes scoring weights (future feature) or to force a re-rank.

**No request body required.**

**Response — HTTP 200**

```json
{
  "count": 6
}
```

| Field | Type | Description |
|-------|------|-------------|
| `count` | integer | Number of recommendations re-scored |

---

## 6. `GET /api/explain/{project_id}`

Generates a fresh explanation for a single project by running the Explainability Agent on demand. Called when the MP clicks a recommendation card in the dashboard — **not** on dashboard load.

**Path Parameter**

| Parameter | Type | Description |
|-----------|------|-------------|
| `project_id` | string | The `project_id` from any `Recommendation` object |

**Response — HTTP 200**

```json
{
  "evidence": [
    "32.0/40 citizen demand — 8 submissions recorded for Roads in Rampur.",
    "25.0/30 severity — 83% infrastructure gap based on real_data.",
    "15.0/20 population impact — approximately 12,400 people affected."
  ],
  "summary": "This Roads issue in Rampur scores 79/100, driven mainly by high citizen demand and a significant infrastructure gap. Eight similar submissions have been recorded, and public data confirms low road connectivity in this area.",
  "confidence_score": 0.9
}
```

| Field | Type | Description |
|-------|------|-------------|
| `evidence` | array of strings | 2–3 evidence bullets citing actual score numbers |
| `summary` | string | 2–3 sentence plain-language explanation for the MP |
| `confidence_score` | number | 0.9 = real_data, 0.6 = estimated, 0.4 = synthetic |

**Error Responses**

| Code | Condition |
|------|-----------|
| 404 | No recommendation found for the given `project_id` |

---

## 7. `GET /api/dashboard`

Returns the full dashboard payload — ranked project list and heatmap. Called on dashboard load and every 10 seconds for auto-refresh.

**Response — HTTP 200**

```json
{
  "projects": [
    {
      "id": "cluster_ab12cd34",
      "title": "Roads — Rampur",
      "category": "Roads",
      "priority_score": 79.0,
      "breakdown": {
        "citizen_demand": 32.0,
        "severity": 25.0,
        "population_impact": 15.0,
        "cost_feasibility": 7.0
      },
      "is_existing_plan_project": false
    }
  ],
  "heatmap": [
    {
      "ward": "Ward 1",
      "lat": 26.850,
      "lon": 80.946,
      "intensity": 8
    },
    {
      "ward": "Ward 2",
      "lat": 26.862,
      "lon": 80.958,
      "intensity": 3
    }
  ],
  "total_submissions": 20,
  "last_updated": "2026-07-04T10:00:00"
}
```

**`projects` array — each item**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Project ID (cluster ID or plan ID) |
| `title` | string | Project title |
| `category` | string | Capitalized category e.g. `"Roads"` |
| `priority_score` | number | **0–100** |
| `breakdown` | object | 4-component score breakdown |
| `is_existing_plan_project` | boolean | Whether this came from the local development plan |

> `explanation` (evidence + summary) is **not** included here. It is fetched separately via `GET /api/explain/{project_id}` when the MP clicks a card.

**`heatmap` array — each item**

| Field | Type | Description |
|-------|------|-------------|
| `ward` | string | Ward name |
| `lat` | number | Latitude |
| `lon` | number | Longitude |
| `intensity` | integer | Number of submissions in this ward |

**Top-level fields**

| Field | Type | Description |
|-------|------|-------------|
| `total_submissions` | integer | Total submissions processed |
| `last_updated` | string | ISO 8601 timestamp of last pipeline run |

---

## Contract Review Status

| Endpoint | Status |
|----------|--------|
| `GET /health` | ✅ Built |
| `POST /api/submissions` | ⬜ Not built |
| `GET /api/submissions/{id}` | ⬜ Not built |
| `GET /api/recommendations` | ⬜ Not built |
| `POST /api/dashboard-refresh` | ⬜ Not built |
| `GET /api/explain/{project_id}` | ⬜ Not built |
| `GET /api/dashboard` | ⬜ Not built |
| Team sign-off (TL, M2, M3, M4) | ⬜ Pending |

---

## What Changed from Version 1.0

| Issue | Old (v1.0) | New (v2.0) |
|-------|-----------|-----------|
| `POST /api/chat` | Existed | **Removed** — not in final architecture |
| `priority_score` scale | 0.0–1.0 | **0–100** |
| `parsed_issue.urgency` | Present | **Removed** — not in final schema |
| `parsed_issue.language` | Missing | **Added** |
| `recommendation.reason` | Direct field | **Moved** into `explanation.summary` |
| `recommendation.evidence` | Direct field | **Moved** into `explanation.evidence` |
| `recommendation.confidence` | Direct field | **Moved** into `explanation.confidence_score` |
| `recommendation.breakdown` | Missing | **Added** (4-component ScoreBreakdown) |
| `recommendation.title` | Missing | **Added** |
| `recommendation.is_existing_plan_project` | Missing | **Added** |
| `Category` values | lowercase (`"roads"`) | **Capitalized** (`"Roads"`) |
| `input_type` value | `"image"` | **`"photo"`** |
| Missing endpoints | — | Added `GET /api/recommendations`, `POST /api/dashboard-refresh`, `GET /api/explain/{project_id}` |
