---
description: Add a new task to the todo list
user-invocable: true
argument: task description
---

# Add Task

Add a new task to the todo list using the CLI.

## Instructions

Run the following command to add the task:

```bash
uv run todo add "<argument>"
```

Where `<argument>` is the task description provided by the user.

If no argument is provided, ask the user what task they want to add.
