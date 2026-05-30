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

  let COMPANIES = null;
  async function loadCompanies() {
    if (COMPANIES) return COMPANIES;
    try {
      const r = await fetch(`${REL}/data/companies.json`);
      COMPANIES = await r.json();
    } catch (e) { COMPANIES = null; }
    return COMPANIES;
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

  // ============================================================
  // SEARCH — site-wide term lookup
  //
  // Index sources: graph.json nodes + graph.json trends + companies.json
  // (no full-text card body — keeps index small, matches stay focused).
  // Match: case-insensitive substring on a normalized haystack with weighted
  // scoring (name > full > ticker > def/note). Top-N shown in a dropdown.
  // Hotkey: '/' focuses the box; Esc closes.
  // ============================================================
  let SEARCH_INDEX = null;

  function normalize(s) {
    return String(s || '').toLowerCase()
      .replace(/[\s　\-_/().,:;!?'"`、。「」『』【】]/g, '');
  }

  function buildSearchIndex(g, c) {
    const idx = [];
    if (g && g.nodes) {
      for (const n of g.nodes) {
        if (n.stub) continue;
        const isMat = n.kind === 'material' || n.id.startsWith('m-');
        idx.push({
          kind: isMat ? 'material' : 'tech',
          id: n.id,
          name: n.name || n.id,
          full: n.full || '',
          hint: (n.def || n.role || '').slice(0, 120),
          href: `${REL}/${isMat ? 'materials' : 'cards'}/${n.id}.html`,
          hay: normalize([n.id, n.name, n.full, n.role, n.def].join(' '))
        });
      }
    }
    if (g && g.trends) {
      for (const t of g.trends) {
        idx.push({
          kind: 'trend', id: t.id, name: t.name, full: '',
          hint: `トレンド軸 (横串)`,
          href: `${REL}/trends/${t.slug}.html`,
          hay: normalize([t.id, t.name, t.slug].join(' '))
        });
      }
    }
    if (g && g.layers) {
      for (const L of g.layers) {
        idx.push({
          kind: 'layer', id: L.slug, name: `L${L.num} ${L.name}`, full: '',
          hint: 'レイヤー (縦階層)',
          href: `${REL}/layers/${L.slug}.html`,
          hay: normalize([L.slug, L.name, `L${L.num}`].join(' '))
        });
      }
    }
    if (c && c.companies) {
      for (const [cid, co] of Object.entries(c.companies)) {
        idx.push({
          kind: 'company', id: cid, name: co.name,
          full: co.ticker || '',
          hint: `${co.market || ''} · ${co.type || ''} · ${(co.note || '').slice(0, 90)}`,
          href: `${REL}/companies.html#co-${cid}`,
          hay: normalize([cid, co.name, co.ticker, co.market, co.type, co.note].join(' '))
        });
      }
    }
    return idx;
  }

  function search(q, max = 10) {
    if (!SEARCH_INDEX) return [];
    const nq = normalize(q);
    if (!nq) return [];
    const res = [];
    for (const it of SEARCH_INDEX) {
      const pos = it.hay.indexOf(nq);
      if (pos < 0) continue;
      // Weight: earlier match in haystack + matches at start of name field score higher.
      const nameHit = normalize(it.name).indexOf(nq);
      const tickerHit = normalize(it.full).indexOf(nq);
      let score = 1000 - pos;
      if (nameHit === 0) score += 500;
      else if (nameHit > 0) score += 200;
      if (tickerHit === 0) score += 300;
      res.push({ it, score });
    }
    res.sort((a, b) => b.score - a.score);
    return res.slice(0, max).map(r => r.it);
  }

  const KIND_LABEL = {
    tech: '技術', material: '部材', company: '銘柄', trend: 'トレンド', layer: 'レイヤー'
  };
  const KIND_COLOR = {
    tech: 'var(--st-emerging)', material: 'var(--gold)',
    company: 'var(--st-active)', trend: 'var(--st-research)', layer: 'var(--cyan-dim)'
  };

  function installSearch() {
    const topbar = document.querySelector('.topbar');
    if (!topbar || topbar.querySelector('.site-search')) return;

    const wrap = document.createElement('div');
    wrap.className = 'site-search';
    wrap.innerHTML = `
      <input type="search" class="site-search-input" placeholder="検索 (用語・銘柄・技術)  /" autocomplete="off" aria-label="サイト内検索">
      <div class="site-search-results" role="listbox" aria-label="検索結果"></div>
    `;
    // Insert after logo (but before breadcrumb if present)
    const breadcrumb = topbar.querySelector('.breadcrumb');
    if (breadcrumb) topbar.insertBefore(wrap, breadcrumb);
    else topbar.appendChild(wrap);

    const input = wrap.querySelector('.site-search-input');
    const list = wrap.querySelector('.site-search-results');

    function renderResults(q) {
      const hits = search(q, 10);
      if (!hits.length) {
        list.innerHTML = q
          ? '<div class="site-search-empty">該当なし</div>'
          : '';
        list.style.display = q ? 'block' : 'none';
        return;
      }
      list.innerHTML = hits.map((it, i) => `
        <a class="site-search-item" href="${it.href}" data-i="${i}" role="option">
          <span class="site-search-kind" style="color:${KIND_COLOR[it.kind] || 'var(--muted)'}">${KIND_LABEL[it.kind] || it.kind}</span>
          <span class="site-search-name">${escapeHtml(it.name)}${it.full ? `<span class="site-search-full"> · ${escapeHtml(it.full)}</span>` : ''}</span>
          ${it.hint ? `<span class="site-search-hint">${escapeHtml(it.hint)}</span>` : ''}
        </a>
      `).join('');
      list.style.display = 'block';
    }

    function escapeHtml(s) {
      return String(s).replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      }[c]));
    }

    input.addEventListener('input', () => renderResults(input.value));
    input.addEventListener('focus', () => { if (input.value) renderResults(input.value); });
    input.addEventListener('blur', () => {
      // Delay so click on a result lands before the dropdown is hidden.
      setTimeout(() => { list.style.display = 'none'; }, 150);
    });

    // Keyboard: arrow keys to move selection, Enter to navigate
    let activeIdx = -1;
    function highlight(i) {
      const items = list.querySelectorAll('.site-search-item');
      items.forEach((el, k) => el.classList.toggle('active', k === i));
      activeIdx = i;
      const el = items[i];
      if (el) el.scrollIntoView({ block: 'nearest' });
    }
    input.addEventListener('keydown', (e) => {
      const items = list.querySelectorAll('.site-search-item');
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (!items.length) return;
        highlight((activeIdx + 1) % items.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (!items.length) return;
        highlight((activeIdx - 1 + items.length) % items.length);
      } else if (e.key === 'Enter') {
        if (activeIdx >= 0 && items[activeIdx]) {
          window.location.href = items[activeIdx].href;
        } else if (items.length === 1) {
          window.location.href = items[0].href;
        }
      } else if (e.key === 'Escape') {
        input.blur(); list.style.display = 'none';
      }
    });

    // Global hotkey: '/' to focus (but not if typing in another input)
    document.addEventListener('keydown', (e) => {
      if (e.key !== '/') return;
      const t = e.target;
      if (t && /INPUT|TEXTAREA|SELECT/.test(t.tagName)) return;
      if (t && t.isContentEditable) return;
      e.preventDefault(); input.focus(); input.select();
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
    // Search box (loads companies.json lazily so it doesn't block initial paint).
    installSearch();
    loadCompanies().then(c => { SEARCH_INDEX = buildSearchIndex(GRAPH, c); });
  });

  // expose for view pages
  window.RoadmapData = { loadGraph, nodeById, cardHref };
})();
