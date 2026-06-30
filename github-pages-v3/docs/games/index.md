---
title: Game Finder
---

# 🎲 Game Finder

Filter **1381 improv games**. Every facet is **multi-select** — tap chips to combine them.
The number in each chip's brackets shows **how many games remain** if you add it, updating live as
you filter. Search by keyword too, and click any game for its full guide.

<div class="gf">
  <div class="gf-search">
    <label for="g-q">Search</label>
    <input type="search" id="g-q" placeholder="game name or keyword…">
  </div>
  <div class="gf-facet" id="g-dom"><span class="gf-name">Domain</span><span class="gf-chips"></span></div>
  <div class="gf-facet" id="g-lv"><span class="gf-name">Level</span><span class="gf-chips"></span></div>
  <div class="gf-facet" id="g-ty"><span class="gf-name">Type</span><span class="gf-chips"></span></div>
  <div class="gf-facet gf-long" id="g-pr"><span class="gf-name">Principle</span><span class="gf-chips"></span></div>
  <div class="gf-facet gf-long" id="g-sk"><span class="gf-name">Skill</span><span class="gf-chips"></span></div>
  <div class="gf-foot">
    <span class="gf-count" id="g-count">Loading…</span>
    <button id="g-reset" type="button">Reset all</button>
  </div>
</div>

<div id="games-results"></div>
