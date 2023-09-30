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
