import pytest
import json
import csv
from pathlib import Path
from schema_func import json_export, csv_export, neo4j_export
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

from schema_func import json_export, csv_export, neo4j_export, rdf_export, turtle_export



@pytest.fixture
def sample_graph():
    return {
        "nodes": [
            {"id": "A"},
            {"id": "B"},
            {"id": "C"},
        ],
        "edges": [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
        ],
        "metadata": {
            "source": "test"
        }
    }



def test_json_export_writes_file(tmp_path, sample_graph):
    out_file = tmp_path / "graph.json"

    json_export(sample_graph, str(out_file))

    assert out_file.exists()

    with open(out_file, "r", encoding="utf-8") as f:
        saved = json.load(f)

    assert saved == sample_graph


def test_csv_export_writes_node_and_edge_files(tmp_path, sample_graph):
    out_dir = tmp_path / "csv_out"

    csv_export(sample_graph, str(out_dir))

    nodes_file = out_dir / "nodes.csv"
    edges_file = out_dir / "edges.csv"

    assert nodes_file.exists()
    assert edges_file.exists()

    with open(nodes_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert rows == [
        {"id": "A"},
        {"id": "B"},
        {"id": "C"},
    ]

    with open(edges_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert rows == [
        {"source": "A", "target": "B"},
        {"source": "B", "target": "C"},
    ]

def test_neo4j_export_writes_node_and_relationship_files(tmp_path, sample_graph):
    out_dir = tmp_path / "neo4j_out"

    neo4j_export(sample_graph, str(out_dir))

    nodes_file = out_dir / "nodes.csv"
    rels_file = out_dir / "relationships.csv"

    assert nodes_file.exists()
    assert rels_file.exists()

    with open(nodes_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert rows == [
        {"id": "A"},
        {"id": "B"},
        {"id": "C"},
    ]

    with open(rels_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert rows == [
        {"source": "A", "target": "B"},
        {"source": "B", "target": "C"},
    ]


def test_neo4j_export_raises_for_missing_nodes(tmp_path):
    bad_graph = {
        "edges": [{"source": "A", "target": "B"}],
        "metadata": {"source": "test"}
    }

    with pytest.raises(ValueError):
        neo4j_export(bad_graph, str(tmp_path / "neo4j_out"))


def test_neo4j_empty_graph_raises_error(tmp_path):
    empty_graph={}

    empty_graph2={
        "metadata":{"source":"something"}
    }

    with pytest.raises(ValueError):
        neo4j_export(empty_graph,str(tmp_path/"neo4j_out"))

    with pytest.raises(ValueError):
        neo4j_export(empty_graph2,str(tmp_path/"neo4j_out"))

#add missing key tests 





EX = Namespace("http://example.org/")


@pytest.fixture
def sample_graph():
    return {
        "nodes": [
            {"id": "A"},
            {"id": "B"},
            {"id": "C"},
        ],
        "edges": [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
        ],
        "metadata": {
            "source": "test"
        }
    }


def test_rdf_export_writes_valid_xml_rdf(tmp_path, sample_graph):
    out_file = tmp_path / "graph.rdf"

    rdf_export(sample_graph, str(out_file))

    assert out_file.exists()

    g = Graph()
    g.parse(out_file, format="xml")

    assert len(g) == 5


def test_rdf_export_contains_expected_triples(tmp_path, sample_graph):
    out_file = tmp_path / "graph.rdf"

    rdf_export(sample_graph, str(out_file))

    g = Graph()
    g.parse(out_file, format="xml")

    node_a = EX["node/A"]
    node_b = EX["node/B"]
    node_c = EX["node/C"]

    assert (node_a, RDF.type, EX.Node) in g
    assert (node_b, RDF.type, EX.Node) in g
    assert (node_c, RDF.type, EX.Node) in g
    assert (node_a, EX.connectsTo, node_b) in g
    assert (node_b, EX.connectsTo, node_c) in g


def test_turtle_export_writes_valid_turtle(tmp_path, sample_graph):
    out_file = tmp_path / "graph.ttl"

    turtle_export(sample_graph, str(out_file))

    assert out_file.exists()

    g = Graph()
    g.parse(out_file, format="turtle")

    assert len(g) == 5


def test_turtle_export_contains_expected_triples(tmp_path, sample_graph):
    out_file = tmp_path / "graph.ttl"

    turtle_export(sample_graph, str(out_file))

    g = Graph()
    g.parse(out_file, format="turtle")

    node_a = EX["node/A"]
    node_b = EX["node/B"]
    node_c = EX["node/C"]

    assert (node_a, RDF.type, EX.Node) in g
    assert (node_b, RDF.type, EX.Node) in g
    assert (node_c, RDF.type, EX.Node) in g
    assert (node_a, EX.connectsTo, node_b) in g
    assert (node_b, EX.connectsTo, node_c) in g


#add empty graph test 
#check overwrite logic 