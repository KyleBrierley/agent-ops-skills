from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/context-packet-builder/scripts/build_context_packet.py"
SPEC = importlib.util.spec_from_file_location("context_packet", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ContextPacketTests(unittest.TestCase):
    def test_example_matches_reference(self) -> None:
        payload = json.loads(
            (
                ROOT
                / "skills/context-packet-builder/examples/input/project-state.json"
            ).read_text(encoding="utf-8")
        )
        expected = (
            ROOT / "skills/context-packet-builder/examples/expected-context-packet.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(MODULE.render(payload, 5), expected)

    def test_blocked_items_sort_first(self) -> None:
        payload = {
            "objective": "Resume safely.",
            "decisions": [],
            "items": [
                {"id": "B", "summary": "Ready", "status": "ready", "priority": "critical"},
                {"id": "A", "summary": "Blocked", "status": "blocked", "priority": "low"},
            ],
            "risks": [],
        }
        result = MODULE.render(payload, 5)
        self.assertLess(result.index("A: Blocked"), result.index("B: Ready"))

    def test_invalid_due_date_fails(self) -> None:
        payload = {
            "objective": "Resume safely.",
            "decisions": [],
            "items": [
                {
                    "id": "A",
                    "summary": "Invalid",
                    "status": "pending",
                    "priority": "medium",
                    "due": "next week",
                }
            ],
            "risks": [],
        }
        with self.assertRaisesRegex(ValueError, "invalid due date"):
            MODULE.render(payload, 5)


if __name__ == "__main__":
    unittest.main()
