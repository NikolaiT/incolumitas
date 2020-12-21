Title: How to dynamically change http/s proxy servers in puppeteer?
Date: 2020-02-14 14:06
Category: Scraping
Tags: Puppeteer, Proxies, Issues, Proxy-Authentication
Slug: dynamically-changing-puppeteer-http-proxy
Author: Nikolai Tschacher

**Find the [updated blog post here.](https://incolumitas.com/2020/12/20/dynamically-changing-puppeteer-proxies/)**

Chrome/Puppeteer has a couple of annoying issues when trying to use **http/s proxies** and **socks proxies** with the chrome browser controlled by puppeteer. The most pressing issues are the following:

1. **Dynamically changing proxy servers: ** Once the chrome browser is started, it is not possible to change the proxy configuration any longer. A restart is required to switch proxy configuration.
2. **user/pass proxy authentication:** The chrome browser does not support username/password proxy authentication **for socks proxies**. Puppeteer supports the http [proxy authentication]() via the `page.authenticate()` function, but it does not have an equivalent for socks proxies.
3. **Per page proxies: ** Per page proxies are not supported with the chrome browser. The global proxy configuration applies to all pages and windows of a launched chrome process. It seems like the new module [](https://github.com/Cuadrix/puppeteer-page-proxy) tries to solve this issue.

For my purposes, I don't really care about problem 3). I don't need per page proxies anyway, since the crawling software I write runs with one browser tab at the time. However, issue 1) is a mandatory requirement for me and thus needs to be solved.

The reason is, I don't want to restart the browser each time I need to change the proxy. Some sites require a different proxy for each url. This would enforce a restart for each url, which prolongs the crawling process significantly.

It seems that the company Apify encountered problems with proxy authentication and thus released a intermediary nodejs proxy server that forwards proxy connections to the real proxy server. They created it back when `page.authenticate()` was not a part of puppeteer yet and made the following scenario possible:

```
[Chrome with command line arg proxy-server=localhost:8000] 
 <===> 
[Forwarding proxy server running on localhost:8000]
 <===> 
[Arbitrary proxy server requiring username:password auth]
```

The software is called [proxy-chain](https://github.com/apifytech/proxy-chain) and there exists a informative [blog article that explains how the software works](https://blog.apify.com/how-to-make-headless-chrome-and-puppeteer-use-a-proxy-server-with-authentication-249a21a79212).

However, the current version of `proxy-chain` only solves the issue with proxy authentication. What we really want is to **dynamically change the browser proxy within our puppeteer code**.

In the remainder of the article our http/s proxy server will have the proxy string **http://proxyuser:proxypassword@100.100.100.100:3128**


## Overview

This is the state of the art of chrome browser proxy support with puppeteer. The contribution of this blog article is to enable to dynamically change http/s proxies via a [modified proxy-chain module](https://github.com/NikolaiT/proxy-chain/commit/1963f76774c958ec3c63354dda60c965c9f65501#diff-6ea992016c2394768b145c7f24a5b2d9).

| Proxy Scheme  | Chrome Browser support  | Authentication  | Dynamic Proxy Change |
| ------------- | -------------           | ----------      | ---------- |
| http/s        | yes                     | with pptr `page.authenticate()`, not via command line | with [modified proxy-chain](https://github.com/NikolaiT/proxy-chain/commit/1963f76774c958ec3c63354dda60c965c9f65501#diff-6ea992016c2394768b145c7f24a5b2d9)|
| socks4        | yes                     |   not a part of socks4             | no, `proxy-chain` only supports http/s proxies |
| socks5        | no                      |   not possible          | no |

## Dynamically changing proxy configuration from puppeteer code
 
Even though it is possible to dynamically change the upstream proxy server in `proxy-chain` by setting an extra http header such as **x-no-forward-upstream-proxy**, this header would also be copied and sent to the upstream proxy. This is not what we want, since it would leak username/passwords of the proxystring to the website we want to crawl. This would be an horrendous idea.

Therefore, we need the intermediate proxy server to have the capability to strip all headers that start with a magic string such as **x-no-forward**.

This is our puppeteer client:

```javascript
const puppeteer = require('puppeteer');

(async() => {
  const proxyUrl = 'http://localhost:8000';
  const browser = await puppeteer.launch({
    args: [`--proxy-server=${proxyUrl}`],
  });

  const page = await browser.newPage();

  // signal to the intermediate proxy server what upstream proxy we want to use
  await page.setExtraHTTPHeaders({
    'x-no-forward-upstream-proxy': 'http://proxyuser:proxypassword@100.100.100.100:3128'
  });

  await page.goto('http://ipinfo.io/json');
  console.log(await page.content());
  await browser.close();
})();
```

And this is our intermediate proxy server:

```javascript
// proxy_server.js
const ProxyChain = require('proxy-chain');

const server = new ProxyChain.Server({
  // Port where the server will listen. By default 8000.
  port: 8000,
  // Enables verbose logging
  verbose: true,
  prepareRequestFunction: ({ request, username, password, hostname, port, isHttp, connectionId }) => {
    let upstream_proxy = request.headers['x-no-forward-upstream-proxy'];
    if (!upstream_proxy) {
      throw Error('please set header `x-no-forward-upstream-proxy`');
    }
    return {
      upstreamProxyUrl: upstream_proxy,
    };
  },
});

server.listen(() => {
  console.log(`Proxy server is listening on port ${server.port}`);
});

// Emitted when HTTP connection is closed
server.on('connectionClosed', ({ connectionId, stats }) => {
  console.log(`Connection ${connectionId} closed`);
  console.dir(stats);
});

// Emitted when HTTP request fails
server.on('requestFailed', ({ request, error }) => {
  console.log(`Request ${request.url} failed`);
  console.error(error);
});
```

In order to set the upstream proxy via the HTTP header **x-no-forward-upstream-proxy**, a [code modification is required](https://github.com/NikolaiT/proxy-chain/commit/1963f76774c958ec3c63354dda60c965c9f65501#diff-6ea992016c2394768b145c7f24a5b2d9) in the source code of the `proxy-chain` module. 

With this small modification, we can switch the proxy server as often as we wish. 

First install the modified module directly from github with the command:

```bash
npm install NikolaiT/proxy-chain
```

which installs the `proxy-chain` fork. Then the server code listed above is launched with the command `node proxy_server.js`.

An example usage could be the following client program. It can be executed with `node proxy_client.js` after the server was started.

```javascript
// proxy_client.js
const puppeteer = require('puppeteer');

(async() => {
  const browser = await puppeteer.launch({
    args: [`--proxy-server=http://localhost:8000`],
  });

  const page = await browser.newPage();

  // signal to the intermediate proxy server what upstream proxy we want to use
  await page.setExtraHTTPHeaders({
    'x-no-forward-upstream-proxy': 'http://proxyuser:proxypass@100.100.100.100:3128'
  });

  await page.goto('http://ipinfo.io/json');
  console.log(await page.content());

  // SWITCH THE PROXY SERVER
  await page.setExtraHTTPHeaders({
    'x-no-forward-upstream-proxy': 'http://proxyuser:proxypass@200.200.200.200:3128'
  });

  await page.goto('http://ipinfo.io/json');
  console.log(await page.content());

  await browser.close();
})();
```

It should output the IP address metadata of two different proxy connections. If that is the case, the experiment **was a success**.

## Solving the problem of missing proxy authentication in chrome

For completeness sake, it is also shown how to authenticate to a proxy with puppeteer. `proxy-chain` is **not needed anymore** to solve the chrome/puppeteer authentication problem. We can simply use `page.authenticate()` to accomplish that.

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
    password: 'proxypassword'
  });

  await page.goto('https://ipinfo.io/json');

  console.log(await page.content());

  await browser.close();
})();
```

## What about socks4/socks5 proxies?

Browser version:

```bash
$ chromium-browser --version
Using PPAPI flash.
Chromium 78.0.3904.108 Built on Ubuntu , running on Ubuntu 18.04
```

Unfortunately, the chrome browser only supports socks4 proxies out of the box. Passing a proxy string such as 
`socks5://proxyuser:proxypass@100.100.100.100:53425` to chrome will not work. The following command will not create a connection

```bash
chromium-browser --proxy-server='socks5://proxyuser:proxypass@100.100.100.100:53425' tps://ipinfo.io/json
```

and fail with **ERR_NO_SUPPORTED_PROXIES**. However, the curl command

```bash
curl --proxy socks5://proxyuser:proxypass@100.100.100.100:53425 http://ipinfo.io/json
```

works flawlessly.

When we use sock4 with the chrome browser, it works as expected:

```bash
chromium-browser --proxy-server='socks://100.100.100.100:53425' https://ipinfo.io/json
```

## Limitations of http/s proxies

There are a couple of security issues with http/s proxy servers. It is also possible to detect that a browser reroutes their traffic through a proxy. For example, the module `apifytech/proxy-chain` deletes the following headers:

```js
const HOP_BY_HOP_HEADERS = [
    'Connection',
    'Keep-Alive',
    'Proxy-Authenticate',
    'Proxy-Authorization',
    'TE',
    'Trailers',
    'Transfer-Encoding',
    'Upgrade',
];
```

Since the `Upgrade` and `Connection` headers are used in the establishment of websocket connections, the chrome browser won't be able to use websites that require websockets. This can easily be confirmed by testing with this script:

```js
const puppeteer = require('puppeteer');
const proxyChain = require('proxy-chain');

(async() => {
  const oldProxyUrl = 'http://proxyuser:proxypassword@100.100.100.100:3128';
  const newProxyUrl = await proxyChain.anonymizeProxy(oldProxyUrl);

  const browser = await puppeteer.launch({
    headless: false,
    args: [`--proxy-server=${newProxyUrl}`],
  });

  // Do your magic here...
  const page = await browser.newPage();
  await page.goto('https://www.websocket.org/echo.html');
  
  // oh wait a minute
  await page.waitFor(60000);
  
  await browser.close();
  // Clean up
  await proxyChain.closeAnonymizedProxy(newProxyUrl, true);
})();
```


