#!/usr/bin/env python3
"""Validate the public skill packages without third-party dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REQUIRED_SECTIONS = (
    "## Inputs",
    "## Outputs",
    "## Workflow",
    "## Failure handling",
    "## Boundaries",
)
FORBIDDEN_PATTERNS = (
    re.compile(r"/Users/"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"\b(?:sk|ghp|gho|github_pat)_[A-Za-z0-9_]+\b"),
)
LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)")


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    try:
        raw = text.split("---\n", 2)[1]
    except IndexError:
        return {}
    values: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def main() -> int:
    failures: list[str] = []
    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())

    if not skill_dirs:
        failures.append("no skills found")

    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            failures.append(f"{skill_dir.name}: missing SKILL.md")
            continue

        text = skill_file.read_text(encoding="utf-8")
        metadata = frontmatter(text)
        if metadata.get("name") != skill_dir.name:
            failures.append(f"{skill_dir.name}: frontmatter name must match directory")
        if len(metadata.get("description", "")) < 30:
            failures.append(f"{skill_dir.name}: description is missing or too short")
        for section in REQUIRED_SECTIONS:
            if section not in text:
                failures.append(f"{skill_dir.name}: missing section {section}")

        for match in LINK_RE.finditer(text):
            target = match.group(1).split("#", 1)[0]
            if target and not (skill_dir / target).resolve().exists():
                failures.append(f"{skill_dir.name}: broken relative link {target}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                failures.append(f"{path.relative_to(ROOT)}: forbidden public-data pattern")

    if failures:
        print("Skill validation failed:")
        for failure in sorted(set(failures)):
            print(f"- {failure}")
        return 1

    print(f"Validated {len(skill_dirs)} skill packages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
