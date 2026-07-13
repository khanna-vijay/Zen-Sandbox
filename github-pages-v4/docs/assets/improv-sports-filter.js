// Improv Sports Game Finder — multi-select chip facets + keyword search + live counts.
// Same engine/idiom as games-filter.js, but scoped to `is-*` element ids and its own
// data file so the two finders never collide (each no-ops on the other's page).
(function () {
  // key, label, kind ("scalar" = single value on the game object)
  var FACETS = [
    ["rt","Rating","scalar"], ["cat","Category","scalar"],
    ["en","Energy","scalar"], ["pl","Players","scalar"]
  ];
  var RT_RANK = { "Best": 0, "Excellent": 1, "Good": 2 };
  var EN_RANK = { "high": 0, "medium": 1, "low": 2 };
  function esc(s){ return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  function gvals(g, key){
    if (key === "rt")  return g.rt  ? [g.rt]  : [];
    if (key === "cat") return g.cat ? [g.cat] : [];
    if (key === "en")  return g.en  ? [g.en]  : [];
    if (key === "pl")  return g.pl  ? [g.pl]  : [];
    return [];
  }
  function sortVals(key, vals){
    if (key === "rt") return vals.slice().sort(function(a,b){
      return (RT_RANK[a]==null?9:RT_RANK[a]) - (RT_RANK[b]==null?9:RT_RANK[b]); });
    if (key === "en") return vals.slice().sort(function(a,b){
      return (EN_RANK[a]==null?9:EN_RANK[a]) - (EN_RANK[b]==null?9:EN_RANK[b]); });
    return vals.slice().sort(function(x,y){
      return (""+x).localeCompare(""+y, undefined, {numeric:true}); });
  }

  var STORE_KEY = "zs-improv-sports-filter";
  function loadState(){ try { return JSON.parse(sessionStorage.getItem(STORE_KEY)) || {}; } catch (e) { return {}; } }
  function saveState(active, qval){
    try {
      var s = { q: qval || "" };
      FACETS.forEach(function(f){ s[f[0]] = Array.from(active[f[0]]); });
      sessionStorage.setItem(STORE_KEY, JSON.stringify(s));
    } catch (e) {}
  }

  function setup(games) {
    var q = document.getElementById("is-q") || { value: "", addEventListener: function () {} };
    var active = {}, chipEls = {};
    FACETS.forEach(function(f){ active[f[0]] = new Set(); chipEls[f[0]] = []; });

    var saved = loadState();
    FACETS.forEach(function(f){
      var avail = {};
      games.forEach(function(g){ gvals(g, f[0]).forEach(function(v){ avail[v] = 1; }); });
      (saved[f[0]] || []).forEach(function(v){ if (avail[v]) active[f[0]].add(v); });
    });
    if (saved.q) q.value = saved.q;

    FACETS.forEach(function(f){
      var key = f[0], wrap = document.querySelector("#is-"+key+" .gf-chips"); if (!wrap) return;
      var vals = [], seen = {};
      games.forEach(function(g){ gvals(g, key).forEach(function(v){
        if (!seen[v]) { seen[v] = 1; vals.push(v); } }); });
      sortVals(key, vals).forEach(function(v){
        var label = (""+v).replace(/_/g, " ");
        var b = document.createElement("button"); b.type = "button"; b.className = "gf-chip";
        if (active[key].has(v)) b.classList.add("on");
        b.innerHTML = esc(label) + '<span class="gf-n"></span>';
        b.addEventListener("click", function(){
          if (active[key].has(v)) { active[key].delete(v); b.classList.remove("on"); }
          else { active[key].add(v); b.classList.add("on"); }
          render();
        });
        wrap.appendChild(b);
        chipEls[key].push({ v: v, el: b, n: b.querySelector(".gf-n") });
      });
    });

    q.addEventListener("input", render);
    var rb = document.getElementById("is-reset");
    if (rb) rb.addEventListener("click", function(){
      q.value = ""; FACETS.forEach(function(f){ active[f[0]].clear(); });
      var on = document.querySelectorAll("#is-results, .gf .gf-chip.on");
      document.querySelectorAll(".gf .gf-chip.on").forEach(function(el){ el.classList.remove("on"); });
      render();
    });

    var count = document.getElementById("is-count"), out = document.getElementById("is-results");
    function haystack(g){ return (g.t+" "+(g.d||"")+" "+((g.kw||[]).join(" "))).toLowerCase(); }
    function matchFacet(g, key){
      var a = active[key]; if (!a.size) return true;
      return gvals(g, key).some(function(v){ return a.has(v); });
    }
    function matchAll(g, exceptKey, qq){
      if (qq && haystack(g).indexOf(qq) < 0) return false;
      for (var i=0;i<FACETS.length;i++){ var k = FACETS[i][0];
        if (k === exceptKey) continue; if (!matchFacet(g, k)) return false; }
      return true;
    }

    function render(){
      var qq = (q.value||"").toLowerCase().trim();
      var rows = games.filter(function(g){ return matchAll(g, null, qq); });

      FACETS.forEach(function(f){
        var key = f[0];
        var base = games.filter(function(g){ return matchAll(g, key, qq); });
        var cnt = {};
        base.forEach(function(g){ gvals(g, key).forEach(function(v){ cnt[v] = (cnt[v]||0) + 1; }); });
        chipEls[key].forEach(function(c){
          var n = cnt[c.v] || 0;
          c.n.textContent = " (" + n + ")";
          if (n === 0 && !active[key].has(c.v)) c.el.classList.add("zero");
          else c.el.classList.remove("zero");
        });
      });

      count.innerHTML = '<strong>' + rows.length + '</strong> of ' + games.length + ' games';
      var cap = 400;
      out.innerHTML = rows.slice(0,cap).map(function(g){
        var b = [];
        if (g.rt)  b.push({ t: g.rt, c: "gb-rt" });
        if (g.cat) b.push({ t: g.cat, c: "" });
        if (g.dur) b.push({ t: "~"+g.dur+" min", c: "" });
        if (g.en)  b.push({ t: g.en, c: "" });
        return '<a class="game-card" href="'+g.u+'"><span class="game-title">'+esc(g.t)+'</span>'
          + '<span class="game-tag">'+esc(g.d||"")+'</span>'
          + '<span class="game-badges">'+b.map(function(x){
              return '<em class="'+x.c+'">'+esc(x.t)+'</em>'; }).join("")+'</span></a>';
      }).join("") || '<p class="gf-empty">No games match — try removing a filter.</p>';
      if (rows.length > cap) out.innerHTML += '<p class="game-more"><em>Showing first '+cap+'. Add filters to narrow down.</em></p>';
      saveState(active, q.value);
      out.style.opacity = 0; requestAnimationFrame(function(){ out.style.opacity = 1; });
    }
    render();
  }
  function init() {
    var root = document.getElementById("is-results");
    if (!root || root.dataset.ready) return; root.dataset.ready = "1";
    fetch("../assets/improv-sports.json").then(function(r){return r.json();})
      .then(setup).catch(function(){
        var c=document.getElementById("is-count"); if(c) c.textContent="Could not load games."; });
  }
  if (window.document$ && window.document$.subscribe) document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
