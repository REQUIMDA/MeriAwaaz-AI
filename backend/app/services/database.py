import os
import sqlite3
from datetime import datetime
from app.schemas.settings import settings


def _get_db_path() -> str:
    # Strip "sqlite:///" prefix to get the actual file path
    path = settings.database_url.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    return path


def _connect():
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS submissions (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            input_type TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            category TEXT,
            location TEXT,
            summary TEXT,
            confidence REAL,
            language TEXT,
            cluster_id TEXT,
            photo_url TEXT,
            video_url TEXT,
            audio_url TEXT
        );

        CREATE TABLE IF NOT EXISTS clusters (
            cluster_id TEXT PRIMARY KEY,
            cluster_name TEXT NOT NULL,
            category TEXT NOT NULL,
            center_location TEXT NOT NULL,
            cluster_size INTEGER NOT NULL,
            last_updated TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            project_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            priority_score REAL NOT NULL,
            citizen_demand REAL NOT NULL,
            severity REAL NOT NULL,
            population_impact REAL NOT NULL,
            cost_feasibility REAL NOT NULL,
            is_existing_plan_project INTEGER NOT NULL DEFAULT 0,
            data_confidence TEXT NOT NULL,
            last_updated TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agent_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            status TEXT NOT NULL,
            duration_ms INTEGER,
            created_at TEXT NOT NULL
        );
    """)
    # Migrations: add new columns to existing databases
    for col_sql in [
        "ALTER TABLE submissions ADD COLUMN photo_url TEXT",
        "ALTER TABLE submissions ADD COLUMN video_url TEXT",
        "ALTER TABLE submissions ADD COLUMN audio_url TEXT",
        "ALTER TABLE submissions ADD COLUMN lat REAL",
        "ALTER TABLE submissions ADD COLUMN lng REAL",
        "ALTER TABLE submissions ADD COLUMN resolved INTEGER DEFAULT 0",
        "ALTER TABLE agent_log ADD COLUMN detail TEXT",
    ]:
        try:
            conn.execute(col_sql)
            conn.commit()
        except Exception:
            pass  # Column already exists
    conn.close()


def insert_submission(sub: dict) -> None:
    conn = _connect()
    sub = {"lat": None, "lng": None, **sub}   # lat/lng optional for older callers
    conn.execute("""
        INSERT OR IGNORE INTO submissions
        (id, created_at, input_type, raw_text, category, location, summary,
         confidence, language, cluster_id, photo_url, video_url, audio_url, lat, lng)
        VALUES (:id, :created_at, :input_type, :raw_text, :category, :location, :summary,
                :confidence, :language, :cluster_id, :photo_url, :video_url, :audio_url, :lat, :lng)
    """, sub)
    conn.commit()
    conn.close()


def get_submission(submission_id: str) -> dict | None:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM submissions WHERE id = ?", (submission_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_submission_cluster(submission_id: str, cluster_id: str) -> None:
    conn = _connect()
    conn.execute(
        "UPDATE submissions SET cluster_id = ? WHERE id = ?",
        (cluster_id, submission_id)
    )
    conn.commit()
    conn.close()


def upsert_cluster(cluster: dict) -> None:
    conn = _connect()
    conn.execute("""
        INSERT INTO clusters (cluster_id, cluster_name, category, center_location, cluster_size, last_updated)
        VALUES (:cluster_id, :cluster_name, :category, :center_location, :cluster_size, :last_updated)
        ON CONFLICT(cluster_id) DO UPDATE SET
            cluster_size = excluded.cluster_size,
            last_updated = excluded.last_updated
    """, cluster)
    conn.commit()
    conn.close()


def upsert_recommendation(rec: dict) -> None:
    conn = _connect()
    conn.execute("""
        INSERT INTO recommendations
        (project_id, title, category, location, priority_score, citizen_demand, severity,
         population_impact, cost_feasibility, is_existing_plan_project, data_confidence, last_updated)
        VALUES (:project_id, :title, :category, :location, :priority_score, :citizen_demand, :severity,
                :population_impact, :cost_feasibility, :is_existing_plan_project, :data_confidence, :last_updated)
        ON CONFLICT(project_id) DO UPDATE SET
            priority_score = excluded.priority_score,
            citizen_demand = excluded.citizen_demand,
            severity = excluded.severity,
            population_impact = excluded.population_impact,
            cost_feasibility = excluded.cost_feasibility,
            last_updated = excluded.last_updated
    """, rec)
    conn.commit()
    conn.close()


def get_recommendation(project_id: str) -> dict | None:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM recommendations WHERE project_id = ?", (project_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_recommendations() -> list[dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM recommendations ORDER BY priority_score DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_submissions(limit: int = 100, offset: int = 0) -> list[dict]:
    """Recent submissions, newest first — powers the MP 'Citizen Issues' list."""
    conn = _connect()
    rows = conn.execute("""
        SELECT id, created_at, input_type, raw_text, category, location, summary,
               confidence, language, cluster_id, photo_url, video_url, audio_url,
               lat, lng, COALESCE(resolved, 0) AS resolved
        FROM submissions
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_submissions_resolved(ids: list[str]) -> int:
    """Mark one or more submissions resolved. Returns rows affected."""
    ids = [i for i in ids if i]
    if not ids:
        return 0
    conn = _connect()
    placeholders = ",".join("?" for _ in ids)
    cur = conn.execute(
        f"UPDATE submissions SET resolved = 1 WHERE id IN ({placeholders})", ids
    )
    conn.commit()
    conn.close()
    return cur.rowcount


def resolved_cluster_ids() -> set[str]:
    """cluster_ids (project_ids) whose feeding submissions are ALL resolved.

    A project with no citizen submissions (e.g. a seed plan) never appears here,
    so plan projects are not hidden. Used to drop fully-resolved clusters from
    the dashboard, recommendations, and heatmap.
    """
    conn = _connect()
    rows = conn.execute("""
        SELECT cluster_id,
               COUNT(*) AS total,
               SUM(COALESCE(resolved, 0)) AS res
        FROM submissions
        WHERE cluster_id IS NOT NULL AND cluster_id != ''
        GROUP BY cluster_id
    """).fetchall()
    conn.close()
    return {r["cluster_id"] for r in rows if r["total"] > 0 and r["res"] == r["total"]}


def count_submissions_by_ward() -> list[dict]:
    conn = _connect()
    rows = conn.execute("""
        SELECT location as ward, COUNT(*) as count
        FROM submissions
        WHERE location IS NOT NULL AND location != 'unspecified'
        GROUP BY location
        ORDER BY count DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_all_submissions() -> int:
    conn = _connect()
    row = conn.execute("SELECT COUNT(*) as total FROM submissions").fetchone()
    conn.close()
    return row["total"] if row else 0


def get_last_updated() -> str | None:
    conn = _connect()
    row = conn.execute(
        "SELECT MAX(last_updated) as last_updated FROM recommendations"
    ).fetchone()
    conn.close()
    result = dict(row) if row else None
    return result.get("last_updated") if result else None


def log_agent(submission_id: str, agent_name: str, status: str,
              duration_ms: int, detail: str = "") -> None:
    conn = _connect()
    conn.execute("""
        INSERT INTO agent_log (submission_id, agent_name, status, duration_ms, detail, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (submission_id, agent_name, status, duration_ms, detail,
          datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_agent_logs(submission_id: str) -> list[dict]:
    conn = _connect()
    rows = conn.execute("""
        SELECT id, agent_name, status, duration_ms, detail, created_at
        FROM agent_log
        WHERE submission_id = ?
        ORDER BY id ASC
    """, (submission_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_agent_logs(limit: int = 50) -> list[dict]:
    conn = _connect()
    rows = conn.execute("""
        SELECT id, submission_id, agent_name, status, duration_ms, detail, created_at
        FROM agent_log
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]