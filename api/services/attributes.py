import random
from datetime import datetime, timezone



# values refer to box 1's entry/list 
# weights refer to box 2's entry/list for sampling


# NOTE rule is defined in AttributeRules.js and carries th following attributes:
    # id: newRuleId(),
    # name: "",
    # kind,
    # values: "", (usually as a list of strings form such as  ["admin", "user", "guest"],)
    # weights: "", like [0.1, 0.7, 0.2]
    # distribution: "uniform",
    # min: 0,
    # max: 1,
    # mean: 0,
    # std: 1,
    # start: "",
    # end: "",

# each function when called, if values and weights == in len
# then use prob. of value matched weight to provide output
def _sample_categorical(rule):
    values = rule["values"]
    weights = rule.get("weights")
    # ensure the number of weights to sample from equals # pf values provided
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

# main call function
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

    nodes = result.get("nodes")
    edges = result.get("edges")

    # handle any errors with ingested nodes or edge lists, debugged for runissues
    if not isinstance(nodes, list) or not all(isinstance(n, dict) for n in nodes):
        raise TypeError(
            f"Invalid graph structure: 'nodes' needs to be a list of node objects "
            f"(needs at least an 'id' field) but got {type(nodes).__name__} "
            f"with {len(nodes) if isinstance(nodes, list) else 'n/a'} items."
        )

    if not isinstance(edges, list) or not all(isinstance(e, dict) for e in edges):
        raise TypeError(
            f"Invalid graph structure: 'edges' needs to be a list of node objects "
            f"(needs'source' and 'target' fields) but got {type(edges).__name__} "
            f"with {len(edges) if isinstance(edges, list) else 'n/a'} items."
        )



    node_type = schema.get("node_type", "node")
    edge_type = schema.get("edge_type", "connected_to")
    node_attribute_rules = schema.get("node_attributes", [])
    edge_attribute_rules = schema.get("edge_attributes", [])

    for i, node in enumerate(nodes):
        node["type"] = node_type
        node["label"] = f"{node_type.capitalize()} {i + 1}"
        for rule in node_attribute_rules:
            name = rule.get("name")
            if name:
                node[name] = _sample_attribute(rule)

    for edge in edges:
        edge["type"] = edge_type
        for rule in edge_attribute_rules:
            name = rule.get("name")
            if name:
                edge[name] = _sample_attribute(rule)

    return result