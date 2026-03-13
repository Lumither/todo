ALTER TABLE tasks ADD COLUMN namespace TEXT NOT NULL DEFAULT 'default';
CREATE INDEX idx_tasks_namespace ON tasks(namespace);
CREATE INDEX idx_tasks_namespace_completed ON tasks(namespace, completed);
