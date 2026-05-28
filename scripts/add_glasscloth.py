#!/usr/bin/env python3
"""Round 3: T-glass (low-CTE glass cloth) was completely missing — a NAND-class
oversight. Nittobo ~90% monopoly, +20% then +20-30%, courted by Apple/NVIDIA/
Google directly, relief not until H2 2027. Add it + HVLP copper foil note.
Strengthen m-hbond (round 2). Idempotent."""
import json, os, copy
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=os.path.join(ROOT,"data","graph.json"); d=json.load(open(P)); orig=copy.deepcopy(d)

# --- round 2: strengthen hybrid bonding equipment angle ---
hb=next(x for x in d['nodes'] if x['id']=='m-hbond')
hb['pricing'],hb['tightness']=4,4
hb['pricenote']=("ハイブリッドボンディング装置はBESI/AMAT(Kinex共同開発)が寡占、ASMLも参入検討。BESIのbacklogは前年比+105%。次世代AIは9倍パッケージ・600倍シリコン面積・400+ダイ・100万I/O/mm²で精度<50nm要求。SoIC/HBM積層を律速する装置側のボトルネック。")
hb['priceetag']='fact'

# --- round 3: T-glass node ---
d["nodes"]=[n for n in d["nodes"] if n["id"] not in ("m-glasscloth","m-copperfoil")]
d["nodes"].append({
  "id":"m-glasscloth","kind":"material","name":"T-glass / ガラスクロス","full":"Low-CTE Glass Cloth (T-glass / NE-glass)",
  "role":"基板補強・寸法安定","etype":"基板素材","layer":"L3",
  "props":{"役割":"CCLの補強繊維(コスト比19%)。低CTEで大型・高発熱パッケージの平坦性を保つ","逼迫":"AI大型基板で層数倍増・コア層でT-glass倍増","代替難":"極薄・無欠陥で一度織り込むと交換不可"},
  "suppliers":["Nittobo(日東紡, T-glass ~90%/NE-glass 60-70%)","AGC","Nan Ya(提携)","旭化成/台湾硝子(代替Low-Dk)"],
  "alts":["Q-glass(石英, 試作段階・高価・加工難)"],
  "def":"IC基板の有機コアに織り込む低CTEガラス繊維布。AIプロセッサが大型・高発熱化するほど平坦性維持に不可欠で、CCL(銅箔/樹脂/ガラスクロス)の補強材。Nittoboがほぼ独占し、Apple/NVIDIA/Google/Amazonが直接供給交渉に動くほどの逼迫=2026年AI最大級のボトルネックの一つ。緩和は2027後半。演算もしない地味な素材だが独占×完売の純度はABFフィルム級——基板の『素材の素材』。"
})
d["nodes"].append({
  "id":"m-copperfoil","kind":"material","name":"HVLP銅箔","full":"Hyper Very Low Profile Copper Foil",
  "role":"高速信号導体","etype":"基板素材","layer":"L3",
  "props":{"役割":"CCLの導体層(コスト比42%)。低粗度で224G+の高速信号損失を抑える","逼迫":"GB200/300超薄箔は2026まで予約満杯"},
  "suppliers":["三井金属","福田金属","古河電工","Circuit Foil"],
  "alts":[],
  "def":"CCLの導体となる極低粗度の銅箔。224G/400Gbpsの高速信号で表面粗さが損失を決めるためHVLP級が要る。AIサーバ基板はRF部品的な振る舞いを要求され、銅箔も性能を律速する素材になった。供給は2026まで逼迫。"
})

MANAGED=set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label:e["label"]=label
    MANAGED.add((s,t,ty));return e
new=[
  mk("m-glasscloth","m-ccl","comp","CCLの補強繊維(19%)"),
  mk("m-copperfoil","m-ccl","comp","CCLの導体層(42%)"),
  mk("m-glasscloth","org-sub","comp"),
  mk("m-glasscloth","T-glass","cross"),  # links to the glass-trend axis if exists
  mk("m-glasscloth","cowos","cross","大型基板の平坦性を律速"),
]
# drop the T-glass cross if trend id doesn't exist
trend_ids={t['id'] for t in d.get('trends',[])}
new=[e for e in new if not (e['t']=='T-glass' and 'T-glass' not in trend_ids and 'T-glass' not in {n['id'] for n in d['nodes']})]
def k(e):return (e["s"],e["t"],e["type"])
d["edges"]=[e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new)

# price axes for new
for nid,(p,t,note,et) in {
  "m-glasscloth":(5,5,"Nittobo T-glass ~90%独占。2025/8 +20%、2026/4 +20-30%。Apple/NVIDIA/Google/Amazonが直接交渉。緩和2027後半。CCLコストの19%だが代替不能で独占純度はABFフィルム級。","fact"),
  "m-copperfoil":(3,4,"HVLP銅箔(三井金属等)。CCLコストの42%。GB200/300超薄箔は2026まで予約満杯だが、ガラスクロスより供給者は多い。","fact"),
}.items():
    n=next(x for x in d['nodes'] if x['id']==nid)
    n['pricing'],n['tightness'],n['pricenote'],n['priceetag']=p,t,note,et

d["meta"]["version"]="1.9-glasscloth"
out=json.dumps(d,ensure_ascii=False,indent=2);json.loads(out)
open(P,"w").write(out+"\n")
print(f"T-glass+copper foil added, hbond strengthened. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
