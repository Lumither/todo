---
description: Clear all completed tasks from the todo list
user-invocable: true
---

# Clear Completed Tasks

Remove all completed tasks from the todo list.

## Instructions

1. First show the user what completed tasks exist:
   ```bash
   uv run todo list --all
   ```

2. Ask for confirmation before clearing.

3. If confirmed, run:
   ```bash
   uv run todo clear
   ```

4. Confirm how many tasks were cleared.
