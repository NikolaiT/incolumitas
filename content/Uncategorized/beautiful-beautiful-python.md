Title: Beautiful, beautiful python
Date: 2014-07-11 19:35
Author: Nikolai Tschacher
Category: Uncategorized
Tags: Uncategorized
Slug: beautiful-beautiful-python
Status: published

### Hey

After a day of programming I went home to program a little bit, trying
to find a way to implement some tests for my
[GoogleScraper](https://github.com/NikolaiT/GoogleScraper "Google Scraper on Github")
project, which lacked focus for a long time. I needed to have some test
data, in my case some words to search for with the above mentioned
scraper, and once more I realized how powerful Python (or any
programming language) is. This silly little code comes in handy, if
you need some random words for some testing purposes:

    :::python
    import requests
    import re

    def random_words(n=50, wordlength=range(10, 15)):
       """Read a random english wiki article and extract some words.

       Arguments:
       n -- The number of words to return. Returns all found ones, if n is more than we were able to found.
       KeywordArguments:
       wordlength -- A range that forces the words to have a specific length.
       """
       valid_words = re.compile(r'[a-zA-Z]{{{},{}}}'.format(wordlength.start, wordlength.stop))
       found = list(set(valid_words.findall(requests.get('http://en.wikipedia.org/wiki/Special:Random').text)))
       try:
           return found[:n]
       except IndexError:
           return found

    print(random_words(200, range(5, 6)))
    print(random_words(77, range(16, 26))
