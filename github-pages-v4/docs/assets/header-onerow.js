// Merge the nav tabs into the header (one compact sticky row) + keep the active tab synced.
(function () {
  function activeFor(href, path) {
    var seg = href.indexOf("/workshops/") >= 0 ? "/workshops/"
            : href.indexOf("/solo-practice/") >= 0 ? "/solo-practice/"
            : href.indexOf("/games/") >= 0 ? "/games/"
            : href.indexOf("/theory/") >= 0 ? "/theory/" : "__about__";
    if (seg === "__about__")
      return path.indexOf("/workshops/") < 0 && path.indexOf("/solo-practice/") < 0
          && path.indexOf("/games/") < 0 && path.indexOf("/theory/") < 0;
    return path.indexOf(seg) >= 0;
  }
  function sync() {
    var path = location.pathname, links = document.querySelectorAll(".md-header__inner .md-tabs__link");
    for (var i = 0; i < links.length; i++) {
      var on = activeFor(links[i].href, path);
      links[i].classList.toggle("md-tabs__link--active", on);
      var li = links[i].closest ? links[i].closest(".md-tabs__item") : null;
      if (li) li.classList.toggle("md-tabs__item--active", on);   // clear the old tab's highlight
    }
  }
  function merge() {
    var inner = document.querySelector(".md-header__inner");
    var list = document.querySelector(".md-tabs__list");
    if (!inner) return;
    if (!inner.querySelector(".md-tabs__list") && list) {
      var title = inner.querySelector(".md-header__title");
      if (title) inner.insertBefore(list, title.nextSibling);
      else inner.appendChild(list);
    }
    document.body.classList.add("zs-onerow");
    sync();
  }
  if (window.document$ && window.document$.subscribe) document$.subscribe(merge);
  else document.addEventListener("DOMContentLoaded", merge);
})();
