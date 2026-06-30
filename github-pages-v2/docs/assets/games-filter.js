// Games List faceted filter.
(function () {
  var FAC = [["dom","Domain"],["pr","Principle"],["sk","Skill"],["te","Technique"],
             ["cx","Complexity"],["lv","Level"],["ty","Type"]];
  function esc(s){ return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  function uniq(a){ return Array.from(new Set(a)).sort(function(x,y){
    return (""+x).localeCompare(""+y, undefined, {numeric:true}); }); }
  function setup(games) {
    var q = document.getElementById("g-q");
    var sel = {}; FAC.forEach(function(f){ sel[f[0]] = document.getElementById("g-"+f[0]); });
    var bag = {}; FAC.forEach(function(f){ bag[f[0]] = []; });
    games.forEach(function(g){
      ["dom","pr","sk","te"].forEach(function(k){ (g[k]||[]).forEach(function(v){ bag[k].push(v); }); });
      if (g.cx != null) bag.cx.push(String(g.cx));
      if (g.lv) bag.lv.push(g.lv); if (g.ty) bag.ty.push(g.ty);
    });
    FAC.forEach(function(f){
      var s = sel[f[0]]; if (!s) return; s.innerHTML = "";
      var o = document.createElement("option"); o.value=""; o.textContent = f[1]+": All"; s.appendChild(o);
      uniq(bag[f[0]]).forEach(function(v){
        var op=document.createElement("option"); op.value=v;
        op.textContent = (""+v).replace(/_/g," "); s.appendChild(op); });
    });
    var count = document.getElementById("g-count");
    var out = document.getElementById("games-results");
    function render() {
      var qq = (q.value||"").toLowerCase().trim();
      var f = {}; FAC.forEach(function(x){ f[x[0]] = sel[x[0]] ? sel[x[0]].value : ""; });
      var rows = games.filter(function(g){
        if (f.dom && (g.dom||[]).indexOf(f.dom)<0) return false;
        if (f.pr  && (g.pr ||[]).indexOf(f.pr )<0) return false;
        if (f.sk  && (g.sk ||[]).indexOf(f.sk )<0) return false;
        if (f.te  && (g.te ||[]).indexOf(f.te )<0) return false;
        if (f.cx  && String(g.cx)!==f.cx) return false;
        if (f.lv  && g.lv!==f.lv) return false;
        if (f.ty  && g.ty!==f.ty) return false;
        if (qq) { var h=(g.t+" "+(g.d||"")+" "+((g.kw||[]).join(" "))).toLowerCase();
                  if (h.indexOf(qq)<0) return false; }
        return true;
      });
      count.textContent = rows.length + " of " + games.length + " games";
      var cap = 300;
      out.innerHTML = rows.slice(0,cap).map(function(g){
        var b=[]; if(g.cx!=null) b.push("Complexity "+g.cx+"/5");
        if(g.lv) b.push((""+g.lv).replace(/_/g," "));
        if(g.dur) b.push("~"+g.dur+" min"); if(g.ty) b.push((""+g.ty).replace(/_/g," "));
        return '<a class="game-card" href="'+g.u+'"><span class="game-title">'+esc(g.t)+'</span>'
          + '<span class="game-tag">'+esc(g.d||"")+'</span>'
          + '<span class="game-badges">'+b.map(function(x){return '<em>'+esc(x)+'</em>';}).join("")+'</span></a>';
      }).join("") || '<p>No games match these filters.</p>';
      if (rows.length>cap) out.innerHTML += '<p class="game-more"><em>Showing first '+cap+' — add filters to narrow down.</em></p>';
    }
    q.addEventListener("input", render);
    FAC.forEach(function(f){ if(sel[f[0]]) sel[f[0]].addEventListener("change", render); });
    var rb=document.getElementById("g-reset");
    if(rb) rb.addEventListener("click", function(){ q.value=""; FAC.forEach(function(f){ if(sel[f[0]]) sel[f[0]].value=""; }); render(); });
    render();
  }
  function init() {
    var root = document.getElementById("games-results");
    if (!root || root.dataset.ready) return; root.dataset.ready = "1";
    fetch("../assets/games.json").then(function(r){return r.json();})
      .then(setup).catch(function(e){
        var c=document.getElementById("g-count"); if(c) c.textContent="Could not load games."; });
  }
  if (window.document$ && window.document$.subscribe) document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
