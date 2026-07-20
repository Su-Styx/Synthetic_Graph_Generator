
import json
import csv
# import apoc 
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace 
from rdflib.namespace import RDF

# note default output from all models has been parsed as JSON for api endpoint usage 
# therefore, each function will intake a JSON dictionary structure, then convert

def validate_graph(graph: dict): #ensure a valid json graph is passed
    required = ["nodes", "edges", "metadata"]
    for key in required:
        if key not in graph:
            raise ValueError(f"Graph missing required key: {key}")


def json_export(graph: dict, out_path: str):
    validate_graph(graph)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)



def csv_export(graph: dict, out_path: str):
    validate_graph(graph)

    out_dir = Path(out_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    nodes_path = out_dir / "nodes.csv"
    edges_path = out_dir / "edges.csv"

    with open(nodes_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id"])
        writer.writeheader()
        writer.writerows(graph["nodes"])

    with open(edges_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target"])
        writer.writeheader()
        writer.writerows(graph["edges"])








def neo4j_export(graph: dict, out_path: str):
    # seems easier to convert from csv to neo4j than json to neo4j; reference https://www.neo4j.com/docs/getting-started/data-import/csv-import/ 

    validate_graph(graph)

    out_dir = Path(out_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    nodes_path = out_dir / "nodes.csv"
    rels_path = out_dir / "relationships.csv"

    with open(nodes_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id"])
        writer.writeheader()
        for node in graph["nodes"]:
            writer.writerow({"id": node["id"]})

    with open(rels_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target"])
        writer.writeheader()
        for edge in graph["edges"]:
            writer.writerow({
                "source": edge["source"],
                "target": edge["target"],
            })



#note primary difference in rdf_export vs turtles_export is the file extension (rdf triples vs a .ttl file) + data triples vs human readaibility (respectively)

# data output format:

# {"nodes": [ {id:0...etc}],"edges":[{"source":0,"target":1}...etc],
# "metadata":{"model": "vgae", "n_nodes": 20, "n_edges": 98, "directed": false,"parameters": {"threshold": 0.5}}}





# def rdf_export(graph: dict, out_path: str):
#     # triples are defined as SUBJECT,PREDICATE,OBJECT => SALLY, EMPLOYED, AMAZON 
#     # note that usually RDF is directed, as there exists a subject and an object 


#     # need to check if there are relations in the metadata, only exist with models compatible AND use it. 
#     g= Graph()
#     g.parse(json_export(graph,out_path))
#     # might be easier to parse from JSON-LD if it is linked data from origin
#     # v = g.serialize(format="json-ld")

#     import pprint
#     for stmt in g:
#         pprint.pprint(stmt)


        

#     # https://rdflib.readthedocs.io/en/stable/intro_to_parsing/#saving-rdf 

#     # EX = Namespace("http://example.org/") 
#     # if graph["metadata"]["relations"] == True:
#     #     # insert logic for non default relation parsing
#     #     pass 
#     # else:
#     #     # insert logic for normal relation
#     #     pass
#     # for n in graph["nodes"]:
#     #     pass
#     # for e in graph["edges"]:
#     #     pass


from rdflib import Graph, Namespace
from rdflib.namespace import RDF

EX = Namespace("http://example.org/")


def _build_rdf_graph(graph: dict) -> Graph:
    validate_graph(graph)

    g = Graph()
    g.bind("ex", EX)

    for node in graph["nodes"]:
        node_uri = EX[f"node/{node['id']}"]
        g.add((node_uri, RDF.type, EX.Node))

    for edge in graph["edges"]:
        source_uri = EX[f"node/{edge['source']}"]
        target_uri = EX[f"node/{edge['target']}"]
        g.add((source_uri, EX.connectsTo, target_uri))

    return g


def rdf_export(graph: dict, out_path: str):
    g = _build_rdf_graph(graph)
    g.serialize(destination=out_path, format="xml")


def turtle_export(graph: dict, out_path: str):
    g = _build_rdf_graph(graph)
    g.serialize(destination=out_path, format="turtle")