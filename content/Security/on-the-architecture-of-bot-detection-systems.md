Title: On the Architecture of Bot Detection Services
Status: draft
Date: 2021-07-14 22:58
Category: Security
Tags: Internet Bots, CAPTCHA, Bot Detection
Slug: on-the-architecture-of-bot-detection-services
Author: Nikolai Tschacher

## Introduction

Without ever having developed a fully functional anti bot system myself, I want to investigate some of the obstacles that need to be overcome if I had to start such a project.

First of all, I have to define the functional specification that such an anti bot system should have: 

*A Bot Detection System should be able to detect passively that a website visitor is in fact not a human but an automated program*.

I deliberately keep my definition very broadly. An *automated program* can be anything. Some Examples:

+ The Google Chrome browser automated with a framework such as [playwright](https://github.com/microsoft/playwright) or [puppeteer](https://github.com/puppeteer/puppeteer)
+ Simple `curl` commands automated with shell scripts
+ Real physical mobile phones running Android automated over `adb` (Android Debug Bridge) and (optionally) automated with frameworks such as [appium.io](https://appium.io/)

Likewise, *detect passively* means: Without actively interrupting the user's (or bot's) browser session by asking to solve a challenge response task such as Google's [reCAPTCHA](https://www.google.com/recaptcha/about/) or [hCAPTCHA](https://www.hcaptcha.com/).

Put differently: The decision whether a website visitor is a human or a bot has to be made by passively by observing signals such as TCP/IP streams and other data sent from the browser via JavaScript.

Our attacker model is as follows:

<figure>
  <img src="{static}/images/attackerModel.png" alt="attacker model" />
  <figcaption>Attacker Model of any Bot Detection Service. The red arrows indicate network messages that possibly contain tainted/spoofed data.</figcaption>
</figure>

Websites are served by web servers. Every message that the browser (client) sends to the web server has to be considered as potentially spoofed and tainted. This includes messages created by JavaScript that are dynamically sent over WebSockets or the [sendBeacon API](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon).

A fundamental property of client/server security is: All input from clients cannot be trusted from the standpoint of the server. This will be important in the remainder of this blog post, that's why I repeat it so vehemently here.

So what are actually some methods to passively detect that a browser is not controlled by an organic human?

Actually there don't exist straightforward signals that fall into that exact binary category of whether a visitor is a human or not. Rather, anti bot vendors rephrase the question to: On what level can we uniquely identify a browser user and then rate limit her? Because that's the overall goal of anti bot systems: Rate limiting unique users.

Some techniques to identify users:

+ By IP address
+ By TLS or [TCP/IP fingerprint](https://github.com/NikolaiT/zardaxt)
+ By HTTP headers and their order/case sensitivity
+ By browser fingerprints obtained via JavaScript (Including WebGL fingerprints, audio fingerprints, [Picasso](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/45581.pdf))
+ By Cookies/Session Ids

It should be obvious that the examples from the list above fall into two categories:

1. Data that is unspoofable, such as IP addresses or to some extent a realistic TLS and TCP/IP fingerprint
2. Data that the clients sends to the server, usually via JavaScript

Of course an attacker can alter her IP address, but then she will need to set up a proxy server. 

Technically, spoofing IP addresses on a IP level will also work, but the first router outside your network will most likely drop the IP packet. And if that does not happen: How are you ever going to receive a reply to your spoofed IP packet? 

With TLS and TCP/IP fingerprint it's way easier to spoof those signals on the client side.

On the other hand, all the data that is collected via JavaScript can be spoofed by the client! Usually, anti bot companies collect a wide range of different data with JavaScript:

1. Fingerprinting data mostly from the `navigator` property
2. Behavioral data such as mouse movements and touch events or key presses
3. WebGL fingerprints or audio fingerprints


## Architecture of Bot Detection Services 

Let's think about how Bot Detection Services are implemented by following a typical browsing session of a website. As discussed above, those systems collect data from both the client side and the server side.

Before a browser is able to display anything, a TCP and TLS handshake has to occur to establish a TCP connection to the web server (In case we are using https, which almost always is the case nowadays).

<figure>
  <img src="{static}/images/tslHandshake.svg" alt="TCP and TLS handshake" />
  <figcaption>Before index.html is downloaded, a TCP and TLS handshake has to happen.<span style="font-size: 60%">(Source: https://hpbn.co/building-blocks-of-tcp/)</span></figcaption>
</figure>


As soon as the first incoming SYN packet arrives on the server, an anti bot system is capable of performing the following lookups on the server side:

1. Obtain the source IP address of the client. As soon as we have the source IP address, we can do a wide range of things: 
    + IP address counter: Check if we already have received too many requests from this specific IP address in a certain time frame. Abort the TCP handshake by sending a RST packet if that's the case.
    + Lookup the IP address on spam abuse databases such as [spamhaus.org](https://www.spamhaus.org/). Are there any databases that indicate that this IP address was used for spamming purposes?
    + Conduct a [datacenter IP lookup](https://incolumitas.com/pages/Datacenter-IP-API/) with the IP address. If the IP address belongs to a datacenter, it's very likely that it's a bot.
    + Look up the geographical location for this IP address. Is it a tier 1 country (rich countries in the west such as United Kingdom or Switzerland)? Or is the country known for spamming (Ukraine, Vietnam, Russia)? 
    + Look up the ASN, organization or registry to which the IP address belongs. This can be done using the `whois` command. For example, `whois 15.23.65.22`.
    + Use IP address metadata services such as [ipinfo.io](https://ipinfo.io/) or [https://ip-api.com/](https://ip-api.com/) to infer more metadata for this IP address.
    + Make a reverse lookup for an IP address with the `host` command. Example: `host 80.185.115.25`. If the hostname belongs to a trustworthy company, give it a better reputation. If it belongs to a untrustworthy organization, block it.

2. Generate a [TCP/IP fingerprint](https://github.com/NikolaiT/zardaxt/) from the SYN packet. A TCP/IP fingerprint gives us information about the assumed operating system of the client based on certain TCP and IP header fields and header values such as TCP options header field. The TCP/IP fingerprint alone does not have enough entropy to reasonably exclude a client. However, when the inferred OS seems to be Linux system, then it's valid to raise the bot score, since most legit users do not use Linux. The TCP/IP fingerprint can be altered and spoofed by the client!

After the initial TCP/IP handshake passed, the TLS handshake comes next. After the TLS handshake completed, the server is able to compute a [TLS handshake fingerprint](https://www.net.in.tum.de/fileadmin/TUM/NET/NET-2020-04-1/NET-2020-04-1_04.pdf).

I am not a specialist regarding TLS fingerprinting, but my guess is that a TLS fingerprint has slightly more entropy to it and allows to differentiate between different TLS implementations and maybe operating systems. If that is the case, then at this point it would be already possible to see if there is a mismatch in TCP/IP fingerprint OS and TLS fingerprint OS. However, TLS fingerprints can easily be forged on the client side.

After the TLS handshake has been established, the client sends an initial HTTP GET request to fetch the requested URL. Based on this very first GET request, we can do a couple of things:

1. Compute a HTTP fingerprint. What headers are sent with the client? In what order are they sent? Are the headers case sensitive? 
2. Does the HTTP headers contain typical proxy headers such as 
```JavaScript
var proxy_headers = ['Forwarded', 'Proxy-Authorization',
'X-Forwarded-For', 'Proxy-Authenticate',
  'X-Requested-With', 'From',
  'X-Real-Ip', 'Via', 'True-Client-Ip', 'Proxy_Connection'];
```

Usually, the browser first fetches the `index.html` document, then the browser parses the page and loads images, CSS and JavaScript files and the executed JavaScript in turn dynamically fetches more content. 





