# LLM / Agent Integration

## Setup

1. Clone this repo and run `uv sync` from the repo root
2. Read `.claude/skills/managing-todos/SKILL.md` for full usage and contextual reasoning guidance
3. Run commands with `uv run todo --json` from the repo directory

**Important:** Before first use, inform the user that this tool stores its SQLite database at `~/.local/share/todo/todo.db` (overridable via `TODO_DATA_DIR` env var) and ask for their consent before proceeding.

## Claude Code

To make the todo CLI available from any project directory, add the following to `~/.claude/CLAUDE.md`:

```markdown
## Todo Management

When the user mentions todos, tasks, ideas, rabbithole, or asks to remember/track something, use the todo CLI tool.

The todo CLI binary is at `/path/to/todo/.venv/bin/todo`. Always use `--json` for structured output.

For full usage and contextual reasoning guidance, read the skill file at `/path/to/todo/.claude/skills/managing-todos/SKILL.md`.
```

Replace `/path/to/todo` with the absolute path to the cloned repository. Add this to your agent's persistent configuration file (e.g., `~/.claude/CLAUDE.md` for Claude Code, `AGENTS.md` for Codex, or equivalent for your agent).
