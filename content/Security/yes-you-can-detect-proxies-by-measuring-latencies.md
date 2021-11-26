Title: Is this a valid method to detect Proxies/VPN?
Date: 2021-11-26 18:46
Category: Security
Tags: proxy, proxy-detection, bot-detection, proxy-provider, bot-detection, anti-scraping
Slug: is-this-a-valid-method-to-detect-proxies-or-vpn
Summary: Is this a valid method to detect Proxies/VPN? I need your help!
Author: Nikolai Tschacher
Status: Published

**Full Disclosure:** I was quite hesitant to publish this article, because I don't know exactly how this proxy detection method works (if it works). I need your help to review this: Please leave a comment!

## Introduction

The goal of this article is to reliably detect proxies and VPN's using JavaScript (more accurate: By measuring latencies with JavaScript). There are many legitimate reasons for proxy/VPN usage, but unfortunately, criminals tend to also camouflage their internet identity (IP address) by abusing proxies and VPN's.

I hate to do deal with latencies and to derive conclusions while looking at them. It's improper science and it's quite dirty to be frank. But I fear that there is some truth hidden in latencies and that it must be considered when trying to detect sneaky bots and malicious traffic.

Let's put it that way: Have you ever attempted to browse a website with a proxy/VPN? Have you noticed that everything tends to load a bit slower? Probably! 

Why should it be impossible to detect this delay and slowness using JavaScript?

<figure>
    <img src="{static}/images/1024px-Mad_scientist.png" alt="Mad Scientist" width="683px" heigh="639px" />
    <figcaption>Me trying to detect proxies with latencies
    <span style="font-size: 70%">(Source: <a href="https://de.wikipedia.org/wiki/Verr%C3%BCckter_Wissenschaftler#/media/Datei:Mad_scientist.svg">https://de.wikipedia.org/wiki/Verr%C3%BCckter_Wissenschaftler#/media/Datei:Mad_scientist.svg</a>)</span>
    </figcaption>
</figure>

What do I even mean when I speak of **detecting proxies with latency measurements**?

There are essentially two ways how bots use proxies in the real world. 

1. They make use of the SOCKS protocol. SOCKS5, the latest version of the protocol is defined in [RFC 1928](https://datatracker.ietf.org/doc/html/rfc1928). This RFC is from March 1996, so it's seen quite some days. SOCKS allows you to route any connection, either UDP or TCP, over a proxy server.
2. Then there are HTTP Proxies.

For [RFC 1928](https://datatracker.ietf.org/doc/html/rfc1928), the most important part is:

> When a TCP-based client wishes to establish a connection to an object
   that is reachable only via a firewall (such determination is left up
   to the implementation), it must open a TCP connection to the
   appropriate SOCKS port on the SOCKS server system.  The SOCKS service
   is conventionally located on TCP port 1080.  If the connection
   request succeeds, the client enters a negotiation for the authentication method to be used, authenticates with the chosen method, then sends a relay request.  The SOCKS server evaluates the
   request, and either establishes the appropriate connection or denies
   it.

As you can read above, the SOCKS specification states
that a SOCKS server basically has to glue two TCP streams 
together (*sends a relay request*).

Each TCP/IP stream, especially the connection establishment, costs several RTT's and thus time. 

A packet being transmitted through two interconnected TCP/IP streams from host A to host B takes more time than a packet flowing through just one TCP channel from host A to host B.

## The Idea

The idea I had is quite simple:

I want to measure the RTT/network latency to three different IP addresses to an arbitrary port that is closed (with high confidence):

1. The special address `0.0.0.0`
2. The special address `127.0.0.1` / `localhost`
3. Differential IP address: An Internet reachable server with IP address for example `167.99.241.135`

**Conjecture:**

If the latency measured with JavaScript to the address `0.0.0.0` is significantly higher compared to the latency to 
`127.0.0.1`, there might be a proxy used by the browser. 

Additionally, the latency to `0.0.0.0` compared to the latency to `167.99.241.135` must be in the same range. Otherwise, the collected data is likely invalid.

### Explanation

But why should the latency to `0.0.0.0` be significantly larger than the latency to `127.0.0.1` when we use a proxy?

Honestly, I don't know for sure.

According to this [hacker news thread](https://news.ycombinator.com/item?id=9048811), the IP `0.0.0.0` should not point to localhost when entered in the chrome address bar. But in this [Chromium bug tracker discussion](https://bugs.chromium.org/p/chromium/issues/detail?id=428046), this is exactly what it does: 

> Allow explicit navigations to "0.0.0.0" to support systems where this performs a
navigation to localhost (in defiance of specs... but seemingly common).

We can quickly look into the [Google Chrome code base](https://chromium.googlesource.com/chromium/src/+/65e7a0403eb51c8490ee13e5da3ed8e544c34926/components/omnibox/autocomplete_input.cc) where address lookup is handled:

```c++
/* components/omnibox/autocomplete_input.cc */

// For hostnames that look like IP addresses, distinguish between IPv6
// addresses, which are basically guaranteed to be navigations, and IPv4
// addresses, which are much fuzzier.
if (host_info.family == url::CanonHostInfo::IPV6)
  return metrics::OmniboxInputType::URL;
if (host_info.family == url::CanonHostInfo::IPV4) {
  // The host may be a real IP address, or something that looks a bit like it
  // (e.g. "1.2" or "3232235521").  We check whether it was convertible to an
  // IP with a non-zero first octet; IPs with first octet zero are "source
  // IPs" and are almost never navigable as destination addresses.
  //
  // The one exception to this is 0.0.0.0; on many systems, attempting to
  // navigate to this IP actually navigates to localhost.  To support this
  // case, when the converted IP is 0.0.0.0, we go ahead and run the "did the
  // user actually type four components" test in the conditional below, so
  // that we'll allow explicit attempts to navigate to "0.0.0.0".  If the
  // input was anything else (e.g. "0"), we'll fall through to returning QUERY
  // afterwards.
  if ((host_info.address[0] != 0) ||
      ((host_info.address[1] == 0) && (host_info.address[2] == 0) &&
        (host_info.address[3] == 0))) {
    // This is theoretically a navigable IP.  We have four cases.  The first
    // three are:
    // * If the user typed four distinct components, this is an IP for sure.
    // * If the user typed two or three components, this is almost certainly a
    //   query, especially for two components (as in "13.5/7.25"), but we'll
    //   allow navigation for an explicit scheme or trailing slash below.
    // * If the user typed one component, this is likely a query, but could be
    //   a non-dotted-quad version of an IP address.
    // Unfortunately, since we called CanonicalizeHost() on the
    // already-canonicalized host, all of these cases will have been changed
    // to have four components (e.g. 13.2 -> 13.0.0.2), so we have to call
    // CanonicalizeHost() again, this time on the original input, so that we
    // can get the correct number of IP components.
    //
    // The fourth case is that the user typed something ambiguous like ".1.2"
    // that fixup converted to an IP address ("1.0.0.2").  In this case the
    // call to CanonicalizeHost() will return NEUTRAL here.  Since it's not
    // clear what the user intended, we fall back to our other heuristics.
    net::CanonicalizeHost(base::UTF16ToUTF8(original_host), &host_info);
    if ((host_info.family == url::CanonHostInfo::IPV4) &&
        (host_info.num_ipv4_components == 4))
      return metrics::OmniboxInputType::URL;
  }
```

The important part:

> The one exception to this is 0.0.0.0; on many systems, attempting to navigate to this IP actually navigates to localhost.

According to [Wikipedia](https://en.wikipedia.org/wiki/0.0.0.0), the address `0.0.0.0` has a special meaning in routing contexts:

> In the context of routing tables, a network destination of 0.0.0.0 is used with a network mask of 0 to depict the default route as a destination subnet. This destination is expressed as 0.0.0.0/0 in CIDR notation. It matches all addresses in the IPv4 address space and is present on most hosts, directed towards a local router.

Maybe when Chrome uses a proxy server, it will route requests going to `0.0.0.0` through the proxy server, but requests going to `127.0.0.1` not. This discrepancy could be measurable.

## Experimental Setup

In order to take latency measurements, I used the following JavaScript code:

```JavaScript
function measureImageLatenciesFetch(url) {
  const N = 5;
  return new Promise((resolve, reject) => {
    let ts = [];
    for (let i = 0; i < N; i++) {
      (function() {
        let t0 = performance.now();
        let fullUrl = url + (44435 + i) + '/' +  (new Date()).getTime() + '.png';
        fetch(fullUrl)
        .then((res) => {

        })
        .catch((err) => {
          let elapsed = (performance.now() - t0)
          ts.push(parseFloat(elapsed.toFixed(3)))
          if (ts.length === N) {
            resolve(ts);
          }
        })
      })();
    }
  });
}

for (let url of ['https://0.0.0.0:', 'https://127.0.0.1:', 'https://167.99.241.135:']) {
  measureImageLatenciesFetch(url).then((latencies) => {
    console.log(url, latencies)
  });
}
```

When I do not use a proxy with my Google Chrome browser, I get the following latencies:

```
https://0.0.0.0: [21.9, 21.6, 22, 21.6, 21.3]

https://127.0.0.1: [23.4, 22.9, 22.4, 22, 26.3]

https://167.99.241.135: [65.6, 64.3, 75.5, 77.3, 79.8]
```

**Observation:** The `0.0.0.0` latencies are in the same range than the `127.0.0.1` latencies.

However, when I start my chrome browser with a local forwarding proxy server (which in turn uses a SOCKS5 upstream proxy) with the command

```bash
chromium-browser --proxy-server=http://localhost:8947 https://incolumitas.com
```

I obtain the following latencies:

```
https://127.0.0.1: [36.9, 37, 38.3, 37.9, 37.4]

https://0.0.0.0: [262.6, 264.8, 325.1, 327.2, 330.4]

https://167.99.241.135: [379.2, 407.9, 410.3, 424, 428.8]
```

**Observation:** It can be seen that the `0.0.0.0` latencies are significantly higher than the `127.0.0.1` latencies.

And when I use a VPN server, this is what I obtain:

```

```

### More Data from the real World

Because I record some data on my 

<a 
  class="orange_button" 
  href="https://bot.incolumitas.com/proxy_detect.html">
Proxy/VPN Detection Page
</a>

I managed to collect some real world data to confirm whether this method works. Some real world data:

#### Data that confirms my Thesis

```
https://abs.incolumitas.com/showFile?fileName=proxy_test_3-9_207.170.172.47_2021-11-24T20:34:08.989Z.json

https://abs.incolumitas.com/showFile?fileName=proxy_test_3-10_45.83.140.9_2021-11-24T20:27:49.329Z.json

https://abs.incolumitas.com/showFile?fileName=proxy_test_2-10_24.118.50.145_2021-11-24T20:26:42.675Z.json

https://abs.incolumitas.com/showFile?fileName=proxy_test_4-10_129.186.252.213_2021-11-24T20:26:06.616Z.json

https://abs.incolumitas.com/showFile?fileName=proxy_test_2-9_69.171.202.234_2021-11-24T19:43:02.409Z.json

https://abs.incolumitas.com/showFile?fileName=proxy_test_3-10_65.129.145.221_2021-11-24T19:28:32.294Z.json

https://abs.incolumitas.com/showFile?fileName=proxy_test_4-11_178.165.190.86_2021-11-23T21:56:48.860Z.json

https://abs.incolumitas.com/showFile?fileName=proxy_test_3-10_193.58.109.139_2021-11-22T20:38:21.556Z.json

https://abs.incolumitas.com/showFile?fileName=proxy_test_2-10_77.119.195.26_2021-11-22T15:17:40.318Z.json
```

#### Bad Data


## I need your Help