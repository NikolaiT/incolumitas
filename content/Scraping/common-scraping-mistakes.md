Title: Common Mistakes in Scraping
Date: 2021-03-01 23:13
Category: Scraping
Tags: web scraping, crawling, puppeteer, playwright
Slug: common-mistakes-in-scraping
Author: Nikolai Tschacher
Summary: In this blog post I am talking about my year long experience with web scraping and some common mistakes. The more I dive into web scraping, the more I realize how easy it is to make mistakes in scraping.

## Introduction

I have been creating scrapers since years. Most of them were quite rubbish. But in the process you kinda learn from some common mistakes. In this blog post, I share some of the most frequent mistakes that I spot in the wild and that I made myself. Furthermore, I give general advice how to remain (somewhat) undetected when scraping.

Note: Many large websites actually don't sanction scraping that much. I would count Google and Amazon to the sites that only moderately prevent scraping. The reason is obvious: Those sites actually massively profit when other people/companies are using their data in their products. Google and Amazon are heavy players when it comes to E-Commerce and Online Marketing. So they both have an incentive to allow third-party-tools to access their platforms to a certain degree.

Other sites such as Instagram and LinkedIn are much more aggressive when it comes to blocking scrapers. They'll ban ill behaving user agents on the first suspicious activity. Websites such as LinkedIn are practically impossible to use without having an account.

## Common Mistakes in Scraping

### 1 - Don't Lie on the User Agent

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

### 2 - Don't scrape too aggressively

This is another common mistakes I see people making. Don't scrape too aggressively. After all, you are interested in public data, you don't want to launch a Denial of Service attack against a website. So please be considerate. 

Furthermore, if your scraping becomes a major pain for the websites administrators, they will be extra careful to block ALL illegitimate traffic.

So it's better to throttle your scraping and to stay below the radar.

### 3 - Don't use AWS Lambda or any other serverless platform for scraping

I am very guilty of this one. I used AWS Lambda for a long time. I could scrape millions of Google SERPs within days on AWS Lambda (even without any proxies and just the AWS Lambda public IP address pool). 

There very [mature modules](https://github.com/alixaxel/chrome-aws-lambda) that ship binaries specifically compiled for the AWS Lambda runtime.

However, there are just too many disadvantages when scraping with AWS Lambda:

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

### 4 - Learn from mistakes from professional scraping services

There are many professional scraping services that you can research. They have learned over the years and you can see how they camouflage they scrapers. Sometimes even the professional services make mistakes though.

[*ScrapingBee*](https://scrapingbee.com)

For example they set the user agent to either 

1. `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36`
2. `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36`

but they forget to spoof the `navigator.platform` property accordingly. It is still set to `"platform": "Linux x86_64"`. Obviously, that is very suspicious and would get flagged by many bot detection companies.

[*ScraperApi*](https://www.scraperapi.com/)

This is another commercial scraping service. Their scrapers also exhibit some weird behavior.

For example, their scraping browsers have the timezone set to `Etc/Unknown`. This is very obscure.

You can obtain the timezone with the JavaScript snippet `(new window.Intl.DateTimeFormat).resolvedOptions().timeZone`. 

Furthermore, the ScraperApi scrapers have no WebGL support. It is not possible to obtain the video card settings.

Usually, normal browsers have a video card such as:
 
```
 "videoCard": [
    "Intel Inc.",
    "Intel Iris OpenGL Engine"
  ],
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

### 5 - To be done.


### 6 - To be done.

