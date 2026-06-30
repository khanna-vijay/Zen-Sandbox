"""
improv_lib.py — game indexing, selection, cross-reference resolution and rendering
helpers for the Improv Workshops curriculum generator.

Stdlib + PyYAML only. See documentation/02_Approach_and_Design.md.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

# --------------------------------------------------------------------------- #
# Paths (retarget here if the repo moves).                                     #
# --------------------------------------------------------------------------- #
HERE = Path(__file__).resolve().parent                      # workshop_design/
REPO = HERE.parent                                          # 30_Improv_GitBook-Website/
SITE = REPO / "v3-github-pages"               # local pipeline SOURCE (gitignored)
DOCS = SITE / "docs"
CONTENT_DIR = DOCS / "content"
INFOGRAPHICS_DIR = DOCS / "assets" / "infographics"
GAMES_DIR = Path(
    "/mnt/c/_VK_Code/00_2026_Priority/31_All_Improv_Code/"
    "03_Improv_Game_Database/Updated_Games_V2"
)
# The DEPLOYED, committed site (github.io/Zen-Sandbox). publish.py mirrors SOURCE -> here
# and copies all 1381 games into DEPLOYED_GAMES with their coded filenames. Workshop game
# links point at those existing pages; we never copy games ourselves.
DEPLOYED = REPO / "github-pages-v3"
DEPLOYED_GAMES = DEPLOYED / "docs" / "games"

BUILD = HERE / "build"
GAME_INDEX_CACHE = BUILD / "_game_index.json"
NAV_FRAGMENT = BUILD / "_nav.yml"             # workshops nav block, consumed by publish.py

# Where generated pages land inside the build tree (mirrors docs/workshops/).
BUILD_WORKSHOPS = BUILD / "workshops"
# Publish target: the pipeline SOURCE tree; publish.py then mirrors it into DEPLOYED.
PUBLISH_WORKSHOPS = DOCS / "workshops"

DOMAIN_NAMES = {
    1: "The Self", 2: "The Partner", 3: "The Scene",
    4: "The Ensemble", 5: "The Audience",
}
DOMAIN_FOLDER = {
    1: "01_the-self", 2: "02_the-partner", 3: "03_the-scene",
    4: "04_the-ensemble", 5: "05_the-audience",
}

# Skill ID -> display name (from the framework, 28 skills).
SKILL_NAMES = {
    "D1.S1": "Unfiltered Spontaneity", "D1.S2": "Emotional Fluidity",
    "D1.S3": "Physicality & Space Work", "D1.S4": "Vocal Craft",
    "D1.S5": "Silence & Stillness", "D1.S6": "Self-Recovery",
    "D2.S1": "Active Listening", "D2.S2": "Status Modulation",
    "D2.S3": "Single-Partner Empathy & Mirroring", "D2.S4": "Offer Reception",
    "D2.S5": "Active Gifting", "D2.S6": "Boundary Navigation",
    "D3.S1": "Game Identification", "D3.S2": "Heightening & Exploration",
    "D3.S3": "Narrative Architecture", "D3.S4": "Stakes / The “Want”",
    "D3.S5": "World-Building", "D3.S6": "Justification",
    "D3.S7": "Raising the Stakes",
    "D4.S1": "Peripheral Awareness", "D4.S2": "Support Work",
    "D4.S3": "Suggestion Deconstruction (A-to-C)", "D4.S4": "Pacing & Rhythm",
    "D4.S5": "Thematic Synthesis", "D4.S6": "Format Literacy",
    "D5.S1": "Room Reading", "D5.S2": "Audience-Energy Management",
    "D5.S3": "Stage Presence & Clarity",
}


# --------------------------------------------------------------------------- #
# Frontmatter / game parsing                                                  #
# --------------------------------------------------------------------------- #
_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)
_GID_RE = re.compile(r"_G(\d+)__(.+)\.md$")


def split_frontmatter(text: str):
    """Return (frontmatter_dict, body_str)."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, m.group(2)


def extract_debrief(body: str):
    """Pull bullet questions from the game's '## Debrief' section."""
    m = re.search(r"^##\s+Debrief\s*\n(.*?)(?=^\#\#\s|\Z)", body, re.S | re.M)
    if not m:
        return []
    lines = re.findall(r"^\s*[-*]\s+(.+?)\s*$", m.group(1), re.M)
    # Prefer questions; keep order, drop dupes.
    out, seen = [], set()
    for ln in lines:
        ln = ln.strip()
        if ln and ln not in seen:
            seen.add(ln)
            out.append(ln)
    return out


def _as_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def parse_game(path: Path):
    """Parse one game card into an index record (or None if unusable)."""
    m = _GID_RE.search(path.name)
    if not m:
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    fm, body = split_frontmatter(text)
    gid = "G" + m.group(1)
    slug = m.group(2)
    skill_ids = [str(s) for s in (fm.get("skill_ids") or [])]
    rec = {
        "gid": gid,
        "slug": slug,
        "base": path.stem,          # full coded filename w/o .md == the deployed games/ page
        "path": str(path),
        "title": fm.get("title") or slug.replace("-", " ").title(),
        "tagline": fm.get("tagline", ""),
        "primary_domain": _as_int(fm.get("primary_domain")),
        "primary_skill_id": str(fm.get("primary_skill_id") or ""),
        "skill_ids": skill_ids,
        "technique_ids": [str(t) for t in (fm.get("technique_ids") or [])],
        "skill_level": str(fm.get("skill_level") or ""),
        "complexity_level": _as_int(fm.get("complexity_level")),
        "min_participants": _as_int(fm.get("min_participants"), 1),
        "max_participants": _as_int(fm.get("max_participants"), 99),
        "ideal_group_size": str(fm.get("ideal_group_size") or ""),
        "duration": _as_int(fm.get("est_duration_minutes"), 0),
        "energy": str(fm.get("energy_level") or ""),
        "physicality": str(fm.get("physicality_level") or ""),
        "modality": str(fm.get("modality") or "in_person"),
        "props_required": str(fm.get("props_required") or "no"),
        "activity_type": str(fm.get("activity_type") or ""),
        "focus": str(fm.get("focus") or ""),
        "engine": str(fm.get("scene_engine_tag") or ""),
        "catalog_serial": _as_int(fm.get("catalog_serial"), 999999),
        "debrief": extract_debrief(body),
    }
    return rec


def build_game_index(force: bool = False):
    """Index every game card; cache to build/_game_index.json."""
    BUILD.mkdir(parents=True, exist_ok=True)
    if GAME_INDEX_CACHE.exists() and not force:
        try:
            return json.loads(GAME_INDEX_CACHE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    index = []
    for path in sorted(GAMES_DIR.glob("*.md")):
        rec = parse_game(path)
        if rec:
            index.append(rec)
    GAME_INDEX_CACHE.write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return index


# --------------------------------------------------------------------------- #
# Cross-reference maps                                                         #
# --------------------------------------------------------------------------- #
_CONTENT_RE = re.compile(r"^(\d\d)_S(\d+)(?:_T(\d+))?__")


def build_content_map():
    """ID -> content Path. Keys: 'D1.S1' and 'D1.S1.T1'."""
    m = {}
    for f in CONTENT_DIR.glob("*/*.md"):
        mm = _CONTENT_RE.match(f.name)
        if not mm:
            continue
        dom, s, t = int(mm.group(1)), mm.group(2), mm.group(3)
        key = f"D{dom}.S{s}.T{t}" if t else f"D{dom}.S{s}"
        m[key] = f
    return m


def build_infographic_map():
    """stem -> Path. Stems like 'D1.S1' / 'D1.S1.T1'."""
    return {f.stem: f for f in INFOGRAPHICS_DIR.glob("*.jpg")}


def resolve_infographic(skill_id: str, info_map: dict):
    """(rel_path_from_week_file, used_fallback) or (None, True)."""
    if skill_id in info_map:
        return _rel_asset(info_map[skill_id]), False
    for t in range(1, 7):
        k = f"{skill_id}.T{t}"
        if k in info_map:
            return _rel_asset(info_map[k]), True
    return None, True


def resolve_content(skill_id: str, content_map: dict):
    """(rel_path_from_week_file, used_fallback) or (None, True)."""
    if skill_id in content_map:
        return _rel_content(content_map[skill_id]), False
    for t in range(1, 7):
        k = f"{skill_id}.T{t}"
        if k in content_map:
            return _rel_content(content_map[k]), True
    return None, True


def _rel_asset(p: Path) -> str:
    # week file lives at docs/workshops/<course>/week-NN.md -> up two -> docs/
    return f"../../assets/infographics/{p.name}"


def _rel_content(p: Path) -> str:
    return f"../../content/{p.parent.name}/{p.name}"


# --------------------------------------------------------------------------- #
# Game selection                                                              #
# --------------------------------------------------------------------------- #
def _targets(session):
    t = [session.get("skill")] + list(session.get("also", []))
    return [x for x in t if x]


def _score(g, targets, domain, sweet):
    s = 0.0
    if g["primary_skill_id"] in targets:
        s += 5
    hits = sum(1 for t in targets if t in g["skill_ids"])
    if hits:
        s += 3 + min(hits - 1, 2)          # reward multi-skill alignment a little
    if domain != "all" and g["primary_domain"] == domain:
        s += 2
    if domain == "all":
        s += 1                              # any on-pool game is welcome in showcases
    if sweet is not None and g["complexity_level"] == sweet:
        s += 2
    mod = g["modality"]
    s += 1 if mod == "in_person" else (0.5 if mod == "hybrid" else -1)
    if g["debrief"]:
        s += 1
    if 2 <= g["min_participants"] and g["max_participants"] <= 12:
        s += 0.5
    return s


def _candidates(index, used, levels, crange, targets, domain, sweet):
    cmin, cmax = crange
    out = []
    for g in index:
        if g["slug"] in used:
            continue
        if levels and g["skill_level"] not in levels:
            continue
        c = g["complexity_level"]
        if c and not (cmin <= c <= cmax):
            continue
        sc = _score(g, targets, domain, sweet)
        if sc <= 0:
            continue
        out.append((sc, g))
    out.sort(key=lambda x: (-x[0], x[1]["complexity_level"], x[1]["catalog_serial"]))
    return out


def select_games(session, index, used, course_cfg, pin_lookup, report):
    """Return list of chosen game records (pinned first, then ranked), de-duped globally."""
    want = int(session.get("games", 2))
    targets = _targets(session)
    domain = session.get("domain")
    levels = set(course_cfg["skill_levels"])
    crange = tuple(course_cfg["complexity"])
    sweet = course_cfg.get("sweet_spot")

    picked, picked_domains = [], set()

    # 1) pins
    for pid in session.get("pins", []) or []:
        g = pin_lookup.get(pid)
        if g and g["slug"] not in used:
            picked.append(g)
            used.add(g["slug"])
            picked_domains.add(g["primary_domain"])

    # 2) ranked fill (strict gate), preferring domain variety on integration weeks
    cands = _candidates(index, used, levels, crange, targets, domain, sweet)
    picked += _fill(cands, picked, used, picked_domains, want, prefer_variety=(domain == "all"))

    # 3) progressive relaxation if short
    relax_steps = [
        ("complexity ±1", (levels, (max(1, crange[0] - 1), min(5, crange[1] + 1)))),
        ("any complexity", (levels, (1, 5))),
        ("any level + any complexity", (set(), (1, 5))),
    ]
    si = 0
    while len(picked) < want and si < len(relax_steps):
        label, (lv, cr) = relax_steps[si]
        si += 1
        cands = _candidates(index, used, lv, cr, targets, domain, sweet)
        before = len(picked)
        picked += _fill(cands, picked, used, picked_domains, want,
                        prefer_variety=(domain == "all"))
        if len(picked) > before:
            report.setdefault("relaxations", []).append(
                {"session": f"{session['course']}/W{session['week']:02d}",
                 "step": label, "added": len(picked) - before})

    if len(picked) < 1:
        report.setdefault("empty_sessions", []).append(
            f"{session['course']}/W{session['week']:02d}")
    return picked[:max(want, len(picked))]


def _fill(cands, picked, used, picked_domains, want, prefer_variety):
    added = []
    # First pass honours domain variety (for showcases); second pass fills the rest.
    for variety_pass in ((True,) if prefer_variety else ()) + (False,):
        for _sc, g in cands:
            if len(picked) + len(added) >= want:
                break
            if g["slug"] in used:
                continue
            if variety_pass and g["primary_domain"] in picked_domains:
                continue
            added.append(g)
            used.add(g["slug"])
            picked_domains.add(g["primary_domain"])
    return added


def order_warmup_first(games):
    """Return games ordered so a short/high-energy one leads as the warm-up."""
    if len(games) <= 1:
        return games

    def warm_key(g):
        energy_rank = {"high": 0, "medium": 1, "low": 2}.get(g["energy"], 1)
        return (energy_rank, g["duration"] or 99, g["complexity_level"])

    lead = min(games, key=warm_key)
    rest = [g for g in games if g is not lead]
    return [lead] + rest
