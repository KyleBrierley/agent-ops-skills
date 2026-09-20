import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "examples/action-approval/executor.py"
SPEC = importlib.util.spec_from_file_location("action_executor", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ActionApprovalTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.path = Path(self.directory.name) / "test.sqlite"
        self.executor = MODULE.Executor(self.path)
        self.executor.seed()
        self.proposal = {"request_id": "r-1", "ticket_id": "DEMO-1",
                         "expected_version": 1, "operation": "set_status", "status": "pending"}

    def tearDown(self):
        self.executor.close()
        self.directory.cleanup()

    def approve(self, proposal=None, approved=True):
        proposal = proposal or self.proposal
        preview = self.executor.preview(proposal)
        self.executor.review(proposal, approved=approved, reviewed_digest=preview["digest"])

    def assert_rejected_without_write(self, proposal, reason):
        before = self.executor.ticket()
        with self.assertRaisesRegex(MODULE.Rejected, reason):
            self.executor.execute(proposal)
        self.assertEqual(self.executor.ticket(), before)
        self.assertEqual(self.executor.events()[-1]["event"], "rejected")

    def test_missing_approval_and_ticket_instructions_do_not_authorize(self):
        self.assertIn("Ignore review", self.executor.ticket()["body"])
        self.assert_rejected_without_write(self.proposal, "approval_required")

    def test_declined_review(self):
        self.approve(approved=False)
        self.assert_rejected_without_write(self.proposal, "approval_required")

    def test_changed_proposal_requires_new_approval(self):
        self.approve()
        self.assert_rejected_without_write({**self.proposal, "status": "resolved"}, "approval_required")

    def test_review_must_match_displayed_digest(self):
        preview = self.executor.preview(self.proposal)
        with self.assertRaisesRegex(MODULE.Rejected, "review_changed"):
            self.executor.review({**self.proposal, "status": "resolved"}, approved=True,
                                 reviewed_digest=preview["digest"])
        self.assert_rejected_without_write(self.proposal, "approval_required")

    def test_successful_change(self):
        self.approve()
        result = self.executor.execute(self.proposal)
        self.assertFalse(result["replayed"])
        self.assertEqual(self.executor.ticket()["status"], "pending")
        self.assertEqual(self.executor.ticket()["version"], 2)
        self.assertEqual([e["event"] for e in self.executor.events()], ["approved", "executed"])

    def test_replay_after_restart_has_one_effect(self):
        self.approve()
        first = self.executor.execute(self.proposal)
        self.executor.close()
        self.executor = MODULE.Executor(self.path)
        second = self.executor.execute(self.proposal)
        self.assertEqual(second, {**first, "replayed": True})
        self.assertEqual(self.executor.ticket()["version"], 2)
        self.assertEqual([e["event"] for e in self.executor.events()].count("executed"), 1)
        self.assertEqual(self.executor.events()[-1]["event"], "replayed")

    def test_reused_request_id_cannot_apply_different_action(self):
        self.approve()
        self.executor.execute(self.proposal)
        self.assert_rejected_without_write({**self.proposal, "status": "resolved"}, "request_id_conflict")

    def test_stale_approved_change_cannot_overwrite(self):
        other = {**self.proposal, "request_id": "r-2", "status": "resolved"}
        self.approve()
        self.approve(other)
        self.executor.execute(other)
        self.assert_rejected_without_write(self.proposal, "stale_version")

    def test_forbidden_operation_and_target(self):
        self.approve()
        for change, reason in [({"operation": "delete"}, "forbidden_operation"),
                               ({"ticket_id": "DEMO-2"}, "forbidden_target")]:
            with self.subTest(change=change):
                self.assert_rejected_without_write({**self.proposal, **change}, reason)

    def test_malformed_input(self):
        for value in [None, [], {}, {**self.proposal, "expected_version": True},
                      {**self.proposal, "expected_version": -1},
                      {**self.proposal, "approved": True},
                      {**self.proposal, "request_id": ""},
                      {**self.proposal, "status": "deleted"}]:
            with self.subTest(value=value):
                self.assert_rejected_without_write(value, "invalid_")

    def test_interruption_rolls_back_and_retry_after_restart_succeeds(self):
        self.approve()
        before = self.executor.ticket()
        with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
            self.executor.execute(self.proposal, simulate_interrupt=True)
        self.executor.close()
        self.executor = MODULE.Executor(self.path)
        self.assertEqual(self.executor.ticket(), before)
        result = self.executor.execute(self.proposal)
        self.assertFalse(result["replayed"])
        self.assertEqual(self.executor.ticket()["version"], 2)
        self.assertEqual([e["event"] for e in self.executor.events()],
                         ["approved", "interrupted", "executed"])

    def test_operator_can_revoke_unexecuted_approval(self):
        self.approve()
        self.approve(approved=False)
        self.assert_rejected_without_write(self.proposal, "approval_required")

    def test_scope_change_blocks_previously_approved_action(self):
        self.approve()
        self.executor.close()
        self.executor = MODULE.Executor(self.path, allowed_tickets=())
        self.assert_rejected_without_write(self.proposal, "forbidden_target")


if __name__ == "__main__":
    unittest.main()
