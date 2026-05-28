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

l4 = L("L4")
subs = {s["id"]: s for s in l4["sub_systems"]}

intro = f"""
<div class="eyebrow">LAYER 4 / 縦階層</div>
<h1>{l4["name"]}</h1>
<p class="lead">{l4["summary"]}</p>
<div class="callout invest"><span class="c-tag">投資判断の要点</span>
AIスケーリングの真の律速は<strong>メモリの壁</strong>。{term("HBM4","hbm4")}で帯域は跳ねるが、性能を決めるのは16-Hiスタックの歩留りと{term("ベースロジックダイ","hbm-basedie")}の統合度。
<span class="etag fact">fact</span> 供給はSK hynix/Samsung/Micronの三寡占＋TSMC(ベースダイ)に集中=構造的チョークポイント。
<span class="etag infer">infer</span> 差別化軸が「容量・帯域」から「ロジック統合度(カスタムHBM)」へ移行中。
<span class="etag stance">stance</span> 2026年の不足の実体は2023年型の"チップ不足"でなく<strong>16-Hi積層と歩留りの問題</strong>。
</div>

<h2>このレイヤーの三系統</h2>
<div class="tbl-wrap"><table>
<thead><tr><th>系統</th><th>役割</th><th>代表</th><th>競争軸</th></tr></thead>
<tbody>
<tr><td><strong>{subs["L4-A"]["name"]}</strong></td><td>広帯域メモリ本体</td><td>{term("HBM4","hbm4")} / {term("HBM4E","hbm4e")}</td><td>帯域・容量・16-Hi歩留り</td></tr>
<tr><td><strong>{subs["L4-B"]["name"]}</strong></td><td>スタック最下層のロジック統合</td><td>{term("ベースダイ / C-HBM4E","hbm-basedie")}</td><td>ロジックノード・カスタム設計</td></tr>
<tr><td><strong>{subs["L4-C"]["name"]}</strong></td><td>ラック規模のメモリ拡張</td><td>{term("CXL プーリング","cxl")}</td><td>容量プール・コヒーレンス</td></tr>
</tbody></table></div>

<h2>断面で理解する: HBMはなぜ「積む」のか</h2>
<p>HBMはDRAMコアダイを{term("TSV","m-tsv")}で垂直貫通させ多段積層し、最下層の{term("ベースロジックダイ","hbm-basedie")}に集約する。広帯域の源泉は2048bitの広いインタフェースを短い垂直配線で実現する点にある。16層への高積層化で熱密度とTSV整列精度が律速になり、接合は{term("MR-MUF","hbm4")}から{term("ハイブリッドボンディング","m-hbond")}へ移行していく。</p>
{svg_fig("hbm-stack.svg","図: HBM内部スタック断面(16-Hi例)。DRAMコアダイを多段積層しTSVが全層貫通、最下層のベースロジックダイ(PHY/コントローラ)に集約。HBM4ではこのベースダイがTSMC先端ロジックノードで製造され、メモリを共プロセッサ化する。")}
"""

# triopoly supplier comparison — the L4 centerpiece
suppliers = f"""
<h2>三寡占の競争構図 (HBM4世代)</h2>
<p>NVIDIAが事実上の唯一の初期顧客=ゲートキーパー。<span class="etag spec">spec</span> 数値は公表/報道ベースで変動余地あり。歩留りを最も安定させた者がNVIDIA受注の大半を得る「歩留り戦争」。</p>
<div class="tbl-wrap"><table>
<thead><tr><th>項目</th><th>SK hynix</th><th>Samsung</th><th>Micron</th></tr></thead>
<tbody>
<tr><td>市場ポジション</td><td class="cell-best">リーダー(>50%シェア)</td><td>垂直統合(自社ファウンドリ)</td><td>効率特化・2026完売</td></tr>
<tr><td>16-Hi接合</td><td class="cell-best">MR-MUF(歩留り優位)</td><td>ハイブリッドボンディング先行(歩留り~10%)</td><td>1-gamma / 自社CMOSベースダイ</td></tr>
<tr><td>DRAMプロセス</td><td>—</td><td>1c(効率+40%)</td><td>1-gamma</td></tr>
<tr><td>帯域/効率の主張</td><td>16-Hi 48GB @11.7Gbps</td><td>1c効率</td><td class="cell-best">2.8TB/s・最高効率</td></tr>
<tr><td>戦略</td><td>TSMC "One Team" 連合</td><td>垂直統合のコスト優位</td><td>推論市場(電力重視)に照準</td></tr>
<tr><td>量産時期</td><td class="cell-best">MP Q3 2026</td><td>HB 16層HBM4Eは2028目標</td><td>SK hynixよりやや後</td></tr>
</tbody></table></div>

<div class="callout warn"><span class="c-tag">レイヤー連結: メモリの壁とアーキ転換</span>
<span class="etag fact">fact</span> HBM4のベースダイがTSMC先端ノード製造に移ったことで、L4はL2(プロセス)・L3({term("ハイブリッドボンディング","m-hbond")})・L5({term("Rubin","rubin")}との共設計)と分かちがたく結合した。
<span class="etag infer">infer</span> 「メモリの壁」を単体HBMで超えるのは限界——{term("CXLプーリング","cxl")}でラック規模に逃がす{term("メモリ中心アーキテクチャ","T-mem")}が次の主戦場。
</div>
"""

sysA = f"""
<h2 id="L4-A">系統A: HBM主系 (スタック)</h2>
{node_block("hbm4")}
{node_block("hbm4e")}
"""
sysB = f"""
<h2 id="L4-B">系統B: ベースダイ・カスタムHBM</h2>
<p>L4で最も投資的に面白い変化点。HBMが受動的記憶からロジックを抱えた共プロセッサへ変質する。ファウンドリ(TSMC)がメモリ価値連鎖に食い込む構造変化。</p>
{node_block("hbm-basedie")}
"""
sysC = f"""
<h2 id="L4-C">系統C: メモリ階層拡張 (NAND / CXL)</h2>
<p>HBMの外側を埋める階層。推論の長コンテキスト化でKVキャッシュ/RAGがHBM容量を超え、その溢れを{term("SOCAMM2","socamm")}・{term("エンタープライズSSD(NAND)","nand")}・{term("CXL","cxl")}が受ける。さらに{term("HBF","hbf")}がHBMとNANDの中間を埋めにくる。メモリは単層でなく帯域-容量-コストの連続体になった。</p>
{node_block("nand")}
{node_block("hbf")}
{node_block("socamm")}
{node_block("cxl")}
"""

refpanel = """
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin-bottom:8px">系統</div>
<a href="#L4-A" style="display:block;margin-bottom:6px">A HBM主系</a>
<a href="#L4-B" style="display:block;margin-bottom:6px">B ベースダイ/カスタム</a>
<a href="#L4-C" style="display:block;margin-bottom:14px">C CXL拡張</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">連結レイヤー</div>
<a href="../layers/l3-packaging.html" style="display:block;margin-bottom:6px">L3 パッケージ (HB接合)</a>
<a href="../layers/l5-compute.html" style="display:block;margin-bottom:6px">L5 演算 (Rubin co-design)</a>
<a href="../layers/l2-process.html" style="display:block;margin-bottom:6px">L2 プロセス (ベースダイ) ·準備中</a>
<a href="../trends/memory-centric.html" style="display:block;margin-bottom:6px">トレンド: メモリ中心アーキ</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">凡例</div>
<div style="font-size:11px;line-height:1.7">
<span class="etag fact">fact</span> 確立事実<br>
<span class="etag infer">infer</span> 推論<br>
<span class="etag spec">spec</span> 予測/不確実<br>
<span class="etag stance">stance</span> 見解
</div>
"""

main = intro + suppliers + sysA + sysB + sysC + pager(("l3-packaging","L3 先端パッケージ"), ("l5-compute","L5 演算チップ"))
out = page(REL, "L4 メモリ", "l4-memory",
           [("レイヤー", None), ("L4 メモリ", None)], main, refpanel)
open(os.path.join(ROOT,"layers","l4-memory.html"),"w").write(out)
print("wrote layers/l4-memory.html", len(out), "bytes")
