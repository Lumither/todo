---
name: managing-todos
description: Manage tasks with priorities, due dates, tags, and attachments using a CLI todo app backed by SQLite. Use when the user asks to create, list, complete, edit, delete, or organize tasks, or when they mention todos, task management, or to-do lists.
---

# Task Management

## Setup

Install the todo CLI from the project root:

```bash
pip install -e /path/to/todo
```

If already installed, skip setup.

## Namespaces

Tasks are organized into namespaces (separate task lists). Resolution order:
1. `-n` / `--namespace` CLI flag (highest priority)
2. `TODO_NAMESPACE` environment variable
3. `"default"` (fallback)

```bash
todo --json -n work add "Task"     # add to 'work' namespace
todo --json -n work ls             # list tasks in 'work'
TODO_NAMESPACE=work todo --json ls # same via env var
todo --json -n all ls              # list ALL tasks across namespaces (read-only)
todo --json ns                     # list all namespaces
```

The `all` namespace is reserved and read-only — write commands return `{"ok": false, "error": "Namespace 'all' is read-only"}`.

## Command reference

Always use `--json` for structured output. Place `--json` and `-n` before the subcommand.

### List tasks

```bash
todo --json ls                  # pending tasks
todo --json ls -a               # all tasks including completed
todo --json ls -t work          # filter by tag
```

Returns a JSON array of task objects.

### Add a task

```bash
todo --json add "Task item" -p 3 -d "2026-03-15T18:00:00" -t "work,urgent"
```

Flags:
- `-p N`: priority (0=none, 1=low, 2=med, 3=high, 4=urgent)
- `-d DATETIME`: due date as `YYYY-MM-DDTHH:MM:SS` or `YYYY-MM-DD`
- `-t TAGS`: comma-separated tags

Returns `{"ok": true, "id": N, "item": "..."}`.

### Show task detail

```bash
todo --json show 1
```

Returns full task object with tags and attachments.

### Complete / reopen

```bash
todo --json done 1
todo --json undone 1
```

### Edit a task

```bash
todo --json edit 1 "New item text" -p 2 -d "2026-04-01" -t "work,dev"
```

All fields are optional. Pass only what you want to change.

### Delete / clear

```bash
todo --json delete 1           # delete one task
todo --json clear              # delete all completed tasks
```

### Tags

```bash
todo --json tag 1 "backend,api"   # append tags to task
```

### Attachments

```bash
todo --json attach 1 /path/to/file -d "Description of attachment"
todo --json detach 3              # remove attachment by attachment ID
```

## JSON output contract

All `--json` output goes to stdout.

**Data queries** (`list`, `show`): return the raw object/array.

**Mutations** (`add`, `done`, `edit`, `delete`, `tag`, `attach`, `detach`, `clear`): return `{"ok": true, ...}` on success.

**Errors**: return `{"ok": false, "error": "..."}`.

## Multi-tag filtering

For queries beyond single-tag filtering, pipe JSON through `jq`:

```bash
todo --json ls | jq '[.[] | select(.tags | contains(["work", "dev"]))]'
```

## Task object schema

```json
{
  "id": 1,
  "item": "string",
  "meta": {},
  "completed": 0,
  "priority": 3,
  "due_at": "2026-03-15T18:00:00",
  "created_at": "2026-03-12T16:00:00",
  "updated_at": "2026-03-12T16:00:00",
  "completed_at": null,
  "namespace": "work",
  "tags": ["work", "dev"],
  "attachments": [
    {
      "id": 1,
      "task_id": 1,
      "file_path": "/path/to/file",
      "description": "optional description",
      "created_at": "2026-03-12T16:00:00"
    }
  ]
}
```

Note: `attachments` is only present in `show` output. `list` output includes `tags` but not `attachments`.

## Workflow patterns

### Batch operations

Parse JSON output to chain operations:

```bash
# Complete all tasks tagged "sprint-1"
todo --json ls -t sprint-1 | jq '.[].id' | xargs -I{} todo --json done {}
```

### Reporting

```bash
# Overdue tasks
todo --json ls | jq '[.[] | select(.due_at != null and .due_at < now | todate)]'

# Tasks by priority
todo --json ls | jq 'group_by(.priority) | reverse'
```
