# import networkx as nx
# from .metrics import _to_networkx

# GENERIC_QUERIES = {
#     "top_degree_nodes": lambda G: sorted(G.degree(), key=lambda x: -x[1])[:10],
#     "isolated_nodes": lambda G: list(nx.isolates(G)),
#     "connected_components_sizes": lambda G: sorted(
#         [len(c) for c in nx.connected_components(G)], reverse=True
#     ),
#     "bridges": lambda G: list(nx.bridges(G)) if nx.is_connected(G) else "n/a (graph not connected)",
#     "articulation_points": lambda G: list(nx.articulation_points(G)),
# }


# def run_generic_queries(result: dict) -> dict:
#     G = _to_networkx(result)
#     output = {}
#     for name, fn in GENERIC_QUERIES.items():
#         try:
#             output[name] = fn(G)
#         except Exception as e:
#             output[name] = f"error: {e}"
#     return output


# def run_custom_query(result: dict, query_type: str, params: dict | None = None) -> dict:
#     G = _to_networkx(result)
#     params = params or {}

#     if query_type == "neighbors":
#         node_id = params.get("node_id")
#         try:
#             node_id = int(node_id)
#         except (TypeError, ValueError):
#             return {"error": f"invalid node_id: {node_id!r}"}

#         if node_id not in G:
#             return {"error": f"node {node_id} not found"}
#         return {"node_id": node_id, "neighbors": list(G.neighbors(node_id))}

#     if query_type == "shortest_path":
#         try:
#             source = int(params.get("source"))
#             target = int(params.get("target"))
#         except (TypeError, ValueError):
#             return {"error": "source and target must be valid node IDs"}

#         try:
#             path = nx.shortest_path(G, source=source, target=target)
#             return {"path": path, "length": len(path) - 1}
#         except nx.NetworkXNoPath:
#             return {"error": "no path exists between these nodes"}
#         except nx.NodeNotFound as e:
#             return {"error": str(e)}

#     if query_type == "filter_by_attribute":
#         attr = params.get("attribute")
#         value = params.get("value")
#         matches = [n for n, d in G.nodes(data=True) if d.get(attr) == value]
#         return {"attribute": attr, "value": value, "matching_nodes": matches, "count": len(matches)}

#     if query_type == "subgraph_by_type":
#         node_type = params.get("node_type")
#         nodes = [n for n, d in G.nodes(data=True) if d.get("type") == node_type]
#         sub = G.subgraph(nodes)
#         return {
#             "node_type": node_type,
#             "node_count": sub.number_of_nodes(),
#             "edge_count": sub.number_of_edges(),
#         }

#     return {"error": f"orted query_type: {query_type}"}



# Generic queries will be common queries, including top degree nodes, isolated nodes, cc size, bridges and articulation points
# Custom queries will be parametrized for desired ucse cases, such as neighbours, shortest paths and filtering by attribute,
# aim is to minimise the user input


import networkx as nx
from typing import Optional
from .metrics import _to_networkx


#generic queries as a dictionary ingesting graph, each takes 2 parameters and is consolidated to list
GENERIC_QUERIES = {
    "top_degree_nodes": lambda G: sorted(G.degree(), key=lambda x: -x[1])[:10],

    "isolated_nodes": lambda G: list(nx.isolates(G)),

    "connected_components_sizes": lambda G: sorted(
        [len(c) for c in nx.connected_components(G)], reverse=True),
    "bridges": lambda G: list(nx.bridges(G)) if nx.is_connected(G) else "n/a (graph not connected)",
    "articulation_points": lambda G: list(nx.articulation_points(G)),
}


def run_generic_queries(result: dict) -> dict:

    # call to and execute generic queries 
    G = _to_networkx(result)
    output = {}
    
    for name, fn in GENERIC_QUERIES.items():
        try:
            output[name] = fn(G)
        except Exception as e:
            # Catch any unexpected errors (e.g. disconnected graph for bridges) and report them
            output[name] = f"error: {e}"
    
    return output


def run_custom_query(result: dict, query_type: str, params: Optional[dict] = None) -> dict:

    # pre-defined 'custom'queries are neighbors, shortest path, filter by attribute filter by type(subgraph)

    # the parameters ingested are (result, query_type, params), summoned by views.py in WorkloadQueryView

    # Run a parameterized custom query on the graph.
    # returns a dictionary of short string description and value... or error

    G = _to_networkx(result)
    params = params or {}


    if query_type == "neighbors":
        node_id = params.get("node_id")
        
        # Try to convert to int (node IDs are generally stored as strings in JSON)
        try:
            node_id = int(node_id)
        except (TypeError, ValueError):
            return {"error": f"invalid node_id: {node_id!r}"}

        if node_id not in G:
            return {"error": f"node {node_id} not found"}
        
        return {"node_id": node_id, "neighbors": list(G.neighbors(node_id))}


    if query_type == "shortest_path":
        try:
            source = int(params.get("source"))
            target = int(params.get("target"))
        except (TypeError, ValueError):
            return {"error": "source and target require valid node IDs"}

        try:
            path = nx.shortest_path(G, source=source, target=target)
            return {"path": path, "length": len(path) - 1}  # length = number of edges, not nodes
        except nx.NetworkXNoPath:
            return {"error": "no path exists between these nodes"}
        except nx.NodeNotFound as e:
            return {"error": str(e)}


    if query_type == "filter_by_attribute":
        attr = params.get("attribute")
        value = params.get("value")
        
        # Search node attributes for matching key-value pair
        matches = [n for n, d in G.nodes(data=True) if d.get(attr) == value]
        
        return {
            "attribute": attr,
            "value": value,
            "matching_nodes": matches,
            "count": len(matches),
        }

    if query_type == "subgraph_by_type":
        node_type = params.get("node_type")
        
        # Find all nodes where node["type"] == node_type
        nodes = [n for n, d in G.nodes(data=True) if d.get("type") == node_type]
        sub = G.subgraph(nodes)
        
        return {
            "node_type": node_type,
            "node_count": sub.number_of_nodes(),
            "edge_count": sub.number_of_edges(),
        }

    # catching unspecified queries (for debugging the development)
    return {"error": f"unsupported query_type: {query_type}"}