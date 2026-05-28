#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

# 7-layer stack as a clickable visual (HTML/CSS, mirrors physical stacking)
stack=""
for L in reversed(G["layers"]):  # top of page = top of stack (L7) down to L1
    done = L.get("status")=="done"
    n = len([x for x in G["nodes"] if x.get("layer")==L["id"] and not x.get("stub")])
    op = "1" if done else "0.55"
    badge = f'<span class="mono" style="color:var(--cyan);font-size:11px">{n} ノード</span>' if done else '<span class="mono" style="opacity:.5;font-size:11px">準備中</span>'
    star = ' ★詳細リファレンス' if L["id"]=="L3" else ''
    stack += f"""<a href="layers/{L['slug']}.html" style="display:block;text-decoration:none;opacity:{op}">
      <div style="display:flex;align-items:center;gap:14px;padding:14px 18px;margin:5px 0;border-radius:6px;
        background:linear-gradient(90deg,var(--navy-3),var(--navy-2));border:1px solid var(--line);transition:.15s"
        onmouseover="this.style.borderColor='var(--cyan)'" onmouseout="this.style.borderColor='var(--line)'">
        <span class="mono" style="color:var(--gold);font-size:20px;min-width:36px">L{L['num']}</span>
        <div style="flex:1"><div style="color:var(--paper);font-weight:700;font-size:15px">{L['name']}<span style="color:var(--gold);font-size:11px">{star}</span></div></div>
        {badge}
      </div></a>"""

trend_chips = "".join(
    f'<a href="trends/{t["slug"]}.html" class="li" style="text-decoration:none;padding:6px 12px;border:1px solid var(--gold-dim);border-radius:20px;color:var(--gold)">{t["name"]}</a>'
    for t in G["trends"])

main = f"""
<div class="eyebrow">{G['meta']['as_of']} 基準 · 投資/事業判断インプット</div>
<h1>AI半導体・データセンター<br>技術ロードマップ</h1>
<p class="lead">技術の階層構造と個々の技術理解を主軸に、時間軸(〜2030)を従属させた知識グラフ。精巧緻密な辞書であると同時に、俯瞰のための教育的成果物。</p>

<div class="callout invest"><span class="c-tag">はじめての方へ</span>
半導体やデータセンターの基礎(ラック・ダイ・GPU・物理的な大きさの入れ子・従来との違い)から入るなら、まず <a href="basics.html"><strong>★ 基礎と全体像</strong></a> を。全体像を掴んでから各レイヤーへ。投資視点では <a href="matrix.html"><strong>価格・供給マトリクス</strong></a> で「値上げ余地×逼迫」が両高の構成物を一望し、具体企業は <a href="companies.html"><strong>銘柄マップ</strong></a> で確認できる。
</div>

<div class="callout"><span class="c-tag">使い方</span>
左の3つの<strong>俯瞰ビュー</strong>で全体像を掴み、各レイヤー/トレンドページで深掘り、用語にカーソルを合わせると逐次解説と個別カードへのリンクが出ます。全7レイヤー・5トレンド軸が揃っています(L3が最も詳細なリファレンス実装)。
</div>

<h2>7レイヤー (縦階層) ＋ トレンド軸 (横串)</h2>
<p>物理ボトムアップで7層。複数レイヤーを横断する論点はトレンド軸として別管理。</p>
{stack}

<div style="margin:20px 0">
<h4>トレンド軸 (横串)</h4>
<div style="display:flex;flex-wrap:wrap;gap:8px">{trend_chips}</div>
</div>

<h2>3つの俯瞰ビュー</h2>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px">
  <a href="views/tree.html" style="text-decoration:none"><div class="card tech"><h3 style="margin:0 0 6px">階層ツリー</h3><p style="margin:0;font-size:13px;color:var(--muted)">親子(part-of)を厳密に。目次にして地図。</p></div></a>
  <a href="views/graph.html" style="text-decoration:none"><div class="card tech"><h3 style="margin:0 0 6px">関係グラフ</h3><p style="margin:0;font-size:13px;color:var(--muted)">横断関係の発見。力学配置・色分け。</p></div></a>
  <a href="views/swimlane.html" style="text-decoration:none"><div class="card material"><h3 style="margin:0 0 6px">時間スイムレーン</h3><p style="margin:0;font-size:13px;color:var(--muted)">世代交代と淘汰を時間軸で。</p></div></a>
</div>

<h2>企業分析の入口</h2>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px">
  <a href="matrix.html" style="text-decoration:none"><div class="card material"><h3 style="margin:0 0 6px">価格・供給マトリクス</h3><p style="margin:0;font-size:13px;color:var(--muted)">構成物ごとの価格決定力と供給逼迫を2軸で見る。</p></div></a>
  <a href="companies.html" style="text-decoration:none"><div class="card tech"><h3 style="margin:0 0 6px">銘柄マップ</h3><p style="margin:0;font-size:13px;color:var(--muted)">各レイヤー・部材に対応する上場企業を事業曝露として整理。</p></div></a>
</div>

<h2>設計思想</h2>
<p>全ページ・全図版・全カードは単一の <code>data/graph.json</code> から生成される。ノードを一つ足せば3ビュー全てに反映され、淘汰フラグ(<code>status: deprecated</code>)も一箇所で管理。<span class="etag fact">fact</span>確立事実 / <span class="etag infer">infer</span>推論 / <span class="etag spec">spec</span>予測 を本文中で明示。</p>
"""

out = page(".", "トップ", "", [], main)
open(os.path.join(ROOT,"index.html"),"w").write(out)
print("wrote index.html", len(out))
