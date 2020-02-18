Title: Tutorial: Youtube scraping with puppeteer
Date: 2018-10-29 13:58
Modified: 2018-10-29 13:58
Category: Scraping
Tags: Youtube, Video, Scraping
Slug: youtube-puppeteer-scraping
Author: Nikolai Tschacher
Summary: How to scrape youtube videos using puppeteer

In this blog post I am going to show you how to scrape YouTube video data using the handy puppeteer library. Puppeteer is a Node library
which uses the DevTools Protocol in order to control chrome browsers (Or any other browser that implements the DevTools Protocol). 

### Quickstart

If you are short in time, just download the library from the [github repository](https://github.com/NikolaiT/youtube-scraping) and follow the instructions there.

### You are not a programmer?

If you are not a programmer, you can still scrape data from youtube (any many other search engines).
I created a service called [Scrapeulous.com](https://scrapeulous.com/) where you can submit keyword files that are then scraped for you.

### Why would you want to scrape YouTube videos?

If you are a **content creator**, you might be interested in your competitors and want to know what kind of videos they are publishing.
And maybe there are 500 video creators in your niche and you cannot monitor all their content by yourself. Therefore, you want to automate
this task. You scrape all new videos from all your competitors and then you look for certain keywords in the title and video description.

With this information you can determine if your competitors are

+ stealing content from you
+ having success with a certain keyword
+ use better marketing strategies than you

If you are a **scientist**, you might be interested in the spreading of fake news for example. You want to monitor the sources of fake news. After some 
hard work you compiled a list of fake news channels and your next step is to monitor this content periodically. To do so, you are interested
in scraping every new published video. Then you can determine from where the news originated.

If you have a list of your **favourite music videos**, you need the youtube urls in order to download the videos. Using the youtube API is not always a pleasure, since
it is a little complex. Therefore this tools helps you to quickly search the links that you need.

There are many other scenarios that motivate collecting information from YouTube...You just need to be creative enough!

### What tools do you need?

We are going to develop the YouTube Scraper in NodeJS. My version is:
```
$ node -v
v10.12.0
```

Lets make a project folder.

```
mkdir youtube-scraping && cd youtube-scraping
```

Init a new node project with:

```
npm init
```

Then we are ready to go. First of all we need to install some third party libraries in order for our code to work.

Install puppeteer:

```
npm i puppeteer
```

Install cheerio:

```
npm i cheerio
```

Now our directory should look similar to this:

```
drwxr-xr-x 57 nikolai nikolai  4096 Okt 29 14:20 node_modules/
-rw-r--r--  1 nikolai nikolai   685 Okt 29 14:20 package.json
-rw-r--r--  1 nikolai nikolai 16500 Okt 29 14:20 package-lock.json
```

###  Our scraping program

We are going to create two files: `youtube.js` which is the library that enables us to scrape
youtube. We will not go through every line since the code should be more or less
self explanatory. Here is the code of `youtube.js`:

```javascript
const cheerio = require('cheerio');

module.exports = {
    scrape_youtube: scrape_youtube,
};

const all_videos = new Set();

const sleep = seconds =>
    new Promise(resolve => setTimeout(resolve, (seconds || 1) * 1000));

async function scrape_youtube(browser, keywords) {

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto('https://www.youtube.com');

    try {
        await page.waitForSelector('input[id="search"]', { timeout: 5000 });
    } catch (e) {
        return results;
    }

    const results = {};

    // before we do anything, parse the results of the front page of youtube
    await page.waitForSelector('ytd-video-renderer,ytd-grid-video-renderer', { timeout: 10000 });
    let html = await page.content();
    results['__frontpage__'] = parse(html);

    for (var i = 0; i < keywords.length; i++) {

        keyword = keywords[i];

        try {
            const input = await page.$('input[id="search"]');
            // overwrites last text in input
            await input.click({ clickCount: 3 });
            await input.type(keyword);
            await input.focus();
            await page.keyboard.press("Enter");

            await page.waitForFunction(`document.title.indexOf('${keyword}') !== -1`, { timeout: 5000 });
            await page.waitForSelector('ytd-video-renderer,ytd-grid-video-renderer', { timeout: 5000 });
            await sleep(1);

            let html = await page.content();
            results[keyword] = parse(html);

        } catch (e) {
            console.error(`Problem with scraping ${keyword}: ${e}`);
        }
    }

    return results;
}

function parse(html) {
    // load the page source into cheerio
    const $ = cheerio.load(html);

    // perform queries
    const results = [];
    $('#contents ytd-video-renderer,#contents ytd-grid-video-renderer').each((i, link) => {
        results.push({
            link: $(link).find('#video-title').attr('href'),
            title: $(link).find('#video-title').text(),
            snippet: $(link).find('#description-text').text(),
            channel: $(link).find('#byline a').text(),
            channel_link: $(link).find('#byline a').attr('href'),
            num_views: $(link).find('#metadata-line span:nth-child(1)').text(),
            release_date: $(link).find('#metadata-line span:nth-child(2)').text(),
        })
    });

    const cleaned = [];
    for (var i=0; i < results.length; i++) {
        let res = results[i];
        if (res.link && res.link.trim() && res.title && res.title.trim()) {
            res.title = res.title.trim();
            res.snippet = res.snippet.trim();
            res.rank = i+1;

            // check if this result has been used before
            if (all_videos.has(res.title) === false) {
                cleaned.push(res);
            }
            all_videos.add(res.title);
        }
    }

    return {
        time: (new Date()).toUTCString(),
        results: cleaned,
    }
}
```

### Using the library

Now it is time to call the library and scrape some keywords and find all the videos for those 
keywords.

Create a file `index.js` and paste the following code:

```javascript
const puppeteer = require('puppeteer');
const youtube = require('./youtube');

try {
    (async () => {

        let keywords = [
            'stupid prank',
            'scraping youtube',
            'climbing lothse',
            'incolumitas.com',
        ];

        const browser = await puppeteer.launch();
        let results = await youtube.scrape_youtube(browser, keywords);
        console.dir(results, {depth: null, colors: true});

        await browser.close();

    })()
} catch (err) {
    console.error(err)
}
```

You can enter whatever keywords you want in the `keyword` array.

Start the scraping with the following command:

```
node index.js
```

this yields me the [following results in JSON format](/data/youtube-scraping.json).

### The Scraper Source Code

The scraper can be found [on this github repository](https://github.com/NikolaiT/youtube-scraping).

In order to run the scraper, you need to first clone the repository.

```
git clone https://github.com/NikolaiT/youtube-scraping
```

Then install dependencies:

```
npm install
```

Create a source file in the directory you downloaded the package and
add the following code.

```javascript
const puppeteer = require('puppeteer');
const youtube = require('./youtube');

try {
    (async () => {

        let keywords = [
            'scrapeulous.com',
            'scraping youtube',
            'stupid prank',
        ];

        const browser = await puppeteer.launch();
        let results = await youtube.scrape_youtube(browser, keywords);
        console.dir(results, {depth: null, colors: true});

        await browser.close();

    })()
} catch (err) {
    console.error(err)
}
```
