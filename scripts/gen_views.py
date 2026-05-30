#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import G, page

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = ".."

# ============================================================
# VIEW 1: INDENT TREE  (hier edges only; the part-of/is-a backbone)
# ============================================================
tree_main = """
<div class="eyebrow">俯瞰ビュー 1 / 3</div>
<h1>階層ツリー</h1>
<p class="lead">part-of / is-a の親子関係だけを描く厳密な木構造。グラフビューが苦手な「親子の明示」を担当する、知識ベースの目次にして地図。</p>
<div class="viewbar">
  <a href="tree.html" class="primary">階層ツリー</a>
  <a href="graph.html">関係グラフ</a>
  <a href="swimlane.html">時間スイムレーン</a>
</div>
<div id="tree-root" style="margin-top:18px"></div>
<script>
window.__INIT_VIEW__ = function(G){
  const elRoot = document.getElementById('tree-root');
  const REL = '..';
  const byLayer = {};
  G.nodes.filter(n=>!n.stub).forEach(n=>{ (byLayer[n.layer]=byLayer[n.layer]||[]).push(n); });
  const statusColor = {active:'var(--st-active)',emerging:'var(--st-emerging)',research:'var(--st-research)',deprecated:'var(--st-deprecated)'};
  function nodeLine(n){
    const sub = n.kind==='material'?'materials':'cards';
    const dep = n.status==='deprecated'?' style="text-decoration:line-through;opacity:.7"':'';
    return `<a href="${REL}/${sub}/${n.id}.html"${dep}>
      <span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${statusColor[n.status]||'#888'};margin-right:8px"></span>
      ${n.name}</a>`;
  }
  let html='';
  G.layers.forEach(L=>{
    const kids=(byLayer[L.id]||[]);
    const open = L.status==='done'?' open':'';
    html+=`<details class="nav-group" style="border:1px solid var(--line);border-radius:6px;margin:8px 0;padding:6px 10px;background:var(--navy-2)"${open}>
      <summary style="color:var(--gold);font-size:14px"><span class="mono">L${L.num}</span> ${L.name} ${L.status!=='done'?'<span style="opacity:.4">·準備中</span>':''}</summary>`;
    // group by sub_system if present
    const subs=L.sub_systems||[];
    if(subs.length){
      subs.forEach(s=>{
        html+=`<div style="margin:6px 0 2px;color:var(--cyan);font-size:12px;font-weight:700;padding-left:8px">${s.name}</div>`;
        kids.filter(k=>k.sub===s.id).forEach(k=>{ html+=`<div style="padding-left:20px">${nodeLine(k)}</div>`; });
      });
      // materials under this layer (no sub) appended
      const noSub=kids.filter(k=>!k.sub && k.kind==='material');
      if(noSub.length){ html+=`<div style="margin:6px 0 2px;color:var(--gold);font-size:12px;padding-left:8px">部材</div>`;
        noSub.forEach(k=>{ html+=`<div style="padding-left:20px">${nodeLine(k)}</div>`; }); }
    } else {
      kids.forEach(k=>{ html+=`<div style="padding-left:12px">${nodeLine(k)}</div>`; });
    }
    html+='</details>';
  });
  // trends
  html+=`<details class="nav-group" open style="border:1px solid var(--gold-dim);border-radius:6px;margin:14px 0;padding:6px 10px;background:var(--navy-2)">
    <summary style="color:var(--gold);font-size:14px">トレンド軸 (横串 / 複数レイヤーを貫く)</summary>`;
  G.trends.forEach(t=>{ html+=`<div style="padding-left:12px"><a href="${REL}/trends/${t.slug}.html">${t.name}</a>
    <span class="mono" style="color:var(--muted);font-size:11px"> → ${t.crosses.join(', ')}</span></div>`; });
  html+='</details>';
  elRoot.innerHTML=html;
};
</script>
"""

# ============================================================
# VIEW 2: FORCE GRAPH  (canvas, dependency-free)
# ============================================================
graph_main = """
<div class="eyebrow">俯瞰ビュー 2 / 3</div>
<h1>関係グラフ</h1>
<p class="lead">全ノードを力学配置し、関係を種別で色分け。予期しない繋がりの発見用。親子はツリービューに委譲しているため、既定では横断関係(影響・世代交代・構成)のみ表示する。</p>
<div class="viewbar">
  <a href="tree.html">階層ツリー</a>
  <a href="graph.html" class="primary">関係グラフ</a>
  <a href="swimlane.html">時間スイムレーン</a>
</div>
<div class="legend" style="margin:10px 0 6px">
  <span class="li"><span class="sw" style="background:#ff8c42"></span>影響/依存</span>
  <span class="li"><span class="sw" style="background:#c792ea"></span>世代交代(置換)</span>
  <span class="li"><span class="sw" style="background:#ffd700"></span>構成部材</span>
  <span class="li"><span class="sw" style="background:#4a5f8b"></span>階層(既定で非表示)</span>
</div>
<div style="display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin-bottom:8px;font-size:12px">
  <label style="cursor:pointer"><input type="checkbox" id="show-hier"> 階層エッジも表示</label>
  <span style="color:var(--muted)">レイヤー絞込:</span>
  <select id="layer-filter" style="background:var(--navy-2);color:var(--paper);border:1px solid var(--line);border-radius:4px;padding:3px 8px;font-size:12px">
    <option value="">全て</option>
  </select>
  <span style="color:var(--muted)">●技術 ◆部材 / クリックでカード / ドラッグ移動 / ホバーで強調</span>
</div>
<canvas id="g" style="width:100%;height:600px;background:var(--navy);border:1px solid var(--line);border-radius:6px;cursor:grab"></canvas>
<script>
window.__INIT_VIEW__ = function(G){
  const REL='..';
  const cv=document.getElementById('g'), ctx=cv.getContext('2d');
  function resize(){ cv.width=cv.clientWidth*devicePixelRatio; cv.height=cv.clientHeight*devicePixelRatio; ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);}
  resize(); window.addEventListener('resize',resize);
  const W=()=>cv.clientWidth, H=()=>cv.clientHeight;
  const EC={hier:'#4a5f8b',cross:'#ff8c42',time:'#c792ea',comp:'#ffd700'};
  const nodes=[], idx={};
  function add(id,label,type,extra){ if(idx[id])return; const n={id,label,type,...extra,x:W()/2+(Math.random()-.5)*500,y:H()/2+(Math.random()-.5)*400,vx:0,vy:0}; nodes.push(n); idx[id]=n; }
  G.nodes.forEach(n=> add(n.id,n.name,n.kind==='material'?'material':'tech',{status:n.status,stub:!!n.stub,layer:n.layer}));
  G.layers.forEach(L=>(L.sub_systems||[]).forEach(s=>add(s.id,s.name,'sub',{layer:L.id})));
  G.trends.forEach(t=>add(t.id,t.name,'trend',{}));
  const allEdges=G.edges.filter(e=>idx[e.s]&&idx[e.t]);
  const statusColor={active:'#3ddc84',emerging:'#00d9ff',research:'#c792ea',deprecated:'#ff6b6b'};
  // populate layer filter
  const lf=document.getElementById('layer-filter');
  G.layers.forEach(L=>{ const o=document.createElement('option'); o.value=L.id; o.textContent='L'+L.num+' '+L.name; lf.appendChild(o); });
  let showHier=false, layerFilter='', hover=null;
  document.getElementById('show-hier').addEventListener('change',e=>{showHier=e.target.checked;});
  lf.addEventListener('change',e=>{layerFilter=e.target.value;});
  function edgeVisible(e){ if(!showHier && e.type==='hier') return false; return true; }
  function nodeVisible(n){
    if(!layerFilter) return true;
    if(n.layer===layerFilter) return true;
    // show neighbors of the filtered layer
    return allEdges.some(e=>edgeVisible(e) && ((e.s===n.id && idx[e.t].layer===layerFilter)||(e.t===n.id && idx[e.s].layer===layerFilter)));
  }
  function tick(){
    const vis=nodes.filter(nodeVisible);
    for(const a of vis){ a.fx=0; a.fy=0; }
    for(let i=0;i<vis.length;i++)for(let j=i+1;j<vis.length;j++){
      const a=vis[i],b=vis[j]; let dx=a.x-b.x,dy=a.y-b.y,d2=dx*dx+dy*dy||1,d=Math.sqrt(d2);
      const rep=5200/d2; a.fx+=dx/d*rep; a.fy+=dy/d*rep; b.fx-=dx/d*rep; b.fy-=dy/d*rep;
    }
    for(const e of allEdges){ if(!edgeVisible(e))continue; const a=idx[e.s],b=idx[e.t]; if(!nodeVisible(a)||!nodeVisible(b))continue;
      let dx=b.x-a.x,dy=b.y-a.y,d=Math.sqrt(dx*dx+dy*dy)||1; const k=(d-120)*0.008; a.fx+=dx/d*k; a.fy+=dy/d*k; b.fx-=dx/d*k; b.fy-=dy/d*k; }
    const cx=W()/2,cy=H()/2;
    for(const a of vis){ a.fx+=(cx-a.x)*0.0015; a.fy+=(cy-a.y)*0.0015;
      if(a===drag)continue; a.vx=(a.vx+a.fx)*0.86; a.vy=(a.vy+a.fy)*0.86; a.x+=a.vx; a.y+=a.vy;
      a.x=Math.max(20,Math.min(W()-20,a.x)); a.y=Math.max(20,Math.min(H()-20,a.y)); }
  }
  function neighbors(n){ const s=new Set(); allEdges.forEach(e=>{ if(!edgeVisible(e))return; if(e.s===n.id)s.add(e.t); if(e.t===n.id)s.add(e.s); }); return s; }
  function draw(){
    ctx.clearRect(0,0,W(),H());
    const hn = hover?neighbors(hover):null;
    for(const e of allEdges){ if(!edgeVisible(e))continue; const a=idx[e.s],b=idx[e.t]; if(!nodeVisible(a)||!nodeVisible(b))continue;
      const hot = hover && (e.s===hover.id||e.t===hover.id);
      ctx.strokeStyle=EC[e.type]||'#555'; ctx.lineWidth=hot?2.5:(e.type==='cross'?1.5:1);
      ctx.setLineDash(e.type==='time'?[5,4]:[]); ctx.globalAlpha=hover?(hot?0.95:0.12):0.65;
      ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke(); }
    ctx.setLineDash([]); ctx.globalAlpha=1;
    for(const a of nodes){ if(!nodeVisible(a))continue;
      const dim = hover && a!==hover && !(hn&&hn.has(a.id));
      const r=a.type==='sub'?9:a.type==='trend'?8:6;
      ctx.fillStyle = a.type==='trend'?'#ffd700': a.type==='sub'?'#15294f': (statusColor[a.status]||'#8da3c0');
      ctx.globalAlpha = a.stub?0.4:(dim?0.25:1);
      ctx.beginPath();
      if(a.type==='material'){ ctx.save(); ctx.translate(a.x,a.y); ctx.rotate(Math.PI/4); ctx.fillRect(-r,-r,2*r,2*r); ctx.restore(); }
      else { ctx.arc(a.x,a.y,r,0,7); ctx.fill(); }
      if(a.type==='sub'||a.type==='trend'){ ctx.strokeStyle='#ffd700'; ctx.lineWidth=1.5; ctx.stroke(); }
      // labels: always for sub/trend/hover+neighbors; others only when few visible or hovered
      const showLabel = a===hover || (hn&&hn.has(a.id)) || a.type==='sub' || a.type==='trend' || !hover;
      if(showLabel){ ctx.globalAlpha=dim?0.3:1; ctx.fillStyle='#cdd9ec'; ctx.font=(a===hover?'bold ':'')+'11px Segoe UI'; ctx.textAlign='center';
        ctx.fillText(a.label, a.x, a.y-10); }
      ctx.globalAlpha=1;
    }
  }
  let drag=null,dragMoved=false;
  function at(mx,my){ for(const a of nodes){ if(nodeVisible(a)&&(mx-a.x)**2+(my-a.y)**2<170)return a;} return null; }
  cv.addEventListener('mousedown',e=>{ const r=cv.getBoundingClientRect(); drag=at(e.clientX-r.left,e.clientY-r.top); dragMoved=false; cv.style.cursor='grabbing'; });
  cv.addEventListener('mousemove',e=>{ const r=cv.getBoundingClientRect(); const mx=e.clientX-r.left,my=e.clientY-r.top;
    if(drag){ drag.x=mx; drag.y=my; drag.vx=drag.vy=0; dragMoved=true; } else { hover=at(mx,my); } });
  cv.addEventListener('mouseleave',()=>{hover=null;});
  cv.addEventListener('mouseup',e=>{ if(drag&&!dragMoved){ const real=G.nodes.find(n=>n.id===drag.id);
      if(real&&!real.stub){ const sub=real.kind==='material'?'materials':'cards'; location.href=`${REL}/${sub}/${drag.id}.html`; }
      else { const tr=G.trends.find(t=>t.id===drag.id); if(tr) location.href=`${REL}/trends/${tr.slug}.html`; } }
    drag=null; cv.style.cursor='grab'; });
  (function loop(){ tick(); draw(); requestAnimationFrame(loop); })();
};
</script>
"""

# ============================================================
# VIEW 3: SWIMLANE  (layers × horizons, time edges + EOL markers)
# ============================================================
swim_main = """
<div class="eyebrow">俯瞰ビュー 3 / 3</div>
<h1>時間スイムレーン</h1>
<p class="lead">横軸=時間(現在 / 2027 / 2030)、縦帯=レイヤー。世代の派生を矢印で繋ぎ、淘汰されるテーマは明示的に「殺す」。置換ベクトル(有機基板→ガラス等)はこのビューで初めて意味を持つ。</p>
<div class="viewbar">
  <a href="tree.html">階層ツリー</a>
  <a href="graph.html">関係グラフ</a>
  <a href="swimlane.html" class="primary">時間スイムレーン</a>
</div>
<div id="swim" style="margin-top:16px"></div>
<script>
window.__INIT_VIEW__ = function(G){
  const REL='..';
  const horizons=['現在 (2026)','2027','2030'];
  const statusColor={active:'var(--st-active)',emerging:'var(--st-emerging)',research:'var(--st-research)',deprecated:'var(--st-deprecated)'};
  const el=document.getElementById('swim');
  let h='<div class="tbl-wrap"><table style="min-width:760px"><thead><tr><th style="width:170px">レイヤー</th>';
  horizons.forEach(x=>h+=`<th>${x}</th>`); h+='</tr></thead><tbody>';
  G.layers.forEach(L=>{
    const kids=G.nodes.filter(n=>n.layer===L.id&&!n.stub&&n.kind!=='material');
    if(L.status!=='done'&&kids.length===0){
      h+=`<tr><td><span class="mono">L${L.num}</span> ${L.name}</td><td colspan="3" style="opacity:.4">準備中</td></tr>`; return;
    }
    h+=`<tr><td><a href="${REL}/layers/${L.slug}.html"><span class="mono">L${L.num}</span> ${L.name}</a></td>`;
    ['now','2027','2030'].forEach(key=>{
      h+='<td>';
      kids.forEach(n=>{
        const ms=(n.milestones||{})[key];
        if(!ms)return;
        const dep=n.status==='deprecated';
        h+=`<div style="margin-bottom:8px;padding-left:8px;border-left:3px solid ${statusColor[n.status]||'#888'}">
          <a href="${REL}/cards/${n.id}.html" style="${dep?'text-decoration:line-through;opacity:.7':''}font-weight:700;font-size:12.5px">${n.name}</a>
          <div style="font-size:11.5px;color:var(--muted);line-height:1.45">${ms}</div></div>`;
      });
      h+='</td>';
    });
    h+='</tr>';
  });
  h+='</tbody></table></div>';
  // explicit replacement/death callouts from time edges
  const timeEdges=G.edges.filter(e=>e.type==='time');
  if(timeEdges.length){
    h+='<h2>世代交代ベクトル (誰が誰を置換するか)</h2><div class="tbl-wrap"><table><thead><tr><th>新</th><th></th><th>旧 (淘汰/置換される側)</th><th>注記</th></tr></thead><tbody>';
    const sub=n=>n.kind==='material'?'materials':'cards';
    timeEdges.forEach(e=>{
      const a=G.nodes.find(n=>n.id===e.s),b=G.nodes.find(n=>n.id===e.t);
      if(!a||!b)return;
      h+=`<tr><td><a href="${REL}/${sub(a)}/${a.id}.html">${a.name}</a></td><td style="color:var(--st-research)">▸ 置換 ▸</td>
        <td><a href="${REL}/${sub(b)}/${b.id}.html" style="opacity:.8">${b.name}</a></td><td>${e.label||''}</td></tr>`;
    });
    h+='</tbody></table></div>';
  }
  el.innerHTML=h;
};
</script>
"""

os.makedirs(os.path.join(ROOT,"views"), exist_ok=True)
for slug, title, main in [("tree","階層ツリー",tree_main),("graph","関係グラフ",graph_main),("swimlane","時間スイムレーン",swim_main)]:
    out = page(REL, title, slug, [("俯瞰ビュー",None),(title,None)], main)
    open(os.path.join(ROOT,"views",f"{slug}.html"),"w").write(out)
    print("wrote views/"+slug+".html", len(out))
