#!/usr/bin/env python3
"""Add pricing-power (pricing) and supply-tightness (tightness) axes (0-5) to nodes.
Major nodes get researched values + evidence note (as-of 2026-05); others get
reasoned inference. Idempotent."""
import json, os, copy
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=os.path.join(ROOT,"data","graph.json"); d=json.load(open(P)); orig=copy.deepcopy(d)

# id -> (pricing, tightness, evidence, etag)  etag in {fact,infer,spec}
DATA = {
 # --- extreme: oligopoly/monopoly + sold-out ---
 "hbm4":      (5,5,"SK/Samsung/Micron寡占。2026分は完全完売、HBM4は$500/個・HBM3e比+30〜50%、NVIDIA向けで約50%プレミアム獲得。不足は2027後半まで。DDR5比3倍のウェハ消費。",  "fact"),
 "cowos":     (5,5,"TSMCほぼ独占。2025〜2026完売、リードタイム50週超。Amkor外注も26-39週。代替不可で最大の律速。", "fact"),
 "m-abf":     (5,5,"味の素がABFフィルムを95%独占(26年)。2026 Q3に+30%。層数増(11+11→13+13)で再逼迫。増設は36ヶ月+歩留り学習曲線で即効性なし。", "fact"),
 # --- high pricing, high tightness ---
 "hbm-basedie":(4,4,"ベースダイをTSMC先端ノードで製造=ファウンドリ律速。カスタム化で差別化。HBM本体の逼迫を継承。", "infer"),
 "glass-sub": (4,3,"ガラスコア基板。次世代で寡占化の可能性。現状は立上げ期で量限定だが代替難。", "infer"),
 "litho":     (5,4,"ASMLがEUV独占。装置リードタイム長。High-NA採否が分かれるが露光自体は代替不可。", "fact"),
 "rubin":     (5,4,"NVIDIA ~80%シェア+CUDA moat。GPU自体の価格決定力は最強だが、上流(HBM/CoWoS)に利益を吸われる構造。", "fact"),
 # --- node materials (TSMC process) ---
 "gaa":       (5,4,"先端ノード(N2/N3)はTSMCに集中、2027+まで予約満杯。価格改定進行。", "fact"),
 "bspdn":     (4,3,"裏面給電はTSMC/Intelの先端のみ。立上げ期で量限定。", "infer"),
 # --- memory tier ---
 "socamm":    (3,3,"LPDDRベース、JEDEC標準化でマルチベンダ化。HBMより競争的だが新規格で当面タイト。", "infer"),
 "cxl":       (3,2,"規格段階、複数ベンダ。逼迫は限定的。", "infer"),
 "hbm4e":     (4,4,"次世代HBM。カスタムベースダイで差別化、立上げで限定供給。", "spec"),
 # --- interconnect ---
 "nvlink":    (5,3,"NVIDIA独自で代替不可だがGPUに内包され単体市場でない。", "infer"),
 "ualink":    (3,3,"オープン規格でマルチベンダ。立上げ期。価格決定力は分散。", "infer"),
 "cpo":       (4,4,"光エンジン/SoIC実装が限られ立上げ逼迫。TSMC SoIC律速。", "spec"),
 "ethernet-uec":(2,3,"オープン標準・多数ベンダで価格決定力低。スイッチ需要は逼迫。", "infer"),
 "infiniband":(4,3,"NVIDIA独自で価格決定力高。ただしEthernetに侵食され将来低下。", "infer"),
 "switch-silicon":(4,4,"Broadcom/Marvell寡占。Tomahawk6等は需要逼迫。設計受託の要。", "fact"),
 # --- power/cooling ---
 "hvdc":      (3,3,"800V HVDCはNVIDIA+多数の電源大手(Infineon/TI/Vertiv等)。競争的だが立上げ逼迫。", "infer"),
 "liquid-cooling":(4,4,"液冷は急拡大で逼迫、CDU/コールドプレートの川上が限られる。Vertiv等。", "infer"),
 "power-supply":(4,5,"電力そのもの=系統接続キュー数年・SMR未成熟で最も構造的に逼迫。価格(電力料金)は地域依存。", "infer"),
 "pdn":       (3,3,"網全体としては多数部品の集合。個別部品で感応度が異なる。", "infer"),
 # --- L5 compute (mostly internalize upstream costs) ---
 "mi400":     (4,3,"AMD。NVIDIAに次ぐが、上流逼迫を継承。", "infer"),
 "tpu":       (4,3,"Broadcom設計・TSMC製造。自社向けで外部価格は不透明だがTCO優位。", "infer"),
 "trainium":  (4,3,"同上(Annapurna/Marvell)。コスト破壊側。", "infer"),
 "cerebras":  (4,3,"ウェハスケールで独自。TSMC 5nm。供給は自社律速。", "infer"),
 "sambanova": (2,2,"独立勢、競争的。Groq吸収で勢力後退。", "infer"),
 "china-asic":(2,3,"SMIC製造で性能劣位だが内需で逼迫。価格は補助金歪み。", "spec"),
 "vera-cpu":  (4,3,"CPU+GPU統合。NVIDIA/AMDで寡占的。", "infer"),
 # --- key materials ---
 "m-mlcc":    (4,5,"AI用高容量MLCCは強い逼迫(BB比>1、リードタイム26-40週)。Murataが2026年4月から+15〜35%値上げ、Taiyo Yuden/SEMCOも+6〜13%追従。AI server特化品でMurata 45%+SEMCO 39%=84%寡占。GB300ラックで44万個、2030年に2025比3.3倍需要。消費者向け汎用は依然軟調。", "fact"),
 "m-sicap":   (5,4,"シリコンキャパシタ/DTCは少数(Empower/TSMC/TI等)。超低ESLで代替難。立上げ逼迫。", "infer"),
 "m-gansic":  (4,4,"GaN/SiCは限られた専業(Infineon等)。800V移行で需要急増、ウェハ供給律速。", "infer"),
 "m-drmos":   (3,3,"DrMOS/SPSは数社。VPDで需要増だが競争的。", "infer"),
 "m-powerinductor":(3,4,"パワーインダクタはMurata等が値上げ。AI大電流で逼迫。", "fact"),
 "m-optengine":(4,4,"光エンジン/Siフォトニクスは少数(Broadcom/TSMC COUPE等)。CPO立上げで逼迫。", "infer"),
 "m-euvmask": (4,3,"EUVマスク。少数(TSMC内製/Toppan/DNP/Hoyaブランクス)。", "infer"),
 "m-cdu":     (4,4,"CDU/コールドプレートはVertiv/Boyd等。液冷急拡大で逼迫。", "infer"),
 "m-retimer": (4,4,"Retimerは少数(Astera/Broadcom等)、224Gで必須化し逼迫。", "infer"),
 "m-hbond":   (4,3,"ハイブリッドボンディング装置はBESI/AMAT寡占。立上げ。", "infer"),
 "m-tsv":     (3,3,"TSV工程。HBM/積層の必須要素で逼迫を継承。", "infer"),
 "m-shunt":   (2,2,"シャント抵抗は競争的(Vishay/Bourns/KOA等)、汎用性高く価格決定力低。", "infer"),
 "m-esd":     (1,2,"汎用保護素子、多数ベンダ、価格決定力低。", "infer"),
 "m-clock":   (3,4,"224G PAM4/1.6T Ethernet/CPOで <25fs級ジッタが必須化。SiTime売上Q1 2026 +88% YoY (AI-DC +158%)。SiTime → Renesas Timing $3B買収進行中。Kyocera 30fs差動XO量産・6月から200万個/月。合成石英オートクレーブが日本集中で短期増産不可。", "fact"),
 "m-ihs":     (2,2,"ヒートスプレッダ、競争的・汎用。", "infer"),
 "m-tim":     (3,3,"高性能TIM(液体金属等)は限られるが標準品は競争的。", "infer"),
 "m-vrm":     (3,3,"VRMコントローラはInfineon/MPS/Renesas等で競争的。", "infer"),
 "m-tgv":     (3,2,"ガラス貫通電極、立上げ期で量限定。", "spec"),
 "m-ccl":     (3,4,"CCLはResonac/三菱ガス化学が+30%。AI基板で逼迫だがABFフィルムよりは競争的。", "fact"),
}

for n in d["nodes"]:
    v = DATA.get(n["id"])
    if v:
        n["pricing"], n["tightness"], n["pricenote"], n["priceetag"] = v
    else:
        # reasoned default by kind: unknown materials lean competitive
        n.setdefault("pricing", 2); n.setdefault("tightness", 2)
        n.setdefault("priceetag","spec")

d["meta"]["version"]="1.6-priceaxes"
out=json.dumps(d,ensure_ascii=False,indent=2); json.loads(out)
open(P,"w").write(out+"\n")
covered=sum(1 for n in d['nodes'] if n['id'] in DATA)
print(f"price axes added. {covered}/{len(d['nodes'])} nodes with researched/inferred values")
