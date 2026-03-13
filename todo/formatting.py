import json
from datetime import datetime, timedelta
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()

PRIORITY_STYLES: dict[int, tuple[str, str]] = {
    4: ("URGENT", "bold red"),
    3: ("HIGH", "red"),
    2: ("MED", "yellow"),
    1: ("LOW", "dim cyan"),
    0: ("", "dim"),
}


def get_console() -> Console:
    return console


def _due_style(due_at: Optional[str], compact: bool = False) -> tuple[str, str]:
    if not due_at:
        return ("", "dim")
    try:
        due = datetime.fromisoformat(due_at)
    except ValueError:
        return (due_at, "dim")

    has_time = "T" in due_at and not due_at.endswith("T23:59:59")
    date_part = due.strftime("%Y-%m-%d")
    time_part = due.strftime("@%H:%M") if has_time else ("" if compact else "      ")
    stamp = f"{date_part}{time_part}"

    now = datetime.now()
    delta = due - now
    total_secs = int(abs(delta.total_seconds()))
    h = total_secs // 3600
    m = total_secs % 3600 // 60
    s = total_secs % 60

    sign = "-" if delta.total_seconds() < 0 else "+"
    days = total_secs // 86400
    if compact:
        counter = f"{h}:{m:02d}:{s:02d}"
        label = f"{stamp} (T{sign}{counter} D{sign}{days})"
    else:
        counter = f"{h:>3d}:{m:02d}:{s:02d}"
        label = f"{stamp} (T{sign}{counter} D{sign}{days:>3d})"

    if delta.total_seconds() < 0:
        return (label, "bold red")
    elif total_secs < 86400:
        return (label, "yellow")
    elif total_secs < 7 * 86400:
        return (label, "white")
    else:
        return (label, "dim")


def _priority_text(priority: int) -> Text:
    label, style = PRIORITY_STYLES.get(priority, (f"P{priority}", "bold magenta"))
    return Text(label, style=style)


def _tag_text(tags: list[str]) -> Text:
    t = Text()
    for i, tag in enumerate(tags):
        if i > 0:
            t.append(" ")
        t.append(f"[{tag}]", style="cyan")
    return t


def print_task_list(tasks: list[dict], show_namespace: bool = False) -> None:
    table = Table(expand=False, show_header=True, header_style="bold")
    table.add_column("", width=3, justify="center")
    table.add_column("#", justify="right", style="dim")
    if show_namespace:
        table.add_column("Namespace", style="magenta")
    table.add_column("Priority", justify="center")
    table.add_column("Item", min_width=20, max_width=50)
    table.add_column("Created", justify="right", style="dim", width=10, no_wrap=True)
    table.add_column("Due", justify="right", no_wrap=True)
    table.add_column("Tags")

    for task in tasks:
        completed = task["completed"]
        row_style = "dim strike" if completed else ""

        due_label, due_style = _due_style(task.get("due_at"))
        cells: list[Text] = [
            Text("x" if completed else " "),
            Text(str(task["id"])),
        ]
        if show_namespace:
            cells.append(Text(task.get("namespace", "default")))
        created = task.get("created_at", "")[:10]
        cells.extend([
            _priority_text(task.get("priority", 0)),
            Text(task["item"]),
            Text(created),
            Text(due_label, style=due_style),
            _tag_text(task.get("tags", [])),
        ])

        table.add_row(*cells, style=row_style)

    console.print(table)


def print_task_detail(task: dict) -> None:
    body = Text()

    status_style = "green" if task["completed"] else "yellow"
    status_label = "completed" if task["completed"] else "pending"
    body.append("Status:    ")
    body.append(f"{status_label}\n", style=status_style)

    prio = task.get("priority", 0)
    prio_label, prio_style = PRIORITY_STYLES.get(prio, (f"P{prio}", "bold magenta"))
    body.append("Priority:  ")
    body.append(f"{prio} {prio_label}\n", style=prio_style)

    ns = task.get("namespace", "default")
    body.append("Namespace: ")
    body.append(f"{ns}\n", style="magenta")

    body.append(f"Created:   {task['created_at']}\n")
    body.append(f"Updated:   {task['updated_at']}\n")

    if task.get("due_at"):
        due_label, due_style = _due_style(task["due_at"], compact=True)
        body.append("Due:       ")
        body.append(f"{due_label}\n", style=due_style)

    if task.get("completed_at"):
        body.append(f"Completed: {task['completed_at']}\n")

    tags = task.get("tags", [])
    if tags:
        body.append("Tags:      ")
        body.append_text(_tag_text(tags))
        body.append("\n")

    meta = task.get("meta", {})
    if meta:
        body.append("\nMeta:\n", style="bold")
        meta_json = json.dumps(meta, indent=2, ensure_ascii=False)
        body.append_text(Text(meta_json, style="dim"))
        body.append("\n")

    attachments = task.get("attachments", [])
    if attachments:
        body.append("\nAttachments:\n", style="bold")
        for att in attachments:
            desc = f" - {att['description']}" if att.get("description") else ""
            body.append(f"  [{att['id']}] ", style="dim")
            body.append(att["file_path"])
            if desc:
                body.append(desc, style="italic")
            body.append("\n")

    title = f"Task #{task['id']}: {task['item']}"
    console.print(Panel(body, title=title, title_align="left", expand=False))


def print_namespace_list(namespaces: list[str], current: str) -> None:
    table = Table(expand=False, show_header=True, header_style="bold")
    table.add_column("", width=2, justify="center")
    table.add_column("Namespace")

    for ns in namespaces:
        marker = Text("*", style="green") if ns == current else Text("")
        name = Text(ns, style="bold green" if ns == current else "")
        table.add_row(marker, name)

    console.print(table)


def print_success(message: str) -> None:
    console.print(f"[green]{message}[/green]")


def print_error(message: str) -> None:
    console.print(f"[red]{message}[/red]")
