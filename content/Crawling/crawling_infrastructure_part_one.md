Title: Crawling Infrastructure - Introduction
Date: 2020-05-18 21:29
Category: Crawling
Tags: Crawling, Distributed Computing, Cloud, Web Bots
Slug: crawling-infrastructure-part-1
Author: Nikolai Tschacher

In this blog article I will introduce my most recent project: [The distributed crawling
infrastructure](https://github.com/NikolaiT/Crawling-Infrastructure) which allows to crawl any website with a low-level Http library or a fully fledged chrome browser configured to evade bot detection attempts.

This introduction is divided into three distinct blog articles, because one blog article would be too large to cover this huge topic.

1. *(This article)* The first part of the series motivates the development of the crawling infrastructure, introduces the architecture of the software and demonstrates how the crawling backend works at a high level.
2. The second part covers the installation of the distributed crawling infrastructure within the AWS cloud infrastructure and tests the freshly deployed stack with a test crawl task.
2. In the third part of this tutorial series, a crawl task with the top 10.000 websites of the world is created. The downloaded Html documents are stored in s3. For the top 10.000 websites, we use the scientific [tranco list](https://tranco-list.eu/): A Research-Oriented top sites ranking hardened against manipulation. As a concluding task, we run business logic on the stored Html files. For example, we extract all urls from the Html documents or we run analytics on the `<meta>` tags found in the `<head>` section of the documents.

## Why would I even need a distributed crawling infrastructure?

You most likely **do not need** a distributed crawling infrastructure. If your requirements are to scrape a single website, you can create a simple script that uses `lxml` and `beautifulsoup` in the case you program with Python. Alternatively, you could write a Nodejs program that uses [puppeteer](https://github.com/puppeteer/puppeteer) if you need to orchestrate a real browser. That approach is sufficient for most cases.

However, if you are already an experienced scraping script author, you might have encountered the following limitations:

1. If you run the crawling script on your development machine, you will **need to keep the machine running as long as the task is not finished.** That is annoying.
2. In case you are using an VPS to run your crawling script, you don't have to worry about the execution time of your crawling program. However, your VPS scales vertically. What if you want to control more than three browsers at the same time? This becomes increasingly more expensive in terms of RAM and CPU costs. Therefore, running a large crawling operation on one single server instance is not scaleable.
3. When you store the crawled data in a database, disk space becomes an issue if you are launching large tasks. Therefore, at some point you will need to outsource storage to the cloud.

Summarized, if you want to create multiple, long running and computationally expensive crawling jobs in a concurrent fashion, the distributed crawling infrastructure presented in this article might be for you.

## The problems that the distributed crawling infrastructure solves

In the following sections, I outline some of the problems and hurdles the crawling infrastructure tackles.

### Handling of large data-sets

The crawling infrastructure stores crawled data in compressed form in the cloud. Currently, the most used storage solution is AWS S3. But you can store the crawled data in any cloud storage of your choice.

That way you don't have to worry about local storage restrictions.

### Dynamic allocation of crawling backends

The crawling infrastructure gives you full choice over the computational resource that executes the crawling code. By default, the crawling worker is executed on AWS Lambda instances, but you could use any other backend such as

1. AWS EC2 Spot instances
2. Azure cloud functions
3. Digital Ocean Droplets

### Detection of the crawling

A huge contribution of the distributed crawling software is the attempt to obfuscate the automated crawling from bot detection approaches. For that reason, the crawling infrastructure uses the puppeteer controlled chromium browser and configures the browser in such a way that makes it hard for anti-bot techniques and fingerprinting scripts to detect the browser.

A wide array of techniques are used, such as user agent obfuscation, changing of http headers such as Accept-Language, proxy support, setting of chrome command line parameters and much more.

### Separation of Concerns

Due to it's design into five distinct components, it is straightforward to debug the crawling infrastructure.
Distributed system are complicated by design, therefore, separating such a software in individual components reduces this complexity.

## Requirements for installing & controlling the crawling infrastructure

Running your own scaleable crawling infrastructure is only possible if you have access to the following resources:

1. You own a AWS/Azure/Google Cloud account
2. You have the requirements to execute long running crawl tasks over hundred thousand and millions of items
3. You know the implications of what you are doing

In order to follow this tutorial, you will at least **require an
AWS account**. We will make use of the following AWS services:

+ **AWS Lambda** as crawling backend
+ **AWS S3** to store crawled Html data
+ An **AWS EC2** instance used as a master server that schedules the crawl task and hosts the mongodb that we use a queue. This is the central part of the crawling infrastructure.

## The architecture of the crawling infrastructure

The whole codebase is written in Typescript, which eliminates some of the problems that large nodejs projects inevitably have when they begin to grow.
The architecture of the crawling infrastructure is divided into five parts.

1. **The Api** that accepts, lists, deletes and manages crawl tasks.
2. **A scheduler** that polls the database for pending crawl tasks and launches worker instances if there is more crawling work to do.
3. **A mongodb database instance** that stores crawling metadata and the items to be crawled. No actual results will be stored in the database, only crawling metadata. The database needs to be remotely accessible.
4. **The crawling worker**. When a crawling worker is launched, it grabs items from the database and makes progress on them. The crawling worker implements all the logic responsible for launching a browser, making it undetectable and executing the crawling logic.
5. **The crawling function**. This is the actual logic of what actually should be done on the crawled website. For example, if you want to scrape Google, the [Google Scraper]() would be chosen as a crawling function. On the other side, if you only want to render & store the html of a website, a [simple render]() crawling functions suffices.

The architecture of the crawling infrastructure is quite complex and is summarized in the diagram below:

![architecture of the crawling infrastructure](https://github.com/NikolaiT/Crawling-Infrastructure/raw/master/docs/diagram/arch_diagram2.png "crawling infra arch")


## Practical part: Launching the first crawl task

Now that we have introduced the crawling infrastructure from a theoretical point of view, it's time to start with something practical: We will test the **crawler** and then create the first simple crawl tasks locally.

Therefore, we won't create a distributed infrastructure just yet. That is saved for the two other parts of this tutorial.

 In order to follow this excursion, you will need to have installed the following software:

1. Nodejs, check out the [installation instructions](https://linuxize.com/post/how-to-install-node-js-on-ubuntu-18.04/)
2. `typescript`, installed globally with `sudo npm install -g typescript`
3. docker, see Ubuntu 18.04 [installation instructions](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)
4. `npm` and `yarn`

If that is the case, go to cozy place on your local file system and download the crawling infrastructure project with the command:

```bash
git clone https://github.com/NikolaiT/Crawling-Infrastructure.git

cd Crawling-Infrastructure/
```

In order to test the crawler, we use the following commands to create the docker crawler image.

```bash
cd crawler/
npm install

# install & compile lib
cd ../lib
npm install
tsc

cd ../crawler
./build.sh
```

After the image was successfully built, you can run the integration test with the following command:

```bash
mocha --timeout 300000 -r ts-node/register test/integration_tests.ts
```

The mocha tests should run successfully. If that is the case, we may proceed with running some local crawl tasks against the running docker image.


### Testing the crawler locally

Now that we have successfully tested the crawler locally, let's see if we can actually crawl a simple url with it.

First launch the docker crawler image in one terminal window with the following command:

```bash
docker run -p 4444:4444 --env PORT=4444 tschachn/crawl_worker:latest

[DOCKER] Starting X virtual framebuffer using: Xvfb :99 -ac -screen 0 1280x720x16 -nolisten tcp
[DOCKER] Starting worker server
CrawlWorker[6c279a53f03d] with pid 9 listening on port 4444
```

And now on a second terminal window, confirm that the crawler docker image is running by issuing the following command:

```bash
curl http://localhost:4444/
{
  "status": 200,
  "message": "Welcome to CrawlWorker running on 6c279a53f03d",
  "version": "1.1.5",
  "author": "Nikolai Tschacher <contact@scrapeulous.com> (https://scrapeulous.com)"
}
```

Everything works fine! Now it's time to crawl a simple website that reflects our IP address. As you can see we pass an empty aws configuration.

```bash
curl http://localhost:4444/invokeRequestResponse \
  -H "Content-Type: application/json" \
  -d '{"API_KEY": "kfTP6E7GgDTtIBZnUQq4skrHGWcuPe1Z",
       "aws_config": {
         "AWS_ACCESS_KEY": "",
         "AWS_SECRET_KEY": "",
         "AWS_REGION": "",
         "AWS_BUCKET": ""
       },
       "local_test": true,
       "function_code": "class Get extends HttpWorker { async crawl(url) { let result = await this.Got(encodeURI(url)); return result.body; } }",
       "items": ["https://ipinfo.io/json"]}'
```
