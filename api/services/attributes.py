
# {"nodes": [ {id:0...etc}],"edges":[{"source":0,"target":1}...etc],
# "metadata":{"model": "vgae", "n_nodes": 20, "n_edges": 98, "directed": false,"parameters": {"threshold": 0.5}}}
import random
from datetime import datetime, timezone

def apply_schema(result: dict, schema: dict | None) -> dict:
    if not schema:
        return result

    node_type = schema.get("node_type", "node")
    edge_type = schema.get("edge_type", "connected_to")

    for i, node in enumerate(result["nodes"]):
        node["type"] = node_type
        node["label"] = f"{node_type.capitalize()} {i + 1}"

    for edge in result["edges"]:
        edge["type"] = edge_type

    return result




def _sample_categorical(rule):
    values = rule["values"]
    weights = rule.get("weights")
    if weights and len(weights) == len(values):
        return random.choices(values, weights=weights, k=1)[0]
    return random.choice(values)


def _sample_numeric(rule):
    if rule.get("distribution") == "normal":
        return round(random.gauss(rule.get("mean", 0), rule.get("std", 1)), 4)
    return round(random.uniform(rule.get("min", 0), rule.get("max", 1)), 4)


def _sample_timestamp(rule):
    start = datetime.fromisoformat(rule["start"]).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(rule["end"]).replace(tzinfo=timezone.utc)
    if end <= start:
        return start.isoformat()
    delta = (end - start).total_seconds()
    offset = random.uniform(0, delta)
    sampled = start.timestamp() + offset
    return datetime.fromtimestamp(sampled, tz=timezone.utc).isoformat()


def _sample_attribute(rule):
    kind = rule.get("kind")
    if kind == "categorical":
        return _sample_categorical(rule)
    if kind == "numeric":
        return _sample_numeric(rule)
    if kind == "timestamp":
        return _sample_timestamp(rule)
    return None


def apply_schema(result: dict, schema: dict | None) -> dict:
    if not schema:
        return result

    node_type = schema.get("node_type", "node")
    edge_type = schema.get("edge_type", "connected_to")
    node_attribute_rules = schema.get("node_attributes", [])
    edge_attribute_rules = schema.get("edge_attributes", [])

    for i, node in enumerate(result["nodes"]):
        node["type"] = node_type
        node["label"] = f"{node_type.capitalize()} {i + 1}"

        for rule in node_attribute_rules:
            name = rule.get("name")
            if name:
                node[name] = _sample_attribute(rule)

    for edge in result["edges"]:
        edge["type"] = edge_type

        for rule in edge_attribute_rules:
            name = rule.get("name")
            if name:
                edge[name] = _sample_attribute(rule)

    return result