#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page
from layer_common import n, L, term, node_block, pager

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = ".."

def svg_fig(fname, caption):
    svg = open(os.path.join(ROOT,"assets","svg",fname)).read()
    return f'<figure class="schematic">{svg}<figcaption>{caption}</figcaption></figure>'

l6 = L("L6")
subs = {s["id"]: s for s in l6["sub_systems"]}

intro = f"""
<div class="eyebrow">LAYER 6 / 縦階層</div>
<h1>{l6["name"]}</h1>
<p class="lead">{l6["summary"]}</p>
<div class="callout invest"><span class="c-tag">投資判断の要点</span>
ラックを1台の巨大GPUに見せる結合層。<span class="etag fact">fact</span> scale-up配線のTAMは既にscale-out(L7)を凌駕——SerDes速度とドメインサイズの拡大で最速成長。
<span class="etag infer">infer</span> 主軸は{term("NVLink","nvlink")}(独自)対{term("UALink","ualink")}(オープン)の規格戦争。NVIDIAはNVLink Fusionで部分開放し両睨み。
<span class="etag spec">spec</span> 銅はラック内で2028頃まで優位、クロスラック(576GPU=8×NVL72)で{term("CPO","cpo")}へ移行が始まる。
</div>

<h2>scale-up と scale-out の境界</h2>
<p>混同しやすいが別レイヤー。<strong>scale-up(L6)</strong>=ラック内・ノード内のGPU間を最短・最大帯域で結ぶ(NVLink/UALink)。<strong>{term("scale-out(L7)","cpo")}</strong>=ラック・クラスタ間をEthernetやInfiniBandで結ぶ。CPOは両者に効くが、TAM的にも導入順としてもscale-upが先行する。</p>
<div class="tbl-wrap"><table>
<thead><tr><th>系統</th><th>性格</th><th>代表</th><th>競争軸</th></tr></thead>
<tbody>
<tr><td><strong>{subs["L6-A"]["name"]}</strong></td><td>独自・最高性能・囲い込み</td><td>{term("NVLink 6 / Fusion","nvlink")}</td><td>帯域・エコシステム</td></tr>
<tr><td><strong>{subs["L6-B"]["name"]}</strong></td><td>オープン・マルチベンダ・低コスト</td><td>{term("UALink / Infinity Fabric","ualink")}</td><td>標準化・コスト</td></tr>
<tr><td><strong>{subs["L6-C"]["name"]}</strong></td><td>銅の物理限界を超える光化</td><td>{term("CPO","cpo")}</td><td>距離・損失・電力</td></tr>
</tbody></table></div>
"""

compare = f"""
<h2>規格戦争のポジショニング</h2>
<p><span class="etag spec">spec</span> 数値は公表/報道ベース。NVLinkが性能で先行、UALinkがオープン性とコストで追う、CPOが次の地殻変動。</p>
<div class="tbl-wrap"><table>
<thead><tr><th>項目</th><th>NVLink 6 (独自)</th><th>UALink 1.0/2.0 (オープン)</th></tr></thead>
<tbody>
<tr><td>帯域</td><td class="cell-best">3.6 TB/s/GPU (400G SerDes/lane)</td><td>200 GT/s/lane</td></tr>
<tr><td>最大scale-up</td><td>144 GPU (Rubin) → 576 (Ultra, 2027)</td><td class="cell-best">最大1,024 GPU</td></tr>
<tr><td>レイテンシ/到達</td><td>銅 &lt;1m</td><td>&lt;4m / &lt;1μs / 1-4ラック</td></tr>
<tr><td>陣営</td><td>NVIDIA(+Marvell $2B)</td><td class="cell-best">AMD/Intel/Google/MS/Meta/Broadcom/Apple</td></tr>
<tr><td>商用時期</td><td class="cell-best">出荷中(NVL72)</td><td>初スイッチ Q4 2026(Upscale AI)</td></tr>
<tr><td>戦略</td><td>独自で囲い込み→Fusionで部分開放</td><td>業界標準でコスト優位・脱NVIDIA</td></tr>
</tbody></table></div>

<h2>銅から光へ: CPOの位置づけ</h2>
<p>scale-upは長らく銅が合理的だった。だがNVLink 6で3.6TB/s/GPU(Rubinで14.4Tbit/s)に達し、クロスラック化で銅の電気損失(200Gb/sで約22dB)・消費電力(30W/port)が限界に。{term("CPO","cpo")}は光変換エンジンをスイッチASIC直近に共パッケージ化して回避する。NVIDIAはGTC2026でFeynman世代のNVLink 8 CPOスイッチ(2028〜)を表明、銅と併存させる。</p>
{svg_fig("cpo-stack.svg","図: CPO(共パッケージ光)断面。スイッチ/演算ダイの両脇に光エンジンを共パッケージ化し電気I/Oを光に置換。ガラスインターポーザは基板内に光導波路を形成できるためCPOと好相性——L3のガラス化トレンドと直結する。")}

<div class="callout warn"><span class="c-tag">レイヤー連結: 光化トレンドの主戦場</span>
<span class="etag fact">fact</span> CPOはTSMC {term("SoIC","soic")}(3Dハイブリッドボンディング)で実装され、{term("ガラスインターポーザ","glass-int")}の光導波路統合と好相性——L6はL3パッケージ技術と分かちがたい。
<span class="etag infer">infer</span> CPO TAMはscale-up主導でscale-outを上回る(SemiAnalysis)。普及率~35%(2030, TrendForce)。
<span class="etag stance">stance</span> 投資的には「規格戦争の勝者」より「光化の不可避性」に賭ける方が確度が高い——SoIC/ガラス/光エンジンの川上に妙味。
</div>
"""

sysA = f"""
<h2 id="L6-A">系統A: 独自ファブリック (NVLink系)</h2>
{node_block("nvlink")}
"""
sysB = f"""
<h2 id="L6-B">系統B: オープン規格 (UALink系)</h2>
<p>「ラックを1台のGPUに見せる」をオープン標準で実現。NVIDIA囲い込みへの業界の集団的回答。AMDはInfinity Fabricからここへ転換。</p>
{node_block("ualink")}
"""
sysC = f"""
<h2 id="L6-C">系統C: 光化 (CPO / 光scale-up)</h2>
<p>規格戦争(銅)の上位で進む地殻変動。どの規格が勝っても、物理層が銅から光へ移る流れは不可逆。</p>
{node_block("cpo")}
"""

refpanel = """
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin-bottom:8px">系統</div>
<a href="#L6-A" style="display:block;margin-bottom:6px">A NVLink系</a>
<a href="#L6-B" style="display:block;margin-bottom:6px">B UALink系</a>
<a href="#L6-C" style="display:block;margin-bottom:14px">C CPO/光化</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">連結レイヤー</div>
<a href="../layers/l5-compute.html" style="display:block;margin-bottom:6px">L5 演算 (NVL72成立)</a>
<a href="../layers/l3-packaging.html" style="display:block;margin-bottom:6px">L3 パッケージ (SoIC/ガラス)</a>
<a href="../layers/l7-scaleout.html" style="display:block;margin-bottom:6px">L7 スケールアウト ·準備中</a>
<a href="../trends/optical.html" style="display:block;margin-bottom:6px">トレンド: 光化</a>
<a href="../trends/system.html" style="display:block;margin-bottom:6px">トレンド: システム統合</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">凡例</div>
<div style="font-size:11px;line-height:1.7">
<span class="etag fact">fact</span> 確立事実<br>
<span class="etag infer">infer</span> 推論<br>
<span class="etag spec">spec</span> 予測/不確実<br>
<span class="etag stance">stance</span> 見解
</div>
"""

main = intro + compare + sysA + sysB + sysC + pager(("l5-compute","L5 演算チップ"), ("l7-scaleout","L7 スケールアウト"))
out = page(REL, "L6 スケールアップ", "l6-scaleup",
           [("レイヤー", None), ("L6 スケールアップ・インターコネクト", None)], main, refpanel)
open(os.path.join(ROOT,"layers","l6-scaleup.html"),"w").write(out)
print("wrote layers/l6-scaleup.html", len(out), "bytes")
