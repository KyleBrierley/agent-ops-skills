#!/usr/bin/env python3
"""Build a deterministic Markdown handoff from normalized project state."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


PRIORITY = {"critical": 0, "high": 1, "medium": 2, "low": 3}
ACTIVE = {"blocked", "in_progress", "ready", "pending"}


def require(payload: dict[str, Any], field: str, expected: type) -> Any:
    value = payload.get(field)
    if not isinstance(value, expected):
        raise ValueError(f"'{field}' must be {expected.__name__}")
    return value


def due_key(value: str | None) -> str:
    if not value:
        return "9999-12-31"
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError(f"invalid due date '{value}'") from exc


def item_key(item: dict[str, Any]) -> tuple[int, int, str, str]:
    status = str(item.get("status", "pending"))
    priority = str(item.get("priority", "medium"))
    return (
        0 if status == "blocked" else 1,
        PRIORITY.get(priority, PRIORITY["medium"]),
        due_key(item.get("due")),
        str(item.get("id", "")),
    )


def render(payload: dict[str, Any], max_items: int) -> str:
    objective = require(payload, "objective", str).strip()
    decisions = require(payload, "decisions", list)
    items = require(payload, "items", list)
    risks = require(payload, "risks", list)
    counts = payload.get("counts", {})
    if not isinstance(counts, dict):
        raise ValueError("'counts' must be dict")

    active = [item for item in items if isinstance(item, dict) and item.get("status") in ACTIVE]
    ranked = sorted(active, key=item_key)
    shown = ranked[:max_items]

    lines = ["# Context packet", "", "## Objective", "", objective, ""]
    lines.extend(["## Decisions", ""])
    lines.extend(f"- {decision}" for decision in decisions) if decisions else lines.append("- None recorded.")

    lines.extend(["", "## Priority work", ""])
    if shown:
        for item in shown:
            due = f"; due {item['due']}" if item.get("due") else ""
            lines.append(
                f"- [{item.get('status')}] {item.get('id')}: {item.get('summary')} "
                f"({item.get('priority', 'medium')}{due})"
            )
    else:
        lines.append("- No active work.")
    omitted = len(ranked) - len(shown)
    if omitted:
        lines.append(f"- {omitted} additional active item(s) omitted by the packet limit.")

    lines.extend(["", "## Risks and blockers", ""])
    lines.extend(f"- {risk}" for risk in risks) if risks else lines.append("- None recorded.")

    lines.extend(["", "## Status counts", ""])
    if counts:
        for name, value in sorted(counts.items()):
            lines.append(f"- {name}: {value}")
    else:
        lines.append("- None recorded.")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-items", type=int, default=5)
    args = parser.parse_args()

    if args.max_items < 1:
        parser.error("--max-items must be positive")

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        parser.error("input root must be an object")
    try:
        result = render(payload, args.max_items)
    except ValueError as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
