Title: Using http/s and socks4/5 proxies with puppeteer and chrome with squid and danted
Date: 2020-02-12 21:42
Modified: 2020-02-13 13:32
Category: Scraping
Tags: Puppeteer, Proxy, Danted, Squid, socks4, socks5
Slug: https-and-socks-proxies-with-puppeteer-and-squid-and-danted
Author: Nikolai Tschacher
Summary: This blogs post demonstrates how puppeteer and the chrome browser can be used with http/s and socks4/5 proxies. For that reason, a proxy server is setup on Ubuntu 18.04 with **squid3** and **dante**.

# For what reason are proxies used when crawling/scraping with puppeteer?

When we are crawling different websites, it's usually a good idea to change the browsing fingerprint by re-routing the TCP traffic through multiple distinct hops.
 
By doing so, the crawled website cannot rate limit the clients requests by IP address blacklisting. Put differently, by switching proxy servers, the detection rate can be reduced by a wide margin. 
 
But changing your IP address is **usually not enough**. It's also smart to alter your browser fingerprint in other ways, such as changing the user agent, cleaning session data such as cookies and cached objects and modifying accept-language headers or changing the browser viewpoint.

Scraping and crawling in the year 2020 is usually done with a fully functional browser in order to prevent blocking attempts that build on the requirement to be able to execute javascript. Puppeteer in combination with headless chromium is often used for that matter.

In this blog post, we will learn how Puppeteer/Chromium can be used with 

1. **Http/Https** proxy support with and without `username:password` authentication. The proxy server is build with [**squid3**](http://www.squid-cache.org/).
2. **Socks** proxy support with and without `username:password` authentication. The proxy server is setup with [**dante**](https://www.inet.no/dante/).

For this reason, we will also show instructions how to create your own http/s proxy server and socks proxy server on Ubuntu 18.04.

# Proxy Server Setup

All proxy server software is going to be installed on a Ubuntu 18.04 server. The only requirement is that the server should have a static, public IP address.

1. **Client IP address** (the computer that uses the proxy) = **1.1.1.1**
2. **Proxy Server IP address** (the server that *is* the proxy) = **100.100.100.100**

## Creating a http/s proxy server with squid3 on Ubuntu 18.04

Squid is a powerful and mature http/s proxy server and caching software. For our purposes, we are solely interested in the proxying functionality. The configuration is based on a [stackoverflow answer](https://stackoverflow.com/questions/48239975/how-do-i-setup-an-elite-http-squid-proxy-with-password-protection-on-ubuntu) that explains in depth how to setup squid to work as an anonymous http/s proxy.

First of all, we need to install the required software packages for `squid3` to work:

```bash
sudo apt-get update
sudo apt-get install squid3
sudo apt-get install apache2-utils
```

Then we create the password file that `squid3` is going to use for authentication. This command requires you to enter a password of your choice. We will use the credentials `proxyuser:proxypass`.

```bash
sudo htpasswd -c /etc/squid/.squid_users proxyuser
```

You can verify that the password works by issuing the following command and enter `proxyuser proxypass` and pressing enter. You should see `OK` as output.

```bash
/usr/lib/squid3/basic_ncsa_auth /etc/squid/.squid_users
```

Then we configure the configuration file `/etc/squid/squid.conf` as follows. Please replace the dummy IP address **100.100.100.100** with the ip address of your own server.

```bash
# http_port: specifies the proxy listen port. This is required
http_port 3128
# dns_v4_first on: effectively turns off IPv6 DNS. Without this your proxy may run very slowly.
dns_v4_first on
# cache deny all: stops the proxy caching pages
cache deny all
# forwarded_for delete: remove the forwarded_for http header which would expose your source to the destination
forwarded_for delete
# tcp_outgoing_address: Set this to the address of your server. You can find the address with the command "ip a"
tcp_outgoing_address 100.100.100.100
# via off: removes more headers which would expose your source
via off
# auth_param: defines your the location of your basic_ncsa_auth and password file you created. Note you may need to check the location of basic_ncsa_auth.
auth_param basic program /usr/lib/squid3/basic_ncsa_auth /etc/squid/.squid_users
auth_param basic realm proxy
# acl authenticated: creates an access control list for user authenticated by the password store
acl authenticated proxy_auth REQUIRED
# http_access allow authenticated: allow user to access the proxy if they have been authenticated by password
http_access allow authenticated
# http_access deny all: if you have not been authenticated by password, you're not coming in
http_access deny all
```

How we need to open the port on the standard firewall of Ubuntu with the command:

```bash
ufw allow 3128
```

After having saved the file, restart the `squid3` service with `service squid restart`.

Test that everything works fine with curl:

```bash
curl --proxy http://proxyuser:proxypass@100.100.100.100:3128 http://ipinfo.io/json
```

The above command should show you the IP details of the proxy server.


## Configuring a socks proxy server with danted

In order to create a socks4/socks5 server, we will use [dante](https://www.inet.no/dante/). **dante** is the name of the software, `danted` stands for *dante daemon*.

First we show how to configure `danted` to create a socks4 proxy server, then how to setup socks5. The difference between socks4 and socks5 is essentially that socks5 supports `username:password` authentication.

In order to begin, you need to install a recent `danted` server. This has been explained countless times: [Here are decent installation instructions](https://gist.github.com/gpchelkin/c7d24a21639d1f120fb082d1801a5fe4).

After you installed `danted`, add this configuration to `/etc/danted.conf`:

```bash
# /etc/danted.conf

logoutput: syslog
user.privileged: root
user.unprivileged: nobody

# The listening network interface or address.
internal: 0.0.0.0 port=53425

# The proxying network interface or address.
external: eth0

# socks-rules determine what is proxied through the external interface.
# The default of "none" permits anonymous access.
socksmethod: username

# client-rules determine who can connect to the internal interface.
# The default of "none" permits anonymous access.
clientmethod: none

client pass {
        from: 1.1.1.1/16 to: 0.0.0.0/0
        log: connect disconnect error
}


socks pass {
        from: 0.0.0.0/0 to: 0.0.0.0/0
        log: connect disconnect error
}
```

In my case, I needed to change the external network interface to **ens3**. You can look it up with the `ifconfig` command.

`danted` uses the credentials username and password of your linux users. Therefore, we create a user with:

```bash
# add user
useradd -r -s /bin/false proxyuser
# set password
passwd proxyuser
```

Now open the port in the firewall with:

```bash
ufw allow 53425
```

Finally, we restart `danted` with the command `service danted restart`.

Confirm that the socks server is working by testing it with curl:

```bash
curl --proxy socks5://proxyuser:proxypass@100.100.100.100:53425 http://ipinfo.io/json
```

If we **do not want to use socks authentication**, we edit `/etc/danted.conf` to alter the line from `socksmethod: username` to `socksmethod: none` and issue the command `service danted restart`.

Then we can test the socks server without auth (which is **socks4**) with:

```bash
curl --proxy socks4://100.100.100.100:53425 http://ipinfo.io/json
```

# Puppeteer with proxies

Now we can see how to use the http/s and socks proxy server that we configured in the previous steps with a fully functional browser controlled via puppeteer.

## Puppeteer with http/s proxy

You can test puppeteer with a http proxy by launching the following node script. The output should show IP address details of the proxy.

```javascript
const puppeteer = require('puppeteer');

(async() => {
  const proxyUrl = 'http://100.100.100.100:3128';

  const browser = await puppeteer.launch({
    args: [`--proxy-server=${proxyUrl}`],
  });

  const page = await browser.newPage();

  await page.authenticate({
    username: 'proxyuser',
    password: 'proxypass'
  });

  await page.goto('https://ipinfo.io/json');
  await page.screenshot({ path: 'ipinfo.png', fullPage: true });
  console.log(await page.content());
  await browser.close();
})();
```

## Puppeteer with socks4 proxy

You can test puppeteer in combination with a socks proxy server by launching the following node program. The output should show IP address details of the proxy.

```javascript
const puppeteer = require('puppeteer');

(async() => {
  const proxyUrl = 'socks://100.100.100.100:53425';

  const browser = await puppeteer.launch({
    args: [`--proxy-server=${proxyUrl}`],
  });

  const page = await browser.newPage();
  await page.goto('https://ipinfo.io/json');
  await page.screenshot({ path: 'ipinfo.png', fullPage: true });
  console.log(await page.content());
  await browser.close();
})();
```

# Tear down the proxy servers

To stop the proxy servers, execute the following commands on your servers:

```bash
systemctl stop danted
systemctl stop squid
```

# Known Limitations

Unfortunately, **it is not possible to use puppeteer/chromium with a socks5 proxy**. The chrome browser does not support socks with authentication.

How to address the problem of [switching proxies on the fly](https://incolumitas.com/2020/02/14/dynamically-changing-puppeteer-http-proxy/) without restarting puppeteer/chromium will be handled in the next blog post.