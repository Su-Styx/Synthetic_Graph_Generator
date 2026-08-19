"""
convert_cora.py

Converts the raw Cora citation dataset (cora.content + cora.cites) into
nodes.csv / edges.csv matching the schema currently used by the VGAE
training pipeline:

nodes.csv:  node_index,node_id,node_type,node_name,node_source
edges.csv:  relation,display_relation,x_index,y_index

Usage:
    python convert_cora.py --content cora.content --cites cora.cites --outdir ./output

Notes on design decisions:
- node_index is a fresh 0..N-1 integer index assigned in the order papers
  appear in cora.content (this is what x_index/y_index in edges.csv refer to,
  matching how your existing nodes.csv/edges.csv pair works).
- node_id keeps the original Cora paper ID string, in the node_id column,
  the same way your example node_id column holds the original NCBI ID
  while node_index holds the fresh sequential index.
- node_type is set to the paper's class label (e.g. "Neural_Networks"),
  since Cora has no separate node "type" concept beyond its class -- this
  mirrors how node_type in your example holds a category like
  "gene/protein".
- node_name is also set to the paper ID (Cora has no separate human-readable
  title in this distribution), and node_source is fixed to "Cora".
- edges.csv direction: cora.cites lines are "<cited_id> <citing_id>", i.e.
  citing_id -> cited_id. This script maps:
      x_index = citing paper (source of the citation)
      y_index = cited paper  (target of the citation)
  relation is set to "citation", display_relation to "cites".
  If your VGAE expects an undirected adjacency (common for GAE/VGAE),
  pass --symmetric to also emit the reverse edge for every citation.
"""

import argparse
import csv
import os


def load_content(content_path):
    """Returns dict: paper_id (str) -> class_label (str), in file order."""
    paper_order = []
    paper_class = {}

    with open(content_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            paper_id = parts[0]
            class_label = parts[-1]
            paper_order.append(paper_id)
            paper_class[paper_id] = class_label

    return paper_order, paper_class


def build_node_table(paper_order, paper_class):
    """Assigns a fresh node_index per paper, in the order they appear."""
    id_to_index = {}
    rows = []

    for idx, paper_id in enumerate(paper_order):
        id_to_index[paper_id] = idx
        rows.append({
            "node_index": idx,
            "node_id": paper_id,
            "node_type": paper_class.get(paper_id, "Unknown"),
            "node_name": paper_id,
            "node_source": "Cora",
        })

    return rows, id_to_index


def build_edge_table(cites_path, id_to_index, symmetric=False):
    rows = []
    skipped = 0

    with open(cites_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                continue

            cited_id, citing_id = parts[0], parts[1]

            if cited_id not in id_to_index or citing_id not in id_to_index:
                # Some Cora distributions reference paper IDs that don't
                # appear in cora.content; skip these rather than failing.
                skipped += 1
                continue

            x_index = id_to_index[citing_id]  # source: the paper doing the citing
            y_index = id_to_index[cited_id]    # target: the paper being cited

            rows.append({
                "relation": "citation",
                "display_relation": "cites",
                "x_index": x_index,
                "y_index": y_index,
            })

            if symmetric:
                rows.append({
                    "relation": "citation",
                    "display_relation": "cites",
                    "x_index": y_index,
                    "y_index": x_index,
                })

    return rows, skipped


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Convert Cora dataset to nodes.csv/edges.csv")
    parser.add_argument("--content", required=True, help="Path to cora.content")
    parser.add_argument("--cites", required=True, help="Path to cora.cites")
    parser.add_argument("--outdir", default=".", help="Output directory")
    parser.add_argument(
        "--symmetric",
        action="store_true",
        help="Also emit the reverse edge for every citation (undirected graph).",
    )
    args = parser.parse_args()

    paper_order, paper_class = load_content(args.content)
    node_rows, id_to_index = build_node_table(paper_order, paper_class)
    edge_rows, skipped = build_edge_table(args.cites, id_to_index, symmetric=args.symmetric)

    os.makedirs(args.outdir, exist_ok=True)

    nodes_path = os.path.join(args.outdir, "nodes.csv")
    edges_path = os.path.join(args.outdir, "edges.csv")

    write_csv(
        nodes_path,
        node_rows,
        fieldnames=["node_index", "node_id", "node_type", "node_name", "node_source"],
    )
    write_csv(
        edges_path,
        edge_rows,
        fieldnames=["relation", "display_relation", "x_index", "y_index"],
    )

    print(f"Wrote {len(node_rows)} nodes to {nodes_path}")
    print(f"Wrote {len(edge_rows)} edges to {edges_path}")
    if skipped:
        print(f"Skipped {skipped} citation lines referencing paper IDs not found in {args.content}")


if __name__ == "__main__":
    main()
