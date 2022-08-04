Title: TCP/IP Fingerprint API
Date: 2022-02-17 23:30
Modified: 2022-08-04 14:00
Author: Nikolai Tschacher
Slug: TCP-IP-Fingerprint
Status: published
Sortorder: 9

| <!-- -->         | <!-- -->                                           |   
|------------------|----------------------------------------------------|
| **Author**       | Nikolai Tschacher                                  |
| **API Version**  | v0.2                                               |
| **Version Date** | 4th June 2022                                      |
| **API Access**   | Free                                               |
| **Download**     | [Open Source](https://github.com/NikolaiT/zardaxt) |


## TCP/IP Fingerprint API Demo

**API Endpoint:** [https://tcpip.incolumitas.com/classify?by_ip=1](https://tcpip.incolumitas.com/classify?by_ip=1)

Based on your initial TCP/IP SYN packet, your device most likely is:

<pre id="tcpipFp">
...loading
</pre>

<script>
fetch('https://tcpip.incolumitas.com/classify?by_ip=1')
  .then(response => response.json())
  .then(function(data) {
    document.getElementById('tcpipFp').innerText = JSON.stringify(data, null, 2);
  })
</script>

Your User-Agent (`navigator.userAgent`) says that you are 

<pre id="userAgent">
</pre>

<script>
document.getElementById('userAgent').innerText = navigator.userAgent;
</script>

## TCP/IP Fingerprint API

The TCP/IP fingerprinting API allows you to get your [TCP/IP fingerprint](https://tcpip.incolumitas.com/classify?by_ip=1). It can be used for various purposes such as:

1. Networking traffic analyisis 
2. Malware detection
3. Bot detection
4. Proxy / VPN detection

Currently, there is only one public API endpoint:

| <!-- -->         | <!-- -->                                           |   
|------------------|----------------------------------------------------|
| **Endpoint**       | /classify                                  |
| **Description**  | This endpoint returns the TCP/IP fingerprint for the requesting client                                               |
| **Live API Call** | [tcpip.incolumitas.com/classify](https://tcpip.incolumitas.com/classify)                                      |


You can invoke this API endpoint also with curl:

Example by using `curl`:

```bash
curl 'https://tcpip.incolumitas.com/classify'
```

## Internal API Behavior

The TCP/IP fingerprint API uses your public IP address to lookup your most recent stored TCP/IP fingerprint. Of course you can have several different devices in the same network with the same public IP address. For example, if you request the TCP/IP fingerprint API first with you laptop running MacOS and then with your Andoid smartphone, the stored fingerprint will be overwritten once and you will first see the fingerprint for the MacOS laptop, then the Android device. 

This is what an API consumer would expect by default, but it's not trivial that the API behaves like this. An alternative behavior would be to return ALL stored TCP/IP fingerprints for the public IP address.

## What is TCP/IP fingerprinting?

The hypothesis is that different operating systems (and different minor versions among those operating systems) use different default values in their initial TCP SYN packet that initiates the [TCP three-way handshake](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Connection_establishment).

In this blog post, we will exclusively look at the initial TCP SYN packet. I am perfectly aware that we could investigate the whole TCP packet exchange to deduce more information, such as for example what kind of [TCP congestion control algorithm](https://en.wikipedia.org/wiki/TCP_congestion_control) the client suggests. For example, [Compound TCP](https://en.wikipedia.org/wiki/Compound_TCP) is mostly supported by Microsoft Windows operating systems. But I will limit the analysis to the initial SYN packet.

What TCP/IP header fields exactly are assumed to be OS-specific?

### Entropy from the [IP header](https://en.wikipedia.org/wiki/IPv4)

+ `IP.ttl (8 bits)` - Initial time to live (TTL) value of the IP header. The TTL indicates how long a IP packet is allowed to circulate in the Internet. Each hop (such as a router) decrements the TTL field by one. The maximum TTL value is 255, the maximum value of a single octet (8 bits). A recommended initial value is 64, but some operating systems customize this value. Hence it's relevancy for TCP/IP fingerprinting.
+ `IP.flags (3 bits)` - Don't fragment (DF) and more fragments (MF) flags. In the flags field of the IPv4 header, there are three bits for control flags. The "don't fragment" (DF) bit plays a central role in Path Maximum Transmission Unit Discovery (PMTUD) because it determines whether or not a packet is allowed to be [fragmented](https://www.cisco.com/c/en/us/support/docs/ip/generic-routing-encapsulation-gre/25885-pmtud-ipfrag.html). Some OS set the DF flag in the IP header, others don't.

### Entropy from the [TCP header](https://en.wikipedia.org/wiki/Transmission_Control_Protocol)

<figure>
    <img src="{static}/images/tcpHeader.jpg" alt="TCP header" />
    <figcaption>TCP header fields <a style="font-size: 80%" href="https://stackoverflow.com/questions/24480272/where-is-the-source-and-destination-address-fields-in-tcp-header">(Image Source)</a><span style="font-size: 60%"></span></figcaption>
</figure>

+ `TCP.data_offset (4 bits)` - This is the size of the TCP header in 32-bit words with a minimum size of 5 words and a maximum size of 15 words. Therefore, the maximum TCP header size size is 60 bytes (with 40 bytes of options data). The TCP header size thus depends on how much options are present at the end of the header. 
+ `TCP.window_size (16 bits)` - Initial window size. The idea is that different operating systems use a different initial window size in the initial TCP SYN packet.
+ `TCP.flags (9 bits)` - This header field contains 9 one-bit flags for TCP protocol controlling purposes. The initial SYN packet has mostly a flags value of 2 (which means that only the SYN flag is set). However, I have also observed flags values of 194 (2^1 + 2^6 + 2^7), which means that the SYN, ECE and CWR flags are set to one. If the SYN flag is set, ECE means that the client is [ECN](https://en.wikipedia.org/wiki/Explicit_Congestion_Notification) capable. Congestion window reduced (CWR) means that the sending host received a TCP segment with the ECE flag set and had responded in congestion control mechanism.
+ `TCP.acknowledgment_number (32 bits)` - If the ACK flag is set then the value of this field is the next sequence number that the sender of the ACK is expecting. *Should* be zero if the SYN flag is set on the very first packet.
+ `TCP.sequence_number (32 bits)` - If the SYN flag is set (1), then this is the initial sequence number. It is conjectured that different operating systems use different initial sequence numbers, but the initial sequence number is most likely randomly chosen. Therefore this field is most likely of no particular help regarding fingerprinting.
+ `TCP.urgent_pointer (16 bits)` - If the URG flag is set, then this 16-bit field is an offset from the sequence number indicating the last urgent data byte. It *should* be zero in initial SYN packets.
+ `TCP.options (Variable 0-320 bits)` - All TCP Options. The length of this field is determined by the data offset field. Contains a lot of information, but most importantly: The Maximum Segment Size (MSS), the Window scale value. Because the TCP options data is variable in size, it is the most important source of entropy to distinguish operating systems. The order of the TCP options is also taken into account.

## TODO

- Think about reverse-engineering the [TCP congestion control algorithm](https://en.wikipedia.org/wiki/TCP_congestion_control) by inspecting the packet flow. Reason: Different operating systems use different congestion control mechanisms. Citing [Wikipedia](https://en.wikipedia.org/wiki/TCP_congestion_contro) shows why it might be interesting: 
> Per the end-to-end principle, congestion control is largely a function of internet hosts, not the network itself. There are several variations and versions of the algorithm implemented in protocol stacks of operating systems of computers that connect to the Internet.

- Collect and create a new fingerprint database, because the old one is from mid-2021 ✔️ [last update of database in May 2022]