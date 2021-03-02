Title: 7 Common Mistakes in Professional Scraping
Date: 2021-03-01 23:13
Modified: 2021-03-02 18:30
Category: Scraping
Tags: web scraping, crawling, puppeteer, playwright
Slug: 7-common-mistakes-in-professional-scraping
Author: Nikolai Tschacher
Summary: In this blog post I am talking about my year long experience with web scraping and some common mistakes. The more I dive into web scraping, the more I realize how easy it is to make mistakes in scraping. For that reason, I compiled a list of seven common mistakes when it comes to web scraping.
 
## Introduction

I have been creating scrapers since years. Most of them were quite rubbish. But in the painful process you learn from some common mistakes. In this blog post, I share some of the most frequent mistakes that I spot in the wild and that I made myself. Furthermore, I give general advice how to remain (somewhat) undetected when scraping.

Mandatory note: Many large websites actually don't sanction scraping that much. I would count [Google](https://www.google.com/) and [Amazon](https://www.amazon.com/) to the sites that only moderately prevent scraping. The reason is obvious: Those platforms actually massively profit when other people/companies are using their data in their products. Google and Amazon are heavy players when it comes to E-Commerce and Online Marketing. So they both have an incentive to allow third-party-tools to access their platforms to a certain degree.

Other sites such as Instagram and LinkedIn are much more aggressive when it comes to blocking scrapers. They'll ban ill behaving user agents on the first suspicious activity. Websites such as LinkedIn are practically impossible to use without having an account.

Therefore, the advice in this blog post might be too strict or too lax for your specific use case. Keep that in mind.

Furthermore, this advice does not explicitly apply to scraping or crawling. Scraping often has a very negative connotation. 

But a increasingly large percentage of people using frameworks such as [puppeteer](https://github.com/puppeteer/puppeteer) or [playwright](https://github.com/microsoft/playwright) to automate otherwise mundane tasks. Therefore, there are many legit reasons why you want to train your software to navigate websites like a real human being.  

## 7 Common Mistakes in Professional Scraping

### 1. Don't Lie on the User Agent

If you are scraping with puppeteer and headless chrome on an Amazon EC2 instance and you set your user agent to be an iPhone 

`Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1`

websites have a million ways to find out that you are lying.

For example, what happens when you forgot to adjust the user agent accordingly in the `navigator.userAgent` and `navigator.appVersion` properties? Or what if you forget to spoof the `navigator.platform` property to the correct iPhone platform?

Those static strings are easy to fix, but the browser exposes such a extremely vast API to websites, which is impossible to fix in its entirety.

It is much harder to fix the following things to behave like a true iPhone device:

+ WebGL rendering and audio fingerprints
+ [Permissions API](https://developer.mozilla.org/en-US/docs/Web/API/Permissions_API), iOS devices have a very unique permissions restrictions 
+ Correct [screen dimensions](https://developer.mozilla.org/en-US/docs/Web/API/Screen). And I mean ALL OF THEM.
+ mobile touch events emulation
+ [battery status API](https://developer.mozilla.org/en-US/docs/Web/API/Battery_Status_API)
+ `deviceorientation` and `devicemotion` events 

And there are many other APIs that behave different on an iPhone compared to other mobile devices.

The following websites are quite good in detecting such inconsistencies: 

1. [creepjs](https://abrahamjuliot.github.io/creepjs/)
2. [pixelscan.net](http://pixelscan.net/checkproxy/)
3. [bot.incolumitas.com](https://bot.incolumitas.com/) (yeah I know)

It is just extremely hard to convincingly pretend you are an iPhone when in reality you are a headless chrome browser in some cloud infrastructure.

For example, when you run the following code:

```JavaScript
const { webkit, devices } = require('playwright');
const androidDevice = devices['Pixel 2 XL'];

(async () => {
  const browser = await webkit.launch({headless: false});
  const context = await browser.newContext({
    ...androidDevice,
    locale: 'en-US',
  });
  const page = await context.newPage();
  await page.goto('https://bot.incolumitas.com/');
  await page.screenshot({ path: 'botOrNot.png' });
  await browser.close();
})();
```

you will find so many cues whey the user agent just can't possibly be a real Pixel smartphone.

What to do instead? 

I'd suggest to not lie on the user agent that you *truly* are. If your automated browser is running on a Linux system in the cloud, don't alter your user agent. Although Linux systems are quite rare in the wild, they are still legit user agents that websites should not block.

### 2. Don't scrape too aggressively

This is another common mistakes I see people making. Don't scrape too aggressively. After all, you are interested in public data, you don't want to launch a Denial of Service attack against a website. So please be considerate. 

Furthermore, if your scraping becomes a major pain for the websites administrators, they will be extra careful to block all illegitimate traffic.

So it's better to throttle your scraping and to stay below the radar.

### 3. Don't use AWS Lambda or any other serverless infrastructure for scraping

I am very guilty of this one. I used üAWS Lambda](https://aws.amazon.com/lambda/) for a long time. I managed to scrape millions of Google SERPs within days on AWS Lambda (even without any proxies and just by using the AWS Lambda public IP address pool).

There exist [mature Node.js modules](https://github.com/alixaxel/chrome-aws-lambda) that ship chromium binaries specifically compiled for the AWS Lambda runtime.

But in order to run the chrome browser on AWS Lambda, you need to launch the chrome browser with many special [command line arguments](https://github.com/alixaxel/chrome-aws-lambda/blob/master/source/index.js):

```JavaScript
/**
  * Returns a list of recommended additional Chromium flags.
  */
static get args() {
  const result = [
    '--autoplay-policy=user-gesture-required',
    '--disable-background-networking',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-breakpad',
    '--disable-client-side-phishing-detection',
    '--disable-component-update',
    '--disable-default-apps',
    '--disable-dev-shm-usage',
    '--disable-domain-reliability',
    '--disable-extensions',
    '--disable-features=AudioServiceOutOfProcess',
    '--disable-hang-monitor',
    '--disable-ipc-flooding-protection',
    '--disable-notifications',
    '--disable-offer-store-unmasked-wallet-cards',
    '--disable-popup-blocking',
    '--disable-print-preview',
    '--disable-prompt-on-repost',
    '--disable-renderer-backgrounding',
    '--disable-setuid-sandbox',
    '--disable-speech-api',
    '--disable-sync',
    '--disk-cache-size=33554432',
    '--hide-scrollbars',
    '--ignore-gpu-blocklist',
    '--metrics-recording-only',
    '--mute-audio',
    '--no-default-browser-check',
    '--no-first-run',
    '--no-pings',
    '--no-sandbox',
    '--no-zygote',
    '--password-store=basic',
    '--use-gl=swiftshader',
    '--use-mock-keychain',
  ];

  if (Chromium.headless === true) {
    result.push('--single-process');
  } else {
    result.push('--start-maximized');
  }

  return result;
}
```

I am quite positive that normal chrome browser are not launched with those command line arguments and that it is possible to detect those settings for the websites being visited.

Furthermore, there are just too many disadvantages when scraping with AWS Lambda:

+ The lambda runtime is very restrictive
+ You have to test every feature twice and double before it works AWS Lambda
+ It is more expensive then self managed VPS servers
+ It is a major pain in the ass for debugging
+ Deployments eat up quite some time 

In the long run, those disadvantages kill the two or three plus points that lambda brings to the table:

+ AWS Lambda caches state and prevents coldstarts
+ You only pay for what you use
+ You do not have to manage servers yourself

Nowadays, I would suggest to use something like a proper Docker scraping image and a cluster management toolchain such as docker swarm or kubernetes instead and rent out VPS servers as scraping demand increases. 

### 4. Learn from mistakes from professional scraping services

There are many professional scraping services that you can research. They have learned over the years and you can see how they camouflage they scrapers. Sometimes even the professional services make mistakes though.

#### [ScrapingBee](https://scrapingbee.com)

For example they set the user agent to either 

1. `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36`
2. `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36`

but they forget to spoof the `navigator.platform` property accordingly. It is still set to `"platform": "Linux x86_64"`. Obviously, that is very suspicious and would get flagged by many bot detection software.

#### [scraperapi.com](https://www.scraperapi.com/)

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

#### [scrapingrobot.com](https://scrapingrobot.com)

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

### 5. Don't disregard Fingerprinting

Scraping is so hard, because there are endless ways to fingerprint a device. You can fingerprint devices on the following levels:

1. **TCP/IP fingerprinting** (for example with [p0f](https://lcamtuf.coredump.cx/p0f3/))
2. **TLS fingerprinting** (for example with [ja3](https://github.com/salesforce/ja3))
3. **Browser/JavaScript fingerprinting** (for example with [fingerprintjs2](https://github.com/fingerprintjs/fingerprintjs))
4. HTTP header fingerprinting
5. ... and probably many others stacks where fingerprinting is applicable

But why is fingerprinting so relevant for scraping?

Remember, when you want to create a scraper that is able to request a certain websites many 1000 times in a short time, your 
overall goal for your scraping traffic is to appear to be organic, human like.

Put differently, your goal is to make it as hard as possible to cluster and correlate your scraping user agents into groups.

That is also the reason why you are using proxies. Each scraper instance changes it's IP address after a couple of requests (sometimes as low as 20).

But what happens if you request a certain website 1.000.000 times and you change the IP address on every 500th request. Then the website cannot reasonably block you based on the IP address level, but they can infer that you are still the very same device, because most likely your browser fingerprint does not change when the IP address changes.

See? 

So what exactly constitutes a good fingerprint?

**A good fingerprint needs to have as much entropy as possible, while at the same time aiming to be resilient against minor changes!** 

Note that those two optimization goals contradict each other! You can't maximize both at the same time. It's a typical optimization problem.

For example, a good browser fingerprint should not change when the browser is updated. Therefore, the User-Agent is not a good entropy source for a fingerprint. Furthermore, a good fingerprint should not change when the user is switching into incognito mode. Therefore, cookies and other server side set data are no good either!

The much liked open source project [fingerprintjs2](https://github.com/fingerprintjs/fingerprintjs) uses the following entropy sources to build its fingerprint:

```Typescript
export const sources = {
  osCpu: getOsCpu, // navigator.oscpu
  languages: getLanguages, // navigator.language and navigator.languages
  colorDepth: getColorDepth, // window.screen.colorDepth
  deviceMemory: getDeviceMemory, // navigator.deviceMemory
  screenResolution: getScreenResolution, // screen.width and screen.height
  availableScreenResolution: getAvailableScreenResolution, // screen.availWidth and screen.availHeight
  hardwareConcurrency: getHardwareConcurrency, // navigator.hardwareConcurrency
  timezoneOffset: getTimezoneOffset, //
  timezone: getTimezone, // (new window.Intl.DateTimeFormat).resolvedOptions().timeZone
  sessionStorage: getSessionStorage, // !!window.sessionStorage
  localStorage: getLocalStorage, // !!window.localStorage
  indexedDB: getIndexedDB, // !!window.indexedDB
  openDatabase: getOpenDatabase, // !!window.openDatabase
  cpuClass: getCpuClass, // navigator.cpuClass
  platform: getPlatform, // navigator.platform
  plugins: getPlugins, // navigator.plugins
  canvas: getCanvasFingerprint, // 
  touchSupport: getTouchSupport,// navigator.maxTouchPoints
  fonts: getFonts, //
  audio: getAudioFingerprint, //
  pluginsSupport: getPluginsSupport, // !!navigator.plugins
  productSub: getProductSub, // navigator.productSub
  emptyEvalLength: getEmptyEvalLength, // eval.toString().length
  errorFF: getErrorFF, //
  vendor: getVendor, // navigator.vendor
  chrome: getChrome, // window.chrome !== undefined
  cookiesEnabled: areCookiesEnabled, // check document.cookie writable
}
```

As you can see from the entropy sources, they are more or less stable. But concatenated and hashed with SHA2, they have enough entropy to be very unique.

### 6. Be aware of Behavioral UI Analysis 

Some anti bot companies such as [PerimeterX](https://www.perimeterx.com/) and [Shape Security](https://www.shapesecurity.com/) record mouse movements and other user generated UI data such as scroll events or key presses. 



### 7. Side channel attacks might reveal the truth

To be done.


## Conclusion

To be done.

