import json
import re
import sys

from guardrail.logger import log_event
from guardrail.matcher import matches_forbidden, resolve_path
from guardrail.policy import load_policy
from guardrail.verdict import decide

_PATH_RE = re.compile(r"(?:~/[^\s\"';<>|&]*|(?:\.{1,2})?/[^\s\"';<>|&]+)")


def extract_paths(tool_name: str, tool_input: dict) -> list[str]:
    if tool_name in ("Read", "Write", "Edit"):
        path = tool_input.get("file_path")
        return [path] if path else []
    if tool_name == "Bash":
        return _PATH_RE.findall(tool_input.get("command", ""))
    return []


def main() -> None:
    payload = json.load(sys.stdin)
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})

    policy = load_policy()
    paths = extract_paths(tool_name, tool_input)

    for raw in paths:
        path = resolve_path(raw)
        if matches_forbidden(path, policy):
            verdict = decide(matched=True, policy=policy)
            log_event(tool_name, str(path), verdict, payload)
            if verdict == "block":
                print(f"[guardrail] BLOCKED: {path} matches forbidden policy", file=sys.stderr)
                sys.exit(1)

    log_event(tool_name, str(paths), "allow", payload)
    sys.exit(0)


if __name__ == "__main__":
    main()
