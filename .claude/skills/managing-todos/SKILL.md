---
name: managing-todos
description: Manage tasks with priorities, due dates, tags, and meta using a CLI todo app backed by SQLite. Use when the user asks to create, list, complete, edit, delete, or organize tasks, or when they mention todos, task management, to-do lists, ideas to track, or "rabbithole".
---

# Task Management

You are the smart layer between the user and the todo CLI. Your job is NOT to transcribe the user's words — it is to **interpret intent, craft clear tasks, and enrich them with context**.

## Setup

Run commands from the repo root with:

```bash
uv run todo --json [command] [args]
```

Always use `--json` for structured output. Place `--json` and `-n NAMESPACE` before the subcommand.

## Namespace rules

Namespaces organize tasks into separate lists. They can be **project-based** (e.g., `myapp`, `todo`) or **category-based** (e.g., `rabbithole`, `work`).

**Critical: When the namespace is not obvious, ASK the user.** Do not guess.

Decision process:
1. User explicitly names one (e.g., "put in rabbithole") → use it
2. User says "rabbithole" or "put to rabbithole" → namespace `rabbithole`
3. Otherwise → **ask the user** which namespace to use
4. Before asking, run `uv run todo --json ns` to show them existing namespaces as options

Listing without `-n` shows all tasks across namespaces. Writing without `-n` goes to `default`.

## Creating tasks — your reasoning process

When the user asks to add a task (explicitly or casually), follow these steps:

### 1. Craft the item text

Write a clear, actionable description. Do NOT just copy the user's raw words.

- Bad: "that thing with the auth"
- Good: "Add rate limiting to authentication module"

### 2. Determine namespace

Follow the namespace rules above. **Ask if uncertain.**

### 3. Infer tags

Based on what the user is doing:

| Context | Tags to consider |
|---------|-----------------|
| Fixing a bug | `bug` |
| New feature or idea | `feature`, `idea` |
| Refactoring | `refactor` |
| Research / exploration | `research` |
| Specific language/tech | `python`, `rust`, etc. |

Combine as appropriate. Let user's explicit tags override your inferences.

### 4. Infer priority

| Signal | Priority |
|--------|----------|
| "urgent", "asap", "critical" | 4 |
| "important", "high priority" | 3 |
| Default for most tasks | 2 |
| "when you get a chance", "low" | 1 |
| "someday", "maybe", exploratory | 0-1 |

### 5. Build metadata

Construct a `--meta` JSON object with contextual information:

```json
{
  "source": "claude-code",
  "cwd": "/current/working/directory",
  "git_branch": "feature/foo",
  "files": ["src/relevant_file.rs:42"],
  "links": ["https://referenced-url.com"],
  "context": "Brief description of what user was doing"
}
```

Rules:
- `source`: always `"claude-code"`
- `cwd`: current working directory
- `git_branch`: run `git branch --show-current` if in a git repo
- `files`: files being discussed or relevant to the task
- `links`: any URLs mentioned in conversation
- `context`: 1-2 sentence summary of the surrounding context
- Only include keys that have actual values

## Command reference

```bash
# Add task
uv run todo --json -n NS add "Item" -p PRIORITY -d "YYYY-MM-DD" -t "tag1,tag2" -m '{"key":"val"}'

# List tasks
uv run todo --json ls                    # all pending tasks (all namespaces)
uv run todo --json -n NS ls             # pending in specific namespace
uv run todo --json ls -a                 # include completed
uv run todo --json ls -t TAG             # filter by tag

# Show / complete / reopen / delete
uv run todo --json -n NS show ID
uv run todo --json -n NS done ID
uv run todo --json -n NS undone ID
uv run todo --json -n NS delete ID

# Edit (all fields optional)
uv run todo --json -n NS edit ID "New text" -p 2 -d "2026-04-01" -t "new,tags" -m '{"key":"val"}'

# Append tags
uv run todo --json -n NS tag ID "tag1,tag2"

# Clear completed / list namespaces
uv run todo --json -n NS clear
uv run todo --json ns
```

Flags: `-p` priority (0-4), `-d` due date, `-t` comma-separated tags, `-m` metadata JSON.

## JSON output contract

- **Queries** (`ls`, `show`): raw object/array
- **Mutations** (`add`, `done`, `edit`, etc.): `{"ok": true, "id": N, ...}`
- **Errors**: `{"ok": false, "error": "..."}`

## Task object schema

```json
{
  "id": 1,
  "item": "Task description",
  "completed": 0,
  "priority": 3,
  "due_at": "2026-03-15T18:00:00",
  "created_at": "2026-03-12T16:00:00",
  "updated_at": "2026-03-12T16:00:00",
  "completed_at": null,
  "namespace": "work",
  "meta": {"source": "claude-code", "files": ["src/main.rs"]},
  "tags": ["feature", "rust"]
}
```

## Examples

**User editing `src/auth.rs`, says "oh we should add rate limiting, add a todo":**

```bash
uv run todo --json -n myproject add "Add rate limiting to authentication module" \
  -p 2 -t "feature,security" \
  -m '{"source":"claude-code","files":["src/auth.rs"],"git_branch":"main","context":"While reviewing auth module, user noticed rate limiting is missing"}'
```

**User says "put this in the rabbithole" after discussing lock-free data structures:**

```bash
uv run todo --json -n rabbithole add "Explore lock-free data structures for concurrent queue implementation" \
  -p 1 -t "research,concurrency" \
  -m '{"source":"claude-code","links":["https://example.com/paper"],"context":"User found interesting paper while researching concurrency patterns"}'
```

**User says "todo: fix the off-by-one in the loop":**

Ask which namespace, then:

```bash
uv run todo --json -n projectname add "Fix off-by-one error in parser loop" \
  -p 3 -t "bug" \
  -m '{"source":"claude-code","files":["src/parser.py:142"],"git_branch":"feature/parser"}'
```
