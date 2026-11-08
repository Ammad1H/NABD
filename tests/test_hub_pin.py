"""Hub-pin enforcement (audit R2 m14 / R3 #5): run_all must refuse a hub at the wrong commit."""
import subprocess
from pathlib import Path

import pytest

from eval import run_all


def _mkrepo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "hub"
    repo.mkdir()
    env = dict(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    import os
    env = {**os.environ, **env}
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "f").write_text("x")
    subprocess.run(["git", "-C", str(repo), "add", "f"], check=True, env=env)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "c"], check=True, env=env)
    sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    return repo, sha


def test_pinned_hub_passes(tmp_path):
    repo, sha = _mkrepo(tmp_path)
    assert run_all.assert_hub_pinned(repo, sha) == sha


def test_wrong_commit_fails(tmp_path):
    repo, _ = _mkrepo(tmp_path)
    with pytest.raises(run_all.HubPinError):
        run_all.assert_hub_pinned(repo, "0" * 40)


def test_missing_hub_fails(tmp_path):
    with pytest.raises(run_all.HubPinError):
        run_all.assert_hub_pinned(tmp_path / "nope", run_all.HUB_SHA)
