## Configure isso

### Read this:

https://oktomus.com/posts/2020/add-comments-to-a-static-blog-with-isso/
https://posativ.org/isso/docs/configuration/client/

```bash
mkdir -p /var/lib/isso/

source /var/lib/isso/env/bin/activate

pip install git+https://github.com/posativ/isso.git

isso -c /etc/isso.cfg run
```

```bash
systemctl status isso
```

I had to copy all js files from 

```
pip install isso
```

to the installation in 

```
pip install git+https://github.com/posativ/isso.git
```

```
cp -r  env/lib/python3.6/site-packages/isso/js/ .
pip install git+https://github.com/posativ/isso.git
cp -r js/ env/lib/python3.6/site-packages/isso/
```

### Import disqus comments

```
cd /opt/isso/
source /opt/isso/bin/activate
isso -c /etc/isso.cfg import incolumitas-disqus.xml
```