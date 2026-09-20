"""Run synthetic scenarios in a temporary local database and print the trace."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from executor import Executor, Rejected


def run():
    with TemporaryDirectory() as directory:
        executor = Executor(Path(directory) / "demo.sqlite")
        try:
            executor.seed()
            proposal = {"request_id": "request-1", "ticket_id": "DEMO-1",
                        "expected_version": 1, "operation": "set_status", "status": "pending"}
            before = executor.ticket()
            preview = executor.preview(proposal)
            try:
                executor.execute(proposal)
            except Rejected as error:
                denied = str(error)
            after_denial = executor.ticket()
            # Scripted operator decision for the demo, not an interactive human approval.
            executor.review(proposal, approved=True, reviewed_digest=preview["digest"])
            executed = executor.execute(proposal)
            replayed = executor.execute(proposal)
            return {"mode": "synthetic, scripted approval, no model or network",
                    "before": before, "preview": preview, "denied": denied,
                    "after_denial": after_denial, "executed": executed,
                    "replayed": replayed, "final_ticket": executor.ticket(),
                    "audit": executor.events()}
        finally:
            executor.close()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
