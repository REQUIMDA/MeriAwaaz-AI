# MeriAwaaz AI — Agent & LLM Architecture

## Overview

MeriAwaaz AI is a multi-agent decision-support system built for Indian Members of Parliament. Citizens submit grievances in any format — text, voice recording, photograph, or video — and the system produces a ranked list of development projects that the MP can act on.

The backend is a **LangGraph StateGraph** pipeline of 5 specialist AI agents, each backed by Google Gemini 2.0 Flash. The system is deliberately designed so that all **numbers (scores, rankings, population figures) are produced deterministically by Python tools**, while **LLMs contribute only language** — natural-language parsing, clustering reasoning, human-readable titles, and explanations. This separation means the rankings are reproducible and auditable, and the system degrades gracefully if the LLM API is unavailable.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| LLM | Google Gemini 2.0 Flash (`gemini-2.0-flash`) |
| Agent Framework | LangGraph `StateGraph` + `create_react_agent` |
| Embeddings | Gemini `text-embedding-004` (768 dimensions) |
| Vector Database | ChromaDB (HNSW, cosine similarity) |
| Structured Storage | SQLite (raw `sqlite3`, no ORM) |
| Media Processing | Gemini File API (video + audio) |
| API Framework | FastAPI |
| In-Memory State | Singleton `_Store` class |

---

## Shared State: AgentState

Every agent in the pipeline reads from and writes to a single Pydantic model called `AgentState`. It flows through the entire graph, accumulating results as each agent completes.

```
AgentState
├── submission_id       UUID for this citizen submission
├── input_type          text | voice | image | video | dashboard_refresh
├── raw_text            The citizen's complaint in plain text (filled by pre-processors for media)
├── media_file_path     On-disk path to uploaded photo / video / audio file
├── audio_url           /uploads/{file} URL for the frontend audio widget
│
├── parsed_issue        [set by Agent 1 — Citizen Intelligence]
│     ├── category      Education | Healthcare | Roads | Water | ... (8 categories)
│     ├── location      Ward/village name, "unspecified" if unclear
│     ├── summary       One-sentence description of the complaint
│     ├── confidence    0.0–1.0 — how clearly the LLM understood the submission
│     └── language      ISO 639-1 code (en, hi, mr, ta, ...)
│
├── cluster             [set by Agent 2 — Demand Intelligence]
│     ├── cluster_id    Unique ID grouping similar complaints together
│     ├── cluster_name  Short human label (e.g. "School Infrastructure")
│     ├── cluster_size  How many citizens have raised this same issue
│     └── center_location Most representative location for the cluster
│
├── knowledge_context   [set by Agent 3 — Knowledge Fusion]
│     ├── category / location
│     ├── demand_count        cluster_size at time of scoring
│     ├── population_affected Ward/district population estimate
│     ├── estimated_cost_inr  Project cost estimate in INR
│     ├── data_confidence     real_data | estimated | synthetic
│     ├── severity_score      0.0–1.0 infrastructure need (from government datasets)
│     ├── category_specific_data  Raw numbers + plan linkage metadata
│     └── is_existing_plan_project  True if a matching plan project was found
│
├── recommendation      [set by Agent 4 — Policy Recommendation]
│     ├── project_id    Stable ID (plan ID if matched, else cluster-based)
│     ├── title         Human-readable project title (LLM-generated)
│     ├── priority_score  0–100 (deterministic)
│     ├── breakdown     citizen_demand(0-40) + severity(0-30) + population_impact(0-20) + cost_feasibility(0-10)
│     ├── is_existing_plan_project
│     └── explanation   [set by Agent 5 — Explainability]
│           ├── evidence         2–3 grounded fact bullets
│           ├── summary          2–3 sentence MP-facing explanation
│           └── confidence_score  How well-supported this recommendation is
│
└── error               Error message if any node degraded to fallback
```

---

## Input Layer: Media Pre-Processors

Before the 5-agent pipeline runs, two pre-processors convert non-text input into plain text that the rest of the pipeline can work with. They are both LangGraph nodes that write into `state.raw_text`.

### Speech Processing (`input_type = "voice"`)

1. Audio file (mp3/wav/m4a/ogg/flac/aac/webm, max 50 MB) is uploaded to the **Gemini File API**
2. System polls until state is `ACTIVE` (max 60 seconds)
3. Gemini 2.0 Flash is called with a strict transcription prompt — exact words only, no paraphrasing, Hindi/Marathi in native script
4. Transcript is written to `state.raw_text`
5. `state.audio_url` is set so the frontend can render a playable audio widget
6. Uploaded file is deleted from Gemini immediately after use

### Vision Processing (`input_type = "image"` or `"video"`)

**Images (jpg/png/webp):**
- Base64-encoded inline in a multimodal Gemini message
- A fixed structured prompt extracts: VISUAL (what damage is visible), LOCATION (signboards/landmarks), COMPLAINT (citizen's request in their own words)
- Result written to `state.raw_text`

**Videos (mp4/mov/avi/mkv/webm, max 50 MB):**
- Uploaded to **Gemini File API**, polled until `ACTIVE` (max 90 seconds)
- Gemini analyzes both the **visual footage AND the audio track simultaneously** — a single model call that returns: VISUAL + AUDIO (exact transcript) + LOCATION + COMPLAINT
- This combined analysis is written to `state.raw_text` as structured text
- Uploaded file is always deleted from Gemini after use

Both pre-processors flow into the Citizen Intelligence Agent as if the submission was text.

---

## The 5-Agent Pipeline

### Why create_react_agent + wrapper functions?

Each specialist agent is built with LangGraph's `create_react_agent`. This creates a mini ReAct loop — the agent can call tools, observe results, and reason before producing its final answer. It uses its own internal `MessagesState` schema.

The outer graph uses `AgentState`. To bridge these two schemas without state collisions, every agent is wrapped in a plain Python function that:

1. Reads the fields it needs from `AgentState`
2. Formats them into `{"messages": [HumanMessage(content=...)]}` for the sub-agent
3. Calls the sub-agent via `.invoke()`
4. Parses the agent's final message (strips markdown fences, extracts JSON)
5. Returns a dict of `AgentState` field updates

---

### Agent 1: Citizen Intelligence

**Purpose:** Understand what the citizen is actually asking for.

**Tools:**
- `extract_issue_details(text)` — Gemini call → returns category, location, summary, confidence as JSON
- `detect_language(text)` — Gemini call → returns ISO 639-1 code

**What the LLM does:** Reads a raw complaint in any language (English, Hindi, Marathi, Tamil, etc.) and extracts structured fields. Handles multilingual input natively.

**Output:** `ParsedIssue` written to `state.parsed_issue`

**Fallback:** If the LLM is unreachable, produces `category="Other"`, `confidence=0.3`, raw text as summary.

---

### Agent 2: Demand Intelligence

**Purpose:** Cluster this submission with similar past complaints to measure collective citizen pressure.

**Tools:**
- `search_similar_submissions(summary, category, top_k)` — queries ChromaDB with a `retrieval_query` embedding, filters by category metadata, returns up to 10 similar past submissions with cosine similarity scores
- `cluster_submissions(submissions, current_summary, category, location)` — Gemini decides whether this complaint belongs to an existing cluster or starts a new one; updates in-memory `STORE.clusters`

**What the LLM does:** Reads the list of similar past complaints and uses judgment to decide if they share a theme. It names the cluster ("School Infrastructure", "Road Repair") and picks the representative location.

**The key insight:** The `cluster_size` this produces is the primary driver of `citizen_demand` in the priority score. A complaint raised by 15 citizens carries far more weight than one raised by 1 citizen — the LLM clustering is what makes this happen.

**ChromaDB detail:** Every submission is stored as a vector using Gemini `text-embedding-004` (768 dimensions, cosine similarity). A sentinel document pattern (`__embedding_model__: models/text-embedding-004`) prevents the collection from being wiped on restart — it only resets when the embedding model changes.

**Output:** `ClusterResult` written to `state.cluster`

**Fallback:** Creates a singleton cluster (size=1) from the current submission.

---

### Agent 3: Knowledge Fusion

**Purpose:** Layer government data on top of citizen demand — "what does public infrastructure data say about this area?"

**Architecture note — deterministic-first:** The tool call happens **before** the LLM call. `lookup_infrastructure` reads local government JSON datasets and returns an `infrastructure_gap` score. This number is authoritative. The LLM is then called to provide supplementary narrative (population estimates, proposal context) but can never override the dataset-derived gap score.

**Tools:**
- `lookup_infrastructure(location, category)` — reads preprocessed JSON files (healthcare_need.json, education_need.json, digital_connectivity_need.json), normalises the need field relative to all records → returns `infrastructure_gap` (0–1) and `data_confidence`
- `lookup_plan_projects(location, category)` — scans the in-memory STORE for existing plan projects matching location + category

**Plan project matching:** If a matching plan project is found, the citizen demand is treated as **validation** of that existing plan rather than a new proposal. This implements the core problem statement: "weigh competing proposals against real demand." The matched plan's `project_id` is attached to the context so the downstream agents use the plan's identity instead of creating a duplicate.

**Complaint boost:** The `severity_score` is lifted by `apply_complaint_boost(gap, cluster_size, 10)` — citizen demand can raise the severity by up to +0.15 (capped at 10 clustered complaints), linking real-world pressure to the infrastructure data score.

**Population fallback:** Government datasets carry need-ratios but not population figures. When no real population is available, a default ward estimate of 5,000 is used so the `population_impact` score component is never zero.

**Output:** `FusedContext` written to `state.knowledge_context`

**Fallback:** Uses only the deterministic tool output (no LLM contribution to narrative fields).

---

### Agent 4: Policy Recommendation

**Purpose:** Score and rank development projects — decide which one deserves the MP's attention most.

**Architecture note — LLM contributes language, not numbers:** The priority score and all breakdown components are computed entirely by `_deterministic_recommendation()`, a pure-Python function. The LLM is called only to generate a human-readable `title` and a one-sentence `reason`. This is a deliberate design choice — scores must be reproducible and auditable.

**Relative scoring (not fixed caps):**
```
citizen_demand    = 40  × (demand_count / max_demand_in_store)
severity          = 30  × severity_score                         (0–1 from KF agent)
population_impact = 20  × (population_affected / max_pop_in_store)
cost_feasibility  = 10  × (1 − estimated_cost / 2×reference_cost)  [5.0 if cost unknown]

priority_score = citizen_demand + severity + population_impact + cost_feasibility  (0–100)
```

Normalising against the strongest competitor in the store (not a fixed cap) means rankings differentiate visibly as new complaints arrive and cluster sizes grow. A single complaint that was worth 0.8 points yesterday becomes more important tomorrow when 9 more citizens echo it.

**Project identity rules (no duplicate cards):**
- If citizen demand validates an existing plan → `project_id = plan_id` (one card per plan)
- Otherwise → `project_id = proj_{cluster_id}` (one card per cluster, not per submission)
- This prevents N submissions from the same cluster creating N separate dashboard cards

**Leaderboard awareness:** The prompt includes the current top-5 ranked projects so the LLM's title and reason can reference relative standing ("this project now ranks #2 because 8 citizens confirmed it vs. only 2 for the top road project").

**Tools used:**
- `compute_priority_score` — deterministic Python formula
- `rank_projects` — sorts by score

**Output:** `Recommendation` written to `state.recommendation`, also persisted to `STORE`

**Fallback:** Uses `_deterministic_recommendation()` directly — pure Python, no LLM required.

---

### Agent 5: Explainability

**Purpose:** Translate the score into language the MP can read and act on in under 10 seconds.

**Tools:**
- `build_evidence_bullets(cluster_size, infrastructure_gap, population, facility_count, category)` — pure Python; generates 2–3 grounded fact bullets referencing real numbers
- `compute_confidence_score(priority_score, cluster_size, data_completeness)` — pure Python; confidence is weighted by: 50% score strength + 30% demand volume (caps at 50 submissions for full signal) + 20% data completeness (real_data=0.9, estimated=0.6, synthetic=0.4)

**What the LLM does:** Reads all the numbers and writes a 2–3 sentence MP-facing explanation. When citizen demand validates an existing plan project, the explanation specifically notes that citizens are confirming this planned work.

**Output:** `Explanation` written into `state.recommendation.explanation`, `STORE` updated

**Fallback:** `_deterministic_explanation()` builds the Explanation object from the pure-Python tools alone — zero LLM calls needed.

---

## Fault Tolerance: LLM Fast Failure

Every node checks `_llm_unavailable(state)` before making any LLM call. If `state.error` contains any of these markers: `resource_exhausted`, `429`, `quota`, `permission_denied`, `api key`, `503`, `unavailable`, `high demand` — the node immediately uses its deterministic fallback without attempting the LLM call.

This means if the Gemini API quota is hit mid-pipeline, all remaining nodes skip their LLM calls and the system still produces a valid (if less explanatory) recommendation. **The pipeline never returns a 500 error due to API unavailability** — it degrades gracefully, marking `state.error` and using pure-Python scoring.

---

## Tracing

Every node is wrapped with `traced("agent_name")(node_fn)`. This:
- Logs start/end/duration to the console
- Persists an entry to the `agent_log` SQLite table with `submission_id`, `agent_name`, `status` (success/error), and `duration_ms`

This makes it possible to query `GET /api/trace/{submission_id}` to see exactly which agents ran, how long each took, and whether any degraded to fallback mode.

---

## Data Flow: End to End

```
Citizen submits complaint
        │
POST /api/submissions (text/voice/photo) or POST /api/submissions/video
        │
        ├─ File saved to disk → /uploads/{uuid}.ext
        │
        ▼
  _pipeline.invoke(AgentState)
        │
  ┌─────▼──────────────────────────────────────────────────────────────┐
  │                    LangGraph StateGraph                             │
  │                                                                     │
  │  route_intake ──→ [speech_processing | vision_processing] ──┐      │
  │                                                              │      │
  │             ┌────────────────────────────────────────────────┘      │
  │             ▼                                                        │
  │  citizen_intelligence_node  ← Gemini: parse complaint text          │
  │             │  state.parsed_issue = {category, location, summary}    │
  │             ▼                                                        │
  │  demand_intelligence_node   ← ChromaDB: find similar complaints      │
  │             │                ← Gemini: name and size the cluster      │
  │             │  state.cluster = {cluster_id, cluster_name, size}      │
  │             ▼                                                        │
  │  knowledge_fusion_node      ← govt JSON datasets: infrastructure gap │
  │             │                ← Gemini: population + narrative extras  │
  │             │                ← plan matching: attach to existing plan?│
  │             │  state.knowledge_context = {severity, population, ...} │
  │             ▼                                                        │
  │  policy_recommendation_node ← Python: compute_relative_breakdown     │
  │             │                ← Gemini: write title + one-line reason  │
  │             │  state.recommendation = {project_id, score, breakdown} │
  │             ▼                                                        │
  │  explainability_node        ← Python: build_evidence_bullets         │
  │             │                ← Gemini: write 2-3 sentence summary     │
  │             │  state.recommendation.explanation = {evidence, summary}│
  └─────────────┼───────────────────────────────────────────────────────┘
                │
                ▼
  Result → SQLite (permanent record)
         → ChromaDB (indexed for future similarity search)
         → STORE (in-memory, powers GET /api/dashboard instantly)
         → API response → Frontend
```

---

## In-Memory Store vs SQLite

The system uses two storage layers for different purposes:

**SQLite (`database.py`)** is the permanent record — every submission, cluster, recommendation, and agent log entry is written here. It survives restarts. Used for analytics queries (count by category, last updated, etc.).

**`STORE` singleton (`store.py`)** is the fast read layer — `FusedContext` and `Recommendation` objects live in Python dicts in RAM. Dashboard reads (`GET /api/dashboard`) hit the STORE, not SQLite, so they return instantly. At startup, 8 seed plan projects are loaded from `local_plans.json` into the STORE with baseline scores. As new submissions are processed, new entries are added or existing ones updated.

---

## ChromaDB Vector Search Details

- Collection: `citizen_submissions`
- Embedding model: `models/text-embedding-004` (768 dims, Gemini)
- Distance metric: cosine similarity (`hnsw:space = cosine`)
- Index task type: `retrieval_document` for indexing, `retrieval_query` for search queries
- Sentinel document: `__embedding_model__: models/text-embedding-004` — the collection only resets when the embedding model name changes, so existing vectors survive server restarts
- Metadata filters: queries are filtered by `category` so Healthcare complaints only match against Healthcare submissions
- Real submission count: `col.count() - 1` (subtracts the sentinel)

---

## LLM Role Summary

| What the LLM does | What pure Python does |
|-------------------|----------------------|
| Transcribe speech (exact words) | Score priority (formula) |
| Describe visual/video content | Compute infrastructure gap (dataset lookup) |
| Parse complaint language + category | Normalize scores (min-max) |
| Detect language | Cluster size tracking |
| Name demand clusters | Population fallback (5,000 default) |
| Decide cluster membership | Complaint boost (+0.15 max) |
| Write project titles + reasons | Build evidence bullets |
| Write MP-facing explanations | Compute confidence score |
| | Plan project matching |
| | All database writes |

The LLM is a language interface. Every number that drives an MP's decision comes from code.
