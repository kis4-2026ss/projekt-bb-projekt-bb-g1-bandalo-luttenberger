import json
import os
from datetime import datetime
from pathlib import Path

AUDIT_LOG = Path(__file__).parent.parent / "guardrail-audit.jsonl"


def log_event(tool: str, path: str, verdict: str, raw_payload: dict) -> None:
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "experiment": os.environ.get("GUARDRAIL_EXPERIMENT", "manual"),
        "tool": tool,
        "path": str(path),
        "verdict": verdict,
    }
    with AUDIT_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")
