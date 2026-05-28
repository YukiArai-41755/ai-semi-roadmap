#!/usr/bin/env python3
"""Populate L6 スケールアップ・インターコネクト into graph.json. Idempotent.
Promotes the cpo stub to a full node so L3 (glass-int -> cpo) auto-resolves."""
import json, os, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "graph.json")
d = json.load(open(P))
orig = copy.deepcopy(d)

for L in d["layers"]:
    if L["id"] == "L6":
        L["status"] = "done"
        L["summary"] = ("ラックを1台のGPUにする結合層。GPU間(scale-up)の超広帯域インターコネクト。"
                        "NVLink(独自)対UALink(オープン)の規格戦争が主軸で、銅の物理限界に伴い"
                        "2028年頃から共パッケージ光(CPO)へ移行が始まる。scale-up配線のTAMは"
                        "既にscale-out(L7)を凌駕——投資的に最重要の結節点の一つ。")
        L["sub_systems"] = [
            {"id": "L6-A", "name": "独自ファブリック (NVLink系)", "desc": "NVIDIAのNVLink。最高性能だが独自。NVLink Fusionで一部開放。"},
            {"id": "L6-B", "name": "オープン規格 (UALink系)", "desc": "UALink/Infinity Fabric。AMD/Intel/Google/MS/Meta/Broadcom連合。低コスト・マルチベンダ。"},
            {"id": "L6-C", "name": "光化 (CPO / 光scale-up)", "desc": "銅の物理限界を超える共パッケージ光。2028頃scale-upから本格導入。"},
        ]

L6_IDS = {"nvlink", "ualink", "cpo"}
d["nodes"] = [n for n in d["nodes"] if n["id"] not in L6_IDS]

L6_NODES = [
  {
    "id": "nvlink", "kind": "tech", "layer": "L6", "sub": "L6-A",
    "name": "NVIDIA NVLink", "full": "NVLink 6 / NVLink Fusion",
    "status": "active", "lineage": "scaleup-proprietary",
    "maturity": 5, "bottleneck": 4, "investment": 5,
    "players": ["NVIDIA", "Marvell(NVLink Fusion, $2B出資)"],
    "alts": ["ualink"],
    "milestones": {
      "now": "NVLink 6: 400G SerDes/lane、3.6TB/s/GPU(14.4Tbit/s)。Vera Rubin NVL72=72GPU/260TB/s集約、144GPUまでscale-up。銅で<1m。UALink対抗でNVLink Fusionにより一部パートナーへ開放。",
      "2027": "Rubin Ultra=576GPU(8×NVL72)へscale-up拡大。クロスラックで銅が限界に。",
      "2030": "Feynman世代でNVLink 8 CPOスイッチ(2028〜)。光と銅の併存(spec)。"
    },
    "def": "NVIDIAのGPU間scale-upインターコネクト。ラックを1台の巨大GPUに見せる中核技術で、NVL72等のラックスケール製品を成立させる。独自規格による囲い込みが競争優位の源泉だが、UALink台頭への対抗でNVLink Fusionとして部分開放。",
    "materials": ["die_logic"]
  },
  {
    "id": "ualink", "kind": "tech", "layer": "L6", "sub": "L6-B",
    "name": "UALink", "full": "Ultra Accelerator Link / AMD Infinity Fabric",
    "status": "emerging", "lineage": "scaleup-open",
    "maturity": 3, "bottleneck": 3, "investment": 4,
    "players": ["AMD", "Intel", "Google", "Microsoft", "Meta", "Broadcom", "Apple", "Upscale AI(スイッチ)"],
    "alts": ["nvlink"],
    "milestones": {
      "now": "UALink 1.0(2025/4): 200GT/s/lane、最大1,024GPU、<4m/<1μs、1〜4ラック決定的性能。AMD HeliosはUALinkで72GPU/260TB/s。AMDはInfinity Fabricからオープン規格へ転換。",
      "2027": "UALink 2.0(2026/4): チップレット標準・制御プレーン追加、200G Data Link 2版。初の商用スイッチQ4 2026(Upscale AI)。",
      "2030": "オープン・エコシステムがNVLinkのコスト優位を侵食(infer)。"
    },
    "def": "NVLinkに対抗するオープンなscale-upインターコネクト標準。AMD/Intel/Google/MS/Meta/Broadcom連合が推進し、業界標準でNVIDIA独自技術より低コストなラックスケール構築を可能にする。マルチベンダのアクセラレータ混載が狙い。",
    "materials": ["die_logic"]
  },
  {
    "id": "cpo", "kind": "tech", "layer": "L6", "sub": "L6-C",
    "name": "CPO (共パッケージ光)", "full": "Co-Packaged Optics for Scale-Up",
    "status": "emerging", "lineage": "scaleup-optical",
    "maturity": 2, "bottleneck": 4, "investment": 5,
    "players": ["NVIDIA(Spectrum-X/Quantum-X)", "Broadcom", "TSMC(SoIC製造)", "OCI-MSA連合", "Marvell"],
    "alts": ["nvlink"],
    "milestones": {
      "now": "GTC2025でscale-up CPOスイッチ発表。光変換エンジンをスイッチASIC直近に統合し、銅トレースの電気損失(200Gb/sで~22dB)・30W/portを回避。TSMC SoIC(3Dハイブリッドボンディング)で実装。",
      "2027": "OCI-MSAが光PHYの相互運用標準を整備(NVIDIAも参加)。銅はラック内<2028で優位を維持。",
      "2030": "Feynman NVLink 8 CPOスイッチ(2028〜)でscale-up光化が本格化。CPO普及率~35%(2030, TrendForce)。光がscale-up結合を席巻(spec)。"
    },
    "def": "電気I/Oを光に置換しスイッチ/演算ダイに共パッケージ化する技術。scale-up領域(GPU間)から先行導入される見込みで、scale-up CPOのTAMはscale-out向けを大きく上回る。ガラスインターポーザの基板内光導波路と好相性。銅の物理限界(距離・損失・電力)を超える次の構造変化点。",
    "materials": ["die_logic", "glass_int"]
  },
]
d["nodes"].extend(L6_NODES)

MANAGED = set()
def mk(s,t,ty,label=None):
    e={"s":s,"t":t,"type":ty}
    if label: e["label"]=label
    MANAGED.add((s,t,ty)); return e

new_edges = [
  mk("nvlink","L6-A","hier"),
  mk("ualink","L6-B","hier"),
  mk("cpo","L6-C","hier"),
  # competition / succession
  mk("ualink","nvlink","cross","オープン規格で対抗"),
  mk("cpo","nvlink","time","銅scale-upを光が置換(2028〜)"),
  # L6 -> L5 (interconnect serves compute)
  mk("nvlink","rubin","cross","Rubin NVL72を成立させる"),
  mk("ualink","mi400","cross","AMD Heliosの結合"),
  # L6 -> L3 (CPO built on SoIC packaging, glass interposer waveguide)
  mk("cpo","soic","cross","TSMC SoICで実装"),
  mk("cpo","glass-int","cross","基板内光導波路と好相性"),
  # trend crossings
  mk("cpo","T-optical","cross"),
  mk("nvlink","T-sys","cross"),
  mk("ualink","T-sys","cross"),
  mk("cpo","T-power","cross"),
]

def k(e): return (e["s"],e["t"],e["type"])
# also drop stale stub-era edge glass-int->cpo (we re-add as cpo->glass-int), keep both directions clean
DROP = {("glass-int","cpo","cross")}
d["edges"] = [e for e in d["edges"] if k(e) not in MANAGED and k(e) not in DROP]
d["edges"].extend(new_edges)

d["meta"]["version"] = "0.4-L3L4L5L6"

out = json.dumps(d, ensure_ascii=False, indent=2)
json.loads(out)
open(P,"w").write(out + "\n")
print(f"L6 populated. nodes {len(orig['nodes'])}->{len(d['nodes'])}, edges {len(orig['edges'])}->{len(d['edges'])}")
print("cpo full node:", not any(n['id']=='cpo' and n.get('stub') for n in d['nodes']))
print("remaining stubs:", [n['id'] for n in d['nodes'] if n.get('stub')])
