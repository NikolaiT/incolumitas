Title: On the Architecture of Anti Bot Services
Status: draft
Date: 2021-07-12 22:58
Category: Security
Tags: Internet Bots, CAPTCHA, Bot Detection
Slug: on-the-architecture-of-anti-bot-services
Author: Nikolai Tschacher

Without having developed a fully functional anti bot system myself, I want to investigate some of the obstacles that need to be overcome if I started such a project.

First of all, I have to define the functional specification that such an anti bot system should be able to provide: *A anti bot software should be able to detect passively that a website visitor is in fact not a human but an automated program*.

I deliberately hold my definition very broadly. An *automated program* can be anything:

+ The Google Chrome browser automated with a framework such as [playwright](https://github.com/microsoft/playwright) or [puppeteer](https://github.com/puppeteer/puppeteer)
+ Simple `curl` command line commands automated with shell scripts
+ Real physical mobile phones running Android automated over `adb` (Android Debug Bridge) and (optionally) automated with frameworks such as [appium.io](https://appium.io/)

Likewise, *passively* means: Without actively interrupting the user's (or bot's) browser session by asking to solve a challenge response system such as Google's [reCAPTCHA](https://www.google.com/recaptcha/about/) or [hCAPTCHA](https://www.hcaptcha.com/). Put differently: The decision whether a website visitor is a human or a bot has to be made by passively observing signals such as TCP/IP messages and data sent from the browser via JavaScript.

Our attacker model is as follows:

<figure>
  <img src="{static}/images/attackerModel.png" alt="attacker model" />
  <figcaption>Attacker Model of any Anti Bot System</figcaption>
</figure>

Websites are served from a web server. Every message that the browser (client) sends to the web server has to be considered as potentially spoofed and tainted data. This includes messages created by JavaScript that are dynamically sent over WebSockets or [sendBeacon](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon) transports.

A fundamental property of client/server security is: All input from clients cannot be trusted. This will be important in the remainder of this blog post, that's why I repeat it so vehemently here.

So what are actually some methods to passively detect that a browser is not controlled by an organic human?

Actually there are are no such straightforward signals that fall into that exact binary category of whether a visitor is a human or not. Anti bot vendors rephrase the question to: On what level can we uniquely identify a browser user and then rate limit her? Because that's the overall goal of anti bot systems: Rate limiting unique users.

Some techniques to identify users:

+ By IP address
+ By TLS or [TCP/IP fingerprint](https://github.com/NikolaiT/zardaxt)
+ By HTTP headers and their order/case sensitivity
+ By browser fingerprint obtained via JavaScript (Including WebGL fingerprint, audio fingerprint, picasso)
+ By Cookies/Session Ids

It should be obvious that the examples from above fall into two categories: 

1. Data that is unspoofable, such as IP addresses or (to some extent) TLS and TCP/IP fingerprint
2. Data that the clients sends to the server, usually via JavaScript

Of course an attacker can alter her IP address, but then she will need to set up a proxy server. Spoofing IP addresses directly will also work, but the first router outside your network will most likely drop the IP packet. And if that does not happen: How are you ever going to receive a reply to your spoofed IP packet? 

With TLS and TCP/IP fingerprint it's way easier to spoof those signals on the client side.

However, all the data that is collected via JavaScript can be spoofed by any client! Usually, anti bot companies collect a wide range of different data with JavaScript:

1. Fingerprinting data mostly from the `navigator` property
2. Behavioral data such as mouse movements and touch events or key presses
3. WebGL fingerprints or audio fingerprints





