Title: Detecting scraping services
Date: 2021-03-06 23:13
Status: draft
Category: Scraping
Tags: detecting, scraping, security, fingerprint
Slug: detecting-scraping-services
Author: Nikolai Tschacher
Summary: In this blog post I will demonstrate how it is possible to detect several scraping services.

There are many professional scraping services that offer scraping / crawling services to their clients. More often than not, they attempt to camouflage the automating scraping process. Sometimes even the professional services make mistakes though.

My intention with this blog post is not to diminish and look down on the work that those services have put into their products. I just want to demonstrate that there are a plethora of ways to detect the automated nature of their traffic.

In my opinion, it is much harder to create a stealthy scraping service than to detect it: For detection, you only need to find one single anomaly. To remain stealthy, you must be perfect. Therefore, a resilient and stealthy scraping service is very hard to find.


## Detecting [luminati.io](https://luminati.io/)

Luminati is arguably one of the best scraping / proxying services out there, albeit one of the most expensive.

For a long time, they only offered proxies, but they started also to offer [data extraction tools](https://luminati.io/products/data-collector) with real web browsers.

With luminiati, you can use proxies like that:

```bash
curl --proxy zproxy.lum-superproxy.io:22225 --proxy-user lum-customer-xxx:yyy "https://bot.incolumitas.com/"
```

But we are more interested in their custom data collector.

We create the following data collector:

https://luminati.io/cp/data_collector/collectors/c_klxn3iw412l3u3v1g1/code

```JavaScript
// Click the 'play' button in the top right to run this code:
// 1. Go to the page where you want to start
navigate('https://bot.incolumitas.com/');
// 2. Add anything else you need to do on the page.
// For example: (see the help box for all command docs).
// click('.some-button')
// type('.some-input', 'shoes')

wait_for_text('#ja3', 'ja3_digest');

// wait('.some-lazy-loaded-element')
// 3. Once the browser page has the data you want, call collect() to add a
// record to your final dataset
collect({
    url: location.href,
    // Before using this line, you need to define the 'price' field in
    // the parser section
    // price: parse().price,
});
```

After scraping the [bot detection site](https://bot.incolumitas.com/) for a couple of times, those are the fingerprints we manage to obtain: 

| # | ip             | user agent                                                                                                         | browser fingerprint              | ja3 fingerprint                                                     | p0f fingerprint             | canvas fingerprint | WebGL fingerprint                                                |
|---|----------------|--------------------------------------------------------------------------------------------------------------------|----------------------------------|---------------------------------------------------------------------|-----------------------------|--------------------|------------------------------------------------------------------|
| 1 | 100.4.193.199  | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.83 Safari/537.36 | ff85adf22012f400f5333f54ffebc916 | b32309a26951912be7dba376398abc3b / 7f805430de1e7d98b1de033adb58cf46 | Linux 2.2.x-3.x [generic]   | DAC6F11B           | 301740ff533ffb146abf0cce712f56cb8d06ba6bb399cd571c092b5519289cb8 |
| 2 | 73.165.148.79  | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.83 Safari/537.36 | 68a9ea61c7ae62f1d9d2c348c1823a2c | b32309a26951912be7dba376398abc3b / 7f805430de1e7d98b1de033adb58cf46 | Linux 2.2.x-3.x [generic]   | DA9F01B9           | 301740ff533ffb146abf0cce712f56cb8d06ba6bb399cd571c092b5519289cb8 |
| 3 | 98.113.59.48   | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 | ffe31d567bd285ba340797681a136cc3 | 7f805430de1e7d98b1de033adb58cf46 / b32309a26951912be7dba376398abc3b | Linux 2.2.x-3.x [generic]   | 6CE02F78           | 301740ff533ffb146abf0cce712f56cb8d06ba6bb399cd571c092b5519289cb8 |
| 4 | 108.65.38.171  | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 | a00f02fed04ef645c1abb335dfe3e12f | 7f805430de1e7d98b1de033adb58cf46 / b32309a26951912be7dba376398abc3b | Linux 2.2.x-3.x [generic]   | 6FDC3774           | 301740ff533ffb146abf0cce712f56cb8d06ba6bb399cd571c092b5519289cb8 |
| 5 | 76.186.133.171 | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 | c0d70db11fc439a78865a0f89f7fa65e | b32309a26951912be7dba376398abc3b / 7f805430de1e7d98b1de033adb58cf46 | Windows NT kernel [generic] | D40672D6           | 301740ff533ffb146abf0cce712f56cb8d06ba6bb399cd571c092b5519289cb8 |
| 6 | 47.35.219.101  | Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 | b631bc196165e8f5931b0388a20eb69f | 7f805430de1e7d98b1de033adb58cf46 / b32309a26951912be7dba376398abc3b | Linux 2.2.x-3.x [generic]   | 5D10FDE8           | 301740ff533ffb146abf0cce712f56cb8d06ba6bb399cd571c092b5519289cb8 |


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


For example they set the user agent to either 

1. *Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36*
2. *Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36*

but they forget to spoof the `navigator.platform` property accordingly. It is still set to `"platform": "Linux x86_64"`. Obviously, that is very suspicious and would get flagged by many bot detection software.


## Detecting [scraperapi.com](https://www.scraperapi.com/)

This is another commercial scraping service. Their scrapers also exhibit some weird behavior.

For example, their scraping browsers have the timezone set to `Etc/Unknown`. This is very obscure.

You can obtain the timezone with the JavaScript snippet `(new window.Intl.DateTimeFormat).resolvedOptions().timeZone`. 

Furthermore, the scraperapi.com scrapers have no WebGL support. It is not possible to obtain the video card settings.

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


## Detecting [scrapingrobot.com](https://scrapingrobot.com)

Some issues with scrapingrobot.com are the following:

The scrapers of scrapingrobot.com are using the following screen size properties:

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