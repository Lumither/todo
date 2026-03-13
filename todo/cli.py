import argparse
import json
import os

from todo import models
from todo.models import NS_RESERVED
from todo.formatting import (
    print_task_list, print_task_detail, print_namespace_list,
    print_success, print_error,
)


def _parse_tags(value: str) -> list[str]:
    return [t.strip() for t in value.split(",") if t.strip()]


def _json_out(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="A simple CLI todo list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    parser.add_argument("-n", "--namespace", dest="namespace", help="Task namespace (default: $TODO_NAMESPACE or 'default')")
    sub = parser.add_subparsers(dest="command", help="Commands")

    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("item", nargs="+", help="Task description")
    p_add.add_argument("-p", "--priority", type=int, default=0, help="Priority (higher = more urgent)")
    p_add.add_argument("-d", "--due", metavar="DATETIME", help="Due date/time (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD)")
    p_add.add_argument("-t", "--tags", metavar="TAG,TAG", help="Comma-separated tags")

    p_list = sub.add_parser("list", aliases=["ls"], help="List tasks")
    p_list.add_argument("-a", "--all", action="store_true", help="Include completed tasks")
    p_list.add_argument("-t", "--tag", metavar="TAG", help="Filter by tag")

    p_show = sub.add_parser("show", help="Show task details")
    p_show.add_argument("id", type=int, help="Task ID")

    p_done = sub.add_parser("done", aliases=["complete"], help="Mark task as completed")
    p_done.add_argument("id", type=int, help="Task ID")

    p_undone = sub.add_parser("undone", aliases=["reopen"], help="Reopen a task")
    p_undone.add_argument("id", type=int, help="Task ID")

    p_edit = sub.add_parser("edit", help="Edit a task")
    p_edit.add_argument("id", type=int, help="Task ID")
    p_edit.add_argument("item", nargs="*", help="New description")
    p_edit.add_argument("-p", "--priority", type=int, help="New priority")
    p_edit.add_argument("-d", "--due", metavar="DATETIME", help="New due date (empty string to clear)")
    p_edit.add_argument("-t", "--tags", metavar="TAG,TAG", help="Replace tags (comma-separated)")

    p_del = sub.add_parser("delete", aliases=["rm"], help="Delete a task")
    p_del.add_argument("id", type=int, help="Task ID")

    sub.add_parser("clear", help="Delete all completed tasks")

    p_tag = sub.add_parser("tag", help="Add tags to a task")
    p_tag.add_argument("id", type=int, help="Task ID")
    p_tag.add_argument("tags", help="Comma-separated tags to add")

    p_attach = sub.add_parser("attach", help="Attach a file to a task")
    p_attach.add_argument("id", type=int, help="Task ID")
    p_attach.add_argument("file", help="File path")
    p_attach.add_argument("-d", "--description", help="Attachment description")

    p_detach = sub.add_parser("detach", help="Remove an attachment")
    p_detach.add_argument("attachment_id", type=int, help="Attachment ID")

    sub.add_parser("ns", help="List all namespaces")

    args = parser.parse_args()
    use_json = args.json_output
    ns = args.namespace or os.environ.get("TODO_NAMESPACE", "default")

    write_commands = {"add", "done", "complete", "undone", "reopen", "edit", "delete", "rm", "clear", "tag", "attach", "detach"}
    if ns in NS_RESERVED and args.command in write_commands:
        msg = f"Namespace '{ns}' is read-only"
        if use_json:
            _json_out({"ok": False, "error": msg})
        else:
            print_error(msg)
        return

    match args.command:
        case "add":
            tags = _parse_tags(args.tags) if args.tags else None
            item = " ".join(args.item)
            task_id = models.add_task(
                item, priority=args.priority, due_at=args.due, tags=tags, namespace=ns,
            )
            if use_json:
                _json_out({"ok": True, "id": task_id, "item": item, "namespace": ns})
            else:
                print_success(f"Added task #{task_id}: {item} (ns: {ns})")

        case "list" | "ls" | None:
            tag = getattr(args, "tag", None)
            show_all = getattr(args, "all", False)
            tasks = models.list_tasks(show_all=show_all, tag=tag, namespace=ns)
            if use_json:
                _json_out(tasks)
            elif not tasks:
                print_error("No tasks found." if show_all else "No pending tasks.")
            else:
                print_task_list(tasks, show_namespace=(ns == "all"))

        case "show":
            task = models.get_task(args.id, namespace=ns)
            if use_json:
                _json_out(task if task else {"ok": False, "error": f"Task #{args.id} not found"})
            elif task:
                print_task_detail(task)
            else:
                print_error(f"Task #{args.id} not found")

        case "done" | "complete":
            ok = models.complete_task(args.id, namespace=ns)
            if use_json:
                _json_out({"ok": ok, "id": args.id, "namespace": ns} if ok else {"ok": False, "error": f"Task #{args.id} not found"})
            elif ok:
                print_success(f"Completed task #{args.id}")
            else:
                print_error(f"Task #{args.id} not found")

        case "undone" | "reopen":
            ok = models.uncomplete_task(args.id, namespace=ns)
            if use_json:
                _json_out({"ok": ok, "id": args.id, "namespace": ns} if ok else {"ok": False, "error": f"Task #{args.id} not found"})
            elif ok:
                print_success(f"Reopened task #{args.id}")
            else:
                print_error(f"Task #{args.id} not found")

        case "edit":
            item = " ".join(args.item) if args.item else None
            tags = _parse_tags(args.tags) if args.tags is not None else None
            ok = models.edit_task(
                args.id, item=item, priority=args.priority, due_at=args.due, tags=tags, namespace=ns,
            )
            if use_json:
                _json_out({"ok": ok, "id": args.id, "namespace": ns} if ok else {"ok": False, "error": f"Task #{args.id} not found"})
            elif ok:
                print_success(f"Updated task #{args.id}")
            else:
                print_error(f"Task #{args.id} not found")

        case "delete" | "rm":
            ok = models.delete_task(args.id, namespace=ns)
            if use_json:
                _json_out({"ok": ok, "id": args.id, "namespace": ns} if ok else {"ok": False, "error": f"Task #{args.id} not found"})
            elif ok:
                print_success(f"Deleted task #{args.id}")
            else:
                print_error(f"Task #{args.id} not found")

        case "clear":
            count = models.clear_completed(namespace=ns)
            if use_json:
                _json_out({"ok": True, "cleared": count, "namespace": ns})
            else:
                print_success(f"Cleared {count} completed task(s)")

        case "tag":
            task = models.get_task(args.id, namespace=ns)
            if not task:
                if use_json:
                    _json_out({"ok": False, "error": f"Task #{args.id} not found"})
                else:
                    print_error(f"Task #{args.id} not found")
            else:
                existing = task["tags"]
                new_tags = _parse_tags(args.tags)
                merged = list(set(existing + new_tags))
                models.edit_task(args.id, tags=merged, namespace=ns)
                if use_json:
                    _json_out({"ok": True, "id": args.id, "tags": merged, "namespace": ns})
                else:
                    print_success(f"Tagged task #{args.id}: {', '.join(merged)}")

        case "attach":
            att_id = models.add_attachment(args.id, args.file, args.description, namespace=ns)
            if use_json:
                if att_id:
                    _json_out({"ok": True, "id": args.id, "attachment_id": att_id, "file": args.file, "namespace": ns})
                else:
                    _json_out({"ok": False, "error": f"Task #{args.id} not found"})
            elif att_id:
                print_success(f"Attached [{att_id}] {args.file} to task #{args.id}")
            else:
                print_error(f"Task #{args.id} not found")

        case "detach":
            ok = models.remove_attachment(args.attachment_id, namespace=ns)
            if use_json:
                _json_out({"ok": ok, "attachment_id": args.attachment_id, "namespace": ns} if ok else {"ok": False, "error": f"Attachment #{args.attachment_id} not found"})
            elif ok:
                print_success(f"Removed attachment #{args.attachment_id}")
            else:
                print_error(f"Attachment #{args.attachment_id} not found")

        case "ns":
            namespaces = models.list_namespaces()
            if use_json:
                _json_out({"namespaces": namespaces, "current": ns})
            elif not namespaces:
                print_error("No namespaces found.")
            else:
                print_namespace_list(namespaces, ns)

        case _:
            parser.print_help()
