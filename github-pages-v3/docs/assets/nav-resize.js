// Resizable + hideable left navigation (persists width & hidden state).
(function () {
  var KW = "zs-nav-w", KH = "zs-nav-hidden", drag = false, sb = null;
  function applyStored() {
    var w = localStorage.getItem(KW);
    if (w) document.documentElement.style.setProperty("--zs-nav-width", w + "px");
    document.body.classList.toggle("zs-nav-hidden", localStorage.getItem(KH) === "1");
  }
  function ensureToggle() {
    if (document.getElementById("zs-nav-toggle")) return;
    var b = document.createElement("button");
    b.id = "zs-nav-toggle"; b.type = "button"; b.className = "zs-nav-toggle";
    b.title = "Hide / show the left navigation";
    b.setAttribute("aria-label", "Toggle navigation");
    function glyph() { b.textContent = document.body.classList.contains("zs-nav-hidden") ? "\u27E9" : "\u27E8"; }
    b.addEventListener("click", function () {
      var hide = !document.body.classList.contains("zs-nav-hidden");
      document.body.classList.toggle("zs-nav-hidden", hide);
      localStorage.setItem(KH, hide ? "1" : "0"); glyph();
    });
    document.body.appendChild(b); glyph();
  }
  function ensureGrip() {
    sb = document.querySelector(".md-sidebar--primary");
    if (!sb || sb.querySelector(".zs-nav-grip")) return;
    var g = document.createElement("div"); g.className = "zs-nav-grip"; sb.appendChild(g);
    g.addEventListener("mousedown", function (e) {
      drag = true; e.preventDefault(); document.body.style.userSelect = "none";
    });
  }
  if (!window.__zsResizeBound) {
    window.__zsResizeBound = true;
    window.addEventListener("mousemove", function (e) {
      if (!drag || !sb) return;
      var w = Math.min(560, Math.max(150, e.clientX - sb.getBoundingClientRect().left));
      document.documentElement.style.setProperty("--zs-nav-width", w + "px");
    });
    window.addEventListener("mouseup", function () {
      if (!drag) return; drag = false; document.body.style.userSelect = "";
      var px = parseInt(getComputedStyle(document.documentElement)
        .getPropertyValue("--zs-nav-width"), 10);
      if (px) localStorage.setItem(KW, px);
    });
  }
  function setup() { applyStored(); ensureToggle(); ensureGrip(); }
  if (window.document$ && window.document$.subscribe) document$.subscribe(setup);
  else document.addEventListener("DOMContentLoaded", setup);
})();
