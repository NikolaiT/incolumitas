Title: Projects
Date: 2013-12-27 14:27
Modified: 2019-08-20 14:01
Author: Nikolai Tschacher
Slug: projects
Status: published

This page is about my business and personal projects.

My main development is done in Python, using Django for web dev and Celery/Redis for asynchronous tasks. Recently, I have picked up quite a bit of modern Javascript, because it is the most used language when developing data extraction / crawling tools. For my master thesis, I used a lot of C, because it involved fuzzing with AFL and LibFuzzer. 

I know a little bit of webdesign too, but tend to avoid it in favour of CSS frameworks such as bulma.io or bootstrap. I'd love to learn a modern web dev framework like Reactjs, but I simply don't have the time.

Currently, I am interested in creating **reliable, distributed and queue-based scraping infrastructures**, because I need them for [scrapeulous](https://scrapeulous.com/).

My most recent projects are:

- [struktur.js](https://github.com/NikolaiT/struktur) A way to extract structured information from any visually rendered HTML page. This project aims to deprecate the scraping of websites with CSS selectors and Xpath queries. I don't have enough time to push it forward, but I like the idea a lot and I think it has a tremendous amount of potential.
- [scrapeulous](https://scrapeulous.com/) A scraping platform, aiming to solve many annoying tasks when developing scrapers/crawlers. Currently (August 2019), scrapeulous focuses on search engine scraping. In the near future, scraping of any website will be possible.
- [se-scraper](https://github.com/NikolaiT/se-scraper) The successor of GoogleScraper that builds on top of puppeteer, written in JS.

A new project of mine (November and December 2018) is a introduction into machine learning. The following blog posts cover the topic:

- [Introduction to machine learning]({static}/ML/Introduction Machine Learning.md)


Some old projects of mine:

- [GoogleScraper]({static}/pages/googlescraper-py.md) deprecated since 2018, gathered 2000 stars on Github and taught me that there is a demand for data extraction and scraping.
- [SVG Captcha]({static}/pages/svgcaptcha.md) A captcha implementation with SVG.
- [Lichess Bot]({static}/pages/lichess-bot.md) based on Stockfish engine