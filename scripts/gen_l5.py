#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page
from layer_common import n, L, term, node_block, pager

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = ".."

l5 = L("L5")
subs = {s["id"]: s for s in l5["sub_systems"]}

intro = f"""
<div class="eyebrow">LAYER 5 / 縦階層</div>
<h1>{l5["name"]}</h1>
<p class="lead">{l5["summary"]}</p>
<div class="callout invest"><span class="c-tag">投資判断の要点</span>
L5は<strong>全レイヤーのボトルネックが集約する出口</strong>。性能の律速はもはや演算FLOPでなく、{term("HBM4","hbm4")}帯域と{term("CoWoS-L","cowos")}/HBM歩留り。
<span class="etag fact">fact</span> NVIDIA ~80%シェア(CUDA moat)だが、独自ASIC出荷は2026に+44.6%でGPU(+16.1%)を上回る成長。
<span class="etag fact">fact</span> Broadcom/Marvellが独自ASIC設計の8割超を担う隠れた要——「全社が自前チップ」の実体は「Broadcomと共同設計」。
<span class="etag infer">infer</span> 真の構図は「NVIDIA vs AMD」でなく多極化(GPU / 独自ASIC / 推論特化 / 中国勢)。
</div>

<h2>このレイヤーの五系統</h2>
<div class="tbl-wrap"><table>
<thead><tr><th>系統</th><th>性格</th><th>代表</th><th>競争軸</th></tr></thead>
<tbody>
<tr><td><strong>{subs["L5-A"]["name"]}</strong></td><td>汎用・ソフト資産</td><td>{term("Rubin","rubin")} / {term("MI400","mi400")}</td><td>CUDA・帯域・容量</td></tr>
<tr><td><strong>{subs["L5-B"]["name"]}</strong></td><td>自社WL特化・垂直統合</td><td>{term("Google TPU","tpu")} / {term("AWS Trainium","trainium")}</td><td>電力性能比・TCO・コスト破壊</td></tr>
<tr><td><strong>{subs["L5-C"]["name"]}</strong></td><td>decode帯域に特化</td><td>{term("Cerebras","cerebras")} / {term("SambaNova","sambanova")}</td><td>推論速度・メモリ局所性</td></tr>
<tr><td><strong>{subs["L5-D"]["name"]}</strong></td><td>規制下の内製・地政学</td><td>{term("Huawei / Alibaba","china-asic")}</td><td>内需・国産化・スケール</td></tr>
<tr><td><strong>{subs["L5-E"]["name"]}</strong></td><td>CPU+GPU密結合</td><td>{term("Vera / EPYC統合","vera-cpu")}</td><td>メモリ中心・システム統合</td></tr>
</tbody></table></div>
"""

compare = f"""
<h2>競争ポジショニング (2026世代)</h2>
<p><span class="etag spec">spec</span> 数値は各社公表/報道ベース。GPU2強の正面衝突と、ASIC/推論特化/中国勢の非対称な攻め筋。</p>
<div class="tbl-wrap"><table>
<thead><tr><th>項目</th><th>Rubin (R100)</th><th>MI455X</th><th>TPU Ironwood</th><th>Trainium3</th><th>Cerebras WSE-3</th></tr></thead>
<tbody>
<tr><td>プロセス</td><td>N3</td><td class="cell-best">N2</td><td>—</td><td>N3</td><td>5nm(ウェハ丸ごと)</td></tr>
<tr><td>メモリ</td><td>288GB HBM4</td><td class="cell-best">432GB HBM4</td><td>192GB HBM3e</td><td>144GB HBM3e</td><td>44GB on-chip SRAM</td></tr>
<tr><td>帯域</td><td>22.2TB/s</td><td>19.6TB/s</td><td>7.4TB/s</td><td>4.9TB/s</td><td class="cell-best">21PB/s(SRAM)</td></tr>
<tr><td>狙い</td><td>汎用・学習/推論</td><td>容量・オープン</td><td>成熟・外販開始</td><td class="cell-best">コスト破壊~50%安</td><td>decode推論2倍超</td></tr>
<tr><td>設計/製造</td><td>NVIDIA/TSMC</td><td>AMD/TSMC</td><td>Broadcom/TSMC</td><td>Annapurna/Marvell</td><td>Cerebras/TSMC</td></tr>
</tbody></table></div>

<div class="callout warn"><span class="c-tag">レイヤー連結: 歩留りが出荷を律速</span>
<span class="etag fact">fact</span> 16-Hi {term("HBM4","hbm4")}歩留り&lt;20%でRubin R100はピン速度を下げる仕様調整。{term("CoWoS-L","cowos")}歩留り問題でRubin Ultraは4ダイ→デュアルダイに縮小。
<span class="etag stance">stance</span> 「チップが足りない」の実体は<strong>パッケージとメモリの歩留り</strong>。投資妙味は歩留り改善技術({term("ガラス","glass-sub")}/L3)、HBMサプライヤ(L4)、そして設計受託のBroadcom/Marvellに波及する。
</div>
"""

sysA = f"""
<h2 id="L5-A">系統A: 商用GPU</h2>
{node_block("rubin")}
{node_block("mi400")}
"""
sysB = f"""
<h2 id="L5-B">系統B: ハイパースケーラ独自ASIC</h2>
<p>自社ワークロードに最適化し垂直統合でコスト破壊。<span class="etag fact">fact</span> Broadcom/MarvellがASIC設計の8割超を担うため、勝者は実は設計受託側でもある。NVIDIAにとってAMDより構造的に大きな脅威。</p>
{node_block("tpu")}
{node_block("trainium")}
"""
sysC = f"""
<h2 id="L5-C">系統C: 推論特化・データフロー</h2>
<p>GPUと異なるアーキでdecode(生成)帯域に特化。{term("Cerebras","cerebras")}のウェハスケールはチップレット/パッケージング(L3)の真逆——ダイシングを廃しオンチップSRAMでメモリの壁を物理回避する。GroqはNVIDIAが$20Bで実質吸収し、独立勢の劣勢が鮮明。</p>
{node_block("cerebras")}
{node_block("sambanova")}
"""
sysD = f"""
<h2 id="L5-D">系統D: 中国勢</h2>
<p>米輸出規制が生んだ第四極。単体性能はNVIDIA比劣るが内需と国家戦略、システム結合(CloudMatrix)で量的に補う。グローバル市場の地政学的分断の象徴。</p>
{node_block("china-asic")}
"""
sysE = f"""
<h2 id="L5-E">系統E: CPU・スーパーチップ統合</h2>
<p>演算チップ単体でなくCPUと密結合した計算ノードとして設計する潮流。{term("システム統合","T-sys")}・{term("メモリ中心アーキテクチャ","T-mem")}の交差点。</p>
{node_block("vera-cpu")}
"""

refpanel = """
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin-bottom:8px">系統</div>
<a href="#L5-A" style="display:block;margin-bottom:6px">A 商用GPU</a>
<a href="#L5-B" style="display:block;margin-bottom:6px">B 独自ASIC</a>
<a href="#L5-C" style="display:block;margin-bottom:6px">C 推論特化</a>
<a href="#L5-D" style="display:block;margin-bottom:6px">D 中国勢</a>
<a href="#L5-E" style="display:block;margin-bottom:14px">E CPU統合</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">連結レイヤー</div>
<a href="../layers/l3-packaging.html" style="display:block;margin-bottom:6px">L3 パッケージ (歩留り律速)</a>
<a href="../layers/l4-memory.html" style="display:block;margin-bottom:6px">L4 メモリ (HBM4)</a>
<a href="../layers/l6-scaleup.html" style="display:block;margin-bottom:6px">L6 スケールアップ (NVL72)</a>
<a href="../trends/system.html" style="display:block;margin-bottom:6px">トレンド: システム統合</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">凡例</div>
<div style="font-size:11px;line-height:1.7">
<span class="etag fact">fact</span> 確立事実<br><span class="etag infer">infer</span> 推論<br>
<span class="etag spec">spec</span> 予測/不確実<br><span class="etag stance">stance</span> 見解
</div>
"""

main = intro + compare + sysA + sysB + sysC + sysD + sysE + pager(("l4-memory","L4 メモリ"), ("l6-scaleup","L6 スケールアップ"))
out = page(REL, "L5 演算チップ", "l5-compute",
           [("レイヤー", None), ("L5 演算チップ", None)], main, refpanel)
open(os.path.join(ROOT,"layers","l5-compute.html"),"w").write(out)
print("wrote layers/l5-compute.html", len(out), "bytes")
