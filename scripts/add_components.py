#!/usr/bin/env python3
"""Add component/material nodes to thin layers (L1/L2/L6/L7) and register
material_legend entries where needed. Idempotent."""
import json, os, copy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "graph.json")
d = json.load(open(P)); orig=copy.deepcopy(d)

NEW_MATERIALS = [
  {"id":"m-gansic","kind":"material","name":"GaN/SiC パワー半導体","full":"Gallium Nitride / Silicon Carbide Power Devices",
   "role":"電力変換素子","etype":"電源部品",
   "props":{"特徴":"ワイドバンドギャップ。高耐圧・高速スイッチング・低損失","用途":"800V HVDC変換、PSU、DC-DC"},
   "suppliers":["Infineon","Navitas","ROHM","STMicroelectronics","TI"],
   "alts":["Si(従来)"],
   "def":"シリコンより広いバンドギャップを持つ半導体。高電圧・高温・高速スイッチングに強く、800V HVDC給電の高効率・高密度変換を可能にする鍵部材。L1電力アーキの中核。"},
  {"id":"m-vrm","kind":"material","name":"電源IC / VRM","full":"Voltage Regulator Module / Power Management IC",
   "role":"電圧変換・安定化","etype":"電源部品",
   "props":{"機能":"高電圧をチップ要求電圧(〜0.7V)へ多段変換","配置":"ダイ近接(垂直給電)へ移行"},
   "suppliers":["Infineon","MPS","Renesas","TI","Vicor"],
   "alts":[],
   "def":"電源電圧をGPU/CPUが要求する低電圧へ変換・安定化する回路。大電流化で損失低減のためダイ直下の垂直給電へ。L1とL5/L3を電気的に繋ぐ。"},
  {"id":"m-optengine","kind":"material","name":"光エンジン / シリコンフォトニクス","full":"Optical Engine / Silicon Photonics",
   "role":"電気↔光変換","etype":"光部品",
   "props":{"構成":"変調器・受光器・レーザ(外部/統合)・導波路","実装":"スイッチ/演算ダイ近接に共パッケージ"},
   "suppliers":["Broadcom","NVIDIA","Marvell","TSMC(COUPE)","Coherent","Lumentum(光源)"],
   "alts":["銅SerDes(電気)"],
   "def":"電気信号を光に変換する部品群。CPO(共パッケージ光)の心臓で、変調器・受光器・レーザ・導波路から成る。銅の距離・損失・電力限界を超える。L6/L7とガラスインターポーザ(L3)に直結。"},
  {"id":"m-euvmask","kind":"material","name":"EUVマスク / フォトマスク","full":"EUV Photomask / Reticle",
   "role":"露光原版","etype":"製造部材",
   "props":{"特徴":"反射型(EUVは吸収されるため)。ペリクル保護が難題","レチクル上限":"26×33mm(~858mm²)"},
   "suppliers":["TSMC(内製)","Toppan","DNP","Hoya(ブランクス)","AGC"],
   "alts":[],
   "def":"回路パターンの原版。EUVでは反射型マスクを使う。1枚のマスクで焼ける最大面積(レチクル上限~858mm²)が、AIの巨大ダイ・CoWoS大型化(L3)の物理制約の根源。マスクスティッチングで継ぐ。"},
  {"id":"m-cdu","kind":"material","name":"CDU / 冷却分配","full":"Coolant Distribution Unit",
   "role":"冷却液循環・分配","etype":"冷却部品",
   "props":{"機能":"液冷ループの熱交換・流量制御","形態":"in-row / in-rack / sidecar"},
   "suppliers":["Vertiv","Boyd","nVent","Accelsius","Trane(Stellar)"],
   "alts":["空冷(限界)"],
   "def":"液冷システムで冷却液を循環・分配し施設水と熱交換する装置。Direct-to-Chip液冷の中核設備。高密度ラックの除熱を担い、L1冷却の投資が集中する部材。"},
]

# de-dup add to nodes
mat_ids={m["id"] for m in NEW_MATERIALS}
d["nodes"]=[n for n in d["nodes"] if n["id"] not in mat_ids]
d["nodes"].extend(NEW_MATERIALS)

# legend entries (for swatches in figures/cards)
LEG_ADD={
  "gansic":{"label":"GaN/SiC","color":"#4a9e6b","hatch":"solid"},
  "optengine":{"label":"光エンジン","color":"#00d9ff","hatch":"lines"},
}
for k,v in LEG_ADD.items(): d["material_legend"][k]=v

# edges: connect components to their tech nodes
MANAGED=set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label:e["label"]=label
    MANAGED.add((s,t,ty));return e
new=[
  mk("hvdc","m-gansic","comp"), mk("hvdc","m-vrm","comp"),
  mk("liquid-cooling","m-cdu","comp"),
  mk("cpo","m-optengine","comp"),
  mk("switch-silicon","m-optengine","comp"),
  mk("litho","m-euvmask","comp"),
  mk("m-gansic","T-power","cross"),
  mk("m-optengine","T-optical","cross"),
  mk("m-euvmask","cowos","cross","レチクル上限の根源"),
]
def k(e):return (e["s"],e["t"],e["type"])
d["edges"]=[e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new)

d["meta"]["version"]="1.3-components"
out=json.dumps(d,ensure_ascii=False,indent=2);json.loads(out)
open(P,"w").write(out+"\n")
print(f"components added. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}, legend {len(d['material_legend'])}")
