#!/usr/bin/env python3
"""Generate the 4 flagship cross-section SVGs from the shared material legend.
Each rect/region carries a class 'hot' and a <title> (native hover) PLUS a
data-term attribute so the page JS can show the richer styled tooltip and link
to the material card. Colors come from graph.json -> material_legend."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEG = json.load(open(os.path.join(ROOT, "data", "graph.json")))["material_legend"]

def c(key): return LEG[key]["color"]

# --- hatch / pattern defs reused across all SVGs ---
DEFS = """
  <defs>
    <pattern id="p-circles" width="8" height="8" patternUnits="userSpaceOnUse">
      <rect width="8" height="8" fill="#9aa7bd"/>
      <circle cx="4" cy="4" r="2.2" fill="#6c7890"/>
    </pattern>
    <pattern id="p-lines" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="6" height="6" fill="#243f6e"/>
      <line x1="0" y1="0" x2="0" y2="6" stroke="#3a5a9a" stroke-width="2"/>
    </pattern>
    <pattern id="p-vlines" width="7" height="7" patternUnits="userSpaceOnUse">
      <rect width="7" height="7" fill="#0f1e3c"/>
      <line x1="3.5" y1="0" x2="3.5" y2="7" stroke="#ffd700" stroke-width="2.4"/>
    </pattern>
    <pattern id="p-tgv" width="7" height="7" patternUnits="userSpaceOnUse">
      <rect width="7" height="7" fill="#15303a"/>
      <line x1="3.5" y1="0" x2="3.5" y2="7" stroke="#7fd4e0" stroke-width="2.2"/>
    </pattern>
    <pattern id="p-grid" width="9" height="9" patternUnits="userSpaceOnUse">
      <rect width="9" height="9" fill="#3a9bb0"/>
      <path d="M9 0H0V9" fill="none" stroke="#2a7e90" stroke-width="1"/>
    </pattern>
    <pattern id="p-pcb" width="10" height="10" patternUnits="userSpaceOnUse">
      <rect width="10" height="10" fill="#243524"/>
      <path d="M10 0H0V10" fill="none" stroke="#3a5a3a" stroke-width="1"/>
    </pattern>
    <pattern id="p-dots" width="7" height="7" patternUnits="userSpaceOnUse">
      <rect width="7" height="7" fill="#3a5c3a"/>
      <circle cx="3.5" cy="3.5" r="1.1" fill="#5c8a5c"/>
    </pattern>
    <pattern id="p-hbond" width="6" height="6" patternUnits="userSpaceOnUse">
      <rect width="6" height="6" fill="#0a2a33"/>
      <line x1="0" y1="3" x2="6" y2="3" stroke="#00d9ff" stroke-width="1.6"/>
    </pattern>
  </defs>"""

def layer(x, y, w, h, fill, label, term, sub="", text_fill="#f5f7fa"):
    """A horizontal stratum rect with centered label + hot hover."""
    s = f'<g class="hot" data-term="{term}">'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#0a1426" stroke-width="1"/>'
    s += f'<title>{label}</title>'
    ty = y + h/2 + 4
    s += f'<text x="{x+w/2}" y="{ty}" class="svg-label" text-anchor="middle" fill="{text_fill}">{label}</text>'
    if sub:
        s += f'<text x="{x+w/2}" y="{ty+13}" class="svg-label-sm" text-anchor="middle">{sub}</text>'
    s += '</g>'
    return s

def bumps(x, y, w, n, fill, r=4, term="c4", label="C4バンプ"):
    s = f'<g class="hot" data-term="{term}"><title>{label}</title>'
    gap = w/(n+1)
    for i in range(1, n+1):
        cx = x + gap*i
        s += f'<circle cx="{cx}" cy="{y}" r="{r}" fill="{fill}" stroke="#0a1426" stroke-width="0.6"/>'
    s += '</g>'
    return s

def dim(x1, y1, x2, y2, txt):
    """Dimension annotation line with text."""
    mx, my = (x1+x2)/2, (y1+y2)/2
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#4ba8c4" stroke-width="0.8" '
            f'stroke-dasharray="3 2"/><text x="{mx+4}" y="{my+3}" class="svg-dim">{txt}</text>')

# ============================================================
# 1. BASELINE FULL STACK  (organic ABF substrate + Si interposer)
# ============================================================
def band_label(x_right, y, h, text, term, color="#cfe0ff"):
    """External left-margin label with leader line into the band."""
    ty = y + h/2 + 3
    return (f'<g class="hot" data-term="{term}">'
            f'<title>{text}</title>'
            f'<text x="{x_right-8}" y="{ty}" class="svg-label" text-anchor="end" fill="{color}" style="font-size:10.5px">{text}</text>'
            f'<line x1="{x_right-4}" y1="{ty-3}" x2="{x_right+6}" y2="{ty-3}" stroke="{color}" stroke-width="0.6" opacity="0.5"/>'
            f'</g>')

def fullstack():
    W, H = 820, 560
    x0, xw = 230, 500
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="パッケージ基板フルスタック断面図">', DEFS]
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#0f1e3c"/>')
    s.append(f'<text x="{W/2}" y="26" class="svg-label" text-anchor="middle" fill="#ffd700" style="font-size:14px;font-weight:bold">パッケージ基板 フルスタック断面 (基準図)</text>')
    s.append(f'<text x="{W/2}" y="42" class="svg-label-sm" text-anchor="middle">各部材にカーソルを合わせると解説 / 部材カードへ移動</text>')

    def plain(x,y,w,h,fill,stroke="#0a1426",sw=1):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

    y = 56
    # IHS / lid
    s.append(f'<g class="hot" data-term="m-ihs"><title>IHS / リッド (ヒートスプレッダ)</title>{plain(x0,y,xw,24,c("ihs"))}</g>')
    s.append(band_label(x0, y, 24, "IHS / リッド", "m-ihs"))
    y += 24
    # TIM
    s.append(f'<g class="hot" data-term="m-tim"><title>TIM (熱界面材)</title>{plain(x0,y,xw,11,c("tim"))}</g>')
    s.append(band_label(x0, y, 11, "TIM (熱界面材)", "m-tim"))
    y += 11
    # die row: 2 HBM stacks flanking a center logic die. Center on band.
    dy, dh = y+8, 76
    cx_mid = x0 + xw/2
    ld_w = 150
    ld_x = cx_mid - ld_w/2
    s.append(f'<g class="hot" data-term="die_logic"><title>ロジックダイ (GPU/ASIC)</title>'
             f'<rect x="{ld_x}" y="{dy}" width="{ld_w}" height="{dh}" fill="{c("die_logic")}" stroke="#00d9ff" stroke-width="1.5"/>'
             f'<text x="{cx_mid}" y="{dy+dh/2+0}" class="svg-label" text-anchor="middle">ロジックダイ</text>'
             f'<text x="{cx_mid}" y="{dy+dh/2+16}" class="svg-label-sm" text-anchor="middle">GPU / ASIC</text></g>')
    hbm_w = 110
    for hx in [x0+24, x0+xw-24-hbm_w]:
        s.append(f'<g class="hot" data-term="hbm-stack"><title>HBMスタック (DRAMコアダイ×N + ベースロジックダイ + TSV)</title>')
        for k in range(8):
            yy = dy + k*7.2
            s.append(f'<rect x="{hx}" y="{yy}" width="{hbm_w}" height="6.6" fill="{c("die_dram")}" stroke="#0a1426" stroke-width="0.4"/>')
        s.append(f'<rect x="{hx}" y="{dy+58}" width="{hbm_w}" height="16" fill="#1a2a52" stroke="#00d9ff" stroke-width="0.8"/>')
        for tx in range(5):
            xx = hx + 16 + tx*20
            s.append(f'<line x1="{xx}" y1="{dy}" x2="{xx}" y2="{dy+58}" stroke="{c("tsv")}" stroke-width="1.3"/>')
        s.append(f'<text x="{hx+hbm_w/2}" y="{dy-5}" class="svg-label-sm" text-anchor="middle" fill="#ffd700">HBM</text></g>')
    s.append(band_label(x0, dy, dh, "HBM + ダイ", "die_logic", "#9fe0ff"))
    y = dy + dh
    # microbumps / hybrid bond interface
    s.append(bumps(x0, y+2, xw, 28, c("ubump"), r=3, term="m-hbond", label="マイクロバンプ / ハイブリッドボンド界面"))
    s.append(band_label(x0, y, 12, "μバンプ/HB", "m-hbond", "#9fe0ff"))
    y += 12
    # underfill
    s.append(f'<g class="hot" data-term="uf"><title>アンダーフィル</title>{plain(x0,y,xw,8,c("uf"))}</g>')
    s.append(band_label(x0, y, 8, "アンダーフィル", "uf"))
    y += 8
    # Si interposer
    s.append(f'<g class="hot" data-term="cowos"><title>Siインターポーザ (CoWoS-S)</title>{plain(x0,y,xw,32,c("si_int"))}</g>')
    for tx in range(16):
        xx = x0 + 18 + tx*30
        s.append(f'<line x1="{xx}" y1="{y}" x2="{xx}" y2="{y+32}" stroke="{c("tsv")}" stroke-width="1" opacity="0.6"/>')
    s.append(band_label(x0, y, 32, "Siインターポーザ", "cowos", "#cfe0ff"))
    s.append(f'<text x="{cx_mid}" y="{y+20}" class="svg-label-sm" text-anchor="middle" fill="#e8eefc">CoWoS-S: ダイ↔HBM高密度配線</text>')
    y += 32
    # C4 bumps
    s.append(bumps(x0, y+8, xw, 20, c("c4"), r=5, term="c4", label="C4バンプ (インターポーザ↔基板)"))
    s.append(band_label(x0, y+2, 14, "C4バンプ", "c4"))
    y += 18
    # ABF top
    s.append(f'<g class="hot" data-term="m-abf"><title>ABF ビルドアップ層 (上)</title>{plain(x0,y,xw,20,c("abf"))}</g>')
    s.append(band_label(x0, y, 20, "ABF (上)", "m-abf", "#1a2233"))
    y += 20
    # CCL core
    s.append(f'<g class="hot" data-term="m-ccl"><title>CCL コア材 (ガラスクロス+樹脂+銅箔)</title>{plain(x0,y,xw,38,c("ccl"))}</g>')
    s.append(band_label(x0, y, 38, "CCL コア材", "m-ccl"))
    s.append(f'<text x="{cx_mid}" y="{y+23}" class="svg-label-sm" text-anchor="middle">基板の機械的な芯</text>')
    y += 38
    # ABF bottom
    s.append(f'<g class="hot" data-term="m-abf"><title>ABF ビルドアップ層 (下)</title>{plain(x0,y,xw,20,c("abf"))}</g>')
    s.append(band_label(x0, y, 20, "ABF (下)", "m-abf", "#1a2233"))
    y += 20
    # solder resist
    s.append(f'<g class="hot" data-term="sr"><title>ソルダーレジスト</title>{plain(x0,y,xw,7,c("sr"))}</g>')
    s.append(band_label(x0, y, 7, "ソルダーレジスト", "sr"))
    y += 7
    # MLCC (land side) + BGA row share this band
    bga_y = y + 16
    s.append(f'<g class="hot" data-term="m-mlcc"><title>MLCC (基板裏面 / ダイ直下 = LSC, 電源デカップリング)</title>')
    for mx in [cx_mid-60, cx_mid-20, cx_mid+20, cx_mid+50]:
        s.append(f'<rect x="{mx}" y="{y+6}" width="24" height="15" fill="{c("mlcc")}" stroke="#0a1426" stroke-width="0.8"/>')
    s.append('</g>')
    s.append(band_label(x0, y+6, 15, "MLCC (LSC)", "m-mlcc", "#ff9a98"))
    s.append(f'<g class="hot" data-term="bga"><title>BGAボール (基板↔PCB)</title>')
    gap = xw/13
    for i in range(1,13):
        bx = x0+gap*i
        if cx_mid-70 <= bx <= cx_mid+80: continue
        s.append(f'<circle cx="{bx}" cy="{bga_y}" r="7" fill="{c("bga")}" stroke="#0a1426"/>')
    s.append('</g>')
    s.append(band_label(x0, bga_y-7, 14, "BGAボール", "bga"))
    y = bga_y + 14
    # PCB
    s.append(f'<g class="hot" data-term="pcb"><title>PCB マザーボード</title>{plain(x0,y,xw,26,"url(#p-pcb)")}</g>')
    s.append(band_label(x0, y, 26, "PCB マザーボード", "pcb", "#cfe0cf"))

    # right-side system brackets
    bx = x0+xw+16
    s.append(f'<line x1="{bx}" y1="{dy-4}" x2="{bx}" y2="{dy+dh+14}" stroke="#00d9ff" stroke-width="2"/>')
    s.append(f'<text x="{bx+14}" y="{dy+dh/2+6}" class="svg-label-sm" fill="#00d9ff" transform="rotate(90 {bx+14} {dy+dh/2+6})" text-anchor="middle">垂直積層系(3D)</text>')
    bz = dy+dh+18
    s.append(f'<line x1="{bx}" y1="{bz}" x2="{bx}" y2="{y+26}" stroke="#ffd700" stroke-width="2"/>')
    s.append(f'<text x="{bx+14}" y="{(bz+y)/2}" class="svg-label-sm" fill="#ffd700" transform="rotate(90 {bx+14} {(bz+y)/2})" text-anchor="middle">水平配線基盤系(2.5D/基板)</text>')
    s.append('</svg>')
    return "".join(s)

# ============================================================
# 2. INTERPOSER 3-WAY COMPARISON
# ============================================================
def interposer_compare():
    W, H = 760, 360
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="インターポーザ3方式比較断面">', DEFS]
    s.append(f'<rect width="{W}" height="{H}" fill="#0f1e3c"/>')
    s.append(f'<text x="{W/2}" y="24" class="svg-label" text-anchor="middle" fill="#ffd700" style="font-size:14px;font-weight:bold">インターポーザ / 基板 3方式比較 (同一スケール)</text>')
    panels = [
        ("CoWoS-S\nSiインターポーザ", "si_int", "cowos", "現行主流。最高密度だが\n面積=コスト・歩留り制約", "#9aa7bd"),
        ("ガラスインターポーザ\n(CoPoS)", "glass_int", "glass-int", "大面積・低損失・低CTE\n2028-29量産見込 (spec)", "#7fd4e0"),
        ("有機ABF基板のみ\n(インターポーザレス)", "abf", "org-sub", "低コスト。大型化で反り\n限界。EMIBで補完", "#cbb98a"),
    ]
    pw = 220; gap = 26; x = 30
    for title, mat, term, note, tc in panels:
        # die row
        s.append(f'<g class="hot" data-term="die_logic"><title>ロジックダイ + HBM</title>'
                 f'<rect x="{x+20}" y="60" width="{pw-90}" height="34" fill="{c("die_logic")}" stroke="#00d9ff"/>'
                 f'<rect x="{x+pw-60}" y="60" width="44" height="34" fill="{c("die_dram")}" stroke="#0a1426"/>'
                 f'<text x="{x+pw/2}" y="82" class="svg-label-sm" text-anchor="middle">die + HBM</text></g>')
        s.append(bumps(x, 100, pw, 7, c("ubump"), r=3, term="m-hbond", label="μbump"))
        # interposer / substrate
        fill = "url(#p-grid)" if mat=="glass_int" else c(mat)
        s.append(f'<g class="hot" data-term="{term}"><title>{title}</title>'
                 f'<rect x="{x}" y="112" width="{pw}" height="44" fill="{fill}" stroke="#0a1426"/></g>')
        if mat=="glass_int":
            for tx in range(8):
                s.append(f'<line x1="{x+18+tx*26}" y1="112" x2="{x+18+tx*26}" y2="156" stroke="{c("tgv")}" stroke-width="1.6"/>')
            s.append(f'<text x="{x+pw/2}" y="138" class="svg-label-sm" text-anchor="middle" fill="#0f1e3c">TGV</text>')
        elif mat=="si_int":
            for tx in range(10):
                s.append(f'<line x1="{x+14+tx*22}" y1="112" x2="{x+14+tx*22}" y2="156" stroke="{c("tsv")}" stroke-width="1.2"/>')
            s.append(f'<text x="{x+pw/2}" y="138" class="svg-label-sm" text-anchor="middle">TSV</text>')
        else:
            s.append(f'<text x="{x+pw/2}" y="138" class="svg-label-sm" text-anchor="middle" fill="#0f1e3c">ABF/CCL</text>')
        # C4 + substrate
        s.append(bumps(x, 164, pw, 10, c("c4"), r=4))
        s.append(f'<rect x="{x}" y="172" width="{pw}" height="20" fill="{c("ccl")}" stroke="#0a1426"/>')
        s.append(f'<text x="{x+pw/2}" y="186" class="svg-label-sm" text-anchor="middle">基板 (CCL/ABF)</text>')
        # title + note
        for i,line in enumerate(title.split("\n")):
            s.append(f'<text x="{x+pw/2}" y="{222+i*16}" class="svg-label" text-anchor="middle" fill="{tc}">{line}</text>')
        for i,line in enumerate(note.split("\n")):
            s.append(f'<text x="{x+pw/2}" y="{262+i*15}" class="svg-label-sm" text-anchor="middle">{line}</text>')
        x += pw + gap
    s.append('</svg>')
    return "".join(s)

# ============================================================
# 3. HBM INTERNAL STACK
# ============================================================
def hbm_stack():
    W, H = 560, 440
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="HBM内部スタック断面">', DEFS]
    s.append(f'<rect width="{W}" height="{H}" fill="#0f1e3c"/>')
    s.append(f'<text x="{W/2}" y="26" class="svg-label" text-anchor="middle" fill="#ffd700" style="font-size:14px;font-weight:bold">HBM 内部スタック断面 (12-Hi 例)</text>')
    x0, w = 150, 260; y = 50; dh = 24
    for k in range(12):
        s.append(f'<g class="hot" data-term="hbm-dram"><title>DRAMコアダイ (層 {12-k})</title>'
                 f'<rect x="{x0}" y="{y}" width="{w}" height="{dh}" fill="{c("die_dram")}" stroke="#0a1426" stroke-width="0.6"/></g>')
        # microbump gaps between dies
        if k < 11:
            for bx in range(10):
                s.append(f'<circle cx="{x0+22+bx*24}" cy="{y+dh}" r="2.4" fill="{c("ubump")}"/>')
        y += dh + 5
    # base logic die
    s.append(f'<g class="hot" data-term="hbm-base"><title>ベースロジックダイ (PHY/コントローラ)</title>'
             f'<rect x="{x0}" y="{y}" width="{w}" height="30" fill="#1a2a52" stroke="#00d9ff" stroke-width="1.4"/>'
             f'<text x="{x0+w/2}" y="{y+19}" class="svg-label-sm" text-anchor="middle" fill="#00d9ff">ベースロジックダイ (PHY)</text></g>')
    # TSV verticals through the whole stack
    for tx in range(11):
        xx = x0 + 18 + tx*22.5
        s.append(f'<line x1="{xx}" y1="50" x2="{xx}" y2="{y}" stroke="{c("tsv")}" stroke-width="1.3" opacity="0.85"/>')
    s.append(f'<text x="{x0+w+16}" y="200" class="svg-label-sm" fill="#ffd700">TSVが全層を貫通</text>')
    s.append(f'<text x="{x0-12}" y="60" class="svg-label-sm" text-anchor="end" fill="#7fb">上層</text>')
    # C4 to interposer
    y += 30
    s.append(bumps(x0, y+8, w, 10, c("c4"), r=4))
    s.append(f'<text x="{x0+w/2}" y="{y+30}" class="svg-label-sm" text-anchor="middle">→ インターポーザへ</text>')
    s.append('</svg>')
    return "".join(s)

# ============================================================
# 4. CPO CO-PACKAGED OPTICS (future)
# ============================================================
def cpo_stack():
    W, H = 720, 360
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="CPO共パッケージ光 断面">', DEFS]
    s.append(f'<rect width="{W}" height="{H}" fill="#0f1e3c"/>')
    s.append(f'<text x="{W/2}" y="26" class="svg-label" text-anchor="middle" fill="#ffd700" style="font-size:14px;font-weight:bold">CPO (共パッケージ光) 断面 — ガラス基板統合の好例</text>')
    x0, xw = 80, 560; y = 60
    # switch/compute die center + optical engines flanking
    s.append(f'<g class="hot" data-term="die_logic"><title>スイッチ/演算ダイ</title>'
             f'<rect x="{x0+200}" y="{y}" width="160" height="56" fill="{c("die_logic")}" stroke="#00d9ff" stroke-width="1.5"/>'
             f'<text x="{x0+280}" y="{y+32}" class="svg-label" text-anchor="middle">スイッチ/演算ダイ</text></g>')
    for ox in [x0+40, x0+400]:
        s.append(f'<g class="hot" data-term="cpo"><title>光エンジン (Optical Engine)</title>'
                 f'<rect x="{ox}" y="{y+10}" width="120" height="40" fill="#1a3a4a" stroke="#00d9ff" stroke-width="1.2"/>'
                 f'<text x="{ox+60}" y="{y+34}" class="svg-label-sm" text-anchor="middle" fill="#00d9ff">光エンジン</text></g>')
        # fiber out
        fx = ox-30 if ox==x0+40 else ox+150
        s.append(f'<line x1="{ox+60 if ox>x0+200 else ox+60}" y1="{y+30}" x2="{fx}" y2="{y+30}" stroke="#ffd700" stroke-width="2"/>')
    s.append(f'<text x="{x0-10}" y="{y+34}" class="svg-label-sm" text-anchor="end" fill="#ffd700">光ファイバ</text>')
    s.append(f'<text x="{x0+xw+10}" y="{y+34}" class="svg-label-sm" fill="#ffd700">光ファイバ</text>')
    y += 56
    s.append(bumps(x0, y+6, xw, 16, c("ubump"), r=3, term="m-hbond", label="μbump"))
    y += 14
    # glass interposer with embedded waveguides
    s.append(f'<g class="hot" data-term="glass-int"><title>ガラスインターポーザ (光導波路統合)</title>'
             f'<rect x="{x0}" y="{y}" width="{xw}" height="40" fill="url(#p-grid)" stroke="#0a1426"/></g>')
    # waveguide line
    s.append(f'<line x1="{x0+100}" y1="{y+20}" x2="{x0+xw-100}" y2="{y+20}" stroke="#ffd700" stroke-width="2" stroke-dasharray="6 3"/>')
    s.append(f'<text x="{x0+xw/2}" y="{y+34}" class="svg-label-sm" text-anchor="middle" fill="#0f1e3c">基板内 光導波路</text>')
    y += 40
    s.append(bumps(x0, y+8, xw, 16, c("c4"), r=4))
    s.append(f'<rect x="{x0}" y="{y+16}" width="{xw}" height="24" fill="{c("ccl")}" stroke="#0a1426"/>')
    s.append(f'<text x="{x0+xw/2}" y="{y+32}" class="svg-label-sm" text-anchor="middle">基板</text>')
    s.append(f'<text x="{W/2}" y="{H-14}" class="svg-label-sm" text-anchor="middle">電気I/Oを光に置換 → 帯域密度↑・消費電力↓。ガラスは導波路を基板内に形成できるためCPOと好相性。</text>')
    s.append('</svg>')
    return "".join(s)

def label(x, y, w, h, fill, text, term, sub="", text_fill="#f5f7fa"):
    s = f'<g class="hot" data-term="{term}">'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#0a1426" stroke-width="1"/>'
    s += f'<title>{text}</title>'
    ty = y + h/2 + 4
    s += f'<text x="{x+w/2}" y="{ty}" class="svg-label" text-anchor="middle" fill="{text_fill}">{text}</text>'
    if sub:
        s += f'<text x="{x+w/2}" y="{ty+13}" class="svg-label-sm" text-anchor="middle">{sub}</text>'
    s += '</g>'
    return s

# ============================================================
# 5. PHYSICAL SCALE NESTING (datacenter -> die)
#    The conceptual key: how the layers nest physically.
# ============================================================
def scale_nesting():
    W, H = 860, 620
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="物理的入れ子構造: データセンターからダイまで">', DEFS]
    s.append(f'<rect width="{W}" height="{H}" fill="#0f1e3c"/>')
    s.append(f'<text x="{W/2}" y="28" class="svg-label" text-anchor="middle" fill="#ffd700" style="font-size:15px;font-weight:bold">物理的な入れ子構造 — データセンターからダイまで</text>')
    s.append(f'<text x="{W/2}" y="46" class="svg-label-sm" text-anchor="middle">外側=大きい/全体システム、内側=小さい/個別部品。各枠が本ロードマップのどのレイヤーかを右に示す。</text>')

    # nested rectangles, each smaller, with scale + layer tag
    levels = [
        ("データセンター / AIファクトリー", "建屋全体・〜数百MW〜GW級", "L1 電力・冷却", "#13284d", 60, 62, 740, 540),
        ("データホール", "1部屋・数MW・多数の列(row)", "L1", "#16305c", 90, 92, 680, 480),
        ("ラック (rack)", "棚1本・〜120kW〜1MW・GPU多数", "L1/L6", "#1a3a6e", 120, 122, 560, 410),
        ("ノード / トレイ (compute tray)", "ラックに挿す引き出し1枚・CPU+GPU+メモリ", "L5/L6", "#1f4680", 150, 162, 470, 320),
        ("PCB / マザーボード", "ノード内の配線基板。部品を載せる土台", "L1/L3", "#274f8c", 180, 200, 400, 230),
        ("パッケージ (package)", "PCB上の1チップ部品。GPU+HBMを1枚に統合", "L3/L4", "#2e5a9e", 220, 238, 320, 150),
        ("ダイ (die)", "パッケージ内のシリコン本体。トランジスタの塊", "L2/L5", "#3a6bb5", 270, 270, 220, 78),
    ]
    for name, scale, tag, fill, x, y, w, h in levels:
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="#00d9ff" stroke-width="1" opacity="0.55"/>')
    # labels along the left edge of each box (top-left), tag on right
    for name, scale, tag, fill, x, y, w, h in levels:
        s.append(f'<text x="{x+10}" y="{y+17}" class="svg-label" fill="#e8eefc" style="font-size:12.5px;font-weight:bold">{name}</text>')
        s.append(f'<text x="{x+10}" y="{y+31}" class="svg-label-sm" fill="#9fb6d6">{scale}</text>')
        # layer tag pill on the right edge of each band
        s.append(f'<rect x="{x+w-86}" y="{y+6}" width="78" height="16" rx="8" fill="#0f1e3c" stroke="#ffd700" stroke-width="0.8"/>')
        s.append(f'<text x="{x+w-47}" y="{y+17}" class="svg-label-sm" fill="#ffd700" text-anchor="middle">{tag}</text>')
    # innermost: show GPU + HBM inside package level (decorative)
    s.append(f'<rect x="288" y="292" width="80" height="40" fill="#1d3563" stroke="#00d9ff" stroke-width="1"/>')
    s.append(f'<text x="328" y="316" class="svg-label-sm" text-anchor="middle" fill="#cfe0ff">GPUダイ</text>')
    for hx in [378, 412]:
        s.append(f'<rect x="{hx}" y="296" width="26" height="34" fill="{c("die_dram")}" stroke="#ffd700" stroke-width="0.6"/>')
    s.append(f'<text x="404" y="344" class="svg-label-sm" text-anchor="middle" fill="#ffd700">HBM</text>')
    s.append('</svg>')
    return "".join(s)

# ============================================================
# 6. L1 POWER CHAIN (grid -> chip), 800V HVDC vs legacy
# ============================================================
def power_chain():
    W, H = 820, 360
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="給電チェーン: 系統からチップまで">', DEFS]
    s.append(f'<rect width="{W}" height="{H}" fill="#0f1e3c"/>')
    s.append(f'<text x="{W/2}" y="26" class="svg-label" text-anchor="middle" fill="#ffd700" style="font-size:14px;font-weight:bold">給電チェーン — 系統からチップまで</text>')

    def chain(y, title, boxes, tcol):
        s.append(f'<text x="40" y="{y-8}" class="svg-label-sm" fill="{tcol}" style="font-weight:bold">{title}</text>')
        bx = 40; bw = (W-80-(len(boxes)-1)*30)/len(boxes)
        for i,(lab,term,col) in enumerate(boxes):
            s.append(f'<g class="hot" data-term="{term}"><title>{lab}</title>'
                     f'<rect x="{bx}" y="{y}" width="{bw}" height="46" rx="4" fill="{col}" stroke="#0a1426"/>'
                     f'<text x="{bx+bw/2}" y="{y+27}" class="svg-label-sm" text-anchor="middle" fill="#f5f7fa">{lab}</text></g>')
            if i < len(boxes)-1:
                ax = bx+bw
                s.append(f'<line x1="{ax+4}" y1="{y+23}" x2="{ax+26}" y2="{y+23}" stroke="#00d9ff" stroke-width="1.5" marker-end="url(#ar)"/>')
            bx += bw + 30
    s.append('<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#00d9ff"/></marker></defs>')

    legacy = [("系統 AC","power-supply","#3a4a6b"),("変圧器","power-supply","#3a4a6b"),("UPS","power-supply","#5a3a3a"),
              ("PDU","power-supply","#5a3a3a"),("PSU 54V","hvdc","#3a4a6b"),("チップ","rubin","#1d3563")]
    new = [("系統 AC","power-supply","#3a4a6b"),("ソリッドステート変圧器","hvdc","#2e6b8a"),("800V HVDC母線","hvdc","#2f9e8a"),
           ("ラック内DC-DC","hvdc","#2f9e8a"),("チップ","rubin","#1d3563")]
    chain(70, "現行 (54V AC配電): 変換段が多く損失大・銅多用", legacy, "#ff9a98")
    chain(180, "800V HVDC: 変換段削減・銅45%減・効率83%→92%+・TCO~30%減", new, "#3ddc84")
    s.append(f'<text x="{W/2}" y="300" class="svg-label-sm" text-anchor="middle" fill="#9fb6d6">高電流・低電圧(54V)はI²R損失が大きい。高電圧(800V)化で同電力を低電流で送り、変換段とUPS/PDUを削減できる。</text>')
    s.append(f'<text x="{W/2}" y="322" class="svg-label-sm" text-anchor="middle" fill="#9fb6d6">GaN/SiC(ワイドバンドギャップ半導体)が高効率・高密度な電力変換を可能にする鍵部材。</text>')
    s.append('</svg>')
    return "".join(s)

# ============================================================
# 7. L2 GAA + BACKSIDE POWER (transistor structural shift)
# ============================================================
def gaa_bspdn():
    W, H = 820, 380
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GAAナノシートと裏面給電">', DEFS]
    s.append(f'<rect width="{W}" height="{H}" fill="#0f1e3c"/>')
    s.append(f'<text x="{W/2}" y="26" class="svg-label" text-anchor="middle" fill="#ffd700" style="font-size:14px;font-weight:bold">L2の二大構造転換 — トランジスタ構造と給電面</text>')

    # Left: FinFET vs GAA nanosheet (transistor cross-section, simplified)
    s.append(f'<text x="210" y="56" class="svg-label" text-anchor="middle" fill="#00d9ff">① トランジスタ構造</text>')
    # FinFET
    s.append(f'<text x="120" y="80" class="svg-label-sm" text-anchor="middle">FinFET (現行)</text>')
    for fx in [100,116,132]:
        s.append(f'<rect x="{fx}" y="90" width="8" height="50" fill="#3a6bb5" stroke="#0a1426"/>')  # fins
    s.append(f'<rect x="92" y="104" width="56" height="22" fill="#ffd700" opacity="0.5"/>')  # gate wraps 3 sides
    s.append(f'<text x="120" y="158" class="svg-label-sm" text-anchor="middle" fill="#9fb6d6">ゲートが3面を覆う</text>')
    # GAA nanosheet
    s.append(f'<text x="300" y="80" class="svg-label-sm" text-anchor="middle" fill="#3ddc84">GAAナノシート (新)</text>')
    for ny in [96,110,124]:
        s.append(f'<rect x="276" y="{ny}" width="48" height="8" fill="#3a6bb5" stroke="#0a1426"/>')  # stacked sheets
    s.append(f'<rect x="268" y="88" width="64" height="48" fill="#ffd700" opacity="0.32"/>')  # gate wraps all around
    s.append(f'<text x="300" y="158" class="svg-label-sm" text-anchor="middle" fill="#9fb6d6">ゲートが全周を覆う→制御向上</text>')
    s.append(f'<line x1="160" y1="115" x2="250" y2="115" stroke="#00d9ff" stroke-width="1" marker-end="url(#ar2)"/>')
    s.append('<defs><marker id="ar2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#00d9ff"/></marker></defs>')

    # Right: frontside vs backside power
    s.append(f'<text x="610" y="56" class="svg-label" text-anchor="middle" fill="#00d9ff">② 給電面 (BSPDN)</text>')
    # frontside
    s.append(f'<text x="520" y="80" class="svg-label-sm" text-anchor="middle">表面給電 (現行)</text>')
    s.append(f'<rect x="470" y="90" width="100" height="40" fill="#1d3563" stroke="#00d9ff"/>')  # device
    s.append(f'<text x="520" y="114" class="svg-label-sm" text-anchor="middle">トランジスタ</text>')
    for lx in range(5):  # signal+power both on top, congested
        s.append(f'<line x1="{478+lx*22}" y1="90" x2="{478+lx*22}" y2="64" stroke="{"#ffd700" if lx%2 else "#00d9ff"}" stroke-width="2"/>')
    s.append(f'<text x="520" y="150" class="svg-label-sm" text-anchor="middle" fill="#9fb6d6">信号と電源が表面で混雑</text>')
    # backside
    s.append(f'<text x="700" y="80" class="svg-label-sm" text-anchor="middle" fill="#3ddc84">裏面給電 (SPR/PowerVia)</text>')
    s.append(f'<rect x="650" y="90" width="100" height="40" fill="#1d3563" stroke="#00d9ff"/>')
    for lx in range(5):  # signal on top
        s.append(f'<line x1="{658+lx*22}" y1="90" x2="{658+lx*22}" y2="70" stroke="#00d9ff" stroke-width="2"/>')
    for lx in range(5):  # power on bottom
        s.append(f'<line x1="{658+lx*22}" y1="130" x2="{658+lx*22}" y2="150" stroke="#ffd700" stroke-width="2.4"/>')
    s.append(f'<text x="700" y="168" class="svg-label-sm" text-anchor="middle" fill="#9fb6d6">電源を裏面へ→表面は信号専用</text>')
    s.append(f'<text x="700" y="182" class="svg-label-sm" text-anchor="middle" fill="#3ddc84">+8-10%速度 / -20%電力</text>')

    s.append(f'<line x1="410" y1="60" x2="410" y2="320" stroke="#2a3f6b" stroke-width="1"/>')
    s.append(f'<text x="{W/2}" y="250" class="svg-label" text-anchor="middle" fill="#cfe0ff" style="font-size:12px">この2つは独立した転換で、AI/HPC向け先端ノード(A16等)では両方を同時採用する</text>')
    s.append(f'<text x="{W/2}" y="276" class="svg-label-sm" text-anchor="middle" fill="#9fb6d6">凡例: <tspan fill="#00d9ff">■信号配線</tspan>  <tspan fill="#ffd700">■電源配線</tspan>  微細化単体の伸びが鈍る中、構造の工夫で性能を絞り出す段階に入った</text>')
    s.append('</svg>')
    return "".join(s)

# ============================================================
# 8. L7 SCALE-UP vs SCALE-OUT topology
# ============================================================
def scaleup_scaleout():
    W, H = 820, 400
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="scale-up と scale-out">', DEFS]
    s.append(f'<rect width="{W}" height="{H}" fill="#0f1e3c"/>')
    s.append(f'<text x="{W/2}" y="26" class="svg-label" text-anchor="middle" fill="#ffd700" style="font-size:14px;font-weight:bold">scale-up (L6) と scale-out (L7) の違い</text>')

    def gpu(x,y,col="#1d3563"):
        return (f'<rect x="{x}" y="{y}" width="34" height="26" rx="3" fill="{col}" stroke="#00d9ff" stroke-width="0.8"/>'
                f'<text x="{x+17}" y="{y+17}" class="svg-label-sm" text-anchor="middle" fill="#cfe0ff">GPU</text>')

    # scale-up: one rack, GPUs densely linked
    s.append(f'<text x="210" y="58" class="svg-label" text-anchor="middle" fill="#00d9ff">scale-up = ラック内をGPU同士で密結合</text>')
    s.append(f'<rect x="90" y="74" width="240" height="220" rx="8" fill="#16305c" stroke="#00d9ff" stroke-width="1" opacity="0.6"/>')
    s.append(f'<text x="210" y="92" class="svg-label-sm" text-anchor="middle" fill="#9fb6d6">1ラック (NVL72 / Helios)</text>')
    pos = [(120,110),(200,110),(280,110),(120,180),(200,180),(280,180),(120,250),(200,250),(280,250)]
    # all-to-all mesh lines (NVLink/UALink)
    for i in range(len(pos)):
        for j in range(i+1,len(pos)):
            s.append(f'<line x1="{pos[i][0]+17}" y1="{pos[i][1]+13}" x2="{pos[j][0]+17}" y2="{pos[j][1]+13}" stroke="#00d9ff" stroke-width="0.5" opacity="0.35"/>')
    for (x,y) in pos: s.append(gpu(x,y))
    s.append(f'<text x="210" y="312" class="svg-label-sm" text-anchor="middle" fill="#00d9ff">NVLink / UALink ・銅・最高帯域・最短距離</text>')

    # scale-out: multiple racks linked via switches
    s.append(f'<text x="610" y="58" class="svg-label" text-anchor="middle" fill="#c792ea">scale-out = ラック/クラスタ間を結ぶ</text>')
    racks = [470, 565, 660, 755]
    # switch at top
    s.append(f'<rect x="560" y="80" width="100" height="24" rx="4" fill="#3a2e5c" stroke="#c792ea"/>')
    s.append(f'<text x="610" y="96" class="svg-label-sm" text-anchor="middle" fill="#c792ea">スイッチ (Tomahawk等)</text>')
    for rx in racks:
        s.append(f'<rect x="{rx-18}" y="150" width="60" height="120" rx="5" fill="#16305c" stroke="#c792ea" stroke-width="0.8" opacity="0.6"/>')
        for gy in [160, 200, 240]:
            s.append(f'<rect x="{rx-10}" y="{gy}" width="44" height="20" rx="2" fill="#1d3563" stroke="#00d9ff" stroke-width="0.5"/>')
        s.append(f'<line x1="{rx+12}" y1="150" x2="610" y2="104" stroke="#c792ea" stroke-width="1" stroke-dasharray="4 3"/>')
        s.append(f'<text x="{rx+12}" y="284" class="svg-label-sm" text-anchor="middle" fill="#9fb6d6">ラック</text>')
    s.append(f'<text x="610" y="312" class="svg-label-sm" text-anchor="middle" fill="#c792ea">Ethernet/UEC・InfiniBand・光・10万GPU+規模</text>')

    s.append(f'<text x="{W/2}" y="350" class="svg-label-sm" text-anchor="middle" fill="#cfe0ff">同じ"GPUを繋ぐ"でも、ラック内(密・近)と ラック間(疎・遠)で技術も投資プレイヤーも別。CPOはまずscale-upから光化する。</text>')
    s.append('</svg>')
    return "".join(s)

os.makedirs(os.path.join(ROOT, "assets", "svg"), exist_ok=True)
out = {
    "fullstack.svg": fullstack(),
    "interposer-compare.svg": interposer_compare(),
    "hbm-stack.svg": hbm_stack(),
    "cpo-stack.svg": cpo_stack(),
    "scale-nesting.svg": scale_nesting(),
    "power-chain.svg": power_chain(),
    "gaa-bspdn.svg": gaa_bspdn(),
    "scaleup-scaleout.svg": scaleup_scaleout(),
}
for name, svg in out.items():
    open(os.path.join(ROOT, "assets", "svg", name), "w").write(svg)
    print(f"wrote {name} ({len(svg)} bytes)")
