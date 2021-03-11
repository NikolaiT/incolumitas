Title: Detecting scraping services
Date: 2021-03-11 22:00
Category: Scraping
Tags: detecting, scraping, security, fingerprint
Slug: detecting-scraping-services
Author: Nikolai Tschacher
Summary: In this blog post I will demonstrate how it is possible to detect several scraping services: [luminati.io](https://luminati.io/), [ScrapingBee](https://scrapingbee.com), [scraperapi.com](https://www.scraperapi.com/), [scrapingrobot.com](https://scrapingrobot.com), [scrapfly.io](https://scrapfly.io).

There exist many professional scraping services that offer data extraction services to their clients. More often than not, those services attempt to camouflage that they are bots. Sometimes even professional services make mistakes though.

My intention with this blog post is not to diminish and look down on the work that those services have put into their products. I just want to demonstrate that there are a plethora of ways to detect the automated nature of their traffic.

In my opinion, it is much harder to create a stealthy scraping service than to detect it: For detection, you only need to find one single anomaly. To remain stealthy, you must be perfect. Therefore, a resilient and stealthy scraping service is very hard to find.

I hope those services can make use of some of my resarch provdided for free here.

Note: The bot detection site [bot.incolumitas.com](https://bot.incolumitas.com) was used as a scraping target with all scraping services listed below.

## Detecting [Luminati.io](https://luminati.io/)

Luminati is arguably one of the best scraping / proxying services out there, albeit one of the most expensive.

I don't like to admit it, because I don't really dig their [business strategy](https://documents.trendmicro.com/assets/white_papers/wp-illuminating-holaVPN-and-the-danger-it-poses.pdf), but from all of the researched scraping businesses they are by far the best.

I heavily suspect that they actually use the real browsers
from the users that have installed the [hola browser extension](https://hola.org/). I cannot explain how else they manage to create such a convincingly real browser profile.

For a long time, Luminati only offered proxies, but they started also to offer [data extraction tools](https://luminati.io/products/data-collector) with real web browsers.

With Luminati, you can use proxies like that:

```bash
curl --proxy zproxy.lum-superproxy.io:22225 --proxy-user lum-customer-xxx:yyy "https://bot.incolumitas.com/"
```

But we are more interested in their custom data collector which uses a real browser to proxy their requests.

We create the following [data collector](https://luminati.io/cp/data_collector/collectors/c_klxn3iw412l3u3v1g1/code):

```JavaScript
navigate('https://bot.incolumitas.com/');
wait_for_text('#ja3', 'ja3_digest');
collect({
    url: location.href,
});
```

After scraping the [bot detection site](https://bot.incolumitas.com/) for a couple of times, those are the fingerprints we manage to obtain: 

| # | ip             | user agent                                                                                                         | browser fingerprint              | ja3 fingerprint                                                     | p0f fingerprint             | canvas fingerprint | WebGL fingerprint                                                |
|---|----------------|--------------------------------------------------------------------------------------------------------------------|----------------------------------|---------------------------------------------------------------------|-----------------------------|--------------------|------------------------------------------------------------------|
| 1 | 100.4.193.199  | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.83 Safari/537.36 | ff85adf22012f400f5333f54ffebc916 | b32309a26951912be7dba376398abc3b / 7f805430de1e7d98b1de033adb58cf46 | Linux 2.2.x-3.x [generic]   | DAC6F11B           | 301740 |
| 2 | 73.165.148.79  | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.83 Safari/537.36 | 68a9ea61c7ae62f1d9d2c348c1823a2c | b32309a26951912be7dba376398abc3b / 7f805430de1e7d98b1de033adb58cf46 | Linux 2.2.x-3.x [generic]   | DA9F01B9           | 301740 |
| 3 | 98.113.59.48   | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 | ffe31d567bd285ba340797681a136cc3 | 7f805430de1e7d98b1de033adb58cf46 / b32309a26951912be7dba376398abc3b | Linux 2.2.x-3.x [generic]   | 6CE02F78           | 301740 |
| 4 | 108.65.38.171  | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 | a00f02fed04ef645c1abb335dfe3e12f | 7f805430de1e7d98b1de033adb58cf46 / b32309a26951912be7dba376398abc3b | Linux 2.2.x-3.x [generic]   | 6FDC3774           | 301740 |
| 5 | 76.186.133.171 | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 | c0d70db11fc439a78865a0f89f7fa65e | b32309a26951912be7dba376398abc3b / 7f805430de1e7d98b1de033adb58cf46 | Windows NT kernel [generic] | D40672D6           | 301740 |
| 6 | 47.35.219.101  | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 | b631bc196165e8f5931b0388a20eb69f | 7f805430de1e7d98b1de033adb58cf46 / b32309a26951912be7dba376398abc3b | Linux 2.2.x-3.x [generic]   | 5D10FDE8           | 301740 |

After a thorough analysis, I have to admit that Luminati is doing many things extremely well. 

The WebGL fingerprint is inaccurate. It does not say much that it is always identical. I have the same WebGL fingerprint on my Android phone. The same applies to the TLS fingerprint. There is not enough entropy here to make a statement.

The canvas fingerprint and the browser fingerprint do change. Just as expected.

The only curious thing is the Linux OS that was detected by [p0f](https://github.com/p0f/p0f). But I do not trust this OS detection feature from p0f enough. p0f seems quite old and is not really maintained since years. It doesn't event detect Linux kernels newer than the 3.x versions.

Maybe we have to dig a bit deeper regarding OS fingerprinting on a TCP/IP level.

[Satori.py](https://github.com/xnih/satori) looks like a good tool for it with an extensive and [up to date database](https://github.com/xnih/satori/blob/master/fingerprints/tcp.xml). It's written in easy to understand Python and this gives me enough freedom to hack my own logic into it if needed. p0f seems a bit more complicated and not so fast for quick changes.

So the strategy looks like the following:

1. We collect several [Luminati.io](https://luminati.io/) TCP/IP network captures and check the RAW TCP/IP signature we obtain.
2. Then we check if this signature is significantly different from the User Agent that Luminati claims to be.

After trying for a bit with [Satori.py](https://github.com/xnih/satori) I realized that the tool was a huge mess and I ended up creating [my own TCP/IP fingerprinting tool](https://github.com/NikolaiT/zardaxt).

I compiled my [own TCP/IP fingerprint database]() and started to compare the Luminati data collector against it.

In almost all cases I got something like this:

```text
{'score': '9.5/9.5', 'os': 'Windows NT 10.0; Win64; x64'}
```

Luminati claims in it's User-Agent that it is *Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36* and in almost all cases, the TCP/IP fingerprint agrees with that.

I had only one case where I got a TCP/IP fingerprint which I could not properly identify.

```text
[{'score': '6/9.5', 'os': 'Macintosh; Intel Mac OS X 11_2_3'}, {'score': '6/9.5', 'os': 'X11; Linux x86_64'}, {'score': '6/9.5', 'os': 'Windows NT 10.0; Win64; x64'}, {'score': '5/9.5', 'os': 'Windows NT 6.1; Win64; x64; rv:87.0'}]
```

In that case, I have no exact match in my database. So when Luminati is lying here, then in maybe 1/10 cases, Luminati is lying about it's User Agent and it's detectable with TCP/IP fingerprinting.

So there must be good way to detect that the traffic coming from [Luminati.io](https://luminati.io/) is not humanly generated and thus not organic.

Of course we could say that the lack of human UI interaction events is suspicous. But the browser only stays on the website for a few seconds. Opening a tab and not interacting with it could also be the result of human behavior.

Maybe scraping from Luminati's network is possible by measuring latency and RTT's. After all, when my theory is correct, they need to route traffic somehow like that:

[Luminati data collector] => [Luminati hola browser extension user] => [bot.incolumitas.com] =>  and all the way back.

Maybe this information helps us to to something...

## Detecting [ScrapingBee](https://scrapingbee.com)

I collected several samples from scrapingbee. I used the following API call:

```bash
curl "https://app.scrapingbee.com/api/v1/?api_key={API_KEY}&url=https%3A%2F%2Fbot.incolumitas.com%2F&wait=4000&block_ads=false&block_resources=false"
```

Here are some extracted criteria from the seven samples:

| # | ip              | user agent                                                                                                                | browser fingerprint              | tls fingerprint                  | tcp/ip fingerprint        |   |
|---|-----------------|---------------------------------------------------------------------------------------------------------------------------|----------------------------------|----------------------------------|---------------------------|---|
| 1 | 107.152.210.73  | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36       | b11a52c168016c4ba71b5275117ccf27 | 7f805430de1e7d98b1de033adb58cf46 | Linux 3.x [generic]       |   |
| 2 | 107.173.246.155 | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36       | b11a52c168016c4ba71b5275117ccf27 | b32309a26951912be7dba376398abc3b | Linux 3.x [generic]       |   |
| 3 | 209.127.110.235 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36 | b11a52c168016c4ba71b5275117ccf27 | -                                | Linux 2.2.x-3.x [generic] |   |
| 4 | 104.144.180.182 | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36       | b11a52c168016c4ba71b5275117ccf27 | b32309a26951912be7dba376398abc3b | Linux 3.x [generic]       |   |
| 5 | 209.127.98.44   | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36 | b11a52c168016c4ba71b5275117ccf27 | -                                | Linux 2.2.x-3.x [generic] |   |
| 6 | 209.127.105.200 | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36       | b11a52c168016c4ba71b5275117ccf27 | -                                | Linux 2.2.x-3.x [generic] |   |
| 7 | 107.175.157.30  | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36       | b11a52c168016c4ba71b5275117ccf27 | b32309a26951912be7dba376398abc3b | Linux 3.x [generic]       |   |
| 8 | 186.179.14.119  | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36       | b11a52c168016c4ba71b5275117ccf27 | -                                | Linux 3.11 and newer      |   |


As you can see, the browser fingerprint is in every case the same: *b11a52c168016c4ba71b5275117ccf27*

This is very bad. This means that it is possible to detect user agents with the above fingerprint to be a [ScrapingBee](https://scrapingbee.com) scraping instance with relatively high likelihood.

But they made more mistakes:

For example they set the user agent to either 

1. *Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36*
2. *Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36*

but they forget to spoof the `navigator.platform` property accordingly. It is still set to `"platform": "Linux x86_64"`. Obviously, that is very suspicious and would get flagged by many bot detection programs.

One issue could be that their browser don't seem to support any multimedia devices:

```JavaScript
"multimediaDevices": {
  "speakers": 0,
  "micros": 0,
  "webcams": 0
}
```

This is usually very uncommon for normal devices. They at least support one multimedia device.

## Detecting [scraperapi.com](https://www.scraperapi.com/)

This is another commercial scraping service. Their scrapers also exhibit some weird behavior.

When scraping with the [scraperapi.com](https://scraperapi.com) API for five times with the following API call:

```bash
curl "http://api.scraperapi.com/?api_key={{API_KEY}}&url=http://bot.incolumitas.com/&render=true"
```

 we obtain the following fingerprints:

| # | user agent                                                                                                         | browser fingerprint              | ja3 fingerprint                  | canvas fingerprint |
|---|--------------------------------------------------------------------------------------------------------------------|----------------------------------|----------------------------------|--------------------|
| 1 | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 | 792ce97b0295f6f9f0d89fe974371a84 | b32309a26951912be7dba376398abc3b | E5063313           |
| 2 | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 | 792ce97b0295f6f9f0d89fe974371a84 | b32309a26951912be7dba376398abc3b | E5063313           |
| 3 | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 | 792ce97b0295f6f9f0d89fe974371a84 | b32309a26951912be7dba376398abc3b | E5063313           |
| 4 | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 | 792ce97b0295f6f9f0d89fe974371a84 | b32309a26951912be7dba376398abc3b | E5063313           |
| 5 | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 | 792ce97b0295f6f9f0d89fe974371a84 | b32309a26951912be7dba376398abc3b | E5063313           |
|   |                                                                                                                    |                                  |                                  |                    |

It is quite obvious that it is very bad that every fingerprint is the same. This means that is possible to state that we are being scraped whenever we have a visitor on our website that uses a browser fingerprint of *792ce97b0295f6f9f0d89fe974371a84*.

Some other issues were:

Their scraping browsers have the timezone set to `Etc/Unknown`. This is very obscure.

You can obtain the timezone with the JavaScript snippet `(new window.Intl.DateTimeFormat).resolvedOptions().timeZone`. 

Furthermore, the [scraperapi.com](https://www.scraperapi.com/) scrapers have no WebGL support. It is not possible to obtain the video card settings.

Usually, normal browsers have a video card such as:
 
```json
"videoCard": [
  "Intel Inc.",
  "Intel Iris OpenGL Engine"
]
```

You can obtain your video card brand names with the following script:

```JavaScript
(function getVideoCardInfo() {
  const gl = document.createElement('canvas').getContext('webgl');

  if (!gl) {
    return {
      error: "no webgl",
    };
  }
  
  const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');

  if(debugInfo){
    return {
      vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
      renderer:  gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL),
    };
  }

  return {
    error: "no WEBGL_debug_renderer_info",
  };
})()
```

Furthermore, their scrapers advertise that they don't have any multimedia devices attached to it:

```JavaScript
"multimediaDevices": {
  "speakers": 0,
  "micros": 0,
  "webcams": 0
}
```

Another strange thing are the screen dimensions:

```json
{
  "outerWidth": 1440,
  "outerHeight": 800,
  "innerWidth": 800,
  "innerHeight": 600,
}
```

Having a inner screen width x height of 800x600 is not prohibited, it is just very uncommon with real devices. But it is very common with default puppeteer chromium browsers...Just saying.

## Detecting [scrapingrobot.com](https://scrapingrobot.com)

When scraping with [scrapingrobot.com](https://scrapingrobot.com) five times, we obtain the following fingerprints:

| # | user agent                                                                                                                                                | browser fingerprint              | ja3 fingerprint                  | canvas fingerprint |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------|----------------------------------|--------------------|
| 1 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36                                  | a265019e42a330492b5182c3a7275db9 | 66918128f1b9b03303d77c6f2eefd128 | 4EDA6E5B           |
| 2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15                                   | 9e945fadfdea5733f328c54542afb842 | 66918128f1b9b03303d77c6f2eefd128 | 4EDA6E5B           |
| 3 | Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36                                        | eae9223cec3ad4985340f60fcb5f7e1f | -                                | 4EDA6E5B           |
| 4 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.41 YaBrowser/21.2.0.1122 Yowser/2.5 Safari/537.36 | 310f1133a18911b800f465e6f783c7b2 | 66918128f1b9b03303d77c6f2eefd128 | 4EDA6E5B           |
| 5 | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36                                       | c877493938932c04567b0f967507f56d | -                                | 4EDA6E5B           |
|   |                                                                                                                                                           |                                  |                                  |                    |

As you can see, the browser fingerprint switches all the time. This is a good sign and prevents the easiest way to detect the scraping. Regarding fingerprinting, I don't see too many issues with [scrapingrobot.com](https://scrapingrobot.com). 

However, there are some other issues with [scrapingrobot.com](https://scrapingrobot.com):

The scrapers of scrapingrobot are using the following screen size properties:

```json
"dimensions": {
  "window.outerWidth": 800,
  "window.outerHeight": 600,
  "window.innerWidth": 2470,
  "window.innerHeight": 1340,
  "window.screen.width": 2560,
  "window.screen.height": 1440
}
```

It should not be the case that the `window.outerWidth` and `window.outerHeight` properties are smaller than 
the `window.innerWidth` and `window.innerWidth` screen dimensions. This is a very strong indication
that the browser was messed with.

Furthermore, their scrapers don't have any plugin information (`navigator.plugins`) associated with them. This is very uncommon for legit
chrome browses. Usually, every chrome browser has standard plugin information such as 

```json
"plugins": [
  {
    "name": "Chrome PDF Plugin",
    "description": "Portable Document Format",
    "mimeType": {
      "type": "application/x-google-chrome-pdf",
      "suffixes": "pdf"
    }
  },
  {
    "name": "Chrome PDF Viewer",
    "description": "",
    "mimeType": {
      "type": "application/pdf",
      "suffixes": "pdf"
    }
  },
  {
    "name": "Native Client",
    "description": "",
    "mimeType": {
      "type": "application/x-nacl",
      "suffixes": ""
    }
  }
]
```

With `scrapingrobot.com`, this information looks like this:

```json
"plugins": [
  {
    "mimeType": null
  },
  {
    "mimeType": null
  }
]
```

Another issue with the scrapers of `scrapingrobot.com` is that they don't have any multimedia devices (`navigator.mediaDevices`) associated with the browser. Usually, a normal browser has at least one multimedia device associated (such as speakers, micros, webcams).

Normal:

```json
"multimediaDevices": {
  "speakers": 1,
  "micros": 1,
  "webcams": 1
}
```

scrapingrobot.com:

```json
"multimediaDevices": {
  "speakers": 0,
  "micros": 0,
  "webcams": 0
}
```

## Detecting [scrapfly.io](https://scrapfly.io)

The fingerprints recorded are as follows:

| # | user agent                                                                                                                | browser fingerprint              | ja3 fingerprint                  | TCP/IP fingerprint | canvas fingerprint | WebGL fingerprint |
|---|---------------------------------------------------------------------------------------------------------------------------|----------------------------------|----------------------------------|--------------------|--------------------|-------------------|
| 1 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 | 75957d6c70a68c4d716e986554e313d4 | b32309a26951912be7dba376398abc3b | Linux / Chrome OS  | 4EDA6E5B           | 45b0cf9d          |
| 2 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 | 210181aae7512e1e68c4058fa330c040 | b32309a26951912be7dba376398abc3b | Linux / Chrome OS  | 4EDA6E5B           | 45b0cf9d          |
| 3 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 | 2c901d174dc4faf1b3c7e71e7a963d62 | b32309a26951912be7dba376398abc3b | Linux / Chrome OS  | 4EDA6E5B           | 45b0cf9d          |
| 4 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 | a841a8e49dca94195ad161674c9762fa | 7f805430de1e7d98b1de033adb58cf46 | Linux / Chrome OS  | 4EDA6E5B           | 45b0cf9d          |
| 5 | Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36 | 52d35b65383ae737bd6d735078d59b20 | b32309a26951912be7dba376398abc3b | Linux / Chrome OS  | 4EDA6E5B           | 45b0cf9d          |
|   |                                                                                                                           |                                  |                                  |                    |                    |                   |

Based on the fingerprints, we cannot state much. The browser fingerprint is different for every sample. This is already a good sign. Maybe it is noteworthy to state that the TCP/IP fingerprint is releatively likely from an Linux based operating system and not from an Mac OS operating system as their User-Agent claims to be. The canvas and WebGL fingerprint are always the same. Those fingerprints don't convey much entropy, hence it is not easy to say that the samples are all conducted from the same scraping software.


They seem to have created a overall good service. Unfortunately, they made quite some mistakes.

The User-Agent in the http headers is not the same as the user agent in the `navigator` property:

1. HTTP User-Agent: *Mozilla/5.0 (X11; Linux x86_64; x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36*
2. `navigator` User-Agent: *Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36*

This is a very obvious mistake and this would result in a ban immediately with anti bot systems.

Furthermore, they always spoof the same graphic card:

```JavaScript
  "videoCard": [
    "Google Inc.",
    "ANGLE (NVIDIA GeForce GTX 660 Direct3D9Ex vs_3_0 ps_3_0)"
  ],
```

Every browser they use has the same string *ANGLE (NVIDIA GeForce GTX 660 Direct3D9Ex vs_3_0 ps_3_0)* as their video cards.

Another issue is that their scraping browser does not have a single multimedia device attached to it:

```JavaScript
  "multimediaDevices": {
    "speakers": 0,
    "micros": 0,
    "webcams": 0
  },
```

Did you ever come accross a Macintosh Computer without micro, speaker or webcam? Nope, I haven'ts.

Another mistake they make is to not set the `navigator.plugins` property at all:

```JavaScript
  "plugins": [],
  "mimeTypes": [],
```

Real browsers always have some standard values here.

Another issue with [scrapfly.io](https://scrapfly.io) is that all their HTTP requests come equipped with the "X-Amzn-Trace-Id" HTTP header set by all outgoing http requests originating from [Amazon AWS](https://aws.amazon.com/premiumsupport/knowledge-center/trace-elb-x-amzn-trace-id/). This feature allows to trace http sessions for debugging reasons.