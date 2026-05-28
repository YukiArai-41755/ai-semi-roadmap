#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page
from layer_common import n, L, metric_bar, term, node_block, pager

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = ".."  # pages in /layers reach root via ..

def svg_fig(fname, caption):
    svg = open(os.path.join(ROOT,"assets","svg",fname)).read()
    return f'<figure class="schematic">{svg}<figcaption>{caption}</figcaption></figure>'

# ---- assemble main ----
l3 = L("L3")
subs = {s["id"]: s for s in l3["sub_systems"]}

intro = f"""
<div class="eyebrow">LAYER 3 / 縦階層</div>
<h1>{l3["name"]}</h1>
<p class="lead">{l3["summary"]}</p>
<div class="callout invest"><span class="c-tag">投資判断の要点</span>
ここは<strong>AIアクセラレータ供給の最大ボトルネック</strong>。トランジスタ微細化(L2)が鈍化する中、性能スケーリングの主役が「いかに多くのダイとHBMを1パッケージに高密度集積するか」へ移った。{term("CoWoS","cowos")}の生産能力が事実上GPU出荷量の上限を決め、{term("ガラス基板","glass-sub")}が次の構造変化点になる。
<span class="etag fact">fact</span> CoWoS需給 / <span class="etag spec">spec</span> ガラス採用時期
</div>

<h2>このレイヤーの二系統</h2>
<p>L3は物理的に異なる二つの系統に分かれる。混同しやすいが、技術スタックも投資プレイヤーも別物。</p>
<div class="tbl-wrap"><table>
<thead><tr><th>系統</th><th>役割</th><th>代表技術</th><th>接合の鍵</th></tr></thead>
<tbody>
<tr><td><strong>{subs["L3-A"]["name"]}</strong></td><td>ダイをZ方向に重ね、配線距離を最短化</td><td>{term("SoIC","soic")} / {term("Foveros","foveros")} / {term("UCIe-3D","ucie")}</td><td>{term("ハイブリッドボンディング","m-hbond")}</td></tr>
<tr><td><strong>{subs["L3-B"]["name"]}</strong></td><td>ダイを平面で繋ぐ配線層と、それを載せる基板</td><td>{term("CoWoS","cowos")} / {term("EMIB","emib")} / {term("ガラスコア基板","glass-sub")} / {term("ガラスインターポーザ","glass-int")}</td><td>{term("インターポーザ","cowos")}・{term("TGV","m-tgv")}</td></tr>
</tbody></table></div>

<h2>断面で理解する物理的実装</h2>
<p>「どの部材がどの層にいるか」は断面でしか伝わらない。基準図では、{term("CCL","m-ccl")}(基板の芯)と{term("ABF","m-abf")}(その上下のビルドアップ絶縁膜)の上下関係、そして{term("MLCC","m-mlcc")}が配線層ではなく裏面(ダイ直下=LSC)に載る受動部品であることに注目。各部材にカーソルを合わせると解説と部材カードへのリンクが出る。</p>
{svg_fig("fullstack.svg", "図1: パッケージ基板フルスタック断面(基準図)。下からPCB→BGA→[ABF/CCL/ABF基板]→C4→Siインターポーザ→μバンプ→ダイ+HBM→TIM→IHS。右ブラケットが二系統の担当範囲。MLCCは基板裏面(LSC)。")}
"""

l3a = f"""
<h2 id="L3-A">系統A: 垂直積層 (3D)</h2>
<p>ダイを縦に積む。鍵は{term("ハイブリッドボンディング","m-hbond")}——はんだバンプを介さず銅-銅を直接接合し、マイクロバンプを大きく上回る配線密度・帯域を得る。ピッチ競争(TSMC 6μm量産 → 3μm目標、Intel サブ5μm)がこの系統の主戦場。</p>
{svg_fig("hbm-stack.svg","図2: HBM内部スタック断面。DRAMコアダイを多段積層し、TSVが全層を貫通、最下層のベースロジックダイ(PHY)に集約。HBM自体がこの系統の量産3D実装例。")}
{node_block("soic")}
{node_block("foveros")}
{node_block("ucie")}
"""

l3b = f"""
<h2 id="L3-B">系統B: 水平配線基盤 (2.5D / 基板)</h2>
<p>ダイを平面で繋ぐ。インターポーザ(配線の盤)と基板(それを載せる土台)の二段で考える。ここに{term("ガラス","glass-sub")}が二方向から侵入する——基板コアの{term("CCL置換","m-ccl")}としてと、{term("Siインターポーザの置換","glass-int")}として。タイムラインも投資妙味も別なので分けて見る。</p>
<div class="callout invest"><span class="c-tag">基板の『素材の素材』(見落としがちな川上)</span>
基板の最上流に、独占×完売の素材が潜む。{term("CCL","m-ccl")}はさらに3素材に分解できる: {term("T-glass(ガラスクロス)","m-glasscloth")}(補強繊維、コスト19%、Nittobo ~90%独占で2026最大級のボトルネック)、{term("HVLP銅箔","m-copperfoil")}(導体、42%)、樹脂(26%)。<span class="etag stance">stance</span> T-glassはNANDと同じ「演算しない地味な川上」だが、独占純度はABFフィルム級。基板を語るならフィルム(味の素)とガラスクロス(Nittobo)の二つの日本企業の独占を見るべき。</div>
{svg_fig("interposer-compare.svg","図3: インターポーザ/基板 3方式比較(同一スケール)。Siインターポーザ(現行)/ガラスインターポーザ(CoPoS, 将来)/有機ABF基板のみ(低コスト)。ガラスはTGVで貫通し低損失・低CTE・大面積が強み。")}
{node_block("cowos")}
{node_block("emib")}
{node_block("org-sub")}
{node_block("glass-sub")}
{node_block("glass-int")}
{node_block("copos-note")}

<h2>系統B内の世代交代(誰が誰を殺すか)</h2>
<div class="callout warn"><span class="c-tag">淘汰のベクトル</span>
<span class="etag infer">infer</span> 有機ABF基板はハイエンドAIで{term("ガラスコア基板","glass-sub")}に部分置換される(2027-2030)。ただし中位以下では存続。
<span class="etag spec">spec</span> Siインターポーザ(CoWoS-S)は大面積領域で{term("ガラスインターポーザ/CoPoS","glass-int")}に置換(2028-2029量産見込)。CoWoS-L(RDL+ブリッジ)は当面併存。
出典の幅: ガラス商用化時期は「late 2026」(基板)〜「2028-2029」(インターポーザ)と情報源で割れており、ここでは用途別に分けて記載。
</div>
"""

refpanel = """
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin-bottom:8px">このページの図版</div>
<a href="#" style="display:block;margin-bottom:6px">図1 フルスタック断面</a>
<a href="#L3-A" style="display:block;margin-bottom:6px">図2 HBMスタック</a>
<a href="#L3-B" style="display:block;margin-bottom:14px">図3 インターポーザ比較</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">関連レイヤー</div>
<a href="../layers/l4-memory.html" style="display:block;margin-bottom:6px">L4 メモリ (HBM) ·準備中</a>
<a href="../layers/l5-compute.html" style="display:block;margin-bottom:6px">L5 演算チップ ·準備中</a>
<a href="../trends/glass.html" style="display:block;margin-bottom:6px">トレンド: ガラス化</a>
<a href="../trends/optical.html" style="display:block;margin-bottom:6px">トレンド: 光化</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">凡例</div>
<div style="font-size:11px;line-height:1.7">
<span class="etag fact">fact</span> 確立事実<br>
<span class="etag infer">infer</span> 推論<br>
<span class="etag spec">spec</span> 予測/不確実<br>
<span class="etag stance">stance</span> 見解
</div>
"""

pager = """
<div class="pager">
  <a href="l2-process.html"><span class="dir">◂ 前のレイヤー</span>L2 製造プロセス・基盤</a>
  <a href="l4-memory.html" style="text-align:right"><span class="dir">次のレイヤー ▸</span>L4 メモリ</a>
</div>
"""

main = intro + l3a + l3b + pager
out = page(REL, "L3 先端パッケージ", "l3-packaging",
           [("レイヤー", None), ("L3 先端パッケージ・チップレット統合", None)],
           main, refpanel)
os.makedirs(os.path.join(ROOT,"layers"), exist_ok=True)
open(os.path.join(ROOT,"layers","l3-packaging.html"),"w").write(out)
print("wrote layers/l3-packaging.html", len(out), "bytes")
