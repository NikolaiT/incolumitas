Title: Detecting Datacenter and Residential Proxies
Date: 2021-04-24 22:07
Modified: 2021-05-27 22:07
Category: Security
Tags: Proxy Detection
Slug: detecting-proxies
Author: Nikolai Tschacher
Summary: Detecting proxys can't be that hard? Can it?

In the following blog article, I assume that we are running a web server that hosts a web page and our task is to detect with sufficient accuracy that this site's visitor is using a proxy to hide it's *true* source IP address.

Graphically:

```
[browser/client] ---> [http/socks proxy] ---> [target website]
```

First I need to define what a proxy is: A proxy is any kind of intermediate host to which you can send your network packets in order to camouflage your true source IP address. Proxies are often used for web scraping, because when you request a website too frequently with the same IP address, you will get blocked based on your IP address access count. Therefore, switching IP addresses by using several different proxies is way to evade this kind of block.

For stupid people (such as me), the Internet basically runs on top of two protocols: 

1. The IP protocol - this is the protocol that handles packet routing on a hop to hop basis
2. The TCP protocol - TCP assumes that some kind of connection exists. It takes for granted that there is a connection from host A to host B. It then handles things such as reliability, congestion control and transmission loss so that applications can communicate without worrying about such things...

Put differently, IP handles all the little annoying details such as: How is my packet properly routed from my Laptop's network card to the my home modem/router, how does the modem send the network packet to the ISP's infrastructure. How does the ISP route the IP packet to the next host? And so on.

For example, the routing path obtained with `tracepath` from my home in Germany to my webserver (also in Germany) looks like the following:

```text
$ tracepath incolumitas.com
 1?: [LOCALHOST]                      pmtu 1500
 1:  _gateway                                              1.640ms 
 1:  fritz.box                                             1.241ms 
 2:  192.0.0.2                                             1.382ms pmtu 1452
 2:  192.0.0.1                                             6.680ms 
 3:  62.214.39.53                                          7.620ms 
 4:  62.214.37.202                                        17.278ms asymm  5 
 5:  et-0-0-2.ams3-edge1.digitalocean.com                 15.166ms 
 6:  138.197.244.86                                       28.158ms 
 7:  138.197.250.142                                      22.939ms asymm  6 
 8:  no reply
 9:  no reply
10:  167.99.241.135                                       20.330ms reached
     Resume: pmtu 1452 hops 10 back 9 
```

However, we cannot take for granted that the above routing information is correct. Path discovery is often done with ICMP and routers can silently drop ICMP packages. Nobody can force any host on the IP packets path to reply (correctly).

The only thing that we are able to see is the external IP address of the incoming IP packet. We don't know if this is the host that is also the originator (in terms of *the process that sent the packet on it's way*) of the packet or if it is just a proxy.

The *real* source is the process the creates the socket and sends the TCP/IP packets on their merry way. The *real* source is the machine that orchestrates and handles the application level logic.

In the remainder of this blog post I will investigate several ideas how to reveal that a visitor requested my web site through a proxy.

## First Idea: Cross Ping

This is not my idea. After visiting [whatleaks.com/](https://whatleaks.com/), I saw that they have a ping test that is capable of detecting whether a proxy/tunnel is used. The idea is straightforward:

> We compare ping from your computer to our server and ping from our server to the host of your external IP. If the difference is too much then there is probably a tunnel and you are using a proxy.

Put differently, the idea is the following:

If there is no intermediate proxy server used, the ping time from computer (browser) to server should be the same as from server to the external IP address. But if there is a proxy server in the middle, then the ping time from server to external IP address should be significantly faster than from computer (browser) to server. We can repeat the pings in order to cancel out statistical deviations.

That sounds easy, but in reality we will face several issues:

1. Ping uses the ICMP protocol. The ICMP packet is encapsulated in an IPv4 packet. The packet consists of header and data sections. ICMP is a thin protocol that builds on top of the IP protocol. We can easily use the `ping` command line utility on the server side, but not from the web browser where all we have is JavaScript. It's really not easy to implement something like ping with JavaScript.
2. When we ping the external IP address (that is assumed to either be the proxy server or the source host), we sometimes don't get an answer. The proxy server can choose to not respond to ICMP packets. However, if it is a proxy server, then a port scan must reveal at least one open TCP/IP port.

The ping on the server side is easy to implement:

```JavaScript
app.get('/ping', async (req, res) => {
  // ping the external IP address
  let ip = getIp(req);

  let command = `timeout 0.75 ping -qc1 ${ip} 2>&1 | awk -F'/' 'END{ print (/^rtt/? "OK "$5" ms":"FAIL") }'`;
  const { stdout, stderr } = await exec(command);

  res.header("Content-Type",'application/json');
  return res.send(JSON.stringify(stdout.trim(), null, 2));
});
```

The ping on the JavaScript side is if course a bit tougher. We can't sent ICMP messages, so we have to make use of what is available. Of course it's also possible to computer the latency with DNS queries, WebSocket frames or even webRTC packets. But in the following solution, we will craft an invalid `<img>` element and use it to estimate the RTT to the webserver. Please keep in mind that while we have a one way latency with `ping`, with JavaScript there is at least a TCP handshake involved and we talk about RTTs. 

```JavaScript
function ping(url) {
  var started = new Date().getTime();
  var started2 = performance.now();
  var http = new XMLHttpRequest();

  var cacheBuster = '?bust=' + (new Date()).getTime()
  url += cacheBuster;

  http.open("GET", url, /*async*/true);
  http.onreadystatechange = function() {
    if (http.readyState == 4) {
      var ended = new Date().getTime();
      var ended2 = performance.now();

      var milliseconds = ended - started;
      console.log("Took ms: ", milliseconds, ended2 - started2);
    }
  };
  try {
    http.send(null);
  } catch(exception) {
    // this is expected
  }
}

ping("https://incolumitas.com")
```

It's slightly pedantic to also use `performance.now()` to measure the RTT, but I want to get extra sure that `new Date()` is not accurate enough. For our use case, the Same Origin Policy does not prevent us from measuring the latency from browser -> server, because we want to measure the latency to our own origin (our own server).

The lines

```JavaScript
var cacheBuster = '?bust=' + (new Date()).getTime()
url += cacheBuster;
```

prevent the browser from caching the images and thus giving false results for latency measurements.

### Live Example and Explanation of Results

You can also visit the example page here: [https://bot.incolumitas.com/crossping.html](https://bot.incolumitas.com/crossping.html)

Keep in mind though: When you visit the [example page](https://bot.incolumitas.com/crossping.html) with your normal browser that is not behind a proxy, your result will look something like this:

<figure>
    <img src="{static}/images/crossping1.png" alt="Crossping with normal Browser without beign behind a proxy" />
    <figcaption>Crossping with normal browser without hiding behind a proxy. Note: I cannot ping a normal computers public IP address from my server, because usually a NAT drops all incoming ICMP packets. That's the reason why the ping fails.<span style="font-size: 60%"></span></figcaption>
</figure>

On the other hand, when a browser hides behind a proxy server, you will obtain a result as below. As an example, I used a well known scraping service and tested their JavaScript capable bot with the [live testing site](https://bot.incolumitas.com/crossping.html).

<figure>
  <img src="{static}/images/crossping2.png" alt="Crossping with normal Browser without beign behind a proxy" />
  <figcaption>Those latencies are clearly different! The route browser -> server takes much longer compared to server -> external IP address!<span style="font-size: 60%"></span></figcaption>
</figure>

And another example for a scraping service's bot that hides behind a proxy:

<figure>
  <img src="{static}/images/crossping3.png" alt="Crossping with normal Browser without beign behind a proxy" />
  <figcaption>Even higher latencies...<span style="font-size: 60%"></span></figcaption>
</figure>

We can make two key observations:

1. Normal users have `browser -> server` JavaScript ping latencies in the range of roughly 100ms to 500ms. But when you hide behind a proxy, this number grows significantly to the range 1500ms - 6000ms.
2. The ping latency from `server -> external IP address` can either not be obtained (because normal computers behind a NAT/CGNAT are not pingable), or the ping latencies are relatively low in case of proxy servers with a range 20ms - 200ms.

From this follows that we need to make an estimate what latencies are considered *normal* and what latencies are high enough to be considered as the result of an intermediate proxy server.