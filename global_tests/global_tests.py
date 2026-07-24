import csv
import networkx as nx
from rdflib import Graph

# from export_layer.schema_func import csv_export, neo4j_export, rdf_export

from export_layer.schema_func import  csv_export, neo4j_export, rdf_export


def nx_to_export_graph(G):
    return {
        "nodes": [
            {
                "id": str(node),
                **attrs,
            }
            for node, attrs in G.nodes(data=True)
        ],
        "edges": [
            {
                "source": str(u),
                "target": str(v),
                **attrs,
            }
            for u, v, attrs in G.edges(data=True)
        ],
        "metadata": {
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "directed": G.is_directed(),
            **dict(G.graph),
        },
    }


def test_barabasi_albert_exports_end_to_end(tmp_path):
    G = nx.barabasi_albert_graph(10, 2, seed=42)

    G.graph["model"] = "barabasi_albert"
    G.graph["seed"] = 42

    for node in G.nodes():
        G.nodes[node]["kind"] = "synthetic"

    for u, v in G.edges():
        G[u][v]["relation"] = "connects"

    graph = nx_to_export_graph(G)

    assert len(graph["nodes"]) == 10
    assert len(graph["edges"]) == G.number_of_edges()

    assert graph["metadata"]["model"] == "barabasi_albert"
    assert graph["metadata"]["seed"] == 42
    assert graph["metadata"]["directed"] is False
    assert "kind" in graph["nodes"][0]
    assert "relation" in graph["edges"][0]

    csv_dir = tmp_path / "csv_out"
    neo4j_dir = tmp_path / "neo4j_out"
    rdf_file = tmp_path / "graph.rdf"

    csv_export(graph, str(csv_dir))
    neo4j_export(graph, str(neo4j_dir))
    rdf_export(graph, str(rdf_file))

    assert (csv_dir / "nodes.csv").exists()
    assert (csv_dir / "edges.csv").exists()

    assert (neo4j_dir / "nodes.csv").exists()
    assert (neo4j_dir / "relationships.csv").exists()

    assert rdf_file.exists()

    with open(csv_dir / "nodes.csv", "r", encoding="utf-8") as f:
        csv_nodes = list(csv.DictReader(f))
    assert len(csv_nodes) == 10

    with open(neo4j_dir / "relationships.csv", "r", encoding="utf-8") as f:
        neo4j_edges = list(csv.DictReader(f))
    assert len(neo4j_edges) == G.number_of_edges()

    rdf_graph = Graph()
    rdf_graph.parse(rdf_file, format="xml")
    assert len(rdf_graph) > 0


    