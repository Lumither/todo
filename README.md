# todo

A CLI todo list backed by SQLite.

## Usage

```bash
todo add "Refactor auth module" -p 3 -d "2026-03-20" -t "feature,backend"
todo ls
todo done 1
```

Use `todo --help` for full command reference.

## Install

Manual installation:

- clone this repo
- `uv sync`

Data is stored at `~/.local/share/todo/todo.db` (override with `TODO_DATA_DIR`).

LLM/agents instructions:

```
Clone https://github.com/lumither/todo, then read AGENTS.md for integration instructions.
```
