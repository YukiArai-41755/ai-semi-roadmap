#!/usr/bin/env python3
"""Populate L5 演算チップ into graph.json. Idempotent: removes any prior L5
content nodes/edges it manages, then re-adds. Writes only if JSON validates."""
import json, os, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "graph.json")
d = json.load(open(P))
orig = copy.deepcopy(d)

# ---- 1. upgrade L5 layer entry ----
for L in d["layers"]:
    if L["id"] == "L5":
        L["status"] = "done"
        L["summary"] = ("AIアクセラレータ本体。GPU(NVIDIA/AMD)とハイ-パースケーラ独自ASICの三つ巴。"
                        "微細化(L2)・パッケージ(L3)・メモリ(L4)の全ボトルネックがここに集約し、"
                        "歩留り(CoWoS-L / 16-Hi HBM4)が出荷量と仕様を直接律速する。")
        L["sub_systems"] = [
            {"id": "L5-A", "name": "商用GPU", "desc": "汎用アクセラレータ。NVIDIA Rubin / AMD Instinct MI400系。CUDA等ソフト資産が競争軸。"},
            {"id": "L5-B", "name": "ハイパースケーラ独自ASIC", "desc": "Google TPU / AWS Trainium / Broadcom系。総体ではNVIDIAへの最大の脅威。"},
            {"id": "L5-C", "name": "CPU・スーパーチップ統合", "desc": "Vera等CPUとGPUをコヒーレント結合。システム統合トレンドの結節点。"},
        ]

# ---- 2/3. manage L5 content nodes ----
L5_NODE_IDS = {"rubin", "mi400", "hyperscaler-asic", "vera-cpu"}
d["nodes"] = [n for n in d["nodes"] if n["id"] not in L5_NODE_IDS]

L5_NODES = [
  {
    "id": "rubin", "kind": "tech", "layer": "L5", "sub": "L5-A",
    "name": "NVIDIA Rubin (R100)", "full": "Vera Rubin Platform / R100 GPU",
    "status": "emerging", "lineage": "commercial-gpu",
    "maturity": 3, "bottleneck": 5, "investment": 5,
    "players": ["NVIDIA", "TSMC(製造)", "SK hynix/Samsung/Micron(HBM4)"],
    "alts": ["mi400", "hyperscaler-asic"],
    "milestones": {
      "now": "GTC2026で詳細確定。TSMC N3(3nm)・4レチクルCoWoS-L・NVIDIA初のチップレット設計。288GB HBM4 / 22.2TB/s(AMD対抗で10%増速)/ 336億トランジスタ / FP4 50PFLOPS。量産2026前半、システムH2 2026(CoreWeave等先行)。",
      "2027": "Rubin Ultra(R200): 当初4ダイ設計→CoWoS-L歩留り問題でデュアルダイに縮小。16-Hi HBM4。",
      "2030": "後継世代。ガラス基板/インターポーザ採用でレチクル制約を緩和(spec)。"
    },
    "def": "NVIDIAの次世代AIアクセラレータ。初のチップレット(マルチダイ)GPU。性能の律速はもはや演算でなくHBM4帯域とCoWoS-L/HBM歩留り——16-Hi HBM4歩留り危機(<20%)でR100はピン速度を下げる仕様調整(spec-down)を実施。",
    "materials": ["die_logic", "ubump"]
  },
  {
    "id": "mi400", "kind": "tech", "layer": "L5", "sub": "L5-A",
    "name": "AMD Instinct MI400 (MI455X)", "full": "Instinct MI455X / MI430X (CDNA 5)",
    "status": "emerging", "lineage": "commercial-gpu",
    "maturity": 2, "bottleneck": 4, "investment": 4,
    "players": ["AMD", "TSMC(N2製造)", "OpenAI(6GW契約)", "Meta/OCP(Helios)"],
    "alts": ["rubin", "hyperscaler-asic"],
    "milestones": {
      "now": "CES2026公表。TSMC N2(2nm)——初の2nm GPUでRubin(N3)に対しプロセス先行。432GB HBM4 / 19.6TB/s(容量はRubinの1.5倍)。CoWoS-L 3.5D。FP4 40PFLOPS。Helios 72-GPUラック(31TB HBM4 / 1.4PB/s)。",
      "2027": "MI500(次世代compute/memory/interconnect)。",
      "2030": "—"
    },
    "def": "AMDの対NVIDIA本命。MI455X(学習/推論)とMI430X(HPC/主権AI, FP64)に分岐。戦略はFLOPで勝つのでなくFP4/FP8で並びメモリ容量とラック相互接続(UALink/UEC等オープン規格)で上回る。CUDA非互換のソフト移行が最大の障壁。",
    "materials": ["die_logic", "ubump"]
  },
  {
    "id": "hyperscaler-asic", "kind": "tech", "layer": "L5", "sub": "L5-B",
    "name": "ハイパースケーラ独自ASIC", "full": "Google TPU / AWS Trainium / Broadcom-design ASIC",
    "status": "active", "lineage": "custom-asic",
    "maturity": 4, "bottleneck": 3, "investment": 5,
    "players": ["Google(TPU)", "AWS(Trainium/Inferentia)", "Broadcom(設計)", "Marvell", "Meta(MTIA)", "Microsoft(Maia)"],
    "alts": ["rubin", "mi400"],
    "milestones": {
      "now": "総体としてNVIDIAへの最大の脅威(AMDより大きく速い成長)。自社ワークロード特化で電力性能比とTCOを最適化。Broadcomが設計受託の中核。",
      "2027": "推論需要(総支出の約2/3)が独自ASICに有利。CPO/UALink等オープン規格と親和。",
      "2030": "垂直統合ハイパースケーラが自社AIインフラの相当部分を内製化(spec)。"
    },
    "def": "クラウド大手が自社設計する専用アクセラレータ。汎用性を捨て特定ワークロードに最適化。NVIDIAのCUDA moatが効かない領域で、AIアクセラレータTAM(~$160B 2025→$200B+ 2026)の最速成長セグメント。",
    "materials": ["die_logic"]
  },
  {
    "id": "vera-cpu", "kind": "tech", "layer": "L5", "sub": "L5-C",
    "name": "CPU・スーパーチップ統合", "full": "NVIDIA Vera / AMD EPYC Venice + GPU coherent integration",
    "status": "emerging", "lineage": "cpu-superchip",
    "maturity": 3, "bottleneck": 3, "investment": 4,
    "players": ["NVIDIA(Vera)", "AMD(EPYC Venice, Zen6/N2)"],
    "alts": [],
    "milestones": {
      "now": "Vera Rubin Superchip = Vera CPU(88コア/176スレッド)×1 + Rubin GPU×2をNVLink-C2Cで結合、FP4 100PFLOPS。CPU-GPUコヒーレンスがメモリ中心アーキの鍵。",
      "2027": "EPYC Venice(Zen6, TSMC N2)等が追随。CXLプーリングと連携。",
      "2030": "—"
    },
    "def": "CPUとGPUを密結合し1つの計算ノードとして設計する潮流。システム統合アーキテクチャ・メモリ中心アーキテクチャの両トレンドが交差する結節点。",
    "materials": ["die_logic"]
  },
]
d["nodes"].extend(L5_NODES)

# ---- 4. manage L5 edges ----
def edge_key(e): return (e["s"], e["t"], e["type"])
# remove old edges touching rubin-as-stub cross and any prior L5-managed edges
MANAGED_EDGE_SIGS = set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label: e["label"]=label
    MANAGED_EDGE_SIGS.add((s,t,ty))
    return e

new_edges = [
  # hierarchy: L5 nodes -> sub-systems
  mk("rubin","L5-A","hier"),
  mk("mi400","L5-A","hier"),
  mk("hyperscaler-asic","L5-B","hier"),
  mk("vera-cpu","L5-C","hier"),
  # competition
  mk("mi400","rubin","cross","競合(N2 vs N3 / 容量 vs FLOP)"),
  mk("hyperscaler-asic","rubin","cross","最大の構造的脅威"),
  # L5 -> L3 packaging dependencies
  mk("rubin","cowos","cross","CoWoS-L採用 / 歩留りが律速"),
  mk("mi400","cowos","cross","CoWoS-L 3.5D採用"),
  mk("rubin","soic","cross","チップレット積層"),
  # L5 -> L4 memory
  mk("rubin","hbm4","cross","HBM4×8-12搭載"),
  mk("mi400","hbm4","cross","HBM4 432GB搭載"),
  # superchip composition
  mk("vera-cpu","rubin","comp","Vera Rubin Superchip"),
  # trend crossings
  mk("vera-cpu","T-sys","cross"),
  mk("vera-cpu","T-mem","cross"),
  mk("hyperscaler-asic","T-optical","cross"),
  mk("rubin","T-power","cross"),
]

# drop superseded stub-era cross edges that we now re-express, plus our managed sigs
DROP = {("cowos","rubin","cross"), ("glass-sub","rubin","cross")}
d["edges"] = [e for e in d["edges"]
              if edge_key(e) not in MANAGED_EDGE_SIGS and edge_key(e) not in DROP]
# re-add glass->rubin as a forward-looking time/cross (kept, meaningful)
d["edges"].append({"s":"glass-sub","t":"rubin","type":"cross","label":"次世代パッケージ採用候補"})
d["edges"].extend(new_edges)

# bump version
d["meta"]["version"] = "0.2-L3L5"

# ---- validate & write ----
out = json.dumps(d, ensure_ascii=False, indent=2)
json.loads(out)  # parse-check
open(P, "w").write(out + "\n")
print(f"L5 populated. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
