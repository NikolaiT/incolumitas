Title: BotOrNot
Date: 2021-01-13 00:13
Modified: 2021-01-24 16:39
Author: Nikolai Tschacher
Slug: BotOrNot
Status: published
Sortorder: 4

<a class="btn" href="https://bot.incolumitas.com" style="padding: 10px; font-weight: 600; font-size: 15px">Visit the BotOrNot detection page!</a>

**Last Edit: 2nd March 2021**

I currently put a lot of effort into researching the question how to distinguish web based bots from real human beings. Researchers are publishing intriguing new papers constantly that try to answer this question for good. On this page however, I try to take a slightly more practical approach to find solutions. 

*— Personal Stance*
Compared to other actors active in this niche, I am convinced that advanced bots are not always bad. On the contrary, they often drive innovation and nurture creativity. After all, the Internet becomes a greater Oligopoly each passing day. Giving information back to smaller actors is a necessary and endorsed correction.

There is an endless cat and mouse game between bot programmers and anti-bot companies. Let's take a deep dive!

### The Five Dimensions of Advanced Web Based Bots

With *Web Based Bots*, I refer to bots that communicate mostly over the `HTTP` and `HTTPS` protocols and thus interact with the Internet that is visible and accessible to normal human users. Furthermore, I will only consider bots that are [somewhat advanced](https://www.imperva.com/blog/bad-bot-report-2020-bad-bots-strike-back/). Put differently, advanced bots leverage real browsers by using some form of browser automation/testing framework such as Playwright, Puppeteer, Selenium, PhantomJS and many others.

 Programmers create *Web Based Bots* for a myriad of different economical reasons:

+ Automating mundane tasks in order to save human labor effort
+ Scraping valuable information from websites (Search Engines, Amazon, eBay, YouTube, ...)

Or the more darker applications:

+ Automatically creating content on social media platforms (Twitter, TikTok, Instagram Bots) in order to influence unaware people
+ Committing Advertisement Fraud by clicking your own ads
+ Impersonating other Users and committing cyber crime

Creating stealthy bots is a multidimensional problem. It follows that detection is a similarly complex problem.

In order to not get detected and labeled as a bad bot, there are several areas where an advanced bot programmer attempts to behave as closely as possible as real human being. In the following five chapters, I try to elaborate on those different realms.

**1. Browser Fingerprinting**

Browser fingerprints is the space of technical configurations of a browser that allow a website to identify and distinguish a visiting user.

Browsers are insanely complex artifacts of software and thus exhibit a wealth of information to the websites they visit. For example, the `window.navigator` exhibits many different pieces of information that allows to fingerprint the browser and to learn more about it's user.

There exist widely used fingerprinting JavaScript libraries such as [fingerprintjs](https://github.com/fingerprintjs/fingerprintjs), whose sole purpose is to collect as many stable browser configuration variables as possible. Obtaining a stable browser fingerprint is a two-dimensional optimization problem.

1. On the one side, you want as many parameters as possible in order to increase the entropy of the fingerprint
2. On the other side, the selected parameters need to be as stable as possible. Stable means: They are unlikely to change over time

Now it becomes clear why it is so hard to create good fingerprints: The more unique your fingerprint gets (entropy increases), the higher the likelihood that some fingerprinting parameter will change with time.

Stable browser fingerprinting parameters are for example:

+ The timezone (`"Europe/Berlin"`) your browser is configured in: `window.Intl.DateTimeFormat().resolvedOptions().timeZone`
+ The platform (`"Linux x86_64"`) on which your browser is running: `navigator.platform`
+ The hardware concurrency (`4`) of the browser: `navigator.hardwareConcurrency`
+ Your screens (`[1920, 1080]`) resolution: `[window.screen.width, window.screen.height]`
+ The amount of memory (`4`) your device has: `navigator.deviceMemory`
+ What audio/video codecs your browser supports
+ Whether the browser has a touch screen activated
+ And many more ...

Each browser has also a unique network behavior. The sequence of HTTP requests that a Browsers sends is unique to each Browser. Different browsers load websites in a different order. Browsers tend to name non-standard HTTP headers (such as `X-Custom-Header`) also in a unique fashion.

How is browser fingerprinting relevant to advanced bots?

Bot creators attempt to forge a browsing fingerprint that is as generic as possible. Their main strategy is to dive under the radar and to camouflage as a visitor with a common browsing fingerprint. 

Another important point for bot creators is **to not lie when spoofing their fingerprint**: For example, setting a iPhone User-Agent but not adapting the User-Agent accordingly in `navigator.userAgent` or `navigator.appVersion` would make it straightforward for anti-bot companies to detect that the browser has likely been tampered with.

Another very common mistake I see in the wild: Bot programmers spoof their User-Agent in the HTTP headers but forget to do so in the `navigator` property (Mostly `navigator.userAgent` and `navigator.appVersion`).

**2. Networking Aspects**

*— IP Address Reputation*

Advanced bots route their traffic through residential or mobile proxy networks in order to change their IP address.

The reason why they are doing this is very simple: Most websites use IP based rate limiting. Put differently: When your bot scrapes thousands of pages in a short amount of time, the bot can get blocked quickly based on the fact that each request originated from the same IP address. 

Furthermore, different types of IP Addresses have different reputations in the Internet. For example, datacenter IP addresses such as the ones from [Amazon AWS](https://aws.amazon.com/) or [Google Cloud Functions](https://cloud.google.com/functions) have a rather low reputation when it comes to web traffic. The reason is very obvious: Webmasters do not like traffic that originates from datacenters because the likelihood is large that it is automated traffic. *What normal human user routes traffic through cloud servers?*

Mobile IP addresses have the highest reputation. It is almost impossible to block traffic originating from mobile IP addresses, since many different users in the same mobile cell area share the same IP address in 4G networks.

Explanation by the experts from [proxidize.com](https://proxidize.com):

> 4G/LTE mobile proxies are so powerful that they render traditional IP bans completely useless, this is thanks to a new technology used by mobile carriers called CGNAT. Carrier Grade Network Address Translation is a very simple concept that means your current IP is being shared by hundreds if not thousands of real people. Websites know this very well and they know if they ban a single IP they could ban hundreds of real users. (Source: [proxidize.com/full-guide/](https://proxidize.com/full-guide/))

*— TCP/IP Fingerprinting*

Another less widely known aspect when it comes to bot detection are TCP/IP fingerprints. Because many operating systems have a unique TCP/IP fingerprint (for example, the `window size` and `MTU` differ among operating systems), it is possible to make a very educated guess about the OS of the host that is communicating with a server based solely on the first incoming TCP SYN packet. [p0f3](https://lcamtuf.coredump.cx/p0f3/) is probably the most used passive TCP/IP fingerprinting tool out there.

Why is this relevant for bot detection?

The reason is obvious: Many bot programmers are using commercial proxy services to switch and hide their real IP address. However, when you configure your browser fingerprint to look like an iPhone, but the TCP SYN packet signature looks like it belongs to a Linux operating system, there are only two plausible explanations for that:

1. Traffic comes from an legitimate iPhone user that uses a VPN/Proxy 
2. A malicious bot programmer forgot to spoof their TCP/IP fingerprint (or more accurate: the proxy server in between)

Bot detection with passive TCP/IP fingerprinting is a technique that potentially leads to many false positives. Therefore, it may be used in a more heuristic fashion such as:

*On a normal day, 5% of my visitors use a VPN/Proxy. But since two hours, 40% of all my users suddenly exhibit some new kind of TCP/IP fingerprint. Let's block that traffic for a while and let's see if someone complains ;)*

**3. Automation Frameworks**

Advanced bots are often based on [puppeteer](https://github.com/puppeteer/puppeteer) or [playwright](https://github.com/microsoft/playwright). Those automation frameworks make use of the [DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/), which allows to automate and control browsers programmatically. This means that you can control the complete functionality of your browser with a [high level API](https://github.com/puppeteer/puppeteer/blob/main/docs/api.md).

Out of the box, those web automation frameworks come shipped with pre-compiled headless browser binaries. Those binaries are often configured slightly different then ordinary browser binaries.

There are Node.js plugins for puppeteer, that attempt to fix the [leaking of the headless browser status by making them stealthy again](https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth#readme).

However, a real human user controls their browsers quite different compared to the behavior that result from using the puppeteer API. For example, a real human does not wait for certain events to fire before he moves his mouse (such as for example the event `networkidle2`).

Furthermore, because puppeteer programs usually communicate over the Web Socket protocol, there is a tiny delay between the execution of commands (or larger delay when using the [DevTools Protocol remotely](https://www.browserless.io/)).

Often, those automation framework [do not have good support](https://github.com/puppeteer/puppeteer/issues/4378) for creating realistic mouse movements or touch events.

**4. Hosting Infrastructure**

Advanced bots need to be hosted somewhere. Only small scale bot operations can be run from the personal computer of their programmers. Therefore, web based bots are usually hosted from within cloud infrastructure.

However, real human beings browser the web from their personal computers and smartphones. With the help of JavaScript, it is often possible to determine the type of computing environment where the JavaScript code is executed.

Because bot programmers want to host their bots in a economic fashion, they **allocate as little CPU/Memory resources as necessary**. This is in stark contrast to the average human user who uses their laptops with 16GB of memory to visit simple websites. This could be another heuristic that can be used to make an educated guess if a user agent is a bot or not. If there are enough of such simple data points, the statement's quality grows polynomially.

Because browsers are such insanely complex pieces of software, there exit a myriad of timing side channel attacks that leak information about the GPU and CPU of the host system.

A simple test would be to measure the time required to [render a WebGL cube](https://bot.incolumitas.com/redpill/webgl.html).
Other tests measure the latency between CPU and GPU. On cheap cloud infrastructure, there is often only virtual GPU support and thus the latency will be larger.

Some cloud VPS's often havae certain default ports open. A fingerprint of open ports can be obtained, because
[port scanning the local network is possible with JavaScript in browsers](https://incolumitas.com/2021/01/10/browser-based-port-scanning/). Therefore, a website could port scan the local network of your bot's operating system and if it looks like an well-known cloud VPS, block you. However, it is needless to say that [browser based port scanning](https://nullsweep.com/why-is-this-website-port-scanning-me/) is very invasive.

**5. Behavioral Fingerprinting**

The best and hardest detection method comes last: Behavior based detection techniques.

Humans behave like a chaotic system. Some humans more than others. But that is not the point I am trying to make here.

Humans move their mouse, keyboard, touch screen and scrolling wheel in an organic fashion. Bots still have a hard time to mimic mouse movements and touchscreen taps like real humans. Some of the JavaScript events that are of interest here: `mousedown`, `mousemove`, `touchstart`, `touchmove`, `keydown`, ...

A simple process to distinguish bots from real humans based on behavioral data could look like the following:

1. The first step is to collect and extract certain features from a huge set of behavioral data samples. 
2. The next (and way harder) step is to classify the data set as either human or bot-like.
3. To conclude, you could pick a suitable neuronal network to train a system that is able to classify fresh behavioral data.

That is way easier said than done. However, there are some companies such as [biocatch](https://www.biocatch.com/) and [perimeterx](https://www.perimeterx.com/) that are already using this approach since years.

But what exactly makes mouse or touch event interaction in a browser *human*? What are features that are extremely hard to emulate mechanically? Some rough ideas (replace *mouse* with touch events in case of mobile devices):

- The mouse is used as a reading aid (*observe yourself*)
- The start and stop speed of the mouse between points of interest
- The trajectory of mouse movements
- The distribution of events between time. Humans look at the screen, process the information visually and react physically. This pattern repeats all the time. The latency in such reaction patterns is intrinsically human.
- Time interval between mouse clicks
- Mouse follows the eye focus point
- Scrolling speed correlates with reading time
- spikes in behavioral data when a website requires interaction
- mouse moves to the top (tabs) when navigating away (not in mobile)
- mobile only: sometimes screen dimensions plummets 180 degrees on auto-rotate
- on disinterest, mouse races very fast to the "close tab" button
- Areas of interest in text are highlighted
- ...?

The established method to distinguish humans from bots is the good old captcha. However, we are approaching an age where [captchas can be solved](https://incolumitas.com/2021/01/02/breaking-audio-recaptcha-with-googles-own-speech-to-text-api/) better by AI than by real humans.
