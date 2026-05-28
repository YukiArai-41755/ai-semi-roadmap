#!/usr/bin/env python3
"""Round 5: EUV photoresist — oligopoly (JSR/TOK/Shin-Etsu/Fujifilm, top5 >50%,
Japan dominates high-end EUV). Real consumable rate-limiter for advanced nodes.
But: EUV reduces chemical volume/wafer vs multipatterning, so tightness < NAND/
T-glass. Pricing high (oligopoly, qualification moat). Idempotent."""
import json, os, copy
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=os.path.join(ROOT,"data","graph.json"); d=json.load(open(P)); orig=copy.deepcopy(d)

d["nodes"]=[n for n in d["nodes"] if n["id"]!="m-resist"]
d["nodes"].append({
  "id":"m-resist","kind":"material","name":"EUVフォトレジスト","full":"EUV / Metal-Oxide Photoresist",
  "role":"露光感光材","etype":"製造材料","layer":"L2",
  "props":{"役割":"EUV露光でパターンを転写する感光性化学材料","参入障壁":"R&D・顧客認定が極めて重い→寡占","注記":"EUVはマルチパターニング比で層数減→ウェハあたり消費量はむしろ減る"},
  "suppliers":["JSR(Inpria買収=メタルオキサイド)","東京応化(TOK)","信越化学","富士フイルム","Dongjin Semichem"],
  "alts":["DUVレジスト(成熟ノード)"],
  "def":"EUV露光で回路パターンを焼き付ける感光材。先端ノード(L2)の歩留りと解像度を左右する化学材料で、日本勢(JSR/TOK/信越/富士)が高端EUVを支配(上位5社で50%超)。認定の重さが参入障壁=寡占。ただしEUVは層数が減るためウェハあたり消費量は逆に減り、逼迫はNAND/T-glassほど極端でない——価格決定力は高いが量の逼迫は中程度、という珍しいプロファイル。",
  "pricing":4,"tightness":3,
  "pricenote":"JSR/TOK/信越/富士の寡占(上位5社>50%)、認定障壁で価格決定力高。ただしEUVは層数減でウェハあたり消費量が減り、量の逼迫はNAND/T-glassより緩い。価格決定力4×逼迫3。",
  "priceetag":"infer"
})

MANAGED=set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label:e["label"]=label
    MANAGED.add((s,t,ty));return e
new=[
  mk("m-resist","litho","comp","EUV露光の感光材"),
  mk("m-resist","gaa","cross","先端ノードの歩留りを左右"),
]
def k(e):return (e["s"],e["t"],e["type"])
d["edges"]=[e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new)

d["meta"]["version"]="2.1-resist"
out=json.dumps(d,ensure_ascii=False,indent=2);json.loads(out)
open(P,"w").write(out+"\n")
print(f"EUV resist added. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
