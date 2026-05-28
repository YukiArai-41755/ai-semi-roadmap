#!/usr/bin/env python3
"""Shared rendering helpers for layer pages. Extracted from the L3 reference
so every layer renders node blocks identically. Import from gen_l*.py."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G

REL = ".."
STATUS_JA = {"active":"量産/主流","emerging":"ランプ/認定","research":"R&D/試作","deprecated":"淘汰中"}

def n(id): return next(x for x in G["nodes"] if x["id"] == id)
def L(id): return next(x for x in G["layers"] if x["id"] == id)
def node_exists(id): return any(x["id"]==id for x in G["nodes"])
def is_stub(id):
    x = next((x for x in G["nodes"] if x["id"]==id), None)
    return bool(x and x.get("stub"))

def metric_bar(label, val):
    pct = int(val/5*100)
    heat = ["--heat-1","--heat-1","--heat-2","--heat-3","--heat-4","--heat-5"][val]
    return (f'<div class="metric"><div class="m-label"><span>{label}</span><span class="mono">{val}/5</span></div>'
            f'<div class="m-track"><div class="m-fill" style="width:{pct}%;background:var({heat})"></div></div></div>')

def term(label, tid):
    return f'<span class="term" data-term="{tid}">{label}</span>'

def alt_link(a):
    """Render an alt/competitor: term-span if it's a real node, else plain."""
    return term(a, a) if node_exists(a) else a

ETAG_JA = {"fact":"確立事実","infer":"推論","spec":"予測"}
def price_note(x):
    note = x.get("pricenote")
    if not note: return ""
    et = x.get("priceetag","infer")
    return (f'<div style="font-size:12.5px;color:var(--muted);margin:2px 0 4px;padding:6px 10px;'
            f'border-left:2px solid var(--gold);background:rgba(255,215,0,0.04)">'
            f'<span class="etag {et}">{ETAG_JA.get(et,et)}</span> '
            f'<strong style="color:#cdd9ec">価格・供給:</strong> {note}</div>')

def node_block(id):
    x = n(id)
    pill = f'<span class="pill {x["status"]}">{STATUS_JA.get(x["status"],x["status"])}</span>'
    players = "、".join(x.get("players",[]))
    alts = "、".join(alt_link(a) for a in x.get("alts",[]))
    ms = x.get("milestones",{})
    variants = ""
    if x.get("variants"):
        variants = ('<div class="card-meta"><div><span class="k">主要バリアント</span><span class="v">'
                    + " / ".join(x["variants"]) + '</span></div></div>')
    mats = ""
    if x.get("materials"):
        chips = []
        for m in x["materials"]:
            leg = G["material_legend"].get(m)
            if leg:
                chips.append(f'<span class="li" data-term="{m}"><span class="sw" style="background:{leg["color"]}"></span>{leg["label"]}</span>')
        if chips:
            mats = '<h4>構成部材</h4><div class="legend">' + "".join(chips) + '</div>'
    return f"""
<div class="card tech" id="{id}">
  <div class="card-head"><h3>{x["name"]} <span class="mono" style="color:var(--muted);font-size:13px">{x.get("full","")}</span></h3>{pill}</div>
  <p>{x["def"]}</p>
  {variants}
  <div class="card-meta">
    <div><span class="k">主要プレイヤー</span><span class="v">{players}</span></div>
    <div><span class="k">代替/競合</span><span class="v">{alts or "—"}</span></div>
  </div>
  {mats}
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:6px 24px;margin:12px 0">
    {metric_bar("成熟度", x.get("maturity",0))}
    {metric_bar("ボトルネック度", x.get("bottleneck",0))}
    {metric_bar("投資妙味", x.get("investment",0))}
    {metric_bar("価格決定力", x.get("pricing",0))}
    {metric_bar("供給逼迫度", x.get("tightness",0))}
  </div>
  {price_note(x)}
  <h4>マイルストーン</h4>
  <div class="tbl-wrap"><table>
    <thead><tr><th>現在 (2026)</th><th>2027</th><th>2030</th></tr></thead>
    <tbody><tr>
      <td>{ms.get("now","—")}</td><td>{ms.get("2027","—")}</td><td>{ms.get("2030","—")}</td>
    </tr></tbody>
  </table></div>
  <div class="viewbar"><a href="{REL}/cards/{id}.html" class="primary">▸ 個別カード詳細</a></div>
</div>"""

def pager(prev, nxt):
    """prev/nxt: (slug,label) or None."""
    left = (f'<a href="{prev[0]}.html"><span class="dir">◂ 前のレイヤー</span>{prev[1]}</a>'
            if prev else '<span></span>')
    right = (f'<a href="{nxt[0]}.html" style="text-align:right"><span class="dir">次のレイヤー ▸</span>{nxt[1]}</a>'
             if nxt else '<span></span>')
    return f'<div class="pager">{left}{right}</div>'
