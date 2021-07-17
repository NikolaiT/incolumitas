Title: On the Architecture of Bot Detection Services
Status: draft
Date: 2021-07-14 22:58
Category: Security
Tags: Internet Bots, CAPTCHA, Bot Detection
Slug: on-the-architecture-of-bot-detection-services
Author: Nikolai Tschacher

## Introduction

Without ever having developed a fully functional anti bot system myself, I want to investigate some of the obstacles that need to be overcome if I started such a project.

First of all, I have to define the functional specification that such an anti bot system must meet: 

> A bot detection system should be able to detect passively (1) that a website visitor (2) is in fact not a human but an automated program (3)

I deliberately keep my definition very broadly.


1. An **automated program** is software not controlled by an human user. Some examples:
    + The Google Chrome browser automated with a framework such as [playwright](https://github.com/microsoft/playwright) or [puppeteer](https://github.com/puppeteer/puppeteer)
    + Simple `curl` commands automated with shell scripts
    + Real physical mobile phones running Android automated over `adb` (Android Debug Bridge) and (optionally) automated with frameworks such as [appium.io](https://appium.io/) or [DeviceFarmer's stf](https://github.com/DeviceFarmer/stf)
2. Likewise, **detecting passively** means: Without actively interrupting the user's (or bot's) browser session by asking to solve a challenge task such as Google's [reCAPTCHA](https://www.google.com/recaptcha/about/) or the newer [hCAPTCHA](https://www.hcaptcha.com/).
Put differently: The decision whether a website visitor is a human or a bot has to be made by passively observing signals such as TCP/IP streams and other data sent from the browser via JavaScript.
3. And what means **website visitor**?
There is a fundamental difference between a website visitor that simply opens a single page before leaving again and a user that performs a complex action such as logging into an online bank and transferring money. In the latter case, a bot detection system has much more time and signals in order to detect a bot. Furthermore, in the latter case, there is also behavioral and intent data, which is completely lacking in the former case.

Our attacker model is as follows:

<figure>
  <img src="{static}/images/attackerModel.png" alt="attacker model" />
  <figcaption>Attacker model of any bot detection service. The red arrows indicate network messages that possibly contains tainted/spoofed data.</figcaption>
</figure>


Some explanatory words regarding the graphic above:

Websites are served by web servers. Every message that the browser (client) sends to the web server has to be considered as potentially spoofed and tainted. This includes network messages created by JavaScript that are dynamically sent over WebSockets or the [sendBeacon API](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon). This is also the reason why in the traffic arrows from the browser to the web server are in red color.

A fundamental property of client/server security is: All input from clients cannot be trusted from the standpoint of the server. This will be important in the remainder of this blog post, that's why I repeat it so vehemently here.

So what are actually some methods to passively detect that a browser is not controlled by an organic human?

Actually there don't exist straightforward signals that fall into that exact binary category of whether a visitor is a human or not. 

Rather, anti bot vendors rephrase the question to: On what level can we uniquely identify a browser user and then rate limit her? Because that's the overall goal of anti bot systems: Rate limiting unique users.

Some techniques to identify users:

+ By IP address
+ By TLS or [TCP/IP fingerprint](https://github.com/NikolaiT/zardaxt)
+ By HTTP headers and their order/case sensitivity
+ By browser fingerprints obtained via JavaScript (Including WebGL fingerprints, audio fingerprints, [Picasso](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/45581.pdf))
+ By Cookies/Session Ids

It should be obvious that the examples from the list above fall into two categories:

1. Signals that are unspoofable by the design of the Internet, such as IP addresses
2. Data that the clients sends to the server, usually via JavaScript, which can be counterfeited by clients

Of course an attacker can alter her IP address, but then she will need to set up a proxy server. 

Technically, spoofing IP addresses on a IP level will work, but the first router outside your home network will most likely drop the IP packet if it detects that the source IP does not belong to the correct network. And even if that does not happen: How are you ever going to receive a reply to your spoofed IP packet?

With TLS and TCP/IP fingerprinting it's way easier to spoof those signals on the client side.

On the other hand, all the data that is collected via JavaScript can be spoofed by the client! Usually, anti bot companies collect a wide range of different data with JavaScript:

1. Fingerprinting data mostly from the `navigator` property
2. Behavioral data such as mouse movements and touch events or key presses
3. WebGL fingerprints or audio fingerprints


## Architecture of Bot Detection Services 

Let's think about how bot detection services are implemented by following a typical browsing session of a user visiting a website. As discussed above, bot detection systems collect data from both the client side and the server side. In the following section, I will follow a typical browsing session on a very low level and I will explain the different checks that a bot detection system performs at each point along the way.

The very first event relevant for bot detection is the DNS lookup of the hostname to which a browser establishes a connection. The browser uses the operating systems local DNS resolver to lookup the A and AAAA DNS resource record of the hostname in the URL. Worded differently, it asks for the IPv4 or IPv6 address that corresponds to the hostname used in the URL that was entered in the browser's address bar. The DNS request will answered by the responsible name server.

During such a lookup, the DNS server can check that the resolvers client's IP address is the same or belongs to the same ISP as the IP address that communicates with the web server. Put differently, on the DNS server it can be checked that no [DNS leak](https://en.wikipedia.org/wiki/DNS_leak) happens. A DNS leak occurs, if the DNS traffic is not routed through the proxy/VPN configured in the browser.

After the IP address of the domain name has been obtained, the browser is ready to establish a connection with the web server.

Before a browser is able to display anything, a TCP and TLS handshake has to occur to establish a TCP connection to the web server (In case we are using https, which almost always is the case nowadays).

<figure>
  <img src="{static}/images/tslHandshake.svg" alt="TCP and TLS handshake" />
  <figcaption>Before the index.html file is downloaded, a TCP and TLS handshake has to happen.<span style="font-size: 70%">(Source: https://hpbn.co/building-blocks-of-tcp/)</span></figcaption>
</figure>

As soon as the first incoming SYN packet arrives on the web server, an anti bot system is capable of performing the following lookups on the server side:

1. Obtain the source IP address of the client. As soon as we have the source IP address, we can do a wide range of things: 
    + IP address counter: Check if we already have received too many requests from this specific IP address in a certain time frame. Abort the TCP handshake by sending a RST packet if that's the case.
    + Lookup the IP address on spam abuse databases such as [spamhaus.org](https://www.spamhaus.org/). Are there any databases that indicate that this IP address was used for spamming purposes?
    + Conduct a [datacenter IP lookup](https://incolumitas.com/pages/Datacenter-IP-API/) with the IP address. If the IP address belongs to a datacenter, it's very likely that it's a bot.
    + Look up the geographical location for this IP address. Is it a tier 1 country (rich countries in the west such as United Kingdom or Switzerland)? Or is the country known for spamming/botting (Ukraine, Vietnam, Russia - nothing personal here)? 
    + Look up the ASN, organization or registry to which the IP address belongs. This can be done using the `whois` command. For example, `whois 15.23.65.22`.
    + Use IP address metadata services such as [ipinfo.io](https://ipinfo.io/) or [https://ip-api.com/](https://ip-api.com/) to infer more metadata for this IP address.
    + Make a reverse lookup for an IP address with the `host` command. Example: `host 80.185.115.25`. If the hostname belongs to a trustworthy company, give it a better reputation. If it belongs to a untrustworthy organization, block it.

2. Generate a [TCP/IP fingerprint](https://github.com/NikolaiT/zardaxt/) from the SYN packet. A TCP/IP fingerprint gives us information about the assumed operating system of the client based on certain TCP and IP header fields/values such as TCP options header field. The TCP/IP fingerprint alone does not have enough entropy to reasonably exclude a client. However, when the inferred OS seems to be Linux system, then it's valid to raise the bot score, since most legit users do not use Linux. The TCP/IP fingerprint can be altered and spoofed by the client!

After the initial TCP/IP handshake passed, the TLS handshake comes next. After the TLS handshake completed, the server is able to compute a [TLS handshake fingerprint](https://www.net.in.tum.de/fileadmin/TUM/NET/NET-2020-04-1/NET-2020-04-1_04.pdf).

I am not a specialist regarding TLS fingerprinting, but my guess is that a TLS fingerprint has slightly more entropy compared to a TCP/IP fingerprint and allows to differentiate between different TLS implementations and maybe operating systems. If that is the case, then at this point it would be already possible to see if there is a mismatch in TCP/IP fingerprint OS and TLS fingerprint OS. However, keep in mind that TLS and TCP/IP fingerprints can be easily forged on the client side.

After the TLS handshake has been established, the client sends an initial HTTP GET request to fetch the requested URL. Let's assume the client requests the `index.html` document. Based on this very first GET request, we can do a couple of things:

- Compute a HTTP fingerprint. What headers are sent with the client? In what order are they sent? Are the headers case sensitive? 
- Do the HTTP headers contain typical proxy headers such as 
```JavaScript
var proxy_headers = ['Forwarded', 'Proxy-Authorization',
'X-Forwarded-For', 'Proxy-Authenticate',
  'X-Requested-With', 'From',
  'X-Real-Ip', 'Via', 'True-Client-Ip', 'Proxy_Connection'];
```
- Does the HTTP Referer look suspicious?
- Is the HTTP version not from a modern browser but from a non-browser library such as `curl` or Python `requests`?

If all checks pass until this point, the web server is going to serve the contents of the `index.html` document. After the `index.html` document has been downloaded, the browser parses the page and loads linked images, CSS and JavaScript files.

The executed JavaScript in turn dynamically fetches more content which results in more HTTP requests, WebSocket streams and other forms of networking requests.

At this point, the anti bot detection system is ready to serve it's JavaScript client library that collects signals from the browser side.

## Bot Detection Techniques on the Client Side with JavaScript

As soon as JavaScript is executed on the browser, there are a lot of different techniques to harvest data that helps to make a decision whether the client is a bot or not.

Keep in mind that the JavaScript engine is controlled by the client! Thus also the data that is sent back to the web server!

Bot detection companies use many different techniques to camouflage their JavaScript signals collection libraries:

1. [JavaScript obfuscation](https://antoinevastel.com/javascript/2019/09/09/improving-obfuscator.html)
2. JavaScript virtual machines
3. Encryption and encoding of payloads sent back to the server (only makes sense in combination with obfuscation/virtual machines)

Those three obfuscation techniques remind me a bit of the old days of reverse engineering. However, it's much much harder to protect JavaScript code than to protect x86 assembly.

There are some reasons for that:

- JavaScript is a interpreted high level language
- Obfuscated JavaScript must conform to the ECMAScript specification
- Obfuscated JavaScript will at some point also be in AST (Abstract Syntax Tree) representation 

A well known JavaScript obfuscator is [https://github.com/javascript-obfuscator/javascript-obfuscator](javascript-obfuscator). A good JavaScript de-obfuscation tool is [de4js](https://github.com/lelinhtinh/de4js).


Before I dive into some of the JavaScript bot detection techniques, I want to explain why collecting signals with JavaScript and stopping bots is so difficult. Assuming the bot detection execution time for the script is 200ms and then the data is transmitted in 50ms to the web server, which in turn has to make an API request to the central bot detection API (again 50ms), 300ms already passed before the client is banned.

This means that all signals recorded by JavaScript that are sent to the bot detection API incur a large delay before a decision can be made on the server side.

What if our goal is to only scrape a specific page? Then we can simply abort the execution of said script. Maybe the server then remembers: Hey, this specific client with IP XYZ never actually sent a JavaScript payload back home. Looks unusual: One of the following cases had to happen:

1. There was a network outage
2. The user navigated away before the JavaScript payload could be sent home
3. The OS or browser crashed
4. The user blocked the execution of the script deliberately to evade bot detection

Only the last point indicates malicious behavior of the client. Therefore, every bot detection system needs to give each client some free attempts, let's say the IP address get blocked if a threshold of `N=20` has surpassed.

But what if the user switches his IP address between requests? For example by using a mobile 4G or 5G proxy that sits between a [Carrier-grade NAT](https://en.wikipedia.org/wiki/Carrier-grade_NAT)?

You can't just block a whole mobile address range because you feel like it. Wikipedia says:

> In cases of banning traffic based on IP addresses, the system might block the traffic of a spamming user by banning the user's IP address. If that user happens to be behind carrier-grade NAT, other users sharing the same public address with the spammer will be mistakenly blocked. This can create serious problems for forum and wiki administrators attempting to address disruptive actions from a single user sharing an IP address with legitimate users.

What I describe above is something very fundamental about bot detection systems: They must work without relying on JavaScript signals reported back home. Not only because every network message originating from the client is potentially spoofed, but also because some browsers simply cannot execute JavaScript or fail in the process of doing so! Some users don't have JavaScript enabled. Banning the IP address because they disabled JavaScript is too aggressive.

Having said that, let's look at some techniques to detect bots on the client side:

1. Browser Fingerprinting with JavaScript is a very popular method. The idea is to collect as much browser entropy such as `navigator.languages` or `navigator.platform` as possible, while simultaneously trying to look for attributes that are static and don't change on browser/OS updates.
2. Proof of work challenges such as solving cryptographic puzzles in the browser as [friendlycaptcha.com](https://friendlycaptcha.com/) is doing.
3. Another common bot detection method is to produce unique fingerprints with the browser built in webGL rendering system that accesses the client's graphic hardware. For example, [Google Picasso](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/45581.pdf) detects the client's operating system class by leveraging the unique outputs of the webGL renderer.
4. JavaScript can be used to [port scan](https://incolumitas.com/2021/01/10/browser-based-port-scanning/) the client's internal network. This allows to find out if certain suspicious well known ports are open, such as the one for the remote debugging protocol (9222) or the one for adb (too lazy to look up).















