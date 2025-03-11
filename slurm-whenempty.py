import os
import json
import re
import time
import subprocess

cmd = ["squeue", "--json"]
ret = subprocess.run(cmd, check=True, capture_output=True, text=True)
jobs = json.loads(ret.stdout)

node_fin_table = {}

def expand_noderange(noderange: str):
    pattern = re.compile(r'([^,\[]*?)\[(.*?)\]')
    matches = pattern.findall(noderange)
    
    if not matches:
        return [noderange]  # Return as-is if no brackets found
    
    expanded_nodes = []
    for prefix, range_part in matches:
        ranges = range_part.split(',')
        expanded_parts = []
        
        for r in ranges:
            if '-' in r:
                start, end = r.split('-')
                width = len(start)  # Preserve leading zeros
                expanded_parts.extend([f"{prefix}{str(i).zfill(width)}" for i in range(int(start), int(end) + 1)])
            else:
                expanded_parts.append(f"{prefix}{r}")
        
        expanded_nodes.extend(expanded_parts)
    
    return expanded_nodes

for job in jobs["jobs"]:
    if job["nodes"]:
      nodes = expand_noderange(job["nodes"])
      end_time = job["end_time"]["number"]
      for node in nodes: 
        if len(node) < 2 and len(node) > 0:
          print(f"hmmm {node}")
        if node not in node_fin_table or end_time > node_fin_table[node]:
          node_fin_table[node] = end_time

results = dict(sorted(node_fin_table.items(), key=lambda item: item[1]))

print(f"{'Node':<20}{'Finishing time':<20}")
print("=" * 42)

for i in results:
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(results[i]))
    print(f"{i:<20} : {t:<20}")

