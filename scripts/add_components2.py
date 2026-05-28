#!/usr/bin/env python3
"""Round 2 component additions: the AI-critical parts the GPT list surfaced that
were genuinely missing as first-class nodes — power-integrity (PDN) family and
signal-integrity family. Deliberately NOT adding universal/commodity parts as
nodes (they go in the reference page instead). Idempotent."""
import json, os, copy
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "graph.json")
d = json.load(open(P)); orig=copy.deepcopy(d)

NEW = [
  # --- Power-integrity / PDN family (AI-critical: 2000A+ transients) ---
  {"id":"m-drmos","kind":"material","name":"DrMOS / Smart Power Stage","full":"Driver+MOSFET / Smart Power Stage (SPS)",
   "role":"電源段(POL変換)","etype":"電源部品",
   "props":{"集約":"ドライバ+ハイ/ローサイドMOSFETを1パッケージ化","SPS":"電流・温度検出を内蔵","AI文脈":"垂直給電(VPD)でプロセッサ直下にタイル配置、1モジュール280A級"},
   "suppliers":["Infineon","MPS","Renesas","onsemi","Vishay"],
   "alts":["ディスクリートMOSFET構成"],
   "def":"VRMの最終変換段。ドライバとMOSFETを1パッケージに集約し、Smart Power Stageは電流/温度センスも内蔵。AIアクセラレータは2000A超をコアレールに流すため、多相化して垂直給電(VPD)でダイ直下にタイル配置する。L1電源とL5チップの電気的接点。"},
  {"id":"m-powerinductor","kind":"material","name":"パワーインダクタ","full":"Power Inductor (Metal Composite)",
   "role":"VRM出力平滑","etype":"電源部品",
   "props":{"用途":"多相VRMの各相出力平滑","AI文脈":"メタルコンポジットで高電流・低損失・小型化、VPDでは電源段の上に積層"},
   "suppliers":["TDK","Murata","Vishay","Cyntec","Delta"],
   "alts":[],
   "def":"VRM出力電流を平滑する磁性部品。AIボードはGPU/HBMの多相電源で多数を使う。垂直給電では電源段の真上に積層し横方向の損失を減らす。受動部品だが電源密度を左右する。"},
  {"id":"m-sicap","kind":"material","name":"シリコンキャパシタ / DTC","full":"Silicon Capacitor / Deep Trench Capacitor / Embedded Capacitor",
   "role":"超低ESLデカップリング","etype":"受動部品",
   "props":{"配置":"パッケージ基板内蔵 / インターポーザ近傍 / ダイ直下","容量":"基板内蔵で9〜37µF級(Empower ECAP)","特徴":"超低ESL/ESRでMLCCより高速な過渡応答"},
   "suppliers":["Empower","TSMC(DTC)","Murata(シリコンキャパシタ)","ST"],
   "alts":["MLCC(ボードレベル)"],
   "def":"シリコン内/基板内に作る高密度デカップリングキャパシタ。Deep Trench Capacitor(DTC)はSi内に深い溝で容量を稼ぐ。ボード上MLCCでは届かない超低ESL・ダイ近接が必要なAIの急峻な電流過渡(power integrity)に対応。CoWoS-Lに統合される。MLCCの「次」。"},
  # --- Signal-integrity family (AI-critical: 224G SerDes, long reach) ---
  {"id":"m-retimer","kind":"material","name":"Retimer / Redriver","full":"Retimer / Redriver (Signal Conditioning)",
   "role":"高速信号補正","etype":"信号部品",
   "props":{"retimer":"信号を再生成(CDR内蔵)し長距離・低BERを確保","redriver":"信号を増幅・等化","用途":"PCIe/CXL/SerDes、224G世代で必須化"},
   "suppliers":["Astera Labs","Broadcom","Marvell","TI","Parade"],
   "alts":["銅直結(短距離のみ)","光化(CPO)"],
   "def":"高速信号の劣化を補正する部品。Retimerはクロックデータ再生で信号を作り直し、Redriverは増幅・等化する。224G SerDes・大規模ラックで配線が長くなるほど必須化。Astera Labsの主力で、AI接続市場の急成長セグメント。L6/L7と銅配線の限界を補う。"},
  {"id":"m-esd","kind":"material","name":"ESD/TVS保護素子","full":"ESD / TVS Protection Diode",
   "role":"静電気・サージ保護","etype":"保護部品",
   "props":{"用途":"高速I/O(PCIe/Ethernet/USB)、管理ポートの保護","要件":"低容量(高速信号を歪めない)"},
   "suppliers":["Nexperia","onsemi","Littelfuse","ST","Bourns"],
   "alts":[],
   "def":"静電気放電やサージから高速I/Oを守るダイオード。高速差動信号を歪めない低容量品が要る。地味だが全I/Oに必要で、信頼性の底を支える。"},
  {"id":"m-clock","kind":"material","name":"クロック / 水晶振動子","full":"Clock Generator / Crystal / TCXO/OCXO",
   "role":"基準クロック供給","etype":"信号部品",
   "props":{"構成":"水晶振動子(基準)+クロックジェネレータ(分配)+TCXO/OCXO(高安定)","用途":"PCIe/Ethernet/SoC/SerDesの位相基準"},
   "suppliers":["SiTime","Renesas(IDT)","TI","Seiko Epson","村田"],
   "alts":["MEMS発振器(SiTime)"],
   "def":"全デジタル動作の時間基準。水晶振動子が基準を作り、クロックジェネレータが各ブロックへ分配、TCXO/OCXOが高安定を要する箇所を担う。SerDesの位相雑音(ジッタ)が帯域を左右するため、AIネットワークで重要度が上がっている。"},
]
new_ids={m["id"] for m in NEW}
d["nodes"]=[n for n in d["nodes"] if n["id"] not in new_ids]
d["nodes"].extend(NEW)

MANAGED=set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label:e["label"]=label
    MANAGED.add((s,t,ty));return e
new_edges=[
  # power-integrity: L1 power -> chips, decoupling near package (L3)
  mk("hvdc","m-drmos","comp"),
  mk("m-drmos","m-powerinductor","cross","多相VRMを構成"),
  mk("m-drmos","rubin","cross","ダイ直下に垂直給電(VPD)"),
  mk("m-sicap","cowos","cross","CoWoS-Lに統合(超低ESL)"),
  mk("m-sicap","m-mlcc","time","ダイ近接デカップリングでMLCCを補完/代替"),
  mk("m-drmos","T-power","cross"),
  # signal-integrity: L6/L7 interconnect
  mk("m-retimer","nvlink","cross","銅scale-upの到達距離を延長"),
  mk("m-retimer","ethernet-uec","cross","PCIe/SerDes信号補正"),
  mk("m-retimer","cpo","time","銅の限界を補うが、最終的に光化が代替"),
  mk("m-esd","ethernet-uec","comp"),
  mk("m-clock","switch-silicon","comp"),
  mk("m-clock","ethernet-uec","cross","SerDesの位相基準(ジッタ)"),
]
def k(e):return (e["s"],e["t"],e["type"])
d["edges"]=[e for e in d["edges"] if k(e) not in MANAGED]
d["edges"].extend(new_edges)

d["meta"]["version"]="1.4-pdn-si"
out=json.dumps(d,ensure_ascii=False,indent=2);json.loads(out)
open(P,"w").write(out+"\n")
print(f"round2 components. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
