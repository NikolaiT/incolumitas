Title: TCP/IP Fingerprinting for VPN and Proxy Detection
Date: 2021-03-13 14:54
Category: Security
Tags: TCP, IP, fingerprinting, Proxy, VPN
Slug: tcp-ip-fingerprinting-for-vpn-and-proxy-detection
Author: Nikolai Tschacher
Summary: TCP/IP fingerprinting is as old as the Internet itself. But this technique seems to have lost it's relevancy in our modern times. However, with the rise of Proxy and VPN Providers, TCP/IP fingerprinting becomes interesting again from a security perspective.

<a class="btn" href="https://github.com/NikolaiT/zardaxt/" style="padding: 10px; font-weight: 600; font-size: 15px;">Visit the GitHub page of the TCP/IP fingerprinting tool</a>

## Example

Classifying a Windows NT 10.0 operating system with the TCP SYN packet only:

```bash
$ python tcp_fingerprint.py -i eth0 --classify

Loaded 260 fingerprints from the database
listening on interface eth0

1615746475: 33.67.251.73:5098 -> 167.99.241.135:443 [SYN]
{'avgScoreOsClass': {'Android': 'avg=3.72, N=16',
                     'Linux': 'avg=4.27, N=35',
                     'Windows': 'avg=6.39, N=146',
                     'iOS': 'avg=3.44, N=8',
                     'macOS': 'avg=3.02, N=51'},
 'bestGuess': [{'os': 'Windows', 'score': '10.0/10'},
               {'os': 'Windows', 'score': '10.0/10'},
               {'os': 'Windows', 'score': '10.0/10'}]}
---------------------------------
1615746475: 167.99.241.135:443 -> 33.67.251.73:5098 [SYN+ACK]
```

## Introduction

In this blog post, I try to TCP/IP fingerprint web clients that connect to a web server.

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

### Example TCP/IP Fingerprint

Enough theory. Let's get practical. Now I will present two TCP/IP fingerprinting samples, one taken with my laptop desktop computer (Ubuntu 18.04), the other recorded with my Android 9 mobile phone (Motorola g6).

Desktop Ubuntu 18.04 (User-Agent: *Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36*)

```json
{
  "ts": 1615647148,
  "src_ip": "79.203.24.230",
  "dst_ip": "167.99.241.135",
  "dst_port": "443",
  "ip_ttl": 55,
  "ip_df": 1,
  "ip_mf": 0,
  "tcp_window_size": 29200,
  "tcp_flags": 2,
  "tcp_ack": 0,
  "tcp_header_length": 160,
  "tcp_urp": 0,
  "tcp_options": "M1412,S,T,N,W7,",
  "tcp_window_scaling": 7,
  "tcp_timestamp": 3733126878,
  "tcp_timestamp_echo_reply": 0,
  "tcp_mss": 1412
}
```

Android Motorola (g6)

```json
{
  "ts": 1615656348,
  "src_ip": "79.203.24.230",
  "dst_ip": "167.99.241.135",
  "dst_port": "443",
  "ip_ttl": 55,
  "ip_df": 0,
  "ip_mf": 0,
  "tcp_window_size": 65535,
  "tcp_flags": 2,
  "tcp_ack": 0,
  "tcp_header_length": 160,
  "tcp_urp": 0,
  "tcp_options": "M1412,S,T,N,W9,",
  "tcp_window_scaling": 9,
  "tcp_timestamp": 1355521,
  "tcp_timestamp_echo_reply": 0,
  "tcp_mss": 1412
}
```

We can observe several things:

+ Ubuntu 18.04 has a entirely different `tcp_window_size` (29200) compared to the `tcp_window_size` in Android 9 (65535)
+ The IP don't fragment (DF) bit `ip_df` is set in Ubuntu 18.04 but not in Android 9
+ The `tcp_window_scaling` value is different in the two operating systems (7 vs 9)

So we learn: Different operating systems send different initial TCP/IP header fields.

But can we really correlate those values with operating systems? How accurate is this *science*?

I don't know :D 

I could investigate the concrete TCP/IP stack implementations or look up the default values, but I am to lazy for that.

## How to correlate the TCP/IP Fingerprint with the Operating System?

Now that we have collected TCP/IP fingerprints, we correlate those values with the User-Agent and the `navigator.platform` property extracted from the HTTP headers and `windows.navigator` object.

The obvious caveat here is: *Shit in, Shit out*.

If an client spoofs any of the recorded values, we create an incorrect correlation which in turn hurts our classification system. But let's assume I have my ways to filter out spoofed data on some other layer (Hint: Behavioral analysis).

The above correlation process will yield a TCP/IP fingerprint enriched with the corresponding operating system. This is how the [database](https://github.com/NikolaiT/zardaxt/tree/master/database) looks like.

The current classification algorithm ([click here](https://github.com/NikolaiT/zardaxt/blob/master/tcp_fingerprint.py) for the newest version) looks like this:

```Python
def makeOsGuess(fp, n=3):
  """
  Return the highest scoring TCP/IP fingerprinting match from the database.
  If there is more than one highest scoring match, return all the highest scoring matches.

  As a second guess, output the operating system with the highest, normalized average score.
  """
  perfectScore = 10
  scores = []
  for i, entry in enumerate(dbList):
    score = 0
    # @TODO: consider `ip_tll`
    # @TODO: consider `tcp_window_scaling`
    # check IP DF bit
    if entry['ip_df'] == fp['ip_df']:
      score += 1
    # check IP MF bit
    if entry['ip_mf'] == fp['ip_mf']:
      score += 1
    # check TCP window size
    if entry['tcp_window_size'] == fp['tcp_window_size']:
      score += 1.5
    # check TCP flags
    if entry['tcp_flags'] == fp['tcp_flags']:
      score += 1
    # check TCP header length
    if entry['tcp_header_length'] == fp['tcp_header_length']:
      score += 1
    # check TCP MSS
    if entry['tcp_mss'] == fp['tcp_mss']:
      score += 1.5
    # check TCP options
    if entry['tcp_options'] == fp['tcp_options']:
      score += 3
    else:
      # check order of TCP options (this is weaker than TCP options equality)
      orderEntry = ''.join([e[0] for e in entry['tcp_options'].split(',') if e])
      orderFp = ''.join([e[0] for e in fp['tcp_options'].split(',') if e])
      if orderEntry == orderFp:
        score += 2

    scores.append({
      'i': i,
      'score': score,
      'os': entry.get('os', {}).get('name'),
    })

  # Return the highest scoring TCP/IP fingerprinting match
  scores.sort(key=lambda x: x['score'], reverse=True)
  guesses = []
  highest_score = scores[0].get('score')
  for guess in scores:
    if guess['score'] != highest_score:
      break
    guesses.append({
      'score': '{}/{}'.format(guess['score'], perfectScore),
      'os': guess['os'],
    })

  # get the os with the highest, normalized average score
  os_score = {}
  for guess in scores:
    if guess['os']:
      if not os_score.get(guess['os']):
        os_score[guess['os']] = []
      os_score[guess['os']].append(guess['score'])

  avg_os_score = {}
  for key in os_score:
    N = len(os_score[key])
    # only consider OS classes with at least 8 elements
    if N >= 8:
      avg = sum(os_score[key]) / len(os_score[key])
      avg_os_score[key] = 'avg={}, N={}'.format(round(avg, 2), N)

  return {
    'bestGuess': guesses[:n],
    'avgScoreOsClass': avg_os_score,
  }
```

To improve upon this, I need to build equivalency classes and I need to define operating system classes.

Major and minor operating system classes:

1. **macOS** and minor versions such as Sierra, High Sierra, Mojave, Catalina
2. **iOS**
3. **Android** and minor versions such as Android 8, Android 9, Android 10
4. **Windows** and minor versions such as Windows 7 (NT 6.1), Windows 8 (NT 6.3) and Windows 10 (NT 10.0)
5. **Linux** and (maybe) distinct distributions such as Ubuntu, Suse, Linux Arch, ...

I don't think it is feasible to classify everything properly for every minor operating system version using the User-Agent alone.

Nevertheless, the User-Agent should be accurate enough for the five major operating system classes. After all, most proxy or VPN servers are running some kind of Linux system, but often, the connecting clients claim to be a macOS or Windows operating system. I just want to detect that they are lying, not *how badly* they are lying.

## Detecting Proxy/VPN Usage with TCP/IP Fingerprinting

General idea: My goal is *not* to identify a specific version of a proxy or VPN software.

Rather, I want to recognize that there is a discrepancy in the operating system derived from the User-Agent and the operating system suspected behind the TCP/IP fingerprint. Such a mismatch is enough to flag the established connection as potentially malicious.

In order to be relatively sure that the observed TCP/IP fingerprint does not pertain to one of the above five listed operating system classes, I need to collect as many unique fingerprint samples as possible for each operating system class.

But what happens if the VPN or proxy server dynamically changes its TCP/IP fingerprint?

Indeed, it is very easy to alter the TCP/IP fingerprint on Linux systems. For example, you can change the MSS on a specific route on Linux with the following command:

```bash
ip route add 11.22.33.44/32 via 172.17.0.1 advmss 1340
```

 The question however is: How practical is that? Are those proxy/VPN services really gonna alter the TCP/IP fingerprint for every client for which they are routing the traffic based on application layer data? 
 
The proxy/VPN service would have to detect the clients operating system by inspecting the HTTP headers and update the TCP/IP fingerprint accordingly. I don't think this approach is practical.


### Detecting Proxy / VPN connections based on MTU/MSS ratio

[This article](https://ipleak.com/articles/proxy-vpn-detection-passive-fingerprinting) suggest to detect proxy / VPN usage by comparing the MTU/MSS ratio of a connection to a standard table of MTU/MSS ratio. 

Remember: 

+ MTU (Maximum Transmission Unit) is the upper size of an IP packet including the header.
+ MSS (Maximum Segment Size) is the upper size of the data unit being transmitted (excluding the header).

Protocols such as PPTP, L2TP, or IPsec IKE lower the MTU setting at the network interface (For example to 1400 for IPsec). By comparing the packet size within an intercepted connection to standard MTU / MSS settings, the use of a proxy or VPN can be detected.