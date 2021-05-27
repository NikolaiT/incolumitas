Title: Detecting Datacenter and Residential Proxies
Date: 2021-04-24 22:07
Modified: 2021-05-26 22:07
Category: Security
Tags: Proxy Detection
Slug: detecting-proxies
Author: Nikolai Tschacher
Summary: Detecting proxys can't be that hard? Can it?

In the following blog article, I assume that we are running a web server and our task is to detect with sufficient accuracy that a client is using a proxy to hide it's source IP address.

Jesus Christ man, detecting proxies can't be that hard? Can it?

First we need to define what a proxy is for our use case?

A proxy is any kind of intermediate host to which you can send your network packets in order to camouflage your true source IP address.

For stupid people (such as me), the Internet basically runs on top of two protocols: 

1. The IP protocol - this is the protocol that handles packet routing on a hop to hop basis
2. The TCP protocol - TCP assumes that some kind of connection exists. It takes for granted that there is a connection from host A to host B. It then handles things such as reliability, congestion control and transmission loss so that applications can communicate without worrying about such things...

Put differently, IP handles all the little annoying details such as, how is my packet properly routed from my Laptop's network card to the home modem, how does the modem send the network packet to the ISP's infrastructure. How does the ISP route the IP packet to the next host?

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

However, we cannot take for granted that the above routing information is correct. Path discovery is often done with ICMP and routers can silently drop those packages. Nobody can force them to reply (correctly).

The only thing that we are able to see is the source IP address of the incoming packet.

We don't know if this is the host that is also the creator of the packet or if it is just a proxy.

I honestly don't care. The only thing that matters for me is that the source IP address is not the 'correct' one.

The *real* source is the computer where all the traffic is generated. The *real* source is the machine that orchestrates and handles the application level logic.

## First Idea: Cross Ping

This is not my idea. After visiting [whatleaks.com/](https://whatleaks.com/), I saw that they have a ping test that is capable of detecting whether a proxy/tunnel is used. The idea is straightforward:

> We compare ping from your computer to our server and ping from our server to the host of your external IP. If the difference is too much then there is probably a tunnel and you are using a proxy.

Put differently, the idea is the following:

If there is no intermediate proxy server used, the ping time from computer (browser) to server should be the same as from server to external IP address. But if there is a proxy server in the middle, then the ping time from server to external IP address should be significantly faster than from computer (browser) to server. We can repeat the pings in order to cancel out statistical errors.

That sounds easy, but in reality we will face several issues:

1. Ping uses the ICMP protocol. The ICMP packet is encapsulated in an IPv4 packet. The packet consists of header and data sections. ICMP is a thin protocol that builds on top of the IP protocol. We can easily use the `ping` command line utility on the server side, but not from the web browser where all we have is JavaScript. It's really not easy to implement something like ping with JavaScript.
2. When we ping the external IP address (that is assumed to either be the proxy server or the source host), we sometimes don't get an answer. The proxy server can choose to not respond to ICMP packets. However, if it is a proxy server, then a port scan must reveal at least one open TCP/IP port.

The first point is the main issue here. 

But I think I have a solution.

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

The ping on the JavaScript side looks like this:

```JavaScript
function ping(url) {
  var started = new Date().getTime();
  var http = new XMLHttpRequest();

  var cacheBuster = '?bust=' + (new Date()).getTime()
  url += cacheBuster;

  http.open("GET", url, /*async*/true);
  http.onreadystatechange = function() {
    if (http.readyState == 4) {
      var ended = new Date().getTime();

      var milliseconds = ended - started;
      console.log("Took ms: ", milliseconds);
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