from pathlib import Path

from guardrail.policy import Policy


def resolve_path(raw: str) -> Path:
    return Path(raw).expanduser().resolve()


def matches_forbidden(path: Path, policy: Policy) -> bool:
    for forbidden in policy.forbidden_paths:
        try:
            path.relative_to(forbidden)
            return True
        except ValueError:
            pass
    for pattern in policy.forbidden_patterns:
        if path.match(pattern):
            return True
    return False
