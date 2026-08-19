from pathlib import Path
import json

import subprocess
seed_list=[]

n_vals={100:.3,1000:.4, 5000:.6}
# n_values=[100,1000,5000]
for i in range(0,15):
    seed_list.append(i)

seed=0

BASE_DIR = Path(__file__).resolve().parent
ER_endpoint  = BASE_DIR/ "ER_endpoint.py"
# cmd = [
#         "python3",
#         str(ER_endpoint),
#         "--n 100", " --p 3 ",
#         "--seed "+str(seed) 
#     ]



import re

text = "Prefix text TargetWord More text"
pattern = r'^.*?n_nodes'  # Matches start to the first occurrence of TargetWord

# Replace the matched prefix with an empty string

import pandas as pd

def parse_completed_processes(strings):
    n_nodes_pattern = re.compile(r'"n_nodes":\s*(\d+)')
    n_edges_pattern = re.compile(r'"n_edges":\s*(\d+)')

    records = []
    for s in strings:
        n_nodes_match = n_nodes_pattern.search(s)
        n_edges_match = n_edges_pattern.search(s)

        records.append({
            "n_nodes": int(n_nodes_match.group(1)) if n_nodes_match else None,
            "n_edges": int(n_edges_match.group(1)) if n_edges_match else None,
        })

    return pd.DataFrame(records, columns=["n_nodes", "n_edges"])

list_of_completed_process_strings=[]
# df = parse_completed_processes(list_of_completed_process_strings)

for n in n_vals:
    # print('entered')
    for seed in seed_list:
        cmd = [
        "python3",
        str(ER_endpoint),
        "--n",str(n), 
        "--p", str(n_vals[n]),
        "--seed",str(seed) 
    ]

        # print(cmd)
        result = str(subprocess.run(cmd, capture_output=True, text=True, timeout=7200))
        # print(result[127:])
        # result = re.sub(pattern, '', result)
        # print(result)
        list_of_completed_process_strings.append(result)
        # print(list_of_completed_process_strings)

print(list_of_completed_process_strings)
df = parse_completed_processes(list_of_completed_process_strings)
df.to_csv('15_runs_per_size.csv', sep='\t')
# CompletedProcess(args=['python3', '/home/styx/Dissertation/Synthetic_Graph_Generator/modules/ER_model/ER_endpoint.py', '--n', '100', '--p', '3', '--seed', '0'], returncode=0, stdout='{\n    "nodes": [\n        0\n    ],\n    "edges": [\n        0\n    ],\n    "metadata": {\n        "model": "erdos_renyi",\n        "n_nodes": 100,\n        "n_edges": 4950,\n        "directed": false,\n        "parameters": {\n            "n": 100,\n            "p": 3.0,\n            "seed": 0\n        }\n    }\n}\n', stderr='')








