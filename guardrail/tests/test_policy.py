from pathlib import Path

import pytest

from guardrail.policy import load_policy


def write_policy(tmp_path, content: str) -> Path:
    p = tmp_path / "guardrail.yaml"
    p.write_text(content)
    return p


def test_valid_policy(tmp_path):
    p = write_policy(tmp_path, """
mode: enforce
forbidden_paths:
  - ~/sandbox/data/sensitive
forbidden_patterns:
  - "**/*.pem"
""")
    policy = load_policy(p)
    assert policy.mode == "enforce"
    assert len(policy.forbidden_paths) == 1
    assert policy.forbidden_paths[0].is_absolute()
    assert "**/*.pem" in policy.forbidden_patterns


def test_audit_mode(tmp_path):
    p = write_policy(tmp_path, "mode: audit\n")
    policy = load_policy(p)
    assert policy.mode == "audit"


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_policy(Path("/nonexistent/guardrail.yaml"))


def test_invalid_mode(tmp_path):
    p = write_policy(tmp_path, "mode: block\n")
    with pytest.raises(ValueError, match="Invalid mode"):
        load_policy(p)


def test_missing_mode(tmp_path):
    p = write_policy(tmp_path, "forbidden_paths: []\n")
    with pytest.raises(ValueError, match="Invalid mode"):
        load_policy(p)


def test_tilde_expansion(tmp_path):
    p = write_policy(tmp_path, """
mode: enforce
forbidden_paths:
  - ~/.ssh
""")
    policy = load_policy(p)
    assert not str(policy.forbidden_paths[0]).startswith("~")
    assert policy.forbidden_paths[0].is_absolute()


def test_empty_lists(tmp_path):
    p = write_policy(tmp_path, "mode: audit\n")
    policy = load_policy(p)
    assert policy.forbidden_paths == []
    assert policy.forbidden_patterns == []


def test_malformed_yaml(tmp_path):
    p = write_policy(tmp_path, "- this\n- is\n- a list\n")
    with pytest.raises(ValueError, match="must be a YAML mapping"):
        load_policy(p)
