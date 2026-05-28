#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = ".."
STATUS_JA = {"active":"量産/主流","emerging":"ランプ/認定","research":"R&D/試作","deprecated":"淘汰中"}

def layer_name(lid):
    L = next((x for x in G["layers"] if x["id"]==lid), None)
    return f'L{L["num"]} {L["name"]}' if L else lid
def layer_slug(lid):
    L = next((x for x in G["layers"] if x["id"]==lid), None)
    return L["slug"] if L else "l3-packaging"

def edges_for(nid):
    outs = [e for e in G["edges"] if e["s"]==nid]
    ins  = [e for e in G["edges"] if e["t"]==nid]
    return outs, ins

def mat_has_card(mkey):
    """A material card exists only for nodes of kind material with that id."""
    return any(nn["id"]==mkey and nn.get("kind")=="material" for nn in G["nodes"])

def link_node(nid):
    """Return an <a> to the card/material/trend/layer for nid, or plain text.
    Only links if a destination page actually exists (non-stub)."""
    nm = next((x for x in G["nodes"] if x["id"]==nid), None)
    if nm and not nm.get("stub"):
        sub = "materials" if nm.get("kind")=="material" else "cards"
        return f'<a href="{REL}/{sub}/{nid}.html">{nm["name"]}</a>'
    if nm and nm.get("stub"):
        return f'{nm["name"]}<span class="mono" style="color:var(--muted);font-size:11px"> (準備中)</span>'
    leg = G["material_legend"].get(nid)
    if leg:
        return f'<a href="{REL}/materials/{nid}.html">{leg["label"]}</a>' if mat_has_card(nid) else leg["label"]
    tr = next((t for t in G["trends"] if t["id"]==nid), None)
    if tr: return f'<a href="{REL}/trends/{tr["slug"]}.html">{tr["name"]}（トレンド軸）</a>'
    sub = next((s for L in G["layers"] for s in L.get("sub_systems",[]) if s["id"]==nid), None)
    if sub: return sub["name"]
    L = next((x for x in G["layers"] if x["id"]==nid), None)
    if L: return f'<a href="{REL}/layers/{L["slug"]}.html">{layer_name(nid)}</a>'
    return nid

EDGE_JA = {"hier":"階層","cross":"影響/依存","time":"世代交代","comp":"構成部材"}

def metric_bar(label, val):
    pct = int(val/5*100)
    heat = ["--heat-1","--heat-1","--heat-2","--heat-3","--heat-4","--heat-5"][val]
    return (f'<div class="metric"><div class="m-label"><span>{label}</span><span class="mono">{val}/5</span></div>'
            f'<div class="m-track"><div class="m-fill" style="width:{pct}%;background:var({heat})"></div></div></div>')

_ETAG_JA = {"fact":"確立事実","infer":"推論","spec":"予測"}
def price_note(x):
    note = x.get("pricenote")
    if not note: return ""
    et = x.get("priceetag","infer")
    return (f'<div style="font-size:12.5px;color:var(--muted);margin:2px 0 8px;padding:6px 10px;'
            f'border-left:2px solid var(--gold);background:rgba(255,215,0,0.04)">'
            f'<span class="etag {et}">{_ETAG_JA.get(et,et)}</span> '
            f'<strong style="color:#cdd9ec">価格・供給:</strong> {note}</div>')

def tech_card(x):
    nid = x["id"]
    outs, ins = edges_for(nid)
    ms = x.get("milestones",{})
    rel_rows = ""
    for e in outs:
        if e["t"] in ("L3-A","L3-B"): continue
        rel_rows += f'<tr><td>{EDGE_JA.get(e["type"],e["type"])}</td><td>→ {link_node(e["t"])}</td><td>{e.get("label","")}</td></tr>'
    for e in ins:
        rel_rows += f'<tr><td>{EDGE_JA.get(e["type"],e["type"])}</td><td>← {link_node(e["s"])}</td><td>{e.get("label","")}</td></tr>'
    mats = ""
    if x.get("materials"):
        chips=[]
        for m in x["materials"]:
            leg=G["material_legend"].get(m)
            if not leg: continue
            label = f'<a href="{REL}/materials/{m}.html">{leg["label"]}</a>' if mat_has_card(m) else leg["label"]
            chips.append(f'<span class="li"><span class="sw" style="background:{leg["color"]}"></span>{label}</span>')
        mats = '<h4>構成部材</h4><div class="legend">'+"".join(chips)+'</div>'
    variants = ""
    if x.get("variants"):
        variants = '<h4>主要バリアント</h4><ul>'+ "".join(f'<li>{v}</li>' for v in x["variants"]) +'</ul>'
    main = f"""
<div class="eyebrow">技術カード / {layer_name(x["layer"])}</div>
<h1>{x["name"]}</h1>
<p class="lead">{x.get("full","")}</p>
<div class="card-head" style="margin-bottom:14px"><span class="pill {x["status"]}">{STATUS_JA.get(x["status"],x["status"])}</span></div>
<p>{x["def"]}</p>
{variants}
<h4>投資判断メトリクス</h4>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:6px 24px;margin:12px 0">
  {metric_bar("成熟度", x.get("maturity",0))}
  {metric_bar("ボトルネック度", x.get("bottleneck",0))}
  {metric_bar("投資妙味", x.get("investment",0))}
  {metric_bar("価格決定力", x.get("pricing",0))}
  {metric_bar("供給逼迫度", x.get("tightness",0))}
</div>
{price_note(x)}
<div class="card-meta">
  <div><span class="k">主要プレイヤー</span><span class="v">{"、".join(x.get("players",[]))}</span></div>
  <div><span class="k">代替/競合</span><span class="v">{"、".join(link_node(a) for a in x.get("alts",[])) or "—"}</span></div>
</div>
{mats}
<h4>マイルストーン</h4>
<div class="tbl-wrap"><table>
<thead><tr><th>現在 (2026)</th><th>2027</th><th>2030</th></tr></thead>
<tbody><tr><td>{ms.get("now","—")}</td><td>{ms.get("2027","—")}</td><td>{ms.get("2030","—")}</td></tr></tbody>
</table></div>
<h4>関係(知識グラフ)</h4>
<div class="tbl-wrap"><table><thead><tr><th>種別</th><th>関係先</th><th>注記</th></tr></thead><tbody>{rel_rows or '<tr><td colspan=3>—</td></tr>'}</tbody></table></div>
<div class="viewbar"><a href="{REL}/layers/{layer_slug(x["layer"])}.html" class="primary">▸ レイヤーページへ戻る</a><a href="{REL}/views/graph.html">▸ 関係グラフで見る</a></div>
"""
    return page(REL, x["name"], layer_slug(x["layer"]),
                [("技術カード",None),(x["name"],None)], main)

def material_card(x):
    nid = x["id"]
    leg_key = nid  # material legend uses same id? legend keys are short; map by props
    outs, ins = edges_for(nid)
    used_by = [link_node(e["s"]) for e in ins if e["type"]=="comp"]
    props = x.get("props",{})
    prop_rows = "".join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in props.items())
    main = f"""
<div class="eyebrow">部材カード / {x.get("etype","")}</div>
<h1>{x["name"]}</h1>
<p class="lead">{x.get("full","")}</p>
<p>{x["def"]}</p>
<div class="card-meta">
  <div><span class="k">役割</span><span class="v">{x.get("role","")}</span></div>
  <div><span class="k">区分</span><span class="v">{x.get("etype","")}</span></div>
</div>
<h4>物性・特性</h4>
<div class="tbl-wrap"><table><tbody>{prop_rows or '<tr><td>—</td></tr>'}</tbody></table></div>
<h4>価格・供給の感応度</h4>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:6px 24px;margin:8px 0">
  {metric_bar("価格決定力", x.get("pricing",0))}
  {metric_bar("供給逼迫度", x.get("tightness",0))}
</div>
{price_note(x)}
<div class="card-meta">
  <div><span class="k">主要サプライヤ</span><span class="v">{"、".join(x.get("suppliers",[]))}</span></div>
  <div><span class="k">代替材</span><span class="v">{"、".join(link_node(a) if any(nn["id"]==a for nn in G["nodes"]) else a for a in x.get("alts",[])) or "—"}</span></div>
</div>
<h4>この部材を使う技術</h4>
<p>{("、".join(used_by)) if used_by else "—"}</p>
<div class="viewbar"><a href="{REL}/layers/l3-packaging.html" class="primary">▸ L3 断面図で位置を見る</a><a href="{REL}/glossary.html">▸ 用語インデックス</a></div>
"""
    return page(REL, x["name"], "l3-packaging",
                [("部材カード",None),(x["name"],None)], main)

os.makedirs(os.path.join(ROOT,"cards"), exist_ok=True)
os.makedirs(os.path.join(ROOT,"materials"), exist_ok=True)
nc=nm=0
for x in G["nodes"]:
    if x.get("stub"): continue
    if x.get("kind")=="material":
        open(os.path.join(ROOT,"materials",f'{x["id"]}.html'),"w").write(material_card(x)); nm+=1
    else:
        open(os.path.join(ROOT,"cards",f'{x["id"]}.html'),"w").write(tech_card(x)); nc+=1
print(f"wrote {nc} tech cards, {nm} material cards")
