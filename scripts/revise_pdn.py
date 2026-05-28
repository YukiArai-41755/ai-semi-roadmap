#!/usr/bin/env python3
"""Add PDN (Power Delivery Network) as the organizing concept for power passives,
add the missing シャント抵抗 node, enrich MLCC with the decoupling hierarchy.
Adds L1-D sub-system. Idempotent."""
import json, os, copy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT,"data","graph.json")
d=json.load(open(P)); orig=copy.deepcopy(d)

# --- L1-D sub-system ---
for L in d["layers"]:
    if L["id"]=="L1":
        subs=L.setdefault("sub_systems",[])
        if not any(s["id"]=="L1-D" for s in subs):
            subs.append({"id":"L1-D","name":"PDN (チップレベル給電網)",
                "desc":"VRM→デカップリング→ダイへ低インピーダンスで電力を届ける網。数百〜数千Aを0.7Vで供給する受動部品群の階層。"})

# --- enrich MLCC: frequency-staged decoupling hierarchy ---
m=next(x for x in d["nodes"] if x["id"]=="m-mlcc")
m["def"]=("配線層でなく受動部品。AI GPUは0.7-0.8Vで数百〜数千A、ナノ秒で負荷急変するため、"
          "VRMが応答するまでの電流を肩代わりして電圧ドロップを防ぐ(デカップリング)。"
          "周波数帯ごとにバルク(低)→MLCC(中)→シリコン/埋込キャパシタ(高・ダイ直近)と階層化する。"
          "ダイ直下(LSC)に多数配置され、HBM/GPUダイと基板面積を奪い合う。")
m["props"]={"配置":"基板裏面(LSC)/ダイ直下/基板内埋込","役割":"中周波デカップリング",
            "課題":"DCバイアスで実効容量低下、リップル発熱∝I²·ESR","要点":"PDNインピーダンス<1mΩ@100MHz目標"}
m.setdefault("players",["Murata","TDK","Samsung Electro-Mechanics","Taiyo Yuden"])

# --- new node: shunt / current-sense (priority #6) ---
d["nodes"]=[n for n in d["nodes"] if n["id"]!="m-shunt"]
d["nodes"].append({
  "id":"m-shunt","kind":"material","name":"シャント抵抗 / 電流検出","full":"Metal-Plate Shunt / Current-Sense Resistor",
  "role":"大電流検出","etype":"電源部品","layer":"L1",
  "props":{"抵抗値":"数mΩ〜サブmΩ","用途":"VRM電流監視・過電流保護・テレメトリ","課題":"発熱∝I²R、温度係数"},
  "suppliers":["Vishay","Bourns","KOA","Rohm","TT Electronics"],
  "alts":["インダクタDCR検出(抵抗レス)"],
  "def":"GPU/VRMが流す数百〜数千Aを電圧降下で測る低抵抗器。電源制御ループの電流フィードバックと過電流保護、消費電力テレメトリに必須。大電流ゆえ自己発熱が課題で、金属板シャントが使われる。PDN制御の目"
})

# --- new concept node: PDN ---
d["nodes"]=[n for n in d["nodes"] if n["id"]!="pdn"]
d["nodes"].append({
  "id":"pdn","kind":"tech","layer":"L1","sub":"L1-D",
  "name":"PDN (電源供給網)","full":"Power Delivery Network",
  "status":"active","lineage":"power-integrity",
  "maturity":4,"bottleneck":5,"investment":4,
  "players":["Vicor","ADI","MPS","Infineon","Empower(埋込Siキャパ)","受動部品各社"],
  "alts":[],
  "milestones":{
    "now":"1000A級TDCのGPUは~3mF級のバイパス容量を要しPCB面積をほぼ占有。VRMをダイ直下に置く垂直給電(vertical power delivery)でPDN抵抗とループインダクタンスを削減。目標インピーダンス<1mΩ@100MHz。",
    "2027":"基板内埋込キャパシタ(ECAP)・シリコンキャパシタでダイ直近の高周波デカップリングを強化。チップレットの多レール給電。",
    "2030":"裏面給電(L2 BSPDN)と垂直給電の統合でPDNがダイ内部まで連続(spec)。"
  },
  "def":"VRMからダイまで電力を低インピーダンスで届ける網全体。AIで最大の電源integrity課題——ナノ秒の負荷急変(高di/dt)に対し、周波数階層化したデカップリング(バルク/MLCC/シリコンキャパシタ)と垂直給電で電圧を0.7Vに保つ。個々の受動部品(MLCC・シャント・パワーインダクタ・DrMOS)はこのPDNを構成する要素。L1電力とL3実装とL5負荷を電気的に結ぶ。",
  "materials":["m-mlcc","m-sicap","m-powerinductor","m-drmos","m-shunt","m-vrm"]
})

MANAGED=set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label:e["label"]=label
    MANAGED.add((s,t,ty));return e
new=[
  mk("pdn","L1-D","hier"),
  mk("m-shunt","pdn","comp"), mk("m-mlcc","pdn","comp"), mk("m-sicap","pdn","comp"),
  mk("m-powerinductor","pdn","comp"), mk("m-drmos","pdn","comp"), mk("m-vrm","pdn","comp"),
  mk("pdn","rubin","cross","数千Aを0.7Vで供給"),
  mk("pdn","bspdn","cross","裏面給電と垂直給電が連続"),
  mk("pdn","T-power","cross"),
  mk("m-shunt","T-power","cross"),
]
def k(e):return (e["s"],e["t"],e["type"])
d["edges"]=[e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new)

d["meta"]["version"]="1.4-pdn"
out=json.dumps(d,ensure_ascii=False,indent=2);json.loads(out)
open(P,"w").write(out+"\n")
print(f"PDN+shunt added. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
