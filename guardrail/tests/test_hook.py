import io
import json
from pathlib import Path

import pytest

import guardrail.hook as hook_module
import guardrail.logger as logger_module
from guardrail.hook import extract_paths
from guardrail.policy import Policy


def make_policy(paths=None, patterns=None, mode="enforce"):
    return Policy(
        mode=mode,
        forbidden_paths=[Path(p).expanduser().resolve() for p in (paths or [])],
        forbidden_patterns=patterns or [],
    )


def _setup(monkeypatch, tmp_path, policy, payload_dict):
    log_file = tmp_path / "audit.jsonl"
    monkeypatch.setattr(logger_module, "AUDIT_LOG", log_file)
    monkeypatch.setattr("guardrail.hook.load_policy", lambda: policy)
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload_dict)))
    return log_file


# --- extract_paths ---

def test_extract_read():
    assert extract_paths("Read", {"file_path": "/foo/bar.txt"}) == ["/foo/bar.txt"]


def test_extract_write():
    assert extract_paths("Write", {"file_path": "/out.txt"}) == ["/out.txt"]


def test_extract_edit():
    assert extract_paths("Edit", {"file_path": "/edit.py"}) == ["/edit.py"]


def test_extract_bash_absolute():
    paths = extract_paths("Bash", {"command": "cat /etc/passwd"})
    assert "/etc/passwd" in paths


def test_extract_bash_tilde():
    paths = extract_paths("Bash", {"command": "ls ~/.ssh/id_rsa"})
    assert any(".ssh" in p for p in paths)


def test_extract_unknown_tool():
    assert extract_paths("UnknownTool", {"file_path": "/x"}) == []


# --- main() ---

def test_main_allows_safe_path(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path, make_policy(paths=["/secret"]), {
        "tool_name": "Read",
        "tool_input": {"file_path": "/tmp/safe.txt"},
    })
    with pytest.raises(SystemExit) as exc:
        hook_module.main()
    assert exc.value.code == 0


def test_main_blocks_forbidden_path(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path, make_policy(paths=["/secret"]), {
        "tool_name": "Read",
        "tool_input": {"file_path": "/secret/key.txt"},
    })
    with pytest.raises(SystemExit) as exc:
        hook_module.main()
    assert exc.value.code == 1


def test_main_logs_block_verdict(monkeypatch, tmp_path):
    log = _setup(monkeypatch, tmp_path, make_policy(paths=["/secret"]), {
        "tool_name": "Read",
        "tool_input": {"file_path": "/secret/key.txt"},
    })
    with pytest.raises(SystemExit):
        hook_module.main()
    entry = json.loads(log.read_text())
    assert entry["verdict"] == "block"
    assert entry["tool"] == "Read"


def test_main_warns_in_audit_mode(monkeypatch, tmp_path):
    log = _setup(monkeypatch, tmp_path, make_policy(paths=["/secret"], mode="audit"), {
        "tool_name": "Read",
        "tool_input": {"file_path": "/secret/key.txt"},
    })
    with pytest.raises(SystemExit) as exc:
        hook_module.main()
    assert exc.value.code == 0
    first_entry = json.loads(log.read_text().splitlines()[0])
    assert first_entry["verdict"] == "warn"
