#!/usr/bin/env python3
"""Populate L2 製造プロセス・基盤 into graph.json. Idempotent. Final layer."""
import json, os, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "graph.json")
d = json.load(open(P))
orig = copy.deepcopy(d)

for L in d["layers"]:
    if L["id"] == "L2":
        L["status"] = "done"
        L["summary"] = ("トランジスタ微細化の最前線。FinFETからGAAナノシートへ、表面配線から裏面給電へと"
                        "二つの構造転換が同時進行。微細化単体の伸びは鈍化し、価値はパッケージ(L3)へ"
                        "移ったが、AI/HPC向けには裏面給電が新たな差別化軸に。TSMCはHigh-NA EUVを"
                        "2029年まで使わない方針——マスクスティッチングで凌ぐ。")
        L["sub_systems"] = [
            {"id": "L2-A", "name": "トランジスタ構造 (GAA)", "desc": "FinFET→ゲートオールアラウンド・ナノシート。N2が初のGAA。電流駆動力の改善。"},
            {"id": "L2-B", "name": "裏面給電 (BSPDN)", "desc": "電源網をウェハ裏面へ。TSMC SPR / Intel PowerVia。AI/HPCノードの差別化軸。"},
            {"id": "L2-C", "name": "リソグラフィ", "desc": "EUV / High-NA EUV / マスクスティッチング。TSMCは2029までHigh-NA不採用。"},
        ]

L2_IDS = {"gaa", "bspdn", "litho"}
d["nodes"] = [n for n in d["nodes"] if n["id"] not in L2_IDS]

L2_NODES = [
  {
    "id": "gaa", "kind": "tech", "layer": "L2", "sub": "L2-A",
    "name": "GAAナノシート", "full": "Gate-All-Around Nanosheet Transistor",
    "status": "active", "lineage": "transistor",
    "maturity": 4, "bottleneck": 3, "investment": 4,
    "players": ["TSMC(N2/A16/A14)", "Intel(18A)", "Samsung(SF2/SF1.4)", "Rapidus(2027)"],
    "alts": [],
    "milestones": {
      "now": "FinFETの後継。N2が初のGAAナノシートで高量産(2025, BSPDNなし)。ゲートがチャネルを全周で囲み短チャネル効果を抑制、電流駆動力を改善。N3比でSRAM密度+22%(主に周辺回路)。",
      "2027": "N2P/N2X/N2U派生。Samsung SF1.4は4ナノシート構造で電流駆動改善。",
      "2030": "A14(2nd gen nanosheet, 2028)→A13/A12(2029)。2Dチャネル材(カーボンナノチューブ/MoS2)が研究段階。"
    },
    "def": "FinFETに代わる次世代トランジスタ構造。ゲートがチャネルを全周で囲むことでリーク制御と電流駆動力を改善。微細化が鈍化する中での性能源泉だが、SRAM(キャッシュ)のスケーリングは頭打ち——メモリの壁の遠因。",
    "materials": []
  },
  {
    "id": "bspdn", "kind": "tech", "layer": "L2", "sub": "L2-B",
    "name": "裏面給電 (BSPDN)", "full": "Backside Power Delivery: TSMC Super Power Rail / Intel PowerVia",
    "status": "emerging", "lineage": "power-rail",
    "maturity": 3, "bottleneck": 4, "investment": 5,
    "players": ["TSMC(Super Power Rail)", "Intel(PowerVia)", "Samsung"],
    "alts": [],
    "milestones": {
      "now": "電源網をウェハ裏面に移し、表面を信号配線専用に解放。Intel PowerViaが18Aで先行(製造容易だがスケーリング益は小、密度は3nm級)。",
      "2027": "TSMC A16のSuper Power Rail(SPR)が量産(2027に後ろ倒し)。直接裏面コンタクトでnTSV不要、+8-10%速度/-20%電力。AI/HPC特化。",
      "2030": "A12(2029)へ拡張。AI/HPCノードはBSPDN必須、モバイルはコスト都合で非搭載——セグメント分岐。"
    },
    "def": "電源配線をチップ裏面へ移す構造転換。表面の混雑を解消し電力供給と信号配線を分離。AI/HPC向け大規模ダイで電力integrityを確保する差別化技術。GAAと並ぶL2の二大構造転換の一つで、微細化鈍化を補う。",
    "materials": []
  },
  {
    "id": "litho", "kind": "tech", "layer": "L2", "sub": "L2-C",
    "name": "リソグラフィ (EUV/High-NA)", "full": "EUV / High-NA EUV / Mask Stitching",
    "status": "active", "lineage": "lithography",
    "maturity": 4, "bottleneck": 4, "investment": 4,
    "players": ["ASML(独占)", "TSMC", "Intel(High-NA先行)", "Samsung"],
    "alts": [],
    "milestones": {
      "now": "EUV(0.33NA)で最大レチクル26×33mm(~858mm²)。これを超える大型ダイはマスクスティッチングで継ぐ(→L3 CoWoSのレチクル制約の根源)。",
      "2027": "Intelは14A(1.4nm)でASML High-NA EUVを推進。TSMCはHigh-NAのコスト見合わずA16/A14では不採用。",
      "2030": "TSMCはA12/A13(2029)までHigh-NA EUVを使わない方針——マスクスティッチングとDTCOで凌ぐ。High-NA採用是非が陣営を分ける。"
    },
    "def": "回路パターンを焼く露光技術。ASMLがEUVを独占。0.33NA EUVのレチクル上限(~858mm²)がAIの巨大ダイ・パッケージ(L3)の物理制約の根源。High-NA EUV採用是非でTSMC(慎重)とIntel(先行)の戦略が分かれる。",
    "materials": []
  },
]
d["nodes"].extend(L2_NODES)

MANAGED = set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label: e["label"]=label
    MANAGED.add((s,t,ty)); return e

new_edges = [
  mk("gaa","L2-A","hier"),
  mk("bspdn","L2-B","hier"),
  mk("litho","L2-C","hier"),
  # L2 -> L5 (process enables compute)
  mk("gaa","rubin","cross","N3でRubin製造"),
  mk("gaa","mi400","cross","N2でMI400製造(2nm先行)"),
  mk("bspdn","mi400","cross","AI/HPC向け裏面給電"),
  # L2 -> L4 (base die on logic node)
  mk("gaa","hbm-basedie","cross","HBMベースダイを先端ノードで製造"),
  # L2 -> L3 (reticle limit is root of packaging constraint)
  mk("litho","cowos","cross","レチクル上限がCoWoS大型化の制約根源"),
  mk("litho","glass-int","cross","マスクスティッチング代替としての大面積"),
  # SRAM scaling stall feeds memory wall
  mk("gaa","hbm4","cross","SRAM頭打ち→メモリ依存増"),
]

def k(e): return (e["s"],e["t"],e["type"])
d["edges"] = [e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new_edges)

d["meta"]["version"] = "1.0-all-layers"

out = json.dumps(d, ensure_ascii=False, indent=2)
json.loads(out)
open(P,"w").write(out + "\n")
print(f"L2 populated. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
print("All 7 layers now done:", all(L.get('status')=='done' for L in d['layers']))
