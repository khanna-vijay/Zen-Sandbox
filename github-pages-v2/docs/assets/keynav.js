// Arrow-key page navigation: ← previous page, → next page.
(function () {
  if (window.__kbnav) return; window.__kbnav = true;
  document.addEventListener("keydown", function (e) {
    if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey || e.shiftKey) return;
    var t = e.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
    var sel = e.key === "ArrowLeft"  ? ".md-footer__link--prev"
            : e.key === "ArrowRight" ? ".md-footer__link--next" : null;
    if (!sel) return;
    var link = document.querySelector(sel);
    if (link && link.getAttribute("href")) { e.preventDefault(); link.click(); }
  });
})();
