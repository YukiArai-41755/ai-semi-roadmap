#!/usr/bin/env python3
"""sync.py — rebuild the entire file group from data/graph.json.
Run after editing graph.json. Order matters: inline data first, then SVGs
(they read the legend), then pages (they read nodes), then cards/views/aux/index."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = os.path.join(ROOT, "scripts")

# 1. validate + regenerate inlined graph data (file:// fallback source)
data = open(os.path.join(ROOT, "data", "graph.json")).read()
json.loads(data)  # raises on malformed JSON
open(os.path.join(ROOT, "assets", "graph-data.js"), "w").write("window.__GRAPH__ = " + data + ";\n")
print("✓ graph-data.js synced from graph.json")

# 2. run generators in dependency order
for script in ["gen_svg.py", "gen_basics.py", "gen_components_ref.py", "gen_matrix.py", "gen_companies.py", "gen_l1.py", "gen_l2.py", "gen_l3.py", "gen_l4.py", "gen_l5.py", "gen_l6.py", "gen_l7.py", "gen_cards.py", "gen_views.py", "gen_aux.py", "gen_index.py"]:
    path = os.path.join(SC, script)
    if not os.path.exists(path):
        print(f"  (skip {script}: not present)"); continue
    r = subprocess.run([sys.executable, path], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"✗ {script} FAILED:\n{r.stderr}"); sys.exit(1)
    print(f"✓ {script}: {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else 'ok'}")

print("\nRebuild complete. Open index.html.")
