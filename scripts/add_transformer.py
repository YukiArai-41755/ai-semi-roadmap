#!/usr/bin/env python3
"""Round 4: HV transformer — the ultimate compute-rate-limiting-bias blind spot
(not even a semiconductor). 10% of DC cost, 100% of the bottleneck. Lead time
24-30mo -> 5yr. Half of 2026 US DC capacity slipping. Add to L1. Idempotent."""
import json, os, copy
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=os.path.join(ROOT,"data","graph.json"); d=json.load(open(P)); orig=copy.deepcopy(d)

d["nodes"]=[n for n in d["nodes"] if n["id"]!="transformer"]
d["nodes"].append({
  "id":"transformer","kind":"tech","layer":"L1","sub":"L1-C",
  "name":"高電圧変圧器・系統設備","full":"HV Transformers / Substations / Switchgear",
  "status":"active","lineage":"grid-infrastructure",
  "maturity":5,"bottleneck":5,"investment":4,
  "players":["TBEA/China XD(中国勢~60%)","Hitachi Energy","Siemens Energy","GE Vernova","Eaton"],
  "alts":["BYOP(自前発電でHV変圧器を回避)"],
  "milestones":{
    "now":"電気設備はDC総コストの10%未満だが、ボトルネックの100%。HV変圧器リードタイムは24-30ヶ月→5年に。系統接続キューは2,100GW超で総容量超過。2026年米DC計画の約半数が変圧器・開閉装置・電池不足で遅延/中止見込み、ホワイトハウスがDPA発動。中国勢が世界生産~60%・受注2027まで満杯。",
    "2027":"GSU変圧器需要は2019比+274%。BYOP(bring-your-own-power)で系統を迂回しオンサイト発電する動きが加速。固体トランス(Enphase等)2028量産。",
    "2030":"系統近代化が追いつくか、自前発電が常態化するか(spec)。電力可用性がAI拡大の真の上限。"
  },
  "def":"AIデータセンターを建てられるかを最終的に決める物理ボトルネック。半導体ですらない高電圧変圧器・変電所・開閉装置が、5年のリードタイムと系統接続キューでGPU出荷に追いつかない。『Nvidiaは出荷しているのにDCが建たない』の正体。演算律速バイアスの究極の盲点——最も地味な川上が、最も効く制約。投資は電力インフラ・自前発電(BYOP)へ波及する。",
  "materials":["m-gansic"],
  "pricing":3,"tightness":5,
  "pricenote":"HV変圧器リードタイム5年・系統キュー2,100GW超。中国勢~60%で価格は競争的だが供給逼迫は極端。電気設備はDCコストの10%未満だがボトルネックの100%。緩和は数年先。",
  "priceetag":"fact"
})

MANAGED=set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label:e["label"]=label
    MANAGED.add((s,t,ty));return e
new=[
  mk("transformer","L1-C","hier"),
  mk("transformer","power-supply","cross","系統設備の物理律速"),
  mk("transformer","hvdc","cross","給電チェーンの最上流"),
  mk("transformer","m-gansic","comp"),
  mk("transformer","T-power","cross"),
]
def k(e):return (e["s"],e["t"],e["type"])
d["edges"]=[e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new)

d["meta"]["version"]="2.0-transformer"
out=json.dumps(d,ensure_ascii=False,indent=2);json.loads(out)
open(P,"w").write(out+"\n")
print(f"transformer added. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
