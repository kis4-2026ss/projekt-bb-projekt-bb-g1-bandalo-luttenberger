import json

import pytest

import guardrail.logger as logger_module


@pytest.fixture(autouse=True)
def tmp_log(tmp_path, monkeypatch):
    log = tmp_path / "guardrail-audit.jsonl"
    monkeypatch.setattr(logger_module, "AUDIT_LOG", log)
    return log


def test_log_event_creates_file(tmp_log):
    logger_module.log_event("Read", "/some/path", "allow", {})
    assert tmp_log.exists()


def test_log_event_fields(tmp_log):
    logger_module.log_event("Write", "/secret/file", "block", {})
    entry = json.loads(tmp_log.read_text())
    assert entry["tool"] == "Write"
    assert entry["path"] == "/secret/file"
    assert entry["verdict"] == "block"
    assert "ts" in entry


def test_log_event_experiment_from_env(tmp_log, monkeypatch):
    monkeypatch.setenv("GUARDRAIL_EXPERIMENT", "B")
    logger_module.log_event("Read", "/path", "allow", {})
    entry = json.loads(tmp_log.read_text())
    assert entry["experiment"] == "B"


def test_log_event_experiment_default(tmp_log, monkeypatch):
    monkeypatch.delenv("GUARDRAIL_EXPERIMENT", raising=False)
    logger_module.log_event("Read", "/path", "allow", {})
    entry = json.loads(tmp_log.read_text())
    assert entry["experiment"] == "manual"


def test_log_event_appends(tmp_log):
    logger_module.log_event("Read", "/a", "allow", {})
    logger_module.log_event("Read", "/b", "block", {})
    lines = tmp_log.read_text().strip().splitlines()
    assert len(lines) == 2
