# Improv Toolkit 🎭

A simple, **visual** guide to improv — the flow of *domains → principles → skills*, with one crisp page per principle and a playful infographic.

**Live site:** https://khanna-vijay.github.io/Zen-Sandbox/

## What's in this repo

```
.
├── .github/workflows/deploy.yml   # builds the site and deploys to GitHub Pages
└── github-pages-v3/
    ├── mkdocs.yml                 # site config + navigation
    ├── requirements.txt           # pinned build dependency (mkdocs-material)
    └── docs/                      # the site content
        ├── index.md              # the domains → principles → skills flow
        ├── principles/           # one page per principle
        └── assets/infographics/  # the principle infographics
```

## Preview locally

```bash
cd github-pages-v3
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
