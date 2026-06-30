# Improv Workshops Curriculum — Requirements

**Project:** Improv Workshops (facilitation layer for `v3-github-pages/`)
**Working folder:** `30_Improv_GitBook-Website/workshop_design/`
**Status:** Approved — *specs first, generate after sign-off*
**Date:** 2026-06-30
**Owner:** khanna-vijay

---

## 1. Purpose

Turn the existing improv **knowledge base** (framework + games + content + infographics) into a
**facilitation layer**: three ready-to-teach courses a coach can run cold.

- **Beginner**, **Intermediate**, **Advanced** — **1 hour / session / week**.
- **16 / 18 / 18 weeks = 52 one-hour sessions** spanning a year.
- Each session = **(1) theory** (skill/principle/technique + its infographic, deep-linked to the
  full content page) → **(2) 1–3 games** for the day (from the 1,381-game database) → **(3) 2–3
  self-reflection questions** that deepen improv *and* transfer to "other-worldly affairs"
  (life, work, leadership).
- Complexity ramps **logically** across each course, governed by the framework's **Maturity
  Stages**, building on prior sessions.
- Published as a new **"Workshops" tab** on the MkDocs site, **cross-referencing** the existing
  content pages, infographics, and game cards so the site stays one coherent organism.

This is the **teaching/delivery track**, complementary to the existing **knowledge track**
(`v3-github-pages/` — the 119-node encyclopedia). Where the knowledge track answers *"what is
this concept?"*, the workshops track answers *"how do I teach a year of it, week by week?"*

---

## 2. Source of Truth

| Input | Location | Role |
|---|---|---|
| Framework (Markdown) | `/mnt/d/VIjay/__Improv/__VK_Improv_Online_Sessions/Research/Improv_Framework.md` | Canon: domains, principles/skills/techniques, **Maturity Stages**, diagonal teaching path |
| Framework (JSON) | `30_Improv_GitBook-Website/Improv_Framework.json` | Machine source — node enumeration (5 domains, 18 principles, 28 skills, 68 techniques) |
| Categories / Layer 0 | `…/Research/Improv Categories.md` | The 5-category extraction + **Layer 0 Safety & Consent container** (taught first) |
| Curriculum page templates | `…/Research/Proposed_Framework_forCurriculum_Design.md` | Per-layer entry templates + the standardized **Game Mechanics block** |
| Games database | `31_All_Improv_Code/03_Improv_Game_Database/Updated_Games_V2/*.md` | **1,381** game cards, rich YAML frontmatter + structured body |
| Teaching content | `v3-github-pages/docs/content/0X_<domain>/*.md` | **80** deep skill/technique pages (deep-link targets) |
| Infographics | `v3-github-pages/docs/assets/infographics/DX.SX[.TY].jpg` | **78** square images (embed targets) |
| Node index | `v3-github-pages/tracker.json` | Canonical IDs + slugs for deterministic cross-linking |
| Inspiration syllabi | `…/Research/Syllabus Curriculum/`, `…/Reusable Assets/` | Format reference (momentImprov leveled syllabus, Harvard, TCS, IAIDB) |
| Site config | `v3-github-pages/mkdocs.yml` | MkDocs Material; auto-nav; tab to be added |

> **Authority rule:** the **framework MD/JSON** is authoritative for *which concepts exist and
> their maturity progression*; the **games DB frontmatter** is authoritative for *game facts*
> (difficulty, players, time, props); the **content pages** are authoritative for *deep theory*.
> The workshops layer **references** these — it never restates or forks the canon.

---

## 3. The pedagogical model (what drives sequencing)

The framework defines a **3-axis model** and a **diagonal teaching path**:

- **Domain** (Self → Partner → Scene → Ensemble → Audience) — *in relation to whom*.
- **Layer** (Principle → Skill → Technique) — *level of abstraction*. You **learn bottom-up**
  (Technique→Principle) and **perform top-down**.
- **Stage** (Novice → Adv. Beginner → Competent → Proficient → Master) — *level of development*.

> **Central thesis:** mastery is not *more* techniques — it is the *same* techniques governed by
> *deeper* principles. The curriculum must climb the **Layer** axis as it advances the **Stage**
> axis, touching **every domain at each stage** (the "diagonal path"), not finishing one domain
> before the next.

### 3.1 Course → Stage → difficulty mapping

| Course | Weeks | Maturity stage | Layer focus | Game `skill_level` window | `complexity_level` |
|---|---:|---|---|---|---|
| **Beginner** | 16 | Novice → Adv. Beginner | Technique (effortful → fluent) | novice, advanced_beginner | 1–2 |
| **Intermediate** | 18 | Competent | Technique → Skill bridge | advanced_beginner, competent | 2–3 |
| **Advanced** | 18 | Proficient → Master | Skill → Principle | competent, proficient | 3–5 + formats |

The game pool supports this: **novice 399 · advanced_beginner 413 · competent 518 · proficient
51**; **complexity 1–3 = 1,242 cards**. Advanced leans on competent+proficient cards plus the
longform **formats** (Harold/Armando/Montage, `D4.S6`).

---

## 4. Functional Requirements

### FR-1 — Three courses, 16 / 18 / 18 = 52 sessions
Exactly 52 weekly sessions: Beginner 16, Intermediate 18, Advanced 18. Each session is a single
self-contained, one-hour lesson plan.

### FR-2 — Diagonal/spiral sequencing
Each course spirals through **all five domains** (Self → Partner → Scene → Ensemble → Audience)
at the course's maturity stage. **Layer 0 (Safety & Consent)** is taught **first** in Beginner
W1 and **re-committed** at the opening of Intermediate and Advanced.

### FR-3 — Maturity-gated complexity ramp
Game selection for each session is gated by the course's `skill_level` + `complexity_level`
window (FR-1 table). Within a course, complexity trends upward week over week; later sessions
**build on** earlier ones (explicit "builds on" back-references).

### FR-4 — Fixed per-session structure (the required format)
Every session page renders, in order:
1. **Header / at-a-glance** — course, week, title, maturity stage, domain, primary
   Principle/Skill/Technique IDs, 1-hour timebox.
2. **Session flow (60 min)** — Check-in 5 · Warm-up 10 · **Theory 12** · **Games 25** ·
   **Reflection/Debrief 8**.
3. **1. Today's Theory** — concise key idea + the **maturity-stage focus** for the day +
   **embedded infographic** + **deep-link** to the full content page(s).
4. **2. Today's Games (1–3)** — per game: compact card (players, time, complexity, energy,
   props), "what it trains", a facilitation cue, link to the published game page.
5. **3. Self-Reflection (2–3 Qs)** — at least one *Deepen-your-improv* question and at least one
   *Beyond-the-stage* (life/work/leadership) transfer question.
6. **Footer** — recap, "builds on" + "next week" pointers, cross-links.

### FR-5 — Theory by reference, not duplication
The theory block is **concise** (facilitator-ready) and **deep-links** to the existing content
page for the skill/technique rather than restating the 30 KB page. Each session embeds the
matching infographic (`DX.SX.jpg` skill-level, or `DX.SX.TY.jpg` technique-level).

### FR-6 — Games sourced from the database, de-duplicated
Games come from `Updated_Games_V2`. Each session lists **1–3**; **no game is used twice** across
the whole 52-session curriculum. Selection may be **pinned** (curated hero games in the
blueprint) or **auto-selected** by the generator from the maturity-gated pool.

### FR-7 — Reflection: improv + worldly transfer
Each session has **2–3** reflection questions. At least one is mined from the day's game
**Debrief** questions (improv depth); at least one is a **transfer** prompt keyed to the day's
skill (how the skill serves leadership, collaboration, communication, presence, etc.).

### FR-8 — Cross-referencing that resolves in the published site
All three cross-reference types must produce **working links in the built MkDocs site**:
- **Infographic** → embedded image, existence-checked, with graceful fallback
  (technique → skill → domain image) for the known gaps (D3/D5 per-skill summaries, D2.S6,
  D4.S5, D5.S2.T1).
- **Content page** → relative link into `../../content/0X_<domain>/…`.
- **Game card** → the curated games used by the curriculum are **published** into the Workshops
  tab (`workshops/games/<slug>.md`, **text only**) so links resolve; the heavy 4 MB game PNGs
  are **not** copied.

### FR-9 — "Workshops" tab on the site
A new top-level **Workshops** tab in the MkDocs nav, with a landing page (3 courses + the
maturity-path rationale) and a left-sidebar section per course, each listing its weeks in order.

### FR-10 — Hybrid generator (authored blueprint + renderer)
A human-authored **`curriculum_map.yaml`** (one row per session: course, week, title, domain,
target Principle/Skill/Technique IDs, maturity stage, pinned games, "builds on") drives a
**Python generator** that selects games, resolves cross-references, and renders all pages. The
build is **re-runnable**: editing the map + rerun regenerates the output deterministically.

### FR-11 — Reproducible, self-validating build
The generator caches a game index, regenerates `build/` from scratch on demand, and runs
**self-checks**: 52 week files present (16/18/18), no duplicate games, every session has 1–3
games + 2–3 reflections + ≥1 existing infographic + ≥1 resolvable content link.

### FR-12 — All code + output under `workshop_design/`
Every script, the blueprint, prompt/data files, and generated `build/` output live under
`workshop_design/`. Publishing copies the generated tree into `v3-github-pages/docs/workshops/`.

---

## 5. Content Quality Requirements

| ID | Requirement |
|---|---|
| CQ-1 | **Facilitator-ready.** A coach can teach the hour from the page alone — clear timings, setup, cues, debrief. |
| CQ-2 | **Crisp theory, deep links.** Theory is a tight summary; depth lives behind the content-page link (no 30 KB restatement). |
| CQ-3 | **Consistent shape.** Every session of every course shares the same skeleton (FR-4) so the year reads coherently. |
| CQ-4 | **Faithful to canon.** Maturity-stage language, engine distinctions (Game vs Narrative; Heightening ≠ Raising the Stakes), and Layer-0-first are respected, not reinvented. |
| CQ-5 | **Logical build.** Each session names what it **builds on**; complexity rises within and across courses. |
| CQ-6 | **Honest references.** A link is only emitted if its target file exists; missing infographics fall back gracefully and are logged, never faked. |
| CQ-7 | **Transfer is real, not glib.** "Beyond-the-stage" questions connect the *specific* day's skill to a concrete life/work situation. |

---

## 6. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | **Stdlib-only generator.** Python 3, standard library only (plus the repo's existing MkDocs deps for building). No LLM calls in the generate step — pure deterministic assembly. |
| NFR-2 | **Idempotent / re-runnable.** Re-running the generator reproduces identical output; `build/` is disposable and regenerable. |
| NFR-3 | **Cross-platform paths.** Source paths span `C:`/`D:` (WSL `/mnt/c`, `/mnt/d`); paths are configurable constants at the top of the generator. |
| NFR-4 | **No heavy assets committed.** Game PNGs (~4 MB each) are excluded; only text game pages are published. |
| NFR-5 | **Clean MkDocs build.** Output must pass `mkdocs build` without missing-file/broken-link warnings for the Workshops tree. |
| NFR-6 | **Publish-agnostic build.** Generation and site-wiring are local; the actual GitHub Pages push is a separate, manual step (known flaky-API / manual-Pages-enable gotchas). |

---

## 7. Out of Scope (v1)

- Re-authoring or editing the existing **content pages**, **infographics**, or **game cards**
  (this layer references them; it does not modify the canon).
- LLM-generated session prose (the generator is deterministic; any future "enrich a session
  with an LLM" step is a later toggle).
- Per-game PNG infographics in the site, audio/video, and PDF/printable export (a print
  stylesheet is a possible later enhancement).
- Automated GitHub Pages deployment (handled by the existing `v3_push_updates_to_gitpages.sh`
  when the user asks).
- Assessment/grading tooling (the framework's maturity tables already serve as the rubric;
  surfacing them per session is in scope, building an app around them is not).

---

## 8. Acceptance Criteria

1. `workshop_design/curriculum_map.yaml` defines **all 52 sessions** (16/18/18) with target IDs
   and pinned/auto game strategy.
2. The generator produces `docs/workshops/` with a landing page, 3 course sections, and 52
   `week-NN.md` files, plus curated `games/<slug>.md` pages — **no game reused**.
3. Every session page conforms to FR-4 (theory + 1–3 games + 2–3 reflections), embeds ≥1
   **existing** infographic, and deep-links ≥1 **existing** content page.
4. `mkdocs build` succeeds with **no** missing-file/broken-link warnings for the Workshops tree;
   the **Workshops tab** appears with all three courses navigable.
5. Spot-check of one session per course confirms: infographic renders, content deep-link opens
   the correct skill page, game links open published game pages, reflection includes both an
   improv and a beyond-the-stage question.
6. Self-check script passes (FR-11).

---

## 9. Decisions (locked at planning)

| # | Decision | Resolution |
|---|---|---|
| D-1 | Week split across 16–18 | **16 / 18 / 18 = 52** |
| D-2 | Authoring approach | **Hybrid** — authored `curriculum_map.yaml` + Python renderer |
| D-3 | Theory depth on the page | **Concise + deep-link** to existing content pages |
| D-4 | Sequencing model | **Diagonal/spiral** — all domains per course, rising maturity stage |
| D-5 | Layer 0 placement | **Taught first** (Beginner W1) + re-committed each course |
| D-6 | Games in the site | **Link the already-published games** at `/games/<coded>.md` (no copies) — cross-references the existing Games List by `Updated_Games_V2` coded filename |
| D-7 | Tab mechanism | `navigation.tabs` (already on in the deployed site); Workshops nav block injected by `pipeline/publish.py` |
| D-8 | Target track | Generate into the **deployed `github-pages-v3/`** site (via `publish.py`), not the local-only `v3-github-pages/` source |
| D-9 | Site name | Renamed **The Improv Framework → An Improv Framework** |

> See `02_Approach_and_Design.md` for the architecture, the full 52-session blueprint, the
> generator design, file-naming, data flow, the cross-reference resolver, risks, and the phased
> build plan.
