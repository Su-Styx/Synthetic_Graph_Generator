import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


def _find_project_root(start: Path) -> Path:
    """
    Walk upward from this test file until we find the directory that
    contains modules/VGAE_model/VGAE_endpoint.py, and return that directory.

    This is what makes the test runnable "as-is" no matter where pytest's
    rootdir ends up or where this file lives inside the repo -- no PYTHONPATH,
    no conftest.py, no sys.path fiddling required from you.
    """
    for candidate in (start, *start.parents):
        if (candidate / "modules" / "VGAE_model" / "VGAE_endpoint.py").is_file():
            return candidate
    raise RuntimeError(
        "Could not find modules/VGAE_model/VGAE_endpoint.py above "
        f"{start}. Is this test file inside the project tree?"
    )


PROJECT_ROOT = _find_project_root(Path(__file__).resolve().parent)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.VGAE_model import VGAE_endpoint as vgae  # noqa: E402


@pytest.fixture
def checkpoint_file(tmp_path):
    path = tmp_path / "vgae_checkpoint.pt"
    path.write_bytes(b"checkpoint")
    return path


def make_completed_process(stdout="", stderr="", returncode=0):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def test_generate_builds_expected_command(monkeypatch, checkpoint_file):
    captured = {}

    def fake_run(cmd, capture_output, text, timeout):
        captured["cmd"] = cmd
        captured["capture_output"] = capture_output
        captured["text"] = text
        captured["timeout"] = timeout
        return make_completed_process(
            stdout=json.dumps(
                {
                    "nodes": [{"id": 0}, {"id": 1}],
                    "edges": [{"source": 0, "target": 1}],
                    "metadata": {
                        "model": "vgae",
                        "n_nodes": 2,
                        "n_edges": 1,
                        "directed": False,
                        "parameters": {"threshold": 0.5},
                    },
                }
            )
        )

    monkeypatch.setattr(vgae.subprocess, "run", fake_run)

    data = vgae.generate(checkpoint=str(checkpoint_file), n=20, t=0.5, seed=123)

    assert captured["cmd"][0] == "python3"
    assert str(vgae.GENERATE_SCRIPT) in captured["cmd"]
    assert "--checkpoint" in captured["cmd"]
    assert str(checkpoint_file) in captured["cmd"]
    assert "--num_nodes" in captured["cmd"]
    assert "20" in captured["cmd"]
    assert "--threshold" in captured["cmd"]
    assert "0.5" in captured["cmd"]
    assert "--seed" in captured["cmd"]
    assert "123" in captured["cmd"]
    assert data["metadata"]["model"] == "vgae"


def test_generate_rejects_missing_checkpoint(tmp_path):
    missing = tmp_path / "missing.pt"

    with pytest.raises(FileNotFoundError):
        vgae.generate(checkpoint=str(missing), n=20, t=0.5)


def test_generate_rejects_bad_json(monkeypatch, checkpoint_file):
    def fake_run(cmd, capture_output, text, timeout):
        return make_completed_process(stdout="not json", stderr="", returncode=0)

    monkeypatch.setattr(vgae.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="invalid JSON"):
        vgae.generate(checkpoint=str(checkpoint_file), n=20, t=0.5)


def test_train_vgae_builds_expected_command(monkeypatch, tmp_path):
    captured = {}

    def fake_run(cmd, capture_output, text, timeout):
        captured["cmd"] = cmd
        return make_completed_process(
            stdout=json.dumps({"test_roc": 0.91, "test_ap": 0.88})
        )

    monkeypatch.setattr(vgae.uuid, "uuid4", lambda: "test-run-id")
    monkeypatch.setattr(vgae.subprocess, "run", fake_run)
    monkeypatch.setattr(vgae, "CHECKPOINT_DIR", tmp_path)

    edges_path = tmp_path / "edges.csv"
    nodes_path = tmp_path / "nodes.csv"
    edges_path.write_text("x_index,y_index\n0,1\n")
    nodes_path.write_text("node_index\n0\n1\n")

    data = vgae.train_vgae(
        edges_path=str(edges_path),
        nodes_path=str(nodes_path),
        model_name="VGAE",
        epochs=50,
        hidden1=32,
        hidden2=16,
        lr=0.01,
        seed=99,
    )

    assert captured["cmd"][0] == "python3"
    assert str(vgae.TRAIN_SCRIPT) in captured["cmd"]
    assert "--dataset" in captured["cmd"]
    assert "disease_features" in captured["cmd"]
    assert "--edges_path" in captured["cmd"]
    assert str(edges_path) in captured["cmd"]
    assert "--nodes_path" in captured["cmd"]
    assert str(nodes_path) in captured["cmd"]
    assert "--epochs" in captured["cmd"]
    assert "50" in captured["cmd"]
    assert "--hidden1" in captured["cmd"]
    assert "32" in captured["cmd"]
    assert "--hidden2" in captured["cmd"]
    assert "16" in captured["cmd"]
    assert "--lr" in captured["cmd"]
    assert "0.01" in captured["cmd"]
    assert "--seed" in captured["cmd"]
    assert "99" in captured["cmd"]
    assert "--checkpoint_out" in captured["cmd"]
    assert str(tmp_path / "test-run-id.pt") in captured["cmd"]
    assert data["checkpoint"] == str(tmp_path / "test-run-id.pt")
    assert data["checkpoint_name"] == "test-run-id.pt"


def test_train_vgae_rejects_bad_json(monkeypatch, tmp_path):
    def fake_run(cmd, capture_output, text, timeout):
        return make_completed_process(stdout="not json", stderr="", returncode=0)

    monkeypatch.setattr(vgae.subprocess, "run", fake_run)
    monkeypatch.setattr(vgae.uuid, "uuid4", lambda: "test-run-id")
    monkeypatch.setattr(vgae, "CHECKPOINT_DIR", tmp_path)

    edges_path = tmp_path / "edges.csv"
    edges_path.write_text("x_index,y_index\n0,1\n")

    with pytest.raises(RuntimeError, match="invalid JSON"):
        vgae.train_vgae(edges_path=str(edges_path))


def test_train_and_generate_uses_existing_checkpoint(monkeypatch, checkpoint_file):
    calls = []

    def fake_generate(checkpoint, n, t, seed=None):
        calls.append(("generate", checkpoint, n, t, seed))
        return {
            "nodes": [{"id": 0}],
            "edges": [],
            "metadata": {"model": "vgae", "n_nodes": n, "n_edges": 0, "directed": False},
        }

    def fake_train_vgae(*args, **kwargs):
        calls.append(("train", args, kwargs))
        return {"checkpoint": str(checkpoint_file), "checkpoint_name": checkpoint_file.name}

    monkeypatch.setattr(vgae, "generate", fake_generate)
    monkeypatch.setattr(vgae, "train_vgae", fake_train_vgae)

    data = vgae.train_and_generate(
        edges_path="ignored.csv",
        n=20,
        threshold=0.5,
        checkpoint=checkpoint_file.name,
    )

    assert calls == [("generate", checkpoint_file.name, 20, 0.5, None)]
    assert data["metadata"]["checkpoint"] == checkpoint_file.name
    assert data["metadata"]["trained"] is False


def test_train_and_generate_trains_then_generates(monkeypatch):
    calls = []

    def fake_generate(checkpoint, n, t, seed=None):
        calls.append(("generate", checkpoint, n, t, seed))
        return {
            "nodes": [{"id": 0}],
            "edges": [{"source": 0, "target": 1}],
            "metadata": {"model": "vgae", "n_nodes": n, "n_edges": 1, "directed": False},
        }

    def fake_train_vgae(**kwargs):
        calls.append(("train", kwargs))
        return {"checkpoint": "/tmp/test-run-id.pt", "checkpoint_name": "test-run-id.pt"}

    monkeypatch.setattr(vgae, "generate", fake_generate)
    monkeypatch.setattr(vgae, "train_vgae", fake_train_vgae)

    data = vgae.train_and_generate(
        edges_path="edges.csv",
        n=20,
        threshold=0.5,
        seed=7,
        epochs=10,
        hidden1=32,
        hidden2=16,
        lr=0.01,
    )

    assert calls[0][0] == "train"
    assert calls[1] == ("generate", "/tmp/test-run-id.pt", 20, 0.5, 7)
    assert data["metadata"]["trained"] is True
    assert data["metadata"]["checkpoint"] == "test-run-id.pt"


def test_list_checkpoints_returns_sorted(tmp_path, monkeypatch):
    monkeypatch.setattr(vgae, "CHECKPOINT_DIR", tmp_path)

    a = tmp_path / "a.pt"
    b = tmp_path / "b.pt"
    a.write_bytes(b"a")
    b.write_bytes(b"b")

    list_result = vgae.list_checkpoints()

    assert isinstance(list_result, list)
    assert len(list_result) == 2
    assert all("checkpoint" in item for item in list_result)
    assert all("path" in item for item in list_result)
    assert all("modified" in item for item in list_result)