#!/usr/bin/env python3
"""Revise L5 演算チップ: expand from 3 to 5 sub-systems, split the monolithic
hyperscaler-asic node into tpu + trainium, add wafer-scale (cerebras),
dataflow/inference (sambanova), China (china-asic), and a Broadcom/Marvell
enabler note. Idempotent. Migrates edges that referenced hyperscaler-asic."""
import json, os, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "graph.json")
d = json.load(open(P))
orig = copy.deepcopy(d)

# ---- 1. L5 sub-systems: 3 -> 5 ----
for L in d["layers"]:
    if L["id"] == "L5":
        L["summary"] = ("AIアクセラレータ本体。商用GPU・ハイパースケーラ独自ASIC・推論特化・中国勢の多極化。"
                        "微細化(L2)・パッケージ(L3)・メモリ(L4)の全ボトルネックがここに集約し、"
                        "歩留りが出荷量と仕様を直接律速する。設計受託のBroadcom/Marvellが"
                        "独自ASICの8割超を支える隠れた要。推論需要の急拡大で独自ASICがGPUを上回る成長率。")
        L["sub_systems"] = [
            {"id": "L5-A", "name": "商用GPU", "desc": "汎用アクセラレータ。NVIDIA Rubin / AMD MI400系。CUDA等ソフト資産が競争軸。"},
            {"id": "L5-B", "name": "ハイパースケーラ独自ASIC", "desc": "Google TPU / AWS Trainium。Broadcom/Marvellが設計受託。総体でNVIDIAへの最大の脅威。"},
            {"id": "L5-C", "name": "推論特化・データフロー", "desc": "Cerebras(ウェハスケール)/SambaNova(データフロー)。decode帯域に特化。Groqはほぼ吸収。"},
            {"id": "L5-D", "name": "中国勢", "desc": "Huawei Ascend / Alibaba T-Head。輸出規制下でSMIC製造、内需で急拡大。"},
            {"id": "L5-E", "name": "CPU・スーパーチップ統合", "desc": "Vera等CPUとGPUをコヒーレント結合。システム統合トレンドの結節点。"},
        ]

# ---- 2. remove old L5 content nodes we manage (incl. retired hyperscaler-asic) ----
L5_IDS = {"rubin","mi400","vera-cpu","hyperscaler-asic","tpu","trainium","cerebras","sambanova","china-asic"}
d["nodes"] = [n for n in d["nodes"] if n["id"] not in L5_IDS]

L5_NODES = [
  {
    "id": "rubin", "kind": "tech", "layer": "L5", "sub": "L5-A",
    "name": "NVIDIA Rubin (R100)", "full": "Vera Rubin Platform / R100 GPU",
    "status": "emerging", "lineage": "commercial-gpu",
    "maturity": 3, "bottleneck": 5, "investment": 5,
    "players": ["NVIDIA", "TSMC(製造)", "SK hynix/Samsung/Micron(HBM4)"],
    "alts": ["mi400", "tpu", "trainium"],
    "milestones": {
      "now": "GTC2026で詳細確定。TSMC N3・4レチクルCoWoS-L・NVIDIA初のチップレットGPU。288GB HBM4 / 22.2TB/s / 336億トランジスタ / FP4 50PFLOPS。量産2026前半、システムH2 2026。Groqを$20Bで実質吸収しLPX(LPU)をプラットフォームに統合。",
      "2027": "Rubin Ultra(R200): CoWoS-L歩留り問題で4ダイ→デュアルダイに縮小。16-Hi HBM4。",
      "2030": "後継世代。ガラス基板採用でレチクル制約緩和(spec)。"
    },
    "def": "NVIDIAの次世代AIアクセラレータ。初のチップレットGPU。律速は演算でなくHBM4帯域とCoWoS-L/HBM歩留り——16-Hi HBM4歩留り危機(<20%)でR100はピン速度を下げる仕様調整を実施。CUDA moatで~80%シェアを維持。",
    "materials": ["die_logic", "ubump"]
  },
  {
    "id": "mi400", "kind": "tech", "layer": "L5", "sub": "L5-A",
    "name": "AMD Instinct MI400 (MI455X)", "full": "Instinct MI455X / MI430X (CDNA 5)",
    "status": "emerging", "lineage": "commercial-gpu",
    "maturity": 2, "bottleneck": 4, "investment": 4,
    "players": ["AMD", "TSMC(N2製造)", "OpenAI($90B/6GW契約)", "Meta/OCP(Helios)"],
    "alts": ["rubin", "tpu"],
    "milestones": {
      "now": "CES2026公表。TSMC N2(初の2nm GPU)でRubin(N3)に対しプロセス先行。432GB HBM4 / 19.6TB/s(容量1.5倍)。CoWoS-L 3.5D。FP4 40PFLOPS。Helios 72-GPUラック。OpenAIと$90B/6GW契約。",
      "2027": "MI500(次世代compute/memory/interconnect)。",
      "2030": "—"
    },
    "def": "AMDの対NVIDIA本命。MI455X(学習/推論)とMI430X(HPC/FP64)に分岐。FLOPで勝つのでなくFP4/FP8で並びメモリ容量とオープン相互接続(UALink/UEC)で上回る戦略。CUDA非互換のソフト移行が最大障壁。",
    "materials": ["die_logic", "ubump"]
  },
  {
    "id": "tpu", "kind": "tech", "layer": "L5", "sub": "L5-B",
    "name": "Google TPU (Ironwood)", "full": "TPU v7 Ironwood / 8th-gen (8t/8i)",
    "status": "active", "lineage": "custom-asic",
    "maturity": 5, "bottleneck": 3, "investment": 5,
    "players": ["Google", "Broadcom(設計, 2031まで)", "MediaTek(8i推論)", "Marvell(交渉中)", "Anthropic(1M chips/1GW+)"],
    "alts": ["rubin", "trainium"],
    "milestones": {
      "now": "Ironwood(v7)一般提供。4.6 PFLOPS FP8 / 192GB HBM3e / 7.4TB/s。GCP外への外販開始(従来は自社限定)。Ironwood全TCOはGB200比~44%低。プログラム7世代の成熟。Anthropicが100万チップ・1GW+を確保。",
      "2027": "第8世代が学習(8t, Broadcom)/推論(8i, MediaTek)に分岐、TSMC 2nm。出荷4.3M(2026)→10M(2027)→35M+(2028)見込。",
      "2030": "ハイパースケーラ最成熟ASICとして地位確立(infer)。"
    },
    "def": "Googleの自社AIアクセラレータ。学習・推論両対応で最も成熟したハイパースケーラASIC(2015〜7世代)。クラスタ協調とソフト(XLA)で優位。Broadcomが設計受託の中核。外販開始でNVIDIA代替の現実味が増す。Gemini/Claude等フロンティアモデルを支える。",
    "materials": ["die_logic"]
  },
  {
    "id": "trainium", "kind": "tech", "layer": "L5", "sub": "L5-B",
    "name": "AWS Trainium", "full": "AWS Trainium3 / Inferentia (Annapurna)",
    "status": "active", "lineage": "custom-asic",
    "maturity": 4, "bottleneck": 3, "investment": 5,
    "players": ["AWS(Annapurna Labs)", "Marvell/Broadcom(設計)", "Anthropic($25B出資/共同設計)"],
    "alts": ["rubin", "tpu"],
    "milestones": {
      "now": "Trainium3(2025/12, 初の3nm): 2.52 PFLOPS FP8 / 144GB HBM3e / 4.9TB/s(T2比1.7倍帯域)。学習Trainium+推論Inferentiaの二枚看板でNVIDIA比最大50%安。T2を50万個+量産(単位数で最大の商用ASICフリート)。",
      "2027": "Trainium4はNVLink 6/NVIDIA MGXと統合(NVLink Fusion、NVIDIAとの協業)。CerebrasとprefillをTrainium/decodeをWSEで分担(Bedrock)。",
      "2030": "コスト破壊でNVIDIA代替の中核(infer)。"
    },
    "def": "AWSの自社AIアクセラレータ。学習(Trainium)/推論(Inferentia)の二枚看板でコスト破壊(NVIDIA比~50%安)を狙う。垂直統合の価格優位はASICを持たない競合が追随困難。Cerebrasと組みdecode帯域を補完するなど構成が柔軟。",
    "materials": ["die_logic"]
  },
  {
    "id": "cerebras", "kind": "tech", "layer": "L5", "sub": "L5-C",
    "name": "Cerebras (ウェハスケール)", "full": "Cerebras WSE-3 / CS-3",
    "status": "active", "lineage": "wafer-scale",
    "maturity": 4, "bottleneck": 4, "investment": 5,
    "players": ["Cerebras", "TSMC(5nm製造)", "OpenAI($20B/750MW)", "AWS(Bedrock)", "G42(Condor Galaxy)"],
    "alts": ["sambanova", "rubin"],
    "milestones": {
      "now": "WSE-3: ウェハ丸ごと1チップ(46,225mm²)、4兆トランジスタ・90万コア・44GB on-chip SRAM・21PB/s(H100の7000倍)。TSMC 5nm。decode特化でLlama4 Maverick 2,500 tok/s(DGX B200の2倍超)。OpenAI $20B/750MW、AWS Bedrog採用、2026/4 IPO申請($22-25B)。",
      "2027": "TrainiumとprefillをTrainium/decodeをWSEで分担する分離アーキが拡大。",
      "2030": "メモリの壁への物理的解(オンチップSRAM)として推論で定着(infer)。"
    },
    "def": "ウェハを切らず丸ごと1つの巨大プロセッサにする逆転の発想。チップレット/パッケージング(L3)の真逆で、ダイシングを廃しオンチップSRAMでメモリの壁を物理的に回避。decode(生成)帯域律速の推論で圧倒的速度。TSMC SoW(System-on-Wafer)と思想的に連続。",
    "materials": ["die_logic"]
  },
  {
    "id": "sambanova", "kind": "tech", "layer": "L5", "sub": "L5-C",
    "name": "SambaNova / 推論特化勢", "full": "SambaNova RDU (SN40L) ほか",
    "status": "active", "lineage": "dataflow",
    "maturity": 3, "bottleneck": 3, "investment": 3,
    "players": ["SambaNova", "(Groqは$20BでNVIDIAが実質吸収)", "Graphcore"],
    "alts": ["cerebras", "tpu"],
    "milestones": {
      "now": "SambaNova RDU(SN40L)=2ロジックダイ+SRAM+HBM+直結DDRの三層メモリで大モデルを少数チップで(70Bを16チップ、Groqの576チップ対比)。再構成可能データフローで多モデル・大規模に柔軟。",
      "2027": "Groq吸収でNVIDIAがLPU技術獲得、独立推論勢の立ち位置は弱体化。",
      "2030": "独自アーキの生存はソフト・特定WL最適化次第(spec)。"
    },
    "def": "GPUと異なるデータフロー/再構成可能アーキで推論を高速化する独立勢。SambaNovaは三層メモリで大モデルを少数チップに収める効率が特徴。GroqのLPU(静的スケジューリング+SRAM)は2026/3にNVIDIAが$20Bで実質吸収しRubinのLPXに統合——独立勢の構造的劣勢を象徴。",
    "materials": ["die_logic"]
  },
  {
    "id": "china-asic", "kind": "tech", "layer": "L5", "sub": "L5-D",
    "name": "中国勢 (Huawei/Alibaba)", "full": "Huawei Ascend 910C/950 / Alibaba T-Head",
    "status": "active", "lineage": "china-domestic",
    "maturity": 3, "bottleneck": 4, "investment": 4,
    "players": ["Huawei(Ascend)", "Alibaba(T-Head/PPU)", "SMIC(製造)", "DeepSeek等(顧客)"],
    "alts": ["rubin"],
    "milestones": {
      "now": "輸出規制でNVIDIA供給を断たれた中国の内製化。Huawei Ascend 910C=H100の約60%推論性能、SMIC製造で2026に60万個目標。Alibaba T-Head累計47万個出荷。DeepSeek V4等が採用。",
      "2027": "CloudMatrix等のシステム結合で単体性能の劣位をスケールで補う。Ascend 950へ。",
      "2030": "国産エコシステムが内需を相当内製化(spec)。輸出規制が分断を固定。"
    },
    "def": "米輸出規制下の中国自製AIアクセラレータ。SMIC製造で単体性能はNVIDIA比劣るが、内需と国家戦略で急拡大しシステム結合(CloudMatrix)で量的に補う。グローバル市場の地政学的分断を象徴する第四極。",
    "materials": ["die_logic"]
  },
  {
    "id": "vera-cpu", "kind": "tech", "layer": "L5", "sub": "L5-E",
    "name": "CPU・スーパーチップ統合", "full": "NVIDIA Vera / AMD EPYC Venice + GPU coherent",
    "status": "emerging", "lineage": "cpu-superchip",
    "maturity": 3, "bottleneck": 3, "investment": 4,
    "players": ["NVIDIA(Vera)", "AMD(EPYC Venice, Zen6/N2)", "Google(Axion)"],
    "alts": [],
    "milestones": {
      "now": "Vera Rubin Superchip = Vera CPU(88コア/176スレッド)×1 + Rubin GPU×2をNVLink-C2Cで結合、FP4 100PFLOPS。CPU-GPUコヒーレンスがメモリ中心アーキの鍵。Google Axion CPUも展開。",
      "2027": "EPYC Venice(Zen6, TSMC N2)等が追随。CXLプーリングと連携。",
      "2030": "—"
    },
    "def": "CPUとGPUを密結合し1ノードとして設計する潮流。システム統合・メモリ中心アーキの交差点。",
    "materials": ["die_logic"]
  },
]
d["nodes"].extend(L5_NODES)

# ---- 3. migrate/rebuild edges: anything referencing hyperscaler-asic -> tpu/trainium ----
# Drop edges touching retired node and all edges we will re-add.
RETIRED = "hyperscaler-asic"
MANAGED = set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label: e["label"]=label
    MANAGED.add((s,t,ty)); return e

# Preserve external edges that pointed at hyperscaler-asic by repointing to tpu (representative)
# (ethernet-uec -> hyperscaler-asic "10万XPUクラスタ" becomes -> tpu)
repointed = []
for e in d["edges"]:
    if e.get("t") == RETIRED and e.get("s") not in L5_IDS:
        repointed.append(mk(e["s"], "tpu", e["type"], e.get("label")))
    if e.get("s") == RETIRED and e.get("t") not in L5_IDS:
        repointed.append(mk("tpu", e["t"], e["type"], e.get("label")))

def k(e): return (e["s"], e["t"], e["type"])
# remove: any edge touching retired node, any edge touching managed L5 ids (we re-add cleanly)
d["edges"] = [e for e in d["edges"]
              if e["s"] != RETIRED and e["t"] != RETIRED
              and e["s"] not in L5_IDS and e["t"] not in L5_IDS]

new_edges = [
  # hierarchy
  mk("rubin","L5-A","hier"), mk("mi400","L5-A","hier"),
  mk("tpu","L5-B","hier"), mk("trainium","L5-B","hier"),
  mk("cerebras","L5-C","hier"), mk("sambanova","L5-C","hier"),
  mk("china-asic","L5-D","hier"),
  mk("vera-cpu","L5-E","hier"),
  # competition
  mk("mi400","rubin","cross","競合(N2 vs N3 / 容量 vs FLOP)"),
  mk("tpu","rubin","cross","最成熟ASIC・外販で代替圧力"),
  mk("trainium","rubin","cross","コスト破壊(~50%安)"),
  mk("cerebras","rubin","cross","decode速度で2倍超(推論)"),
  mk("china-asic","rubin","cross","規制下の代替(~60%性能)"),
  # disaggregation pattern
  mk("cerebras","trainium","cross","prefill=Trainium / decode=WSE 分離"),
  # L5 -> L3 packaging
  mk("rubin","cowos","cross","CoWoS-L採用 / 歩留り律速"),
  mk("mi400","cowos","cross","CoWoS-L 3.5D採用"),
  mk("rubin","soic","cross","チップレット積層"),
  mk("cerebras","soic","cross","ウェハスケール=SoWと連続"),
  # L5 -> L4 memory
  mk("rubin","hbm4","cross","HBM4×8-12搭載"),
  mk("mi400","hbm4","cross","HBM4 432GB搭載"),
  mk("trainium","hbm4","cross","HBM3e/HBM4搭載"),
  # superchip composition
  mk("vera-cpu","rubin","comp","Vera Rubin Superchip"),
  # enabler concentration (Broadcom/Marvell design 80%+ of ASIC) — express as cross to L7 switch silicon proxy not ideal; keep as tpu/trainium players only
  # trend crossings
  mk("vera-cpu","T-sys","cross"), mk("vera-cpu","T-mem","cross"),
  mk("tpu","T-sys","cross"),
  mk("cerebras","T-mem","cross"),
  mk("rubin","T-power","cross"),
]
d["edges"].extend(repointed)
d["edges"].extend(new_edges)
# de-dup edges by (s,t,type) keeping first
seen=set(); dedup=[]
for e in d["edges"]:
    kk=k(e)
    if kk in seen: continue
    seen.add(kk); dedup.append(e)
d["edges"]=dedup

d["meta"]["version"] = "1.1-L5expanded"

out = json.dumps(d, ensure_ascii=False, indent=2)
json.loads(out)
open(P,"w").write(out + "\n")
l5n=[n['id'] for n in d['nodes'] if n.get('layer')=='L5']
print(f"L5 revised. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
print("L5 nodes:", l5n)
print("hyperscaler-asic removed:", not any(n['id']=='hyperscaler-asic' for n in d['nodes']))
