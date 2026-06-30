// Games List filter: multi-select chips (Domain/Level/Type) + dropdowns (Principle/Skill/Technique).
(function () {
  var CHIPS = [["dom","Domain"],["lv","Level"],["ty","Type"]];
  var SELS  = [["pr","Principle"],["sk","Skill"],["te","Technique"]];
  function esc(s){ return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  function uniq(a){ return Array.from(new Set(a)).sort(function(x,y){
    return (""+x).localeCompare(""+y, undefined, {numeric:true}); }); }

  function setup(games) {
    var q = document.getElementById("g-q");
    var active = { dom: new Set(), lv: new Set(), ty: new Set() }, sel = {};
    var bag = { dom: [], lv: [], ty: [], pr: [], sk: [], te: [] };
    games.forEach(function(g){
      (g.dom||[]).forEach(function(v){ bag.dom.push(v); });
      if (g.lv) bag.lv.push(g.lv); if (g.ty) bag.ty.push(g.ty);
      (g.pr||[]).forEach(function(v){ bag.pr.push(v); });
      (g.sk||[]).forEach(function(v){ bag.sk.push(v); });
      (g.te||[]).forEach(function(v){ bag.te.push(v); });
    });

    CHIPS.forEach(function(f){
      var wrap = document.querySelector("#g-"+f[0]+" .gf-chips"); if (!wrap) return;
      uniq(bag[f[0]]).forEach(function(v){
        var b = document.createElement("button"); b.type = "button"; b.className = "gf-chip";
        b.textContent = (""+v).replace(/_/g, " ");
        b.addEventListener("click", function(){
          if (active[f[0]].has(v)) { active[f[0]].delete(v); b.classList.remove("on"); }
          else { active[f[0]].add(v); b.classList.add("on"); }
          render();
        });
        wrap.appendChild(b);
      });
    });

    SELS.forEach(function(f){
      var s = document.getElementById("g-"+f[0]); sel[f[0]] = s; if (!s) return; s.innerHTML = "";
      var o = document.createElement("option"); o.value = ""; o.textContent = "All"; s.appendChild(o);
      uniq(bag[f[0]]).forEach(function(v){
        var op = document.createElement("option"); op.value = v; op.textContent = v; s.appendChild(op); });
      s.addEventListener("change", render);
    });

    q.addEventListener("input", render);
    var rb = document.getElementById("g-reset");
    if (rb) rb.addEventListener("click", function(){
      q.value = ""; Object.keys(active).forEach(function(k){ active[k].clear(); });
      var on = document.querySelectorAll(".gf-chip.on"); for (var i=0;i<on.length;i++) on[i].classList.remove("on");
      SELS.forEach(function(f){ if (sel[f[0]]) sel[f[0]].value = ""; });
      render();
    });

    var count = document.getElementById("g-count"), out = document.getElementById("games-results");
    function render() {
      var qq = (q.value||"").toLowerCase().trim();
      var pr = sel.pr ? sel.pr.value : "", sk = sel.sk ? sel.sk.value : "", te = sel.te ? sel.te.value : "";
      var rows = games.filter(function(g){
        if (active.dom.size && !(g.dom||[]).some(function(x){ return active.dom.has(x); })) return false;
        if (active.lv.size && !active.lv.has(g.lv)) return false;
        if (active.ty.size && !active.ty.has(g.ty)) return false;
        if (pr && (g.pr||[]).indexOf(pr) < 0) return false;
        if (sk && (g.sk||[]).indexOf(sk) < 0) return false;
        if (te && (g.te||[]).indexOf(te) < 0) return false;
        if (qq) { var h=(g.t+" "+(g.d||"")+" "+((g.kw||[]).join(" "))).toLowerCase();
                  if (h.indexOf(qq) < 0) return false; }
        return true;
      });
      count.innerHTML = '<strong>' + rows.length + '</strong> of ' + games.length + ' games';
      var cap = 300;
      out.innerHTML = rows.slice(0,cap).map(function(g){
        var b = []; if (g.lv) b.push(""+g.lv); if (g.dur) b.push("~"+g.dur+" min");
        if (g.ty) b.push((""+g.ty).replace(/_/g," "));
        return '<a class="game-card" href="'+g.u+'"><span class="game-title">'+esc(g.t)+'</span>'
          + '<span class="game-tag">'+esc(g.d||"")+'</span>'
          + '<span class="game-badges">'+b.map(function(x){return '<em>'+esc(x)+'</em>';}).join("")+'</span></a>';
      }).join("") || '<p class="gf-empty">No games match — try removing a filter.</p>';
      if (rows.length > cap) out.innerHTML += '<p class="game-more"><em>Showing first '+cap+'. Add filters to narrow down.</em></p>';
      out.style.opacity = 0; requestAnimationFrame(function(){ out.style.opacity = 1; });
    }
    render();
  }
  function init() {
    var root = document.getElementById("games-results");
    if (!root || root.dataset.ready) return; root.dataset.ready = "1";
    fetch("../assets/games.json").then(function(r){return r.json();})
      .then(setup).catch(function(){
        var c=document.getElementById("g-count"); if(c) c.textContent="Could not load games."; });
  }
  if (window.document$ && window.document$.subscribe) document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
