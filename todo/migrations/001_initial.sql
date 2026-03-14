CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 0,
    due_at TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')),
    updated_at TEXT,
    completed_at TEXT,
    namespace TEXT NOT NULL DEFAULT 'default',
    meta TEXT DEFAULT '{}'
);

CREATE INDEX idx_tasks_namespace ON tasks(namespace);
CREATE INDEX idx_tasks_namespace_completed ON tasks(namespace, completed);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);
