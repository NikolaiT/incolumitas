Title: A lot of work to do for GoogleScraper in the future  and request for comments!
Date: 2015-03-01 12:52
Author: Nikolai Tschacher
Category: Googlescraper
Tags: Software, Python, Programming, Googlescraper
Slug: a-lot-of-work-to-do-for-googlescraper-in-the-future-and-request-for-comments
Status: published

Hello dear readers

I get a lot of mail regarding questions about GoogleScraper. I really
appreciate them, but at some stage I cannot answer them anymore. In the
last weeks I didn't have a lot of time (and motivation I must admit) to
put into GoogleScraper.

The reason is, that I am still unconfortable with the architecture of
GoogleScraper. There are basically two ways to use the tool:

-   As a command line tool
-   From another program over the API (programming approach)

and furthermore there are 3 very different modes GoogleScraper runs in:

-   http mode
-   selenium mode which again can be divided in Firefox, Chrome and
    PhantomJS selenium browsers
-   asynchronous mode

whereas I think that selenium is the hardest to work with (very buggy
and complex to program in). This leads to a complex software
architecture, mainly because the two operational modes (CLI tool and
API) have *different priorities of how to handle exceptions*.

The CLI tool should be VERY robust and it should to everything it can to
continue scraping with the remaining ressources (like proxies, RAM, when
lots of selenium instances become an issue, networking bandwith, ...),
because the user cannot handle these problems by himself when he calls
GoogleScraper from the command line. It's better to just keep running
until we just can't anymore (no more proxies, networking failure, ...)

The API on the other hand should return the results of individual
workers as soon as possible to the caller. Maybe, the API user even
wants to stop GoogleScraper as soon as some sort of problem appears
(like: A proxy is detected, some sort of issue appears, ...)

These are two fundamentally different approaches and to guarantee the to
work both, a very sophisticatd middleware architecture is needed. To be
honest, in the beginning of GoogleScraper I wasn't aware of these
differences.

### Which tools to use?

Another issue are the technology I currently use. I realized from
discussions with some people that were interested in GoogleScraper, that
there is a lot of good and stable software out there that could help me.
Right now I use hand crafted caching to store scraped data. But honestly
it would be much faster and less error prone to switch to Redis or
similar technologies. [The python redis
client](https://github.com/andymccurdy/redis-py "this python redis client")
looks very promising and would help me improve the performance of
GoogleScraper immensly.

I am quite sure that there is other software that I *should* use but am
currently unaware of. Please kind people: **Shoot me a short comment if
you have some hints and ideas what software thing I must absolutely
use!**

Before I begin programming I want to plan ahead and define some
milestone I want to reach. Currently I am reading a book about test
driven development and I feel that I have to read at least these two
books before I continue with GoogleScraper:

-   [Operating system
    book](http://pages.cs.wisc.edu/~remzi/OSTEP/ "operating systems book")
-   [Test driven development
    book](http://chimera.labs.oreilly.com/books/1234000000754/index.html "test driven development")

Otherwise I will make other mistakes and I will never arise at a stable
and mature software. And I think the people would like to use such a
tool. I got 450 stars on github over the last year and I feel like there
is a lot of interest in this area. And I want to be the man who delivers
such a tool :)

### Please help me!

This may sound a bit hypocrite because all of you already helped me a
great deal (and I still have around 30 issues to resolve on Github), but
I especially need some tips about the architecture and ideas how to
design the framework of GoogleScraper. Leave some comments please :)

Best Regards

Nikolai

**This post is not completed yet. I will update it and use it as a rough
outline for improvements of GoogleScraper**
