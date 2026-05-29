/* ============================================================
   app.js — shared behavior for the whole file group
   - enriches .term spans and SVG .hot groups with styled tooltips
     sourced from data/graph.json (single source of truth)
   - wires SVG cross-section hotspots to material/tech cards
   - highlights active sidebar nav
   - mobile/touch support: tap to show tip, tap-again to navigate,
     tap-outside to close; hamburger toggle for sidebar
   Vanilla ES6, no dependencies.
   ============================================================ */
(function () {
  const REL = document.documentElement.getAttribute('data-rel') || '.';
  let GRAPH = null;

  // Touch / coarse pointer detection — coarse pointer or no hover capability.
  const IS_TOUCH = (() => {
    try {
      if (window.matchMedia && window.matchMedia('(hover: none), (pointer: coarse)').matches) return true;
    } catch (_) {}
    return ('ontouchstart' in window) || (navigator.maxTouchPoints || 0) > 0;
  })();

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
    // Trends (T-glass / T-optical / T-sys / T-mem / T-power)
    if (GRAPH.trends) {
      const t = GRAPH.trends.find(t => t.id === id);
      if (t) return {
        id: t.id, name: t.name, kind: 'trend', slug: t.slug,
        def: `トレンド軸: ${t.name}。横串で複数レイヤーを貫く動因。`
      };
    }
    if (GRAPH.material_legend && GRAPH.material_legend[id])
      return { id, name: GRAPH.material_legend[id].label, def: SYN[id] || '' };
    if (SYN[id]) return { id, name: id, def: SYN[id] };
    return null;
  }

  // Resolve a card URL for a term/material id
  function cardHref(id) {
    const n = nodeById(id);
    if (!n) return null;
    if (n.kind === 'trend' && n.slug) return `${REL}/trends/${n.slug}.html`;
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
    if (href) html += `<span class="t-more">${IS_TOUCH ? '▸ もう一度タップで詳細を開く' : '▸ 詳細カードを開く'}</span>`;
    return html;
  }

  // ----- Shared floating tooltip with viewport-edge detection -----
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

  function hideTip() {
    if (floatTip) floatTip.style.display = 'none';
    activeTipTarget = null;
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
    if (x + r.width + pad > vw) x = Math.max(pad, vw - r.width - pad); // re-clamp
    if (y + r.height + pad > vh) y = cy - r.height - 16;    // flip up
    if (y < pad) y = pad;                                   // clamp
    ft.style.left = x + 'px'; ft.style.top = y + 'px';
  }

  // Track which element currently has the tip showing (for tap-again logic)
  let activeTipTarget = null;

  function showTipFor(el, id, fb, cx, cy) {
    const ft = ensureFloatTip(); ft.innerHTML = tipHTML(id, fb);
    placeTip(ft, cx, cy);
    activeTipTarget = el;
  }

  // Dismiss on outside tap / scroll / Escape
  document.addEventListener('touchstart', (e) => {
    if (!activeTipTarget) return;
    if (activeTipTarget.contains(e.target)) return;
    hideTip();
  }, { passive: true });
  document.addEventListener('click', (e) => {
    if (!IS_TOUCH || !activeTipTarget) return;
    if (activeTipTarget.contains(e.target)) return;
    hideTip();
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hideTip(); });
  window.addEventListener('scroll', () => { if (IS_TOUCH) hideTip(); }, { passive: true });
  window.addEventListener('resize', hideTip);

  function enrichTerms() {
    document.querySelectorAll('.term[data-term]').forEach(el => {
      const id = el.getAttribute('data-term');
      const fb = el.getAttribute('data-fallback');
      // remove any legacy inline .tip (CSS version) to avoid double tooltips
      const legacy = el.querySelector('.tip'); if (legacy) legacy.remove();
      const href = cardHref(id);

      if (IS_TOUCH) {
        // Touch: first tap shows tip, second tap on same el navigates, tap-away closes.
        el.style.cursor = 'pointer';
        el.setAttribute('tabindex', '0');
        el.setAttribute('role', 'button');
        el.addEventListener('click', (e) => {
          e.preventDefault(); e.stopPropagation();
          if (activeTipTarget === el && href) {
            window.location.href = href;
            return;
          }
          const r = el.getBoundingClientRect();
          showTipFor(el, id, fb, r.left + r.width / 2, r.bottom);
        });
      } else {
        // Pointer (mouse): hover shows tip, click navigates.
        el.addEventListener('mouseenter', () => {
          const r = el.getBoundingClientRect();
          showTipFor(el, id, fb, r.left + r.width / 2, r.bottom);
        });
        el.addEventListener('mousemove', () => {
          if (activeTipTarget === el) {
            const r = el.getBoundingClientRect();
            placeTip(ensureFloatTip(), r.left + r.width / 2, r.bottom);
          }
        });
        el.addEventListener('mouseleave', hideTip);
        if (href) {
          el.style.cursor = 'pointer';
          el.addEventListener('click', () => { window.location.href = href; });
        }
      }
    });
  }

  function enrichSVGHotspots() {
    document.querySelectorAll('figure.schematic .hot[data-term]').forEach(g => {
      const id = g.getAttribute('data-term');
      const href = cardHref(id);

      if (IS_TOUCH) {
        // Touch tap-toggle. SVG <g> click works fine.
        g.style.cursor = 'pointer';
        g.addEventListener('click', (e) => {
          e.preventDefault(); e.stopPropagation();
          if (activeTipTarget === g && href) {
            window.location.href = href; return;
          }
          // Position near the bounding box center
          let cx, cy;
          try {
            const r = g.getBoundingClientRect();
            cx = r.left + r.width / 2; cy = r.bottom;
          } catch (_) {
            cx = e.clientX; cy = e.clientY;
          }
          showTipFor(g, id, null, cx, cy);
        });
      } else {
        g.addEventListener('mousemove', (e) => {
          showTipFor(g, id, null, e.clientX, e.clientY);
        });
        g.addEventListener('mouseleave', hideTip);
        if (href) {
          g.style.cursor = 'pointer';
          g.addEventListener('click', () => { window.location.href = href; });
        }
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

  // ----- Mobile sidebar drawer -----
  // The sidebar is a vertical TOC. On narrow screens (handled by CSS), it
  // becomes a slide-in drawer with a hamburger toggle in the topbar.
  function installMobileMenu() {
    const topbar = document.querySelector('.topbar');
    const sidebar = document.querySelector('.sidebar');
    if (!topbar || !sidebar) return;
    if (document.querySelector('.menu-toggle')) return; // idempotent
    const btn = document.createElement('button');
    btn.className = 'menu-toggle';
    btn.setAttribute('aria-label', 'メニュー');
    btn.setAttribute('aria-expanded', 'false');
    btn.innerHTML = '<span></span><span></span><span></span>';
    topbar.insertBefore(btn, topbar.firstChild);

    const backdrop = document.createElement('div');
    backdrop.className = 'menu-backdrop';
    document.body.appendChild(backdrop);

    function setOpen(open) {
      document.body.classList.toggle('menu-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      setOpen(!document.body.classList.contains('menu-open'));
    });
    backdrop.addEventListener('click', () => setOpen(false));
    // Auto-close on link tap inside sidebar
    sidebar.addEventListener('click', (e) => {
      if (e.target.tagName === 'A') setOpen(false);
    });
    // Close on Escape
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setOpen(false); });
  }

  // ----- Collapse nav groups on mobile so the menu fits a phone screen.
  function collapseNavGroupsOnMobile() {
    if (!IS_TOUCH && window.innerWidth > 820) return;
    document.querySelectorAll('.sidebar details.nav-group').forEach(d => {
      // Keep the group containing the active link open; collapse the others.
      const hasActive = d.querySelector('a.active');
      d.open = !!hasActive;
    });
  }

  document.addEventListener('DOMContentLoaded', async () => {
    await loadGraph();
    enrichTerms();
    enrichSVGHotspots();
    markActiveNav();
    installMobileMenu();
    collapseNavGroupsOnMobile();
    if (window.__INIT_VIEW__) window.__INIT_VIEW__(GRAPH);
  });

  // expose for view pages
  window.RoadmapData = { loadGraph, nodeById, cardHref };
})();
