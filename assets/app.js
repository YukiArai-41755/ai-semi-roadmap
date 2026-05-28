/* ============================================================
   app.js — shared behavior for the whole file group
   - enriches .term spans and SVG .hot groups with styled tooltips
     sourced from data/graph.json (single source of truth)
   - wires SVG cross-section hotspots to material/tech cards
   - highlights active sidebar nav
   Vanilla ES6, no dependencies.
   ============================================================ */
(function () {
  const REL = document.documentElement.getAttribute('data-rel') || '.';
  let GRAPH = null;

  async function loadGraph() {
    if (GRAPH) return GRAPH;
    try {
      const r = await fetch(`${REL}/data/graph.json`);
      GRAPH = await r.json();
    } catch (e) {
      // Fallback: file:// fetch may be blocked. Use inlined data if present.
      if (window.__GRAPH__) GRAPH = window.__GRAPH__;
    }
    return GRAPH;
  }

  const SYN = {
    'hbm-stack': 'HBMスタック (DRAMコアダイ×N + ベースロジックダイ + TSV貫通)',
    'hbm-dram': 'DRAMコアダイ (HBM内部の記憶ダイ)',
    'hbm-base': 'ベースロジックダイ (HBM最下層のPHY/コントローラ)',
    'die_logic': 'ロジックダイ (GPU/ASIC本体)',
    'uf': 'アンダーフィル (バンプ間を充填し応力緩和する樹脂)',
    'sr': 'ソルダーレジスト (配線保護の絶縁膜)',
    'c4': 'C4バンプ (Controlled Collapse Chip Connection: インターポーザ↔基板のはんだバンプ)',
    'bga': 'BGAボール (Ball Grid Array: 基板↔PCBのはんだボール)',
    'pcb': 'PCB マザーボード (システム基板)'
  };

  function nodeById(id) {
    if (!GRAPH) return null;
    const hit = (GRAPH.nodes || []).find(n => n.id === id);
    if (hit) return hit;
    if (GRAPH.material_legend && GRAPH.material_legend[id])
      return { id, name: GRAPH.material_legend[id].label, def: SYN[id] || '' };
    if (SYN[id]) return { id, name: id, def: SYN[id] };
    return null;
  }

  // Resolve a card URL for a term/material id
  function cardHref(id) {
    const n = nodeById(id);
    if (!n) return null;
    if (n.kind === 'material' || id.startsWith('m-')) return `${REL}/materials/${id}.html`;
    if (n.kind === 'tech') return `${REL}/cards/${id}.html`;
    return null;
  }

  function tipHTML(id, fallbackText) {
    const n = nodeById(id);
    const head = n ? (n.name || id) : id;
    const body = n && n.def ? n.def : (fallbackText || '');
    const href = cardHref(id);
    let html = `<span class="t-head">${head}</span>${body}`;
    if (href) html += `<span class="t-more">▸ 詳細カードを開く</span>`;
    return html;
  }

  // Attach tooltip span to a .term element using its data-term
  // Shared floating tooltip with full viewport-edge detection (fixes clipping
  // inside tables / reference panel — the pure-CSS version could not detect edges).
  let floatTip;
  function ensureFloatTip() {
    if (floatTip) return floatTip;
    floatTip = document.createElement('div');
    floatTip.className = 'svg-floattip';
    Object.assign(floatTip.style, {
      position: 'fixed', zIndex: 9999, maxWidth: '300px', display: 'none',
      background: 'var(--navy-3)', border: '1px solid var(--cyan)',
      borderRadius: '6px', padding: '10px 12px', fontSize: '13px',
      lineHeight: '1.5', color: 'var(--paper)', boxShadow: 'var(--shadow)',
      pointerEvents: 'none', width: 'max-content'
    });
    document.body.appendChild(floatTip);
    return floatTip;
  }

  // Position the floating tip near (cx,cy) but always fully inside the viewport.
  function placeTip(ft, cx, cy) {
    ft.style.display = 'block';
    ft.style.left = '-9999px'; ft.style.top = '-9999px'; // measure first
    const r = ft.getBoundingClientRect();
    const vw = window.innerWidth, vh = window.innerHeight, pad = 8;
    let x = cx + 14, y = cy + 16;
    if (x + r.width + pad > vw) x = cx - r.width - 14;     // flip left
    if (x < pad) x = pad;                                   // clamp
    if (y + r.height + pad > vh) y = cy - r.height - 16;    // flip up
    if (y < pad) y = pad;                                   // clamp
    ft.style.left = x + 'px'; ft.style.top = y + 'px';
  }

  function enrichTerms() {
    document.querySelectorAll('.term[data-term]').forEach(el => {
      const id = el.getAttribute('data-term');
      const fb = el.getAttribute('data-fallback');
      // remove any legacy inline .tip (CSS version) to avoid double tooltips
      const legacy = el.querySelector('.tip'); if (legacy) legacy.remove();
      el.addEventListener('mouseenter', () => {
        const ft = ensureFloatTip(); ft.innerHTML = tipHTML(id, fb);
        const r = el.getBoundingClientRect();
        placeTip(ft, r.left + r.width / 2, r.bottom);
      });
      el.addEventListener('mousemove', (e) => {
        if (floatTip && floatTip.style.display === 'block') {
          const r = el.getBoundingClientRect();
          placeTip(floatTip, r.left + r.width / 2, r.bottom);
        }
      });
      el.addEventListener('mouseleave', () => { if (floatTip) floatTip.style.display = 'none'; });
      const href = cardHref(id);
      if (href) {
        el.style.cursor = 'pointer';
        el.addEventListener('click', () => { window.location.href = href; });
      }
    });
  }

  function enrichSVGHotspots() {
    document.querySelectorAll('figure.schematic .hot[data-term]').forEach(g => {
      const id = g.getAttribute('data-term');
      g.addEventListener('mousemove', (e) => {
        const ft = ensureFloatTip();
        ft.innerHTML = tipHTML(id);
        placeTip(ft, e.clientX, e.clientY);
      });
      g.addEventListener('mouseleave', () => { if (floatTip) floatTip.style.display = 'none'; });
      const href = cardHref(id);
      if (href) {
        g.style.cursor = 'pointer';
        g.addEventListener('click', () => { window.location.href = href; });
      }
    });
  }

  function markActiveNav() {
    const path = location.pathname.split('/').pop();
    document.querySelectorAll('.sidebar a').forEach(a => {
      const href = a.getAttribute('href');
      if (href && href.split('/').pop() === path) {
        a.classList.add('active');
        const grp = a.closest('details.nav-group');
        if (grp) grp.open = true;
      }
    });
  }

  document.addEventListener('DOMContentLoaded', async () => {
    await loadGraph();
    enrichTerms();
    enrichSVGHotspots();
    markActiveNav();
    if (window.__INIT_VIEW__) window.__INIT_VIEW__(GRAPH);
  });

  // expose for view pages
  window.RoadmapData = { loadGraph, nodeById, cardHref };
})();
