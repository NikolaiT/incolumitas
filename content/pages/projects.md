Title: Projects
Date: 2013-12-27 14:27
Modified: 2022-02-18 18:28
Author: Nikolai Tschacher
Slug: projects
Status: published
Sortorder: 0

My main development is done in Node.js, Typescript and Python. I use Django for web development and Celery/Redis for asynchronous tasks. Nowadays, I mostly program in modern JavaScript, because it is the most used language when developing data extraction / crawling tools.

Some JavaScript frameworks I used a lot recently: [React](https://reactjs.org/), [Ant.design](https://ant.design/), puppeteer, express, serverless. For my master thesis, I used a lot of good old C, because it involved fuzzing with [AFL](https://github.com/google/AFL) and [LibFuzzer](https://llvm.org/docs/LibFuzzer.html). I know a bit of web design too, but tend to avoid it in favor of CSS frameworks such as bulma.io, bootstrap or ant.design.

My most recent projects are:

- [TCP/IP Fingerprinting](https://incolumitas.com/pages/TCP-IP-Fingerprint/) - Similar to the TLS fingerprinting technique, different operating systems use different TCP/IP stack configurations which are advertised in the initial SYN packet in a TCP/IP three-way handshake. By correlating the HTTP User-Agent with OS-specific TCP/IP header fields, it is possible to deduce the operating system by looking exclusively at the TCP/IP layer. The research has been released as [zardaxt.py](https://github.com/NikolaiT/zardaxt).
- [TLS Fingerprinting](https://incolumitas.com/pages/TLS-Fingerprint/) - In this project, I investigate several different approaches how to fingerprint TLS 1.2 and TLS 1.3 connections. I make use of existing research and deep-dive into TLS fingerprinting techniques and try to get one step further than existing solutions such as Saleforce's [JA3 and JA3S TLS fingerprint](https://github.com/salesforce/ja3) and the [Cisco TLS fingerprint](https://github.com/cisco/joy) have gone.
- [Proxy/VPN Detection Test Site](https://bot.incolumitas.com/proxy_detect.html) - In this project, I make use of [several different methods](https://incolumitas.com/2021/10/16/7-different-ways-to-detect-proxies/) to detect proxies and VPN's. There is no exact method, but the accumulation of independent tests gives a rather good heuristic if a visitor of a website is using a proxy to hide their true IP address.
- [Bot Detection Test](https://bot.incolumitas.com) - This is a [puppeteer](https://github.com/puppeteer/puppeteer)/[playwright](https://github.com/microsoft/playwright) bot detection page. It implements [widely known bot detection tests](https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth). This page is constantly under development and tries to incorporate the most recent bot detection techniques.
- [Breaking Google's Audio ReCaptcha](https://github.com/NikolaiT/uncaptcha3) - In this project, I make use of a method from 2019 that demonstrates how to solve the audio ReCaptcha with Googel's own Speech to Text API. This method still works, which is quite astonishing.
- [Detecting AdBlock with JavaScript only](https://www.npmjs.com/package/adblock-detect-javascript-only) - This tiny library detects when website visitors have an active AdBlock plugin installed. It is based on JavaScript only and thus is very easy to setup. The approach is very reliable and will very likely don't cease to work.
- [Distributed crawling infrastructure](https://github.com/NikolaiT/Crawling-Infrastructure) - Distributed crawling infrastructure running on top of serverless computation, cloud storage (such as S3) and sophisticated queues. This software allows you to crawl and scrape the Internet in scale. It supports basic crawling via http as well as sophisticated crawling with the help of a heavily customized headless chrome browser controlled via puppeteer.
- [struktur.js](https://github.com/NikolaiT/struktur) - A way to extract structured information from any visually rendered HTML page. This project aims to deprecate the scraping of websites with CSS selectors and Xpath queries. I don't have enough time to push it forward, but I like the idea a lot and I think it has a tremendous amount of potential.

Some old/deprecated projects of mine:

- [scrapeulous](https://scrapeulous.com/) - A scraping platform, aiming to solve many annoying tasks when developing scrapers/crawlers. Currently, scrapeulous focuses on search engine scraping. In the near future, scraping of any website will be possible. *Discontinued*
- [se-scraper](https://github.com/NikolaiT/se-scraper) - The successor of GoogleScraper that builds on top of puppeteer, written in JS. *Discontinued*
- [GoogleScraper]({filename}/pages/googlescraper-py.md) deprecated since 2018, gathered 2200 stars on Github and taught me that there is a demand for data extraction and scraping.
- [SVG Captcha]({filename}/pages/svgcaptcha.md) A captcha implementation with SVG.
- [Lichess Bot]({filename}/pages/lichess-bot.md) based on Stockfish engine
