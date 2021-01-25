Title: BotOrNot
Date: 2021-01-13 00:13
Modified: 2021-01-24 16:39
Author: Nikolai Tschacher
Slug: BotOrNot
Status: published

**Last Edit: 26th January 2021**

I am currently putting a lot of effort into researching how to distinguish web based bots from real human beings. Many researchers published a lot of papers investigating this interesting subject. On this page however, I will take a slightly more practical approach.

<a class="btn" href="https://bot.incolumitas.com" style="padding: 8px; font-weight: 600;">Visit the BotOrNot detection page!</a>

### The Five Dimensions of Advanced Web Based Bots

With *Web Based Bots*, I refer to bots that communicate mostly over the `HTTP` and `HTTPS` protocols and thus interact with the Internet that is visible and accessible to the normal human user. Furthermore, I will only consider bots that are [somewhat advanced](https://www.imperva.com/blog/bad-bot-report-2020-bad-bots-strike-back/). Put differently, advanced bots leverage real browsers by using some form of browser automation/testing framework such as Playwright, Puppeteer, Selenium, PhantomJS, ... 

 Programmers create *Web Based Bots* for a myriad of economical reasons:

+ Automating mundane tasks in order to save human work effort 
+ Scraping valuable information from websites that cannot be accessed by API
+ Creating content on social media platforms (Twitter, TikTok, Instagram Bots)

Creating stealthy bots is a multidimensional problem. It follows that detection is also a complex problem.

In order to not get detected and labeled as a bad bot, there are several areas where an advanced bot programmer attempts to behave as closely as possible as real human being.

**1. Browser Fingerprinting**

Browser fingerprints is the space of technical configurations of a browser that allow a website to identify and distinguish a visiting user.

Browsers are insanely complex artifacts of software and thus exhibit a wealth of information to the websites they visit. For example, the `window.navigator` object has a lot of different pieces of information that allows to fingerprint the browser and to learn more about it's user.

There are widely used fingerprinting JavaScript libraries such as [fingerprintjs](https://github.com/fingerprintjs/fingerprintjs) whose sole purpose is to collect as many stable browser configuration variables as possible. Obtaining a stable browser fingerprint is a two-dimensional optimization problem.

1. On the one side, you want as many parameters as possible in order to increase the entropy of your fingerprint
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

Each browser has also a unique networking behavior. The sequence of HTTP requests that a Browsers sends is unique to each Browser. Different browsers load websites in a different order. Different browsers name non-standard HTTP headers also in a unique ways.

How is browser fingerprinting relevant to advanced bots?

Bot creators attempt to forge a browsing fingerprint that is as generic as possible. Their main strategy is to dive under the radar and to camouflage as a visitor with a browsing fingerprint that is very common. 

Another important point for bot creators is **to not lie when spoofing their fingerprint**: For example, setting a iPhone User-Agent but not adapting the User-Agent accordingly in `navigator.userAgent` or `navigator.appVersion` would make it straightforward for anti-bot companies to detect that the browser has likely been tampered with.

Another very common mistake I see in the wild: Bot programmers change their User-Agent in the HTTP headers but forget to do so in the `navigator` property (Mostly `navigator.userAgent` and `navigator.appVersion`).

**2. Networking Aspects**

*- IP Address Reputation -*

Advanced bots need to route their traffic through a residential or mobile proxy network in order to change their IP address.

The reason is very simple: Most websites use IP based rate limiting. Put differently: When your bot scrapes thousands of pages in a short amount of time, the bot can get blocked quickly based on the fact that each request originated from the same IP address. 

Furthermore, different types of IP Addresses have different reputations in the Internet. For example, datacenter IP addresses such as the ones from [Amazon AWS](https://aws.amazon.com/) or [Google Cloud Functions](https://cloud.google.com/functions) have a rater low reputation when it comes to web traffic. The reason is very obvious: Webmasters do not like traffic that originates from datacenters because the likelihood is large that it is automated traffic. *What normal human user routes their traffic through the cloud?*

Mobile IP addresses have the highest reputation. It is almost impossible to block traffic originating from mobile IP addresses, since many different users in the same mobile cell area share the same IP address in 4G networks.

Explanation by the experts:

> 4G/LTE mobile proxies are so powerful that they render traditional IP bans completely useless, this is thanks to a new technology used by mobile carriers called CGNAT. Carrier Grade Network Address Translation is a very simple concept that means your current IP is being shared by hundreds if not thousands of real people. Websites know this very well and they know if they ban a single IP they could ban hundreds of real users. (Source: [proxidize.com/full-guide/](https://proxidize.com/full-guide/))

*- TCP/IP Fingerprinting -*

Another less known aspect when it comes to bot detection is TCP/IP fingerprints. Because many operating systems have a unique TCP/IP fingerprint (for example, the `window size` and `MTU` differ among some operating systems), it is possible to make a very educated guess about the OS of the host that is communicating with a server based solely on the first incoming SYN packet. [p0f3](https://lcamtuf.coredump.cx/p0f3/) is probably the most used passive TCP/IP fingerprinting tool out there.

Why is this relevant for bot detection?

The reason is obvious: Many bot programmers are using proxy services to switch and hide their real IP address. However, when you configure your browser fingerprint to look like an iPhone, but the TCP SYN packet signature looks like it belongs to a Linux operating system, then there are only two possible explanations for that:

1. Traffic comes from an legitimate iPhone user that uses a VPN/Proxy 
2. A malicious bot programmer forgot to spoof their TCP/IP fingerprint (or more accurate: the proxy server in between)

This is a technique that potentially leads to many false positives. Therefore, it may be used in a more heuristic way such as:

*On a normal day, 5% of my visitors use a VPN/Proxy, but since two hours, there are 40% of all users suddenly using some new kind of TCP/IP fingerprint. Let's block that traffic and let's see if someone complains ;)*

**3. Automation Frameworks**

Advanced bots are often based on [puppeteer](https://github.com/puppeteer/puppeteer) or [playwright](https://github.com/microsoft/playwright). Those automation frameworks make use of the [DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/), which allows their users to automate and control browsers programmatically.

Out of the box, those web automation frameworks and their shipped browsers are configured slightly different then ordinary browsers. There are plugins, [that attempt to fix those artifacts](https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth#readme).

However, a real human user controls browsers quite different compared to the actions that result from puppeteer scripts. For example, a real human user does not wait for certain events to fire, such as for example `networkidle2`.

**4. Hosting Infrastructure**

Advanced bots need to be hosted somewhere. Only small scale bot operations can be run from the personal computer of their programmers. Therefore, web based bots are usually hosted in cloud infrastructure.

However, real human beings browser the web from their personal computers and smartphone. With the help of JavaScript, it is often possible to determine the type of computing environment that executes the JavaScript. There are timing side channel attacks that leak information about the GPU and CPU of the host system.

For example, some folks are running their puppeteer bots in AWS infrastructure (or other cloud infra). 
AWS infrastructure often has certain ports open. A fingerprint of open ports can be obtained. 
[Port scanning is possible with JavaScript in browsers](https://incolumitas.com/2021/01/10/browser-based-port-scanning/).
Therefore, a website could port scan the local network of your bot and if it looks like an AWS host, ban you (of course only if you exhibit other bot heuristics...)

**5. Behavioral Fingerprinting**

Then there is behavior based detection techniques. Humans behave like a chaotic system. Some humans more than others. But that is not the point I am trying to make here. Humans move their mouse, keyboard, and scrolling wheel like humans. Bots still have a hard time to simulate mouses and touchscreens as if humans were the source of those events. Some of the JavaScript events that are of interest: `mousedown`, `mousemove`, `touchstart`, `touchmove`, `keydown`, ...

We are approaching an age where (certain) [captchas can be solved](https://incolumitas.com/2021/01/02/breaking-audio-recaptcha-with-googles-own-speech-to-text-api/) better by AI than by real humans.
