Title: TCP/IP Fingerprinting for VPN and Proxy Detection
Date: 2021-03-13 14:54
Category: Security
Tags: TCP, IP, fingerprinting, Proxy, VPN
Slug: tcp-ip-fingerprinting-for-vpn-and-proxy-detection
Author: Nikolai Tschacher
Summary: TCP/IP fingerprinting is as old as the Internet itself. But this technique seems to have lost it's relevancy it seems. However, with the rise of Proxy and VPN Providers, TCP/IP fingerprinting becomes interesting again.

## Introduction

In this blog post, I try to fingerprint web clients that connect to a web server.

The [fingerprinting tool](https://github.com/NikolaiT/zardaxt) is running passively on the server and does not modify TCP/IP packets. The goal is to detect a mismatch in the operating system specified in the HTTP User-Agent header and the operating system inferred from the TCP/IP header intricacies. Put differently: If the TCP/IP fingerprint operating system is different than the claimed User-Agent operating system, there *must* be something wrong with that client.

Quick TCP/IP recap:

The [Internet Protocol (IP)](https://en.wikipedia.org/wiki/Internet_Protocol) is responsible for transmitting packets from host to host. A host is a node in a network that is addressable with a IPv4 or IPv6 address. The IP protocol operates on the Internet/Network layer.

[Transmission Control Protocol (TCP)](https://en.wikipedia.org/wiki/Transmission_Control_Protocol) however is one layer above the IP protocol. TCP is mainly responsible to guarantee a robust, fail-proof connection between two hosts. The TCP protocol brings packet loss recovery, guarantees the packet order and handles congestion control. TCP is connection oriented, it does not care about the routers and intermediate hops between the two communicating hosts.

## Motivation

Many users need to access anonymizing services such as VPNs or Proxy servers in order to evade Geo-blocking or governmental firewalls.

Those services are also frequently used for scraping purposes (which I don't have any issues with, as long as the scraping traffic does not impair the websites or accesses private data).

However, many cyber criminals also use services such as SOCKS Proxies, TOR or VPN's to launch cyber attacks and to hide their true IP identity.

For those reasons, it would be nice to have a tool that allows to make a statistical conjecture such as: *"It is very likely that this TCP/IP connection is routed over a VPN/Proxy"*.

## But what exactly is TCP/IP fingerprinting?

The hypothesis is that different operating systems (and different minor versions among those operating systems) use different default values in their initial TCP SYN packet that initiates the [TCP three-way handshake](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Connection_establishment).

In this blog post, we will exclusively look at the initial TCP SYN packet. I am perfectly aware that we could investigate the whole TCP packet exchange to deduce more information, such as for example what kind of [TCP congestion control algorithm](https://en.wikipedia.org/wiki/TCP_congestion_control) the client suggests. For example, [Compound TCP](https://en.wikipedia.org/wiki/Compound_TCP) is mostly supported by Microsoft Windows operating systems. But I will limit the analysis to the initial SYN packet.

What TCP/IP header fields exactly are assumed to be OS-specific?

#### Entropy from the [IP header](https://en.wikipedia.org/wiki/IPv4)

+ `IP.ttl (8 bits)` - Initial time to live (TTL) value of the IP header. The TTL indicates how long a IP packet is allowed to circulate in the Internet. Each hop (such as a router) decrements the TTL field by one. The maximum TTL value is 255, the maximum value of a single octet (8 bits). A recommended initial value is 64, but some operating systems customize this value. Hence it's relevancy for TCP/IP fingerprinting.
+ `IP.flags (3 bits)` - Don't fragment (DF) and more fragments (MF) flags. In the flags field of the IPv4 header, there are three bits for control flags. The "don't fragment" (DF) bit plays a central role in Path Maximum Transmission Unit Discovery (PMTUD) because it determines whether or not a packet is allowed to be [fragmented](https://www.cisco.com/c/en/us/support/docs/ip/generic-routing-encapsulation-gre/25885-pmtud-ipfrag.html). Some OS set the DF flag in the IP header, others don't.

#### Entropy from the [TCP header](https://en.wikipedia.org/wiki/Transmission_Control_Protocol)

<figure>
    <img src="{static}/images/tcpHeader.jpg" alt="TCP header" />
    <figcaption>TCP Header <a style="font-size: 80%" href="https://stackoverflow.com/questions/24480272/where-is-the-source-and-destination-address-fields-in-tcp-header">(Image Source)</a><span style="font-size: 60%"></span></figcaption>
</figure>

+ `TCP.data_offset (4 bits)` - This is the size of the TCP header in 32-bit words with a minimum size of 5 words and a maximum size of 15 words. Therefore, the maximum TCP header size size is 60 bytes (with 40 bytes of options data). The TCP header size thus depends on how much options are present at the end of the header. 
+ `TCP.window_size (16 bits)` - Initial window size. The idea is that different operating systems use a different initial window size in the initial TCP SYN packet.
+ `TCP.flags (9 bits)` - This header field contains 9 one-bit flags for TCP protocol controlling purposes. The initial SYN packet has mostly a flags value of 2 (which means that only the SYN flag is set). However, I have also observed flags values of 194 (2^1 + 2^6 + 2^7), which means that the SYN, ECE and CWR flags are set to one. If the SYN flag is set, ECE means that the client is [ECN](https://en.wikipedia.org/wiki/Explicit_Congestion_Notification) capable. Congestion window reduced (CWR) means that the sending host received a TCP segment with the ECE flag set and had responded in congestion control mechanism.
+ `TCP.acknowledgment_number (32 bits)` - If the ACK flag is set then the value of this field is the next sequence number that the sender of the ACK is expecting. *Should* be zero if the SYN flag is set on the very first packet.
+ `TCP.sequence_number (32 bits)` - If the SYN flag is set (1), then this is the initial sequence number. It is conjectured that different operating systems use different initial sequence numbers, but the initial sequence number is most likely randomly chosen. Therefore this field is most likely of no value. 
+ `TCP.urgent_pointer (16 bits)` - If the URG flag is set, then this 16-bit field is an offset from the sequence number indicating the last urgent data byte. It *should* be zero in initial SYN packets.
+ `TCP.options (Variable 0-320 bits)` - All TCP Options. The length of this field is determined by the data offset field. Contains a lot of information, but most importantly: The Maximum Segment Size, the Window scale value. Because the TCP options data is variable in size, it is the most important source of entropy to distinguish operating systems. The order of the TCP options is also taken into account.