ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 0;
ALTER TABLE tasks ADD COLUMN due_at TEXT;
ALTER TABLE tasks ADD COLUMN updated_at TEXT;
ALTER TABLE tasks ADD COLUMN completed_at TEXT;

UPDATE tasks SET updated_at = created_at WHERE updated_at IS NULL;
