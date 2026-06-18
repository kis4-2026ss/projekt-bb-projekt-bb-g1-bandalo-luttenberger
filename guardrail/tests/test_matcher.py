from pathlib import Path

from guardrail.matcher import matches_forbidden, resolve_path
from guardrail.policy import Policy


def make_policy(paths=None, patterns=None, mode="enforce"):
    return Policy(
        mode=mode,
        forbidden_paths=[Path(p).expanduser().resolve() for p in (paths or [])],
        forbidden_patterns=patterns or [],
    )


def test_resolve_path_returns_absolute():
    assert resolve_path("/tmp/foo").is_absolute()


def test_resolve_path_expands_tilde():
    p = resolve_path("~/something")
    assert p.is_absolute()
    assert "~" not in str(p)


def test_exact_path_match():
    policy = make_policy(paths=["~/.ssh"])
    assert matches_forbidden(Path("~/.ssh").expanduser().resolve(), policy)


def test_subdir_of_forbidden_path():
    policy = make_policy(paths=["~/.ssh"])
    assert matches_forbidden(Path("~/.ssh/id_rsa").expanduser().resolve(), policy)


def test_glob_pem_match():
    policy = make_policy(patterns=["**/*.pem"])
    assert matches_forbidden(Path("/certs/server.pem"), policy)


def test_glob_env_match():
    policy = make_policy(patterns=["**/.env"])
    assert matches_forbidden(Path("/project/.env"), policy)


def test_no_match_returns_false():
    policy = make_policy(paths=["~/.ssh"], patterns=["**/*.pem"])
    assert not matches_forbidden(Path("/tmp/safe.txt"), policy)


def test_nonexistent_path_still_matches():
    policy = make_policy(paths=["/does/not/exist"])
    assert matches_forbidden(Path("/does/not/exist/secret.txt"), policy)
