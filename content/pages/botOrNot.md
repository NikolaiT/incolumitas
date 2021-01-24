Title: BotOrNot
Date: 2021-01-13 00:13
Modified: 2021-01-24 16:39
Author: Nikolai Tschacher
Slug: BotOrNot
Status: published

**Last Edit: 25th January 2021**

I am currently putting a lot of effort into researching how to distinguish web based bots from real human beings browsing the web.

<a class="btn" href="https://bot.incolumitas.com" style="padding: 8px; font-weight: 600;">Visit the BotOrNot detection page!</a>

### The Five Dimensions of Advanced Web Based Bots

With *Web Based Bots* I refer to bots that communicate mostly over the `http` and `https` protocols and thus interact with the Internet that is visible and accessible to the normal human user. Programmers create *Web Based Bots* for a myriad of reasons:

+ Automating mundane tasks
+ Scraping valuable information from websites that cannot be accessed via API
+ Influencing readers by automatically creating content (Twitter, Instagram Bots)

Creating advanced bots is a multidimensional problem. Therefore, detection is also a complex problem.

In order to not get detected and labeled as a bad bot, there are several areas where an advanced bot attempts to behave as closely as possible as real human.

**1. Browser Fingerprinting**

Browser fingerprints is the set of technical configurations that allow to identify different user agents (such as Google Chrome browser).

Browsers are insanely complex artifacts of software and thus exhibit a wealth of information to the websites they visit. For example, the `window.navigator` object has a lot of different pieces of information that allows to fingerprint the browser and to learn more about it's user.

Each browser has also a unique networking behavior. Some browsers send different HTTP requests as other Browsers in the same situation. Different browsers load websites in a different sequence.

Bot creators attempt to forge a browsing fingerprint that is as generic as possible. Another important point for bot creators is **to not lie (convincingly)**: For example, setting a IPhone User-Agent but then not adapting the User-Agent in `navigator.userAgent` or `navigator.appVersion` would make it easy for websites that the browser is most likely a bot.

**2. Networking Aspects**

Advanced bots need to route their traffic through a residential or mobile proxy network in order to change their IP address.

The reason is very simple: Most websites use IP based rate limiting. When your bot scrapes thousands of pages in a short amount of time, they can be quickly blocked based on the fact that each request originated from the same IP address. 

Different types of IP Addresses have different reputations in the Internet. For example, 

Datacenter IP addresses such as the ones from Amazon AWS or Google Cloud Functions have a rater low reputation

Mobile IP addresses have the highest reputation. It is almost impossible to block traffic originating from mobile IP addresses, since many different users in the same mobile cell area share the same IP address in 4G networks.

> 4G/LTE mobile proxies are so powerful that they render traditional IP bans completely useless, this is thanks to a new technology used by mobile carriers called CGNAT. Carrier Grade Network Address Translation is a very simple concept that means your current IP is being shared by hundreds if not thousands of real people. Websites know this very well and they know if they ban a single IP they could ban hundreds of real users. (Source: [proxidize.com/full-guide/](https://proxidize.com/full-guide/))

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
