#!/usr/bin/env python3
"""Populate L7 スケールアウト・ネットワーク into graph.json. Idempotent."""
import json, os, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "graph.json")
d = json.load(open(P))
orig = copy.deepcopy(d)

for L in d["layers"]:
    if L["id"] == "L7":
        L["status"] = "done"
        L["summary"] = ("ラック・クラスタ間を結ぶ後方ネットワーク。10万XPU超のクラスタを成立させる。"
                        "InfiniBand(独自・低レイテンシ)対Ethernet/UEC(オープン)の主導権争いで、"
                        "800G→1.6T→3.2Tと世代ごとに電気層を総取り替えする激しい更新サイクル。"
                        "Ethernetが800G普及でInfiniBandを逆転する見込み。スイッチシリコンとCPOが川上の要。")
        L["sub_systems"] = [
            {"id": "L7-A", "name": "InfiniBand (独自・低レイテンシ)", "desc": "NVIDIA主導。最低レイテンシで学習クラスタの主流。NDR 400G→XDR 800G。"},
            {"id": "L7-B", "name": "Ethernet / UEC (オープン)", "desc": "Ultra Ethernet Consortium。全層再構築でInfiniBandに対抗。推論で優位、800Gで逆転見込み。"},
            {"id": "L7-C", "name": "スイッチシリコン・光", "desc": "Tomahawk/Spectrum等の大容量スイッチASICとscale-out CPO。102.4Tbps競争。"},
        ]

L7_IDS = {"infiniband", "ethernet-uec", "switch-silicon"}
d["nodes"] = [n for n in d["nodes"] if n["id"] not in L7_IDS]

L7_NODES = [
  {
    "id": "infiniband", "kind": "tech", "layer": "L7", "sub": "L7-A",
    "name": "InfiniBand", "full": "InfiniBand (NDR/XDR) + Spectrum-X",
    "status": "active", "lineage": "scaleout-proprietary",
    "maturity": 5, "bottleneck": 3, "investment": 4,
    "players": ["NVIDIA(Quantum/ConnectX/BlueField)"],
    "alts": ["ethernet-uec"],
    "milestones": {
      "now": "最低レイテンシ(1-2μs)・クレジットベースのロスレス転送で学習クラスタの主流。NDR 400G主流、XDR 800G展開中。Quantum-X800出荷。SHARP/適応ルーティング等の機能で囲い込み。",
      "2027": "Ethernetが800G普及で逆転圧力。NVIDIAはSpectrum-X(独自Ethernet)で両睨み($10B run-rate)。",
      "2030": "学習=IB / 推論=Ethernet の住み分けが定着(infer)。"
    },
    "def": "スーパーコンピュータ由来の超低レイテンシ・ロスレス・ネットワーク。生成AI初期に学習クラスタを押さえた性能リーダーだが、ベンダーロックインとTCOが弱点。NVIDIAはEthernet版のSpectrum-Xも展開し二正面。",
    "materials": ["die_logic"]
  },
  {
    "id": "ethernet-uec", "kind": "tech", "layer": "L7", "sub": "L7-B",
    "name": "Ethernet / UEC", "full": "Ultra Ethernet Consortium 1.0 / AI Ethernet",
    "status": "emerging", "lineage": "scaleout-open",
    "maturity": 4, "bottleneck": 3, "investment": 5,
    "players": ["AMD", "Arista", "Broadcom", "Cisco", "Meta", "Microsoft", "Intel", "HPE", "NVIDIA(創設メンバー)"],
    "alts": ["infiniband"],
    "milestones": {
      "now": "UEC 1.0(2025/6, 1.0.1更新): RoCEv2の改良でなくSoftware/Transport/Network/Link/Physical全層の再構築。Packet Delivery Sublayer(PDS)で低レイテンシ化。Broadcom Thor Ultra(初の800G UEC NIC, 10万XPU+対応)。",
      "2027": "1.6T(IEEE 802.3dj 200G/lane, 2026末)。Ethernetが800G普及でInfiniBandを逆転(analyst見込)。",
      "2030": "3.2Tへ。AI scale-outの主流規格(spec)。"
    },
    "def": "InfiniBandに対抗するオープンなscale-out規格。UECは単一ベンダ依存を避ける開放標準として、RDMAの近代化(パケットレベル・マルチパス、順序外配置、HW再送、プログラマブル輻輳制御)で低レイテンシ・大規模性を実現。Ethernetが性能でIBに追いつきつつある。",
    "materials": ["die_logic"]
  },
  {
    "id": "switch-silicon", "kind": "tech", "layer": "L7", "sub": "L7-C",
    "name": "スイッチシリコン・scale-out光", "full": "Switch ASIC (Tomahawk/Spectrum) + Scale-Out CPO",
    "status": "active", "lineage": "scaleout-silicon",
    "maturity": 4, "bottleneck": 4, "investment": 5,
    "players": ["Broadcom(Tomahawk 6/Jericho 4)", "NVIDIA(Spectrum-X)", "Marvell(Teralynx)", "Cisco(Silicon One)"],
    "alts": [],
    "milestones": {
      "now": "Broadcom Tomahawk 6=102.4Tbps(先行出荷)。NVIDIA Spectrum-X1600 102.4Tbpsは2026後半(約1年遅れ)。各社CPO版を準備。",
      "2027": "scale-out CPOが本格化(scale-upに次ぐ)。1.6T世代。",
      "2030": "3.2T・CPO標準化。スイッチASICがネットワーク価値の中核(spec)。"
    },
    "def": "scale-outネットワークの心臓=大容量スイッチASICと、その光化(CPO)。帯域(102.4Tbps級)とポート消費電力の競争。Broadcomが先行、NVIDIAが追う。scale-out CPOはscale-up(L6)に次いで導入が進む。",
    "materials": ["die_logic", "glass_int"]
  },
]
d["nodes"].extend(L7_NODES)

MANAGED = set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label: e["label"]=label
    MANAGED.add((s,t,ty)); return e

new_edges = [
  mk("infiniband","L7-A","hier"),
  mk("ethernet-uec","L7-B","hier"),
  mk("switch-silicon","L7-C","hier"),
  mk("ethernet-uec","infiniband","cross","オープン規格で逆転を狙う"),
  mk("ethernet-uec","infiniband","time","800G普及でEthernetが逆転(spec)"),
  # L7 <-> L6 boundary (scale-out vs scale-up)
  mk("switch-silicon","cpo","cross","scale-out CPOはscale-upに次ぐ"),
  # L7 -> L5 (network serves compute clusters)
  mk("ethernet-uec","hyperscaler-asic","cross","10万XPUクラスタを結合"),
  mk("infiniband","rubin","cross","学習クラスタの後方網"),
  # L7 -> L3 (switch CPO on packaging)
  mk("switch-silicon","glass-int","cross","CPO光導波路"),
  # trend crossings
  mk("switch-silicon","T-optical","cross"),
  mk("ethernet-uec","T-sys","cross"),
]

def k(e): return (e["s"],e["t"],e["type"])
d["edges"] = [e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new_edges)

d["meta"]["version"] = "0.5-L3L4L5L6L7"

out = json.dumps(d, ensure_ascii=False, indent=2)
json.loads(out)
open(P,"w").write(out + "\n")
print(f"L7 populated. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
