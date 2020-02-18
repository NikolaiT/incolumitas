Title: Discontinuation of GoogleScraper
Date: 2018-12-24 18:00
Modified: 2018-12-24 18:00
Category: GoogleScraper
Tags: discontinuation, GoogleScraper, scraping
Slug: discontinuation-googlescraper
Author: Nikolai Tschacher
Summary: Discontinuation of GoogleScraper in favor of https://www.npmjs.com/package/se-scraper

in this blog post I am going to briefly outline the reasons why I decided to stop 
developing the GoogleScraper Python3 module.

1. Python is not the language/framework for modern scraping. Node/Javascript is. The reason is puppeteer. puppeteer is the de-facto standard for controlling and automatizing web browsers (especially Chrome). GoogleScraper however uses Selenium. Selenium is kind of old and outdated.
2. Scraping in 2019 is almost completely reduced to controlling webbrowsers. There is no longer any need to scrape directly on the HTTP protocol level. It's too bugy and detectable by anit-bot mechanisms. And GoogleScraper still supports raw http requests.
3. Scraping should be parallelized in the cloud or among a set of dedicated machines. GoogleScraper cannot handle such use cases without significant effort.
4. GoogleScraper's architecture is too complicated. Additionally, the code base is too bugy and long scraping jobs are notoriously unreliable. 

## https://www.npmjs.com/package/se-scraper

Instead I will maintain a small node library based on puppeteer that scrapes a range of popular search engines.

This project will never become complicated and will instead focus on small scrape jobs. If you want to scrape a 
large amount of keywords, you can pay so on [scrapeulous.com](https://scrapeulous.com/) or you can hire me directly as a programmer.

For simple use cases, https://www.npmjs.com/package/se-scraper is more than enough.

For this node module I will focus on keeping up to date with html changes of the search engines and will guarantee that basic scraping functionality is working. Large features won't be implemented however.
