#!/usr/bin/env python3
"""
website_checker.py — recursive link checker + random navigation tester.

Crawls a static website starting at BASE_URL, follows internal links recursively,
checks the HTTP status of every referenced link / image / stylesheet / script
(internal and external), and writes a comprehensive Markdown report of any broken
or missing URLs — each listed with the page(s) that reference it.

It then runs a set of RANDOM NAVIGATION walks over the discovered link graph
(simulating a user clicking around at random) and reports any path that lands on a
non-200 page.

Stdlib only (urllib + html.parser) — no pip installs required.

Usage:
    python3 website_checker.py [BASE_URL] [options]

Options:
    --out PATH          report file (default: website_link_report.md)
    --max-pages N       max internal pages to crawl (default: 5000)
    --walks N           number of random navigation walks (default: 25)
    --hops N            max hops per random walk (default: 12)
    --timeout S         per-request timeout seconds (default: 20)
    --delay S           delay between page fetches (default: 0.0)
    --workers N         threads for asset/external checks (default: 8)
    --skip-external     do not check off-site links
    --seed N            RNG seed for reproducible random walks
"""
import argparse
import json
import random
import re
import sys
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen

UA = "website-checker/1.0 (+link-audit)"
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:", "ftp:")


class LinkParser(HTMLParser):
    """Collect (kind, url) for anchors, images, scripts, stylesheets."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self.links.append(("link", d["href"]))
        elif tag in ("img", "source") and d.get("src"):
            self.links.append(("image", d["src"]))
        elif tag == "script" and d.get("src"):
            self.links.append(("script", d["src"]))
        elif tag == "link" and d.get("href"):
            rel = (d.get("rel") or "").lower()
            # preconnect / dns-prefetch are connection hints, not fetchable documents.
            if "preconnect" in rel or "dns-prefetch" in rel:
                return
            self.links.append(("asset", d["href"]))


def fetch(url, timeout, method="GET", retries=2):
    """Return (status, content_type, body_bytes). status 0 => connection error.
    Retries connection-level failures to avoid false positives on flaky networks."""
    last = (0, "no attempt", b"")
    for attempt in range(retries + 1):
        req = Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urlopen(req, timeout=timeout) as r:
                body = r.read() if method == "GET" else b""
                return r.status, r.headers.get("Content-Type", ""), body
        except HTTPError as e:
            # Retry transient server/rate-limit responses; return real client errors at once.
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                last = (e.code, f"HTTP {e.code}", b"")
                time.sleep(0.6 * (attempt + 1))
                continue
            return e.code, e.headers.get("Content-Type", "") if e.headers else "", b""
        except (URLError, TimeoutError, ConnectionError) as e:
            last = (0, f"{type(e).__name__}: {getattr(e, 'reason', e)}", b"")
        except Exception as e:  # noqa: BLE001
            last = (0, f"{type(e).__name__}: {e}", b"")
        time.sleep(0.4 * (attempt + 1))
    return last


def check_status(url, timeout):
    """HEAD first (cheap); fall back to GET if HEAD is unsupported/odd."""
    code, ct, _ = fetch(url, timeout, method="HEAD")
    if code in (405, 501, 0) or code >= 400:
        code, ct, _ = fetch(url, timeout, method="GET")
    return code, ct


def norm(base):
    return base if base.endswith("/") else base + "/"


def canon(u):
    """Normalize a URL for de-duplication: add a trailing slash to directory-style paths
    (no file extension), so `/x` and `/x/` aren't crawled as two separate pages."""
    p = urlparse(u)
    path = p.path or "/"
    last = path.rsplit("/", 1)[-1]
    # Don't touch URLs that carry a query (e.g. Google Fonts /css?family=…) — adding a
    # trailing slash there changes the endpoint and yields false 404s.
    if last and "." not in last and not path.endswith("/") and not p.query:
        path += "/"
    return p._replace(path=path, fragment="").geturl()


def seed_from_sitemap(base, timeout):
    """Return all <loc> URLs from <base>sitemap.xml — covers pages that are only linked
    via JavaScript (e.g. a JS-rendered index), which a static crawler can't discover."""
    code, _ct, body = fetch(urljoin(base, "sitemap.xml"), timeout, "GET")
    if code != 200 or not body:
        return []
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body.decode("utf-8", "ignore"))
    return [urldefrag(u)[0] for u in locs]


def site_health(base, timeout):
    """Verify JS-driven content actually has its data/assets. A pure link crawl can't tell
    that the Game Finder will show 'Could not load games' because games.json is missing or
    invalid, or that hero images fail to display. Returns [label, rel, detail, ok]."""
    rows = []

    def add(label, rel, detail, ok):
        rows.append([label, rel, detail, ok])

    for rel in ["assets/games.json", "assets/games-filter.js", "assets/games-page.js",
                "assets/nav-resize.js", "assets/keynav.js", "assets/extra.css"]:
        code, _ = check_status(urljoin(base, rel), timeout)
        add(rel, rel, f"HTTP {code or 'ERR'}", code == 200)

    code, _ct, body = fetch(urljoin(base, "assets/games.json"), timeout, "GET")
    data = None
    if code == 200:
        try:
            data = json.loads(body)
        except Exception:  # noqa: BLE001
            data = None
    ok = isinstance(data, list) and len(data) > 0
    add("games.json valid + non-empty", "assets/games.json",
        (f"{len(data)} games" if ok else "INVALID / empty"), ok)

    if ok:                                       # sample hero images actually load
        mid = len(data) // 2
        for b in {(data[0].get("u") or "").rstrip("/"),
                  (data[mid].get("u") or "").rstrip("/"),
                  (data[-1].get("u") or "").rstrip("/")} - {""}:
            rel = f"games/img/{b}.jpg"
            code, _ = check_status(urljoin(base, rel), timeout)
            add(f"hero image · {b[:36]}", rel, f"HTTP {code or 'ERR'}", code == 200)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base", nargs="?", default="https://khanna-vijay.github.io/Zen-Sandbox/")
    ap.add_argument("--out", default="website_link_report.md")
    ap.add_argument("--max-pages", type=int, default=5000)
    ap.add_argument("--walks", type=int, default=25)
    ap.add_argument("--hops", type=int, default=12)
    ap.add_argument("--timeout", type=float, default=20)
    ap.add_argument("--delay", type=float, default=0.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--skip-external", action="store_true")
    ap.add_argument("--no-sitemap", action="store_true",
                    help="don't seed the crawl from sitemap.xml")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    base = norm(args.base)
    host = urlparse(base).netloc
    rng = random.Random(args.seed)

    def internal(u):
        return u.startswith(base)

    status = {}                     # url -> (code, content_type/note)
    refs = defaultdict(set)         # target url -> {source pages}
    kinds = defaultdict(set)        # target url -> {kinds: link/image/script/asset}
    graph = defaultdict(list)       # page -> [internal link targets]
    page_links = {}                 # page -> kind set (for typing)
    visited = set()
    queue = deque([base])
    if not args.no_sitemap:
        seeds = [canon(u) for u in seed_from_sitemap(base, args.timeout) if internal(u)]
        print(f"[sitemap] seeded {len(seeds)} URLs", file=sys.stderr)
        queue.extend(seeds)
    crawled = 0

    print(f"[crawl] start {base}", file=sys.stderr)
    while queue and crawled < args.max_pages:
        page = queue.popleft()
        if page in visited:
            continue
        visited.add(page)
        code, ct, body = fetch(page, args.timeout, "GET")
        status[page] = (code, ct)
        crawled += 1
        if crawled % 50 == 0:
            print(f"[crawl] {crawled} pages…", file=sys.stderr)
        if code != 200 or "html" not in ct.lower():
            continue
        parser = LinkParser()
        try:
            parser.feed(body.decode("utf-8", "ignore"))
        except Exception:  # noqa: BLE001
            pass
        for kind, raw in parser.links:
            raw = (raw or "").strip()
            if not raw or raw.startswith("#") or raw.lower().startswith(SKIP_SCHEMES):
                continue
            target = urldefrag(urljoin(page, raw))[0]
            if not target.startswith(("http://", "https://")):
                continue
            target = canon(target)
            refs[target].add(page)
            kinds[target].add(kind)
            if kind == "link" and internal(target):
                graph[page].append(target)
                if target not in visited:
                    queue.append(target)
            else:
                page_links.setdefault(target, set()).add(kind)
        if args.delay:
            time.sleep(args.delay)

    # Status-check every referenced URL we haven't already fetched (assets + external).
    to_check = [u for u in refs if u not in status]
    if args.skip_external:
        to_check = [u for u in to_check if internal(u)]
    print(f"[check] {len(to_check)} referenced assets/links…", file=sys.stderr)

    def _do(u):
        return u, check_status(u, args.timeout)

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        for u, st in ex.map(_do, to_check):
            status[u] = st

    # Broken = status >= 400 or connection error (0).
    def broken(u):
        c = status.get(u, (0, ""))[0]
        return c == 0 or c >= 400

    internal_broken = sorted(u for u in refs if internal(u) and broken(u))
    # Only count externals we actually checked (skip-external leaves them unchecked).
    external_broken = sorted(u for u in refs if not internal(u) and u in status and broken(u))
    # Broken / missing images (so "images not showing" is surfaced on its own).
    broken_images = sorted(u for u in refs if "image" in kinds.get(u, set()) and broken(u))

    # Site-health checks for JS-driven content (catches "Could not load games", missing
    # data/assets, and dead hero images that a pure link crawl can't infer).
    health = site_health(base, args.timeout)

    # ---- Random navigation walks over the internal link graph ----
    walk_results = []
    good_pages = [p for p in graph if status.get(p, (0,))[0] == 200]
    for w in range(args.walks if good_pages else 0):
        cur = base if status.get(base, (0,))[0] == 200 else rng.choice(good_pages)
        path, failure = [cur], None
        for _ in range(args.hops):
            nxt_choices = [u for u in graph.get(cur, []) if internal(u)]
            if not nxt_choices:
                break
            nxt = rng.choice(nxt_choices)
            code = status.get(nxt, (None,))[0]
            if code is None:
                code = fetch(nxt, args.timeout, "GET")[0]
                status[nxt] = (code, "")
            path.append(nxt)
            if code != 200:
                failure = (nxt, code)
                break
            cur = nxt
        walk_results.append((path, failure))

    write_report(args, base, host, status, refs, internal_broken,
                 external_broken, walk_results, crawled, broken_images, health)
    health_fail = [h for h in health if not h[3]]
    print(f"[done] crawled {crawled} pages · {len(status)} urls checked · "
          f"{len(internal_broken)} internal broken · {len(broken_images)} broken images · "
          f"{len(external_broken)} external broken · {len(health_fail)} health checks failed")
    print(f"[done] report → {args.out}")
    return 1 if (internal_broken or broken_images or health_fail) else 0


def write_report(args, base, host, status, refs, internal_broken,
                 external_broken, walk_results, crawled, broken_images=None, health=None):
    broken_images = broken_images or []
    health = health or []
    health_fail = [h for h in health if not h[3]]
    rel = lambda u: u[len(base):] or "/" if u.startswith(base) else u  # noqa: E731
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    walk_fail = [r for r in walk_results if r[1]]
    lines = []
    lines.append(f"# 🔗 Website Audit — {host}")
    lines.append("")
    lines.append(f"- **Site:** {base}")
    lines.append(f"- **Generated:** {now}")
    lines.append(f"- **Pages crawled:** {crawled}")
    lines.append(f"- **Unique URLs checked:** {len(status)}")
    lines.append(f"- **Broken internal links:** {len(internal_broken)}")
    lines.append(f"- **Broken / missing images:** {len(broken_images)}")
    lines.append(f"- **Broken external:** "
                 f"{'(skipped)' if args.skip_external else len(external_broken)}")
    lines.append(f"- **Site-health checks failed:** {len(health_fail)} of {len(health)}")
    lines.append(f"- **Random walks:** {len(walk_results)} "
                 f"({len(walk_fail)} hit a non-200 page)")
    lines.append("")
    problems = len(internal_broken) + len(broken_images) + len(health_fail)
    lines.append("✅ **No problems found.**" if not problems
                 else f"❌ **{problems} problem(s) found** "
                      f"({len(internal_broken)} links, {len(broken_images)} images, "
                      f"{len(health_fail)} health).")
    lines.append("")

    # ---- Site health (JS-driven content: data + assets + sample images) ----
    lines.append("## 🩺 Site health (data & assets)")
    lines.append("")
    if not health:
        lines.append("_Not run._")
    else:
        lines.append("| Check | Path | Result | OK |")
        lines.append("|---|---|---|---|")
        for label, hrel, detail, ok in health:
            lines.append(f"| {label} | `{hrel}` | {detail} | {'✅' if ok else '❌'} |")
    lines.append("")

    def table(urls):
        out = ["| Broken URL | Status | Referenced from |", "|---|---|---|"]
        for u in urls:
            code = status.get(u, (0, ""))[0]
            srcs = sorted(refs.get(u, []))
            shown = ", ".join(rel(s) for s in srcs[:5]) + (" …" if len(srcs) > 5 else "")
            out.append(f"| `{rel(u)}` | {code or 'ERR'} | {shown} |")
        return out

    lines.append("## Broken internal links")
    lines += table(internal_broken) if internal_broken else ["", "_None._"]
    lines.append("")

    lines.append("## 🖼️ Broken / missing images")
    lines.append("")
    lines.append("> Images referenced via `<img>` that returned a non-200 status (won't display).")
    lines += table(broken_images) if broken_images else ["", "_None._"]
    lines.append("")

    if not args.skip_external:
        lines.append("## Broken external links")
        lines.append("")
        lines.append("> External failures can be transient (rate-limiting, UA blocks); "
                     "verify manually before acting.")
        lines += table(external_broken) if external_broken else ["", "_None._"]
        lines.append("")

    lines.append("## Random navigation walks")
    lines.append("")
    if not walk_results:
        lines.append("_No walks run (no crawlable link graph)._")
    else:
        lines.append(f"Simulated {len(walk_results)} random click-paths from the home page "
                     f"(up to {args.hops} hops each).")
        lines.append("")
        if walk_fail:
            lines.append("### ❌ Walks that hit a broken page")
            for path, fail in walk_fail:
                lines.append(f"- **{fail[1]}** at `{rel(fail[0])}` — path: "
                             + " → ".join(rel(p) for p in path))
        else:
            lines.append("✅ All random walks stayed on healthy (200) pages.")
        lines.append("")
        lines.append("<details><summary>Show all walk paths</summary>")
        lines.append("")
        for i, (path, fail) in enumerate(walk_results, 1):
            mark = "❌" if fail else "✅"
            lines.append(f"{i}. {mark} " + " → ".join(rel(p) for p in path))
        lines.append("")
        lines.append("</details>")
    lines.append("")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
