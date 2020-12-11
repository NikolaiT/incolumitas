Title: Projects
Date: 2013-12-27 14:27
Modified: 2020-05-17 14:01
Author: Nikolai Tschacher
Slug: projects
Status: published

My main development is done in Nodejs, Typescript and Python (using Django for web dev and Celery/Redis for asynchronous tasks). Recently, I have picked up quite a bit of modern Javascript, because it is the most used language when developing data extraction / crawling tools.

Some Javascript frameworks I used a lot: Reactjs, Ant.design, puppeteer, express, serverless.

For my master thesis, I used a lot of good old C, because it involved fuzzing with AFL and LibFuzzer.

I know a bit of web design too, but tend to avoid it in favor of CSS frameworks such as bulma.io, bootstrap or ant.design.

Currently, I am interested in creating **reliable, distributed and queue-based scraping infrastructures**, because I need them for [scrapeulous](https://scrapeulous.com/).

My most recent projects are:

- [Distributed crawling infrastructure](https://github.com/NikolaiT/Crawling-Infrastructure) Distributed crawling infrastructure running on top of serverless computation, cloud storage (such as S3) and sophisticated queues. This software allows you to crawl and scrape the Internet in scale. It supports basic crawling via http as well as sophisticated crawling with the help of a heavily customized headless chrome browser controlled via puppeteer.
- [struktur.js](https://github.com/NikolaiT/struktur) A way to extract structured information from any visually rendered HTML page. This project aims to deprecate the scraping of websites with CSS selectors and Xpath queries. I don't have enough time to push it forward, but I like the idea a lot and I think it has a tremendous amount of potential.
- [scrapeulous](https://scrapeulous.com/) A scraping platform, aiming to solve many annoying tasks when developing scrapers/crawlers. Currently (August 2019), scrapeulous focuses on search engine scraping. In the near future, scraping of any website will be possible.
- [se-scraper](https://github.com/NikolaiT/se-scraper) The successor of GoogleScraper that builds on top of puppeteer, written in JS.

A new project of mine (November and December 2018) is a introduction into machine learning. The following blog posts cover the topic:

- [Introduction to machine learning]({filename}/ML/Introduction Machine Learning.md)

Some old projects of mine:

- [GoogleScraper]({filename}/pages/googlescraper-py.md) deprecated since 2018, gathered 2000 stars on Github and taught me that there is a demand for data extraction and scraping.
- [SVG Captcha]({filename}/pages/svgcaptcha.md) A captcha implementation with SVG.
- [Lichess Bot]({filename}/pages/lichess-bot.md) based on Stockfish engine
