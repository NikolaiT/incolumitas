## Configure isso

### Read this:

https://therandombits.com/2018/12/how-to-add-isso-comments-to-your-site/
https://blog.phusion.nl/2018/08/16/isso-simple-self-hosted-commenting-system/

```bash
mkdir -p /var/lib/isso/

source /opt/isso/bin/activate

pip install git+https://github.com/posativ/isso.git

isso -c /etc/isso.cfg run
```

```bash

systemctl status isso
```