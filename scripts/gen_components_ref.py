#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = "."

def term(label, tid):
    return f'<span class="term" data-term="{tid}">{label}</span>'

# Component families, organized by FUNCTION and tagged by AI-criticality + layer.
# crit: 5=AI性能/供給を直接律速, 3=AI構成で重要, 1=汎用(あらゆる電子機器共通)
FAMILIES = [
  ("演算・ロジック", "L5/L3", [
    ("GPUダイ / ASICダイ / NPU", 5, "L5", "演算本体。チップレット化が進む。", "rubin"),
    ("チップレット / I/Oダイ", 5, "L3", "大ダイを分割し統合。歩留り・混載で有利。", "soic"),
    ("Tensor Core系演算ブロック", 3, "L5", "行列演算の専用回路。ダイ内のIPブロック。", None),
  ]),
  ("メモリ", "L4", [
    ("HBM3E / HBM4 スタック", 5, "L4", "ダイ近傍の広帯域メモリ。AI性能の実質的律速。", "hbm4"),
    ("DRAMコアダイ / ベースダイ", 5, "L4", "HBMを構成する記憶ダイとロジック土台。", "hbm-basedie"),
    ("TSV (シリコン貫通電極)", 5, "L4", "HBM各層を縦に貫く電極。", "m-tsv"),
    ("SOCAMM2 / LPDDR", 3, "L4", "HBMとDDRの中間階層。CPU近接の低電力メモリ。", "socamm"),
  ]),
  ("2.5D/3D 実装・接合", "L3", [
    ("シリコンインターポーザ / RDL", 5, "L3", "ダイ間を高密度配線する盤。CoWoSの中核。", "cowos"),
    ("ハイブリッドボンディング", 5, "L3", "バンプレス銅直接接合。3D積層の心臓。", "m-hbond"),
    ("マイクロバンプ / Cuピラー", 3, "L3", "ダイ↔インターポーザの微細接合。", "ubump"),
    ("C4バンプ / はんだボール(BGA)", 1, "L3", "インターポーザ↔基板↔PCBの接合。", "c4"),
    ("ガラスインターポーザ / TGV", 3, "L3", "Si代替の次世代配線盤と貫通電極。", "glass-int"),
    ("銀焼結材 / 熱圧着材(TCB)", 1, "L3", "接合プロセス材。", None),
  ]),
  ("パッケージ基板・材料", "L3/L2", [
    ("ABFビルドアップフィルム", 5, "L3", "高密度基板の絶縁層。味の素が独占。", "m-abf"),
    ("CCL / コア材 / プリプレグ / BT基板", 3, "L3", "基板の機械的な芯と多層材。", "m-ccl"),
    ("ガラスコア基板", 3, "L3", "有機コアをガラスに置換。低CTE・高平坦。", "glass-sub"),
    ("低Dk/低Df材料", 3, "L3", "高速信号の損失を抑える誘電材料。", None),
    ("ソルダーレジスト / 銅箔・銅めっき", 1, "L3", "配線保護と導体形成。", "sr"),
  ]),
  ("電源・PDN (電力供給網)", "L1/L5", [
    ("PDN (電源供給網) ※概念", 5, "L1", "下記部品が構成する網全体。0.7Vで数千Aを供給する電源integrityの総体。", "pdn"),
    ("DrMOS / Smart Power Stage", 5, "L1", "POL変換段。VPDでダイ直下にタイル配置。", "m-drmos"),
    ("パワーインダクタ", 3, "L1", "多相VRMの出力平滑。", "m-powerinductor"),
    ("シリコンキャパシタ / DTC / 基板内蔵Cap", 5, "L3", "超低ESLデカップリング。MLCCの次。", "m-sicap"),
    ("MLCC (高容量/低ESL/低ESR)", 5, "L3", "デカップリングの主力受動部品。", "m-mlcc"),
    ("GaN FET / SiC MOSFET", 5, "L1", "高効率電力変換。800V/48V系の鍵。", "m-gansic"),
    ("VRMコントローラ / PMIC / LDO", 3, "L1", "電源制御・管理・局所低ノイズ電源。", "m-vrm"),
    ("eFuse / Hot-swapコントローラ", 1, "L1", "過電流保護・活線挿抜保護。", None),
    ("電解/ポリマー/タンタル/フィルムコンデンサ", 1, "L1", "PSU・バルク平滑。汎用電源部品。", None),
    ("スーパーキャパシタ / BESS", 3, "L1", "瞬低対策・エネルギーバッファ。", "power-supply"),
  ]),
  ("信号・高速I/O・ネットワーク", "L6/L7", [
    ("Retimer / Redriver", 5, "L7", "高速信号補正。224G世代で必須化。", "m-retimer"),
    ("Ethernet PHY / SerDes", 5, "L7", "400G/800G/1.6T通信の物理層。", "ethernet-uec"),
    ("光トランシーバ / 光エンジン", 5, "L7", "電気↔光変換。CPOへ統合進む。", "m-optengine"),
    ("クロック / 水晶 / TCXO/OCXO", 3, "L7", "基準クロック。ジッタが帯域を左右。", "m-clock"),
    ("ESD/TVSダイオード", 3, "L7", "I/Oのサージ・静電気保護。", "m-esd"),
    ("ACカップリングCap / 終端抵抗", 1, "L7", "差動信号のDC遮断・整合。", None),
    ("PCIe/NVLinkコネクタ / ソケット", 1, "L6", "物理接続部材。", "nvlink"),
  ]),
  ("抵抗・磁性・センサ (汎用)", "—", [
    ("金属板シャント / 電流検出抵抗", 3, "L1", "GPU/VRMの大電流検出。PDN制御の目。", "m-shunt"),
    ("チップ抵抗 / 薄膜・厚膜 / 精密抵抗", 1, "—", "バイアス・分圧・終端など汎用。", None),
    ("コモンモードチョーク / フェライトビーズ", 1, "—", "ノイズ対策。", None),
    ("NTC/PTCサーミスタ / バリスタ", 1, "L1", "温度検出・過電流・サージ保護。", None),
  ]),
  ("冷却・熱対策", "L1/L3", [
    ("TIM / 液体金属TIM", 5, "L1", "ダイ↔放熱の熱界面材。高TDPで律速。", "m-tim"),
    ("コールドプレート / マイクロチャネル冷却板", 5, "L1", "液冷の受熱部。埋込冷却へ。", "m-cdu"),
    ("CDU / ポンプ / クイックディスコネクト", 5, "L1", "液冷ループの循環・分配・接続。", "m-cdu"),
    ("ヒートスプレッダ(IHS) / ベイパーチャンバー", 3, "L3", "熱拡散。リッドレス化の圧力も。", "m-ihs"),
    ("熱伝導ギャップフィラー / グラファイトシート", 1, "L1", "周辺部品の熱接続・面内拡散。", None),
  ]),
  ("製造・リソグラフィ部材", "L2", [
    ("EUVマスク / フォトマスク", 5, "L2", "露光原版。レチクル上限がL3制約の根源。", "m-euvmask"),
    ("ペリクル / フォトレジスト / ブランクス", 3, "L2", "マスク保護・感光材・マスク素材。", None),
  ]),
  ("ストレージ・管理系 (周辺)", "L4/—", [
    ("エンタープライズSSD / NAND (QLC)", 5, "L4", "推論KVキャッシュ/RAGの受け皿。2026完売・価格+234%・寡占。HBMに次ぐ利益柱。", "nand"),
    ("HBF (高帯域フラッシュ)", 3, "L4", "HBMとNANDの中間を埋める新アーキ。SanDisk/SK hynix標準化。", "hbf"),
    ("BMC / EEPROM / RTC / センサ", 1, "—", "サーバ管理系。", None),
  ]),
]

def crit_pill(c):
    if c>=5: return '<span class="pill deprecated" style="color:#e8643c">AI律速</span>'
    if c>=3: return '<span class="pill emerging">AI重要</span>'
    return '<span class="pill" style="color:var(--muted)">汎用</span>'

rows=""
for fam, layer, items in FAMILIES:
    rows += f'<tr><td colspan="4" style="background:var(--navy-3);color:var(--gold);font-weight:700;padding:10px 12px">{fam} <span class="mono" style="color:var(--cyan-dim);font-size:11px;font-weight:400">{layer}</span></td></tr>'
    for name, crit, lyr, desc, tid in items:
        linked = term(name, tid) if tid else name
        rows += (f'<tr><td style="padding-left:18px">{linked}</td>'
                 f'<td>{crit_pill(crit)}</td>'
                 f'<td class="mono" style="color:var(--cyan-dim);font-size:12px">{lyr}</td>'
                 f'<td style="font-size:13px;color:#cdd9ec">{desc}</td></tr>')

intro = f"""
<div class="eyebrow">付録 / 部材リファレンス</div>
<h1>構成部材リファレンス</h1>
<p class="lead">AI半導体・データセンターを構成する部材を機能別に整理し、<strong>AIにとっての重要度</strong>と<strong>担当レイヤー</strong>でタグ付けした。網羅性を保ちつつ「何がAI性能・供給を律速し、何が汎用部品か」を区別する——フラットな列挙では失われる視点。</p>

<div class="callout invest"><span class="c-tag">設計方針: 網羅 ≠ 羅列</span>
あらゆる電子機器に共通する部品(汎用抵抗・コンデンサ・チョーク等)まで列挙すれば数百点になるが、それは「AIロードマップ」の解像度を下げる。本表は<strong>機能でグルーピングし、AI文脈での重要度(AI律速 / AI重要 / 汎用)を明示</strong>する。<span class="etag stance">stance</span> 投資・技術判断に効くのは「律速」タグの部材。
</div>

<div class="legend" style="margin:8px 0 16px">
  <span class="li">{crit_pill(5)} AI性能・供給を直接律速する</span>
  <span class="li">{crit_pill(3)} AI構成で重要</span>
  <span class="li">{crit_pill(1)} 汎用(あらゆる電子機器共通)</span>
</div>
<p style="font-size:13px;color:var(--muted)">リンク付き部材はカーソルで解説・個別カードへ。リンクなしは本表のみの汎用部材。</p>

<div class="tbl-wrap"><table>
<thead><tr><th style="width:38%">部材</th><th>AI重要度</th><th>レイヤー</th><th>役割</th></tr></thead>
<tbody>{rows}</tbody>
</table></div>

<h2>外部リストとの突合 — 正直な評価</h2>
<p>網羅的な外部部材リスト(GPT-5.5生成)と本ロードマップを突合した。<span class="etag stance">stance</span> 外部リストは<strong>breadth(広さ)では優秀</strong>だが、以下の弱点がある。これは生成AIの部材列挙に共通する傾向でもある。</p>

<h3>外部リストが優れていた点 → 取り込んだ</h3>
<p>本ロードマップに欠けていた以下のAI重要部材を、外部リストを契機に第一級ノードとして追加した: {term("DrMOS/Smart Power Stage","m-drmos")}(垂直給電)、{term("シリコンキャパシタ/DTC","m-sicap")}(超低ESLデカップリング)、{term("パワーインダクタ","m-powerinductor")}、{term("Retimer/Redriver","m-retimer")}(信号補正)、{term("クロック/水晶","m-clock")}、{term("ESD/TVS","m-esd")}。特にPDN(電源供給網)と信号補正は、2000A級過渡電流と224G SerDesというAI固有の要求で重要度が上がっており、補強の価値が高かった。</p>

<h3>外部リストの弱点・不正確な点</h3>
<div class="callout warn"><span class="c-tag">指摘 (正確性のために)</span>
<ul style="margin:6px 0;padding-left:20px;line-height:1.7">
<li><span class="etag fact">fact</span> <strong>階層と因果がない</strong>: フラットな表で「どの部材がどのスケール(ダイ/パッケージ/ボード/ラック)にいて、何を律速するか」が欠落。MLCCとSSDが同列に並ぶ。本ロードマップは物理階層と{term("メモリの壁","hbm4")}等の因果でこれを補う。</li>
<li><span class="etag fact">fact</span> <strong>真に汎用な部材の混在</strong>: 「管理系(RTC/EEPROM/BMC)」「汎用チップ抵抗」はAIサーバにも在るが性能・収益を律速しない。これらをHBMやCoWoSと並べると優先順位を誤らせる。<strong>ただし注意</strong>: ストレージ(NAND/SSD)をここに含めるのは誤り——下記の自己訂正を参照。</li>
<li><span class="etag infer">infer</span> <strong>過剰な細分化</strong>: MLCCを「高容量/低ESL/低ESR/逆ジオメトリ/3端子/Feedthrough/高耐圧/高温/C0G/X7R/薄型」と11種列挙しているが、これらは同一部品の仕様バリエーションで、別部材ではない。網羅性の見かけを増やすが理解は深まらない。本表では「MLCC(高容量/低ESL/低ESR)」に集約。</li>
<li><span class="etag fact">fact</span> <strong>時間軸・世代がない</strong>: 「HBM2E/HBM3/HBM3E/HBM4」を併記するが、どれが現行でどれが旧世代かの区別がない。2026時点のAI新規設計はHBM3E→HBM4が主で、HBM2Eは事実上レガシー。</li>
<li><span class="etag infer">infer</span> <strong>新潮流の欠落</strong>: 垂直給電(VPD)、裏面給電(BSPDN)との電源協調、ガラスインターポーザの光導波路統合、CPOの光エンジンといった<strong>構造変化の方向</strong>が部材リストからは見えない。静的な「今ある部品」の列挙に留まり、「どこへ向かうか」がない。</li>
</ul>
</div>
<p><span class="etag stance">stance</span> 結論: 外部リストは「漏れのないチェックリスト」として有用で、実際に本ロードマップの部材ノードを6点増やす契機になった(正直に認める)。一方で<strong>「AI半導体の構造変化を捉える」という本来の目的には、列挙でなく階層・因果・時間軸・重要度の付与が要る</strong>。本ロードマップの価値はそこにある。</p>

<h3>自己訂正 — NANDを過小評価していた</h3>
<div class="callout warn"><span class="c-tag">訂正 (正直に)</span>
本ロードマップは当初、NAND/SSDを「ストレージ=AI性能の主律速ではない」として汎用(crit 1)に分類していた。これは誤りだった。<span class="etag fact">fact</span> 2026年、推論のKVキャッシュ/RAGがHBM容量を超えてエンタープライズSSDへ溢れ、NAND価格はGartner予想で+234%、Kioxiaは完売・利益48倍・株価24倍、SanDiskも1年で+210%超。<span class="etag fact">fact</span> Samsung/SK hynixがHBM優先でNANDウェハを削減した供給共食いも逼迫を増幅。
<span class="etag stance">stance</span> 誤りの原因は明確で、<strong>「演算を律速するか」だけを重要度の軸にし、本ツールが備える「価格決定力×供給逼迫」の投資2軸を適用し忘れた</strong>こと。NANDは演算帯域は律速しないが、寡占×完売×新需要で投資妙味の右上象限に入る。{term("NAND/エンタープライズSSD","nand")}を crit 5・L4ノードに格上げし、{term("HBF","hbf")}(NANDとHBMの中間アーキ)を新設した。「ストレージは脇役」という2023年的な前提こそが、捉えるべき構造変化だった。
</div>

<div class="viewbar">
  <a href="basics.html" class="primary">▸ 基礎と全体像</a>
  <a href="companies.html">▸ 銘柄マップ</a>
  <a href="glossary.html">▸ 用語・部材インデックス</a>
  <a href="views/graph.html">▸ 関係グラフ</a>
</div>
"""

out = page(REL, "構成部材リファレンス", "components-ref", [("構成部材リファレンス", None)], intro)
open(os.path.join(ROOT,"components.html"),"w").write(out)
print("wrote components.html", len(out), "bytes")
