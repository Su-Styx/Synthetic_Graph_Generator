# import sys, os
# from pathlib import Path

import subprocess

mtx_path = "/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Soc-Wiki-Vote/soc-wiki-Vote.mtx"
seed = "42"

process = subprocess.Popen(
    ["Rscript", "ERGM_fit_runner.R", mtx_path, seed],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

for line in process.stdout:
    print(line, end="")

process.wait()

if process.returncode != 0:
    print(f"\nProcess failed with exit code {process.returncode}")
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ERGM_model'))
# from ERGM_endpoint import fit_and_generate_from_file

# edge_file = Path(__file__).resolve().parent.parent.parent / "Data" / "woc-wiki-Vote" / ""
# assert edge_file.exists(), f"File not found: {edge_file}"

# result = fit_and_generate_from_file(
#     file_path=str(edge_file),
#     seed=42
# )
# print(result)

