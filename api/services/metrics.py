# import networkx as nx


# def _to_networkx(result: dict) -> nx.Graph:
#     G = nx.Graph()
#     for node in result.get("nodes", []):
#         node_id = node["id"]
#         attrs = {k: v for k, v in node.items() if k != "id"}
#         G.add_node(node_id, **attrs)

#     edges = result.get("edges", result.get("links", []))
#     for edge in edges:
#         attrs = {k: v for k, v in edge.items() if k not in ("source", "target")}
#         G.add_edge(edge["source"], edge["target"], **attrs)

#     return G


# def preliminary_fields(G: nx.Graph) -> dict:
#     n = G.number_of_nodes()
#     m = G.number_of_edges()

#     node_ids = list(G.nodes())
#     duplicate_ids = len(node_ids) != len(set(node_ids))

#     dangling_edges = [
#         (u, v) for u, v in G.edges()
#         if u not in G.nodes or v not in G.nodes
#     ]

#     self_loops = nx.number_of_selfloops(G)

#     return {
#         "node_count": n,
#         "edge_count": m,
#         "duplicate_node_ids": duplicate_ids,
#         "dangling_edge_count": len(dangling_edges),
#         "self_loop_count": self_loops,
#         "is_valid_graph": n > 0 and not duplicate_ids and len(dangling_edges) == 0,
#     }


# def completeness(G: nx.Graph) -> dict:
#     if G.number_of_nodes() == 0:
#         return {
#             "connected_components": 0,
#             "largest_component_ratio": "n/a",
#             "isolated_node_count": 0,
#             "has_giant_component": "n/a",
#         }

#     components = list(nx.connected_components(G))
#     largest = max(len(c) for c in components) if components else 0
#     isolated = nx.number_of_isolates(G)

#     return {
#         "connected_components": len(components),
#         "largest_component_ratio": round(largest / G.number_of_nodes(), 4),
#         "isolated_node_count": isolated,
#         "has_giant_component": largest / G.number_of_nodes() > 0.5,
#     }


# def structural_fidelity(G: nx.Graph, source_result: dict | None) -> dict:
#     if not source_result:
#         return {
#             "degree_distribution_similarity": "n/a",
#             "clustering_similarity": "n/a",
#             "density_delta": "n/a",
#             "note": "No source/input data provided — structural fidelity requires ground-truth graph for comparison.",
#         }

#     G_source = _to_networkx(source_result)

#     gen_degrees = sorted([d for _, d in G.degree()])
#     src_degrees = sorted([d for _, d in G_source.degree()])

#     try:
#         from scipy.stats import wasserstein_distance
#         degree_similarity = round(
#             1 / (1 + wasserstein_distance(gen_degrees, src_degrees)), 4
#         )
#     except ImportError:
#         degree_similarity = "n/a"

#     gen_clustering = nx.average_clustering(G) if G.number_of_nodes() > 0 else 0
#     src_clustering = nx.average_clustering(G_source) if G_source.number_of_nodes() > 0 else 0
#     clustering_similarity = round(1 - abs(gen_clustering - src_clustering), 4)

#     gen_density = nx.density(G)
#     src_density = nx.density(G_source)

#     return {
#         "degree_distribution_similarity": degree_similarity,
#         "clustering_similarity": clustering_similarity,
#         "density_delta": round(gen_density - src_density, 4),
#     }


# def quantitative_metrics(G: nx.Graph) -> dict:
#     n = G.number_of_nodes()
#     m = G.number_of_edges()

#     if n == 0:
#         return {
#             "n_nodes": 0, "n_edges": 0, "avg_degree": "n/a",
#             "degree_assortativity": "n/a", "avg_clustering_coefficient": "n/a",
#             "avg_path_length": "n/a", "triangle_count": "n/a", "density": "n/a",
#         }

#     degrees = [d for _, d in G.degree()]
#     avg_degree = round(sum(degrees) / n, 4)

#     try:
#         assortativity = round(nx.degree_assortativity_coefficient(G), 4)
#         if assortativity != assortativity:  # NaN check
#             assortativity = "n/a (undefined for regular-degree graphs)"
#     except Exception:
#         assortativity = "n/a"

#     avg_clustering = round(nx.average_clustering(G), 4)
#     triangle_count = sum(nx.triangles(G).values()) // 3

#     if nx.is_connected(G):
#         avg_path_length = round(nx.average_shortest_path_length(G), 4)
#     else:
#         components = [G.subgraph(c).copy() for c in nx.connected_components(G) if len(c) > 1]
#         if components:
#             lengths = [nx.average_shortest_path_length(c) for c in components]
#             avg_path_length = round(sum(lengths) / len(lengths), 4)
#         else:
#             avg_path_length = "n/a (no multi-node components)"

#     return {
#         "n_nodes": n,
#         "n_edges": m,
#         "avg_degree": avg_degree,
#         "max_degree": max(degrees),
#         "degree_assortativity": assortativity,
#         "avg_clustering_coefficient": avg_clustering,
#         "avg_path_length": avg_path_length,
#         "triangle_count": triangle_count,
#         "density": round(nx.density(G), 4),
#     }


# def compute_all_metrics(result: dict, source_result: dict | None = None) -> dict:
#     G = _to_networkx(result)

#     return {
#         "preliminary_fields": preliminary_fields(G),
#         "completeness": completeness(G),
#         "structural_fidelity": structural_fidelity(G, source_result),
#         "quantitative_metrics": quantitative_metrics(G),
#     }

"""
Graph metrics module — computes structural and comparative metrics for generated graphs.

This module provides a layered analysis:
1. preliminary_fields: Basic sanity checks (valid nodes/edges, no duplicates, etc.)
2. completeness: Connectivity structure (components, isolated nodes, giant component)
3. structural_fidelity: Comparison to a source/ground-truth graph (degree distribution, clustering, density)
4. quantitative_metrics: Standard network science metrics (assortativity, path length, triangles, etc.)

All functions accept a NetworkX graph or a graph dict (nodes/edges format) and return
human-readable dicts suitable for API responses or dashboard display.
"""

import networkx as nx
from typing import Optional


def _to_networkx(result: dict) -> nx.Graph:
    """
    Convert a graph dict (from ERGM, VGAE, etc.) to a NetworkX Graph.
    
    Expected input format:
    {
        "nodes": [{"id": "1", ...}, {"id": "2", ...}],
        "edges": [{"source": "1", "target": "2", ...}, ...]
    }
    
    Node attributes (all fields except 'id') and edge attributes (all fields except
    'source'/'target') are preserved.
    """
    G = nx.Graph()
    
    for node in result.get("nodes", []):
        node_id = node["id"]
        # Preserve all node attributes except the 'id' field
        attrs = {k: v for k, v in node.items() if k != "id"}
        G.add_node(node_id, **attrs)

    # Support both 'edges' and 'links' keys (some generators use 'links')
    edges = result.get("edges", result.get("links", []))
    for edge in edges:
        # Preserve all edge attributes except 'source' and 'target'
        attrs = {k: v for k, v in edge.items() if k not in ("source", "target")}
        G.add_edge(edge["source"], edge["target"], **attrs)

    return G


def preliminary_fields(G: nx.Graph) -> dict:
    """
    Run basic sanity checks on the graph structure.
    
    Returns flags for:
    - Node and edge counts
    - Duplicate node IDs (should never happen in a valid graph)
    - Dangling edges (edges referencing non-existent nodes)
    - Self-loops (edges from a node to itself)
    - Overall validity (passes all checks)
    """
    n = G.number_of_nodes()
    m = G.number_of_edges()

    # Check for duplicate node IDs (indicates a serialization or generation bug)
    node_ids = list(G.nodes())
    duplicate_ids = len(node_ids) != len(set(node_ids))

    # Check for edges that reference nodes that don't exist
    dangling_edges = [
        (u, v) for u, v in G.edges()
        if u not in G.nodes or v not in G.nodes
    ]

    # Count self-loops (often acceptable, but worth flagging)
    self_loops = nx.number_of_selfloops(G)

    return {
        "node_count": n,
        "edge_count": m,
        "duplicate_node_ids": duplicate_ids,
        "dangling_edge_count": len(dangling_edges),
        "self_loop_count": self_loops,
        "is_valid_graph": n > 0 and not duplicate_ids and len(dangling_edges) == 0,
    }


def completeness(G: nx.Graph) -> dict:
    """
    Assess the connectivity structure of the graph.
    
    Returns:
    - Number of connected components
    - Ratio of nodes in the largest component (0–1)
    - Count of isolated nodes (degree = 0)
    - Whether a "giant component" exists (>50% of nodes in one component)
    """
    if G.number_of_nodes() == 0:
        return {
            "connected_components": 0,
            "largest_component_ratio": "n/a",
            "isolated_node_count": 0,
            "has_giant_component": "n/a",
        }

    components = list(nx.connected_components(G))
    largest = max(len(c) for c in components) if components else 0
    isolated = nx.number_of_isolates(G)

    return {
        "connected_components": len(components),
        "largest_component_ratio": round(largest / G.number_of_nodes(), 4),
        "isolated_node_count": isolated,
        "has_giant_component": largest / G.number_of_nodes() > 0.5,
    }


def structural_fidelity(G: nx.Graph, source_result: Optional[dict] = None) -> dict:

    # Compare the generated graph to a groundtruth
    
    # Measures:
    # - Degree distribution similarity from Wasserstein distance, normalised into 0 to 1 
    # - Clustering coefficient similarity abs difference
    # - Density delta generated − source a positive value indicates more dense 
    

    if not source_result:
        return {
            "degree_distribution_similarity": "n/a",
            "clustering_similarity": "n/a",
            "density_delta": "n/a",
            "note": "No source/input data provided — structural fidelity requires ground-truth graph for comparison.",
        }

    G_source = _to_networkx(source_result)

    # Compare degree distributions using Wasserstein distance
    gen_degrees = sorted([d for _, d in G.degree()])
    src_degrees = sorted([d for _, d in G_source.degree()])

    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wasserstein_distance.html
    try:
        from scipy.stats import wasserstein_distance
        # Transform distance to similarity: 1 / (1 + distance) = 1.0 = identical, 0.0 = no similarity
        degree_similarity = round(
            1 / (1 + wasserstein_distance(gen_degrees, src_degrees)), 4
        )
    except ImportError:
        degree_similarity = "n/a"

    # Compare avg clustering coefficients
    gen_clustering = nx.average_clustering(G) if G.number_of_nodes() > 0 else 0
    src_clustering = nx.average_clustering(G_source) if G_source.number_of_nodes() > 0 else 0
    clustering_similarity = round(1-abs(gen_clustering - src_clustering), 4)

    # Compare densities
    gen_density = nx.density(G)
    src_density = nx.density(G_source)

    return {
        "degree_distribution_similarity": degree_similarity,
        "clustering_similarity": clustering_similarity,
        "density_delta": round(1-abs(gen_density - src_density), 4),
    }


def quantitative_metrics(G: nx.Graph) -> dict:
 
    #  func to return:
    
    # Returns:
    # Basic counts (nodes, edges)
    # Degree statistics (average, max)
    # Degree assortativity (tendency for high-degree nodes to connect to other high-degree nodes)
    # Average clustering coefficient (triadic closure tendency)
    # Average path length (typical distance between nodes)
    # Triangle count
    # Density

    n = G.number_of_nodes()
    m = G.number_of_edges()

    if n == 0:
        return {
            "n_nodes": 0, "n_edges": 0, "avg_degree": "n/a",
            "degree_assortativity": "n/a", "avg_clustering_coefficient": "n/a",
            "avg_path_length": "n/a", "triangle_count": "n/a", "density": "n/a",
        }

    degrees = [d for _, d in G.degree()]
    avg_degree = round(sum(degrees) / n, 4)

    # Degree assortativity: -1 (disassortative) to +1 (assortative), 0 = neutral
    try:
        assortativity = round(nx.degree_assortativity_coefficient(G), 4)
        # Handle NaN for regular-degree graphs (all nodes have same degree)
        if assortativity != assortativity:  # NaN check
            assortativity = "n/a (undefined for regular-degree graphs)"
    except Exception:
        assortativity = "n/a"

    # average clustering: 0 = no triangles, 1 = fully clustered
    avg_clustering = round(nx.average_clustering(G), 4)
    
    # triangle count each triangle is counted 3 times in nx.triangles, div by 3
    triangle_count = sum(nx.triangles(G).values()) // 3

    # avg path length is only defined for connected graphs
    if nx.is_connected(G):
        avg_path_length = round(nx.average_shortest_path_length(G), 4)
    else:
        # when >1 component exists, take average 
        components = [G.subgraph(c).copy() for c in nx.connected_components(G) if len(c) > 1]
        if components:
            lengths = [nx.average_shortest_path_length(c) for c in components]
            avg_path_length = round(sum(lengths) / len(lengths), 4)
        else:
            avg_path_length = "n/a (no multi-node components)"

    density=round(nx.density(G),4)

    return {
        "n_nodes": n,
        "n_edges": m,
        "avg_degree": avg_degree,
        "max_degree": max(degrees),
        "degree_assortativity": assortativity,
        "avg_clustering_coefficient": avg_clustering,
        "avg_path_length": avg_path_length,
        "triangle_count": triangle_count,
        "density": density,
    }


def compute_all_metrics(result: dict, source_result: Optional[dict] = None) -> dict:
    
    # main call/compute metrics section
    
    # result is required, output from the generated graph dict
    # source_result is the same just 
    
    # nested dictionary with 4 main sections:
    #     preliminary_fields: Basic validity checks
    #     completeness: Connectivity structure
    #     structural_fidelity: Comparison to source (if provided)
    #     quantitative_metrics: Standard network metrics
    
    G = _to_networkx(result)

    return {
        "preliminary_fields": preliminary_fields(G),
        "completeness": completeness(G),
        "structural_fidelity": structural_fidelity(G, source_result),
        "quantitative_metrics": quantitative_metrics(G),
    }