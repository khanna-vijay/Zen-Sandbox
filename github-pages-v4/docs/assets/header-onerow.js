// Merge the nav tabs into the header (one compact sticky row) + keep the active tab synced.
//
// Why sync() exists at all: navigation.instant swaps the page body without a reload, and the
// tab list has been MOVED out of .md-tabs into .md-header__inner, so Material's own re-render
// of .md-tabs never touches the copy we are actually showing. We have to re-mark it ourselves.
//
// The active test is derived from the tabs themselves — first path segment after the site
// base — rather than a hardcoded list of section names. The previous hardcoded version knew
// only about workshops/solo-practice/games/theory, so every OTHER section (improv-sports, and
// now play) fell through to the "About" branch and lit up About *plus* every other unlisted
// tab at once. Deriving it means a new top-level tab needs no change here.
(function () {
  // Site base path: "/" locally, "/Zen-Sandbox/" on Pages. The logo always links to the root.
  function basePath() {
    var logo = document.querySelector(".md-header__button.md-logo");
    if (!logo) return "/";
    var p = new URL(logo.href, location.href).pathname;
    return p.charAt(p.length - 1) === "/" ? p : p + "/";
  }

  // First path segment below the site base. "" for the site root and for pages that sit
  // directly in docs/ (improv-philosophy, Gratitude, …) — those belong to the About tab.
  function section(pathname, base) {
    var rest = pathname.indexOf(base) === 0 ? pathname.slice(base.length) : pathname.replace(/^\//, "");
    var i = rest.indexOf("/");
    return i < 0 ? "" : rest.slice(0, i);
  }

  function sync() {
    var links = document.querySelectorAll(".md-header__inner .md-tabs__link");
    if (!links.length) return;
    var base = basePath();
    var here = section(location.pathname, base);

    // A tab whose own section matches wins. Anything that did not match falls back to the
    // tab pointing at the site root (About) — one winner, never several.
    var match = -1, root = -1;
    for (var i = 0; i < links.length; i++) {
      var s = section(new URL(links[i].href, location.href).pathname, base);
      if (s === "") root = i;
      else if (s === here) match = i;
    }
    var winner = match >= 0 ? match : root;

    for (var j = 0; j < links.length; j++) {
      var on = (j === winner);
      links[j].classList.toggle("md-tabs__link--active", on);
      var li = links[j].closest ? links[j].closest(".md-tabs__item") : null;
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
