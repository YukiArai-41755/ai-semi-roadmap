#!/usr/bin/env python3
"""Round 1: L3 packaging tech nodes were missing price/supply axes (defaulted 2x2).
CoWoS=5x5 but its constituents were unscored — clearly inconsistent. Fix with
researched values (2026-05). Idempotent."""
import json, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=os.path.join(ROOT,"data","graph.json"); d=json.load(open(P))

DATA={
 "soic":      (5,5,"TSMC独占の3D積層(SoIC)。CoWoSと共に2026完売、18新工場建設中。ピッチ6μm→4.5μm(2029)。ハイブリッドボンディング装置(BESI/AMAT)律速。AMD MI3xx/次世代が採用。","fact"),
 "foveros":   (3,3,"Intel 3D積層。CoWoSのオーバーフロー先として実需立上げ(Clearwater Forest H1 2026量産、17タイル)。利用可能性が売りで逼迫度はCoWoSより低いが、価格決定力もIntel単独で限定的。","fact"),
 "emib":      (3,3,"Intelのブリッジ実装。CoWoSから設計移行が実際に発生(Diamond Rapids H2 2026)。成熟・即納可能=代替の受け皿だが、availabilityが売りゆえ価格は抑制的。","fact"),
 "ucie":      (2,3,"チップレット相互接続の標準規格。オープンで価格決定力低。採用拡大で重要性増すが規格自体は無償。","infer"),
 "org-sub":   (4,4,"有機ビルドアップ基板(ABF基板)。Unimicron/Ibiden/AT&S寡占(上位5社74%)。ABFフィルム逼迫(味の素95%)を継承し層数増で逼迫。基板メーカー自体はフィルムより競争的。","fact"),
 "glass-int": (3,2,"ガラスインターポーザ/CoPoS。次の構造変化だが立上げ前で量産限定。代替難だが現時点の逼迫は小。2027以降に本格化(spec)。","spec"),
 "copos-note":(2,2,"パネルレベルパッケージ(PLP)。コスト低減狙いで立上げ期。価格決定力・逼迫とも現状限定的。","spec"),
}
for nid,(p,t,note,et) in DATA.items():
    n=next((x for x in d['nodes'] if x['id']==nid),None)
    if n: n['pricing'],n['tightness'],n['pricenote'],n['priceetag']=p,t,note,et
    else: print("WARN missing", nid)

d["meta"]["version"]="1.8-l3priceaxes"
out=json.dumps(d,ensure_ascii=False,indent=2);json.loads(out)
open(P,"w").write(out+"\n")
print("L3 price axes set for:", ", ".join(DATA.keys()))
