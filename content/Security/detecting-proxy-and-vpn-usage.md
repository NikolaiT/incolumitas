Title: Detecting Proxy and VPN Usage - An Essay on Anonymity in the Internet
Status: draft
Date: 2021-06-28 21:58
Category: Security
Tags: Proxy, VPN, Anonimity, Detection
Slug: detecting-proxy-and-vpn-usage
Author: Nikolai Tschacher
Summary: Many people use proxy servers and VPN's to remain anonymous when browsing the Internet. In this blog post, it is attempted to detect such a anonymous connection on the web server side.

## Introduction

In this blog post, I try to detect that a browser is using a proxy server or VPN when accessing a website.

Therefore, the attacker model is as follows: I (the attacker) have full control over my web server. My goal is to detect that a client is using a VPN or proxy to access my website. The client uses a modern browser such as Google Chrome or Firefox with JavaScript enabled. Therefore, I can also execute JavaScript 

There are many reasons why people use proxies and VPN's. Them most common reasons are:

1. Many people attempt to circumvent IP geoblocking filters that lock out entire continents from accessing websites (For example, many German media sites such as [sportschau.de](https://www.sportschau.de/index.html) or [zdf.de](https://www.zdf.de/) lock out users accessing those sites from outside of Germany)

2. Another reason is censorship in countries such as China or Belarus: Many Chinese citizens need to access the Internet over a VPN to evade censorship or surveillance in order to access the Internet uncensored. The [Great Firewall](https://en.wikipedia.org/wiki/Great_Firewall) uses sophisticated filter technology and side channel attacks to block protocols such as OpenVPN or IPSec.

3. Cybercriminals wish to remain anonymous when they commit their crimes in the Internet. For that reason, they often use proxies or VPN's.


<figure>
    <img src="{static}/images/vpn_usage.jpg" alt="Reasons for VPN Usage" />
    <figcaption>Reasons for VPN usage <span style="font-size: 60%">(Source: https://blogs.akamai.com/2021/03/act-against-geopiracy-with-enhanced-proxy-detection.html)</span></figcaption>
</figure>


But are tunnels they only way to remain anonymous in the Internet? Why do we even want to use a proxy or VPN for anonymity in the first place?

The fundamental property of a VPN or proxy server regarding anonymity is that the clients routes Internet traffic over an intermediate server. This means that the web server that is accessed can only see the IP address of the intermediate server (proxy). But it's more obvious in an image:

<figure>
    <img src="{static}/images/how-proxies-work.png" alt="How Proxies work" />
    <figcaption>How Proxies work <span style="font-size: 60%">(Source: https://ipdata.co/blog/what-are-proxies-and-how-can-we-detect-them/)</span></figcaption>
</figure>



## Detection Techniques


## Detecting VPN's


## Detecting Scraping/Proxy Providers
