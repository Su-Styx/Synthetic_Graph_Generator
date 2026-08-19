import json
import subprocess
import sys

mtx_path = "/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Wikivote/soc-wiki-Vote.mtx"
seed = "42"

process = subprocess.run(
    ["Rscript", "ERGM_fit_runner.R", mtx_path, seed],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

if process.stderr:
    print("=== R STDERR / LOGS ===")
    print(process.stderr)

if process.returncode != 0:
    print(f"\nProcess failed with exit code {process.returncode}")
    sys.exit(process.returncode)

try:
    result = json.loads(process.stdout)
except json.JSONDecodeError as e:
    print("Failed to parse JSON from stdout")
    print("Raw stdout:")
    print(process.stdout[:2000])
    raise

print("=== JSON SUMMARY ===")
print("Top-level keys:", list(result.keys()))
print("Node count:", len(result.get("nodes", [])))
print("Edge count:", len(result.get("edges", [])))
print("Metadata keys:", list(result.get("metadata", {}).keys()))

metadata = result.get("metadata", {})

assert "nodes" in result, "Missing nodes"
assert "edges" in result, "Missing edges"
assert "metadata" in result, "Missing metadata"
assert metadata.get("fitted") is True, "metadata.fitted is not True"

print("ERGM runner output is valid.")

# --- Convergence check ---
convergence = metadata.get("convergence", {})
print("\n=== CONVERGENCE ===")
print(f"Chosen spec: {metadata.get('chosen_spec')}")
print(f"Converged: {convergence.get('converged')}")
if not convergence.get("converged", True):
    print(
        f"  failure_flag={convergence.get('failure_flag')}, "
        f"has_bad_std_errors={convergence.get('has_bad_std_errors')}"
    )

# --- Coefficient table ---
print("\n=== COEFFICIENTS ===")
for row in metadata.get("coefficient_table", []):
    est = row.get("estimate")
    se = row.get("std_error")
    p = row.get("p_value")
    print(f"  {row.get('term'):<30} estimate={est:.4f}  "
          f"se={se if se is None else round(se, 4)}  "
          f"p={p if p is None else round(p, 4)}")

print(f"\nAIC: {metadata.get('aic')}")
print(f"BIC: {metadata.get('bic')}")

# --- GOF summary ---
gof = metadata.get("gof")
if not gof:
    print("\nNo GOF results returned (gof step may have failed — check R stderr above).")
else:
    print("\n=== GOF SUMMARY (per statistic) ===")
    for stat_name, records in gof.items():
        p_values = [
            r.get("MC.p.value") or r.get("MC.p.value.") or r.get("p.value")
            for r in records
            if isinstance(r, dict)
        ]
        p_values = [p for p in p_values if p is not None]

        min_p = min(p_values) if p_values else None
        print(f"  {stat_name:<12} bins={len(records):<4} min MC p-value={min_p}")

    # Save full GOF tables to disk for the dissertation evaluation section
    with open("gof_results.json", "w") as f:
        json.dump(gof, f, indent=2)
    print("\nFull GOF tables written to gof_results.json")

# Save the whole result too, useful for later analysis/plots
with open("ergm_run_result.json", "w") as f:
    json.dump(result, f, indent=2)
print("Full run result written to ergm_run_result.json")