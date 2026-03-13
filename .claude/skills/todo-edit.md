---
description: Edit a task's description
user-invocable: true
argument: task ID and new description
---

# Edit Task

Edit the description of an existing task.

## Instructions

1. If no task ID is provided, first list the tasks:
   ```bash
   uv run todo list --all
   ```
   Then ask the user which task they want to edit.

2. If no new description is provided, ask the user for the new description.

3. Once you have both the task ID and new description, run:
   ```bash
   uv run todo edit <id> "<new description>"
   ```

4. Confirm the task was updated to the user.
