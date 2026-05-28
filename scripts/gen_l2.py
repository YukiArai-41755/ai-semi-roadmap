#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page
from layer_common import n, L, term, node_block, pager

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = ".."

l2 = L("L2")
subs = {s["id"]: s for s in l2["sub_systems"]}

def svg_fig(fname, caption):
    svg = open(os.path.join(ROOT,"assets","svg",fname)).read()
    return f'<figure class="schematic">{svg}<figcaption>{caption}</figcaption></figure>'

intro = f"""
<div class="eyebrow">LAYER 2 / 縦階層</div>
<h1>{l2["name"]}</h1>
<p class="lead">{l2["summary"]}</p>
<div class="callout invest"><span class="c-tag">投資判断の要点</span>
<span class="etag fact">fact</span> 二つの構造転換が同時進行: FinFET→{term("GAAナノシート","gaa")}、表面配線→{term("裏面給電(BSPDN)","bspdn")}。
<span class="etag stance">stance</span> 微細化単体の伸びは鈍化し価値はパッケージ(L3)へ移ったが、AI/HPC向けには裏面給電が新たな差別化軸。
<span class="etag fact">fact</span> TSMCはHigh-NA EUVを2029年まで使わない方針——{term("マスクスティッチング","litho")}で凌ぐ。これがL3のレチクル制約の根源。
</div>

<h2>このレイヤーの三系統</h2>
<div class="tbl-wrap"><table>
<thead><tr><th>系統</th><th>役割</th><th>代表</th><th>競争軸</th></tr></thead>
<tbody>
<tr><td><strong>{subs["L2-A"]["name"]}</strong></td><td>トランジスタの構造</td><td>{term("GAAナノシート","gaa")}</td><td>電流駆動力・リーク制御</td></tr>
<tr><td><strong>{subs["L2-B"]["name"]}</strong></td><td>電源網を裏面へ</td><td>{term("SPR / PowerVia","bspdn")}</td><td>電力integrity・速度</td></tr>
<tr><td><strong>{subs["L2-C"]["name"]}</strong></td><td>パターン露光</td><td>{term("EUV / High-NA","litho")}</td><td>解像度・コスト・レチクル上限</td></tr>
</tbody></table></div>
"""

detail = f"""
<h2>二大構造転換を図で理解する</h2>
<p>L2の変化は二つ。トランジスタの形(FinFET→{term("GAAナノシート","gaa")})と、電源を流す面({term("裏面給電","bspdn")})。どちらも微細化が鈍る中で性能を絞り出す工夫で、先端ノードでは同時に採用される。</p>
{svg_fig("gaa-bspdn.svg","図: 左=トランジスタ構造(FinFETはゲートが3面、GAAナノシートは全周を囲み制御性向上)。右=給電面(表面給電は信号と電源が混雑、裏面給電は電源を裏へ回し表面を信号専用に→+8-10%速度/-20%電力)。")}

<h2>ノードロードマップ (TSMC NA Symposium 2026)</h2>
<p><span class="etag spec">spec</span> 量産時期は公表ベース。AI/HPCノードは裏面給電を早期搭載、モバイルはコスト都合で非搭載のセグメント分岐が鮮明。</p>
<div class="tbl-wrap"><table>
<thead><tr><th>ノード</th><th>特徴</th><th>量産</th><th>用途</th></tr></thead>
<tbody>
<tr><td>N2</td><td>初のGAAナノシート(BSPDNなし)</td><td>2025</td><td>汎用・モバイル・AMD MI400(2nm先行)</td></tr>
<tr><td>N2P / N2X / N2U</td><td>N2派生・改良</td><td>2026-</td><td>モバイル/AI/HPC</td></tr>
<tr><td class="cell-best">A16 (1.6nm)</td><td>N2P + Super Power Rail(裏面給電)、+8-10%速度/-20%電力</td><td>2027(後ろ倒し)</td><td class="cell-best">AI/HPC</td></tr>
<tr><td>A14 (1.4nm)</td><td>2nd gen ナノシート</td><td>2028(モバイル)→2029(BSPDN, DC)</td><td>モバイル→AI</td></tr>
<tr><td>A13 / A12</td><td>A14派生 / フルノード(BSPDN)</td><td>2029</td><td>AI/HPC・CPU</td></tr>
</tbody></table></div>

<h2>三社の構造選択</h2>
<div class="tbl-wrap"><table>
<thead><tr><th>項目</th><th>TSMC</th><th>Intel</th><th>Samsung</th></tr></thead>
<tbody>
<tr><td>GAA量産</td><td class="cell-best">N2(2025)・歩留り優位</td><td>18A</td><td>SF2 / SF1.4(4ナノシート)</td></tr>
<tr><td>裏面給電</td><td>A16 SPR(直接コンタクト, 2027)</td><td class="cell-best">PowerVia(18Aで先行・容易だが益小)</td><td>追随</td></tr>
<tr><td>High-NA EUV</td><td>2029まで不採用(コスト見合わず)</td><td class="cell-best">14Aで先行推進</td><td>検討</td></tr>
<tr><td>課題</td><td>—</td><td>世界級歩留りは~2027</td><td class="cell-worst">GAA歩留りに苦戦</td></tr>
</tbody></table></div>

<div class="callout warn"><span class="c-tag">レイヤー連結: 微細化鈍化が上位を駆動</span>
<span class="etag fact">fact</span> EUV(0.33NA)のレチクル上限(~858mm²)がL3 {term("CoWoS","cowos")}の大型化制約とマスクスティッチングの根源。
<span class="etag infer">infer</span> {term("SRAM(キャッシュ)","gaa")}のスケーリング頭打ちがメモリ依存を強め、L4 {term("HBM4","hbm4")}の重要性を押し上げる(メモリの壁の遠因)。
<span class="etag stance">stance</span> 微細化の限界効用逓減で、性能の主役はL2からL3(パッケージ)・L4(メモリ)・L6/L7(インターコネクト)へ分散した——本ロードマップが微細化を最下層の一レイヤーに留め、時間軸を従属させた理由がここにある。
</div>
"""

sysA = f'<h2 id="L2-A">系統A: トランジスタ構造 (GAA)</h2>{node_block("gaa")}'
sysB = f'<h2 id="L2-B">系統B: 裏面給電 (BSPDN)</h2><p>GAAと並ぶもう一つの構造転換。電源と信号を物理的に分離する。AI/HPC大規模ダイで効く。</p>{node_block("bspdn")}'
sysC = f'<h2 id="L2-C">系統C: リソグラフィ</h2><p>ASMLが独占。High-NA採用是非がTSMC(慎重)とIntel(先行)の戦略を分ける。鍵部材は{term("EUVマスク","m-euvmask")}(レチクル上限~858mm²がL3の巨大パッケージ制約の根源)と{term("EUVフォトレジスト","m-resist")}(JSR/TOK/信越/富士の寡占で価格決定力高、ただしEUVは層数減で量の逼迫は中程度)。</p>{node_block("litho")}'

refpanel = """
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin-bottom:8px">系統</div>
<a href="#L2-A" style="display:block;margin-bottom:6px">A GAA</a>
<a href="#L2-B" style="display:block;margin-bottom:6px">B 裏面給電</a>
<a href="#L2-C" style="display:block;margin-bottom:14px">C リソグラフィ</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">連結レイヤー</div>
<a href="../layers/l3-packaging.html" style="display:block;margin-bottom:6px">L3 パッケージ (レチクル制約)</a>
<a href="../layers/l5-compute.html" style="display:block;margin-bottom:6px">L5 演算 (ノード製造)</a>
<a href="../layers/l4-memory.html" style="display:block;margin-bottom:6px">L4 メモリ (ベースダイ)</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">凡例</div>
<div style="font-size:11px;line-height:1.7">
<span class="etag fact">fact</span> 確立事実<br><span class="etag infer">infer</span> 推論<br>
<span class="etag spec">spec</span> 予測/不確実<br><span class="etag stance">stance</span> 見解
</div>
"""

main = intro + detail + sysA + sysB + sysC + pager(("l1-power-cooling","L1 施設・電力・冷却"), ("l3-packaging","L3 先端パッケージ"))
out = page(REL, "L2 製造プロセス・基盤", "l2-process",
           [("レイヤー", None), ("L2 製造プロセス・基盤", None)], main, refpanel)
open(os.path.join(ROOT,"layers","l2-process.html"),"w").write(out)
print("wrote layers/l2-process.html", len(out), "bytes")
