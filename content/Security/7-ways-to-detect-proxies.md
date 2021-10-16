Title: 7 different ways to detect Proxies
Date: 2021-10-16 12:46
Category: Security
Tags: proxy, proxy-detection, bot-detection, proxy-provider, bot-detection, anti-scraping
Slug: 7-different-ways-to-detect-proxies
Summary: In this blog post I demonstrate 7 unique ways how you can detect proxy usage from the server side when the client is visiting your web sever either with `curl` or the most recent Chrome browser.
Author: Nikolai Tschacher
Status: Draft

## Introduction

In the past months, I have been writing a lot about bot detection and proxy detection.

For example, I wrote a blog article about [proxy detection using latency measurements]({filename}/Security/detecting-proxies.md) that leverages two different latency measurements, one taken with WebSocket messages from the browser, the other looking at the latencies of the incoming three-way TCP/IP handshake on the server side. The rough idea is: If the statistical median of the two measurements differ significantly, there could be a proxy sitting between the browser and the web server.

But why is proxy detection important in IT security and bot detection? In order to understand that, it's important to see why your IP address bears so much weight in bot detection:

1. The IP address is the unique piece of entropy that tells your communication partners where they have to send their packets in order to speak to you.
2. Usually, your ISP assigns an IP address to you. It doesn't matter if you are using a home modem/router or a mobile phone with a SIM card that grants you access to a mobile carrier network, in the end your ISP connects you to the Internet and your host will be identified uniquely by your IP address. Your ISP knows at any moment in time which customer (with your name, address and passport copy that you provided upon registration) is associated to which IP address.
3. The basic assumption web services can make about a private customers IP address is that a relatively small group of end users use the same IP address. However, this is not necessarily the case with mobile 3G or 4G [Carrier-grade NATs](https://en.wikipedia.org/wiki/Carrier-grade_NAT).
4. A very important security property of IP addresses is that they are [hard to spoof](https://en.wikipedia.org/wiki/IP_address_spoofing): While there is no technical limitation that prevents you from changing the source address of your IP packets, *smart* routers and Intrusion Detection Systems (IDS) on the routing path will drop spoofed packets by using methods such as [ingress](https://en.wikipedia.org/wiki/Ingress_filtering) or [egress](https://en.wikipedia.org/wiki/Egress_filtering) filtering. Furthermore, the TCP three-way handshake won't event work with hosts that spoof source IP addresses.
5. All the above properties give web service providers some confidence that IP addresses are usually shared by a relatively small group of people and that real human beings will not send more than a certain threshold of network packets. Put differently: You can stop bots by counting how many requests per time period you received from a certain IP address. If an IP address exceeds that threshold, you rate limit them or serve them a CAPTCHA.

<figure>
    <img src="{static}/images/IPv4_Packet-en.svg.png" alt="IPv4_Packet" />
    <figcaption>The IPv4 packet header, because it's so beautiful
    <span style="font-size: 70%">(Source: <a href="https://en.wikipedia.org/wiki/IPv4#Header">https://en.wikipedia.org/wiki/IPv4#Header</a>)</span>
    </figcaption>
</figure>

## The Attacker Model

The basic scenario is as follows: A scraper developed a bot and tries to scrape many pages of a huge website. Because the website is programmed in React, the scraper decided to use a real browser for his scraping endeavours instead of relying on `curl`.

All proxy detection tests in this blog article assume that the client is using the most recent Chrome browser with a http/s or socks proxy configured. You can achieve that by starting Chrome with the following shell command: `google-chrome --proxy-server="socks5://localhost:1080"`

Furthermore, it is assumed that the Chrome browser comes configured as is, without any plugins or extensions active. JavaScript is enabled by default, as it should be.

The attacker model is as follows: The attacker has full control over a web server and lures the client into visiting the attacker's website (the proxy detection site), which will run the tests specified in this blog article.

Some of the tests rely upon JavaScript execution and transferring information back to the attacker's website by means such as the WebSocket or [Navigator.sendBeacon()](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon) JavaScript API's. 

Of course, the client is able to alter and spoof any JavaScript logic, so if a proxy detection test relies exclusively on JavaScript / client side logic, it will be marked as such. This client side spoofing is often made harder by [obfuscating and compressing JavaScript](https://github.com/javascript-obfuscator/javascript-obfuscator).

Furthermore, time plays also a crucial role. If a detection test gives a result immediately, before even serving the `index.html` file, it's easier to put an stop to scraping. But some tests rely on complicated JavaScript logic, long after the web page has been served, which means that the scraper can be blocked only on subsequent requests to the website.

## General Notes for all Detection Tests

I will not show source code for the proxy detection tests in this blog article. Rather, I will link to my older blog articles in which I often provide implementation. Where applicable, I will provide a link to GitHub projects with source code.

All proxy detection tests can be found on the following dedicated web site: 

<a 
  class="orange_button" 
  href="https://bot.incolumitas.com/proxy_detect.html"
  style="margin: 20px 0">
Visit the proxy detection page
</a>

You can look at the source code of the client side proxy detection test when inspecting the page source code. 

## 1. Latency Test

| Test Property               | Test Property Value                                                                                                     |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------------|
| *Description*          | Compare latency from browser to server with the latency from web server to external IP address                          |
| *Spoofable?*           | Yes, the latency measurements from browser to server are obtained with JavaScript and can be manipulated by the client. |
| *Results Availability* | ~500 ms after `DOMContentLoaded`                                                                                        |
| *Accuracy*             | Depends on the geographical location of the proxy and it's latency.                                                     |                                                    |                                                   |

I created an in-depth description of the basic idea of this bot detection test in [an earlier blog article]({filename}/Security/detecting-proxies.md). The idea is to take two latency measurements:

1. **Browser to Server Latency:** Send `N=10` WebSocket messages from the browser to the web server. The web server immediately replies to each message with the same message (basic echo server). The browser stores the time delta as latency measurement.
2. **Server to Browser Latency:** On the server, when the browser establishes a http connection, we measure the time delta in the initial three-way TCP/IP handshake.

If both latency measurements differ significantly (namely the **Browser to Server Latency** is significantly higher than the **Server to Browser Latency**), it is possible to conjecture that there is an intermediate host between the browser and the web server.

The intermediate proxy server has only one purpose: It splits the TCP/IP connection between client and web-server into two separate TCP/IP connections, so that the web server only sees the source IP address of the proxy server!

1. TCP/IP connection 1, from browser to proxy server
2. TCP/IP connection 2, from proxy server to web server

Because this detour over the proxy server often incurs a geographical and application level delay, we are able to observe a difference in latencies! 

The application level delay is non-negligible: On it's normal routing path, an IP packet only has to pass several extremely high-speed IP-level industrial routers that are built on top of dedicated purpose hardware for routing. A proxy server such as [3proxy](https://github.com/3proxy/3proxy) however usually runs on a off the shelf Linux server and the IP packet has to be passed through the Linux TCP/IP stack all the way up to the user land where the proxy server establishes a new TCP/IP connection with the web server. This takes some milliseconds.

Large proxy providers may optimize the geo-latency and they probably have super fast proxy servers, but they still need to glue the two TCP/IP connections together in order to appear to the web server that it's talking directly to the proxy server. This will always cost some time.

There are a lot of things that can dilute the timing measurements: Network congestion, unexpected networking issues on the client side and many other reasons. On the plus side, it's possible to detect those issues with JavaScript.


## 2. WebRTC Test


| Test Property               | Test Property Value                                               |
|-----------------------------|-------------------------------------------------------------------|
| *Description*          | Check if WebRTC leaks the real IP address                         |
| *Spoofable?*           | Yes, obtaining the real IP address via WebRTC requires JavaScript |
| *Results Availability* | ~200 ms after `DOMContentLoaded`                                  |
| *Accuracy*             | 100%                                               |                                                   |


[WebRTC for proxy detection](https://webrtchacks.com/so-your-vpn-is-leaking-because-of-webrtc/) is an older technique, but still very relevant. [WebRTC](https://en.wikipedia.org/wiki/WebRTC) (Web Real-Time Communication) is a technique that allows direct peer-to-peer communication in browsers over UDP. It is intended to enable direct audio and video communication between peers. 

Because direct peer to peer communication is possible, there must be a way to detect the public and internal IP addresses of the peers. This is made possible with a so called [STUN protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Protocols).

> Session Traversal Utilities for NAT (STUN) (acronym within an acronym) is a protocol to discover your public address and determine any restrictions in your router that would prevent a direct connection with a peer. The client will send a request to a STUN server on the Internet who will reply with the client’s public address and whether or not the client is accessible behind the router’s NAT. ([Source](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Protocols))

However, WebRTC in Chrome is unaffected by any proxy configuration. If a browser is configured to use a proxy server (`google-chrome --proxy-server="socks5://localhost:1080"`), WebRTC does not communicate through this proxy, because WebRTC uses UDP by default and most http/s or socks proxies only support TCP. This standard behavior by Chrome [can be fixed](https://webrtchacks.com/so-your-vpn-is-leaking-because-of-webrtc/).

Without further ado, the html source below will display your IP address as seen by WebRTC:


```html
<!DOCTYPE html><html>
  <head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WebRTC leak</title>
</head>
  <body>
    <script>
      var ips = [];

      function findIP() {
        var myPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection;
        var pc = new myPeerConnection({iceServers: [{urls: "stun:stun.l.google.com:19302"}]}),
          noop = function() {},
          localIPs = {},
          ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/g,
          key;

        function ipIterate(ip) {
          if (!localIPs[ip]) {
            ips.push(ip);
            document.getElementById("webRTCResult").innerHTML = JSON.stringify(ips, null, 2);
          }
          localIPs[ip] = true;
        }
        
        pc.createDataChannel("");
        
        pc.createOffer(function(sdp) {
          sdp.sdp.split('\n').forEach(function(line) {
            if (line.indexOf('candidate') < 0) return;
            line.match(ipRegex).forEach(ipIterate);
          });
          pc.setLocalDescription(sdp, noop, noop);
        }, noop);
        
        pc.onicecandidate = function(ice) {
          if (!ice || !ice.candidate || !ice.candidate.candidate || !ice.candidate.candidate.match(ipRegex)) return;
          ice.candidate.candidate.match(ipRegex).forEach(ipIterate);
        };
      }

      try {
        findIP();
      } catch(err) {
        ips = 'WebRTC failed: ' + err.toString();
        document.getElementById("webRTCResult").innerHTML = JSON.stringify(ips, null, 2);
      }
    </script>

    <h4>WebRTC Detected IPs</h4>
    <pre id="webRTCResult"></pre>
  </body>
</html>
```

If your IP address obtained with WebRTC differs from the IP address that the browser uses otherwise, it's almost always a sure signal that a proxy server is used. Therefore, this test is very helpful in order to detect (misconfigured) proxy-browser sessions. 


## 3. TCP/IP Fingerprint Test

| Test Property               | Test Property Value                                                                                                                                                                                                                                                |
|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Description*          | Compare the OS induced from the TCP/IP fingerprint with the OS advertised by the User-Agent                                                                                                                                                                        |
| *Spoofable?*           | Somewhat. The client will need to alter their TCP/IP stack configuration to change their TCP/IP fingerprint.  In case of a proxy server, the proxy server needs to dynamically match the TCP/IP stack configuration of the User-Agent it routes the traffic for.   |
| *Results Availability* | Right after the User-Agent header of the first incoming HTTP request reached the server.                                                                                                                                                                           |
| *Accuracy*             | 100%                                                                                                                                                                                                                                                               |

I created a python module named [zardaxt.py](https://github.com/NikolaiT/zardaxt) that uses `tcpdump` in order to detect the operating system from an incoming SYN packet belonging to a three-way TCP/IP handshake. 

Please consult the [GitHub page](https://github.com/NikolaiT/zardaxt) if you want to know exactly how this technique works, but to put things shortly: The TCP and IP header fields have different default values on the major operating systems (Linux, Windows, iOS), thus it's possible to infer the operating system by looking at those header fields alone.

This test compares the operating system inferred from the TCP/IP fingerprint with the operating system displayed in the User-Agent or `navigator.userAgent` property from the browser. If there is a mismatch, there might be a proxy used!

I have to admit that this test is not 100% accurate, I look at it more as *one bit* of additional information to make an educated guess.


## 4. Open Ports Test

| Test Property          | Test Property Value                                                                                                                                                                      |
|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Description*          | Check if the host connecting to the web server has open ports or is reachable from the Internet                                                                                          |
| *Spoofable?*           | Somewhat. Either the client is pingable from the Internet or not.  A properly configured iptables can drop any packet that reaches a host that does not belong to a outbound connection. |
| *Results Availability* | After the `nmap` portscan or `ping` probe completed. Maybe 500ms after first SYN packet.                                                                                                 |
| *Accuracy*             | High                                                                                                                                                                                     |


This test is maybe a bit invasive, but it's relatively easy to explain how it works: If I have sufficient grounds to assume that an incoming connection belongs to a proxy, I make an port scan with `nmap`. Alternatively I can `ping` the host. If the host is up and reachable from the Internet, it usually is already a sign that it could be a proxy. Most normal Internet users are behind a ISP or carrier grade NAT, thus not allowing incoming connections from the Internet.

If the host has well-known proxy ports open such as `3128` or `1080`, it is a hard sign that the host has a proxy server running. 

Of course, smart proxy providers will disallow any incoming connections from arbitrary IP ranges, but maybe some magic can be done with [nmap firewall and intrusion detection system detection](https://nmap.org/book/firewalls.html).

I consider this test to be only necessary when there is some evidence that the host might be a proxy but I am not entirely sure.

## 5. Datacenter IP Test

| Test Property          | Test Property Value                                                                                                                                                                                                                                                |
|------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Description*          | Check if the IP address belongs to a datacenter. Datacenter proxies are often hosted in public datacenters such as AWS or Digitalocean. Those cloud providers publish their IP ranges, which makes it possible to check if a proxy belongs to a datacenter or not. |
| *Spoofable?*           | No (if the public IP ranges of the datacenters are to be trusted)                                                                                                                                                                                                  |
| *Results Availability* | Immediately after first incoming SYN packet.                                                                                                                                                                                                                       |
| *Accuracy*             | 100%                                                                                                                                                                                                                                                               |

## 6. DNS Leak Test

| Test Property          | Test Property Value                                                                                                                                                                     |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Description*          | Check if the DNS server of the client leaks any data. If the client uses a DNS resolver that leaks the IP address of the ISP DNS resolver,  it's a mismatch to the proxy IP address.    |
| *Spoofable?*           | Yes, just use a generic DNS resolver such as the one from Google (8.8.8.8) or Cloudflare                                                                                                |
| *Results Availability* | As soon as the SYN packet arrives on the server and the DNS query reached the DNS server.                                                                                               |
| *Accuracy*             | 100%                                                                                                                                                                                    |

## 7. HTTP Proxy Headers Test

| Test Property          | Test Property Value                                                            |
|------------------------|--------------------------------------------------------------------------------|
| *Description*          | Look for suspicious proxy headers in the HTTP headers                          |
| *Spoofable?*           | Yes, just drop any proxy headers on your proxy server                          |
| *Results Availability* | Right after the headers of the first incoming HTTP request reached the server. |
| *Accuracy*             | 100%                                                                           |

## Even More Juice

And there are even more viable tests:

1. IP Timezone vs Browser Timezone Test: Compare the IP geolocation timezone with the browser timezone
2. Browser Based Port Scanning of the internal network: With browser based port scanning techniques, it is possible to find out if there is a proxy server listening for connections.