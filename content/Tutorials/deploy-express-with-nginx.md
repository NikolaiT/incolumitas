Title: Deploy an Express App with Nginx and forward real IP Address
Date: 2020-12-31 14:48
Category: Tutorials
Tags: express, nginx, reverse proxy, IP forward
Slug: express-with-nginx-and-forward-real-ip-address
Author: Nikolai Tschacher
Summary: In this tutorial it is demonstrated how an Express App is deployed with Nginx as reverse proxy. Static files are served with Nginx and the real IP address is forwarded to the Express app.

[Express](https://expressjs.com/) is probably one of the widely used web frameworks out there. It is incredibly easy to use and extremely powerful. [Nginx](http://nginx.org/) is one of the most popular web servers and is often used as a reverse proxy. Nginx is super fast and powerful, making it one of the go-to choices when deploying web servers.

In this blog article it is shown how an Express application can be deployed with Nginx as a reverse proxy. The following common problems will be solved:

1. How to forward the remote IP address of a client to the web app from Nginx
2. How to serve static files with Nginx
3. Bonus: Deploy SSL certificates with [Let's Encrypt](https://letsencrypt.org/)

You can follow each step along in this tutorial.

Important: It is assumed that every step in this tutorial is made on a VPS server that is publicly accessable from the Internet. 
To be specific, an Ubuntu 18.04 Linux server is used. The instructions should be identical with Ubuntu 20.04.

### Setting up the project

You need to have [Node.js and npm installed](https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-18-04).

Create the project directory and change into it.

```text
mkdir express-with-nginx

cd express-with-nginx/
```

Install express:

```text
npm install express
```

And then save the following server code as `server.js`:

```JavaScript
const express = require('express');
const app = express();
const port = 3000;

function getIp(req) {
  let ip = req.connection.remoteAddress;
  ip = ip.replace('::ffff:', '');

  if (ip == '127.0.0.1') {
    ip = req.headers['x-real-ip'];
  }

  return ip;
}

app.get('/', (req, res) => {
  res.send('Hello World from: ' + getIp(req));
})

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
})
```

Now you have a functional express server.

Start the server with the command:

```text
node server.js
```

### Configure Nginx

The next step is to setup Nginx as a reverse proxy.

Create the Nginx configuration file in `/etc/nginx/sites-available/express_nginx.conf`:

```text
# /etc/nginx/sites-available/express_nginx.conf
server {
  listen      80;
  server_name test.incolumitas.com;

  location / {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Host $host;
    proxy_set_header  X-Real-IP $remote_addr;
    proxy_cache_bypass $http_upgrade;
  }
}
```

Please change the domain name **test.incolumitas.com** to whatever domain you are using.

Note: The directive `proxy_pass` tells Nginx to forward all traffic arriving on `test.incolumitas.com` to the local server listening on `http://localhost:3000`.

The directive `proxy_set_header  X-Real-IP $remote_addr;` forwards the real IP address of the user in a header `X-Real-IP` to our Express application.

Enable the Nginx configuration file with the command:

```bash
ln -s /etc/nginx/sites-available/express_nginx.conf /etc/nginx/sites-enabled/
```

And then restart the server:

```bash
service nginx restart
```

Now visit the URL [http://test.incolumitas.com](http://test.incolumitas.com) with your browser. You should see something like this in your browser: 

```text
Hello World from: 145.54.78.22
```

### Deploy an SSL certificate with Let's Encrypt

In a real production environment, you should of course deploy the webserver with SSL support. This tutorial shows how to do so with [Ubuntu and Nginx and Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04).

Assuming that `certbot` is correctly installed, you can issue the following command to use SSL:

```bash
certbot --nginx -d test.incolumitas.com
```

You will see the following output. Choose the option **2: Redirect** when prompted.

```text
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator nginx, Installer nginx
Obtaining a new certificate
Performing the following challenges:
http-01 challenge for test.incolumitas.com
Waiting for verification...
Cleaning up challenges
Deploying Certificate to VirtualHost /etc/nginx/sites-enabled/express_nginx.conf

Please choose whether or not to redirect HTTP traffic to HTTPS, removing HTTP access.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
1: No redirect - Make no further changes to the webserver configuration.
2: Redirect - Make all requests redirect to secure HTTPS access. Choose this for
new sites, or if you're confident your site works on HTTPS. You can undo this
change by editing your web server's configuration.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Select the appropriate number [1-2] then [enter] (press 'c' to cancel): 2
Redirecting all traffic on port 80 to ssl in /etc/nginx/sites-enabled/express_nginx.conf

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Congratulations! You have successfully enabled https://test.incolumitas.com

You should test your configuration at:
https://www.ssllabs.com/ssltest/analyze.html?d=test.incolumitas.com
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```

Then restart the nginx server with

```bash
service nginx restart
```

You can now access your Express application with the URL [https://test.incolumitas.com](http://test.incolumitas.com).

This will modify your Nginx configuration file to use an SSL certificate. After the command, it will look something like this:

```text
server {
  server_name test.incolumitas.com;

  location / {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Host $host;
    proxy_set_header  X-Real-IP $remote_addr;
    proxy_cache_bypass $http_upgrade;
  }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/test.incolumitas.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/test.incolumitas.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}
server {
    if ($host = test.incolumitas.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


  listen      80;
  server_name test.incolumitas.com;
  return 404; # managed by Certbot
}
```

