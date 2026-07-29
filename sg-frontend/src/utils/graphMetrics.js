// src/utils/graphMetrics.js
export function buildGraphData(result) {
  if (!result) return null;

  const nodes = Array.isArray(result.nodes) ? result.nodes : [];
  const rawLinks = result.links ?? result.edges ?? [];
  if (!nodes.length) return null;

  const links = rawLinks.map((edge, i) => ({
    id: edge.id ?? `edge-${i}`,
    label: edge.label ?? edge.type ?? "",
    ...edge,
  }));

  return { nodes, links };
}

export function computeMetrics(graphData) {
  if (!graphData) return null;
  const { nodes, links } = graphData;
  const n = nodes.length;
  const m = links.length;
  if (!n) return null;

  const adj = new Map(nodes.map((node) => [node.id, new Set()]));
  links.forEach(({ source, target }) => {
    const s = source?.id ?? source;
    const t = target?.id ?? target;
    adj.get(s)?.add(t);
    adj.get(t)?.add(s);
  });

  const degrees = nodes.map((node) => adj.get(node.id)?.size ?? 0);
  const avgDegree = degrees.reduce((a, b) => a + b, 0) / n;
  const density = n > 1 ? (2 * m) / (n * (n - 1)) : 0;

  const clusterSum = nodes.reduce((sum, node) => {
    const neighbors = [...(adj.get(node.id) ?? [])];
    const k = neighbors.length;
    if (k < 2) return sum;
    let linked = 0;
    for (let i = 0; i < k; i++)
      for (let j = i + 1; j < k; j++)
        if (adj.get(neighbors[i])?.has(neighbors[j])) linked++;
    return sum + linked / ((k * (k - 1)) / 2);
  }, 0);

  return {
    nodeCount: n,
    edgeCount: m,
    avgDegree: avgDegree.toFixed(2),
    maxDegree: Math.max(...degrees, 0),
    density: density.toFixed(4),
    avgClustering: (clusterSum / n).toFixed(4),
  };
}

export function extraKeys(items, coreKeys) {
  const keys = new Set();
  items?.forEach((item) =>
    Object.keys(item).forEach((k) => !coreKeys.has(k) && keys.add(k))
  );
  return [...keys];
}