"""
LocalFlow — Database helpers.
All database operations use the team-db CLI (Turso sync).
No direct sqlite3 usage.
"""

import json
import subprocess
import uuid
from datetime import datetime
from typing import Any, Optional


def _run_sql(sql: str) -> list[dict[str, Any]]:
    """Execute a single SQL statement via team-db CLI and return parsed JSON results."""
    result = subprocess.run(
        ["team-db", sql],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"team-db error: {result.stderr.strip() or result.stdout.strip()}")
    if not result.stdout.strip():
        return []
    return json.loads(result.stdout.strip())


def new_id() -> str:
    """Generate a short UUID for use as a primary key."""
    return uuid.uuid4().hex[:12]


def now() -> str:
    """Return current timestamp string."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def today() -> str:
    """Return today's date string."""
    return datetime.utcnow().strftime("%Y-%m-%d")


def _escape(val: Any) -> str:
    """Escape a value for safe SQL insertion."""
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def insert(table: str, data: dict[str, Any]) -> str:
    """Insert a row and return its ID."""
    record_id = data.get("id", new_id())
    data["id"] = record_id

    cols = ", ".join(data.keys())
    placeholders = ", ".join(_escape(v) for v in data.values())

    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
    _run_sql(sql)
    return record_id


def update(table: str, record_id: str, data: dict[str, Any]) -> None:
    """Update a row by ID."""
    if "updated_at" not in data and table == "leads":
        data["updated_at"] = now()

    set_clause = ", ".join(
        f"{k} = {_escape(v)}"
        for k, v in data.items()
    )
    sql = f"UPDATE {table} SET {set_clause} WHERE id = '{record_id}'"
    _run_sql(sql)


def get(table: str, record_id: str) -> Optional[dict[str, Any]]:
    """Get a single row by ID."""
    results = _run_sql(f"SELECT * FROM {table} WHERE id = '{record_id}'")
    return results[0] if results else None


def list_all(table: str, where: str = "", order_by: str = "", limit: int = 100) -> list[dict[str, Any]]:
    """List rows from a table with optional WHERE, ORDER BY, and LIMIT."""
    sql = f"SELECT * FROM {table}"
    if where:
        sql += f" WHERE {where}"
    if order_by:
        sql += f" ORDER BY {order_by}"
    sql += f" LIMIT {limit}"
    return _run_sql(sql)


def count(table: str, where: str = "") -> int:
    """Count rows matching optional WHERE clause."""
    sql = f"SELECT COUNT(*) as cnt FROM {table}"
    if where:
        sql += f" WHERE {where}"
    results = _run_sql(sql)
    return results[0]["cnt"] if results else 0


def delete(table: str, record_id: str) -> None:
    """Delete a row by ID."""