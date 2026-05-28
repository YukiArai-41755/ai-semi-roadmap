#!/usr/bin/env python3
"""Populate L1 施設・電力・冷却 into graph.json. Idempotent."""
import json, os, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "graph.json")
d = json.load(open(P))
orig = copy.deepcopy(d)

for L in d["layers"]:
    if L["id"] == "L1":
        L["status"] = "done"
        L["summary"] = ("AIスケーリングの最終律速=電力と熱。ラック電力はH100 40kW→GB200 120kW→"
                        "Rubin Ultra 600kW-1MW(2027)と3年で25倍。800V HVDC給電と液冷が標準の組合せになり、"
                        "さらに電力供給そのもの(系統接続・SMR・BESS)が新たなボトルネック。"
                        "「チップをどう作るか」から「どう電気を確保するか」へ問いが移る。")
        L["sub_systems"] = [
            {"id": "L1-A", "name": "給電アーキテクチャ (800V HVDC)", "desc": "54V AC→800V HVDC。変換段削減・銅45%減・効率92%+。Rubin Ultra Kyberで本格化。"},
            {"id": "L1-B", "name": "冷却 (液冷→埋込)", "desc": "空冷→Direct-to-Chip液冷→マイクロ流体/埋込→二相液浸。熱流束500W/cm²へ。"},
            {"id": "L1-C", "name": "電力供給・系統", "desc": "系統接続待ち→ビハインドザメーター・SMR/原子力・BESS・ソフト定義電力。ギガワット級の確保競争。"},
        ]

L1_IDS = {"hvdc", "liquid-cooling", "power-supply"}
d["nodes"] = [n for n in d["nodes"] if n["id"] not in L1_IDS]

L1_NODES = [
  {
    "id": "hvdc", "kind": "tech", "layer": "L1", "sub": "L1-A",
    "name": "800V HVDC給電", "full": "800V High-Voltage DC Power Architecture",
    "status": "emerging", "lineage": "power-delivery",
    "maturity": 3, "bottleneck": 5, "investment": 5,
    "players": ["NVIDIA", "Infineon", "TI", "Vertiv", "ABB", "Eaton", "Delta", "Navitas/ROHM/STM(GaN/SiC)"],
    "alts": [],
    "milestones": {
      "now": "GTC2025で800V HVDC発表。54V ACの多段変換を廃しグリッド→チップを再構築。UPS/PDU削減、銅45%減、効率83%→92%+、TCO約30%減。GaN/SiCワイドバンドギャップ素子が鍵。実証2025/量産2026。",
      "2027": "Rubin Ultra Kyberで600kW-1MWラックを成立させる本命給電として大量展開。ただしハイパースケーラ毎に仕様分岐(Meta 600-800kW / Google 900kW-1.1MW / Amazon ±400V/800kW、NVIDIAは単極800V/660kW)。",
      "2030": "ギガワット級AIファクトリの標準給電(spec)。"
    },
    "def": "高電流・低電圧(54V)の多段変換による損失を、800V高電圧直流で解消する給電アーキの全面再構築。2300W級TDPチップと600kWラックを物理的に可能にする「イネーブラ」。液冷との協調設計が競争差別化点。",
    "materials": []
  },
  {
    "id": "liquid-cooling", "kind": "tech", "layer": "L1", "sub": "L1-B",
    "name": "液冷・先進冷却", "full": "Direct-to-Chip / Immersion / Embedded Cooling",
    "status": "active", "lineage": "thermal",
    "maturity": 4, "bottleneck": 5, "investment": 5,
    "players": ["Vertiv", "Boyd/Eaton", "nVent", "Accelsius(二相DTC)", "Microsoft+Corintis(マイクロ流体)", "TSMC(直接シリコン冷却)"],
    "alts": [],
    "milestones": {
      "now": "Direct-to-Chip液冷が>100kWラックの標準(負圧ループで漏洩リスク低減、CDU経由)。二相DTCも商用化(Accelsius 150kW)。空冷は限界。",
      "2027": "マイクロ流体/埋込冷却(Microsoft-Corintisの葉脈状マイクロチャネル、TSMC直接シリコン冷却SiCP)で100+W/cm²のホットスポットに対応。HP/NVIDIAがドロップイン化(2026-2028)。",
      "2030": "二相液浸(500W/cm², PUE~1.02)が最高密度向けに。埋込冷却が標準化(spec)。"
    },
    "def": "高TDP化で空冷が破綻し、液冷が必須化。Direct-to-Chip(冷却液をコールドプレートでチップ直近へ)→マイクロ流体/埋込(ダイ/基板内にチャネル)→二相液浸(誘電性流体の相変化)と高密度化。800V HVDCと対で設計される。L3のTIM/IHSと物理的に連続。",
    "materials": ["m-tim", "m-ihs"]
  },
  {
    "id": "power-supply", "kind": "tech", "layer": "L1", "sub": "L1-C",
    "name": "電力供給・系統", "full": "Power Availability: Grid / SMR / BESS / Software-Defined Power",
    "status": "emerging", "lineage": "energy-supply",
    "maturity": 2, "bottleneck": 5, "investment": 5,
    "players": ["ハイパースケーラ各社", "SMR各社", "電力系統事業者", "BESS事業者"],
    "alts": [],
    "milestones": {
      "now": "電力確保が新たなゴールドラッシュ。系統接続キューが数年に伸び、ビハインドザメーター発電へ。ソフト定義電力(BESS+負荷制御で電力インフラをオーバーサブスクライブ)。",
      "2027": "SMR(小型モジュール炉)のカーボンフリー基荷電源としての計画・規制枠組みが具体化(全面展開は2026以降に遅延)。再エネ+蓄電+マイクログリッドの混成。",
      "2030": "原子力含む専用電源がギガワット級AIファクトリを支える(spec)。"
    },
    "def": "演算でなく「電気そのもの」がAIスケーリングの最終律速。系統接続の遅延でビハインドザメーター発電・SMR・BESS・ソフト定義電力が焦点に。データセンターの立地と規模を電力可用性が決める構造変化。地域の電力・水資源への懸念でプロジェクト遅延も。",
    "materials": []
  },
]
d["nodes"].extend(L1_NODES)

MANAGED = set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label: e["label"]=label
    MANAGED.add((s,t,ty)); return e

new_edges = [
  mk("hvdc","L1-A","hier"),
  mk("liquid-cooling","L1-B","hier"),
  mk("power-supply","L1-C","hier"),
  # within-layer: HVDC + liquid cooling co-designed
  mk("hvdc","liquid-cooling","cross","800V+液冷は対の標準組合せ"),
  # L1 -> L5 (power/cooling enable compute density)
  mk("hvdc","rubin","cross","600kW級ラックを給電"),
  mk("liquid-cooling","rubin","cross","高TDPダイを冷却"),
  # L1 -> L6 (rack density enables copper scale-up reach)
  mk("hvdc","nvlink","cross","高密度=銅scale-up到達距離を確保"),
  # L1 -> L3 (cooling continuous with TIM/IHS)
  mk("liquid-cooling","m-tim","comp"),
  mk("liquid-cooling","m-ihs","comp"),
  # trend crossings
  mk("hvdc","T-power","cross"),
  mk("liquid-cooling","T-power","cross"),
  mk("power-supply","T-power","cross"),
  mk("hvdc","T-sys","cross"),
]

def k(e): return (e["s"],e["t"],e["type"])
d["edges"] = [e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new_edges)

d["meta"]["version"] = "0.6-L1L3L4L5L6L7"

out = json.dumps(d, ensure_ascii=False, indent=2)
json.loads(out)
open(P,"w").write(out + "\n")
print(f"L1 populated. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
