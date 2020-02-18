#!/bin/bash

set -e
source /opt/isso/bin/activate
export LANG=C.UTF-8
export ISSO_SETTINGS=/etc/isso.cfg
exec gunicorn -n gunicorn-isso -b 127.0.0.1:1927 --preload -w 3 --log-file /var/log/isso/isso.log isso.dispatch 2>>/var/log/isso/isso.log