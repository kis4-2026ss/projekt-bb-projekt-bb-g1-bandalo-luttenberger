import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

AUDIT_LOG = Path(__file__).parent.parent / "guardrail-audit.jsonl"


def load_events(log_path: Path) -> list[dict]:
    if not log_path.exists():
        print(f"No audit log found at {log_path}", file=sys.stderr)
        sys.exit(1)
    events = []
    with log_path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def main() -> None:
    events = load_events(AUDIT_LOG)

    by_experiment: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        by_experiment[event["experiment"]].append(event)

    for experiment, evts in sorted(by_experiment.items()):
        total = len(evts)
        verdicts = Counter(e["verdict"] for e in evts)
        blocked = verdicts.get("block", 0)
        warned = verdicts.get("warn", 0)
        allowed = verdicts.get("allow", 0)
        violations = blocked + warned

        honeypots = Counter(e["path"] for e in evts if e["verdict"] in ("block", "warn"))

        print(f"Experiment {experiment}")
        print(f"  Total calls:   {total}")
        print(f"  Allowed:       {allowed}")
        print(f"  Violations:    {violations}  (blocked: {blocked}, warned: {warned})")
        if honeypots:
            hits = ", ".join(f"{p} ({n}x)" for p, n in honeypots.most_common())
            print(f"  Honeypots hit: {hits}")
        print()
