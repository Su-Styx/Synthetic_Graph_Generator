# VGAE_endpoint.py

import subprocess
import json
import uuid
from pathlib import Path
from typing import Optional

import pandas as pd  # NEW: used to read node attributes


BASE_DIR = Path(__file__).resolve().parent
GENERATE_SCRIPT = BASE_DIR / "vgae_pytorch" / "generate.py"
TRAIN_SCRIPT    = BASE_DIR / "vgae_pytorch" / "train.py"

CHECKPOINT_DIR = BASE_DIR / "media" / "vgae_checkpoints"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


def generate(
    checkpoint: str,
    n: int,
    t: float,
    seed: Optional[int] = None,
    edges_path: Optional[str] = None,
    nodes_path: Optional[str] = None,
) -> dict:
    checkpoint_path = Path(checkpoint)
    if not checkpoint_path.is_absolute():
        checkpoint_path = CHECKPOINT_DIR / checkpoint

    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    cmd = [
        "python3",
        str(GENERATE_SCRIPT),
        "--checkpoint", str(checkpoint_path),
        "--num_nodes", str(n),
        "--threshold", str(t),
    ]

    if edges_path is not None:
        cmd += ["--edges_path", str(edges_path)]
    if nodes_path is not None:
        cmd += ["--nodes_path", str(nodes_path)]

    if seed is not None:
        cmd += ["--seed", str(seed)]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)

    if result.returncode != 0:
        raise RuntimeError(f"VGAE generate failed: {result.stderr.strip()}")

    try:
            stdout = result.stdout.strip()
            if not stdout:
                raise RuntimeError(
                    f"VGAE generate produced no output. "
                    f"stderr head: {result.stderr[:500]!r}"
                )

            lines = [ln for ln in stdout.splitlines() if ln.strip()]
            last = lines[-1]
            return json.loads(last)
    except (IndexError, json.JSONDecodeError) as e:
            raise RuntimeError(
                f"VGAE generate returned invalid JSON. "
                f"stdout head: {result.stdout[:500]!r}, stderr head: {result.stderr[:500]!r}"
            ) from e


def train_vgae(
    edges_path: str,
    nodes_path: Optional[str] = None,
    model_name: str = "VGAE",
    epochs: int = 200,
    hidden1: int = 32,
    hidden2: int = 16,
    lr: float = 0.01,
    seed: Optional[int] = None,
) -> dict:
    run_id = str(uuid.uuid4())
    checkpoint_path = CHECKPOINT_DIR / f"{run_id}.pt"

    cmd = [
        "python3",
        str(TRAIN_SCRIPT),
        "--dataset", "disease_features",
        "--edges_path", str(edges_path),
        "--model", model_name,
        "--epochs", str(epochs),
        "--hidden1", str(hidden1),
        "--hidden2", str(hidden2),
        "--lr", str(lr),
        "--checkpoint_out", str(checkpoint_path),
    ]

    if nodes_path:
        cmd += ["--nodes_path", str(nodes_path)]

    if seed is not None:
        cmd += ["--seed", str(seed)]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)

    if result.returncode != 0:
        raise RuntimeError(f"VGAE training failed: {result.stderr.strip()}")

    # Training finished successfully; result.stdout just contains logs, not JSON.
    stdout_head = result.stdout[:500]
    stderr_head = result.stderr[:500]

    payload = {
        "status": "ok",
        "log_head": stdout_head,
        "error_head": stderr_head,
        "checkpoint": str(checkpoint_path),
        "checkpoint_name": checkpoint_path.name,
    }
    return payload
    # except json.JSONDecodeError as e:
    #     raise RuntimeError(
    #         f"VGAE train returned invalid JSON. "
    #         f"stdout head: {result.stdout[:500]!r}, stderr head: {result.stderr[:500]!r}"
    #     ) from e

    # payload["checkpoint"] = str(checkpoint_path)
    # payload["checkpoint_name"] = checkpoint_path.name
    # return payload


def train_and_generate(
    edges_path: str,
    n: Optional[int],          # requested number of nodes; if None, use full dataset size
    threshold: float,
    nodes_path: Optional[str] = None,
    model_name: str = "VGAE",
    epochs: int = 200,
    hidden1: int = 32,
    hidden2: int = 16,
    lr: float = 0.01,
    seed: Optional[int] = None,
    checkpoint: Optional[str] = None,
) -> dict:
    """
    Desired behavior:
      - If checkpoint is provided: use it directly, generate adjacency for the
        same number of nodes as in nodes_path (or the given n), and attach attributes.
      - Otherwise: train a fresh VGAE, save checkpoint, then generate and attach attributes.
    """
    if nodes_path is None:
        raise ValueError("nodes_path is required to attach node attributes.")

    # Load node attributes and determine dataset size
    nodes_df = pd.read_csv(nodes_path).sort_values("node_index").reset_index(drop=True)
    num_nodes_total = len(nodes_df)

    # If n is None, use full dataset size
    if n is None:
        n = num_nodes_total

    if n != num_nodes_total:
        # You can relax this if you later want subsampling, but then you
        # must decide how to map generated indices to original nodes.
        raise ValueError(
            f"Requested n={n} but source data has {num_nodes_total} nodes. "
            f"For 1-1 attribute pairing, n must equal number of nodes in source data."
        )

    # CASE 1: Use an existing checkpoint
    if checkpoint:
        # generated_raw = generate(checkpoint=checkpoint, n=n, t=threshold, seed=seed)
        generated_raw = generate(
            checkpoint=checkpoint,
            n=n,
            t=threshold,
            seed=seed,
            edges_path=edges_path,
            nodes_path=nodes_path,
        )
        trained_flag = False
        training_result = None
        checkpoint_name = Path(checkpoint).name
    else:
        # CASE 2: Train a new VGAE
        training_result = train_vgae(
            edges_path=edges_path,
            nodes_path=nodes_path,
            model_name=model_name,
            epochs=epochs,
            hidden1=hidden1,
            hidden2=hidden2,
            lr=lr,
            seed=seed,
        )
        checkpoint = training_result["checkpoint"]
        checkpoint_name = training_result["checkpoint_name"]
        generated_raw = generate(
            checkpoint=checkpoint,
            n=n,
            t=threshold,
            seed=seed,
            edges_path=edges_path,
            nodes_path=nodes_path,
        )
        trained_flag = True

    # Attach attributes to generated nodes
    nodes_out = []
    for i in range(n):
        row = nodes_df.iloc[i]
        nodes_out.append({
            "id":           int(i),
            "node_index":   int(row["node_index"]),
            "node_id":      str(row["node_id"]),      # cast to str to be safe
            "node_type":    str(row["node_type"]),
            "node_name":    str(row["node_name"]),
            "node_source":  str(row["node_source"]),
        })

    edges_out = generated_raw.get("edges", [])

    metadata = generated_raw.get("metadata", {})
    metadata["checkpoint"] = checkpoint_name
    metadata["trained"] = trained_flag
    if training_result is not None:
        metadata["training"] = training_result

    result = {
        "nodes":    nodes_out,
        "edges":    edges_out,
        "metadata": metadata,
    }
    return result


def list_checkpoints() -> list[dict]:
    files = sorted(CHECKPOINT_DIR.glob("*.pt"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [
        {
            "checkpoint": f.name,
            "path": str(f),
            "modified": f.stat().st_mtime,
        }
        for f in files
    ]

def generate_VGAE_graph(
    *,
    edges_path: str,
    nodes_path: str,
    n: int | None,
    threshold: float,
    model_name: str = "VGAE",
    epochs: int = 200,
    hidden1: int = 32,
    hidden2: int = 16,
    lr: float = 0.01,
    seed: int | None = None,
    checkpoint: str | None = None,
) -> dict:
    """
    Programmatic API equivalent of calling the CLI, returning the same JSON
    structure that the script prints.
    """
    return train_and_generate(
        edges_path=edges_path,
        nodes_path=nodes_path,
        n=n,
        threshold=threshold,
        model_name=model_name,
        epochs=epochs,
        hidden1=hidden1,
        hidden2=hidden2,
        lr=lr,
        seed=seed,
        checkpoint=checkpoint,
    )

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train and generate using VGAE.")
    parser.add_argument("--edges_path", required=True, help="Path to the edges CSV file.")
    parser.add_argument("--nodes_path", required=True, help="Path to the nodes CSV file.")
    parser.add_argument("--n", type=int, help="Number of nodes to generate (default: full dataset).")
    parser.add_argument("--threshold", type=float, required=True, help="Threshold for edge generation.")
    parser.add_argument("--model_name", default="VGAE", help="Model name (default: VGAE).")
    parser.add_argument("--epochs", type=int, default=200, help="Number of training epochs (default: 200).")
    parser.add_argument("--hidden1", type=int, default=32, help="Size of first hidden layer (default: 32).")
    parser.add_argument("--hidden2", type=int, default=16, help="Size of second hidden layer (default: 16).")
    parser.add_argument("--lr", type=float, default=0.01, help="Learning rate (default: 0.01).")
    parser.add_argument("--seed", type=int, help="Random seed (optional).")
    parser.add_argument("--checkpoint", help="Path to an existing checkpoint to use for generation (optional).")

    args = parser.parse_args()

    result = train_and_generate(
        edges_path=args.edges_path,
        nodes_path=args.nodes_path,
        n=args.n,
        threshold=args.threshold,
        model_name=args.model_name,
        epochs=args.epochs,
        hidden1=args.hidden1,
        hidden2=args.hidden2,
        lr=args.lr,
        seed=args.seed,
        checkpoint=args.checkpoint,
    )

    print(json.dumps(result, indent=4))