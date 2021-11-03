Title: So you want to Scrape like the Big Boys? 🚀
Date: 2021-11-03 23:48
Category: Security
Tags: scraping, industrial level scraping, big boys
Slug: so-you-want-to-scrape-like-the-big-boys
Summary: What it really takes to scrape without getting detected.
Author: Nikolai Tschacher
Status: Published

## Intro

Let's do some thinking, shall we?

When I used to run a scraping service, I managed to scrape at most a couple of million Google SERP pages per week. But I never ever purchased proxies from proxy providers such as [Brightdata](https://brightdata.com/), [Packetstream](https://packetstream.io/) or [Oxylabs](https://oxylabs.io/).

Why? 

Because I could not fully trust other people using those services. What if I share proxy servers with outright criminals that do more than some SERP scraping? Furthermore, those proxy services are quite *pricey*, and me being a stingy German, I didn't possibly see a reasonable way of this combination working out.

<figure>
  <img src="{static}/images/work different.png" alt="farm man" />
  <figcaption>It had to be said.</figcaption>
</figure>

So how did I manage to scrape millions of Google SERP's?

I used [AWS Lambda](https://aws.amazon.com/lambda/), put Headless Chrome into an [AWS Lambda function](https://aws.amazon.com/getting-started/hands-on/run-serverless-code/) and used [puppeteer-extra](https://github.com/berstend/puppeteer-extra) and [chrome-aws-lambda](https://github.com/alixaxel/chrome-aws-lambda) to create a function that automatically launches a browser for 300 seconds that I can solely use for scraping.

Actually, I could have probably achieved the same with plain `curl`, because Google really doesn't put too much effort into blocking bots from their own search engine (they mostly rate limit by IP). But I needed a full browser for other projects, so there was that.

Anyhow, AWS gives you access to 16 regions all around the world (are there even more regions in the meantime?) and after three AWS Lambda function invocations, your function receives a new public IP address. And if you concurrently invoke 1000 Lambda functions, you will bottom out at around 250 public IP addresses. And then you have 16 regions, which gives you around `16 * 250 = 4000` public IP addresses at any time when using AWS Lambda.

I tried the same with [Google Cloud Platform](https://cloud.google.com/), but funnily enough, Google blocks their own cloud infrastructure much more aggressively compared to traffic from AWS.

**But I digress.**

The above setup is not good. It will work for scraping Google, because Google *wants* to be scraped to a certain extent.

But it will never work against well protected websites who employ protection from anti bot companies such as from [DataDome](https://datadome.co/), [Akamai](https://www.akamai.com/) or [Imperva](https://www.imperva.com/) (there are more anti bot companies, don't be salty when I didn't name you, okay?).

Those companies employ ill-adjusted individuals that do nothing else than look for the most recent possibilities to fingerprint browsers, find out if a browser [lies about it's own configuration](https://github.com/abrahamjuliot/creepjs) or exhibits artifacts that don't pertain to a humanly controlled browser. When normal people are out drinking in the pub on Friday night, these individuals invent increasingly bizarre ways to fingerprint browsers and detect bots:

1. Browser Red Pills 
2. Browser Based Port Scanning
3. Google Picasso
4. Font Fingerprinting
5. TCP/IP Fingerprinting
6. Browser based Crypto Challenges - Proof of Work
7. Generic Browser Fingerprinting
8. TLS Fingerprinting
9. WebGL Fingerprinting
10. WebRTC real IP detection
11. Behavioral Classification
12. Gyroscope API querying (device movement / rotation detection)
13. ....

I kid you not, there are millions of ways to detect if a browser is being controlled by a bot or not. It's insanely complex and almost all bot architectures are to a degree vulnerable to detection.

The main reason is simple economics: In order for 

But fuck that, right?

Let's propose a scraping architecture that is not as easily detectable.

## An undetectable and massively scalable scraping infrastructure

1. The second most important rule about evading anti bot companies is: **You shall not lie about your browser configuration**.
2. And the most important rule is: **You shall only lie about your browser configuration if nobody catches you**.