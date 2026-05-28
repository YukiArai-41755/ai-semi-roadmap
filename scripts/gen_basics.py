#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = "."  # this page lives at root

def svg_fig(fname, caption):
    svg = open(os.path.join(ROOT,"assets","svg",fname)).read()
    return f'<figure class="schematic">{svg}<figcaption>{caption}</figcaption></figure>'

# basic terms — defined inline (not graph nodes; these are foundational vocabulary)
BASICS = [
  ("ダイ (die)", "シリコンウェハから切り出した半導体チップ本体。トランジスタが作り込まれた「生のチップ」。これをパッケージに収めて初めて製品になる。L2で作られL3で封止される。"),
  ("ウェハ (wafer)", "シリコンの円盤(直径300mm)。この上に多数のダイをまとめて作り、最後に切り分ける。Cerebrasは切らずに丸ごと1チップにする(ウェハスケール)。"),
  ("パッケージ (package)", "ダイを保護し外部と電気的に繋ぐ「殻」。現代のAIチップはGPUダイ+HBMなど複数のダイを1パッケージに統合する(これがL3先端パッケージ)。"),
  ("PCB / 基板", "Printed Circuit Board。部品を載せて配線する板。パッケージはこのPCBに半田付けされる。文中の「マザーボード」もこれ。"),
  ("ラック (rack)", "サーバ機器を縦に収める棚。AIでは1ラックに多数のGPUを詰め、ラック全体を1台の巨大計算機として設計する(NVL72等)。電力は今や1ラック120kW〜1MW級。"),
  ("ノード / トレイ", "ラックに挿す引き出し1枚分の計算ユニット。CPU・GPU・メモリ・PCBが載る。サーバ1台分に相当。"),
  ("CPU", "Central Processing Unit。汎用の頭脳。少数の高性能コアで逐次処理や制御が得意。AIではGPUを束ねる司令塔役(L5のスーパーチップ統合)。"),
  ("GPU", "Graphics Processing Unit。元は画像処理用。多数の単純コアで並列計算が得意で、AIの行列演算に最適。NVIDIA/AMDの主力(L5商用GPU)。"),
  ("ASIC", "Application-Specific Integrated Circuit。特定用途専用チップ。汎用性を捨てる代わりに電力効率・コストで勝る。GoogleのTPU、AWSのTrainiumなど(L5独自ASIC)。"),
  ("FinFET", "ひれ(fin)状の立体トランジスタ構造。長く微細化を支えたが限界に近づき、GAAナノシートへ移行中(L2)。"),
  ("トランジスタ", "電気のオン/オフを切り替える最小素子。これを数百億〜数兆個集積したものがダイ。微細化=より多く詰めること。"),
  ("TDP", "Thermal Design Power。チップが発する熱の設計上限(W)。AIチップは2000W超へ。これを捌く冷却(L1)が律速になる。"),
  ("HBM", "High Bandwidth Memory。DRAMを縦に積みダイ近傍に置く広帯域メモリ。AIの性能を実質的に決める(L4)。"),
  ("帯域 / バンド幅", "単位時間に運べるデータ量(TB/s等)。AIは大量の重みを高速に読む必要があり、演算速度より帯域が律速になりがち(=メモリの壁)。"),
  ("レイテンシ", "信号が届くまでの遅延(μs等)。学習・推論の応答速度を左右し、インターコネクト(L6/L7)で重要。"),
  ("チップレット", "1つの大きなダイの代わりに、小さなダイ(チップレット)を複数繋いで1チップ相当にする設計。歩留り・コスト・混載で有利(L3)。"),
  ("歩留り (yield)", "製造した中で良品の割合。微細化・高積層・大型パッケージほど下がり、AIチップ供給の真の律速になっている。"),
  ("スケールアップ / スケールアウト", "scale-up=1台(1ラック)を大きく強くする(L6)。scale-out=多数を繋いで台数で稼ぐ(L7)。AIは両方必要。"),
  ("推論 / 学習", "学習(training)=モデルを作る計算。推論(inference)=作ったモデルを使う計算。近年は推論需要が支出の約2/3を占め、チップ設計の重心も推論へ。"),
  ("PDN / 電源供給網", "Power Delivery Network。VRM(電源回路)からダイまで電力を届ける網。AI GPUは0.7Vで数千Aを使い、負荷がナノ秒で急変するため、電圧を保つのが極めて難しい。MLCC等の受動部品はこの網を支える要素(L1)。"),
  ("デカップリング", "電源電圧の急な落ち込みを、ダイの近くに置いたコンデンサが電流を肩代わりして防ぐこと。AIの高速・大電流ではコンデンサの量と配置が性能を左右する。"),
  ("受動部品", "電源を作らず整える部品(コンデンサ・抵抗・インダクタ)。トランジスタのような能動部品と対。地味だがAIの電源安定性の鍵で、GPU周りに大量に載る。"),
  ("VRM", "Voltage Regulator Module。高い入力電圧をGPU/CPUが要る低電圧(〜0.7V)へ変換・安定化する電源回路。DrMOSやパワーインダクタで構成。"),
]

basics_rows = "".join(
  f'<tr><td style="white-space:nowrap;font-weight:700;color:var(--cyan)">{t}</td><td>{d}</td></tr>'
  for t,d in BASICS)

intro = f"""
<div class="eyebrow">はじめに / 基礎</div>
<h1>基礎と全体像</h1>
<p class="lead">各レイヤーの詳細に入る前に、(1)物理的な大きさの入れ子、(2)基礎用語、(3)既存の枠組みを押さえる。半導体に詳しくなくてもここを読めば全7レイヤーが繋がる。</p>

<h2>1. 物理的な入れ子 — 大きいものから小さいものへ</h2>
<p>「データセンターの中に箱があって、ラックがあって、基板があって、GPUが載っていて…」という感覚を一枚に。外側ほど大きく(システム全体)、内側ほど小さい(個別部品)。各枠が本ロードマップのどのレイヤーに対応するかを示した。</p>
{svg_fig("scale-nesting.svg","図: 物理的な入れ子。データセンター→データホール→ラック→ノード/トレイ→PCB→パッケージ→ダイ。右の金色タグが担当レイヤー。GPUとHBMは最も内側のパッケージ/ダイの層にいる。")}

<div class="callout invest"><span class="c-tag">読み方の勘所</span>
一番外(データセンター全体の電力・冷却)が<strong>L1</strong>、一番内(ダイのトランジスタ)が<strong>L2</strong>。その間を、演算チップ(L5)・メモリ(L4)・それらを1パッケージに統合する技術(L3)・ラック内結合(L6)・ラック間結合(L7)が埋める。<br>
重要なのは: <strong>近年のAIの性能向上は、一番内側(微細化=L2)だけでは足りなくなり、パッケージ(L3)・メモリ(L4)・結合(L6/L7)・電力(L1)へと主役が広がった</strong>。本ロードマップが微細化を最下層の一レイヤーに留め、時間軸より階層構造を主軸にした理由がこれ。
</div>

<h2>2. 基礎用語</h2>
<p>本文で頻出する基本語。各レイヤーの専門用語は本文中でカーソルを合わせると個別解説が出る。</p>
<div class="tbl-wrap"><table>
<thead><tr><th style="width:160px">用語</th><th>説明</th></tr></thead>
<tbody>{basics_rows}</tbody>
</table></div>

<h2>3. 既存の枠組み — 何がベースで、何が変わったか</h2>
<p>AIデータセンターは、従来のコンピュータ/データセンターの延長線上にある。まず土台を押さえると、各レイヤーの「変化」が何からの変化なのかが分かる。</p>

<h3>従来のコンピュータ (ノイマン型)</h3>
<p>計算機はおおまかに <strong>演算(CPU)・記憶(メモリ)・配線(バス)</strong> から成る。CPUがメモリからデータと命令を読み、計算し、書き戻す。この「CPUとメモリの間でデータを往復させる」構造がノイマン型で、半世紀の基本形。ここで<strong>データ往復が遅さの原因になる(ノイマン・ボトルネック)</strong>——AIで顕在化した「メモリの壁」(L4)の正体はこれ。</p>

<h3>従来のデータセンター</h3>
<p>サーバ(CPU中心)をラックに並べ、Ethernetで繋ぎ、空冷し、AC電源(54V系)で給電する。1ラック数kW〜十数kW。汎用計算・Webサービス向けの構成。</p>

<h3>AIデータセンターで何が変わったか (本ロードマップの主題)</h3>
<div class="tbl-wrap"><table>
<thead><tr><th>観点</th><th>従来</th><th>AI時代の変化</th><th>レイヤー</th></tr></thead>
<tbody>
<tr><td>主役の計算機</td><td>CPU(逐次)</td><td>GPU/ASIC(超並列)</td><td><a href="layers/l5-compute.html">L5</a></td></tr>
<tr><td>性能の律速</td><td>CPUクロック・微細化</td><td>メモリ帯域・パッケージ/HBM歩留り</td><td><a href="layers/l4-memory.html">L4</a>/<a href="layers/l3-packaging.html">L3</a></td></tr>
<tr><td>チップの作り方</td><td>1枚の大きなダイ</td><td>チップレットを多数統合(先端パッケージ)</td><td><a href="layers/l3-packaging.html">L3</a></td></tr>
<tr><td>メモリ</td><td>DDR(基板上)</td><td>HBM(ダイ近傍に積層)+多層階層</td><td><a href="layers/l4-memory.html">L4</a></td></tr>
<tr><td>ラック内結合</td><td>PCIe程度</td><td>NVLink/UALinkで全GPU密結合=1巨大GPU化</td><td><a href="layers/l6-scaleup.html">L6</a></td></tr>
<tr><td>ラック間結合</td><td>通常Ethernet</td><td>専用の超高速網(InfiniBand/UEC)・光化</td><td><a href="layers/l7-scaleout.html">L7</a></td></tr>
<tr><td>給電</td><td>AC・54V・数kW/ラック</td><td>800V HVDC・600kW-1MW/ラック</td><td><a href="layers/l1-power-cooling.html">L1</a></td></tr>
<tr><td>冷却</td><td>空冷</td><td>液冷・液浸・埋込冷却</td><td><a href="layers/l1-power-cooling.html">L1</a></td></tr>
<tr><td>製造</td><td>FinFET・表面給電</td><td>GAAナノシート・裏面給電</td><td><a href="layers/l2-process.html">L2</a></td></tr>
</tbody></table></div>

<div class="callout"><span class="c-tag">要約</span>
従来は「1個の速いチップ(CPU)」を作る競争だった。AI時代は<strong>「多数のチップを、いかに密に繋ぎ、いかに速くメモリを供給し、いかに電力と熱を捌いて、巨大な1つの計算機にまとめるか」</strong>の競争になった。本ロードマップの7レイヤーは、その「まとめ方」を物理ボトムアップで分解したもの。
</div>

<h2>4. このロードマップの収録方針 (正直な線引き)</h2>
<p>AIサーバには数百種の部材が載る。本ロードマップは<strong>網羅的な部品表ではなく、投資・事業判断に効く構造変化を捉える地図</strong>として、収録粒度を意図的に選んでいる。何を入れ、何を入れていないかを明示する。</p>
<div class="tbl-wrap"><table>
<thead><tr><th>方針</th><th>具体</th></tr></thead>
<tbody>
<tr><td><strong>個別ノード化したもの</strong></td><td>構造変化の主役・ボトルネック・投資の結節点。先端パッケージ、HBM/カスタムベースダイ、演算チップ各系統、インターコネクト規格、800V HVDC、液冷、PDN中核部材(MLCC・シリコンキャパシタ・パワーインダクタ・DrMOS・シャント)、GaN/SiC、光エンジン、EUVマスク等。</td></tr>
<tr><td><strong>概念として束ねたもの</strong></td><td>個別部品でなく「網・系」として理解すべきもの。受動部品群は<a href="layers/l1-power-cooling.html#L1-D">PDN(電源供給網)</a>として束ねた——MLCCの12バリアントを個別に並べるより、周波数階層(バルク→MLCC→シリコンキャパシタ)として捉える方が判断に効くため。</td></tr>
<tr><td><strong>意図的に省いたもの</strong></td><td>アーキテクチャ判断に影響しない汎用部材・標準部品: 一般的なチップ抵抗/汎用MLCCの全バリアント、コネクタ/ソケット、BMC/EEPROM/RTC、ストレージ(NVMe/NAND)、はんだペースト/フラックス等の実装副資材、水晶の全種別。これらは重要だが「どれを選ぶか」が競争優位を決めないため、地図の解像度を上げる対象から外した。</td></tr>
</tbody></table></div>
<div class="callout warn"><span class="c-tag">見解</span>
<span class="etag stance">stance</span> 部品を多く列挙すること自体は価値でない。<strong>どの部材がどのボトルネックに効き、どのレイヤーの構造変化に連動するか</strong>を関係として示すことが、この知識グラフの目的。網羅リストが必要なら部品表(BOM)を見るべきで、本ツールはその上位の判断レイヤーを担う。
</div>

<div class="viewbar">
  <a href="index.html" class="primary">▸ トップ / 全体マップ</a>
  <a href="views/tree.html">▸ 階層ツリー</a>
  <a href="layers/l1-power-cooling.html">▸ L1から読む</a>
</div>
"""

out = page(REL, "基礎と全体像", "basics", [("基礎と全体像", None)], intro)
open(os.path.join(ROOT,"basics.html"),"w").write(out)
print("wrote basics.html", len(out), "bytes")
