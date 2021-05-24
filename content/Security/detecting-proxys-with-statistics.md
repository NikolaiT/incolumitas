Title: Detecting Datacenter/Residential Proxies Part Two
Date: 2021-04-24 22:07
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

