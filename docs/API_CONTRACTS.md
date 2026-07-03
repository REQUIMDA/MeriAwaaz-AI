# MeriAwaaz AI — API Contracts

**Version:** 1.0 | **Status:** Day 1 Baseline | **Owner:** M3

> This document covers only the Day 1 API contracts as defined in the Project Specification v1.0 and Implementation Checklist v2.1.
> Additional endpoints introduced in later milestones will be documented during their respective implementation milestones.

---

## Source of Truth

All contracts in this document are derived directly from:
- Project Specification v1.0, Section 13 (API Contracts) and Section 14 (JSON Contracts)
- Implementation Checklist v2.1, Sections 11.1–11.3
- Approved Pydantic schemas: `SubmissionRequest`, `ParsedIssue`, `Recommendation`, `DashboardData`
- Database schema: Spec Section 8 (`submissions` table)

No fields have been invented or renamed.

---

## Endpoints

### 1. `POST /api/chat`

Handle conversational messages and follow-up questions before final submission.

**Request Body**

```json
{
  "text": "The road near the school is broken",
  "location_hint": "Ward 12"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | The citizen's message text |
| `location_hint` | string | No | Optional ward or area hint |

**Response — HTTP 200**

```json
{
  "status": "awaiting_follow_up"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always `"awaiting_follow_up"` at this stage |

**Error Responses**

| Code | Condition |
|------|-----------|
| 422 | Request body is invalid or missing required fields |

---

### 2. `POST /api/submissions`

Create a submission and trigger the agent workflow.

**Request Body**

```json
{
  "text": "Roads are broken near the school",
  "location_hint": "Ward 12"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | The citizen's submission text |
| `location_hint` | string | No | Optional ward or area hint |

**Response — HTTP 200**

```json
{
  "submission_id": "sub_001",
  "status": "processing"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `submission_id` | string | Unique ID assigned to the submission |
| `status` | string | Always `"processing"` immediately after submission |

**Error Responses**

| Code | Condition |
|------|-----------|
| 422 | Request body is invalid or missing required fields |
| 500 | Agent workflow failure |

---

### 3. `GET /api/submissions/{submission_id}`

Return the latest state for a submission, including parsed issue and recommendation if the pipeline has completed.

**Path Parameter**

| Parameter | Type | Description |
|-----------|------|-------------|
| `submission_id` | string | The ID returned by `POST /api/submissions` |

**Response — HTTP 200**

The response combines the `submissions` table row (Spec Section 8), the `ParsedIssue` schema, and the `Recommendation` schema.

```json
{
  "id": "sub_001",
  "created_at": "2026-07-04T10:00:00",
  "source": "text",
  "text": "Roads are broken near the school",
  "location_hint": "Ward 12",
  "issue_category": "roads",
  "urgency": "high",
  "summary": "Broken roads near the school",
  "confidence": 0.9,
  "cluster_id": "cluster_001",
  "parsed_issue": {
    "category": "roads",
    "urgency": "high",
    "location": "Ward 12",
    "summary": "Broken roads near the school",
    "confidence": 0.9
  },
  "recommendation": {
    "project_id": "proj_001",
    "priority_score": 0.84,
    "confidence": 0.8,
    "reason": "High demand and poor infrastructure",
    "evidence": ["3 similar requests", "low road coverage", "high local need"]
  }
}
```

**Top-level fields (from `submissions` table, Spec Section 8)**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Submission primary key |
| `created_at` | string | ISO 8601 timestamp |
| `source` | string | Input type: `"text"`, `"voice"`, or `"image"` |
| `text` | string | Original submission text |
| `location_hint` | string | Ward or area hint provided at submission |
| `issue_category` | string | Category extracted by Citizen Intelligence Agent |
| `urgency` | string | Urgency level extracted by Citizen Intelligence Agent |
| `summary` | string | One-sentence summary extracted by Citizen Intelligence Agent |
| `confidence` | number | Extraction confidence score (0.0–1.0) |
| `cluster_id` | string | Cluster assigned by Demand Intelligence Agent (null until pipeline completes) |

**`parsed_issue` object (from approved `ParsedIssue` schema)**

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | Issue category (roads, water, electricity, health, other) |
| `urgency` | string | Urgency level (low, medium, high) |
| `location` | string | Resolved location |
| `summary` | string | One-sentence summary |
| `confidence` | number | Confidence score (0.0–1.0) |

**`recommendation` object (from approved `Recommendation` schema)**

| Field | Type | Description |
|-------|------|-------------|
| `project_id` | string | ID of the recommended project |
| `priority_score` | number | Deterministic priority score (0.0–1.0) |
| `confidence` | number | Recommendation confidence (0.0–1.0) |
| `reason` | string | Human-readable reason for the recommendation |
| `evidence` | array of strings | Supporting evidence bullets |

> Note: `parsed_issue` and `recommendation` will be `null` if the pipeline has not completed yet.

**Error Responses**

| Code | Condition |
|------|-----------|
| 404 | No submission found for the given `submission_id` |

---

### 4. `GET /api/dashboard`

Return the current ranked projects, heatmap points, and submission summary.

**No request parameters required.**

**Response — HTTP 200**

The response matches the `DashboardData` schema (approved in Section 10.4).

```json
{
  "projects": [
    {
      "id": "proj_001",
      "title": "Road Repair — Ward 12",
      "category": "roads",
      "priority_score": 0.84,
      "confidence": 0.8,
      "reason": "",
      "evidence": []
    }
  ],
  "heatmap": [
    {
      "ward": "Ward 1",
      "lat": 26.85,
      "lon": 80.95,
      "intensity": 5
    }
  ],
  "total_submissions": 20,
  "last_updated": "2026-07-04T10:00:00"
}
```

**`projects` array — each item is a `ProjectCard`**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Project primary key |
| `title` | string | Project title |
| `category` | string | Project category (roads, water, electricity, health, other) |
| `priority_score` | number | Latest computed priority score (0.0–1.0) |
| `confidence` | number | Score confidence (0.0–1.0) |
| `reason` | string | Empty on dashboard load; populated on card click via a later endpoint |
| `evidence` | array of strings | Empty on dashboard load; populated on card click via a later endpoint |

**`heatmap` array — each item is a `HeatmapPoint`**

| Field | Type | Description |
|-------|------|-------------|
| `ward` | string | Ward name |
| `lat` | number | Latitude |
| `lon` | number | Longitude |
| `intensity` | integer | Number of submissions in this ward |

**Top-level fields**

| Field | Type | Description |
|-------|------|-------------|
| `total_submissions` | integer | Total number of submissions in the system |
| `last_updated` | string | ISO 8601 timestamp of the last pipeline run |

---

## Contract Review Status

| Step | Status |
|------|--------|
| 11.1 `POST /api/submissions` documented | ✅ |
| 11.2 `GET /api/submissions/{id}` documented | ✅ |
| 11.3 `GET /api/dashboard` documented | ✅ |
| 11.4 Team sign-off (TL, M2, M3, M4) | Pending — required before Day 2 begins |
