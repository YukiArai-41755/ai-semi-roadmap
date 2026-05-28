#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = "."

def term(label, tid): return f'<span class="term" data-term="{tid}">{label}</span>'

LAYER_COLOR = {"L1":"#ff8c42","L2":"#c792ea","L3":"#00d9ff","L4":"#3ddc84",
               "L5":"#ffd700","L6":"#ff6b9d","L7":"#6bd5ff"}

# collect plottable nodes (exclude pure concept/sub); keep tech+material with axes
pts = []
for n in G["nodes"]:
    if "pricing" not in n or "tightness" not in n: continue
    if n.get("stub"): continue
    lyr = n.get("layer","")
    pts.append({
        "id": n["id"], "name": n["name"], "layer": lyr,
        "p": n["pricing"], "t": n["tightness"],
        "kind": n.get("kind","tech"), "etag": n.get("priceetag","infer"),
    })

# --- build scatter SVG ---
W, H = 760, 640
M = 70  # margin
plot = W - 2*M
def sx(p): return M + (p/5)*plot
def sy(t): return (H-M) - (t/5)*plot  # invert y

svg = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="価格決定力×供給逼迫マトリクス">']
svg.append(f'<rect width="{W}" height="{H}" fill="#0f1e3c"/>')
# quadrant shading (top-right = hot)
svg.append(f'<rect x="{sx(3)}" y="{sy(5)}" width="{sx(5)-sx(3)}" height="{sy(3)-sy(5)}" fill="#ffd700" opacity="0.07"/>')
svg.append(f'<text x="{sx(4.3)}" y="{sy(4.7)+4}" text-anchor="middle" fill="#ffd700" style="font-size:11px;opacity:0.7">値上げし放題 × 取り合い</text>')
# grid
for i in range(6):
    svg.append(f'<line x1="{sx(i)}" y1="{sy(0)}" x2="{sx(i)}" y2="{sy(5)}" stroke="#1e3358" stroke-width="1"/>')
    svg.append(f'<line x1="{sx(0)}" y1="{sy(i)}" x2="{sx(5)}" y2="{sy(i)}" stroke="#1e3358" stroke-width="1"/>')
    svg.append(f'<text x="{sx(i)}" y="{sy(0)+18}" text-anchor="middle" fill="#6f86ad" style="font-size:10px">{i}</text>')
    svg.append(f'<text x="{sx(0)-14}" y="{sy(i)+3}" text-anchor="middle" fill="#6f86ad" style="font-size:10px">{i}</text>')
# axis labels
svg.append(f'<text x="{W/2}" y="{H-18}" text-anchor="middle" fill="#cdd9ec" style="font-size:13px;font-weight:bold">価格決定力 (pricing power) →</text>')
svg.append(f'<text x="22" y="{H/2}" text-anchor="middle" fill="#cdd9ec" style="font-size:13px;font-weight:bold" transform="rotate(-90 22 {H/2})">供給逼迫度 (supply tightness) →</text>')

# de-overlap: simple jitter by tiny offset per identical coord
from collections import defaultdict
seen = defaultdict(int)
for pt in sorted(pts, key=lambda z:-(z["p"]+z["t"])):
    k=(pt["p"],pt["t"]); off=seen[k]; seen[k]+=1
    ang=off*2.3; import math
    dx=(off and 9+ (off*2))*math.cos(ang); dy=(off and 9+(off*2))*math.sin(ang)
    x=sx(pt["p"])+dx; y=sy(pt["t"])+dy
    col=LAYER_COLOR.get(pt["layer"],"#8da3c0")
    r=5 if pt["kind"]=="material" else 6
    href=("materials/" if pt["kind"]=="material" else "cards/")+pt["id"]+".html"
    hot = pt["p"]>=4 and pt["t"]>=4
    svg.append(f'<a href="{href}"><g class="hot" data-term="{pt["id"]}">')
    if pt["kind"]=="material":
        svg.append(f'<rect x="{x-r}" y="{y-r}" width="{2*r}" height="{2*r}" transform="rotate(45 {x} {y})" fill="{col}" stroke="{"#fff" if hot else "#0a1426"}" stroke-width="{1.5 if hot else 0.6}"/>')
    else:
        svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" stroke="{"#fff" if hot else "#0a1426"}" stroke-width="{1.5 if hot else 0.6}"/>')
    # label only hot ones to reduce clutter; stagger vertically to avoid collision
    if hot:
        ldy = 3 + (off%3 - 1)*11
        svg.append(f'<text x="{x+9}" y="{y+ldy}" fill="#e8eefc" style="font-size:9.5px">{pt["name"][:13]}</text>')
    svg.append('</g></a>')
# legend
lx=M+10; ly=M-30
svg.append(f'<text x="{lx}" y="{ly}" fill="#6f86ad" style="font-size:10px">●技術 ◆部材 / 色=レイヤー / 右上=投資妙味大 / クリックで詳細</text>')
svg.append('</svg>')
scatter = "".join(svg)

# --- compute top-right quadrant ranking ---
hot = sorted([p for p in pts if p["p"]>=4 and p["t"]>=4], key=lambda z:-(z["p"]*z["t"]))
def nlink(p):
    href=("materials/" if p["kind"]=="material" else "cards/")+p["id"]+".html"
    return f'<a href="{href}">{p["name"]}</a>'
hot_rows = "".join(
    f'<tr><td>{nlink(p)}</td><td class="mono">{p["layer"]}</td>'
    f'<td style="text-align:center">{p["p"]}</td><td style="text-align:center">{p["t"]}</td>'
    f'<td style="text-align:center;color:var(--gold);font-weight:700">{p["p"]*p["t"]}</td></tr>'
    for p in hot)

intro = f"""
<div class="eyebrow">投資分析 / 横断</div>
<h1>価格決定力 × 供給逼迫マトリクス</h1>
<p class="lead">各構成物を2軸で評価する。<strong>価格決定力</strong>=サプライヤーが値上げを下流に通せる度合い(寡占・代替困難・低BOM比率・性能律速で高い)。<strong>供給逼迫度</strong>=AI需要の増分に供給が追従できない度合い(増設リードタイム・特殊設備・既存需要からの差分で高い)。右上(両方高い)ほど、サプライヤーが利益を独占できる=投資妙味が大きい。</p>

<div class="callout invest"><span class="c-tag">分析の前提と限界</span>
<span class="etag fact">fact</span> 主要部材(HBM/CoWoS/ABF/MLCC/CCL/先端ノード)は2026年の実市況(値上げ率・寡占度・完売状況・増設計画)を検索で確認した。
<span class="etag infer">infer</span> それ以外は寡占度・代替可能性・BOM比率からの推論。
<span class="etag spec">spec</span> 価格弾力性の実数は非公開のため、各ノードの値は序列の目安であり精密値ではない。各ノードのカードに根拠と確度タグを付した。
</div>

<figure class="schematic">{scatter}<figcaption>図: 横軸=価格決定力、縦軸=供給逼迫度(0-5)。右上の網掛けが「値上げし放題かつ取り合い」の象限。色はレイヤー(L1橙/L2紫/L3シアン/L4緑/L5金/L6桃/L7空)。クリックで個別カードへ。</figcaption></figure>

<h2>読み解き — 右上象限(値上げ余地×逼迫が両高)</h2>
<p>下流の価格感応度が低く(代替不能・性能律速・寡占)、かつ供給がAI需要に追従できない部材。サプライヤー利益が最も伸びやすい。スコア=価格決定力×供給逼迫度。</p>
<div class="tbl-wrap"><table>
<thead><tr><th>構成物</th><th>レイヤー</th><th>価格決定力</th><th>供給逼迫</th><th>積</th></tr></thead>
<tbody>{hot_rows}</tbody>
</table></div>

<div class="callout warn"><span class="c-tag">最上位の構造的勝者 (stance)</span>
<span class="etag fact">fact</span> 純粋な独占/寡占×完売の三役者が突出する: <strong>{term("HBM","hbm4")}</strong>(三寡占・2026完売・HBM4で約50%プレミアム)、<strong>{term("CoWoS","cowos")}</strong>(TSMCほぼ独占・50週超のリードタイム)、<strong>{term("ABFフィルム","m-abf")}</strong>(味の素95%独占・+30%)。
<span class="etag stance">stance</span> 共通項は「<strong>1社/数社しか作れず、増設に36ヶ月+歩留り学習曲線がかかり、代替が効かない</strong>」こと。GPU本体({term("Rubin","rubin")})は価格決定力こそ最強だが、利益の相当部分をこの上流3者に吸い上げられる構造。投資妙味の純度は<strong>上流の独占部材の方が高い</strong>。
</div>

<h2>差分で見る逼迫 — なぜAIで急に足りなくなるか</h2>
<p>逼迫の本質は「既存(汎用)需要からのAI差分」が、専用供給の増設速度を上回ること。同じ部材名でも汎用品とAI用ハイエンド品で需給が真逆になる例が、構造を最もよく示す。</p>
<div class="tbl-wrap"><table>
<thead><tr><th>部材</th><th>汎用(既存)</th><th>AI用ハイエンド差分</th><th>結果</th></tr></thead>
<tbody>
<tr><td>{term("MLCC","m-mlcc")}</td><td>消費者向けは軟調・値下げ圧</td><td>AIサーバは1台でスマホの10-20倍を消費、2030に3.3倍需要</td><td>同一部材で価格二極化。高端のみ逼迫(+5-13%)</td></tr>
<tr><td>{term("HBM","hbm4")}</td><td>—(DRAMから転換)</td><td>HBMはDDR5比3倍のウェハを消費。生産がHBMへ移りDRAM全体も逼迫</td><td>DRAM供給の構造的制約・200-400%高騰の波及</td></tr>
<tr><td>{term("ABF","m-abf")}</td><td>PC向け4-8層が市場の69%</td><td>AIは11+11〜13+13層。面積×層数で需要急増</td><td>味の素フィルムが再逼迫、+30%</td></tr>
<tr><td>{term("先端ノード","gaa")}</td><td>成熟ノードは空き</td><td>N2/N3にAI殺到</td><td>N2/N3は2027+まで満杯、N7は8-16週で空き</td></tr>
</tbody></table></div>
<div class="callout"><span class="c-tag">含意 (stance)</span>
<span class="etag stance">stance</span> 「AI半導体が足りない」の正体は、汎用品も含めた全体不足ではなく、<strong>専用ハイエンド供給の局所的・構造的逼迫</strong>。汎用品(チップ抵抗・消費者MLCC・成熟ノード)はむしろ余り得る。投資判断では「AI差分が大きく、かつ専用供給が増やせない」交点を見るべき——それがこのマトリクスの右上。
</div>

<h2>過小評価の系統的再点検 (5巡)</h2>
<p>NANDの誤分類(演算律速バイアス=演算帯域を律速しない部材を機械的に過小評価)を教訓に、同型の見落としがないか観点を変えて5巡再評価した。発見:</p>
<div class="tbl-wrap"><table>
<thead><tr><th>巡</th><th>観点</th><th>発見・修正</th></tr></thead>
<tbody>
<tr><td>1</td><td>L3パッケージ技術の価格軸欠落</td><td>{term("SoIC","soic")}等がデフォルト2×2のまま放置されていた。CoWoSが5×5なのに構成技術が未評価=矛盾。SoICを5×5、{term("有機基板","org-sub")}4×4等に修正。</td></tr>
<tr><td>2</td><td>製造装置</td><td>{term("ハイブリッドボンディング装置","m-hbond")}をBESI/AMAT寡占(backlog+105%)の観点で4×4に強化。汎用成膜/エッチ装置はスコープ外と判断。</td></tr>
<tr><td>3</td><td>基板の上流素材</td><td><strong>{term("T-glass(ガラスクロス)","m-glasscloth")}を完全に見落としていた</strong>——Nittobo ~90%独占、2026最大級のボトルネック、独占純度ABF級。5×5で追加。{term("HVLP銅箔","m-copperfoil")}も。</td></tr>
<tr><td>4</td><td>演算律速バイアス再点検</td><td><strong>{term("高電圧変圧器","transformer")}——半導体ですらない究極の盲点</strong>。DCコストの10%未満だがボトルネックの100%、リードタイム5年。3×5で追加。</td></tr>
<tr><td>5</td><td>静かな寡占の消耗材</td><td>{term("EUVフォトレジスト","m-resist")}(JSR/TOK/信越/富士寡占)を4×3で追加。ただしEUVは層数減で量の逼迫は中程度、と正直に評価。CMPスラリー/特殊ガスはスコープ外。</td></tr>
</tbody></table></div>
<div class="callout warn"><span class="c-tag">再点検で見えたパターン (stance)</span>
<span class="etag stance">stance</span> 過小評価は一貫して<strong>「演算しない地味な川上」</strong>で起きた——NAND、T-glass、変圧器。いずれも目立たず、演算性能を律速しないが、独占×完売で投資妙味の右上に入る。教訓は、重要度を「演算律速」で測る癖を捨て、<strong>常に価格決定力×供給逼迫で機械的に再評価する</strong>こと。本ツールが備える2軸を、自分自身に厳格に適用し続ける必要がある。
<span class="etag fact">fact</span> 一方でスコープは保った: 汎用部品・建設資材・装置メーカー投資・CMPスラリー等は「重要だが本ツールの解像度の対象外」と線引きし、網羅リスト化による焦点のぼやけを避けた。
</div>

<div class="viewbar">
  <a href="layers/l4-memory.html" class="primary">▸ L4 メモリ(HBM)</a>
  <a href="layers/l3-packaging.html">▸ L3 パッケージ(CoWoS/ABF)</a>
  <a href="companies.html">▸ 銘柄マップ</a>
  <a href="components.html">▸ 構成部材リファレンス</a>
</div>
"""

out = page(REL, "価格・供給マトリクス", "matrix", [("価格・供給マトリクス", None)], intro)
open(os.path.join(ROOT,"matrix.html"),"w").write(out)
print("wrote matrix.html", len(out), "bytes |", len(pts), "points,", len(hot), "in hot quadrant")
