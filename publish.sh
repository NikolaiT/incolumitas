#!/bin/bash

PRIV_KEY=~/.ssh/root_new_server;

if [[ $1 = "build" ]]; then
  pelican -s publishconf.py;
fi

function deploy_isso () {
  scp -i $PRIV_KEY /home/nikolai/projects/work/backups/var/lib/isso/comments.db root@167.99.241.135:/var/lib/isso/comments.db;
  scp -i $PRIV_KEY /home/nikolai/projects/private/incolumitas/incolumitas/isso/isso.cfg root@167.99.241.135:/etc/isso.cfg;
  scp -i $PRIV_KEY /home/nikolai/projects/private/incolumitas/incolumitas/isso/isso_nginx.conf root@167.99.241.135:/etc/nginx/sites-available/isso_nginx.conf;
  scp -i $PRIV_KEY /home/nikolai/projects/private/incolumitas/incolumitas/isso/isso.service root@167.99.241.135:/etc/systemd/system/isso.service;
}

if [[ $1 = "isso" ]]; then
  deploy_isso;
fi

echo "Upload blog contents"
rsync -q -avc --delete -e "ssh -i $PRIV_KEY" output/ root@167.99.241.135:/var/www/incolumitas.com/
ssh -i $PRIV_KEY root@167.99.241.135 "chown -R www-data:www-data /var/www/incolumitas.com/"

# echo "Restart server and isso"
ssh -i $PRIV_KEY root@167.99.241.135 "systemctl daemon-reload && systemctl restart isso && systemctl restart nginx"
ssh -i $PRIV_KEY root@167.99.241.135 "/var/lib/isso/env/bin/isso --version"