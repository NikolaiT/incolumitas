#!/bin/bash

PRIV_KEY=~/.ssh/ipapi_is;
SERVER=root@162.55.51.87;
ROOT="$(cd "$(dirname "$0")" && pwd)"

if [[ $1 = "build" ]]; then
  pelican -s publishconf.py;
fi

# Shrink large JPEG/PNG/WebP in output/ to WebP and rewrite generated HTML.
if [[ -d "$ROOT/output" ]]; then
  echo "Compressing images"
  python3 "$ROOT/compress_images.py" "$ROOT/output" || exit 1
else
  echo "error: output/ does not exist; run with 'build' or ./deploy.sh first" >&2
  exit 1
fi

# isso runs on the same server as the blog (proxied via isso.incolumitas.com -> localhost:7136).
# Config lives at /var/lib/isso/isso.cfg, service unit at /etc/systemd/system/isso.service.
function deploy_isso () {
  scp -i $PRIV_KEY isso/isso.service $SERVER:/etc/systemd/system/isso.service;
  scp -i $PRIV_KEY isso/isso_nginx.conf $SERVER:/etc/nginx/sites-available/isso_nginx.conf;
  ssh -i $PRIV_KEY $SERVER "systemctl daemon-reload && systemctl restart isso && systemctl reload nginx";
}

if [[ $1 = "isso" ]]; then
  deploy_isso;
fi

echo "Upload blog contents"
# --exclude protects legacy content that only exists on the server
# (no source in this repo) from being deleted by --delete:
#   /pages/Hosting-Providers-List/  -> old generated page, still gets traffic
rsync -avc --delete \
  --exclude '/pages/Hosting-Providers-List/' \
  -e "ssh -i $PRIV_KEY" "$ROOT/output/" $SERVER:/var/www/incolumitas.com/
ssh -i $PRIV_KEY $SERVER "chown -R www-data:www-data /var/www/incolumitas.com/"
