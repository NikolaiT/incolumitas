Title: Scraping search engines in 2019
Date: 2019-2-4 18:00
Category: Scraping
Tags: puppeteer, scraping, modern
Slug: scraping-search-engines-in-2019
Author: Nikolai Tschacher
Summary: Modern scraping now is mostly done with real browsers, configured to behave like real humans.

When I started developing a simple Python script in 2012, which later would become the open source software [GoogleScraper](https://github.com/NikolaiT/GoogleScraper), I needed to stay up to date with the latest web technology. Since then, I developed a love-hate relationship with web scraping. One the one side, being able to scrape websites in large quantities gives you instant access to the most up-to-date information of the world. On the other side, web scraping is inherently a unstable business, because you are a third party source and rely on the provider (such as Google or Bing). The provider can change their markup at every time, ban IP ranges at will and make your life extremely annoying.


### Web Crawling

Search engine scraping can be considered crawling of search engines. The result is a meta search engine. Search engines themselves are huge web scrapers. But instead of scraping, they call the process *web crawling*. There are many open source web crawlers such as [Apache Nutch](http://nutch.apache.org/) or the [Storm Crawler](http://stormcrawler.net). They all are capable of indexing a complete web page by recursively following all the links encountered during the crawling process. Usually, those programs respect the crawling policy determined by the `robots.txt` file and try to avoid being a heavy burden on the crawled page.

If you as an individual (or as a small company) are seriously interested in deploying your own crawler for many million URL's, you should probably realize that you are dealing with Big Data problems. This almost instantly means a whole new programming paradigm called the [MapReduce programming model](https://en.wikipedia.org/wiki/MapReduce) and involves coordinating resources distributed on potentially many different machines. This is expensive and the learning curve is not straightforward. Even though I have a computer science degree (M. Sc.), I would not start such a project without precisely specifying the goals and steps in such a project and considering the possibility that it will be too hard/expensive for a small team (pessimistic view). Additionally, such projects almost always involve spending money for hardware infrastructure (such as Amazon EC2 instances) to launch your crawl.

Therefore, it is advised to start a project that depends on web crawling by analyzing the [CommonCrawl](http://commoncrawl.org/) project beforehand. They are crawling the web since 10 years and make their crawling corpus available for free. This enables you to bootstrap your project idea and go right to the step where you determine whether your business idea is still valid with real world data.

Then there is for example [scrapy](https://scrapy.org/), a large and well maintained scraping/crawling library written in Python. Scrapy is a mix between crawler and scraping framework. They abstract the whole crawling process into a powerful framework. Scrapy for example has a downloader middleware that allows you to plug in random proxy selection mechanisms in order to anonymize the individual requests to the target site.

### Port Scanning

Then there are other amazing open source programs such as [ZMap](https://zmap.io/) or [Masscan](https://github.com/robertdavidgraham/masscan) which allow you to port scan the entire internet within hours (yes, the whole `2^32` IP addresses). Those port scanners can be considered crawlers for lower level TCP/IP protocols. Maybe your business idea is to create a low level meta search engine that answers queries such as

* How many hosts with open port 80 have nginx version X installed?
* What percentage of real world TLS/SSL implementation use the ellipitic curve `NIST P-256` ?
* How many webservers have a `phpinfo.php` laying around the root of the webserver?

To answer these questions, you need to port scan a significant subset of the complete Internet.

Those questions are for example extremely interesting for security researches (as well as blackhat hackers).

### Scraping Search Engines

In the case of [scrapeulous.com](https://scrapeulous.com/), we have specialized in scraping a representative set of search engines such as Google, Bing, Duckduckgo and others.

In our opinion, it is actually a shame that such a small amount of companies (Google, Facebook, Twitter, Microsoft) almost completely monopolizes the whole Internet. 

They can determine which user (by IP) from which region (Geo Location) will see what content of their services. The can determine the usage limits of viewing their pages. 

And they are only interested in human users of course. They don't want too feed bots with information that costs them valuable resources. 

The interest in real human beings is of course understandable. Real human beings can make purchase decisions, are easily influenced by advertisements and produce valuable data.

This exactly is the motivation for scraping search engines. 

We at [scrapeulous.com](https://scrapeulous.com/) thrive to imitate real human search behavior as closely as possible. For this reason, we follow those guidelines that constitute **best practices in modern web scraping from 2019**:

1. The customer must be able to launch a scrape job over many keywords (quantity).

2. The region from where the searches originate should be consistent. This means that a scrape job should have the same IP address from the same geographical region/country.

3. Scraping should be done by launching real browsers. For example [scrapeulous.com](https://scrapeulous.com/) uses the well maintained browser automation library [puppeteer](https://github.com/GoogleChrome/puppeteer)

4. It should be impossible to detect that the search originated from a bot. This is achieved by randomizing requests with delays, valid user agents and following guidelines such as the one [published here](https://intoli.com/blog/not-possible-to-block-chrome-headless/).


### Use cases of search engine scraping

Honestly, using a service such as [scrapeulous.com](https://scrapeulous.com/) is motivated by the same reasons why we use search engines like Google in our everyday life. The only difference is that [scrapeulous.com](https://scrapeulous.com/) allows to search in large quantities.

The most prominent use cases are the following:

* Scientist need data and usually they need a lot of data for empirical studies. Searching 10k keywords manually will take you several days.

* Marketing and business analysts need to know how, and through which keywords their sites are discovered. By creating many different keyword combinations and analyzing the results algorithmically, it's much easier to derive knowledge.

* Often business decision depend on data published in search engines. Scraping search engines makes a lot of sense in those cases.