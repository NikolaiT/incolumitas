Title: TCP/IP Fingerprint API
Date: 2022-02-17 23:30
Modified: 2023-03-11 14:00
Author: Nikolai Tschacher
Slug: TCP-IP-Fingerprint
Status: published
Sortorder: 9

| <!-- -->         | <!-- -->                                           |
|------------------|----------------------------------------------------|
| **Author**       | Nikolai Tschacher                                  |
| **API Version**  | v0.3                                               |
| **Version Date** | 11th March 2023                                    |
| **API Access**   | Free                                               |
| **Download**     | [Open Source](https://github.com/NikolaiT/zardaxt) |

## TCP/IP Fingerprint API Demo

**Detailed TCP/IP Fingerprint:** [https://tcpip.incolumitas.com/classify?detail=1](https://tcpip.incolumitas.com/classify?detail=1)

**Short TCP/IP Fingerprint:** [https://tcpip.incolumitas.com/classify](https://tcpip.incolumitas.com/classify)

Based on your last observed TCP/IP SYN packet, the following TCP/IP fingerprint data was collected:

<pre id="wrapper">
  <code id="tcpip_fp" class="JSON hljs">...loading (JavaScript required)</code>
</pre>

<script>
var el = document.getElementById('tcpip_fp');
hljs.highlightBlock(el);

fetch('https://tcpip.incolumitas.com/classify?detail=1')
  .then(response => response.json())
  .then(function(data) {
    document.getElementById('tcpip_fp').innerHTML = JSON.stringify(data, null, 2);
    hljs.highlightBlock(el);
  })
</script>

Your User-Agent (`navigator.userAgent`) says that you are

<pre id="userAgent">
</pre>

<script>
document.getElementById('userAgent').innerText = navigator.userAgent;
</script>

## TCP/IP Fingerprint API

The TCP/IP fingerprinting API allows you to get your [TCP/IP fingerprint](https://tcpip.incolumitas.com/classify?). It can be used for various purposes such as:

1. Networking traffic analysis
2. Proxy detection

Currently, there is only one public API endpoint:

| <!-- -->         | <!-- -->                                           |
|------------------|----------------------------------------------------|
| **Description**  | This endpoint returns the TCP/IP fingerprint for the requesting client                                               |
| **Detailed** | [/classify?detail=1](https://tcpip.incolumitas.com/classify?detail=1)                                      |
| **Short** | [/classify](https://tcpip.incolumitas.com/classify)                                      |

You can invoke this API endpoint also with curl:

Example by using `curl`:

```bash
curl 'https://tcpip.incolumitas.com/classify?'
curl 'https://tcpip.incolumitas.com/classify?detail=1'
```

## What is TCP/IP fingerprinting?

The hypothesis is that different operating systems (and different minor versions among those operating systems) use different default values in their initial TCP SYN packet that initiates the [TCP three-way handshake](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Connection_establishment).

In this blog post, we will exclusively look at the initial TCP SYN packet. I am perfectly aware that we could investigate the whole TCP packet exchange to deduce more information, such as for example what kind of [TCP congestion control algorithm](https://en.wikipedia.org/wiki/TCP_congestion_control) the client suggests. For example, [Compound TCP](https://en.wikipedia.org/wiki/Compound_TCP) is mostly supported by Microsoft Windows operating systems. But I will limit the analysis to the initial SYN packet.

What TCP/IP header fields exactly are assumed to be OS-specific?

### Entropy from the [IP header](https://en.wikipedia.org/wiki/IPv4)

<figure>
    <img src="{static}/images/ipHeader.svg" alt="IP header" />
    <figcaption>IP header fields <a style="font-size: 80%" href="https://upload.wikimedia.org/wikipedia/commons/6/60/IPv4_Packet-en.svg">(Image Source)</a><span style="font-size: 60%"></span></figcaption>
</figure>

+ `IP.ihl (4 bits)` - **Internet Header Length (IHL)** - The IPv4 header is variable in size due to the optional 14th field (Options). The IHL field contains the size of the IPv4 header. The minimum value for this field is 5 (20 bytes) and the maximum value is 15 (60 bytes). If the IP options field correlates with the the underlying OS (which I don't think is necessarily the case), the `IP.ihl` is relevant.
+ `IP.len (16 bits)` - **Total Length** - This 16-bit field defines the entire packet size in bytes, including header and data. The minimum size is 20 bytes (header without data) and the maximum is 65,535 bytes. `IP.len` is likely relevant for the TCP/IP fingerprint.
+ `IP.id (16 bits)` - **Identification** - This field is an identification field and is primarily used for uniquely identifying the group of fragments of a single IP datagram. However, the `IP.id` field is used for other purposes and it seems that [its behavior is OS dependent](https://perso.telecom-paristech.fr/drossi/paper/rossi17ipid.pdf): "We find that that the majority
of hosts adopts a constant IP-IDs (39%) or local counter (34%), that
the fraction of global counters (18%) significantly diminished, that a non
marginal number of hosts have an odd behavior (7%) and that random
IP-IDs are still an exception (2%)."
+ `IP.flags (3 bits)` - **Flags** - Don't fragment (DF) and more fragments (MF) flags, bit 0 (RF) is always 0. In the flags field of the IPv4 header, there are three bits for control flags. The "don't fragment" (DF) bit plays a central role in Path Maximum Transmission Unit Discovery (PMTUD) because it determines whether or not a packet is allowed to be [fragmented](https://www.cisco.com/c/en/us/support/docs/ip/generic-routing-encapsulation-gre/25885-pmtud-ipfrag.html). Some OS set the DF flag in the IP header, others don't.
+ `IP.ttl (8 bits)` - **Time to live (TTL)** - An eight-bit time to live field limits a datagram's lifetime to prevent network failure in the event of a routing loop. The TTL indicates how long a IP packet is allowed to circulate in the Internet. Each hop (such as a router) decrements the TTL field by one. The maximum TTL value is 255, the maximum value of a single octet (8 bits). A recommended initial value is 64, but some operating systems customize this value. Hence it's relevancy for TCP/IP fingerprinting.
+ `IP.protocol (8 bits)` - **Protocol** - This field defines the protocol used in the data portion of the IP datagram. IANA maintains a list of IP protocol numbers as directed by RFC 790. It does not seem to be that relevant for TCP/IP fingerprinting, since it is mostly TCP (6).
+ `IP.sum (16 bits)` - **Header checksum** - The 16-bit IPv4 header checksum field is used for error-checking of the header. When a packet arrives at a router, the router calculates the checksum of the header and compares it to the checksum field. If the values do not match, the router discards the packet. Errors in the data field must be handled by the encapsulated protocol. Both UDP and TCP have separate checksums that apply to their data. Probably has no use for TCP/IP fingerprinting.

### Entropy from the [TCP header](https://en.wikipedia.org/wiki/Transmission_Control_Protocol)

<figure>
    <img src="{static}/images/tcpHeader.jpg" alt="TCP header" />
    <figcaption>TCP header fields <a style="font-size: 80%" href="https://stackoverflow.com/questions/24480272/where-is-the-source-and-destination-address-fields-in-tcp-header">(Image Source)</a><span style="font-size: 60%"></span></figcaption>
</figure>

+ `TCP.sequence_number (32 bits)` - **Sequence Number** -  If the SYN flag is set (1), then this is the initial sequence number. It might be the case that different operating systems use different initial sequence numbers, but the initial sequence number is most likely randomly chosen. Therefore this field is most likely of no particular help regarding fingerprinting.
+ `TCP.acknowledgment_number (32 bits)` - **Acknowledgment Number** -  If the ACK flag is set then the value of this field is the next sequence number that the sender of the ACK is expecting. *Should* be zero if the SYN flag is set.
+ `TCP.data_offset (4 bits)` - **Data Offset** - This is the size of the TCP header in 32-bit words with a minimum size of 5 words and a maximum size of 15 words. Therefore, the maximum TCP header size size is 60 bytes (with 40 bytes of options data). The TCP header size thus depends on how much options are present at the end of the header. This is correlating with the OS, since the TCP options correlate with the TCP/IP fingerprint.
+ `TCP.flags (9 bits)` - **Flags** -  This header field contains 9 one-bit flags for TCP protocol controlling purposes. The initial SYN packet has mostly a flags value of 2 (which means that only the SYN flag is set). However, I have also observed flags values of 194 (2^1 + 2^6 + 2^7), which means that the SYN, ECE and CWR flags are set to one. If the SYN flag is set, ECE means that the client is [ECN](https://en.wikipedia.org/wiki/Explicit_Congestion_Notification) capable. Congestion window reduced (CWR) means that the sending host received a TCP segment with the ECE flag set and had responded in congestion control mechanism.
+ `TCP.window_size (16 bits)` - **Window Size** -  Initial window size. The idea is that different operating systems use a different initial window size in the initial TCP SYN packet.
+ `TCP.checksum (16 bits)` - **Checksum** -  The 16-bit checksum field is used for error-checking of the TCP header, the payload and an IP pseudo-header. The pseudo-header consists of the source IP address, the destination IP address, the protocol number for the TCP protocol (6) and the length of the TCP headers and payload (in bytes).
+ `TCP.urgent_pointer (16 bits)` - **Urgent Pointer** -  If the URG flag is set, then this 16-bit field is an offset from the sequence number indicating the last urgent data byte. It *should* be zero in initial SYN packets.
+ `TCP.options (Variable 0-320 bits)` - **Options** -   All TCP Options. The length of this field is determined by the data offset field. Contains a lot of information, but most importantly: The Maximum Segment Size (MSS), the Window scale value. Because the TCP options data is variable in size, it is the most important source of entropy to distinguish operating systems. The order of the TCP options is also taken into account.
