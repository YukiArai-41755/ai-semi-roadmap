#!/usr/bin/env python3
"""Correct the NAND omission: add NAND/enterprise-SSD and HBF nodes to L4.
NAND was wrongly classed as generic; 2026 data shows oligopoly + sold-out +
+234% pricing + structural AI inference demand. Idempotent."""
import json, os, copy
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=os.path.join(ROOT,"data","graph.json"); d=json.load(open(P)); orig=copy.deepcopy(d)

# rename L4-C to reflect it now holds the full non-HBM hierarchy incl. NAND
for L in d["layers"]:
    if L["id"]=="L4":
        for s in L["sub_systems"]:
            if s["id"]=="L4-C":
                s["name"]="メモリ階層拡張 (NAND/CXL)"
                s["desc"]="HBMの外側を埋める階層: HBF→SOCAMM→DDR5→エンタープライズSSD(NAND)→CXL。推論のKVキャッシュ/RAGがHBMからNANDへ溢れる構造変化の受け皿。"

d["nodes"]=[n for n in d["nodes"] if n["id"] not in ("nand","hbf")]

d["nodes"].append({
  "id":"nand","kind":"tech","layer":"L4","sub":"L4-C",
  "name":"NAND / エンタープライズSSD","full":"Enterprise SSD (QLC NAND) for AI Inference",
  "status":"active","lineage":"nand-storage",
  "maturity":5,"bottleneck":4,"investment":5,
  "players":["Samsung","SK hynix/Solidigm","Kioxia/SanDisk","Micron"],
  "alts":["hbf"],
  "milestones":{
    "now":"AI推論のKVキャッシュ/RAGインデックスがHBMからSSDへ溢れ、エンタープライズSSD需要が急増。NAND価格はQ1 2026 +85-90%QoQ、Gartner 2026通年+234%予想。Samsung/SK hynixがHBM優先でNANDウェハを削減し供給共食い。Kioxia 2026完売・利益48倍。QLC大容量化(122TB/245TB)。",
    "2027":"緩和は2027後半まで見込めず。512TB Gen6 SSD・PCIe6.0(Micron 9650は28GB/s)。KVキャッシュ向けSLC高DWPD SSD(Micron)。",
    "2030":"推論ストレージ階層がメモリ階層の正式な一段として定着(infer)。"
  },
  "def":"AI推論で需要が構造的に急増したフラッシュストレージ。長コンテキスト推論のKVキャッシュ/RAGがGPUのHBM容量を超え、その溢れをエンタープライズSSDが受ける。寡占(上位5社で約90%)かつ供給共食い(HBM転用)で完売・価格急騰。Kioxia/SanDiskの株価急騰はこの構造変化を市場が織り込んだもの——『ストレージ=汎用』は2023年的発想で、2026年のNANDはHBMに次ぐ第二の利益柱。",
  "materials":["die_nand"] if any(m['id']=='die_nand' for m in d['nodes']) else []
})

d["nodes"].append({
  "id":"hbf","kind":"tech","layer":"L4","sub":"L4-C",
  "name":"HBF (高帯域フラッシュ)","full":"High Bandwidth Flash",
  "status":"emerging","lineage":"nand-hbm-bridge",
  "maturity":1,"bottleneck":4,"investment":4,
  "players":["SanDisk","SK hynix(標準化協業)","Kioxia/NVIDIA(高IOPS SSD)"],
  "alts":["hbm4","nand"],
  "milestones":{
    "now":"SanDisk+SK hynixが標準化協業(2025/8)。NANDとHBMの速度差を橋渡しし、HBMの容量制約を一部肩代わり。HBFが推論標準になればSanDiskのTAM倍増の可能性。",
    "2027":"2026後半サンプル→2027にHBF採用の推論デバイス。Kioxia+NVIDIAの1億IOPS SSD(現行の40-50倍、GPU直結でHBM補完)も同方向。",
    "2030":"HBM/HBF/SSDの帯域-容量-コストの連続体が確立(spec)。"
  },
  "def":"HBM(高速・小容量・高価)とNAND(低速・大容量・安価)の中間を埋める新アーキテクチャ。HBMライクなスタック実装をNANDベースで行い、推論で必要な大容量を低コストで供給する。GPUに直結しHBM容量を実質拡張する構想で、L4メモリ階層に新たな段を加える構造変化。NAND勢(SanDisk/Kioxia)がHBM領域へ攻め上がる楔。",
  "materials":[]
})

MANAGED=set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label:e["label"]=label
    MANAGED.add((s,t,ty));return e
new=[
  mk("nand","L4-C","hier"), mk("hbf","L4-C","hier"),
  mk("hbf","hbm4","cross","HBMの容量を一部代替"),
  mk("hbf","nand","cross","NANDベースで高帯域化"),
  mk("nand","hbm4","cross","KVキャッシュがHBMから溢れる受け皿"),
  mk("nand","T-mem","cross"), mk("hbf","T-mem","cross"),
  mk("nand","cerebras","cross","推論ストレージ階層"),
  # supply cannibalization: HBM prioritization squeezes NAND
  mk("hbm4","nand","cross","HBM優先でNANDウェハ削減=供給共食い"),
]
def k(e):return (e["s"],e["t"],e["type"])
d["edges"]=[e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new)

# price/supply axes (researched)
for nid,(pr,ti,note,et) in {
  "nand":(4,5,"寡占(上位5社で約90%: Samsung/SK hynix+Solidigm/Kioxia+SanDisk/Micron)。Q1 2026 +85-90%QoQ、Gartner 2026 +234%、緩和2027後半。Kioxia 2026完売・利益48倍。HBM粗利には及ばないが供給共食いで逼迫は極端。","fact"),
  "hbf":(4,4,"SanDisk/SK hynix標準化、Kioxia/NVIDIA高IOPS。立上げ前で供給限定、推論標準化なら需要爆発。新規アーキで代替難。","spec"),
}.items():
    n=next(x for x in d['nodes'] if x['id']==nid)
    n['pricing'],n['tightness'],n['pricenote'],n['priceetag']=pr,ti,note,et

d["meta"]["version"]="1.7-nand"
out=json.dumps(d,ensure_ascii=False,indent=2);json.loads(out)
open(P,"w").write(out+"\n")
print(f"NAND+HBF added. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
