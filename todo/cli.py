import argparse
import json
import os

from todo import models
from todo.formatting import (
    print_error,
    print_namespace_list,
    print_success,
    print_task_detail,
    print_task_list,
)
from todo.models import NS_RESERVED


def _parse_tags(value: str) -> list[str]:
    return [t.strip() for t in value.split(",") if t.strip()]


def _json_out(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _ok_or_not_found(
    use_json: bool, ok: bool,
    data: dict, msg: str, entity: str, eid: int,
) -> None:
    if ok:
        if use_json:
            _json_out(data)
        else:
            print_success(msg)
    else:
        nf = f"{entity} #{eid} not found"
        if use_json:
            _json_out({"ok": False, "error": nf})
        else:
            print_error(nf)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="A simple CLI todo list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--json", action="store_true",
        dest="json_output", help="Output as JSON",
    )
    parser.add_argument(
        "-n", "--namespace", dest="namespace",
        help="Task namespace (default: $TODO_NAMESPACE or 'default')",
    )
    sub = parser.add_subparsers(dest="command", help="Commands")

    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("item", nargs="+", help="Task description")
    p_add.add_argument(
        "-p", "--priority", type=int, default=0,
        help="Priority (higher = more urgent)",
    )
    p_add.add_argument(
        "-d", "--due", metavar="DATETIME",
        help="Due date/time (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD)",
    )
    p_add.add_argument(
        "-t", "--tags", metavar="TAG,TAG",
        help="Comma-separated tags",
    )
    p_add.add_argument(
        "-m", "--meta", metavar="JSON",
        help="Metadata as JSON string",
    )

    p_list = sub.add_parser(
        "list", aliases=["ls"], help="List tasks",
    )
    p_list.add_argument(
        "-a", "--all", action="store_true",
        help="Include completed tasks",
    )
    p_list.add_argument(
        "-t", "--tag", metavar="TAG", help="Filter by tag",
    )

    p_show = sub.add_parser("show", help="Show task details")
    p_show.add_argument("id", type=int, help="Task ID")

    p_done = sub.add_parser(
        "done", aliases=["complete"],
        help="Mark task as completed",
    )
    p_done.add_argument("id", type=int, help="Task ID")

    p_undone = sub.add_parser(
        "undone", aliases=["reopen"], help="Reopen a task",
    )
    p_undone.add_argument("id", type=int, help="Task ID")

    p_edit = sub.add_parser("edit", help="Edit a task")
    p_edit.add_argument("id", type=int, help="Task ID")
    p_edit.add_argument("item", nargs="*", help="New description")
    p_edit.add_argument(
        "-p", "--priority", type=int, help="New priority",
    )
    p_edit.add_argument(
        "-d", "--due", metavar="DATETIME",
        help="New due date (empty string to clear)",
    )
    p_edit.add_argument(
        "-t", "--tags", metavar="TAG,TAG",
        help="Replace tags (comma-separated)",
    )
    p_edit.add_argument(
        "-m", "--meta", metavar="JSON",
        help="Metadata as JSON string",
    )

    p_del = sub.add_parser(
        "delete", aliases=["rm"], help="Delete a task",
    )
    p_del.add_argument("id", type=int, help="Task ID")

    sub.add_parser("clear", help="Delete all completed tasks")

    p_tag = sub.add_parser("tag", help="Add tags to a task")
    p_tag.add_argument("id", type=int, help="Task ID")
    p_tag.add_argument("tags", help="Comma-separated tags to add")

    sub.add_parser("ns", help="List all namespaces")

    return parser


def _parse_meta(raw: str | None) -> dict | None | str:
    """Parse --meta JSON string. Returns dict, None, or error string."""
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return f"Invalid JSON for --meta: {e}"


def _cmd_add(args, use_json: bool, ns: str) -> None:
    tags = _parse_tags(args.tags) if args.tags else None
    meta = _parse_meta(args.meta)
    if isinstance(meta, str):
        if use_json:
            _json_out({"ok": False, "error": meta})
        else:
            print_error(meta)
        return
    item = " ".join(args.item)
    task_id = models.add_task(
        item,
        priority=args.priority,
        due_at=args.due,
        tags=tags,
        namespace=ns,
        meta=meta,
    )
    if use_json:
        _json_out({
            "ok": True, "id": task_id,
            "item": item, "namespace": ns,
        })
    else:
        print_success(f"Added task #{task_id}: {item} (ns: {ns})")


def _cmd_list(args, use_json: bool, ns: str) -> None:
    tag = getattr(args, "tag", None)
    show_all = getattr(args, "all", False)
    tasks = models.list_tasks(
        show_all=show_all, tag=tag, namespace=ns,
    )
    if use_json:
        _json_out(tasks)
    elif not tasks:
        print_error(
            "No tasks found." if show_all
            else "No pending tasks.",
        )
    else:
        print_task_list(tasks, show_namespace=(ns == "all"))


def _cmd_show(args, use_json: bool, ns: str) -> None:
    task = models.get_task(args.id, namespace=ns)
    nf = f"Task #{args.id} not found"
    if use_json:
        _json_out(task or {"ok": False, "error": nf})
    elif task:
        print_task_detail(task)
    else:
        print_error(nf)


def _cmd_done(args, use_json: bool, ns: str) -> None:
    ok = models.complete_task(args.id, namespace=ns)
    _ok_or_not_found(
        use_json, ok,
        {"ok": True, "id": args.id, "namespace": ns},
        f"Completed task #{args.id}",
        "Task", args.id,
    )


def _cmd_undone(args, use_json: bool, ns: str) -> None:
    ok = models.uncomplete_task(args.id, namespace=ns)
    _ok_or_not_found(
        use_json, ok,
        {"ok": True, "id": args.id, "namespace": ns},
        f"Reopened task #{args.id}",
        "Task", args.id,
    )


def _cmd_edit(args, use_json: bool, ns: str) -> None:
    item = " ".join(args.item) if args.item else None
    tags = (
        _parse_tags(args.tags)
        if args.tags is not None else None
    )
    meta = _parse_meta(args.meta)
    if isinstance(meta, str):
        if use_json:
            _json_out({"ok": False, "error": meta})
        else:
            print_error(meta)
        return
    ok = models.edit_task(
        args.id,
        item=item,
        priority=args.priority,
        due_at=args.due,
        tags=tags,
        namespace=ns,
        meta=meta,
    )
    _ok_or_not_found(
        use_json, ok,
        {"ok": True, "id": args.id, "namespace": ns},
        f"Updated task #{args.id}",
        "Task", args.id,
    )


def _cmd_delete(args, use_json: bool, ns: str) -> None:
    ok = models.delete_task(args.id, namespace=ns)
    _ok_or_not_found(
        use_json, ok,
        {"ok": True, "id": args.id, "namespace": ns},
        f"Deleted task #{args.id}",
        "Task", args.id,
    )


def _cmd_clear(_args, use_json: bool, ns: str) -> None:
    count = models.clear_completed(namespace=ns)
    if use_json:
        _json_out({
            "ok": True, "cleared": count, "namespace": ns,
        })
    else:
        print_success(f"Cleared {count} completed task(s)")


def _cmd_tag(args, use_json: bool, ns: str) -> None:
    task = models.get_task(args.id, namespace=ns)
    nf = f"Task #{args.id} not found"
    if not task:
        if use_json:
            _json_out({"ok": False, "error": nf})
        else:
            print_error(nf)
        return
    existing = task["tags"]
    new_tags = _parse_tags(args.tags)
    merged = list(set(existing + new_tags))
    models.edit_task(args.id, tags=merged, namespace=ns)
    if use_json:
        _json_out({
            "ok": True, "id": args.id,
            "tags": merged, "namespace": ns,
        })
    else:
        print_success(
            f"Tagged task #{args.id}: {', '.join(merged)}",
        )


def _cmd_ns(_args, use_json: bool, ns: str) -> None:
    namespaces = models.list_namespaces()
    if use_json:
        _json_out({"namespaces": namespaces, "current": ns})
    elif not namespaces:
        print_error("No namespaces found.")
    else:
        print_namespace_list(namespaces, ns)


COMMANDS = {
    "add": _cmd_add,
    "list": _cmd_list,
    "ls": _cmd_list,
    "show": _cmd_show,
    "done": _cmd_done,
    "complete": _cmd_done,
    "undone": _cmd_undone,
    "reopen": _cmd_undone,
    "edit": _cmd_edit,
    "delete": _cmd_delete,
    "rm": _cmd_delete,
    "clear": _cmd_clear,
    "tag": _cmd_tag,
    "ns": _cmd_ns,
}

WRITE_COMMANDS = {
    "add", "done", "complete", "undone", "reopen",
    "edit", "delete", "rm", "clear", "tag",
}


def main():
    parser = _build_parser()
    args = parser.parse_args()
    use_json = args.json_output
    ns = args.namespace or os.environ.get("TODO_NAMESPACE", "default")

    if ns in NS_RESERVED and args.command in WRITE_COMMANDS:
        msg = f"Namespace '{ns}' is read-only"
        if use_json:
            _json_out({"ok": False, "error": msg})
        else:
            print_error(msg)
        return

    cmd = args.command
    if cmd is None:
        cmd = "list"

    handler = COMMANDS.get(cmd)
    if handler:
        handler(args, use_json, ns)
    else:
        parser.print_help()
