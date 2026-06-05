from dataclasses import dataclass, field
from pathlib import Path

import yaml

VALID_MODES = {"audit", "enforce"}
DEFAULT_POLICY_PATH = Path(__file__).parent.parent / "guardrail.yaml"


@dataclass
class Policy:
    mode: str
    forbidden_paths: list[Path] = field(default_factory=list)
    forbidden_patterns: list[str] = field(default_factory=list)


def load_policy(path: Path = DEFAULT_POLICY_PATH) -> Policy:
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    with open(path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(f"Policy file must be a YAML mapping: {path}")

    mode = raw.get("mode")
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid mode {mode!r} — must be one of {VALID_MODES}")

    forbidden_paths = [
        Path(p).expanduser().resolve()
        for p in raw.get("forbidden_paths", [])
    ]
    forbidden_patterns = raw.get("forbidden_patterns", [])

    return Policy(
        mode=mode,
        forbidden_paths=forbidden_paths,
        forbidden_patterns=forbidden_patterns,
    )
