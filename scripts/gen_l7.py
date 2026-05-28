#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page
from layer_common import n, L, term, node_block, pager

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = ".."

l7 = L("L7")
subs = {s["id"]: s for s in l7["sub_systems"]}

def svg_fig(fname, caption):
    svg = open(os.path.join(ROOT,"assets","svg",fname)).read()
    return f'<figure class="schematic">{svg}<figcaption>{caption}</figcaption></figure>'

intro = f"""
<div class="eyebrow">LAYER 7 / 縦階層</div>
<h1>{l7["name"]}</h1>
<p class="lead">{l7["summary"]}</p>
<div class="callout invest"><span class="c-tag">投資判断の要点</span>
ラック・クラスタ間を結ぶ後方網。10万XPU超のクラスタを成立させる。
<span class="etag fact">fact</span> 主導権は{term("InfiniBand","infiniband")}(独自・低レイテンシ)対{term("Ethernet/UEC","ethernet-uec")}(オープン)。
<span class="etag infer">infer</span> Ethernetが800G普及でInfiniBandを逆転する見込み(学習=IB / 推論=Ethernet の住み分け)。
<span class="etag fact">fact</span> 800G→1.6T(2027)→3.2T(2030)と世代ごとに電気層を総取り替え——歴史上最速の更新サイクル。{term("スイッチシリコン","switch-silicon")}が川上の要。
</div>

<h2>このレイヤーの三系統</h2>
<div class="tbl-wrap"><table>
<thead><tr><th>系統</th><th>性格</th><th>代表</th><th>競争軸</th></tr></thead>
<tbody>
<tr><td><strong>{subs["L7-A"]["name"]}</strong></td><td>独自・最低レイテンシ・学習向き</td><td>{term("InfiniBand","infiniband")}</td><td>レイテンシ・性能一貫性</td></tr>
<tr><td><strong>{subs["L7-B"]["name"]}</strong></td><td>オープン・マルチベンダ・推論向き</td><td>{term("Ethernet / UEC","ethernet-uec")}</td><td>標準化・コスト・供給柔軟性</td></tr>
<tr><td><strong>{subs["L7-C"]["name"]}</strong></td><td>ネットワークの心臓=スイッチASIC+光</td><td>{term("Tomahawk / Spectrum / CPO","switch-silicon")}</td><td>帯域(102.4Tbps級)・電力</td></tr>
</tbody></table></div>
{svg_fig("scaleup-scaleout.svg","図: scale-up(L6, 左)はラック内のGPUを全結合で密に繋ぐ(NVLink/UALink・銅)。scale-out(L7, 右)はラック/クラスタ間をスイッチ経由で繋ぐ(Ethernet/InfiniBand・光・10万GPU+)。同じ「GPUを繋ぐ」でも近distと遠distで別技術。")}
"""

compare = f"""
<h2>主導権争い: InfiniBand 対 Ethernet</h2>
<p><span class="etag spec">spec</span> 数値は公表/報道ベース。IBが性能で先行も、Ethernetが規模とコストとオープン性で逆転局面へ。</p>
<div class="tbl-wrap"><table>
<thead><tr><th>項目</th><th>InfiniBand (独自)</th><th>Ethernet / UEC (オープン)</th></tr></thead>
<tbody>
<tr><td>レイテンシ</td><td class="cell-best">1-2μs(ロスレス)</td><td>~5-10μs(改善中, UEC PDS)</td></tr>
<tr><td>現行速度</td><td>NDR 400G → XDR 800G</td><td>800G普及中 → 1.6T(2027)</td></tr>
<tr><td>主用途</td><td>学習クラスタ</td><td class="cell-best">推論・大規模(10万XPU+)</td></tr>
<tr><td>陣営</td><td>NVIDIA(+Spectrum-Xで両睨み)</td><td class="cell-best">AMD/Arista/Broadcom/Cisco/Meta/MS/Intel/HPE</td></tr>
<tr><td>規格性質</td><td>独自・ロックイン・高TCO</td><td class="cell-best">UEC 1.0 全層再構築・標準</td></tr>
<tr><td>趨勢</td><td>性能リーダーだが侵食</td><td class="cell-best">800G普及で逆転見込</td></tr>
</tbody></table></div>

<h2>スイッチシリコンの覇権争い</h2>
<p>規格の上で実際に帯域を運ぶのは大容量スイッチASIC。<span class="etag fact">fact</span> Broadcom Tomahawk 6が102.4Tbpsで先行出荷、NVIDIA Spectrum-X1600(102.4Tbps)は2026後半で約1年遅れ。各社CPO版を準備し、scale-out光化が{term("scale-up(L6)","cpo")}に次いで始まる。</p>

<div class="callout warn"><span class="c-tag">レイヤー連結: scale-up との対</span>
<span class="etag fact">fact</span> L7(scale-out=ラック間)はL6(scale-up=ラック内)と対をなす。Broadcom Thor Ultra等のNICはNVLinkと競合せず、ラックを出た先を担う。
<span class="etag infer">infer</span> {term("CPO","cpo")}はscale-up先行・scale-out追随。スイッチASICの光化で{term("ガラスインターポーザ","glass-int")}(L3)需要がさらに広がる。
<span class="etag stance">stance</span> 投資的には「IB vs Ethernet」の勝敗より、どちらも食う{term("スイッチシリコン","switch-silicon")}・光・SerDesの川上(Broadcom/Marvell/TSMC)が堅い。
</div>
"""

sysA = f"""
<h2 id="L7-A">系統A: InfiniBand</h2>
{node_block("infiniband")}
"""
sysB = f"""
<h2 id="L7-B">系統B: Ethernet / UEC</h2>
<p>「単一ベンダに依存しないAI網」を全層再構築で実現。NVIDIAすら創設メンバーとして参加する不可避の潮流。</p>
{node_block("ethernet-uec")}
"""
sysC = f"""
<h2 id="L7-C">系統C: スイッチシリコン・scale-out光</h2>
<p>規格戦争の勝敗を超えて、帯域を運ぶ実体。ここの川上(Broadcom/Marvell)が最も堅い投資対象。光化の鍵部材は{term("光エンジン","m-optengine")}。</p>
{node_block("switch-silicon")}
"""

refpanel = """
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin-bottom:8px">系統</div>
<a href="#L7-A" style="display:block;margin-bottom:6px">A InfiniBand</a>
<a href="#L7-B" style="display:block;margin-bottom:6px">B Ethernet/UEC</a>
<a href="#L7-C" style="display:block;margin-bottom:14px">C スイッチシリコン</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">連結レイヤー</div>
<a href="../layers/l6-scaleup.html" style="display:block;margin-bottom:6px">L6 スケールアップ (対をなす)</a>
<a href="../layers/l5-compute.html" style="display:block;margin-bottom:6px">L5 演算 (クラスタ)</a>
<a href="../layers/l3-packaging.html" style="display:block;margin-bottom:6px">L3 パッケージ (CPO/ガラス)</a>
<a href="../trends/optical.html" style="display:block;margin-bottom:6px">トレンド: 光化</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">凡例</div>
<div style="font-size:11px;line-height:1.7">
<span class="etag fact">fact</span> 確立事実<br>
<span class="etag infer">infer</span> 推論<br>
<span class="etag spec">spec</span> 予測/不確実<br>
<span class="etag stance">stance</span> 見解
</div>
"""

main = intro + compare + sysA + sysB + sysC + pager(("l6-scaleup","L6 スケールアップ"), ("l1-power-cooling","L1 施設・電力・冷却"))
out = page(REL, "L7 スケールアウト", "l7-scaleout",
           [("レイヤー", None), ("L7 スケールアウト・ネットワーク", None)], main, refpanel)
open(os.path.join(ROOT,"layers","l7-scaleout.html"),"w").write(out)
print("wrote layers/l7-scaleout.html", len(out), "bytes")
