#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# website_checker.sh — reusable link checker + random navigation tester.
#
# Recursively crawls a website, checks every internal/external link, image,
# stylesheet and script for broken/missing URLs, runs random navigation walks,
# and writes a Markdown report.
#
# Usage:
#   ./website_checker.sh                         # checks the default site
#   ./website_checker.sh https://example.com/    # checks another site
#   ./website_checker.sh https://example.com/ --max-pages 200 --walks 40
#   ./website_checker.sh --help
#
# Output: website_link_report.md (override with --out PATH)
# Requires: python3 (standard library only — no pip installs).
# ---------------------------------------------------------------------------
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_URL="https://khanna-vijay.github.io/Zen-Sandbox/"

PY="$(command -v python3 || command -v python || true)"
if [[ -z "${PY}" ]]; then
  echo "error: python3 not found on PATH" >&2
  exit 127
fi

# First arg is the URL unless it's an option (starts with '-').
URL="${DEFAULT_URL}"
if [[ $# -gt 0 && "${1}" != -* ]]; then
  URL="${1}"; shift
fi

echo "🔎 Checking ${URL}"
echo "   (report: website_link_report.md — pass --out to change)"
exec "${PY}" "${HERE}/website_checker.py" "${URL}" "$@"
