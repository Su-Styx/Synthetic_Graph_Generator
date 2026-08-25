

import argparse
import csv
import math
import statistics
from pathlib import Path

import networkx as nx
from scipy.stats import chisquare, binom


def test_configuration(n, p, runs, seed_start):
    all_degrees = []
    edge_counts = []

    for run in range(runs):
        graph = nx.erdos_renyi_graph(n, p, seed=seed_start + run)
        all_degrees.extend(dict(graph.degree()).values())
        edge_counts.append(graph.number_of_edges())

    trials = n - 1
    expected_mean_degree = trials * p
    expected_degree_variance = trials * p * (1 - p)
    generated_mean_degree = statistics.mean(all_degrees)
    generated_degree_variance = statistics.variance(all_degrees)
    variance_ratio = generated_degree_variance / expected_degree_variance

    possible_edges = n * (n - 1) // 2
    expected_edges = possible_edges * p
    mean_generated_edges = statistics.mean(edge_counts)
    generated_density = mean_generated_edges / possible_edges

    # Use scipy's stable binomial probability calculation. This avoids
    # converting enormous factorial values to floating point numbers.
    observed = [all_degrees.count(k) for k in range(trials + 1)]
    expected = [len(all_degrees) * binom.pmf(k, trials, p) for k in range(trials + 1)]

    # Remove bins with negligible expected counts, then renormalise expected
    # counts so that observed and expected totals are exactly equal.
    keep = [i for i, value in enumerate(expected) if value >= 1e-8]
    observed_kept = [observed[i] for i in keep]
    expected_kept = [expected[i] for i in keep]
    scale = sum(observed_kept) / sum(expected_kept)
    expected_kept = [value * scale for value in expected_kept]

    gof = chisquare(observed_kept, expected_kept)

    return {
        "nodes": n,
        "p": p,
        "runs": runs,
        "possible_edges": possible_edges,
        "expected_edges": expected_edges,
        "mean_generated_edges": mean_generated_edges,
        "generated_density": generated_density,
        "expected_mean_degree": expected_mean_degree,
        "mean_generated_degree": generated_mean_degree,
        "expected_degree_variance": expected_degree_variance,
        "generated_degree_variance": generated_degree_variance,
        "degree_variance_ratio": variance_ratio,
        "chi_square_statistic": gof.statistic,
        "chi_square_p_value": gof.pvalue,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", nargs="+", type=int, default=[100, 1000, 5000])
    parser.add_argument("--p", nargs="+", type=float, default=[0.2, 0.4, 0.6])
    parser.add_argument("--runs", type=int, default=15)
    parser.add_argument("--seed-start", type=int, default=1000)
    parser.add_argument("--output", type=Path, default=Path("degree_distribution_summary.csv"))
    args = parser.parse_args()

    if len(args.n) != len(args.p):
        parser.error("--n and --p must contain the same number of values")

    results = []
    for index, (n, p) in enumerate(zip(args.n, args.p)):
        results.append(test_configuration(n, p, args.runs, args.seed_start + index * 100000))

    fields = list(results[0].keys())
    with args.output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print("\nDegree-distribution results:\n")
    for result in results:
        print(
            f"n={result['nodes']}, p={result['p']}: "
            f"mean degree {result['mean_generated_degree']:.4f} "
            f"(expected {result['expected_mean_degree']:.4f}), "
            f"variance ratio {result['degree_variance_ratio']:.4f}, "
            f"chi-square p-value {result['chi_square_p_value']:.4f}"
        )

    print(f"\nSaved results to {args.output}")


if __name__ == "__main__":
    main()
