import json
from datetime import datetime

from todo.db import get_connection

NS_DEFAULT = "default"
NS_ALL = "all"
NS_RESERVED = {NS_ALL}


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _normalize_due(due_at: str | None) -> str | None:
    if not due_at:
        return due_at
    if len(due_at) == 10:
        return due_at + "T23:59:59"
    return due_at


def add_task(
    item: str,
    priority: int = 0,
    due_at: str | None = None,
    tags: list[str] | None = None,
    namespace: str = NS_DEFAULT,
    meta: dict | None = None,
) -> int:
    if namespace in NS_RESERVED:
        raise ValueError(f"Cannot create tasks in reserved namespace '{namespace}'")
    conn = get_connection()
    now = _now()
    meta_json = json.dumps(meta) if meta else "{}"
    cursor = conn.execute(
        "INSERT INTO tasks"
        " (item, priority, due_at, created_at, updated_at, namespace, meta)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (item, priority, _normalize_due(due_at), now, now, namespace, meta_json),
    )
    assert cursor.lastrowid is not None
    task_id = cursor.lastrowid
    if tags:
        _set_tags(conn, task_id, tags)
    conn.commit()
    conn.close()
    return task_id


def list_tasks(
    show_all: bool = False,
    tag: str | None = None,
    namespace: str = NS_DEFAULT,
) -> list[dict]:
    conn = get_connection()
    query = "SELECT * FROM tasks"
    conditions: list[str] = []
    params: list = []

    if namespace != NS_ALL:
        conditions.append("namespace = ?")
        params.append(namespace)

    if not show_all:
        conditions.append("completed = 0")
    if tag:
        conditions.append(
            "id IN (SELECT task_id FROM task_tags"
            " JOIN tags ON tags.id = task_tags.tag_id"
            " WHERE tags.name = ?)"
        )
        params.append(tag)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY completed, priority DESC, id"
    rows = conn.execute(query, params).fetchall()

    result = []
    for row in rows:
        task = dict(row)
        task["tags"] = _get_task_tags(conn, row["id"])
        result.append(task)

    conn.close()
    return result


def get_task(task_id: int, namespace: str = NS_DEFAULT) -> dict | None:
    conn = get_connection()
    if namespace == NS_ALL:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND namespace = ?", (task_id, namespace)
        ).fetchone()
    if not row:
        conn.close()
        return None
    task = dict(row)
    task["tags"] = _get_task_tags(conn, task_id)
    if task.get("meta"):
        task["meta"] = json.loads(task["meta"])
    else:
        task["meta"] = {}
    conn.close()
    return task


def complete_task(task_id: int, namespace: str = NS_DEFAULT) -> bool:
    conn = get_connection()
    now = _now()
    cursor = conn.execute(
        "UPDATE tasks SET completed = 1, completed_at = ?, updated_at = ? "
        "WHERE id = ? AND namespace = ?",
        (now, now, task_id, namespace),
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def uncomplete_task(task_id: int, namespace: str = NS_DEFAULT) -> bool:
    conn = get_connection()
    now = _now()
    cursor = conn.execute(
        "UPDATE tasks SET completed = 0, completed_at = NULL, updated_at = ? "
        "WHERE id = ? AND namespace = ?",
        (now, task_id, namespace),
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def edit_task(
    task_id: int,
    item: str | None = None,
    priority: int | None = None,
    due_at: str | None = None,
    tags: list[str] | None = None,
    namespace: str = NS_DEFAULT,
    meta: dict | None = None,
) -> bool:
    conn = get_connection()
    sets = ["updated_at = ?"]
    params: list = [_now()]

    if item is not None:
        sets.append("item = ?")
        params.append(item)
    if priority is not None:
        sets.append("priority = ?")
        params.append(priority)
    if due_at is not None:
        sets.append("due_at = ?")
        params.append(_normalize_due(due_at) if due_at != "" else None)
    if meta is not None:
        sets.append("meta = ?")
        params.append(json.dumps(meta))

    params.extend([task_id, namespace])
    cursor = conn.execute(
        f"UPDATE tasks SET {', '.join(sets)} WHERE id = ? AND namespace = ?", params
    )
    if tags is not None and cursor.rowcount:
        _set_tags(conn, task_id, tags)
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def delete_task(task_id: int, namespace: str = NS_DEFAULT) -> bool:
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM tasks WHERE id = ? AND namespace = ?", (task_id, namespace)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def clear_completed(namespace: str = NS_DEFAULT) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM tasks WHERE completed = 1 AND namespace = ?", (namespace,)
    )
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count


def list_namespaces() -> list[str]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT namespace FROM tasks ORDER BY namespace"
    ).fetchall()
    conn.close()
    return [r["namespace"] for r in rows]


def _get_or_create_tag(conn, name: str) -> int:
    row = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
    if row:
        return row["id"]
    cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (name,))
    return cursor.lastrowid


def _set_tags(conn, task_id: int, tag_names: list[str]):
    conn.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))
    for name in tag_names:
        tag_id = _get_or_create_tag(conn, name.strip().lower())
        conn.execute(
            "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
            (task_id, tag_id),
        )


def _get_task_tags(conn, task_id: int) -> list[str]:
    rows = conn.execute(
        "SELECT tags.name FROM tags "
        "JOIN task_tags ON tags.id = task_tags.tag_id "
        "WHERE task_tags.task_id = ?",
        (task_id,),
    ).fetchall()
    return [r["name"] for r in rows]


