Title: Battling incomplete information: Connect market demand with market supply by Google advertisement scraping and lead crawling
Date: 2019-9-30 19:42
Category: Scraping, Crawling
Tags: puppeteer, web scraping, headless chrome, marketing
Slug: connecting-market-demand-and-supply-with-ad-scraping
Author: Nikolai Tschacher
Summary: In this blog post, it is explained how a lack of perfect information about the market allows the clever middleman to connect market supply with market demand by advertisement scrawping and lead crawling.

## The scenario

Let's assume Alexandra is a very well connected women in the law industry and is an executive in a large insurance cooperation that consists of hundreds of branches spread all around the United States.
 
 It frequently occurs that clients that have been referred to Alexandra's insurance company require legal counseling to settle various disputes. This referring process is a decision where a lot of money is made (lead). It's common practice that the party that controls the demand (the law company) charges a fee in order to advertise and prioritize certain lawyers and legal professionals to their clients. Therefore, in a way, not the best lawyers are recommended, but the attorneys that bought the right for being referred from the law company.
 
 This is a mechanism that can be found in any industry or economy, where companies control demand and the clients do not have perfect information about the supply. It's a consequence of the inability of individuals to (1) process a large collection of information and (2) lack of perfect information in the first hand.
 
 There exists a myriad of examples where people without proper information are shamelessly ripped of:
 
 + As a tourist, you are vulnerable to all kinds of information disadvantages. You pay a tourist price from the taxi drive from the airport to your hotel, you pay an increased price for the hotel itself, because you used sites such as [booking.com to book your accommodation](https://dannymekic.com/201607/no-longer-use-booking-com-shouldnt-either). When you eat in restaurants, you most likely end up paying more than the locals, just because you are a foreigner. The list goes on and on. As a tourist, you are basically viewed as privileged person with lots of disposable income.
 
+ It's even worse in the housing market. When you are searching an affordable shared flat and you start looking on online platforms, you most likely pay a at least 50% inflated price compared to what you would pay when you knew the landlords in person.

<figure>
    <img src="https://www.amchameu.eu/sites/default/files/styles/committee_thumbnail/public/group/digital_economy.jpg" alt="digital economy" style="width: 100%;" />
    <figcaption>Incomplete information is the norm in every market (Source: https://www.amchameu.eu/committees-groups/digital-economy) </figcaption>
</figure>


Put differently, for every kind of business where access to information is regulated (which is more or less the case in every industry), you pay a certain fee to an intermediary which connects market demand and market supply. Examples for large Internet intermediaries are [AirBnb](https://www.airbnb.com) or [the devilish dating app Tinder](https://tinder.com/). In both cases, the platform makes money by creating the possibility of a transaction. The platform that brings together demand and supply doesn't add any value, it merely attempts to simulate a better market.

Let's jump back to Alexandra and her control over the demand in form of clients that need to be referred to a legal counselor. Of course any client can decide for himself which lawyer he would prefer, but the consulting effect of the law company comes with a certain authority, especially because the patient finds himself in a vulnerable situation.

So what is Alexandra looking after? She is in need of market supply. So she can offer a continuous stream of many hundreds of clients whose insurances are going to pay large law bills to the legal counselors. So her **goal is to contact as many legal practitioners as possible** and make a contract about client referrals **with the law practitioners that pay the highest referring fee**.


## Mining market supply

Because Alexandra is so well connected, she contacts the CEO of [scrapeulous.com](https://scrapeulous.com/), a promising startup in the data mining and scraping industry. She asks the staff of scrapeulous to give her a list of contact information of legal practices from distinct law subfields that are actively looking for new clients and are willed to pay a certain percentage for promising referrals.

The staff from scrapeulous suggest to scrape Google advertisement links for certain keyword combinations. The keywords shall consist of a **city name** and **law field** such as for example "family law New York" or "civil law Boston". By scraping the advertisement SERP results, it can be assumed that the law companies that paid for the advertisement are accepting new clients. That way it can be ensured that the practices are willed to offer supply.

Using Google AdSense or Google Ads is probably the best way to reach potential customers. It is assumed that at least 50% of the population in the west find service providers such as a doctors or lawyers by making a Google search with the type of service combined with their geographical location.

By only considering Google Advertisements, it is made sure that the law firms are in demand of new clients. If a existing directory of lawyers would be scraped instead, it cannot be assumed that all leads are actively looking for new clients.

After having extracted the advertisement SERP results, the next step is to visit the advertisement link and extract telephone and email information from the website. Then a generic mail is automatically sent to each law practice with the offer to refer to them new clients, if a certain referral fee (or percentage) is paid. If only 2% of all contacted law firms accept the deal, a very lucrative new revenue stream is generated for the insurance cooperation. Of course in real life, there are a couple of other problems that need to be solved, but we will neglect those for the purpose of this blog post.


## Implementing the lead generation pipeline

In a first step, the keywords that are monitored for advertisement results are created. In this example, ten large US cities are combined with seven common law subfields. The following cities

+ Detroit
+ El Paso
+ Memphis
+ Seattle
+ Denver
+ Washington
+ Boston
+ Baltimore
+ Oklahoma City
+ Albuquerque

and the following keywords 

+ DUI law
+ criminal law
+ employment law
+ family law
+ immigration lawyer
+ civil law
+ real estate attorney

yields the following [list of 70 keýwords](https://incolumitas.com/data/law_keywords.txt) when combined.

<figure>
    <img src="https://incolumitas.com/images/keyword_gen.png" alt="keyword generation" style="width: 100%;" />
    <figcaption>Quickly generating keywords with Python</figcaption>
</figure>

After the keywords have been created, it's time to obtain the SERP result pages from Google. It's mandatory to scrape from the same country as the services offered. Therefore, the keywords need to be scraped from the US. Furthermore, we only want the links from advertisements. Google will not display advertisements to a simple scraping script that requests the page with a HTTP GET request, instead a headless browser such as chromium controlled via [puppeteer](https://github.com/GoogleChrome/puppeteer) must be used.

Because we do not want to reinvent the wheel, we will simply use the SERP API from [scrapeulous.com](https://scrapeulous.com/) and sign up to a free plan that allows to search up to 500 keywords on Google. You can easily [sign up here](https://scrapeulous.com/accounts/signup/).

After you have signed up, [go to the dashboard](https://scrapeulous.com/dashboard/api) where you can see the instructions how to use the API. You should also copy your API key into the script below. We will scrape all 70 keywords from the region US with the following quick Python script that makes use of the SERP API and downloads the keywords from this blog.


```Python
import requests
import json

url = 'https://scrapeulous.com/api/new'

req = requests.get('https://incolumitas.com/data/law_keywords.txt')
keywords = [kw for kw in req.text.split('\n') if kw]

payload = {
    "search_engine": "google",
    "num_pages": 1,
    "region": "us",
    "keywords": keywords
}

headers = {
    'X-Api-Key': ''
}

r = requests.post(url, data=json.dumps(payload), headers=headers)
data = r.json()

with open('scraped_keywords.json', 'w') as f:
    json.dump(data, f)
```

After having scraped those keywords with scrapeulous.com, it's time to extract the paid advertisement links from the SERP data. The following little script does the job and prints out all advertisement links that have been gathered from the SERP results:

```Python
import json

ad_links = []

with open('scraped_keywords.json') as f:
    data = json.load(f)
    
    for kw, value in data['results'].items():
    
        if '1' in value:
        
            for ad in value['1']['bottom_ads']:
                ad_links.append(ad.get('link'))
                
            for ad in value['1']['top_ads']:
                ad_links.append(ad.get('link'))
                
print(ad_links)
print(len(ad_links))
```

The above code prints out 17 advertisement links, admittedly not many, but it is enough to justify the purpose of this blog post. When repeating the scraping process, Google will likely serve different advertisement links.

After that, we will use another scraping tool from scrapeulous.com, [the cloud crawler API](https://scrapeulous.com/dashboard/cloud-crawler). The [lead scraping function](https://github.com/NikolaiT/scrapeulous/blob/master/leads.js) from cloudcrawler will be used and all valid urls will be fed into this function.


```Python
import requests
import json

ad_links = ['https://www.drunkdrivinglawyers.com/sem/dui-api1', 'https://ij.org/detroit-forfeiture/', 'https://www.fiegerlaw.com/employment-law/', 'http://immigrationlawyer911.com/', 'https://www.geoffreygnathanlaw.com/', 'https://www.duidenver.com/-/denver/dui-defense/', 'https://www.dui.com/colorado/denver-county/', 'https://www.lazzaralegal.com/criminal-defense/dui/', 'https://www.midsouthcriminaldefense.com/criminal-defense/dui/', 'https://www.duncanandhill.com/', 'https://www.bishoplawmd.com/practice-area/dui-law/', 'https://www.bishoplawmd.com/practice-area/criminal-law/', 'https://family.unbundledlegalhelp.com/alimony/baltimore-md?t=nil', 'https://cordellcordell.com/offices/maryland/baltimore/family-law-for-men-baltimore/', 'https://barrjoneslegal.com/', 'https://www.raygriffithlaw.com/', 'https://www.drunkdrivinglawyers.com/sem/dui-api1']

url = 'https://scrapeulous.com/api/cc'

payload = {
    "invocation_type": "request_response",
    "worker_type": "http",
    "function": "https://raw.githubusercontent.com/NikolaiT/scrapeulous/master/leads.js",
    "items": ad_links,
    "region": "de"
}

headers = {
    'X-Api-Key': ''
}

r = requests.post(url, data=json.dumps(payload), headers=headers)
data = r.json()

with open('leads.json', 'w') as f:
    json.dump(data, f)
```

And the above code will produce the following [lead contact information results](https://incolumitas.com/data/leads.json). Surely they are not perfect, but if this process is repeated with more keywords and every six hours with a cronjob, you will end up with many lead contact information to which you can send automated emails that include your detailed offer of referring law clients.

## Conclusion

In this blog post it was shown using a example scenario how it is possible to connect existing demand with supply and make money by bringing together service providers with new clients. Scraping Google Ads is an efficient method to locate service providers that have enough supply.

This strategy can be applied to any other industry where you control the demand.