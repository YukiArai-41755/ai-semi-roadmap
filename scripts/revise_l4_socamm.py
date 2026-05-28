#!/usr/bin/env python3
"""Add SOCAMM2 / LPDDR memory-tier node to L4-C. Idempotent."""
import json, os, copy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "graph.json")
d = json.load(open(P)); orig=copy.deepcopy(d)

d["nodes"] = [n for n in d["nodes"] if n["id"] != "socamm"]
d["nodes"].append({
  "id": "socamm", "kind": "tech", "layer": "L4", "sub": "L4-C",
  "name": "SOCAMM2 / LPDDR", "full": "Small Outline Compression Attached Memory Module 2 (LPDDR5X)",
  "status": "emerging", "lineage": "memory-tier-expansion",
  "maturity": 3, "bottleneck": 3, "investment": 4,
  "players": ["NVIDIA(発案)", "SK hynix", "Samsung", "Micron", "JEDEC(JESD328)"],
  "alts": ["cxl"],
  "milestones": {
    "now": "CAMM2由来のLPDDR5Xモジュール。HBMより安価・低電力(RDIMM比1/3)で着脱可能。GB300はLPDDR5X 18TB/14.3TB/s。SOCAMM1はGB300 Cordeliaで熱問題により頓挫→従来LPDDRに戻した。",
    "2027": "SOCAMM2(JEDEC標準化、9600MT/s、スループット+40%、熱改善)がVera Rubinで採用。SK hynix 1cで量産。HBM/SOCAMM/DDR5/CXLの多層メモリ階層を形成。",
    "2030": "LPDDR6ベースへ(512GBモジュール)。CPU近接メモリの標準(spec)。"
  },
  "def": "HBM(GPU近接・最高帯域)とDDR5/CXL(大容量)の中間を埋めるLPDDRベースのモジュール型メモリ。DRAM消費電力がCPUを上回る現状で電力効率が競争軸。AIサーバのメモリ階層がHBM単層から多層構造へ移行する象徴。NVIDIA発案だがJEDEC標準化でマルチベンダ化。",
  "materials": ["die_dram"]
})

MANAGED=set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label:e["label"]=label
    MANAGED.add((s,t,ty));return e
new=[mk("socamm","L4-C","hier"),
     mk("socamm","cxl","cross","メモリ階層を補完"),
     mk("socamm","hbm4","cross","HBMの下位階層を担う"),
     mk("socamm","vera-cpu","cross","Vera CPU近接メモリ"),
     mk("socamm","T-mem","cross")]
def k(e):return (e["s"],e["t"],e["type"])
d["edges"]=[e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new)
d["meta"]["version"]="1.2-L4socamm"
out=json.dumps(d,ensure_ascii=False,indent=2);json.loads(out)
open(P,"w").write(out+"\n")
print(f"socamm added. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
