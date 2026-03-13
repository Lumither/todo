import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "todo.db"
MIGRATIONS_DIR = Path(__file__).parent / "migrations"

MIGRATION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime'))
);
"""


def _get_applied_versions(conn: sqlite3.Connection) -> set[int]:
    rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    return {r[0] for r in rows}


def _discover_migrations() -> list[tuple[int, str, Path]]:
    migrations = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = int(path.name.split("_", 1)[0])
        migrations.append((version, path.name, path))
    return migrations


def _run_migrations(conn: sqlite3.Connection) -> None:
    conn.executescript(MIGRATION_TABLE)
    applied = _get_applied_versions(conn)
    for version, name, path in _discover_migrations():
        if version in applied:
            continue
        sql = path.read_text()
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
            (version, name),
        )
        conn.commit()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    _run_migrations(conn)
    return conn
