"""
PhishGuard SQLite Database Manager
Provides lightweight, local SQLite persistence for scan history.
Fails gracefully if the database file is inaccessible or deleted.
"""

from __future__ import annotations
import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "phishguard.db"


_db_initialized = False

def get_connection() -> sqlite3.Connection:
    """Creates a connection with row factory enabled and ensures schema is initialized."""
    global _db_initialized
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    if not _db_initialized:
        init_db(conn)
        _db_initialized = True
    return conn


def init_db(existing_conn: Optional[sqlite3.Connection] = None):
    """Initializes the database schema if not present."""
    try:
        def _execute(conn):
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT UNIQUE NOT NULL,
                    scan_type TEXT NOT NULL,
                    target_preview TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    is_phishing INTEGER NOT NULL,
                    confidence_score REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    indicators_count INTEGER NOT NULL,
                    model_version TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    details_json TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_type ON scan_history(scan_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prediction ON scan_history(prediction)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON scan_history(created_at)")
            conn.commit()

        if existing_conn:
            _execute(existing_conn)
        else:
            with sqlite3.connect(str(DB_PATH), timeout=10.0) as conn:
                _execute(conn)
        logger.info("PhishGuard SQLite scan_history database initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {e}", exc_info=True)


def insert_scan_record(record: Dict[str, Any]) -> bool:
    """Inserts a sanitized scan record into history."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scan_history (
                    scan_id, scan_type, target_preview, prediction,
                    is_phishing, confidence_score, risk_level,
                    indicators_count, model_version, created_at, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record["scan_id"],
                record["scan_type"],
                record["target_preview"],
                record["prediction"],
                1 if record["is_phishing"] else 0,
                record["confidence_score"],
                record["risk_level"],
                record.get("indicators_count", 0),
                record.get("model_version", "v1.0.0"),
                record["created_at"],
                json.dumps(record.get("details", {}))
            ))
            conn.commit()
            return True
    except Exception as e:
        logger.warning(f"Failed to persist scan record to database: {e}")
        return False


def get_scan_history(
    scan_type: Optional[str] = None,
    prediction: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Retrieves paginated scan history with filtering."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            conditions = []
            params = []

            if scan_type and scan_type.lower() in ["url", "email"]:
                conditions.append("scan_type = ?")
                params.append(scan_type.lower())

            if prediction:
                if "phish" in prediction.lower():
                    conditions.append("is_phishing = 1")
                elif "legit" in prediction.lower():
                    conditions.append("is_phishing = 0")

            if search:
                conditions.append("target_preview LIKE ?")
                params.append(f"%{search.strip()}%")

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            # Count total matching
            count_query = f"SELECT COUNT(*) as total FROM scan_history {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()["total"]

            # Query page
            query = f"""
                SELECT scan_id, scan_type, target_preview, prediction,
                       is_phishing, confidence_score, risk_level,
                       indicators_count, model_version, created_at, details_json
                FROM scan_history
                {where_clause}
                ORDER BY id DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [limit, offset])
            rows = cursor.fetchall()

            items = []
            for r in rows:
                details = {}
                try:
                    details = json.loads(r["details_json"])
                except Exception:
                    pass

                items.append({
                    "scan_id": r["scan_id"],
                    "scan_type": r["scan_type"],
                    "target_preview": r["target_preview"],
                    "prediction": r["prediction"],
                    "is_phishing": bool(r["is_phishing"]),
                    "confidence_score": r["confidence_score"],
                    "risk_level": r["risk_level"],
                    "indicators_count": r["indicators_count"],
                    "model_version": r["model_version"],
                    "created_at": r["created_at"],
                    "details": details
                })

            return {"total": total, "items": items}
    except Exception as e:
        logger.error(f"Error querying scan history: {e}")
        return {"total": 0, "items": []}


def delete_scan_record(scan_id: str) -> bool:
    """Deletes a single scan record."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scan_history WHERE scan_id = ?", (scan_id,))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error deleting scan record {scan_id}: {e}")
        return False


def clear_all_history() -> int:
    """Clears all records from scan_history."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scan_history")
            deleted = cursor.rowcount
            conn.commit()
            return deleted
    except Exception as e:
        logger.error(f"Error clearing scan history: {e}")
        return 0


def get_scan_summary_stats() -> Dict[str, Any]:
    """Computes summary statistics for the overview dashboard."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM scan_history")
            total = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) as phish FROM scan_history WHERE is_phishing = 1")
            phish = cursor.fetchone()["phish"]

            cursor.execute("SELECT COUNT(*) as legit FROM scan_history WHERE is_phishing = 0")
            legit = cursor.fetchone()["legit"]

            cursor.execute("SELECT COUNT(*) as url_scans FROM scan_history WHERE scan_type = 'url'")
            url_scans = cursor.fetchone()["url_scans"]

            cursor.execute("SELECT COUNT(*) as email_scans FROM scan_history WHERE scan_type = 'email'")
            email_scans = cursor.fetchone()["email_scans"]

            return {
                "total_scans": total,
                "phishing_scans": phish,
                "legitimate_scans": legit,
                "url_scans": url_scans,
                "email_scans": email_scans,
                "phishing_ratio": round(phish / total, 4) if total > 0 else 0.0,
            }
    except Exception as e:
        logger.error(f"Error getting scan stats: {e}")
        return {
            "total_scans": 0,
            "phishing_scans": 0,
            "legitimate_scans": 0,
            "url_scans": 0,
            "email_scans": 0,
            "phishing_ratio": 0.0,
        }
