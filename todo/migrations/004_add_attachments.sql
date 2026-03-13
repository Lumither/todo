CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime'))
);
