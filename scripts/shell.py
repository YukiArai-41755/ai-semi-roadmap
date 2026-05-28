#!/usr/bin/env python3
"""Shared HTML shell. Every page is rendered through page() so chrome stays
identical across the whole file group. Nav is generated from graph.json layers
+ trends so adding a layer updates every page's sidebar."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = json.load(open(os.path.join(ROOT, "data", "graph.json")))

def sidebar(rel, active_slug=""):
    layers = G["layers"]; trends = G["trends"]
    parts = ['<nav class="sidebar">']
    parts.append('<details class="nav-group" open><summary>レイヤー (縦階層)</summary>')
    for L in layers:
        done = L.get("status") == "done"
        href = f'{rel}/layers/{L["slug"]}.html'
        cls = ' class="active"' if L["slug"] == active_slug else ''
        tag = '' if done else ' <span style="opacity:.4">·準備中</span>'
        parts.append(f'<a href="{href}"{cls}><span class="nav-layer-num">L{L["num"]}</span>{L["name"]}{tag}</a>')
    parts.append('</details>')
    parts.append('<details class="nav-group" open><summary>トレンド軸 (横串)</summary>')
    for T in trends:
        href = f'{rel}/trends/{T["slug"]}.html'
        cls = ' class="active"' if T["slug"] == active_slug else ''
        parts.append(f'<a href="{href}"{cls}>{T["name"]}</a>')
    parts.append('</details>')
    parts.append('<details class="nav-group" open><summary>俯瞰ビュー</summary>')
    for slug, name in [("tree","階層ツリー"),("graph","関係グラフ"),("swimlane","時間スイムレーン")]:
        href = f'{rel}/views/{slug}.html'
        cls = ' class="active"' if slug == active_slug else ''
        parts.append(f'<a href="{href}"{cls}>{name}</a>')
    parts.append('</details>')
    parts.append('<details class="nav-group" open><summary>索引・基礎</summary>')
    for slug, href, label in [
        ("basics", f"{rel}/basics.html", "★ 基礎と全体像"),
        ("matrix", f"{rel}/matrix.html", "価格・供給マトリクス"),
        ("companies", f"{rel}/companies.html", "銘柄マップ"),
        ("index", f"{rel}/index.html", "トップ / 全体マップ"),
        ("components", f"{rel}/components.html", "構成部材リファレンス"),
        ("glossary", f"{rel}/glossary.html", "用語・部材インデックス"),
    ]:
        cls = ' class="active"' if slug == active_slug else ''
        parts.append(f'<a href="{href}"{cls}>{label}</a>')
    parts.append('</details>')
    parts.append('</nav>')
    return "".join(parts)

def breadcrumb(rel, trail):
    """trail: list of (label, href_or_None)."""
    items = [f'<a href="{rel}/index.html">TOP</a>']
    for label, href in trail:
        items.append('<span class="sep">/</span>')
        if href:
            items.append(f'<a href="{href}">{label}</a>')
        else:
            items.append(f'<span class="cur">{label}</span>')
    return '<div class="breadcrumb">' + "".join(items) + '</div>'

def page(rel, title, active_slug, trail, main_html, refpanel_html=""):
    ref = f'<aside class="refpanel">{refpanel_html}</aside>' if refpanel_html else '<aside class="refpanel"></aside>'
    return f"""<!DOCTYPE html>
<html lang="ja" data-rel="{rel}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title} — AI半導体ロードマップ</title>
<link rel="stylesheet" href="{rel}/assets/base.css">
<script src="{rel}/assets/graph-data.js"></script>
<script src="{rel}/assets/app.js" defer></script>
</head>
<body>
<div class="circuit-bg"></div>
<div class="app">
  <div class="topbar">
    <span class="logo">AI-SEMI ▸ ROADMAP</span>
    {breadcrumb(rel, trail)}
  </div>
  {sidebar(rel, active_slug)}
  <main>
{main_html}
  </main>
  {ref}
  <footer class="site">
    AI半導体・データセンター技術ロードマップ · データ基準 {G['meta']['as_of']} · v{G['meta']['version']} ·
    すべての図版・カードは data/graph.json から生成
  </footer>
</div>
</body>
</html>"""

if __name__ == "__main__":
    print("shell module OK; layers:", len(G["layers"]))
