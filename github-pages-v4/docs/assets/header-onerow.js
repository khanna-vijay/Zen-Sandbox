// Merge the nav tabs into the header (one compact sticky row) + keep the active tab synced.
(function () {
  function activeFor(href, path) {
    var seg = href.indexOf("/workshops/") >= 0 ? "/workshops/"
            : href.indexOf("/games/") >= 0 ? "/games/"
            : href.indexOf("/content/") >= 0 ? "/content/" : "__about__";
    if (seg === "__about__")
      return path.indexOf("/workshops/") < 0 && path.indexOf("/games/") < 0
          && path.indexOf("/content/") < 0;
    return path.indexOf(seg) >= 0;
  }
  function sync() {
    var path = location.pathname, links = document.querySelectorAll(".md-header__inner .md-tabs__link");
    for (var i = 0; i < links.length; i++)
      links[i].classList.toggle("md-tabs__link--active", activeFor(links[i].href, path));
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
