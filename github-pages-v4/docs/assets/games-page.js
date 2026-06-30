// Game-page enhancements: body class, section icons, prev/next + keyboard nav.
(function () {
  var ICONS = {
    "overview":"📖","what it trains":"🎯","objective":"🎯","at a glance":"📊","setup":"🔧",
    "how to play":"▶️","facilitation notes":"🧑‍🏫","variations":"🔀","debrief":"💬",
    "safety & inclusion":"🛡️","safety and inclusion":"🛡️","why it works":"✨"
  };
  var games = null, fetching = false;
  function esc(s){ return (s||"").replace(/[&<>\"]/g,function(c){
    return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]; }); }
  function curBase(){
    var m = location.pathname.match(/\/games\/([^\/]+)\/?$/);
    return (m && m[1] !== "index") ? m[1] : null;
  }
  function decorate(){
    document.querySelectorAll(".md-content .md-typeset h2").forEach(function(h){
      if (h.dataset.gi) return;
      var key = (h.textContent||"").toLowerCase().replace(/\s*¶\s*$/,"").trim();
      var ic = ICONS[key];
      if (ic){ h.dataset.gi="1"; h.insertAdjacentText("afterbegin", ic + "  "); }
    });
  }
  function buildFooter(base){
    if (!games || document.getElementById("game-pn")) return;
    var i = -1;
    for (var k=0;k<games.length;k++){ if ((games[k].u||"").replace(/\/$/,"")===base){ i=k; break; } }
    if (i < 0) return;
    var prev = i>0 ? games[i-1] : null, next = i<games.length-1 ? games[i+1] : null;
    window.__gamePN = { prev: prev, next: next };
    var nav = document.createElement("nav"); nav.id="game-pn"; nav.className="game-pn";
    nav.innerHTML =
      (prev ? '<a class="game-pn-prev" href="../'+prev.u+'"><span class="gpn-k">← Prev</span>'
              +'<span class="gpn-t">'+esc(prev.t)+'</span></a>' : '<span></span>')
    + (next ? '<a class="game-pn-next" href="../'+next.u+'"><span class="gpn-k">Next →</span>'
              +'<span class="gpn-t">'+esc(next.t)+'</span></a>' : '<span></span>');
    var art = document.querySelector(".md-content .md-typeset");
    if (art) art.appendChild(nav);
  }
  function go(dir){
    var pn = window.__gamePN; if(!pn) return;
    var t = dir<0 ? pn.prev : pn.next;
    if (t) location.href = "../" + t.u;
  }
  if (!window.__gamekbnav){
    window.__gamekbnav = true;
    document.addEventListener("keydown", function(e){
      if (e.defaultPrevented||e.ctrlKey||e.metaKey||e.altKey||e.shiftKey) return;
      var t=e.target; if(t&&(t.tagName==="INPUT"||t.tagName==="TEXTAREA"||t.isContentEditable)) return;
      if (!document.body.classList.contains("game-page")) return;
      if (e.key==="ArrowLeft"){ e.preventDefault(); go(-1); }
      else if (e.key==="ArrowRight"){ e.preventDefault(); go(1); }
    });
  }
  function init(){
    window.__gamePN = null;
    var base = curBase();
    var isGame = !!base && !document.getElementById("games-results");
    if (!isGame){ document.body.classList.remove("game-page"); return; }
    document.body.classList.add("game-page");
    decorate();
    if (games){ buildFooter(base); return; }
    if (fetching) return; fetching = true;
    fetch("../../assets/games.json").then(function(r){return r.json();})
      .then(function(d){ games=d; fetching=false; buildFooter(base); })
      .catch(function(){ fetching=false; });
  }
  if (window.document$ && window.document$.subscribe) document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
