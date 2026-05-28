#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page
from layer_common import n, L, term, node_block, pager

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = ".."

l1 = L("L1")
subs = {s["id"]: s for s in l1["sub_systems"]}

def svg_fig(fname, caption):
    svg = open(os.path.join(ROOT,"assets","svg",fname)).read()
    return f'<figure class="schematic">{svg}<figcaption>{caption}</figcaption></figure>'

intro = f"""
<div class="eyebrow">LAYER 1 / 縦階層</div>
<h1>{l1["name"]}</h1>
<p class="lead">{l1["summary"]}</p>
<div class="callout invest"><span class="c-tag">投資判断の要点</span>
AIスケーリングの<strong>最終律速</strong>。
<span class="etag fact">fact</span> ラック電力はH100 40kW→GB200 120kW→Rubin Ultra 600kW-1MW(2027)と3年で約25倍。
<span class="etag fact">fact</span> {term("800V HVDC","hvdc")}+{term("液冷","liquid-cooling")}が標準の組合せに(変換段削減・銅45%減・効率92%+・TCO約30%減)。
<span class="etag stance">stance</span> 問いが「チップをどう作るか」から「電気をどう確保するか」へ移った。{term("電力供給","power-supply")}(系統・SMR)が真のボトルネック。
</div>

<h2>このレイヤーの三系統</h2>
<div class="tbl-wrap"><table>
<thead><tr><th>系統</th><th>役割</th><th>代表</th><th>競争軸</th></tr></thead>
<tbody>
<tr><td><strong>{subs["L1-A"]["name"]}</strong></td><td>グリッド→チップの給電</td><td>{term("800V HVDC","hvdc")}</td><td>効率・電力密度・GaN/SiC</td></tr>
<tr><td><strong>{subs["L1-B"]["name"]}</strong></td><td>高TDPダイの除熱</td><td>{term("液冷・先進冷却","liquid-cooling")}</td><td>熱流束(W/cm²)・PUE</td></tr>
<tr><td><strong>{subs["L1-C"]["name"]}</strong></td><td>電力そのものの確保</td><td>{term("系統 / SMR / BESS","power-supply")}</td><td>可用性・立地・規制</td></tr>
</tbody></table></div>
"""

detail = f"""
<h2>電力密度の暴走と給電の再構築</h2>
<p>ラック電力密度は3年で25倍。従来のAC配電チェーン(変圧器→UPS→PDU→PSU)が物理的に追従できず、{term("800V HVDC","hvdc")}でグリッドからチップまでを再構築する。変換段を削減し銅使用量を45%減、エンドツーエンド効率を83%→92%+に。Rubin Ultra Kyber(600kW-1MW)世代で本格化する。</p>
{svg_fig("power-chain.svg","図: 給電チェーンの比較。現行は系統AC→変圧器→UPS→PDU→PSU(54V)と変換段が多い。800V HVDCは変換段を削減し損失と銅を減らす。GaN/SiCが高効率変換の鍵。")}
<div class="callout"><span class="c-tag">ハイパースケーラ毎の仕様分岐 (spec)</span>
<span class="etag fact">fact</span> 標準(Diablo 400)があるが実装は分裂。Meta 600-800kW、Google 900kW-1.1MW、Amazon ±400V/800kW、NVIDIAは単極800V/660kW(標準の外)。給電は各社の設計思想が最も出る領域。
</div>

<h2>冷却の世代交代</h2>
<p>高TDP化で空冷は破綻。<span class="etag fact">fact</span> Direct-to-Chip液冷が>100kWラックの標準(負圧ループで漏洩リスク低減)。次はマイクロ流体/埋込冷却(Microsoft-Corintisの葉脈状チャネル、TSMC直接シリコン冷却)で100+W/cm²のホットスポットに対応。最高密度には二相液浸(500W/cm², PUE~1.02)。{term("800V HVDC","hvdc")}と対で設計され、L3の{term("TIM","m-tim")}・{term("IHS","m-ihs")}と物理的に連続する。</p>

<div class="callout warn"><span class="c-tag">レイヤー連結: 電力が全てを律速する</span>
<span class="etag fact">fact</span> 高密度給電・冷却がL5の演算密度と、銅で全てに届くL6 scale-up設計を成立させる。
<span class="etag stance">stance</span> 投資的最重要点は{term("電力供給","power-supply")}=系統接続キューが数年に伸び、ビハインドザメーター発電・SMR・BESS・ソフト定義電力へ。データセンターの立地と規模を電力可用性が決める。GaN/SiC・電源IC・冷却(CDU/マイクロ流体)の川上に妙味。
</div>
"""

sysA = f'<h2 id="L1-A">系統A: 給電アーキテクチャ (800V HVDC)</h2>{node_block("hvdc")}'
sysB = f'<h2 id="L1-B">系統B: 冷却 (液冷→埋込)</h2>{node_block("liquid-cooling")}'
sysC = f'<h2 id="L1-C">系統C: 電力供給・系統</h2><p>演算でなく「電気そのもの」が最終律速。最も非技術的(規制・立地・系統)だが最も効く。さらにその物理的実体として、{term("高電圧変圧器","transformer")}が半導体ですらない最大のボトルネックになっている。</p>{node_block("power-supply")}{node_block("transformer")}'

components = f"""
<h2 id="L1-D">系統D: PDN — チップレベル給電網</h2>
<p>系統A(800V HVDC)が建屋〜ラックの給電なら、PDNはその先、<strong>VRMからダイまで</strong>の最終区間。AI最大の電源integrity課題で、GPT列挙のMLCC・シリコンキャパシタ・パワーインダクタ・DrMOS・シャント抵抗はすべてここを構成する部品。個々の部品でなく「網」として理解するのが勘所。</p>
{node_block("pdn")}
<div class="callout invest"><span class="c-tag">なぜPDNが効くか</span>
<span class="etag fact">fact</span> AI GPUは0.7-0.8Vで数百〜数千A、ナノ秒で負荷急変(高di/dt)。VRMが応答する前の電流を{term("デカップリングキャパシタ","m-mlcc")}が肩代わりし電圧崩壊を防ぐ。
<span class="etag fact">fact</span> 1000A級GPUは~3mFのバイパス容量が必要でPCB面積をほぼ占有→VRMをダイ直下に置く垂直給電でループインダクタンスを削減。
<span class="etag infer">infer</span> 周波数階層: バルク(低)→{term("MLCC","m-mlcc")}(中)→{term("シリコン/埋込キャパシタ","m-sicap")}(高・ダイ直近)。L2の{term("裏面給電","bspdn")}と連続していく。
</div>

<h2>主要部材</h2>
<p>L1の投資妙味は装置・部材の川上に集中する。給電(PDN)・冷却の両系統。</p>
<div class="legend" style="gap:8px 14px">
<span class="li" data-term="m-gansic"><span class="sw" style="background:#4a9e6b"></span>GaN/SiC パワー半導体</span>
<span class="li" data-term="m-vrm"><span class="sw" style="background:#8a7d5a"></span>電源IC / VRM</span>
<span class="li" data-term="m-drmos"><span class="sw" style="background:#8a7d5a"></span>DrMOS / SPS</span>
<span class="li" data-term="m-powerinductor"><span class="sw" style="background:#5a7a9a"></span>パワーインダクタ</span>
<span class="li" data-term="m-mlcc"><span class="sw" style="background:#b94a48"></span>MLCC</span>
<span class="li" data-term="m-sicap"><span class="sw" style="background:#2e6b8a"></span>シリコンキャパシタ</span>
<span class="li" data-term="m-shunt"><span class="sw" style="background:#9aa7bd"></span>シャント抵抗</span>
<span class="li" data-term="m-cdu"><span class="sw" style="background:#a05c7a"></span>CDU / 冷却分配</span>
</div>
<p style="font-size:13px;color:var(--muted)">各部材にカーソルで解説。電源系は{term("PDN","pdn")}として束ねて理解する。</p>
"""

refpanel = """
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin-bottom:8px">系統</div>
<a href="#L1-A" style="display:block;margin-bottom:6px">A 800V HVDC</a>
<a href="#L1-B" style="display:block;margin-bottom:6px">B 冷却</a>
<a href="#L1-C" style="display:block;margin-bottom:14px">C 電力供給</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">連結レイヤー</div>
<a href="../layers/l5-compute.html" style="display:block;margin-bottom:6px">L5 演算 (密度を給電)</a>
<a href="../layers/l3-packaging.html" style="display:block;margin-bottom:6px">L3 パッケージ (TIM/IHS)</a>
<a href="../layers/l6-scaleup.html" style="display:block;margin-bottom:6px">L6 スケールアップ (銅到達)</a>
<a href="../trends/power.html" style="display:block;margin-bottom:6px">トレンド: 電力制約</a>
<div style="font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin:14px 0 8px">凡例</div>
<div style="font-size:11px;line-height:1.7">
<span class="etag fact">fact</span> 確立事実<br><span class="etag infer">infer</span> 推論<br>
<span class="etag spec">spec</span> 予測/不確実<br><span class="etag stance">stance</span> 見解
</div>
"""

main = intro + detail + sysA + sysB + sysC + components + pager(("l7-scaleout","L7 スケールアウト"), ("l2-process","L2 製造プロセス"))
out = page(REL, "L1 施設・電力・冷却", "l1-power-cooling",
           [("レイヤー", None), ("L1 施設・電力・冷却", None)], main, refpanel)
open(os.path.join(ROOT,"layers","l1-power-cooling.html"),"w").write(out)
print("wrote layers/l1-power-cooling.html", len(out), "bytes")
