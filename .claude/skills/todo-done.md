---
description: Mark a task as completed
user-invocable: true
argument: task ID number
---

# Complete Task

Mark a task as completed in the todo list.

## Instructions

1. If no task ID is provided as argument, first list the pending tasks:
   ```bash
   uv run todo list
   ```
   Then ask the user which task they want to mark as done.

2. Once you have the task ID, run:
   ```bash
   uv run todo done <id>
   ```

3. Confirm the task was completed to the user.
