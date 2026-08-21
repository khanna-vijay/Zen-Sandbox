# Improv Toolkit 🎭

A simple, **visual** guide to improv — the flow of *domains → principles → skills*, with one crisp page per principle and a playful infographic.

**Live site:** https://khanna-vijay.github.io/Zen-Sandbox/

## What's in this repo

```
.
├── .github/workflows/deploy.yml   # builds the site and deploys to GitHub Pages
└── github-pages-v4/               # the live site (this is what gets deployed)
    ├── mkdocs.yml                 # site config + navigation
    ├── requirements.txt           # pinned build dependencies (mkdocs-material + plugins)
    ├── overrides/                 # theme template overrides
    └── docs/                      # the site content
        ├── index.md              # the domains → principles → skills flow
        ├── theory/               # one page per principle, grouped by domain
        ├── games/                # game library
        ├── improv-sports/        # improv sports library
        ├── workshops/            # workshop formats
        ├── solo-practice/        # solo drills
        ├── play/                 # PowerPoint Karaoke and other play pieces
        └── assets/               # infographics, CSS, JS, data files
```

Earlier versions (`github-pages/`, `old_v3-github-pages/`) are kept for reference
only — they are not built or deployed.

## Preview locally

```bash
cd github-pages-v4
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
mkdocs serve            # → http://localhost:8000
```

## How it deploys

Every push to `main` triggers the GitHub Actions workflow, which builds the
MkDocs site and publishes it to GitHub Pages (the workflow enables Pages on its
first run). No manual steps.

## License

Content: **CC BY-SA 4.0**. Configuration/scripts: MIT.
