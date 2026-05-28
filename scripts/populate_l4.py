#!/usr/bin/env python3
"""Populate L4 メモリ into graph.json. Idempotent. Writes only if JSON validates.
Promotes the hbm4 stub to a full node so L5 cross-edges (rubin/mi400 -> hbm4)
auto-resolve to a real card."""
import json, os, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "graph.json")
d = json.load(open(P))
orig = copy.deepcopy(d)

# ---- 1. upgrade L4 layer entry ----
for L in d["layers"]:
    if L["id"] == "L4":
        L["status"] = "done"
        L["summary"] = ("AIスケーリングの真の律速=メモリの壁。HBM4で帯域は跳ねるが、性能を決めるのは"
                        "16-Hiスタックの歩留りとベースロジックダイの統合度。HBMは受動的な記憶素子から"
                        "ロジックを抱えた共プロセッサへ変質しつつある。供給はSK hynix/Samsung/Micronの"
                        "三寡占とTSMC(ベースダイ)に集中——構造的チョークポイント。")
        L["sub_systems"] = [
            {"id": "L4-A", "name": "HBM主系 (スタック)", "desc": "広帯域メモリ本体。HBM4 / 16-Hi / 次世代HBM4E。帯域・容量・歩留りの競争。"},
            {"id": "L4-B", "name": "ベースダイ・カスタムHBM", "desc": "スタック最下層のロジックダイ。TSMC等の先端ノードで製造し、HBMを共プロセッサ化。C-HBM4Eで差別化軸に。"},
            {"id": "L4-C", "name": "メモリ階層拡張 (CXL)", "desc": "単一GPUの物理境界を超えるラック規模のメモリプーリング。メモリ中心アーキの中核。"},
        ]

# ---- 2/3. manage L4 content nodes ----
L4_NODE_IDS = {"hbm4", "hbm4e", "hbm-basedie", "cxl"}
d["nodes"] = [n for n in d["nodes"] if n["id"] not in L4_NODE_IDS]

L4_NODES = [
  {
    "id": "hbm4", "kind": "tech", "layer": "L4", "sub": "L4-A",
    "name": "HBM4", "full": "High Bandwidth Memory 4 (JEDEC 6th gen)",
    "status": "emerging", "lineage": "hbm-stack",
    "maturity": 3, "bottleneck": 5, "investment": 5,
    "players": ["SK hynix(>50%シェア)", "Samsung", "Micron", "TSMC(ベースダイ)"],
    "alts": ["hbm4e"],
    "milestones": {
      "now": "CES2026で各社16-Hi公開。インタフェース2048bit(HBM3eの2倍)・32ch。JEDEC基準2.0TB/s @8Gbpsだが、NVIDIAがピン速度>11Gbpsを要求し全社再サンプル→量産は1Q26末以降に後ろ倒し。SK hynix 16-Hi 48GB @11.7Gbps(MR-MUF)、MP Q3 2026。Micron 2.8TB/s・最高効率・2026分は完売。",
      "2027": "16-Hi歩留りが本格律速。20層ロードマップでハイブリッドボンディングへ移行(SK hynix)。",
      "2030": "HBM4E/HBM5世代でハイブリッドボンディングが業界標準化(spec)。"
    },
    "def": "第6世代広帯域メモリ。インタフェース幅倍増(2048bit)で1スタック2.0TB/s超。単なる速度向上でなくロジックベースダイを統合する設計思想の転換。性能の真の律速はもはや演算でなくHBM帯域と16-Hi歩留り——AIスケーリングのメモリの壁。",
    "materials": ["die_dram", "tsv", "hbond", "die_logic"]
  },
  {
    "id": "hbm-basedie", "kind": "tech", "layer": "L4", "sub": "L4-B",
    "name": "HBMベースダイ / カスタムHBM", "full": "HBM Logic Base Die / C-HBM4E",
    "status": "emerging", "lineage": "memory-logic-integration",
    "maturity": 2, "bottleneck": 4, "investment": 5,
    "players": ["TSMC(製造)", "SK hynix", "Micron", "GUC/世芯(PHY IP)", "NVIDIA(co-design)"],
    "alts": [],
    "milestones": {
      "now": "HBM4ベースダイをTSMC 12FFC/N5等の先端ロジックノードで製造。PHY/コントローラが大型化(15mm² vs HBM3e 11mm²)。電圧0.8V(HBM3e 1.1V)で2倍の電力効率。",
      "2027": "C-HBM4E: 顧客仕様カスタムベースダイがN3Pへ。電圧0.75V・面積効率2.5倍。Vera Rubin Ultra向け。SK hynix/Micron共にTSMCでベースダイ製造。",
      "2030": "カスタムHBM市場が本格立ち上がり。メモリとロジックの境界が溶解(spec)。"
    },
    "def": "HBMスタック最下層のロジックダイ。HBM4でDRAMプロセスでなくTSMC等の先端ロジックノードで製造され、HBMを「受動的記憶」から「能動的共プロセッサ」へ変える。C-HBM4Eで顧客がメモリロジックをファウンドリと共設計——L2(プロセス)・L5(GPU)とL4を結ぶ結節点。",
    "materials": ["die_logic", "hbond"]
  },
  {
    "id": "hbm4e", "kind": "tech", "layer": "L4", "sub": "L4-A",
    "name": "HBM4E (拡張)", "full": "HBM4 Extended",
    "status": "research", "lineage": "hbm-stack",
    "maturity": 1, "bottleneck": 4, "investment": 4,
    "players": ["SK hynix", "Samsung", "Micron", "TSMC"],
    "alts": ["hbm4"],
    "milestones": {
      "now": "次世代。カスタムベースダイ(C-HBM4E)で差別化。データ転送最大12.8GT/s目標。",
      "2027": "Vera Rubin Ultra世代向け。16-Hi HBM4Eへ。Samsungはハイブリッドボンディングで16層HBM4Eを2028目標。",
      "2030": "ハイブリッドボンディング標準化・20層級へ(spec)。"
    },
    "def": "HBM4の拡張版。最大の特徴はカスタマイズ可能なベースダイ(C-HBM4E)で、顧客固有のインタフェース・回路を3nm級ロジックで実装可能。メモリの差別化軸が「容量・帯域」から「ロジック統合度」へ移る。",
    "materials": ["die_dram", "tsv", "hbond", "die_logic"]
  },
  {
    "id": "cxl", "kind": "tech", "layer": "L4", "sub": "L4-C",
    "name": "CXL メモリプーリング", "full": "Compute Express Link / Memory Pooling",
    "status": "emerging", "lineage": "memory-tier-expansion",
    "maturity": 3, "bottleneck": 3, "investment": 3,
    "players": ["Intel", "AMD", "Samsung", "SK hynix", "Marvell", "CXL Consortium"],
    "alts": [],
    "milestones": {
      "now": "ラック規模でメモリをプール化し、単一GPUの物理境界を超える。長コンテキスト推論のKVキャッシュ拡張に有効。",
      "2027": "メモリ中心アーキの中核として普及。HBM(近接・高帯域)とCXL(遠隔・大容量)の階層化。",
      "2030": "ラック=1台の計算機のメモリ基盤(spec)。"
    },
    "def": "CPU・GPU・メモリをコヒーレントに接続しメモリをプール共有する規格。HBMの容量制約を補い、ラック全体で「記憶」を共有することでメモリの壁をシステムレベルで緩和。メモリ中心アーキテクチャ・システム統合トレンドの交差点。",
    "materials": []
  },
]
d["nodes"].extend(L4_NODES)

# ---- 4. manage L4 edges ----
MANAGED = set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label: e["label"]=label
    MANAGED.add((s,t,ty)); return e

new_edges = [
  # hierarchy
  mk("hbm4","L4-A","hier"),
  mk("hbm4e","L4-A","hier"),
  mk("hbm-basedie","L4-B","hier"),
  mk("cxl","L4-C","hier"),
  # generational succession
  mk("hbm4e","hbm4","time","次世代(カスタムベースダイで拡張)"),
  # L4 internal: base die is part of the stack
  mk("hbm4","hbm-basedie","cross","ベースダイを最下層に統合"),
  mk("hbm4e","hbm-basedie","cross","カスタムベースダイ(C-HBM4E)"),
  # L4 -> L3 packaging (hybrid bonding migration)
  mk("hbm4","m-hbond","cross","20層世代でHB移行"),
  mk("hbm4","m-tsv","comp"),
  # L4 -> L2 process (base die on logic node) — L2 stub target ok (renders as layer link)
  mk("hbm-basedie","L2","cross","ベースダイを先端ロジックノードで製造"),
  # trend crossings
  mk("hbm4","T-mem","cross"),
  mk("cxl","T-mem","cross"),
  mk("cxl","T-sys","cross"),
  mk("hbm-basedie","T-mem","cross"),
]

# Drop superseded stub-era edge label and our managed sigs to avoid dups.
def k(e): return (e["s"],e["t"],e["type"])
d["edges"] = [e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new_edges)

d["meta"]["version"] = "0.3-L3L4L5"

out = json.dumps(d, ensure_ascii=False, indent=2)
json.loads(out)
open(P,"w").write(out + "\n")
print(f"L4 populated. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
print("hbm4 is now a full node:", not any(n['id']=='hbm4' and n.get('stub') for n in d['nodes']))
