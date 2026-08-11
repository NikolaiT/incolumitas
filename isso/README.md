# Install and configure isso comment system

## Download old isso database

```bash
scp -i ~/.ssh/root_new_server root@167.99.241.135:/var/lib/isso/comments.db .
```

## Upload new database

```bash
scp -i /Users/nikolaitschacher/.ssh/pd_server comments.db root@162.55.51.87:/var/lib/isso/
```

## Read this

<https://isso-comments.de/docs/guides/quickstart/>
<https://isso-comments.de/docs/reference/installation/>
<https://isso-comments.de/docs/reference/installation/#init-scripts>

```bash
apt install python3-pip
mkdir -p /var/lib/isso/
pip install isso
```

Create config `/var/lib/isso/isso.cfg`

```bash
isso -c /var/lib/isso/isso.cfg run
```

### Current production config (August 2026)

Comment moderation is enabled: new comments are held back until approved.
Every new comment triggers a notification email to admin@incolumitas.com
with one-click approve/delete links. Pending comments older than 30 days
are purged automatically.

Comments can also be moderated in the admin panel:
<https://isso.incolumitas.com/admin> (password is in the `[admin]` section
of `/var/lib/isso/isso.cfg` on the server).

```ini
[general]
name = isso
dbpath = /var/lib/isso/comments.db
host = https://incolumitas.com
max-age = 15m
log-file = /var/lib/isso/isso.log
gravatar = true
notify = smtp

[moderation]
enabled = true
purge-after = 30d

[admin]
enabled = true
password = <see server config>

[server]
listen = http://localhost:7136
reload = off
profile = off
public-endpoint = https://isso.incolumitas.com

[guard]
enabled = true
ratelimit = 2
direct-reply = 3
reply-to-self = true
require-author = false
require-email = false

[smtp]
username = info@ipapi.is
password = <gmail app password, see server config>
host = smtp.gmail.com
port = 587
security = starttls
to = admin@incolumitas.com
from = info@ipapi.is
timeout = 10
```

To turn moderation off again, set `enabled = false` in the `[moderation]`
section and `systemctl restart isso`.

```bash
systemctl status isso
```

I had to copy all js files from

```bash
pip install isso
```

to the installation in

```bash
pip install git+https://github.com/posativ/isso.git
```

```bash
cp -r  env/lib/python3.6/site-packages/isso/js/ .
pip install git+https://github.com/posativ/isso.git
cp -r js/ env/lib/python3.6/site-packages/isso/
```

### Create a systemd service

```bash
vim /etc/systemd/system/isso.service
```

```bash
[Unit]
Description=isso

[Service]
ExecStart=/usr/local/bin/isso -c /var/lib/isso/isso.cfg run
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
```

### Import disqus comments

```bash
cd /opt/isso/
source /opt/isso/bin/activate
isso -c /etc/isso.cfg import incolumitas-disqus.xml
```

### TODO

run isso with gunicorn.

Reason: Way better for production and also faster.

Howto: <https://posativ.org/isso/docs/extras/deployment/>
