import json
import subprocess
import sys

mtx_path = "/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Soc-Wiki-Vote/wiki_vote_500_edgelist.txt"
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

assert "nodes" in result, "Missing nodes"
assert "edges" in result, "Missing edges"
assert "metadata" in result, "Missing metadata"
assert result["metadata"].get("fitted") is True, "metadata.fitted is not True"

print("ERGM runner output is valid.")