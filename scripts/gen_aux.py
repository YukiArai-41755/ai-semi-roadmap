#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

# ---------- TREND PAGES ----------
TREND_BODY = {
 "glass": ("""
<p class="lead">一つの材料が複数レイヤーを縦串で変容させる典型。ガラスは「層」ではなく「層内技術 ∩ 横断トレンド」として二重に存在する。</p>
<div class="callout invest"><span class="c-tag">投資テーゼ</span>
2026がR&D→パイロット/認定の元年。<span class="etag fact">fact</span> Absolicsがジョージア工場でAMD向け量産サンプル供給、IntelがEMIB+ガラスコア実証(NEPCON 2026)。
<span class="etag spec">spec</span> ハイエンドAIでの本格採用は基板で2027、インターポーザで2028-2029。素材・装置(TGV/PR/めっき)の川上に妙味。
</div>
<h2>どのレイヤーをどう変容させるか</h2>
<div class="tbl-wrap"><table><thead><tr><th>レイヤー</th><th>変容</th><th>関連ノード</th></tr></thead><tbody>
<tr><td>L3 パッケージ</td><td>有機コア(CCL)→ガラスコア基板、Siインターポーザ→ガラスインターポーザ(CoPoS)</td><td><a href="../cards/glass-sub.html">ガラスコア基板</a> / <a href="../cards/glass-int.html">ガラスインターポーザ</a></td></tr>
<tr><td>L5 演算</td><td>低CTE・高平坦で超大型パッケージ(複数レチクル級)が可能に。Rubin以降の集積限界を緩和</td><td>L5で詳述予定</td></tr>
<tr><td>L4 メモリ</td><td>寸法安定性がHBM高段積み(16-Hi超)・微細バンプを支える</td><td>L4で詳述予定</td></tr>
<tr><td>光化(交差)</td><td>基板内に光導波路を形成可能 → CPOと好相性。最も投資的に面白い交差点</td><td><a href="optical.html">光化トレンド</a></td></tr>
</tbody></table></div>
<h2>淘汰されるもの</h2>
<div class="callout warn"><span class="c-tag">死ぬテーマ</span><span class="etag infer">infer</span> 有機ABF基板はハイエンドで部分置換(中位以下は存続)。味の素のABF独占ポジションへの長期的逆風。</div>
""", ["glass-sub","glass-int","m-tgv","m-ccl","m-abf"]),

 "optical": ("""
<p class="lead">電気I/Oを光に置換する破壊的トレンド。パッケージ・スケールアップ・スケールアウトを横断する。CPOは独立レイヤーにするには薄いが、串刺しトレンドとしての重要性は高い、という非対称性を持つ。</p>
<div class="callout invest"><span class="c-tag">投資テーゼ</span><span class="etag spec">spec</span> 帯域密度と消費電力の限界が電気SerDesに迫る中、CPO/シリコンフォトニクスへの移行が2027-2030の焦点。<a href="../cards/glass-int.html">ガラスインターポーザ</a>の光導波路統合が鍵。詳細はL6/L7で展開予定。</div>
<h2>交差するレイヤー</h2>
<div class="tbl-wrap"><table><thead><tr><th>レイヤー</th><th>論点</th></tr></thead><tbody>
<tr><td>L3 パッケージ</td><td>光エンジンの共パッケージ化、ガラス基板内導波路</td></tr>
<tr><td>L6 スケールアップ</td><td>ラック内の低レイテンシ光リンク</td></tr>
<tr><td>L7 スケールアウト</td><td>CPOスイッチ、光トランシーバの置換</td></tr>
</tbody></table></div>
""", ["glass-int"]),

 "system": ("""
<p class='lead'>ラック/ポッドを1台の計算機として設計する潮流(NVL72 / Helios系)。電力・冷却・インターコネクト・演算が交差し、CapExが最も集中する結節点。「ラックが新たな計算単位」。</p>
<div class='callout invest'><span class='c-tag'>投資テーゼ</span><span class='etag fact'>fact</span> NVIDIA NVL72(72GPU/260TB/s)・AMD Helios(72GPU)が「巨大な単一GPU」を志向。<span class='etag infer'>infer</span> 競争軸が単体チップからラック設計(給電・冷却・結合の協調)へ移り、システム統合力が参入障壁化。</div>
<h2>交差するレイヤー</h2>
<div class='tbl-wrap'><table><thead><tr><th>レイヤー</th><th>論点</th><th>関連</th></tr></thead><tbody>
<tr><td>L1 電力・冷却</td><td>600kW-1MWラックの給電・冷却協調設計</td><td><a href='../layers/l1-power-cooling.html'>L1</a> / <a href='../cards/hvdc.html'>800V HVDC</a></td></tr>
<tr><td>L5 演算</td><td>CPU+GPUスーパーチップ、ラック単位の最適化</td><td><a href='../cards/vera-cpu.html'>Vera/EPYC統合</a></td></tr>
<tr><td>L6 スケールアップ</td><td>NVLink/UALinkでラックを1GPU化</td><td><a href='../cards/nvlink.html'>NVLink</a> / <a href='../cards/ualink.html'>UALink</a></td></tr>
</tbody></table></div>
<div class='callout warn'><span class='c-tag'>見解</span><span class='etag stance'>stance</span> このトレンドの勝者は単体性能でなく「ラック全体を協調設計できる統合力」を持つ者。NVIDIAの真の堀はGPUでなくフルスタック統合にある。</div>
""", []),
 "memory-centric": ("""
<p class='lead'>演算でなくメモリ帯域・容量が律速になる中での再設計。HBMの高積層化、ベースダイのロジック統合、SOCAMM/CXLによる階層化とプーリング。「メモリの壁」への多層的応答。</p>
<div class='callout invest'><span class='c-tag'>投資テーゼ</span><span class='etag fact'>fact</span> 推論のKVキャッシュは帯域律速。SRAM(L2キャッシュ)のスケーリング頭打ちがメモリ依存を強める。<span class='etag infer'>infer</span> メモリ階層がHBM単層→HBM/SOCAMM/DDR5/CXLの多層へ。価値がDRAM三寡占+TSMC(ベースダイ)に集中。</div>
<h2>交差するレイヤー</h2>
<div class='tbl-wrap'><table><thead><tr><th>レイヤー</th><th>論点</th><th>関連</th></tr></thead><tbody>
<tr><td>L4 メモリ</td><td>HBM4高積層・カスタムベースダイ・SOCAMM・CXL</td><td><a href='../cards/hbm4.html'>HBM4</a> / <a href='../cards/cxl.html'>CXL</a> / <a href='../cards/socamm.html'>SOCAMM2</a></td></tr>
<tr><td>L3 パッケージ</td><td>HBMをダイ直上に積むハイブリッドボンディング</td><td><a href='../materials/m-hbond.html'>HB</a></td></tr>
<tr><td>L5 演算</td><td>ウェハスケール(オンチップSRAM)でメモリの壁を物理回避</td><td><a href='../cards/cerebras.html'>Cerebras</a></td></tr>
</tbody></table></div>
<div class='callout warn'><span class='c-tag'>見解</span><span class='etag stance'>stance</span> 「メモリの壁」は単一技術で超えられない。HBM(近接)・SOCAMM(中間)・CXL(プール)・オンチップSRAM(Cerebras)の各層がそれぞれの解——投資は単一でなく階層全体に分散すべき。</div>
""", []),
 "power": ("""
<p class='lead'>電力がAIスケーリングの最終律速。48V→800V HVDC給電、液冷の高度化、そして電力供給そのもの(系統・SMR)の制約。「チップをどう作るか」から「電気をどう確保するか」へ。</p>
<div class='callout invest'><span class='c-tag'>投資テーゼ</span><span class='etag fact'>fact</span> ラック電力は3年で25倍(40kW→600kW-1MW)。<span class='etag stance'>stance</span> 最終的なボトルネックはシリコンでなく電力可用性——系統接続キュー・SMR・立地が事業規模を決める。GaN/SiC・電源IC・冷却(CDU/マイクロ流体)の川上に妙味。</div>
<h2>交差するレイヤー</h2>
<div class='tbl-wrap'><table><thead><tr><th>レイヤー</th><th>論点</th><th>関連</th></tr></thead><tbody>
<tr><td>L1 電力・冷却</td><td>800V HVDC・液冷・電力供給(SMR/系統/BESS)</td><td><a href='../cards/hvdc.html'>800V HVDC</a> / <a href='../cards/power-supply.html'>電力供給</a></td></tr>
<tr><td>L5 演算</td><td>2300W級TDPチップ、電力性能比の競争</td><td><a href='../cards/rubin.html'>Rubin</a></td></tr>
<tr><td>L6 スケールアップ</td><td>CPOで電気I/Oの消費電力(30W/port)を削減</td><td><a href='../cards/cpo.html'>CPO</a></td></tr>
</tbody></table></div>
<div class='callout warn'><span class='c-tag'>見解</span><span class='etag stance'>stance</span> 電力制約は他の全レイヤーの上限を決める「メタ制約」。微細化・パッケージ・メモリがいくら進んでも、電気と熱を捌けなければ展開できない。2027-2030で最も効く投資テーマ。</div>
""", []),
}

def link_node(nid):
    nm = next((x for x in G["nodes"] if x["id"]==nid), None)
    if nm:
        sub = "materials" if nm.get("kind")=="material" else "cards"
        return f'<a href="../{sub}/{nid}.html">{nm["name"]}</a>'
    return nid

for t in G["trends"]:
    body, related = TREND_BODY.get(t["slug"], ("<p>準備中</p>",[]))
    rel_html = ""
    if related:
        rel_html = '<h2>関連カード</h2><div class="legend">' + "".join(
            f'<span class="li">▸ {link_node(r)}</span>' for r in related) + '</div>'
    main = f'<div class="eyebrow">トレンド軸 (横串)</div><h1>{t["name"]}</h1>{body}{rel_html}'
    out = page("..", t["name"], t["slug"], [("トレンド軸",None),(t["name"],None)], main)
    open(os.path.join(ROOT,"trends",f'{t["slug"]}.html'),"w").write(out)
print("wrote", len(G["trends"]), "trend pages")

# ---------- STUB LAYER PAGES ----------
for L in G["layers"]:
    if L.get("status")=="done": continue
    main = f"""<div class="eyebrow">LAYER {L["num"]} / 縦階層</div>
<h1>{L["name"]}</h1>
<div class="callout"><span class="c-tag">準備中</span>
このレイヤーはリファレンス実装(L3)のテンプレートに沿って順次構築されます。L3で確定した構造——二系統分割・部材ノード・旗艦SVG断面・ホバー解説・3ビュー連携——を同じ型で流し込みます。
</div>
<p>先に <a href="l3-packaging.html">L3 先端パッケージ</a> が完成形リファレンスとして閲覧可能です。</p>
<div class="viewbar"><a href="l3-packaging.html" class="primary">▸ L3 リファレンスを見る</a><a href="../views/tree.html">▸ 全体ツリー</a></div>
"""
    out = page("..", f'L{L["num"]} {L["name"]}', L["slug"], [("レイヤー",None),(f'L{L["num"]} {L["name"]}',None)], main)
    open(os.path.join(ROOT,"layers",f'{L["slug"]}.html'),"w").write(out)
print("wrote stub layer pages")

# ---------- GLOSSARY ----------
rows=""
for x in sorted(G["nodes"], key=lambda n:(n.get("kind",""),n["id"])):
    if x.get("stub"): continue
    sub = "materials" if x.get("kind")=="material" else "cards"
    kind = "部材" if x.get("kind")=="material" else "技術"
    rows += f'<tr><td><a href="{sub}/{x["id"]}.html">{x["name"]}</a></td><td>{x.get("full","")}</td><td>{kind}</td><td>{x.get("def","")[:80]}…</td></tr>'
gmain = f"""<div class="eyebrow">索引</div><h1>用語・部材インデックス</h1>
<p class="lead">全ノードの一覧。技術カード・部材カードへの入口。</p>
<div class="tbl-wrap"><table><thead><tr><th>名称</th><th>正式名</th><th>区分</th><th>概要</th></tr></thead><tbody>{rows}</tbody></table></div>"""
open(os.path.join(ROOT,"glossary.html"),"w").write(page(".", "用語インデックス", "", [("用語・部材インデックス",None)], gmain))
print("wrote glossary.html")
