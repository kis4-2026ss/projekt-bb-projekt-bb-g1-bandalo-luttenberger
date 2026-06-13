import json

import pytest

import guardrail.report as report_module


@pytest.fixture(autouse=True)
def tmp_log(tmp_path, monkeypatch):
    log = tmp_path / "guardrail-audit.jsonl"
    monkeypatch.setattr(report_module, "AUDIT_LOG", log)
    return log


def write_events(log, events):
    with log.open("w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")


def test_report_missing_log_exits(tmp_log, capsys):
    with pytest.raises(SystemExit):
        report_module.main()


def test_report_counts(tmp_log, capsys):
    write_events(tmp_log, [
        {"experiment": "A", "tool": "Read", "path": "/ok", "verdict": "allow"},
        {"experiment": "A", "tool": "Read", "path": "/secret", "verdict": "block"},
        {"experiment": "A", "tool": "Read", "path": "/secret2", "verdict": "warn"},
    ])
    report_module.main()
    out = capsys.readouterr().out
    assert "Total calls:   3" in out
    assert "Allowed:       1" in out
    assert "blocked: 1, warned: 1" in out


def test_report_honeypots_listed(tmp_log, capsys):
    write_events(tmp_log, [
        {"experiment": "B", "tool": "Read", "path": "/secret/creds", "verdict": "block"},
        {"experiment": "B", "tool": "Read", "path": "/secret/creds", "verdict": "block"},
    ])
    report_module.main()
    out = capsys.readouterr().out
    assert "/secret/creds (2x)" in out


def test_report_multiple_experiments(tmp_log, capsys):
    write_events(tmp_log, [
        {"experiment": "A", "tool": "Read", "path": "/ok", "verdict": "allow"},
        {"experiment": "C", "tool": "Read", "path": "/ok", "verdict": "allow"},
    ])
    report_module.main()
    out = capsys.readouterr().out
    assert "Experiment A" in out
    assert "Experiment C" in out
