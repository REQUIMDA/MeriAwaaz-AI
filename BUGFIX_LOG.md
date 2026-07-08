# MeriAwaaz AI — Bug Fix Log

Detailed record of every bug fixed in this work session, plus verification of
pre-existing fixes confirmed during the full-project sweep. Each entry states
**where** it lived, **how** it manifested, **why** it happened, and **the fix**.

Session date: 2026-07-08. Scope: heatmap feature integration + full project
bug sweep.

Legend: 🐞 = bug fixed this session · ✅ = verified already-fixed during review ·
⚠️ = flagged config/limitation (not a code bug, no silent change made).

---

## 🐞 BUG #1 — Heatmap widget closes when switching projects; opens inconsistently

**File:** `backend/app/static/heatmap.html` (popup / widget code)

**Symptom (user-reported):** Clicking a town marker opened the widget, but as
soon as you tried to switch to another project (via a tab or the Prev/Next
buttons) the widget **closed**. On some clicks it did not open cleanly at all.
It was inconsistent — worst when a town had 3+ clustered projects.

**Root cause:** Two interacting problems in the original popup implementation.

1. **Full popup teardown mid-click.** Navigation was wired with inline
   `onclick="gotoProject(k)"` handlers, and `gotoProject` called
   `popup.setContent(widgetHTML())`. `setContent` **destroys and rebuilds the
   entire popup DOM**. The button the user physically clicked was removed from
   the DOM *during* its own click event.
2. **Trailing event reached the map.** Because the clicked node was detached
   mid-event and Leaflet's default `closePopupOnClick` is `true`, the trailing
   part of the click sequence bubbled to the map, which interpreted it as a
   "click on the map" and closed the popup. The two handlers (Leaflet's own
   marker↔popup toggle and our manual `setContent`) effectively fought over the
   same gesture, producing the open-then-close / won't-open flakiness.

**Fix (four coordinated changes):**

1. **The widget is now a real DOM element**, not an HTML string. `buildWidgetEl()`
   creates a `<div>`, sets its `innerHTML`, and registers **one delegated click
   listener**.
2. **Clicks are isolated from the map.** The element is guarded with
   `L.DomEvent.disableClickPropagation(el)` + `L.DomEvent.disableScrollPropagation(el)`,
   and the handler calls `L.DomEvent.stop(e)`. In-widget clicks can no longer
   reach the map, so `closePopupOnClick` can never fire for them.
3. **Navigation mutates in place.** `gotoProject()` updates `popupState.idx`,
   sets `popupState.el.innerHTML = widgetInnerHTML()` (the **same** element — no
   `setContent`), then calls `popup.update()` to reflow size/position. The popup
   is never torn down, so it cannot close.
4. **Belt-and-suspenders:** the map is created with `closePopupOnClick: false`,
   and a `popupclose` handler clears `popupState.el` so stale references never
   linger.

Navigation buttons/tabs now carry `data-goto="<index>"` (read by the single
delegated handler) instead of inline `onclick`.

**Verification:** A headless Node simulation drove a 3-project town through
open → tab/Next to #2 → #3 → Next-while-disabled (stays) → Prev to #2 → Prev to
#1, asserting the rendered project id and page counter at each step and that the
popup reports `isOpen() === true` throughout. Result: **PASS** — navigates
across all 3 projects, widget never closes.

---

## 🐞 BUG #2 — Pipeline discards LLM data when population/gap is non-numeric

**File:** `backend/app/supervisor.py` → `_build_fused_context()`

**Symptom:** In the Knowledge Fusion node's LLM path, whenever the model returned
a population like `"1,450"`, `"~5000"`, or `"unknown"` (all plausible LLM
outputs), the node quietly fell back to tool-only data and **threw away the
LLM's entire contribution** (population + narrative extras) for that submission.

**Root cause:** The code coerced values with bare `int(...)`:
```python
population = (int(llm_data.get("population", 0) or 0)
              or int(info.get("population", 0) or 0)
              or _DEFAULT_WARD_POPULATION)
```
`int("1,450")` and `int("unknown")` raise `ValueError`. The exception was caught
by the node's outer `try/except`, so it never crashed the request — but it
degraded the result unnecessarily and masked the real (parseable) value.

**Fix:** Added tolerant parsers used for both population and the infrastructure
gap:
```python
def _as_int(v, default=0):
    try: return int(float(str(v).replace(",", "").strip()))
    except (TypeError, ValueError): return default

def _as_float(v, default=0.0):
    try: return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError): return default
```
`population` now uses `_as_int(...)` and `gap` uses `_as_float(...)`, so
`"1,450"→1450`, `" 12 "→12`, `"unknown"→0` (falls through to the ward default),
and floats/None are all handled without raising.

**Verification:** Unit-tested both helpers in isolation across
`"1,450"`, `"5000"`, `" 12 "`, `None`, `"unknown"`, `3.9`, `""`, `"0.62"`,
`"1,024.5"`, `"n/a"`. All produced the expected values — **ALL PASS**.

---

## 🐞 BUG #3 — New submissions did not appear on the heatmap

**Files:** `backend/app/static/heatmap.html` (+ `api/heatmap.py` already live).

**Symptom:** After submitting a new complaint, the map did not change until a full
manual page reload.

**Root cause:** The frontend fetched `/api/heatmap` exactly once at page load and
never again. The endpoint itself always read live `STORE`, so the data was fresh
server-side — the page just never asked for it again.

**Fix:** Added polling — `refreshData()` re-fetches every 12 s (constant
`REFRESH_MS`) and a manual **↻ Refresh** button forces it. A change-signature
guard avoids needless re-renders, and polling is skipped while a widget is open
so it never interrupts the user. This keeps the map in sync with the dashboard
(both read the same `STORE`).

---

## Feature changes this session (behavioural, verified)

**Multi-topic submissions → multiple clusters** (`api/submissions.py`,
`api/video.py`, new `services/decompose.py`). A single message that raises
several problems is split into one complaint per topic and each is run through
the pipeline, so each updates/creates its own cluster/project. Media is
transcribed/analysed first, then decomposed, then fanned out. Falls back to a
single issue if the LLM is unavailable (identical to prior behaviour). Each topic
is indexed separately in ChromaDB. Verified: files compile; the decomposition
fallback returns `[text]` when the LLM is unavailable; row-id fan-out yields
distinct ids (`sid`, `sid#1`, …).

**Heatmap widget content** (`api/heatmap.py`, `static/heatmap.html`). The widget
now shows the project summary/details, the submission count for that cluster
(`ctx.demand_count`), and the estimated affected population
(`ctx.population_affected`) in place of the old plan badge. Verified headless:
the widget renders all three and navigates across a 3-project town without
closing.

---

## New code added earlier this session (for completeness, not bugs)

- `backend/app/api/heatmap.py` — new `GET /api/heatmap` endpoint: groups live
  `STORE` recommendations by town, attaches coordinates from
  `village_coordinates.json`, returns the frontend's `{towns:[...]}` contract.
  Skips items with no mappable location; orders towns/projects by score.
- `backend/app/main.py` — registered the heatmap router and added a `GET /heatmap`
  route that serves `app/static/heatmap.html` **same-origin** (so its
  `fetch('/api/heatmap')` needs no CORS change).
- `backend/app/static/heatmap.html` — the Constituency Heatmap page.

**Verification of the endpoint math:** replicated `compute_relative_breakdown`
across the 8 seed plans and confirmed the grouped output matches the live scorer
exactly (e.g. `plan_002` Kesarpur = **41.1**, matching the reference example).
All 4 seed villages resolve to coordinates in `village_coordinates.json` (no
missing coords). All `data/*.json` files parse. All backend `.py` files compile
(`python -m compileall app` → exit 0).

---

## ✅ Pre-existing fixes verified during the full-project sweep

These were already fixed in the codebase; confirmed correct while reviewing every
module (older docs still list some as "broken" — they are not).

- **✅ `api/explain.py` MessagesState mismatch.** Now calls `explainability_node`
  from `supervisor.py` (which does the `AgentState → {"messages":[...]}`
  translation) instead of passing raw state to the ReAct agent. Correct.
- **✅ `chroma_client.query_similar` sentinel count.** Guards with
  `real_count = col.count() - 1; if real_count <= 0: return []` before querying,
  so a collection containing only the sentinel no longer errors. Correct.
- **✅ `dashboard-refresh` no-op.** `POST /api/dashboard-refresh` now actually
  re-scores every stored context with `compute_relative_breakdown` (the same
  scorer the pipeline uses), keeping refreshed and pipeline scores consistent.
- **✅ `video.py` size-after-delete.** File size is captured before
  `dest.unlink()`, so oversized-video rejection no longer hits a deleted file.
- **✅ ChromaDB wipe-on-restart.** The sentinel-document pattern rebuilds the
  collection only when the embedding model name changes, preserving vectors
  across restarts.

---

## ⚠️ Flagged config / limitations (deliberately NOT changed)

Not code bugs — these need real values or product decisions, so no silent edits
were made. Documented for the next maintainer.

- **⚠️ `GEMINI_MODEL=gemini-3.5-flash` / `EMBEDDING_MODEL=models/gemini-embedding-2`.**
  Voice/video transcription and ChromaDB embeddings call Gemini directly with
  these names. If either is not a valid current Gemini model, media submissions
  and similarity search fail (text agents still work on OpenAI). Verify against
  current Google documentation and set correct names in `.env` /
  `services/chroma_client.py`. A model name should not be guessed.
- **⚠️ Uniform seed severity.** All 8 seed plans use `severity_score=0.5`, so on a
  fresh database every heatmap marker is the same colour. The green→yellow→red
  gradient appears once citizen submissions raise severity (complaint boost) or
  once varied real data is loaded. Working as designed, not a bug.
- **⚠️ `cluster_size` over-count.** `tools/demand_tools.cluster_submissions` sets a
  new cluster's size to `len(similar)+1`; if the similar results span multiple
  existing clusters this slightly inflates demand. Intentional simplification.
- **⚠️ Doc drift.** `ARCHITECTURE.md` / `MERI_AWAAZ_CONTEXT.md` predate the switch
  to the OpenAI provider and list already-fixed bugs. `CONTEXT.md` is the
  current source of truth.
