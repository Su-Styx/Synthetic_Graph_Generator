let ruleIdCounter = 0;

function newRuleId() {
  ruleIdCounter += 1;
  return `rule-${Date.now()}-${ruleIdCounter}`;
}

export function emptyRule(kind = "categorical") {
  return {
    id: newRuleId(),
    name: "",
    kind,
    values: "",
    weights: "",
    distribution: "uniform",
    min: 0,
    max: 1,
    mean: 0,
    std: 1,
    start: "",
    end: "",
  };
}

export function serializeRule(rule) {
  const name = rule.name.trim();
  if (!name) return null;

  if (rule.kind === "categorical") {
    const values = rule.values.split(",").map((v) => v.trim()).filter(Boolean);
    if (!values.length) return null;

    const parsedWeights = rule.weights.trim()
      ? rule.weights.split(",").map((w) => Number(w.trim())).filter((w) => !Number.isNaN(w))
      : [];

    return {
      name,
      kind: "categorical",
      values,
      ...(parsedWeights.length === values.length ? { weights: parsedWeights } : {}),
    };
  }

  if (rule.kind === "numeric") {
    return rule.distribution === "normal"
      ? {
          name,
          kind: "numeric",
          distribution: "normal",
          mean: Number(rule.mean),
          std: Number(rule.std),
        }
      : {
          name,
          kind: "numeric",
          distribution: "uniform",
          min: Number(rule.min),
          max: Number(rule.max),
        };
  }

  if (rule.kind === "timestamp") {
    if (!rule.start || !rule.end) return null;
    return { name, kind: "timestamp", start: rule.start, end: rule.end };
  }

  return null;
}

export function buildAttributeConfig(rules) {
  return rules.map(serializeRule).filter(Boolean);
}