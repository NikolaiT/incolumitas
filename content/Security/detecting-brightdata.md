Title: Detecting Brightdata's (formerly Luminati Networks) Data Collector
Status: published
Date: 2021-06-03 21:21
Category: Security
Tags: bot detection, anti scraping
Slug: detecting-brightdata-data-collector
Author: Nikolai Tschacher
Summary: In this blog article I demonstrate several ways how to detect Brigthdata's scraping bot named data collector.

## Introduction

[Brightdata](https://brightdata.com/) (formerly Luminati Networks) is probably the largest Proxy provider on the planet.

Their main product is a large proxy network. They offer datacenter, residential and mobile proxies. They can do so, because their sister company [hola.org](https://hola.org/) provides as browser extension that allows to share your network bandwith with other users of [hola.org](https://hola.org/). It's a peer-to-peer network and allows their users to change their IP address. 

Put differently: [hola.org](https://hola.org/) installs a proxy server on each person that installs the browser extension and [Brightdata](https://brightdata.com/) resells this bandwith/proxies as residential and mobile proxies to large business customers.

But most recently, they also strongly push into the data collection niche by allowing their clients a full fledged browser with JavaScript capabilities that is hard to distinguish from a real human controlled browser.

<figure>
    <img src="{static}/images/brightdata.png" alt="Brightdata data collector" />
    <figcaption>Brightdata data collector - Or: Best solution for sneaker bots?</figcaption>
</figure>

As their own image above suggests, the data collector can be used to scrape Google, scrape prices from E-Commerce websites, scrape the most recent published realtor ads on websites. If you have an advanced undetectable bot, you have an enormous advantage in the Internet. 

In this blog post, my goal is to find some reliable ways to detect the [Brightdata data collector](https://brightdata.com/products/data-collector).

## Approach

We will use the following bot detection sites and visit them with [Brightdata's data collector](https://brightdata.com/products/data-collector):

1. [creepjs](https://abrahamjuliot.github.io/creepjs/)
2. [pixelscan.net](https://pixelscan.net/)
3. [whatleaks.com](https://whatleaks.com/)
4. [f.vision](http://f.vision/)

For each detected artifact, I will try to re-implement the test that triggered the detection. 

Only when I am capable of re-implementing the test, I truly understand why a site claims to have detected the visitor as bot.

For each bot detection site listed above, I will request the site five times.

## Testing with whatleaks.com

I will use the following [Brightdata data collector ](https://brightdata.com/products/data-collector) script:

```JavaScript
navigate('https://whatleaks.com/');

// just let the data collector time out because we wait for 
// an #id that never appears
wait_for_text('#doesNOtExit', 'blabla');

collect({
    url: location.href,
});
```

Here [is a link]() to the [whatleaks.com](https://whatleaks.com/) results.

#### Result: IP found in Blacklist

[whatleaks.com](https://whatleaks.com/) claims: 

```
Result:
IP found in blacklists (1)
Name
Description
dnsbl.sorbs.net:
Unsolicited bulk/commercial email senders
```

When looking up the IP address `184.91.1.148` on [dnsbl.info](https://www.dnsbl.info/dnsbl-database-check.php) I can confirm the finding.

<figure>
    <img src="{static}/images/dnsbl.png" alt="Brightdata data collector" />
    <figcaption>Brightdata  IP address is listed on [dnsbl.info](https://www.dnsbl.info/dnsbl-database-check.php</figcaption>
</figure>

I have to idea how accurate [dnsbl.info](https://www.dnsbl.info/dnsbl-database-check.php) is, but as a quick check, I inserted my own public IP address and there also one spam report on this IP (Detected on `b.barracudacentral.org`). So I would not consider those publicly accessible spam lookup databases as overly trustworthy. 

With the other IP addresses of the other four samples I got a similar result.


#### Result: Ping - Proxies are detected in your connection.

When looking up the test description on [whatleaks.com](https://whatleaks.com/):

> We compare ping from your computer to our server and ping from our server to the host of your external IP. If the difference is too much then there is probably a tunnel and you are using a proxy.

I re-implemented this ping proxy detection test in [my last blog article](http://localhost:8000/2021/04/24/detecting-proxies/) where I also quickly programmed my own test.

Link to my own ping-based proxy detection test: [bot.incolumitas.com/crossping.html](https://bot.incolumitas.com/crossping.html)

For example, those are the results of the crossping test for [Brightdata's data collector](https://brightdata.com/products/data-collector):

Test 1:

```json
{
  "browserToServer-0": 914.4649999216199,
  "browserToServer-1": 1014.5399998873472,
  "browserToServer-2": 1015.4400002211332,
  "browserToServer-3": 1101.740000769496,
  "browserToServer-4": 1102.8800001367927,
  "serverToExternalIP-0": "72.180.224.177 - OK 134.796 ms",
  "serverToExternalIP-1": "72.180.224.177 - OK 131.744 ms",
  "serverToExternalIP-2": "72.180.224.177 - OK 133.993 ms",
  "serverToExternalIP-3": "72.180.224.177 - OK 139.276 ms",
  "serverToExternalIP-4": "72.180.224.177 - OK 137.525 ms"
}
```

Test 2:

```json
{
  "browserToServer-0": 717.8099993616343,
  "browserToServer-3": 959.8300000652671,
  "browserToServer-4": 962.6200003549457,
  "browserToServer-1": 1128.740000538528,
  "browserToServer-2": 1131.4850002527237,
  "serverToExternalIP-0": "45.130.83.183 - OK 93.502 ms",
  "serverToExternalIP-1": "45.130.83.183 - OK 92.907 ms",
  "serverToExternalIP-2": "45.130.83.183 - OK 92.825 ms",
  "serverToExternalIP-3": "45.130.83.183 - OK 92.782 ms",
  "serverToExternalIP-4": "45.130.83.183 - OK 92.935 ms"
}
```

And this is me without any proxy visiting my detection site:

```json
{
  "browserToServer-0": 107,
  "browserToServer-1": 114,
  "browserToServer-4": 116.59999999962747,
  "browserToServer-2": 119.80000000074506,
  "browserToServer-3": 190.09999999962747,
  "serverToExternalIP-0": "84.152.212.142 - FAIL",
  "serverToExternalIP-1": "84.152.212.142 - FAIL",
  "serverToExternalIP-2": "84.152.212.142 - FAIL",
  "serverToExternalIP-3": "84.152.212.142 - FAIL",
  "serverToExternalIP-4": "84.152.212.142 - FAIL"
}
```

As you can see, the ping time for `browserToServer` is significantly higher for [Brightdata's data collector](https://brightdata.com/products/data-collector) compared to my own browser (without any bot). And of course I cannot ping my own IP address `84.152.212.142` from the Internet, because I am behind a NAT.

However, I could obtain correct latencies for `serverToExternalIP` by measuring the TCP handshake.


#### Result: Open Ports

```
RDP:
open ports detected: 3389
VNC:
open ports detected: 5900
TeamViewer:
no open ports detected
AnyplaceControl:
open ports detected: 5279
```

#### Result: Open Ports

```
Passive OS Fingerprint
OS:
Passive OS Fingerprint: 	Linux
Browser Useragent: 	Windows
```