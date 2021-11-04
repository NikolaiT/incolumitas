Title: So you want to Scrape like the Big Boys? 🚀
Date: 2021-11-03 23:48
Category: Security
Tags: scraping, industrial level scraping, big boys
Slug: so-you-want-to-scrape-like-the-big-boys
Summary: What it really takes to scrape without getting detected.
Author: Nikolai Tschacher
Status: Published

## Intro

Let's do some thinking, shall we?

When I used to run a scraping service, I managed to scrape at most a couple of million Google SERP pages per week. But I never ever purchased proxies from proxy providers such as [Brightdata](https://brightdata.com/), [Packetstream](https://packetstream.io/) or [Oxylabs](https://oxylabs.io/).

Why? 

Because I could not fully trust other people using those services. What if I share proxy servers with outright criminals that do more than some SERP scraping? Furthermore, those proxy services are quite *pricey*, and me being a stingy German, I didn't possibly see a reasonable way of this combination working out.

<figure>
  <img src="{static}/images/work different.png" alt="farm man" />
  <figcaption>It had to be said.</figcaption>
</figure>

So how did I manage to scrape millions of Google SERP's?

I used [AWS Lambda](https://aws.amazon.com/lambda/), put Headless Chrome into an [AWS Lambda function](https://aws.amazon.com/getting-started/hands-on/run-serverless-code/) and used [puppeteer-extra](https://github.com/berstend/puppeteer-extra) and [chrome-aws-lambda](https://github.com/alixaxel/chrome-aws-lambda) to create a function that automatically launches a browser for 300 seconds that I can solely use for scraping.

Actually, I could have probably achieved the same with plain `curl`, because Google really doesn't put too much effort into blocking bots from their own search engine (they mostly rate limit by IP). But I needed a full browser for other projects, so there was that.

Anyhow, AWS gives you access to 16 regions all around the world (are there even more regions in the meantime?) and after three AWS Lambda function invocations, your function receives a new public IP address. And if you concurrently invoke 1000 Lambda functions, you will bottom out at around 250 public IP addresses. And then you have 16 regions, which gives you around `16 * 250 = 4000` public IP addresses at any time when using AWS Lambda.

I tried the same with [Google Cloud Platform](https://cloud.google.com/), but funnily enough, Google blocks their own cloud infrastructure much more aggressively compared to traffic from AWS.

**But I digress.**

The above setup is not good. It will work for scraping Google, because Google *wants* to be scraped to a certain extent.

But it will never work against well protected websites who employ protection from anti bot companies such as from [DataDome](https://datadome.co/), [Akamai](https://www.akamai.com/) or [Imperva](https://www.imperva.com/) (there are more anti bot companies, don't be salty when I didn't name you, okay?).

Those companies employ ill-adjusted individuals that do nothing else than look for the most recent possibilities to fingerprint browsers, find out if a browser [lies about it's own configuration](https://github.com/abrahamjuliot/creepjs) or exhibits artifacts that don't pertain to a humanly controlled browser. When normal people are out drinking in the pub on Friday night, these individuals invent increasingly bizarre ways to fingerprint browsers and detect bots:

1. Browser Red Pills 
2. Browser Based Port Scanning
3. Google Picasso
4. Font Fingerprinting
5. TCP/IP Fingerprinting
6. Browser based Crypto Challenges - Proof of Work
7. Generic Browser Fingerprinting
8. TLS Fingerprinting
9. WebGL Fingerprinting
10. WebRTC real IP detection
11. Behavioral Classification
12. Gyroscope API querying (device movement / rotation detection)
13. ....

I kid you not, there are millions of ways to detect if a browser is being controlled by a bot or not. It's insanely complex and almost all bot architectures are to a degree vulnerable to detection.

The main reason that makes bots prone to detection is simple economics: In order to scrape millions of pages, bot programmers but their scraping browsers into docker containers and orchestrate them with docker swarm. Others use Kubernetes to orchestrate scraping clusters. And of course they will use cloud providers such as Hetzner, AWS or Digitalocean to host their bots. Nobody uses their Macbook Pro to run 20 Chrome Docker Images over night. 

The above described architecture is highly non-humanlike, what sane human being is browsing Instagram from within a docker container on a Hetzner VPS?!

Let's propose a scraping architecture that is not that easily detectable.

## An undetectable and massively scalable scraping infrastructure

First let's proclaim the two laws of successful scraping: 

1. The second most important rule about evading anti bot companies is: **You shall not lie about your browser configuration**.
2. And the most important rule is: **You shall only lie about your browser configuration if nobody catches you**.

Because I am not that skilled and I am not that good at reverse engineering those [heavily obfuscated fingerprinting libraries](https://incolumitas.com/data/imperva.js) from anti bot companies, my suggestion is to just use real devices for scraping. 

<figure>
  <img src="{static}/images/shelf_closeup_790x.jpg" alt="phones man" />
  <figcaption>Device Farm (Source: https://github.com/DeviceFarmer/stf)</figcaption>
</figure>

If I would try to create a *undetectable* scraping service, I would probably buy 500 [cheap Android devices](https://www.zdnet.com/article/best-phone-under-100/) (Starting at 58$ per device), maybe from 5 different manufacturers. We want diversity after all for fingerprinting reasons! You can also buy old (but more powerful) Android devices. If you buy 100 devices at once, you'll get a massive discount. 

Then I would buy cheap data plans for the devices and I would control the devices with [DeviceFarmer/stf](https://github.com/DeviceFarmer/stf) and rent some cheap storage space (With a mobile cellular antenna closeby) in five top major cities of the world such as London, Paris, Boston, Frankfurt and LA and put 100 phones in there each.

Then I put the lightweight Android Go on each device, throw out everything unnecessary that bloats my device and then plug it into a power source. Every 5 minutes I turn on/off airplane mode so my phone gets another IP address from the [4G carrier grade NAT](https://en.wikipedia.org/wiki/Carrier-grade_NAT).

Mobile IP addresses are practically un-bannable, because they are shared by up to hundred thousands of legitimate users in major cities. Instagram will never dare to ban 200.000 people in LA just because of some pesky spammers! When Carrier Grade NATs were designed, [the designers knew about that issue](https://www.ofcom.org.uk/__data/assets/pdf_file/0020/37802/cgnat.pdf):

> In the event that an IPv4 address is blocked or blacklisted as a source of spam, the impact on a
CGN would be greater, potentially affecting an entire subscriber base. This would increase cost
and support load for the ISP, and, as we have seen earlier, damage its IP reputation.

One problem with the setup described above is that I will need to spoof those pesky `deviceorientation` and `devicemotion` [JavaScript events](https://developer.mozilla.org/en-US/docs/Web/Events/Detecting_device_orientation) on a kernel level, because no real device is laying on the ground without rotation/movement all day long. Every website can access rotation and velocity data from Android data without asking for permission. So we have to spoof that.

But apart from that, I cannot see a way how bot detection system are going to block this scraping infrastructure. *But you probably do, don't you?*

Of course the downsides are apparent: 

1. I have to buy 500 Android devices. I own already three of those things, I would go ballistic with 500 of them.
2. I need to rent storage space in major cities. That's expensive.
3. I need people in 5 cities to fix problems in the device farms.

So that would be a larger project, probably costing thousands of dollars in maintenance.

### Improvement: Emulate Android

Instead of buying real Android devices, it would be better to emulate Android devices with Android emulators such as [Android x86 with VirtualBox](https://www.android-x86.org/documentation/virtualbox.html), [bluestacks](https://www.bluestacks.com/de/index.html) or the [Android Studio Emulator](https://developer.android.com/studio/run/emulator).

Obviously, here we play with the devil again because we want to cut costs!

Can those pesky anti bot companies find out that we are emulating Android devices? 

Maybe with browser based red pills that reveals emulation?

Maybe the emulators are imperfect and this lack is exhibited by the massive JavaScript API that the chrome browser has? 

I am absolutely in favour of the emulation approach. This would mean that we only have to own several powerful servers, plug [4G dongles into them](https://proxidize.com/) and we are ready to go. It could look like this (The image is taken from [proxidize.com/](https://proxidize.com/)): 

<figure>
  <img src="{static}/images/MicrosoftTeams-image-33.png.webp" alt="phones man" />
  <figcaption>A couple of 4G dongles that I use for checking mails and writing Whatsapp messages (Source: https://proxidize.com/gallery/)</figcaption>
</figure>

What [proxidize.com/](https://proxidize.com/) is doing is offering 4G mobile proxies. I don't want proxies, because [proxies are detectable by itself](https://bot.incolumitas.com/proxy_detect.html). I want to directly use the 4G dongle from the very sample geographical position from within the Android Emulator! No Latency!