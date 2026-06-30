#!/usr/bin/env python3
"""
generate.py — render the 52-session Improv Workshops curriculum.

Reads curriculum_map.yaml + reflection_prompts.yaml, selects games from the
games database, resolves cross-references to the existing content pages and
infographics, and writes a self-contained docs/workshops/ tree.

Usage:
    python3 generate.py [--force] [--check] [--publish] [--course NAME]

    --force    rebuild the cached game index
    --check    generate + validate, but do not publish
    --publish  copy the generated tree into v3-github-pages/docs/workshops/
    --course   limit rendering to one course (beginner|intermediate|advanced)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import yaml

import improv_lib as L


# --------------------------------------------------------------------------- #
# Rendering helpers                                                            #
# --------------------------------------------------------------------------- #
def skill_label(sid: str) -> str:
    name = L.SKILL_NAMES.get(sid)
    return f"`{sid}` — {name}" if name else f"`{sid}`"


def domain_label(dom) -> str:
    if dom == "all":
        return "All domains (integration)"
    return f"D{dom} — {L.DOMAIN_NAMES.get(dom, '')}"


def game_card(g: dict, role: str) -> str:
    skill = L.SKILL_NAMES.get(g["primary_skill_id"], g["primary_skill_id"] or "—")
    props = "none" if str(g["props_required"]).lower() == "no" else "required"
    mx = g["max_participants"]
    players = f"{g['min_participants']}+" if mx <= 0 else f"{g['min_participants']}–{mx}"
    focus = g["focus"].replace("_", " ") if g["focus"] else ""
    meta = (f"`Players {players}` · `~{g['duration']} min` · "
            f"`Complexity {g['complexity_level']}/5` · `Energy {g['energy']}` · "
            f"`Props: {props}`")
    lines = [f"#### {role} — {g['title']}"]
    if g["tagline"]:
        lines.append(f"> {g['tagline']}")
    lines.append(meta)
    trains = f"**Trains:** {skill}"
    if focus:
        trains += f" · _{focus}_"
    lines.append(trains)
    # Link to the already-published Games List entry (coded filename = source of truth).
    lines.append(f"[Open the full game card »](../../games/{g['base']}.md)")
    return "\n\n".join(lines)


def backup_block(backups: list) -> str:
    """A COLLAPSED admonition of spare games — facilitator buffer; core plan unchanged."""
    if not backups:
        return ""
    out = ['??? note "🎒 Backup games — if you have time, or a game falls flat"']
    out.append("    *Swap-ins drawn from the same maturity band; not part of the timed hour.*")
    for g in backups:
        skill = L.SKILL_NAMES.get(g["primary_skill_id"], g["primary_skill_id"] or "—")
        mx = g["max_participants"]
        players = f"{g['min_participants']}+" if mx <= 0 else f"{g['min_participants']}–{mx}"
        out.append(
            f"    - **[{g['title']}](../../games/{g['base']}.md)** — "
            f"`{players}` · `~{g['duration']}m` · `Cx {g['complexity_level']}/5` "
            f"· `Energy {g['energy']}` · _{skill}_")
    return "\n".join(out) + "\n"


def reflection_block(session: dict, games: list, prompts: dict):
    key = session.get("meta")
    if key not in prompts:
        key = session.get("skill")
    pr = prompts.get(key) or prompts["default"]
    deepen = []
    for g in games:
        for q in g["debrief"]:
            if q not in deepen:
                deepen.append(q)
    deepen = deepen[:2]
    if not deepen:
        deepen = [pr.get("improv") or prompts["default"]["improv"]]
    elif len(deepen) < 2 and pr.get("improv") and pr["improv"] not in deepen:
        deepen.append(pr["improv"])
    transfer = pr.get("transfer") or prompts["default"]["transfer"]
    return deepen[:2], transfer


def render_week(session, games, course_cfg, content_map, info_map, prompts,
                prev_s, next_s, report, backups=None) -> str:
    course = session["course"]
    week = session["week"]
    total = course_cfg["weeks"]
    skill = session["skill"]

    info_rel, info_fb = L.resolve_infographic(skill, info_map)
    content_rel, content_fb = L.resolve_content(skill, content_map)

    games = L.order_warmup_first(games)

    out = []
    out.append("---")
    out.append(f'title: "W{week:02d} · {session["title"]}"')
    out.append("---\n")
    out.append(f'# Week {week:02d} — {session["title"]}')
    out.append(f'> *{session["essence"]}*\n')

    # At-a-glance
    out.append("| Course | Week | Domain | Focus | Stage |")
    out.append("|---|---|---|---|---|")
    out.append(f"| {course_cfg['title']} | {week}/{total} | {domain_label(session.get('domain'))} "
               f"| {skill_label(skill)} | {course_cfg['stage']} |")
    out.append("")

    if session.get("layer0"):
        out.append('!!! warning "Layer 0 — Safety & Consent first"')
        out.append("    The consent container is taught before anything else and re-affirmed here. "
                   "The rule of consent overrides the rule of agreement.\n")
    if session.get("builds_on"):
        out.append('!!! note "Builds on"')
        out.append(f"    {session['builds_on']}\n")

    # Session flow
    out.append("## ⏱️ Session flow (60 minutes)\n")
    out.append("| Time | Block |")
    out.append("|---|---|")
    out.append("| 0:00–0:05 | Arrival & safety check-in |")
    out.append("| 0:05–0:15 | Warm-up game |")
    out.append("| 0:15–0:27 | **1. Today's theory** |")
    out.append("| 0:27–0:52 | **2. Today's games** |")
    out.append("| 0:52–1:00 | **3. Reflection & debrief** |")
    out.append("")

    # 1. Theory
    out.append("## 1. 🧠 Today's theory\n")
    out.append(f"**Focus:** {skill_label(skill)}  ")
    also = session.get("also") or []
    if also:
        out.append("**Also touches:** " + ", ".join(skill_label(a) for a in also) + "  ")
    out.append(f"**Maturity goal today:** {session['stage_focus']}\n")
    if info_rel:
        alt = f"Infographic — {L.SKILL_NAMES.get(skill, skill)}"
        out.append(f"![{alt}]({info_rel}){{ .infographic }}")
        if info_fb:
            out.append("<small>*(technique-level infographic shown for this skill)*</small>")
        out.append("")
    out.append(f"- **The big idea:** {session['essence']}")
    out.append(f"- **Where you are on the path:** {session['stage_focus']}")
    out.append(f"- **The one cue to coach:** *“{session['cue']}”*")
    out.append("")
    if content_rel:
        out.append(f'!!! abstract "📖 Go deeper"')
        out.append(f"    Read the full write-up: [{L.SKILL_NAMES.get(skill, skill)}]({content_rel})")
        for a in also:
            ar, _ = L.resolve_content(a, content_map)
            if ar:
                out.append(f"    · [{L.SKILL_NAMES.get(a, a)}]({ar})")
        out.append("")

    # 2. Games
    out.append("## 2. 🎲 Today's games\n")
    if not games:
        out.append("_No game matched the filters for this session — see facilitator notes._\n")
    for i, g in enumerate(games):
        role = "Warm-up" if (i == 0 and len(games) > 1) else "Core game"
        out.append(game_card(g, role))
        out.append("")

    bb = backup_block(backups or [])
    if bb:
        out.append(bb)

    # 3. Reflection
    deepen, transfer = reflection_block(session, games, prompts)
    out.append("## 3. 💭 Self-reflection\n")
    out.append("**Deepen your improv**")
    for i, q in enumerate(deepen, 1):
        out.append(f"{i}. {q}")
    out.append("")
    out.append("**Beyond the stage**")
    out.append(f"{len(deepen) + 1}. {transfer}")
    out.append("")

    # Footer nav
    out.append("---")
    nav = []
    if prev_s:
        nav.append(f"⬅️ *Previous:* [W{prev_s['week']:02d} — {prev_s['title']}]"
                   f"(week-{prev_s['week']:02d}.md)")
    if next_s:
        nav.append(f"*Next:* [W{next_s['week']:02d} — {next_s['title']}]"
                   f"(week-{next_s['week']:02d}.md) ➡️")
    if nav:
        out.append("  ·  ".join(nav))
    out.append("")

    # record stats
    report.setdefault("sessions", []).append({
        "id": f"{course}/W{week:02d}",
        "title": session["title"],
        "skill": skill,
        "n_games": len(games),
        "n_reflection": len(deepen) + 1,
        "infographic": info_rel, "infographic_fallback": info_fb,
        "content": content_rel, "content_fallback": content_fb,
        "games": [g["base"] for g in games],
        "backups": [g["base"] for g in (backups or [])],
    })
    return "\n".join(out)


def render_course_index(course_key, course_cfg, sessions, content_map) -> str:
    out = []
    out.append("---")
    out.append(f'title: "{course_cfg["title"]}"')
    out.append("---\n")
    out.append(f"# {course_cfg['title']}")
    out.append(f"> *{course_cfg['stage']} · {course_cfg['layer_focus']} · "
               f"{course_cfg['weeks']} weekly one-hour sessions*\n")
    out.append(course_cfg["intro"].strip() + "\n")
    out.append("## The weeks\n")
    out.append("| Wk | Session | Domain | Focus skill | Maturity goal |")
    out.append("|---:|---|---|---|---|")
    for s in sessions:
        out.append(f"| {s['week']} | [{s['title']}](week-{s['week']:02d}.md) "
                   f"| {domain_label(s.get('domain'))} | {skill_label(s['skill'])} "
                   f"| {s['stage_focus']} |")
    out.append("")
    out.append('!!! tip "How to use this course"')
    out.append("    Each session is a ready-to-run hour: a short theory beat with its infographic "
               "(deep-linked to the full write-up), one to three games drawn from the master game "
               "library, and reflection questions that connect the skill to both the stage and the "
               "rest of your life. Complexity rises week over week — teach them in order.")
    out.append("")
    return "\n".join(out)


def render_workshops_index(courses) -> str:
    out = []
    out.append("---")
    out.append('title: "Workshops"')
    out.append("---\n")
    out.append("# 🎭 Improv Workshops — A Year of Lesson Plans\n")
    out.append("Three facilitator-ready courses that take a group from first nerves to a full "
               "improvised show — **one hour a week, 52 weeks a year**. Every session reuses the "
               "toolkit's framework, games, infographics and deep-dive content, so the workshops "
               "and the encyclopedia stay one connected whole.\n")
    out.append("## The three courses\n")
    out.append("| Course | Weeks | Stage | Layer focus |")
    out.append("|---|---:|---|---|")
    for key in ("beginner", "intermediate", "advanced"):
        c = courses[key]
        out.append(f"| [{c['title']}]({c['folder']}/index.md) | {c['weeks']} "
                   f"| {c['stage']} | {c['layer_focus']} |")
    out.append("")
    out.append("## The teaching model\n")
    out.append("This curriculum follows the framework's **diagonal teaching path**: instead of "
               "finishing one domain before the next, every course **spirals through all five "
               "domains** — *The Self → The Partner → The Scene → The Ensemble → The Audience* — at "
               "a higher **maturity stage** each time. You *learn bottom-up* (Technique → Skill → "
               "Principle) and *perform top-down*. **Safety & Consent (Layer 0) is taught first** "
               "and re-committed at the start of every course.\n")
    out.append('!!! abstract "Every session, the same shape"')
    out.append("    **1. Theory** (a skill/principle + its infographic, linked to the full page) → "
               "**2. Games** (1–3, drawn from the master library) → "
               "**3. Reflection** (deepen your improv *and* carry it beyond the stage).\n")
    out.append("### The one-hour session\n")
    out.append("| Time | Block |")
    out.append("|---|---|")
    out.append("| 0:00–0:05 | Arrival & safety check-in |")
    out.append("| 0:05–0:15 | Warm-up game |")
    out.append("| 0:15–0:27 | Today's theory |")
    out.append("| 0:27–0:52 | Today's games |")
    out.append("| 0:52–1:00 | Reflection & debrief |")
    out.append("")
    return "\n".join(out)


def write_nav_fragment(courses, by_course):
    """Emit the Workshops nav block (mkdocs YAML) for publish.py to splice in.

    Bare page paths let MkDocs use each page's own title (from frontmatter)."""
    lines = ["  - Workshops:", "      - workshops/index.md"]
    for key in ("beginner", "intermediate", "advanced"):
        cc = courses[key]
        lines.append(f"      - {_q(cc['title'])}:")
        lines.append(f"          - workshops/{cc['folder']}/index.md")
        for s in by_course.get(key, []):
            lines.append(f"          - workshops/{cc['folder']}/week-{s['week']:02d}.md")
    L.NAV_FRAGMENT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _q(s: str) -> str:
    return '"' + str(s).replace('"', "'") + '"'


# --------------------------------------------------------------------------- #
# Validation                                                                   #
# --------------------------------------------------------------------------- #
def validate(report, courses, only_course):
    errors, warnings = [], []
    expect = {k: v["weeks"] for k, v in courses.items()}
    counts = {}
    all_games = []
    for s in report.get("sessions", []):
        course = s["id"].split("/")[0]
        counts[course] = counts.get(course, 0) + 1
        all_games += s["games"]
        all_games += s.get("backups", [])
        if not (1 <= s["n_games"] <= 3):
            errors.append(f"{s['id']}: {s['n_games']} games (want 1–3)")
        if not (2 <= s["n_reflection"] <= 3):
            errors.append(f"{s['id']}: {s['n_reflection']} reflection Qs (want 2–3)")
        if not s["infographic"]:
            errors.append(f"{s['id']}: no infographic resolved")
        if not s["content"]:
            errors.append(f"{s['id']}: no content page resolved")
        if s["infographic_fallback"]:
            warnings.append(f"{s['id']}: infographic fallback ({s['skill']})")
        if s["content_fallback"]:
            warnings.append(f"{s['id']}: content fallback ({s['skill']})")
    if not only_course:
        for course, n in expect.items():
            if counts.get(course, 0) != n:
                errors.append(f"{course}: {counts.get(course, 0)} sessions (want {n})")
    dupes = {g for g in all_games if all_games.count(g) > 1}
    if dupes:
        errors.append(f"duplicate games across curriculum: {sorted(dupes)}")
    report["validation"] = {"errors": errors, "warnings": warnings}
    return errors, warnings


# --------------------------------------------------------------------------- #
# Main                                                                         #
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="rebuild game index cache")
    ap.add_argument("--check", action="store_true", help="generate + validate, do not publish")
    ap.add_argument("--publish", action="store_true", help="copy build into docs/workshops/")
    ap.add_argument("--course", help="limit to one course")
    args = ap.parse_args()

    cmap = yaml.safe_load((L.HERE / "curriculum_map.yaml").read_text(encoding="utf-8"))
    prompts = yaml.safe_load((L.HERE / "reflection_prompts.yaml").read_text(encoding="utf-8"))
    courses = cmap["courses"]
    sessions = cmap["sessions"]

    print(f"[index] parsing games in {L.GAMES_DIR} …")
    index = L.build_game_index(force=args.force)
    print(f"[index] {len(index)} games")
    pin_lookup = {g["gid"]: g for g in index}
    content_map = L.build_content_map()
    info_map = L.build_infographic_map()
    print(f"[xref] {len(content_map)} content keys · {len(info_map)} infographics")

    report = {}
    used = set()
    # group sessions by course (preserve file order)
    by_course = {}
    for s in sessions:
        by_course.setdefault(s["course"], []).append(s)

    # select games for ALL sessions first (deterministic global de-dup in file order)
    selected = {}
    for s in sessions:
        cc = courses[s["course"]]
        selected[(s["course"], s["week"])] = L.select_games(
            s, index, used, cc, pin_lookup, report)

    # second pass: 2 backup games per session from the REMAINING pool (core reserved first)
    backups = {}
    for s in sessions:
        cc = courses[s["course"]]
        bs = dict(s)
        bs["games"], bs["pins"] = 2, []
        backups[(s["course"], s["week"])] = L.select_games(
            bs, index, used, cc, pin_lookup, report)

    # reset build tree
    if L.BUILD_WORKSHOPS.exists():
        shutil.rmtree(L.BUILD_WORKSHOPS)
    L.BUILD_WORKSHOPS.mkdir(parents=True, exist_ok=True)

    (L.BUILD_WORKSHOPS / "index.md").write_text(
        render_workshops_index(courses), encoding="utf-8")

    used_bases = set()
    for course_key, slist in by_course.items():
        if args.course and course_key != args.course:
            continue
        cc = courses[course_key]
        cdir = L.BUILD_WORKSHOPS / cc["folder"]
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / "index.md").write_text(
            render_course_index(course_key, cc, slist, content_map), encoding="utf-8")
        for i, s in enumerate(slist):
            games = selected[(course_key, s["week"])]
            bks = backups.get((course_key, s["week"]), [])
            used_bases.update(g["base"] for g in games)
            used_bases.update(g["base"] for g in bks)
            prev_s = slist[i - 1] if i > 0 else None
            next_s = slist[i + 1] if i + 1 < len(slist) else None
            md = render_week(s, games, cc, content_map, info_map, prompts,
                             prev_s, next_s, report, backups=bks)
            (cdir / f"week-{s['week']:02d}.md").write_text(md, encoding="utf-8")

    write_nav_fragment(courses, by_course)

    # Confirm every referenced game has a published page in the deployed Games List.
    missing_live = sorted(b for b in used_bases
                          if not (L.DEPLOYED_GAMES / f"{b}.md").exists())
    if missing_live:
        report["games_not_on_live_site"] = missing_live

    errors, warnings = validate(report, courses, args.course)
    (L.BUILD / "_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n[done] {len(report.get('sessions', []))} sessions · "
          f"{len(used_bases)} unique games referenced")
    if report.get("games_not_on_live_site"):
        print(f"[warn] {len(report['games_not_on_live_site'])} referenced game(s) "
              f"not found in the deployed Games List:")
        for b in report["games_not_on_live_site"][:20]:
            print(f"   - {b}")
    if warnings:
        print(f"[warn] {len(warnings)} warning(s):")
        for w in warnings[:40]:
            print(f"   - {w}")
    if errors:
        print(f"[FAIL] {len(errors)} error(s):")
        for e in errors:
            print(f"   ✗ {e}")
    else:
        print("[ok] validation passed")

    if args.publish and not errors:
        if L.PUBLISH_WORKSHOPS.exists():
            shutil.rmtree(L.PUBLISH_WORKSHOPS)
        shutil.copytree(L.BUILD_WORKSHOPS, L.PUBLISH_WORKSHOPS)
        print(f"[publish] -> {L.PUBLISH_WORKSHOPS}")
    elif args.publish and errors:
        print("[publish] skipped — fix validation errors first")
        return 1
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
