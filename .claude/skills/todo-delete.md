---
description: Delete a task from the todo list
user-invocable: true
argument: task ID number
---

# Delete Task

Delete a task from the todo list.

## Instructions

1. If no task ID is provided as argument, first list all tasks:
   ```bash
   uv run todo list --all
   ```
   Then ask the user which task they want to delete.

2. Once you have the task ID, run:
   ```bash
   uv run todo delete <id>
   ```

3. Confirm the task was deleted to the user.
