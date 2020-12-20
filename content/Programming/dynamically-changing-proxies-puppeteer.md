Title: Dynamically changing proxies with puppeteer
Date: 2020-12-20 00:22
Category: Security
Tags: puppeteer, proxies, dynamic, api
Slug: dynamically-changing-puppeteer-proxies
Author: Nikolai Tschacher
Summary: The chrome browser controlled via puppeteer does not support switching proxies without restarting the browser. In this tutorial, I demonstrate how to implement this functionality with the help of a third party node module named `proxy-chain`.

The chrome browser does not support fain-grained proxy configuration. Therefore, the following use cases are not possible when using puppeteer and the chrome browser:

+ Use of a dedicated proxy for each tab/page in a chrome browser
+ Switching proxies without restarting the entire browser

This is a bit annoying, because restarting the entire browser is an expensive operation in terms of computational resources.

One solution is to use a intermediate proxy solution that routes traffic to the upstream proxy. This is exactly what I am going to implement in this blog post.

This is the design of the intended solution:

```
[local chrome instance] <====> [local intermediate proxy service] <====> [upstream proxy] <====> [target website]
```

In this tutorial, I will build a very simple Api that allows the Api caller to make requests with the chrome browser. The caller can specify the following parameters:

```
{
  url: string,
  proxy: string
}
```

As a response, the rendered HTML will be returned. If a valid proxy is specified, the url will be requested through the proxy. If no proxy is passed, no proxy will be used. The browser will never be restarted in between requests. Browser cookies are cleared between calls to the Api.

### Implementation

The up-to-date source code can be found in the respective [Github repo](https://github.com/NikolaiT/dynamically-changing-puppeteer-proxies).

Without further ado, the full implementation of the proof of concept can be found in the code snippet below. 
In order to setup the program, you need to issue the following commands:

```bash
npm i puppeteer-core express body-parser valid-url proxy-chain
```

And then save the code listed below as `dynamic-proxy-api.js` and execute it with:

```bash
node dynamic-proxy-api.js
```

And then use the Api with a sample proxy such as `http://11.22.33.44:1234/`:

```bash
curl -i "http://localhost:3333/api?url=http://httpbin.org/get&proxy=http://11.22.33.44:1234/"
```

The first Api call will start the browser initially. The next Api call with a new proxy `http://22.22.22.22:2222/` will use
the same browser session but with a new proxy.

```bash
curl -i "http://localhost:3333/api?url=http://httpbin.org/get&proxy=http://22.22.22.22:2222/"
```

```Javascript
const express = require('express');
const bodyParser = require('body-parser');
const validUrl = require('valid-url');
const puppeteer = require('puppeteer-core');
const ProxyChain = require('proxy-chain');

const CHROME_BINARY_PATH = '/usr/bin/chromium-browser';
const app = express();
const port = 3333;
const proxyServerPort = 8947;
let browser = null;

app.use(express.json());
app.use(bodyParser.json({ limit: '2mb' }));

function log(msg) {
  console.log(`[${(new Date()).getTime()}] - ${msg}`);
}

function validateProxy(proxy) {
  let match = false;
  let prefixes = ['http://', 'https://', 'socks://', 'socks5://', 'socks4://'];
  for (let prefix of prefixes) {
    if (proxy.startsWith(prefix)) {
      match = true;
    }
  }
  if (match === false) {
    return false;
  }
  return validUrl.isWebUri(proxy);
}

async function getBrowser() {
  if (browser === null) {
    browser = await puppeteer.launch({
      executablePath: CHROME_BINARY_PATH,
      headless: false,
      args: [`--proxy-server=http://localhost:` + proxyServerPort],
    });
    log('Browser started');
  }
}

async function startProxyServer(proxy) {
  return new Promise(function(resolve, reject) {
    const server = new ProxyChain.Server({
      port: proxyServerPort,
      verbose: false,
      prepareRequestFunction: function (params) {
        var {request, username, password, hostname, port, isHttp, connectionId} = params;
        return {
          requestAuthentication: false,
          // http://username:password@proxy.example.com:3128
          upstreamProxyUrl: proxy,
        };
      },
    });

    // Emitted when HTTP connection is closed
    server.on('connectionClosed', (params) => {
      var {connectionId, stats} = params;
      log(`Connection ${connectionId} closed`);
    });

    // Emitted when HTTP request fails
    server.on('requestFailed', (params) => {
      var {request, error} = params;
      log(`Request ${request.url} failed with error ${error}`);
    });

    server.listen(() => {
      log(`ProxyServer listening on port ${server.port}`);
      resolve(server);
    });
  });
}

async function clearCookies(page) {
  try {
    log('Deleting cookies with Network.clearBrowserCookies');
    const client = await page.target().createCDPSession();
    await client.send('Network.clearBrowserCookies');
  } catch (err) {
    log(`Could not delete cookies: ${err.toString()}`);
  }
}

app.get('/api', async (req, res) => {
  if (req.query.proxy) {
    if (!validateProxy(req.query.proxy)) {
      return res.status(403).send('Invalid proxy format');
    } else {
      log(`Using proxy: ${req.query.proxy}`);
    }
  }

  if (req.query.url) {
    if (!validUrl.isWebUri(req.query.url)) {
      return res.status(403).send(`url is not valid`);
    }
  } else {
    return res.status(403).send(`url is required`);
  }

  let proxyServer = await startProxyServer(req.query.proxy);

  await getBrowser();
  let page = await browser.newPage();
  await page.goto(req.query.url, { waitUntil: "domcontentloaded" });
  let content = await page.content();
  // clear cookies after we are done
  await clearCookies(page);

  proxyServer.close();
  await page.close();

  res.set('Content-Type', 'text/html');
  return res.send(Buffer.from(content));
});

app.listen(port, () => {
  log(`Dynamic proxy puppeteer Api listening on port ${port}`);
});
```