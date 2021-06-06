Title: Detecting Brightdata's (formerly Luminati Networks) Data Collector as a bot
Status: published
Date: 2021-06-05 17:45
Date: 2021-06-06 12:46
Category: Security
Tags: proxy-provider, bot-detection, anti-scraping
Slug: detecting-brightdata-data-collector-as-bot
Author: Nikolai Tschacher
Summary: In this blog article I demonstrate several bullet-proof ways how to detect [Brightdata Data Collector](https://brightdata.com/products/data-collector) as a bot without any doubt.

# TL;DR

It's very easy to detect [Brightdata Data Collector](https://brightdata.com/products/data-collector) as bot. Brightdata former name was Luminati Networks.

The four largest findings to detect their data collector as bot:

1. It's easy to demonstrate that the `navigator` object is heavily spoofed by comparing certain [Web Worker](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers) `navigator` properties and [Service Worker](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API) `navigator` properties to the DOM's `window.navigator` properties (such as `navigator.userAgent` or `navigator.platform`). Furthermore, it's possible to see that `HeadlessChrome` as a browser and `Linux x86_64` as a platform is used.
2. By comparing the network latencies from browser to server and from server to external IP address, it's possible to interpolate that proxies are used. Furthermore, the external IP's of [Brightdata Data Collector](https://brightdata.com/products/data-collector) answer to ICMP ping packets (sometimes).
3. The TCP/IP fingerprint recorded with my own tool [zardaxt.py](https://github.com/NikolaiT/zardaxt) indicates a different operating system (mostly Linux) than what is advertised in the HTTP User Agent header (which is mostly Windows 10)
4. It's possible to detect that the canvas `getImageData()` method was spoofed. There are several spoofing mechanisms and anti-canvas fingerprinting defenses that should not occur with real browsers.

# Introduction

[Brightdata](https://brightdata.com/) (formerly *Luminati Networks*) is probably the largest proxy provider on the planet.

Their main product is a large proxy network. They offer datacenter, residential and mobile proxies. They can do so, because their sister company [hola.org](https://hola.org/) provides as browser extension that allows to share the network bandwith with other users of [hola.org](https://hola.org/). It's a peer-to-peer network and allows their often unaware clients to change their IP address to circumvent geo-blocking or remain anonymous. If you are not from Europe or the US, you very often have to endure ridiculous geo-blocking. That's why such services and VPN providers are in huge demand.

Put differently: [hola.org](https://hola.org/) installs a proxy server on each person's computer/mobile phone and [Brightdata](https://brightdata.com/) resells this bandwith/proxies as residential and mobile proxies to large business customers. There is no such thing as a free service. If it's free, then you are the product.

But most recently, [Brightdata](https://brightdata.com/) also strongly pushed into the data collection niche (data as a service) by allowing their clients access to a full fledged browser with JavaScript capabilities that is hard to distinguish from a real human controlled browser. This service is called [Brightdata Data Collector](https://brightdata.com/products/data-collector) and is the center of attention in this blog article.

<figure>
    <img src="{static}/images/brightdata.png" alt="Brightdata data collector" />
    <figcaption>Brightdata data collector - Or: Best solution for sneaker bots?</figcaption>
</figure>

As Brightdata's product marketing image above suggests, the data collector can be used to scrape search engines, prices from E-Commerce websites, scrape the most recent published real estate listings on realtor websites. If you have an advanced undetectable bot, you have an enormous advantage in the Internet, because speed and automatization is often a huge advantage in transactions were demand is high and supply is low.

In this blog post, my goal is to find some reliable ways to detect [Brightdata's data collector](https://brightdata.com/products/data-collector) as a bot.

# Approach

I will use the following bot detection sites and visit them with [Brightdata's data collector](https://brightdata.com/products/data-collector). Put differently: Instead of scraping an arbitrary site such as Google, I will let the bot visit a bot detection site and investigate the results of the detection site.

1. [creepjs](https://abrahamjuliot.github.io/creepjs/)
2. [pixelscan.net](https://pixelscan.net/)
3. [whatleaks.com](https://whatleaks.com/)
4. [f.vision](http://f.vision/)

For each detected listing, I will try to re-implement the test that triggered the detection. Only when I am capable of re-implementing the detection test, I truly understand why a site claims to have detected the visitor as bot and I am able to craft my own judgement.

For each bot detection site listed above, I will request the site five times.

# Testing with whatleaks.com

Here [is a link](https://github.com/NikolaiT/detecting-brightdata/tree/main/whatleaks) to the [whatleaks.com](https://whatleaks.com/) results.

I will use the following [Brightdata data collector ](https://brightdata.com/products/data-collector) script:

```JavaScript
navigate('https://whatleaks.com');

wait('#doesNOtExit', {timeout: 230000})

collect({
    url: location.href,
});
```

<figure>
    <img src="{static}/images/whatLeaks.png" alt="Brightdata data collector" />
    <figcaption>This is what the whatleaks.com results page looks like.</figcaption>
</figure>

#### Result 1: Data Collector IP found in Spam Blacklist

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
    <figcaption>Brightdata  IP address is listed on https://www.dnsbl.info/dnsbl-database-check.php</figcaption>
</figure>

I have to idea how accurate [dnsbl.info](https://www.dnsbl.info/dnsbl-database-check.php) is, but as a quick check, I looked up my own public IP address and there is also one spam report for my very own ISP IP (Detected on `b.barracudacentral.org`). So I would not consider those publicly accessible spam lookup databases as overly trustworthy.

With the other IP addresses of the other four samples I got a similar result.

#### Result 2: Ping - Proxy usage detected in Connection

When looking up the test description on [whatleaks.com](https://whatleaks.com/):

> We compare ping from your computer to our server and ping from our server to the host of your external IP. If the difference is too much then there is probably a tunnel and you are using a proxy.

I re-implemented this ping proxy detection test in [my last blog article](http://localhost:8000/2021/04/24/detecting-proxies/) where I also quickly programmed my own test. Link to my own ping-based proxy detection test: [bot.incolumitas.com/crossping.html](https://bot.incolumitas.com/crossping.html)

For example, those are the results of the crossping test when letting [Brightdata's data collector](https://brightdata.com/products/data-collector) visit my [crossping test site](https://bot.incolumitas.com/crossping.html):

Test Run 1:

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

Test Run 2:

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

And this is me with my own Laptop and Browser and without any proxy visiting my detection site:

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

As you can see, the ping time for `browserToServer` is significantly higher for [Brightdata's data collector](https://brightdata.com/products/data-collector) compared to my own browser (without any bot). And of course I cannot ping my own IP address `84.152.212.142` from my webserver, because I am behind a NAT.

If I really need reliable `serverToExternalIP` measurements, I could obtain correct latencies for `serverToExternalIP` by measuring the TCP handshake RTT.

So what can we say from the tests above? 

In both cases when using [Brightdata's data collector](https://brightdata.com/products/data-collector), the latencies were quite high with around 1 second. This stands in contrast to very small latencies around 100ms when visiting the test with my own browser without any proxy. Of course geolocation latencies need to be kept in mind, but usually geolocation induced latencies don't add up to more than 200ms - 300ms.  

In conclusion I can say that I am quite confident that it must be possible to apply some statistics and make a statement such as: The `browserToServer` latencies are significantly higher than the `serverToExternalIP` latencies and therefore we can conclude that there must be some intermediary in the connection!

#### Result: Data Collector IP has Open Ports

I implemented a simple portscan route on my Express web server:

```JavaScript
app.get('/portscan', async (req, res) => {
  // ping the external IP address
  let ip = getIp(req);

  let command = `nmap -p3389,5900,5901,5938,5939,5279 ${ip} 2>&1`;
  const { stdout, stderr } = await exec(command);

  res.header("Content-Type",'application/json');
  return res.send(ip + ' - ' + stdout.trim());
});
```

Test site: [portscan](https://abs.incolumitas.com/portscan)

[whatleaks.com](https://whatleaks.com/) claims that [Brightdata's data collector](https://brightdata.com/products/data-collector) has open ports:

<figure>
    <img src="{static}/images/whatLeaksPorts.png" alt="Several Open Ports detected by whatleaks.com" />
    <figcaption>Several Open Ports detected by whatleaks.com</figcaption>
</figure>

I could reproduce those findings with my portscan method above. See the image below for proof:

<figure>
    <img src="{static}/images/portscanWL.png" alt="Several Open Ports detected by whatleaks.com" />
    <figcaption>Several Open Ports detected by my port scanning function</figcaption>
</figure>

I assume that Brightdata defends against port scanning with restrictive `iptables` rules, that's why I only get `filtered` as result. But undoubtedly, those ports are open.

#### Result: Data Collector's TCP/IP Fingerprint different from claimed Browser User Agent

I will use my own TCP/IP fingerprinting tool named [zardaxt.py](https://github.com/NikolaiT/zardaxt/) to conduct this test. 

Link to the TCP/IP detection test site: [bot.incolumitas.com/tcpip.html](https://bot.incolumitas.com/tcpip.html)

When visiting the [whatleaks.com](https://whatleaks.com/) test site with [Brightdata's data collector](https://brightdata.com/products/data-collector), the site detects a passive OS fingerprint of `Linux` but a `Windows` OS according to the User Agent.

<figure>
    <img src="{static}/images/wlfp.png" alt="Several Open Ports detected by whatleaks.com" />
    <figcaption>Linux as detected by the TCP/IP fingerprint, but User Agent says Windows</figcaption>
</figure>

Replication: When testing [Brightdata's data collector](https://brightdata.com/products/data-collector) three times with my [own TCP/IP fingerprinting tool](https://bot.incolumitas.com/tcpip.html), I get the following results:

<figure>
    <img src="{static}/images/tcpip-zxt1.png" alt="TCP/IP fingerprint for Brightdata data collector" />
    <figcaption>Here it is quite obvious that the User Agent OS is different compared to the TCP/IP fingerprint OS. The TCP/IP fingerprint is most likely Linux.</figcaption>
</figure>

<figure>
    <img src="{static}/images/tcpip-zxt2.png" alt="TCP/IP fingerprint for Brightdata data collector" />
    <figcaption>Here zardaxt.py fails to make a convincing statement. However, the score for Windows is the lowest, although the User Agent says it's a Windows device...</figcaption>
</figure>

<figure>
    <img src="{static}/images/tcpip-zxt3.png" alt="TCP/IP fingerprint for Brightdata data collector" />
    <figcaption>Here the User Agent OS matches the suggested TCP/IP fingerprint OS. This one looks legit.</figcaption>
</figure>


# Testing with creepjs

Here [is a link](https://github.com/NikolaiT/detecting-brightdata/tree/main/creepjs) to the [creepjs](https://abrahamjuliot.github.io/creepjs/) results.

I will use the following [Brightdata data collector ](https://brightdata.com/products/data-collector) script:

```JavaScript
navigate('https://abrahamjuliot.github.io/creepjs/', {timeout: 230000});

wait('#fingerprint-data > div:nth-child(3) > div:nth-child(2) a');

click('#fingerprint-data > div:nth-child(3) > div:nth-child(2) a');

collect({
    url: location.href,
});
```

CreepJS is really devastating in it's opinion about [Brightdata data collector](https://brightdata.com/products/data-collector). It gives a trust score of **0%**, see the image below:

<figure>
    <img src="{static}/images/creepJS.png" alt="creepjs results page" />
    <figcaption>This is what the creepjs results page look like. The data collector gets the worst trust score possible.</figcaption>
</figure>

The [creepjs](https://abrahamjuliot.github.io/creepjs/) bot detection site is a gold mine. Even better, the library is [open source](https://github.com/abrahamjuliot/creepjs).

There are so many findings, it's hard to list them all. Let's get started:

#### Result 1: Service Worker navigator differs from main navigator

<figure>
    <img src="{static}/images/creepSW.png" alt="creepjs results page" />
    <figcaption>creepjs reports that Service Worker navigator properties show the un-spoofed values for the real navigator property</figcaption>
</figure>

To put it shortly, modern browsers have something called [Service Workers](https://developers.google.com/web/fundamentals/primers/service-workers). It's basically a proxy layer that sits between the web application and the server and adds offline-mode features (amongst others).

In the context of [Service Workers](https://developers.google.com/web/fundamentals/primers/service-workers), there is also a `navigator` property.

My claim (and of course creepjs's claim) is: The bot programmers forgot to spoof those values like they did with main `navigator` property.

Therefore, I implemented a test that compares the `navigator` values from the DOM with the values from the Service Worker context. Link to test: [https://bot.incolumitas.com/sw.html](https://bot.incolumitas.com/sw.html)

This is the result:

<figure>
    <img src="{static}/images/sw-mismatch.png" alt="creepjs results page" />
    <figcaption>boom - detected</figcaption>
</figure>

Do you see what I see?

The bot claims to be `Win32` but is `Linux x86_64` when inspecting `navigator.platform`

The bot claims to be `Chrome/90.0.4430.72` but is `HeadlessChrome/90.0.4430.93` when inspecting `navigator.userAgent`.

Totally busted.

#### Result 2: Web Worker navigator differs from main navigator

Same logic here, expect that [Brightdata data collector ](https://brightdata.com/products/data-collector) spoof's a bit more with [Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API), so it's less fatal, but still enough to detect them as bot.

Link to test: [https://bot.incolumitas.com/ww.html](https://bot.incolumitas.com/ww.html)

<figure>
    <img src="{static}/images/ww-mismatch.png" alt="creepjs results page" />
    <figcaption>boom - detected</figcaption>
</figure>

Same as with Service Workers above, the bot claims to be `Win32` but is `Linux x86_64` when inspecting `navigator.platform`.

The User Agent is correctly spoofed, unlike with Service Workers above.

But `["en-US"]` as taken from `navigator.languages` is different to `["en-US","en"]`.

It's enough to see that the browser *lies*. The values are not consistent.

# Testing with pixelscan.net

Here [is a link](https://github.com/NikolaiT/detecting-brightdata/tree/main/pixelscan) to the [pixelscan.net](https://pixelscan.net/) results.

I will use the following [Brightdata data collector ](https://brightdata.com/products/data-collector) script:

```JavaScript
navigate('https://pixelscan.net/', {timeout: 230000});

wait('#doesNOtExit', {timeout: 230000})

collect({
    url: location.href,
});
```

# Testing with f.vision

Here [is a link](https://github.com/NikolaiT/detecting-brightdata/tree/main/f.vision) to the [f.vision](http://f.vision/) results.

I will use the following [Brightdata data collector ](https://brightdata.com/products/data-collector) script:

```JavaScript
navigate('http://f.vision', {timeout: 60000});

wait('#start-button > span');

click('#start-button > span');

wait('#collapse-buttons > button.btn.btn-outline.btn-primary.expand-all', {timeout: 60000})

click('#collapse-buttons > button.btn.btn-outline.btn-primary.expand-all');

collect({
    url: location.href,
});
```

#### Result 1: Fake Canvas detected in Data Collector bot

[f.vision](http://f.vision) detection site claims to have detected fake canvas in [Brightdata data collector ](https://brightdata.com/products/data-collector)

<figure>
    <img src="{static}/images/fakeCanvas.png" alt="Detected fake canvas" />
    <figcaption>Detected fake canvas</figcaption>
</figure>

When expanding the information for *fake canvas*, [f.vision](http://f.vision) tells me:

<figure>
    <img src="{static}/images/fakeCanvasInfo.png" alt="Detected fake canvas" />
    <figcaption>More Information on fake canvas</figcaption>
</figure>

It seems that those fake canvas detection tests originate from [here](https://github.com/kkapsner/CanvasBlocker/issues/287). The original test site is named [webGL-Test](https://canvasblocker.kkapsner.de/test/webGL-Test.html).

The author states in this GitHub issue:

> As you already found out the "fake input" mode prevents the detection of normal canvas. For WebGL I'm not aware of any (reasonable) way to prevent the detection there (actually I also have a detection page for webGL: https://canvasblocker.kkapsner.de/test/webGL-Test.html)

I won't reproduce the test here, but I am quite confident that this finding is correct and that the bot spoofs different values for WebGL functionality.

#### Result 2: Various Browser Fingerprints are Static across Bot Samples

The bot detection site [f.vision](http://f.vision/) has quite nice fingerprinting techniques. For that reason I will test if it is possible to detect
[Brightdata's bot](https://brightdata.com/products/data-collector) with those fingerprints. Detection is possible if the following two properties hold:

1. The fingerprints stay the same among many independent bot samples
2. Those fingerprints together have enough entropy so you can uniquely identify the bot among thousands of normal visitors


| # | HSTS   | WEBGL            | CANVAS      | PLUGINS          | AUDIO            | CLIENT RECTS     | FONTS            |
|---|--------|------------------|-------------|------------------|------------------|------------------|------------------|
| 1 | N/A    | d0ae1aeb6476af3f | 2140246792  | f98ba1457738b341 | 19f2ec826da99435 | c01b66fbb94df014 | 8dc9258100071ba8 |
| 2 | cc832e | d0ae1aeb6476af3f | 1470235470  | f98ba1457738b341 | 19f2ec826da99435 | c01b66fbb94df014 | da39a3ee5e6b4b0d |
| 3 | cc832e | d0ae1aeb6476af3f | 1470235470  | f98ba1457738b341 | 19f2ec826da99435 | c01b66fbb94df014 | da39a3ee5e6b4b0d |
| 4 | b8c752 | d0ae1aeb6476af3f | -2125110224 | f98ba1457738b341 | 19f2ec826da99435 | c01b66fbb94df014 | 023e4ca61828dfc7 |
| 5 | 94832d | d0ae1aeb6476af3f | -198118648  | f98ba1457738b341 | 19f2ec826da99435 | c01b66fbb94df014 | 064d6b2722232577 |
| 6 | 1c7937 | d0ae1aeb6476af3f | 1426403692  | f98ba1457738b341 | 19f2ec826da99435 | c01b66fbb94df014 | da39a3ee5e6b4b0d |
| 7 | dca0b6 | d0ae1aeb6476af3f | -579119140  | f98ba1457738b341 | 19f2ec826da99435 | c01b66fbb94df014 | da39a3ee5e6b4b0d |
| 8 | fd36e9 | d0ae1aeb6476af3f | 271321058   | f98ba1457738b341 | 19f2ec826da99435 | c01b66fbb94df014 | 2aaf3ba9b5696cec |
| 9 | 69116b | d0ae1aeb6476af3f | -2097547378 | f98ba1457738b341 | 19f2ec826da99435 | c01b66fbb94df014 | da39a3ee5e6b4b0d |

As you can see from the nine [Brightdata bot](https://brightdata.com/products/data-collector) samples collected, the fingerprints for WEBGL, PLUGINS, AUDIO and CLIENT RECTS stays consistent for each bot visit. The big question: How much entropy do those fingerprints have? Is it possible to uniquely identify a [Brightdata data collector bot](https://brightdata.com/products/data-collector) with those fingerprints?

We can quickly test the entropy of the fingerprint data above by collecting samples with real devices.

The fingerprints below are taken with four different real devices when visiting [f.vision](http://f.vision/):

1. With my laptop, Linux with Chrome
2. With my Android mobile phone with Firefox
3. With [browserstack.com real device](https://www.browserstack.com/) OSX Big Sur with Chrome 91
4. With [browserstack.com real device](https://www.browserstack.com/) Win10 with Chrome 91


| # | HSTS   | WEBGL            | CANVAS      | PLUGINS          | AUDIO            | CLIENT RECTS     | FONTS            |
|---|--------|------------------|-------------|------------------|------------------|------------------|------------------|
| Linux with Chrome | 420525    | ab4364d46077693b | -31304244   | cb43bb325b87c16f | 19f2ec826da99435 | ee5b6ada17b403ef | af1e3afb793f6d87 |
| Android with Firefox | 40b4f1 | 19208ef875544de3 | 1250865652  |  N/A | 41efd79c6069738c | 4612193a6e9f936b | da39a3ee5e6b4b0d |
| OSX Big Sur with Chrome 91    | 1d26d5 | 2def3b550c3e950d | -434613739  | f98ba1457738b341 | d263e57872d8cbf0 | 09b8cf131bb1dacc | a5103579b5284324 |
| Win10 with Chrome 91 | 356893 | d0ae1aeb6476af3f | -17f22f0632  | f98ba1457738b341 | 19f2ec826da99435 | 09b8cf131bb1dacc | a267018f11767e47 |

Now let's check if the fingerprints WEBGL, PLUGINS, AUDIO and CLIENT RECTS have enough entropy.

I can disregard the WEBGL fingerprint as low entropy, because Win10 with Chrome has the same value as the bot (`d0ae1aeb6476af3f`).

Same applies to the PLUGINS fingerprint, because `f98ba1457738b341` appears also in OSX Big Sur with Chrome 91 and Win10 with Chrome 91.

Same story with AUDIO fingerprint. `19f2ec826da99435` occurs in Linux with Chrome and in Win10 with Chrome 91.

And CLIENT RECTS has also low entropy, because both OSX Big Sur with Chrome 91 and Win10 with Chrome 91 have the value `09b8cf131bb1dacc`.

**Conclusion:** Fingerprinting for [Brightdata's bot](https://brightdata.com/products/data-collector) will not be straighforward with [f.vision](http://f.vision/) fingerprints.


