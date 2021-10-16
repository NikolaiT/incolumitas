Title: 7 different ways to detect proxies
Date: 2021-10-16 12:46
Category: Security
Tags: proxy, proxy-detection, bot-detection
Slug: 7-different-ways-to-detect-proxies
Summary: In this blog post I demonstrate 7 unique ways how you can detect proxy usage from the server side when the client is visiting your web sever either with `curl` or the most recent Chrome browser.
Author: Nikolai Tschacher
Status: Draft

## Introduction

In the past months, I have been writing a lot about bot detection and proxy detection.

For example, I wrote a blog article about [proxy detection using latency measurements]({filename}/Security/detecting-proxies.md) that leverages two different latency measurements, one taken with WebSocket messages from the browser, the other looking at the latencies of the incoming three-way TCP/IP handshake on the server side. The rough idea is: If the statistical median of the two measurements differ significantly, there could be a proxy sitting between the browser and the web server.

But why is proxy detection important in IT security and bot detection? In order to understand that, it's important to understand why your IP address bears so much weight in IT security:

1. The IP address is the unique piece of entropy that tells your communication partners where they have to send their packets in order to communicate with you.
2. Usually, your ISP assigns you an IP address. It doesn't matter if you are using a home modem/router or your mobile phone with a SIM card granting you access to mobile carriers network, in the end your ISP connects you to the Internet and your host will be identified by your IP address. Your ISP knows all the time which customer (with your name, address, passport copy) is associated to which IP address.
3. The basic assumption web services can make about a private customers IP address is that a relatively small group of end users use the same IP address. However, this is not the case anymore with mobile 3G or 4G [Carrier-grade NATs](https://en.wikipedia.org/wiki/Carrier-grade_NAT).
4. A very important security property of IP addresses is that they are [hard to spoof](https://en.wikipedia.org/wiki/IP_address_spoofing): While there is no technical limitation that prevents you from changing the source address of your IP packets, *smart* routers and Intrusion Detection Systems (IDS) on the routing path between you and your communication partner will drop spoofed packets by using methods such as [ingress](https://en.wikipedia.org/wiki/Ingress_filtering) or [egress](https://en.wikipedia.org/wiki/Egress_filtering) filtering. Furthermore, the TCP three-way handshake won't event work with hosts that spoof source IP addresses.
5. All those above properties combined give web service providers some confidence that IP addresses are usually shared by a relatively small group of people and that real human beings will not exceed a certain threshold of network packets. Put differently: You can stop bots by counting how many requests per time period you receive from a certain IP address. If an IP address exceeds that threshold, you rate limit them or serve an CAPTCHA.

<figure>
    <img src="{static}/images/IPv4_Packet-en.svg.png" alt="IPv4_Packet" />
    <figcaption>The IPv4 packet header, because it's so beautiful
    <span style="font-size: 70%">(Source: <a href="https://en.wikipedia.org/wiki/IPv4#Header">https://en.wikipedia.org/wiki/IPv4#Header</a>)</span>
    </figcaption>
</figure>

## The Attacker Model

All proxy detection test in this blog article assume that the client is using the most recent Chrome browser with a http/s or socks proxy configured. You can achieve that by starting Chrome with the following command:

```
google-chrome --proxy-server="socks5://localhost:1080"
```

Furthermore, it is assumed that the Chrome browser comes configured as is, without any plugins or extensions active. JavaScript is enabled.

The attacker model is as follows: The attacker has full control over a web server and lures the client into visiting the attacker's website, that will run the tests specified below. Some of the tests rely upon JavaScript execution and transferring information back to the attacker's website by means such as WebSocket or [Navigator.sendBeacon()](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon) JavaScript API's. 

Of course, the client is able to alter and spoof any JavaScript logic, so if a proxy detection relies exclusively on JavaScript / client side logic, it will be marked as such. This client side spoofing is often made harder by [obfuscating and compressing JavaScript](https://github.com/javascript-obfuscator/javascript-obfuscator).

## 1. Latency Test

Compare ping from browser to server with ping from web server to external IP address

## 2. WebRTC Test

Check if WebRTC leaks the real IP address

## 3. TCP/IP Fingerprint Test

Compare the OS induced from the TCP/IP fingerprint with the OS advertised by the User-Agent

## 4. Open Ports Test

Check if the host connecting to the web server has open ports

## 5. Datacenter IP Test

Check if the IP address belongs to a datacenter

## 6. DNS Leak Test

Check if the DNS server of the client leaks any data

## 7. HTTP Proxy Headers Test

Look for suspicious proxy headers in the HTTP headers

## Even More Juice

And there are even more viable tests:

1. IP Timezone vs Browser Timezone Test: Compare the IP geolocation timezone with the browser timezone