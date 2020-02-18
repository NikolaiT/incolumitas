Title: Scraping Amazon Reviews using Headless Chrome Browser and Python3
Date: 2018-10-03 17:02
Modified: 2018-10-03 17:02
Category: Scraping
Tags: Amazon, Reviews, Scraping
Slug: scraping-amazon-reviews
Author: Nikolai Tschacher
Summary: Tutorial that teaches how scrape amazon reviews

In this tutorial we are going to learn how to scrape Amazon Reviews using Python and a headless chrome browser.

### Why scraping amazon reviews?

There are many reasons why it is interesting to scrape reviews of a amazon product?

For example you want to know if somebody spams fake reviews and you want to conduct a content analysis. In order to achieve this, you
are going to need the reviews as text data to launch your analysis.

Another reason is to find out what kind of reviews people are upvoting the most and then copy the style, structure and approach of this reviews
on your own products. The scraper also collects the number of upvotes for each review.

There are indefinitely more reasons why scraping review data might be a interesting idea. A lot of them have to do with business intelligence and
marketing analysis.

### Scraping reviews with headless browsers

Of course one could scrape reviews by using low level http clients like **curl** or the **requests** library, but this makes it much easier
for Amazon to detect scraping efforts. Therefore the best solution is to mimic real users by using real browsers.

This led us to the choice of using headless chrome and the chromedriver for the automatic testing framework selenium.

With this stack (headless chrome, selenium, python) we will build our scraper.

###  How to prevent being banned by Amazon?

There are several methods how a service provider like Amazon detects scraping bots.

1. Requests originate from limited pool of IP addresses.
2. The browser profile is always the same or similar.
3. The requests follow a similar pattern time wise.

Those three detection ways are the obvious patterns. There are many more ways to detect scraping bots, but
Amazon has a hard way of banning them, because filtering them out creates too much false positives.

So how can you prevent being banned:

1. Use a large pool of distinct IP addresses. Proxies, changing IP services, the Cloud
2. Change the user agent and identifying plugins/libraries from your browser
3. Insert random sleeps before scraping new reviews

I know from experience that **it is hard** to achieve those three points, **especially point 1**.

Therefore if you have a large scraping project **you can always hire me to launch such a scraping project for you**.
Head to the contact section of this blog and write me a email and we can discuss your projects goals.

### The Scraper Source Code

The scraper can be found [on this github repository](https://github.com/NikolaiT/scraping-amazon-reviews).

In order to run the scraper, you need to first clone the repository.

```
git clone https://github.com/NikolaiT/scraping-amazon-reviews
```

Then you need to download the headless chrome browser and the chrome driver. You can do so with this command.

```
./setup.sh
```

Now you can scrape amazon reviews by editing the file `scraper.py` and add some amazon product urls you want to have the reviews from:

```
if __name__ == '__main__':
    config = {
    "urls": [
      "https://www.amazon.de/Crocs-Crocband-Unisex-Erwachsene-Charcoal-Ocean/dp/B007B9MI8K/ref=sr_1_1?s=shoes&ie=UTF8&qid=1537363983&sr=1-1",
      "https://www.amazon.de/Samsung-UE55MU6179U-Fernseher-Triple-Schwarz/dp/B06XGS3Q4Y/ref=sr_1_4?s=home-theater&ie=UTF8&qid=1538584798&sr=1-4&keywords=tv",
      "https://www.amazon.de/gp/product/B07BKN76JS/ref=s9_acsd_zwish_hd_bw_bDtHh_cr_x__w?pf_rd_m=A3JWKAKR8XB7XF&pf_rd_s=merchandised-search-8&pf_rd_r=TM716ESMTY46877D33XM&pf_rd_r=TM716ESMTY46877D33XM&pf_rd_t=101&pf_rd_p=5f7031a3-d321-54f0-8d79-d0961244d5fa&pf_rd_p=5f7031a3-d321-54f0-8d79-d0961244d5fa&pf_rd_i=3310781"
    ]}
    main(config)
```

Then just run the scraper:

```
python src/scraper.py
```
