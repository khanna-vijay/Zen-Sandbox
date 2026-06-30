# Improv Workshops Curriculum — Approach & Design

**Project:** Improv Workshops (facilitation layer for `v3-github-pages/`)
**Status:** Approved design — build follows the phases in §10
**Date:** 2026-06-30

> Companion to `01_Requirements.md`. This doc holds the architecture, the full **52-session
> blueprint**, the **session page template**, the **generator design**, the **cross-reference
> resolver**, file-naming, data flow, risks, and the phased build plan.

---

## 1. Design philosophy

Three ideas govern every decision:

1. **Reference, don't fork.** The repo already has the canon (framework), the depth (content
   pages), the visuals (infographics), and the activities (1,381 games). The workshops layer is
   a thin, high-value **orchestration** over them — a year-long *path* through assets that
   already exist. It links; it does not restate.
2. **The framework's diagonal path is the spine.** Sequence **by Stage across all domains**, not
   domain-by-domain. Each course re-walks Self→Partner→Scene→Ensemble→Audience at a higher
   Maturity Stage, climbing the Layer axis (Technique→Skill→Principle). Safety (Layer 0) comes
   first and is recommitted each course.
3. **Deterministic + curated (hybrid).** A human-authored blueprint encodes the *pedagogy*
   (what each week teaches, hero games, build-on chains); a stdlib Python generator handles the
   *mechanics* (game selection from the gated pool, cross-ref resolution, rendering, validation).
   Editing the blueprint + rerun = new curriculum, reproducibly.

---

## 2. System overview

```
                 AUTHORED                         GENERATED                         PUBLISHED
   ┌────────────────────────────┐   ┌──────────────────────────────┐   ┌────────────────────────────┐
   │ curriculum_map.yaml (52)   │   │ improv_lib.py                │   │ docs/workshops/             │
   │ reflection_prompts.yaml    │──▶│   • index 1,381 games        │──▶│   index.md                  │
   │                            │   │   • select (gate+rank+dedup) │   │   01_beginner/  (16 weeks)  │
   └────────────────────────────┘   │   • crossref resolver        │   │   02_intermediate/(18 weeks)│
                                     │ generate.py                  │   │   03_advanced/  (18 weeks)  │
   ┌────────────────────────────┐   │   • render pages → build/    │   │   games/<slug>.md (curated) │
   │ SOURCES (read-only):       │──▶│   • copy used game pages     │   └────────────────────────────┘
   │  games DB · content ·      │   │   • self-validate            │                │
   │  infographics · tracker    │   └──────────────────────────────┘                ▼
   └────────────────────────────┘                                        mkdocs.yml: + navigation.tabs
```

Generation writes to `workshop_design/build/`; a publish step copies it into
`v3-github-pages/docs/workshops/`. The MkDocs site then exposes it as the **Workshops** tab.

---

## 3. The 52-session blueprint

IDs use the framework scheme: `DX` domain, `DX.SX` skill. **Layer 0** = Safety & Consent
container. Each row → one `week-NN.md`. (Authoritative machine copy: `curriculum_map.yaml`.)

### 3.1 Beginner — *Foundations: The Brave Beginner* (16 wks · Novice → Adv. Beginner · Technique)

| Wk | Title | Domain | Primary skill | Maturity focus |
|---:|---|---|---|---|
| 1 | Welcome & the Safety Container | Layer 0 / Partner | Boundary Navigation `D2.S6` | Consent overrides agreement; check-ins, "Cut" |
| 2 | The First Thought Is a Gift | Self | Unfiltered Spontaneity `D1.S1` | Offer the first thought in drills |
| 3 | The Emotional Dial | Self | Emotional Fluidity `D1.S2` | Switch emotion on an external cue |
| 4 | Your Body Speaks | Self | Physicality & Space Work `D1.S3` | Character walks/centers; basic object work |
| 5 | Finding Your Voice | Self | Vocal Craft `D1.S4` | Projection on command; one character voice |
| 6 | Fail Joyfully & Recover | Self | Self-Recovery `D1.S6` | Reframe the flub; "that's exactly what I meant" |
| 7 | Really Listening | Partner | Active Listening `D2.S1` | Last-word response in drills |
| 8 | Yes, And — Accept & Add | Partner | Offer Reception `D2.S4` | Clear "Yes, And…" in drills |
| 9 | Make Your Partner a Genius | Partner | Active Gifting `D2.S5` | Give a clear endowment when prompted |
| 10 | Two Minds, One Mirror | Partner | Empathy & Mirroring `D2.S3` | Mirror exercise; emotional echo |
| 11 | Status: High & Low | Partner | Status Modulation `D2.S2` | Play assigned high/low status |
| 12 | Show, Don't Tell (Build a World) | Scene | World-Building / CROW `D3.S5` | Establish Character-Relationship-Objective-Where |
| 13 | Make It Make Sense | Scene | Justification `D3.S6` | Justify the absurd |
| 14 | We're a Team | Ensemble | Support Work `D4.S2` | Clean walk-on / tap-in on instruction |
| 15 | Playing to the Back Row | Audience | Stage Presence & Clarity `D5.S3` | Cheat out & project when reminded |
| 16 | Putting It Together (Showcase) | All | Integration | A full short-form mini-set |

### 3.2 Intermediate — *Choices Under Pressure* (18 wks · Competent · Technique→Skill)

| Wk | Title | Domain | Primary skill | Maturity focus |
|---:|---|---|---|---|
| 1 | Re-entry & Safety Recommit | Layer 0 / Self | Unfiltered Spontaneity `D1.S1` | Bypass the editor under mild scene pressure |
| 2 | Emotion with Logic | Self | Emotional Fluidity `D1.S2` | Transition when scene logic calls |
| 3 | The Power of Stillness | Self | Silence & Stillness `D1.S5` | Decide when a moment needs silence |
| 4 | Listening for Subtext | Partner | Active Listening `D2.S1` | Build on the partner's *specific* offers |
| 5 | The Status Seesaw | Partner | Status Modulation `D2.S2` | Pick status that fits the relationship |
| 6 | Gifting that Serves | Partner | Active Gifting `D2.S5` | Choose gifts that ease the partner's job |
| 7 | Finding the Game | Scene | Game Identification `D3.S1` | Identify the game *during* the scene [GAME] |
| 8 | Heightening the Pattern | Scene | Heightening & Exploration `D3.S2` | The ladder; explore the "why" |
| 9 | The Story Spine | Scene | Narrative Architecture `D3.S3` | Build Platform, then Tilt [NARRATIVE] |
| 10 | What's at Stake | Scene | Stakes / The "Want" `D3.S4` (+`D3.S7`) | Establish what's at risk for the character |
| 11 | Which Engine? Game vs Story | Scene | Engine Selection (meta) | Choose an engine consciously at scene start |
| 12 | Build the World, Justify the Absurd | Scene | World-Building `D3.S5` (+`D3.S6`) | Endowment chains; reincorporation |
| 13 | Eyes in the Back of Your Head | Ensemble | Peripheral Awareness `D4.S1` | Track all active threads |
| 14 | Support Work that Lands | Ensemble | Support Work `D4.S2` | Enter only when a scene needs something |
| 15 | A-to-C: Beyond the Obvious | Ensemble | Suggestion Deconstruction `D4.S3` | Select the non-obvious ("C") premise |
| 16 | Editing on Time | Ensemble | Pacing & Rhythm `D4.S4` | Edit at the right moment (Sweep / Tag-out) |
| 17 | Reading the Room | Audience | Room Reading `D5.S1` (+`D5.S2`) | Read temperature; ride a laugh, re-engage |
| 18 | Competent Showcase | All | Integration | Mixed game + story scenes |

### 3.3 Advanced — *Serve the Piece* (18 wks · Proficient → Master · Skill→Principle)

| Wk | Title | Domain | Primary skill | Maturity focus |
|---:|---|---|---|---|
| 1 | Re-entry: Impulse = Action | Layer 0 / Self | Unfiltered Spontaneity `D1.S1` | No latency; model safety for total risk-taking |
| 2 | The Voice as Instrument | Self | Vocal Craft `D1.S4` (+`D1.S2`) | Modulate real emotion to serve the scene |
| 3 | The Shared Mind | Partner | Active Listening `D2.S1` (+`D2.S5`) | Read breath/micro-expressions; invisible gifting |
| 4 | Invisible Status | Partner | Status Modulation `D2.S2` | Status purposeful and unnoticed |
| 5 | Find It, Play It, Break It | Scene | Game Identification `D3.S1` (+`D3.S2`) | Find, play, *and* intentionally break the game |
| 6 | Architecting the Arc | Scene | Narrative Architecture `D3.S3` | Full arc + consequence + change in real time |
| 7 | Stakes They Can Feel | Scene | Raising the Stakes `D3.S7` (+`D3.S4`) | Make the audience care about absurd people |
| 8 | Engine-Switching Mid-Scene | Scene | Engine Selection (meta) | Serve game *or* story invisibly |
| 9 | Group Mind & Follow the Follower | Ensemble | Peripheral Awareness `D4.S1` (principles) | See the whole show as one organism |
| 10 | Invisible Support, Surrendered Ego | Ensemble | Support Work `D4.S2` | Off-focus support elevates others |
| 11 | Weaving the Threads | Ensemble | Thematic Synthesis `D4.S5` | Callbacks & mapping; weave the threads |
| 12 | Conducting Pace | Ensemble | Pacing & Rhythm `D4.S4` | Edit the audience never consciously notices |
| 13 | The Harold | Ensemble | Format Literacy `D4.S6` | Longform structure I |
| 14 | Armando, Montage & Longform | Ensemble | Format Literacy `D4.S6` | Longform structure II |
| 15 | Unify the Room | Audience | Room Reading `D5.S1` | Convert a fragmented audience into one organism |
| 16 | Conducting Audience Energy | Audience | Audience-Energy Management `D5.S2` | Direct address as a deliberate lever |
| 17 | Serve the Piece | Ensemble / Audience | (principles: Serve the Piece / Story) | Choose what the show needs, not what you want |
| 18 | Capstone Performance | All | Integration: full longform | Audience as co-author |

**Totals:** 16 + 18 + 18 = **52**. Domains touched each course: all five. Layer 0 first +
recommitted W1 of each course.

---

## 4. Session page template (`week-NN.md`)

```
---
title: "W<NN> · <Title>"
course: <beginner|intermediate|advanced>
week: <NN>
domain: "D<X> — <name>"
primary_skill: "<ID> <name>"
maturity_stage: "<stage>"
---

# Week <NN> — <Title>
> <one-line essence of the day>

| Course | Week | Domain | Focus | Stage | Time |
|---|---|---|---|---|---|
| <Course> | <NN>/<total> | <domain> | <skill ID + name> | <stage> | 60 min |

!!! note "Builds on"
    <link to prior session(s) this depends on>

## ⏱️ Session flow (60 min)
| Time | Block |
|---|---|
| 0:00–0:05 | Arrival & safety check-in |
| 0:05–0:15 | Warm-up game |
| 0:15–0:27 | 1. Today's theory |
| 0:27–0:52 | 2. Today's games |
| 0:52–1:00 | 3. Reflection & debrief |

## 1. 🧠 Today's Theory
**Focus:** <Skill/Principle/Technique + ID> · **Maturity goal today:** <stage benchmark>

![<alt>](../../assets/infographics/<DX.SX[.TY]>.jpg){ .infographic }

- <2–4 crisp bullets: core idea, the day's stage benchmark, the one cue to coach>

> 📖 **Go deeper:** [<Skill name>](../../content/<domain>/<file>.md)

## 2. 🎲 Today's Games
### Warm-up — <game name>
<compact card> · *Trains:* … · *Cue:* … · [full game »](../games/<slug>.md)
### Core — <game name(s)>  (1–2)
<compact card> · *Trains:* … · *Cue:* … · [full game »](../games/<slug>.md)

## 3. 💭 Self-Reflection
**Deepen your improv**
1. <from the day's game Debrief Qs>
2. <skill-specific improv question>
**Beyond the stage**
3. <life/work/leadership transfer prompt keyed to today's skill>

---
*Builds on: W<NN-…>  ·  Next: [W<NN+1> — <title>](week-<NN+1>.md)*
```

Course `index.md` pages: course goal, maturity arc, the week list (table), how-to-use. Workshops
`index.md`: the three courses, the diagonal-path rationale, the 60-minute model, Layer-0-first
note.

---

## 5. Generator design

### 5.1 `improv_lib.py` (library)
- **`load_game_index()`** — parse YAML frontmatter of every `Updated_Games_V2/*.md`; return a
  list of dicts (id `G###`, slug, title, primary_domain, principle/skill/technique IDs +
  `skill_ids[]`, skill_level, complexity_level, min/max participants, duration, energy,
  physicality, modality, props, body sections incl. **Debrief**). Cache → `build/_game_index.json`.
- **`select_games(session, pool, used)`** — see §6.
- **`resolve_infographic(domain, skill, technique)`** — existence-checked path with fallback
  (technique → skill → domain) — see §7.
- **`resolve_content_link(domain, skill, technique)`** — map IDs → content filename under
  `docs/content/0X_<domain>/` (using the on-disk filenames / `tracker.json` slugs).
- **`copy_game_page(game)`** — write a clean text-only `docs/workshops/games/<slug>.md` (MkDocs
  `title` frontmatter + the game body; **no PNG**).

### 5.2 `generate.py` (orchestrator)
1. Load `curriculum_map.yaml` + `reflection_prompts.yaml` + game index.
2. For each session: select games (pinned first, then auto), resolve infographic + content
   links, assemble reflection (game Debrief Qs + transfer prompt), render `week-NN.md`.
3. Copy each used game → `games/<slug>.md`.
4. Render course `index.md` ×3 + Workshops `index.md`.
5. **Self-validate** (§9); write `build/_report.json`; print a summary.
6. Output to `build/`; `--publish` copies `build/` → `../v3-github-pages/docs/workshops/`.

Flags: `--publish`, `--course <name>`, `--force` (rebuild cache), `--check` (validate only).

---

## 6. Game-selection algorithm

For each session, from the global index minus already-`used` games:

1. **Gate** (hard filters):
   - skill/technique match: `session.skill_id ∈ game.skill_ids` (or domain match for
     integration weeks / principle weeks);
   - `game.skill_level ∈ course.skill_levels`;
   - `game.complexity_level ∈ course.complexity_range`;
   - modality ∈ {in_person, hybrid} (virtual allowed for online cohorts via a map flag).
2. **Rank** (score, high→low): exact primary-skill match (+3) → complexity at the course's sweet
   spot (+2) → ideal group size fits a class (+1) → duration ≤ block budget (+1) → has a Debrief
   block (+1) → energy fits slot (warm-up=high, core=any).
3. **Pick**: honor **pinned** game IDs from the blueprint first; fill remaining slots (target
   1–3, default 2: one warm-up + one core) from the ranked list; mark chosen games `used`.
4. **Fallback**: if the gate empties (rare, e.g. proficient + complexity 5), widen one notch
   (complexity ±1, or domain-match) and **log** the relaxation.

De-dup is global: a `used` set spanning all 52 sessions guarantees no repeats (FR-6).

---

## 7. Cross-reference resolver

| Target | Path pattern (from `workshops/<course>/week-NN.md`) | Fallback |
|---|---|---|
| Infographic (technique) | `../../assets/infographics/DX.SX.TY.jpg` | → skill image |
| Infographic (skill) | `../../assets/infographics/DX.SX.jpg` | → any technique image in skill → domain note |
| Content page (skill) | `../../content/0X_<domain>/0X_SX__<slug>.md` | → domain folder index |
| Content page (technique) | `../../content/0X_<domain>/0X_SX_TY__<slug>.md` | → parent skill page |
| Game page | `../games/<slug>.md` (copied text-only) | n/a (always copied) |

**Known infographic gaps** (no per-skill summary jpg): `D3.S*`, `D5.S*`, plus `D2.S6`, `D4.S5`,
`D5.S2.T1`. The resolver substitutes a technique-level image for that skill (or the domain), and
records every substitution in `_report.json` so gaps are visible, never faked.

---

## 8. Reflection design

- **Deepen-your-improv** questions: pulled from the **Debrief** section of the day's selected
  games (already authored, scene-specific) — pick 1–2.
- **Beyond-the-stage** question: one per session from `reflection_prompts.yaml`, keyed by skill
  ID — a concrete life/work/leadership transfer (e.g. Active Listening → *"Recall a meeting where
  you were loading your reply instead of listening. What did you miss?"*). Each skill has a
  curated prompt; integration weeks draw a synthesis prompt.

---

## 9. Self-validation (run every build)

Assertions (fail the build, or warn, as marked):
- **[fail]** exactly 16 + 18 + 18 week files exist;
- **[fail]** no game `slug` appears in more than one session;
- **[fail]** every session has 1–3 games and 2–3 reflection questions;
- **[fail]** every embedded infographic path exists on disk;
- **[fail]** every content deep-link resolves to an existing file;
- **[warn]** any infographic/content fallback used (listed in `_report.json`);
- **[warn]** any session whose game gate needed relaxation.

---

## 10. Build phases

| Phase | Output |
|---|---|
| **A** ✅ | `documentation/01_Requirements.md` + `02_Approach_and_Design.md` |
| **B** | `curriculum_map.yaml` (52 rows) + `reflection_prompts.yaml` |
| **C** | `improv_lib.py` + `generate.py` |
| **D** | `build/` generated + self-validation green; spot-check 3 sessions |
| **E** | copy → `docs/workshops/`; add `navigation.tabs` to `mkdocs.yml`; `mkdocs build` clean |
| **F** | *(on request)* git publish via `v3_push_updates_to_gitpages.sh` |

---

## 11. File naming

```
workshop_design/
  documentation/01_Requirements.md, 02_Approach_and_Design.md
  curriculum_map.yaml          # 52 session rows + course config
  reflection_prompts.yaml      # skill_id -> transfer prompt
  improv_lib.py  generate.py  README.md
  build/                       # generated mirror of docs/workshops/ + _game_index.json + _report.json

docs/workshops/                # published tree (numeric prefixes => deterministic order)
  index.md
  01_beginner/index.md     + week-01.md … week-16.md
  02_intermediate/index.md + week-01.md … week-18.md
  03_advanced/index.md     + week-01.md … week-18.md
  games/<slug>.md
```

---

## 12. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Game gate too narrow (proficient/complexity-5 sparse) | Ranked fallback widens one notch + logs; Advanced leans on competent + formats |
| Infographic gaps (D3/D5 per-skill) | Resolver falls back technique→skill→domain; reported, never faked |
| Game links breaking once published | Used games copied into `workshops/games/` (text only); validated in build |
| Nav label cosmetics (`01 Beginner`) | Matches existing `01 The Self` convention; explicit-nav polish is a later option |
| Duplicate games across 52 weeks | Global `used` set + self-check assertion |
| Source paths differ on Windows vs WSL | Path constants at top of `improv_lib.py`; one place to retarget |

---

## 12b. Addendum (2026-06-30) — deployment integration (corrected)

Clarified after inspecting the live pipeline. **Two tracks exist:**

| Track | Role | Git |
|---|---|---|
| `v3-github-pages/` | **Local pipeline SOURCE** (generated content, infographics, `pipeline/publish.py`) | **gitignored** (`/v3-github-pages/`) |
| `github-pages-v3/` | **Deployed, committed site** → `khanna-vijay.github.io/Zen-Sandbox/` | tracked & pushed |

`pipeline/publish.py` mirrors SOURCE→DEPLOYED, compresses infographics, **copies all 1,381
games into `github-pages-v3/docs/games/<coded>.md`** (coded filename = `Updated_Games_V2`
basename) and builds the filterable **Games List**, then auto-writes `github-pages-v3/mkdocs.yml`.

**What changed in the workshops build to fit this reality:**
- **No game copies.** All 1,381 games are *already live* under `/games/` with coded names.
  Session pages link straight to them: `../../games/<coded-base>.md` (e.g.
  `D1_P1_S1_T0_G791__oscar-winning-moment.md`) — so they cross-reference the existing Games List.
- **Output mirrored via `publish.py`.** `generate.py --publish` writes the source tree
  (`v3-github-pages/docs/workshops/`); a new `build_workshops()` in `publish.py` runs the
  generator, mirrors the tree into `github-pages-v3/docs/workshops/`, and splices the
  **Workshops nav block** (from `workshop_design/build/_nav.yml`) into the auto-generated
  `mkdocs.yml`. With `navigation.tabs`, **Workshops** becomes a top tab beside **Content** and
  **Games List**.
- **Site renamed** `The Improv Framework` → **`An Improv Framework`** (`site_name` + `copyright`).
- **Validation** additionally checks every referenced game has a published page in
  `github-pages-v3/docs/games/`.

**Verified:** `mkdocs build` (strict) of the deployed site passes — 52 week pages built; coded
game links, content "Go deeper" links, and embedded infographics all resolve.

## 13. Verification (end-to-end)

1. `cd workshop_design && python3 generate.py --check` → self-validation green.
2. `python3 generate.py --publish` → tree lands in `docs/workshops/`.
3. `cd ../v3-github-pages && pip install -r requirements.txt && mkdocs build` → no missing-file
   / broken-link warnings for the Workshops tree.
4. `mkdocs serve` → **Workshops** tab present; 3 courses navigable; infographics render; content
   deep-links open the right skill pages; game links open published game pages; each session shows
   theory + 1–3 games + 2–3 reflections.
