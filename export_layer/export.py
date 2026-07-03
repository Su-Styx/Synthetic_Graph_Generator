import argparse 
from schema_func import * 









if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, choices=["JSON", "Neo4j", "CSV", "RDF", "Turtles"])
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.input, "r") as f:
            graph = json.load(f)

    if args.type == "JSON":
        json_export(graph, args.output)
    elif args.type == "Neo4j":
        neo4j_export(graph, args.output)
    elif args.type == "CSV":
        csv_export(graph, args.output)
    elif args.type == "RDF":
        rdf_export(graph, args.output)
    elif args.type == "Turtles":
        turtles_export(graph, args.output)