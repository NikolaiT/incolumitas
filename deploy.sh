#!/bin/bash
#
# Build the production site and push it live in one step.
#
#   ./deploy.sh        build with publishconf.py, then rsync output/ to the server
#   ./deploy.sh isso    same, plus redeploy the isso comment service
#
set -euo pipefail

cd "$(dirname "$0")"

DEPLOY_ISSO=""
case "${1:-}" in
  "") ;;
  isso) DEPLOY_ISSO=1 ;;
  -h|--help)
    echo "usage: $(basename "$0") [isso]"
    echo "  (no args)  build with publishconf.py and rsync output/ to the live server"
    echo "  isso       additionally redeploy the isso comment service"
    exit 0
    ;;
  *)
    echo "usage: $(basename "$0") [isso]" >&2
    exit 1
    ;;
esac

# Use the repo venv directly so this works without activating it first.
if [ -x venv/bin/pelican ]; then
  PELICAN=venv/bin/pelican
elif command -v pelican >/dev/null 2>&1; then
  PELICAN=pelican
else
  echo "error: pelican not found, expected venv/bin/pelican" >&2
  exit 1
fi

echo "==> Building production site"
"$PELICAN" content -o output -s publishconf.py

# publishconf.py sets DELETE_OUTPUT_DIRECTORY and publish.sh rsyncs with --delete,
# so shipping a truncated build would take the live site down with it.
HTML_COUNT=$(find output -type f -name '*.html' | wc -l | tr -d ' ')
if [ ! -s output/index.html ] || [ "$HTML_COUNT" -lt 100 ]; then
  echo "error: build looks incomplete ($HTML_COUNT html files), refusing to deploy" >&2
  exit 1
fi

echo "==> Deploying $HTML_COUNT pages"
if [ -n "$DEPLOY_ISSO" ]; then
  ./publish.sh isso
else
  ./publish.sh
fi

echo "==> Done: https://incolumitas.com/"
