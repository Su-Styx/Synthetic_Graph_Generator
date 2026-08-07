import subprocess
import json
import uuid
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent
GENERATE_SCRIPT = BASE_DIR / "vgae_pytorch" / "generate.py"
TRAIN_SCRIPT = BASE_DIR / "vgae_pytorch" / "train.py"

CHECKPOINT_DIR = BASE_DIR / "media" / "vgae_checkpoints"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


def generate(checkpoint: str, n: int, t: float, seed: Optional[int] = None) -> dict:
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

    if seed is not None:
        cmd += ["--seed", str(seed)]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)

    if result.returncode != 0:
        raise RuntimeError(f"VGAE generate failed: {result.stderr.strip()}")

    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError as e:
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

    try:
        payload = json.loads(result.stdout.strip())
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"VGAE train returned invalid JSON. "
            f"stdout head: {result.stdout[:500]!r}, stderr head: {result.stderr[:500]!r}"
        ) from e

    payload["checkpoint"] = str(checkpoint_path)
    payload["checkpoint_name"] = checkpoint_path.name
    return payload


def train_and_generate(
    edges_path: str,
    n: int,
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
    if checkpoint:
        generated = generate(checkpoint=checkpoint, n=n, t=threshold, seed=seed)
        generated.setdefault("metadata", {})
        generated["metadata"]["checkpoint"] = checkpoint
        generated["metadata"]["trained"] = False
        return generated

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

    generated = generate(
        checkpoint=training_result["checkpoint"],
        n=n,
        t=threshold,
        seed=seed,
    )

    generated.setdefault("metadata", {})
    generated["metadata"]["checkpoint"] = training_result["checkpoint_name"]
    generated["metadata"]["training"] = training_result
    generated["metadata"]["trained"] = True
    return generated


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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train and generate using VGAE.")
    parser.add_argument("--edges_path", required=True, help="Path to the edges CSV file.")
    parser.add_argument("--nodes_path", help="Path to the nodes CSV file (optional).")
    parser.add_argument("--n", type=int, required=True, help="Number of nodes to generate.")
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

    # python VGAE_endpoint.py --edges_path /home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/edges.csv --nodes_path  /home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/nodes.csv --n 30 --threshold 0.5 --model_name VGAE --epochs 2 --hidden1 32 --hidden2 16 --lr .01 --seed 42 
# MAC RUN: python VGAE_endpoint.py --edges_path /Users/nicholas/Desktop/MSC_Works/DISSERTATION/Synthetic_Graph_Generator/Synthetic_Graph_Generator/Data/Dataverse/edges.csv --nodes_path  /Users/nicholas/Desktop/MSC_Works/DISSERTATION/Synthetic_Graph_Generator/Synthetic_Graph_Generator/Data/Dataverse/nodes.csv --n 30 --threshold 0.5 --model_name VGAE --epochs 2 --hidden1 32 --hidden2 16 --lr .01 --seed 42