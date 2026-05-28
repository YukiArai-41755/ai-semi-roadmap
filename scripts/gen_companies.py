#!/usr/bin/env python3
"""Generate the neutral company/ticker exposure map.

This page intentionally stays separate from graph.json. The graph remains the
technical model; companies.json maps listed companies onto that model.
"""
import html
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = "."

DATA = json.load(open(os.path.join(ROOT, "data", "companies.json")))
COMPANIES = DATA["companies"]
NODE_BY_ID = {n["id"]: n for n in G["nodes"]}


def esc(value):
    """Escape a value for HTML text."""
    return html.escape(str(value), quote=True)


def node_link(node_id):
    """Return a link chip for an existing technical/material node."""
    n = NODE_BY_ID.get(node_id)
    if not n:
        return f'<span class="pill" style="color:var(--muted)">{esc(node_id)}</span>'
    sub = "materials" if n.get("kind") == "material" else "cards"
    return (
        f'<a class="pill" style="text-decoration:none;color:var(--cyan-dim)" '
        f'href="{sub}/{esc(node_id)}.html">{esc(n["name"])}</a>'
    )


def company_label(company_id, tag=""):
    """Render one company as a compact ticker chip."""
    c = COMPANIES.get(company_id)
    if not c:
        return f'<span class="pill" style="color:var(--st-deprecated)">未定義:{esc(company_id)}</span>'
    ticker = c["ticker"]
    color = "var(--gold)" if c.get("type") == "中核" else "var(--cyan-dim)"
    if c.get("type") == "非上場" or ticker == "非上場":
        color = "var(--muted)"
    tag_html = f' <span style="color:var(--muted)">/{esc(tag)}</span>' if tag else ""
    return (
        f'<span class="pill" style="color:{color};margin:2px 4px 2px 0">'
        f'{esc(c["name"])} <span class="mono">{esc(ticker)}</span>{tag_html}</span>'
    )


def confidence_pill(confidence):
    """Render a confidence label."""
    color = {
        "高": "var(--st-active)",
        "中": "var(--gold)",
        "低": "var(--st-research)",
    }.get(confidence, "var(--muted)")
    return f'<span class="pill" style="color:{color}">確度 {esc(confidence)}</span>'


def section_html(section):
    """Render one layer section."""
    rows = []
    for item in section["rows"]:
        chips = "".join(company_label(c["id"], c.get("tag", "")) for c in item["candidates"])
        nodes = '<div class="legend" style="margin:0">' + "".join(node_link(n) for n in item.get("nodes", [])) + "</div>"
        rows.append(
            "<tr>"
            f'<td><strong>{esc(item["theme"])}</strong><br>{nodes}</td>'
            f'<td>{chips}</td>'
            f'<td>{confidence_pill(item.get("confidence", ""))}</td>'
            f'<td style="font-size:13px;color:#cdd9ec">{esc(item["rationale"])}</td>'
            f'<td style="font-size:13px;color:var(--muted)">{esc(item["caveat"])}</td>'
            "</tr>"
        )
    body = "".join(rows)
    return f"""
<h2>{esc(section["layer"])} {esc(section["title"])}</h2>
<div class="callout"><span class="c-tag">見方</span>{esc(section["stance"])}</div>
<div class="tbl-wrap"><table>
<thead><tr><th style="width:22%">テーマ / 対応ノード</th><th style="width:34%">候補銘柄</th><th>確度</th><th>選定理由</th><th>注意点</th></tr></thead>
<tbody>{body}</tbody>
</table></div>
"""


def material_table():
    """Render a compact material-by-material lookup table."""
    rows = []
    for item in DATA["material_rows"]:
        chips = "".join(company_label(cid) for cid in item["candidates"])
        nodes = '<div class="legend" style="margin:0">' + "".join(node_link(n) for n in item.get("nodes", [])) + "</div>"
        rows.append(
            "<tr>"
            f'<td><strong>{esc(item["material"])}</strong><br>{nodes}</td>'
            f"<td>{chips}</td>"
            f'<td style="font-size:13px;color:#cdd9ec">{esc(item["comment"])}</td>'
            "</tr>"
        )
    return f"""
<h2>部材別クイックマップ</h2>
<p>材料・部品ノードだけを抜き出した早見表。レイヤー表と重複するが、部材起点で探すときはこちらが速い。</p>
<div class="tbl-wrap"><table>
<thead><tr><th style="width:26%">部材</th><th style="width:44%">候補銘柄</th><th>コメント</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table></div>
"""


def company_universe():
    """Render a deduplicated company universe table with exposure counts."""
    exposures = defaultdict(list)
    for section in DATA["sections"]:
        for row in section["rows"]:
            for cand in row["candidates"]:
                exposures[cand["id"]].append(f'{section["layer"]}: {row["theme"]}')
    for row in DATA["material_rows"]:
        for cid in row["candidates"]:
            exposures[cid].append(f'部材: {row["material"]}')

    def sort_key(cid):
        c = COMPANIES[cid]
        type_rank = {"中核": 0, "準中核": 1, "下流/内製": 2, "周辺": 3, "非上場": 4}.get(c.get("type"), 5)
        return (type_rank, c["name"])

    rows = []
    for cid in sorted(exposures, key=sort_key):
        c = COMPANIES[cid]
        exp = "<br>".join(esc(x) for x in exposures[cid][:4])
        if len(exposures[cid]) > 4:
            exp += f'<br><span style="color:var(--muted)">他 {len(exposures[cid]) - 4} 件</span>'
        rows.append(
            "<tr>"
            f'<td><strong>{esc(c["name"])}</strong><br><span class="mono" style="color:var(--gold)">{esc(c["ticker"])}</span> <span style="color:var(--muted)">{esc(c["market"])}</span></td>'
            f'<td><span class="pill" style="color:var(--cyan-dim)">{esc(c.get("type", ""))}</span></td>'
            f'<td style="font-size:13px;color:#cdd9ec">{esc(c["note"])}</td>'
            f'<td style="font-size:12.5px;color:var(--muted)">{exp}</td>'
            f'<td style="font-size:13px;color:var(--muted)">{esc(c["risk"])}</td>'
            "</tr>"
        )
    return f"""
<h2>企業ユニバース</h2>
<p>ページ内で使った企業を重複排除した一覧。ここでの「中核」は投資推奨ではなく、対象技術への事業曝露の純度を表す。</p>
<div class="tbl-wrap"><table>
<thead><tr><th style="width:18%">企業 / ティッカー</th><th>分類</th><th style="width:28%">主な曝露</th><th style="width:28%">登場箇所</th><th>主な注意点</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table></div>
"""


def references_html():
    """Render source links used for the first pass."""
    links = "".join(
        f'<span class="li">▸ <a href="{esc(r["url"])}">{esc(r["title"])}</a></span>'
        for r in DATA.get("references", [])
    )
    return f"""
<h2>参照リンク</h2>
<p>一次情報・公式IRを中心に、ティッカーや事業曝露の確認に使った代表リンク。個別の売上比率や株価水準は別途IRで更新する前提。</p>
<div class="legend">{links}</div>
"""


sections = "".join(section_html(s) for s in DATA["sections"])
main = f"""
<div class="eyebrow">企業分析 / 銘柄マップ · {esc(DATA["meta"]["as_of"])}</div>
<h1>AI半導体・データセンター<br>銘柄マップ</h1>
<p class="lead">技術ロードマップの各レイヤー・部材に対し、対応する上場企業を<strong>事業曝露</strong>として整理した。これは売買判断ではなく、どの会社がどの技術ボトルネックに紐づくかを見るためのフラットな企業分析。</p>

<div class="callout warn"><span class="c-tag">重要: 投資助言ではない</span>
本ページは買い/売り/保有、目標株価、ポートフォリオ比率を示さない。<span class="etag fact">fact</span> ティッカーと事業領域、<span class="etag infer">infer</span> 技術ロードマップとの対応関係、<span class="etag stance">stance</span> 事業曝露の純度、を分けて記載する。バリュエーション、財務安全性、需給、株価モメンタムは別分析が必要。
</div>

<div class="callout invest"><span class="c-tag">分類ルール</span>
{esc(DATA["meta"]["method"])} 「中核」は推奨順位ではなく、該当技術への売上・技術・顧客接点が濃いという意味。
</div>

<div class="viewbar">
  <a href="matrix.html" class="primary">▸ 価格・供給マトリクス</a>
  <a href="components.html">▸ 構成部材リファレンス</a>
  <a href="views/graph.html">▸ 関係グラフ</a>
</div>

{sections}
{material_table()}
{company_universe()}
{references_html()}
"""

out = page(REL, "銘柄マップ", "companies", [("銘柄マップ", None)], main)
open(os.path.join(ROOT, "companies.html"), "w").write(out)
print("wrote companies.html", len(out), "bytes")
