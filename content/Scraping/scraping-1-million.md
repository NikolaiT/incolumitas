Title: Scraping 1 million keywords on the Google Search Engine
Date: 2019-9-17 23:30
Category: Scraping
Tags: puppeteer, web scraping, headless chrome, 1 million, queue, architecture
Slug: scraping-one-million-google-serps
Author: Nikolai Tschacher
Summary: Scraping one million keywords is not a easy task. There are proxy problems, big data problems and reliability issues. In this blog post, the most valuable insights are shared.

This blog post is not a practical guide on how to scrape one million keywords on Google. It rather presents a collection of thoughts on technical issues that have been encountered during the journey of scraping 1 million SERP's on Google. Different possible scraping architectures and methodologies are discussed as well.

## Problems encountered when scraping 1 million Google SERP's

### The big data problem

Launching millions of http requests creates immediately a bunch of different issues. There is the problem of the **size of the crawled data**. Assuming that one request produces 50 kilobytes of data, the total amount of crawled data amounts to 50GB in size. It is annoying to store such amounts of data on the central production server (especially when processing several scrape jobs of this size), therefore it makes sense to store it in the cloud on [Nearline Storage](https://cloud.google.com/storage/docs/storage-classes). AWS S3 or GCP Storage are examples for cloud storage services. The costs to store 50GB of data are negligible, it won't cost you more than a few cents.

<figure>
    <img src="https://sloanreview.mit.edu/content/uploads/2016/11/MAG-FR-Chai-Big-Data-1200x627.jpg
" alt="big data" style="width: 100%" />
    <figcaption>Scraping produces a lot of data (Source: https://sloanreview.mit.edu/article/why-big-data-isnt-enough/) </figcaption>
</figure>


### The proxy problem

Another major problem is the issue of getting blocked by Google when repeatedly using the same IP address for the scraping process. Therefore, the ambitious scraping apprentice needs to rent either different cloud computing resources or needs to subscribe to a proxy provider such as [luminati.io](https://luminati.io/) or [intoli.com](https://intoli.com/). Web scraping is a **dirty business**. When you subscribe to a proxy service, you never know [how *clean* the proxies actually are](https://proxyway.com/guides/best-proxy-providers-for-amazon). Furthermore, using http or socks proxies usually reduces the RTT and latency, all factors that the might Google search engine considers when classifying the likelihood of the client being a annoying automated scraping process.

As a viable alternative solution to using a proxy provider is the renting of cloud computing instances. You could run your [scraping logic on Amazon AWS](https://incolumitas.com/2019/08/31/web-scraping-puppeteer-aws-lambda/#web-scraping-puppeteer-aws-lambda) or on GCP Functions. Back in June 2018, I tested how many keywords you can actually scrape with one IP address and a headless chrome browser controlled with [puppeteer](https://github.com/GoogleChrome/puppeteer) before getting blocked. This usually depends on many different factors. I tested different combinations consisting of the variables:

1. Randomly sleeping between requests
2. [Changing user agents](https://www.npmjs.com/package/user-agents) between requests
3. Different levels of concurrency (With incognito chrome browser windows)
4. Blocking certain media requests or image loading requests

It turned out that the best combination of the above variables (and a couple more) gave us up to **2806** successful requests with a single datacenter IP address from a well known cloud provider before Google blocked us. The average number of successful requests was usually between 1000 and 1500. This number would likely increase when a residential proxy is chosen.

I developed a [little library named se-scraper](https://github.com/NikolaiT/se-scraper) that allows to scrape search engines such as Google, Bing or Yandex. The library has convenient docker support and runs on Ubuntu 18.04 and newer versions. It's main purpose is to scrape the most common search engines in a robust fashion. Therefore, the library comes shipped with a lot of static tests for different Google/Bing SERP layouts.

One possible approach would be to create one large bucket on S3 that serves as data storage and create a script that automatically spawns new cloud VPS server instances via the cloud service API. Those VPS servers are billed by hour and the price for 2GB RAM is around $0.015/hour on a common cloud service provider. Assuming that each such instance manages to scrape 500 keywords in one hour before getting blocked by Google, we need to rent 1.000.000 / 500 = 2000 VPS instances. This accumulates to roughly 30 USD in infrastructure costs. 


### The task queuing problem

A central instance is required that keeps track of the keywords that have already been scraped. On [scrapeulous.com](https://scrapeulous.com/), a simple Python dictionary is used as queue that is stored as JSON file on disk and updated as soon as a scraping worker made progress. Of course Redis may also be used as in memory storage for the queue (with [persistance](https://redis.io/topics/persistence)). However, I don't see the necessity if the queue file is only updated a couple of thousand times. A modern SSD should manage that frequency without any hassle.

This central instance decides when and how a new scraping worker needs to be launched. The scraping worker accepts an array of keywords, attempts to scrape this array of keywords, uploads the results to the AWS S3 storage and notifies the central instance with the list of keywords that have been successfully scraped. The central instance updates the queue and schedules another worker. The central instance also decides how many parallel workers should make progress.

### The noise problem

Scraping is not really appreciated by many website maintainers. Therefore, the scraping infrastructure should not annoy the target website and should **hide below-the-radar**. Hence, the number of parallel scraping workers should be reduced and the scraping process must be distributed evenly over a time interval of at least 7 days in order to not create large, suspicious traffic spikes. By scraping over a time interval of at least 7 days, 5952 keywords per hour are required to be scraped, or 1.65 keywords per second. This frequency should not be suspicious for a search engine as large as Google, that handles probably hundred thousands of requests per second.

<figure>
    <img src="https://internet-governance-radar.de/assets/images/radar_2.jpg" alt="stay under the radar" style="width: 100%" />
    <figcaption>The distributed scraping should stay under the radar (Source: https://internet-governance-radar.de) </figcaption>
</figure>


### Conclusion

By scraping one million keywords, a few important things have been learned:

1. Absolutely use a **queuing based approach**, otherwise things get complicated quickly and a lot of time is lost trying to figure out what keywords were already scraped.
2. All operations should be idempotent. This means that repeatedly executing the same operation does not destroy any results. In maths: If we have a function `f(x) = y`, then `f` is idempotent if `f(f(x)) = f(x) = y`
3. **Do not piss of the scraped website**. Therefore, distribute the scraping over a larger time interval in order to avoid excess traffic or even a DoS.
4. **Divide and Conquer**: Use several scraping worker instances with distinct IP addresses from a cloud computing provider. Change the worker if the IP address is detected. Only use a cloud service provider that allows to rent computing instances on a hourly base.

If you also want to scrape 1 million keywords on any website, please contact us at [scrapeulous.com](https://scrapeulous.com/contact/).

