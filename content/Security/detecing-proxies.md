Title: Detecting Proxies and VPN's with Latency Measurements
Status: published
Date: 2021-06-07 20:00
Modified: 2021-06-09 20:00
Category: Security
Tags: proxy-detection, anti-scraping
Slug: detecting-proxies-and-vpn-with-latencies
Author: Nikolai Tschacher
Summary: VPN's and Proxy Servers can be detected by comparing latencies from Browser -> Server with the latency of the TCP/IP handshake RTT on the webserver.

## Task

**Premise:** I am the owner of the website and I have full control of my web server (root rights). My web server is not behind a load balancer or some other mechanism that prevents me to hook into the incoming TCP/IP stream from the external IP address.

**Goal:** For each visitor of my site, I want to detect that this visitor is using some tunnel such as a Proxy Server (socks, https, ...) or a VPN provider or any other intermediate service.

**Visually:** 

<figure>
    <img src="{static}/images/proxy-latency.png" alt="Proxy Latency" />
</figure>

Put differently, I want to take two latency measurements and compare them.

1. Latency from **browser -> web server**, measured with JavaScript from within the browser
2. Latency from **external IP -> web server**, measured on incoming TCP/IP handshake

## Obtain Browser -> Web Server Latency with JavaScript

Good resources regarding latency measurement with the DOM and JavaScript:

1. [Analyzing Network Characteristics Using JavaScript And The DOM](https://www.smashingmagazine.com/2011/11/analyzing-network-characteristics-using-javascript-and-the-dom-part-1/)
2. [Measure network latency (time to first byte) from the client with JavaScript](https://stackoverflow.com/questions/43821243/measure-network-latency-time-to-first-byte-from-the-client-with-javascript)

Without much explanation, this is the JavaScript source code to obtain the latency from browser to web server. I make 10 measurements and I will use the median value.

```JavaScript
let N = 10;

function ping(url) {
  return new Promise((resolve, reject) => {
    var started = performance.now();
    var http = new XMLHttpRequest();

    var cacheBuster = '?bust=' + (new Date()).getTime()
    url += cacheBuster;

    http.open("GET", url, /*async*/true);
    http.onreadystatechange = function() {
      if (http.readyState == 4) {
        var ended = performance.now();
        var milliseconds = ended - started;
        resolve(milliseconds);
      }
    };
    try {
      http.send(null);
    } catch(exception) {
      // this is expected
    }
  })
}

(async () => {
  let promises = [];
  for (var i=0; i <= N; i++) {
    promises.push(ping("https://incolumitas.com"));
  }
  Promise.all(promises).then((results) => {
    results.sort((a, b) => a - b);
    let median = null;
    let m1 = Math.floor(results.length / 2);
    let m2 = Math.ceil(results.length / 2);
    if (results.length % 2 == 0) {
      median = (results[m1] + results[m2]) / 2;
    } else {
      median = results[m1];
    }
    console.log('median', median);
    console.log('measurements', results);
  });
})()
```

The above code gives me the following result on `incolumitas.com`:

```JavaScript
median 126.5
measurements [41.5, 91.5, 108.70000000298023, 121.19999999925494, 124.89999999850988, 126.5, 126.70000000298023, 130.09999999776483, 130.19999999925494, 145.10000000149012, 145.5]
```

However, there is a big problem. Using `XMLHttpRequest` to measure latencies gives wrong results. A substantial part of the latency does not come from the round trip time, but from browser networking internal things such as 

+ Resource Scheduling, Queueing
+ Connection start such as stalling, DNS lookup (negligible), initial connection, SSL

What we really want is the `Waiting (TTFB)` part. See the image below taken from the Dev Console network tab:	

<figure>
    <img src="{static}/images/requestTiming.png" alt="Waiting (TTFB)" />
    <figcaption>I am only interested in the Waiting (TTFB) part.</figcaption>
</figure>

## Second Idea: Obtain the browser -> server Latency with WebSockets

Seeing the latency measurements problems with the `XMLHttpRequest` technique from above, it's time to try out WebSockets in order to get more accurate latency (RTT) measurements with JavaScript.

I am not interested in the WebSocket connection establishment latency, I only want the latency between `socket.send()` and `socket.recv()` functions. All my WebSocket server does it to send the message back. It's a simple echo server. On each `socket.send()`, I send the `performance.now()` relative timestamp with the message. That way, I can interpolate the latency.

The good thing with WebSockets: There is zero incentive to delay or stall WebSocket messages once the connection is established. This gives us accurate samples.

This is the WebSocket latency measurement code and here is a link to the live test site: [https://bot.incolumitas.com/ws-latency.html](https://bot.incolumitas.com/ws-latency.html).

```html
<!doctype html>

<html>
  <head>
    <meta charset = "utf-8">
    <title>WebSocket Latency Check</title>
    <meta name ="description" content="fu">
    <meta name ="author" content="NT">
  </head>

  <body>
    <pre id="data"></pre>
    <script>
      function roundToTwo(num) {    
        return +(Math.round(num + "e+2")  + "e-2");
      }

      // Create a Web Socket
      const socket = new WebSocket('wss://abs.incolumitas.com:5555/');

      socket.onerror = function (err) {
        console.log(err.toString());
      }

      var messages = [];

      socket.onopen = function () {
        socket.send(JSON.stringify({
          type: 'ws-latency',
          ts: roundToTwo(performance.now()),
        }));
      }

      socket.onmessage = function (event) {
        messages.push(JSON.parse(event.data));
        document.getElementById('data').innerHTML = JSON.stringify(messages, null, 2);
        if (messages.length <= 2) {
          socket.send(JSON.stringify({
            type: 'ws-latency',
            ts: roundToTwo(performance.now()),
          }));
        }
      }
    </script>
  </body>
</html>
```

Example value with my local browser:

```JavaScript
[
  {
    "type": "ws-latency",
    "ts": 159.7
  },
  {
    "type": "ws-latency",
    "ts": 183.3
  },
  {
    "type": "ws-latency",
    "ts": 210.5
  }
]
```

Those are very promising results. WebSockets don't suffer from internal queuing and stalling issues such as the `XMLHttpRequest` object. This gives us much more accurate data to work with.

Furthermore, we can also inspect the corresponding latencies for the incoming WebSocket messages on the server side.

If the latencies don't match with a very low margin of error, then there is likely a tunnel or proxy in between.

## Obtain External IP -> Web Server Latency with TCP/IP handshake RTT

This is a bit more complex, because I have to hook into the raw TCP/IP handshake. Without much explanation, the Python script below does the job:

```Python
from pypacker import ppcap
from pypacker.layer12 import ethernet
from pypacker.layer12 import linuxcc
from pypacker.layer3 import ip
from pypacker.layer3 import icmp
from pypacker.layer4 import tcp
from pypacker.layer4 import udp
from pypacker import pypacker
import pcapy
import getopt
import time
import sys
import traceback
import signal
import json

classify = False
interface = None
verbose = False
rtts = {}


def updateFile():
  print('writing RTTs.json with {} objects...'.format(len(rtts)))
  with open('RTTs.json', 'w') as fp:
    json.dump(rtts, fp, indent=2, sort_keys=False)


def signal_handler(sig, frame):
  updateFile()
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler) # ctlr + c
signal.signal(signal.SIGTSTP, signal_handler) # ctlr + z


def tcpProcess(pkt, layer, ts):
  """
  Understand this: https://www.keycdn.com/support/tcp-flags

  from src -> dst, SYN
  from dst -> src, SYN-ACK
  from src -> dst, ACK

  I want the time between SYN-ACK and first ACK
  """
  ip4 = pkt.upper_layer
  tcp1 = pkt.upper_layer.upper_layer

  # SYN (1 bit): Synchronize sequence numbers. Only the first packet sent from each
  # end should have this flag set. Some other flags and fields change meaning
  # based on this flag, and some are only valid when it is set, and others when it is clear.
  if tcp1.flags:
    label = ''
    key = '%s:%s' % (pkt[ip.IP].src_s, pkt[tcp.TCP].sport)
    if key not in rtts:
      rtts[key] = {}
    if (tcp1.flags & tcp.TH_SYN) and not (tcp1.flags & tcp.TH_ACK):
      label = 'SYN'
      if not label in rtts[key]:
        rtts[key][label] = time.time()
    if (tcp1.flags & tcp.TH_ACK) and not (tcp1.flags & tcp.TH_SYN):
      label = 'ACK'
      if 'SYN+ACK' in rtts[key] and 'ACK' not in rtts[key]:
        rtts[key][label] = time.time()
    if (tcp1.flags & tcp.TH_SYN) and (tcp1.flags & tcp.TH_ACK):
      key = '%s:%s' % (pkt[ip.IP].dst_s, pkt[tcp.TCP].dport)
      label = 'SYN+ACK'
      if not label in rtts[key]:
        rtts[key][label] = time.time()

    if "SYN+ACK" in rtts[key] and "ACK" in rtts[key] and not 'RTT' in rtts[key]:
      rtts[key]['RTT'] = '%sms' % round(((rtts[key]["ACK"] - rtts[key]["SYN+ACK"]) * 1000), 2)
      rtts[key]['RTT2'] = round(rtts[key]["ACK"] - rtts[key]["SYN+ACK"], 4)
      print("%d: %s:%s -> %s:%s [%s], RTT=%s" % (ts, pkt[ip.IP].src_s, pkt[tcp.TCP].sport,
          pkt[ip.IP].dst_s, pkt[tcp.TCP].dport, label, rtts[key]['RTT']))


def usage():
  print("""
    -i, --interface   interface to listen to; example: -i eth0
    -l, --log         log file to write output to; example -l output.txt (not implemented yet)
    -v, --verbose     verbose logging, mostly just telling you where/what we're doing, not recommended if want to parse output typically""")


def main():
  logger = pypacker.logging.getLogger("pypacker")
  pypacker.logger.setLevel(pypacker.logging.ERROR)

  counter = 0
  startTime = time.time()

  print('listening on interface {}'.format(interface))

  try:
    preader = pcapy.open_live(interface, 65536, False, 1)
    preader.setfilter('tcp port 80 or tcp port 443')
  except Exception as e:
    print(e, end='\n', flush=True)
    sys.exit(1)

  while True:
    try:
      counter = counter + 1
      (header, buf) = preader.next()
      ts = header.getts()[0]

      tcpPacket = False
      pkt = None
      layer = None

      # try to determine what type of packets we have, there is the chance that 0x800
      # may be in the spot we're checking, may want to add better testing in future
      eth = ethernet.Ethernet(buf)
      if hex(eth.type) == '0x800':
        layer = 'eth'
        pkt = eth

        if (eth[ethernet.Ethernet, ip.IP, tcp.TCP] is not None):
          tcpPacket = True

      lcc = linuxcc.LinuxCC(buf)
      if hex(lcc.type) == '0x800':
        layer = 'lcc'
        pkt = lcc

        if (lcc[linuxcc.LinuxCC, ip.IP, tcp.TCP] is not None):
          tcpPacket = True

      if tcpPacket and pkt and layer:
        tcpProcess(pkt, layer, ts)

    except (KeyboardInterrupt, SystemExit):
      raise
    except Exception as e:
      error_string = traceback.format_exc()
      print(str(error_string))

try:
  opts, args = getopt.getopt(sys.argv[1:], "i:v:c:", ['interface=', 'verbose'])
  proceed = False

  for opt, val in opts:
    if opt in ('-i', '--interface'):
      interface = val
      proceed = True
    if opt in ('-v', '--verbose'):
      verbose = True

  if (__name__ == '__main__') and proceed:
    main()
  else:
    print('Need to provide a pcap to read in or an interface to watch', end='\n', flush=True)
    usage()
except getopt.error:
  usage()
```

Save the above script on your server as `lat.py` and run it with:

```bash
python lat.py -i eth0
```

My RTT measurement tool will produce the following output. The sample was taken from someone from South America visiting my blog:

```JavaScript
1623092439: 192.123.255.204:65238 -> 167.99.241.135:443 [ACK], RTT=231.72ms
1623092439: 192.123.255.204:65237 -> 167.99.241.135:443 [ACK], RTT=239.88ms
1623092439: 192.123.255.204:65240 -> 167.99.241.135:443 [ACK], RTT=239.9ms
1623092440: 192.123.255.204:65243 -> 167.99.241.135:443 [ACK], RTT=239.88ms
1623092440: 192.123.255.204:65244 -> 167.99.241.135:443 [ACK], RTT=231.86ms
1623092441: 192.123.255.204:65248 -> 167.99.241.135:443 [ACK], RTT=240.3ms
1623092441: 192.123.255.204:65251 -> 167.99.241.135:443 [ACK], RTT=244.61ms
1623092441: 192.123.255.204:65253 -> 167.99.241.135:443 [ACK], RTT=239.75ms
1623092442: 192.123.255.204:65254 -> 167.99.241.135:443 [ACK], RTT=241.58ms
1623092444: 192.123.255.204:65258 -> 167.99.241.135:443 [ACK], RTT=239.84ms
1623092444: 192.123.255.204:65259 -> 167.99.241.135:443 [ACK], RTT=240.11ms
```

## Testing the XMLHttpRequest Latency Technique

I will visit the following detection test site: [https://bot.incolumitas.com/latency.html](https://bot.incolumitas.com/latency.html) twice:

1. Once with my normal browser without any proxy
2. The second time with a scraping service that uses a proxy

And on the server side, I will let my TCP/IP latency measurement tool running.

#### Visiting with my normal browser without Proxy

Latencies recorded from the TCP/IP handshake:

```JavaScript
1623144210: 84.151.230.146:33724 -> 167.99.241.135:443 [ACK], RTT=15.79ms
1623144211: 84.151.230.146:33726 -> 167.99.241.135:443 [ACK], RTT=23.87ms
1623144211: 84.151.230.146:33728 -> 167.99.241.135:443 [ACK], RTT=15.82ms
1623144211: 84.151.230.146:33732 -> 167.99.241.135:443 [ACK], RTT=15.53ms
1623144211: 84.151.230.146:33736 -> 167.99.241.135:443 [ACK], RTT=16.08ms
1623144211: 84.151.230.146:33730 -> 167.99.241.135:443 [ACK], RTT=23.66ms
1623144211: 84.151.230.146:33734 -> 167.99.241.135:443 [ACK], RTT=23.66ms
1623144211: 84.151.230.146:33738 -> 167.99.241.135:443 [ACK], RTT=23.18ms
1623144211: 84.151.230.146:33740 -> 167.99.241.135:443 [ACK], RTT=15.92ms
1623144211: 84.151.230.146:33742 -> 167.99.241.135:443 [ACK], RTT=15.32ms
1623144211: 84.151.230.146:33746 -> 167.99.241.135:443 [ACK], RTT=23.64ms
1623144211: 84.151.230.146:33744 -> 167.99.241.135:443 [ACK], RTT=24.43ms
```

Latencies recorded from the browser with JavaScript

```JavaScript
{
  "median": 136.4,
  "measurements": [
    109.9,
    116.2,
    124.8,
    134.4,
    134.6,
    136.4,
    165,
    175,
    181.5,
    190.5,
    196
  ]
}
```

#### Visiting with a Scraping Service that uses a Proxy

Latencies recorded from the TCP/IP handshake:

```JavaScript
1623144996: 24.125.86.142:56938 -> 167.99.241.135:443 [ACK], RTT=127.85ms
1623144997: 24.125.86.142:55420 -> 167.99.241.135:443 [ACK], RTT=183.9ms
1623144997: 24.125.86.142:37906 -> 167.99.241.135:443 [ACK], RTT=127.97ms
1623144997: 24.125.86.142:52654 -> 167.99.241.135:443 [ACK], RTT=120.19ms
1623144997: 24.125.86.142:41199 -> 167.99.241.135:443 [ACK], RTT=127.78ms
1623144997: 24.125.86.142:42204 -> 167.99.241.135:443 [ACK], RTT=127.82ms
1623144997: 24.125.86.142:47526 -> 167.99.241.135:443 [ACK], RTT=136.08ms
```

Latencies recorded from the browser with JavaScript

```JavaScript
{
  "median": 1147.83,
  "measurements": [
    871.23,
    977.15,
    979.31,
    1012.47,
    1034.18,
    1147.83,
    1190.57,
    1229.74,
    1276.93,
    1287.49,
    1318.97
  ]
}
```

#### Conclusion

Browser -> Server with Proxy: `1100ms`
Server -> External IP with Proxy: `120ms`

Browser -> Server without Proxy: `136ms`
Server -> External IP with Proxy: `20ms`

Factor Proxy = `1100 / 120 = 9`
Factor no Proxy = `136 / 20 = 6.8`

Those are definitely not enough samples. I needed to record real world samples with people all over the world
visiting the above JavaScript. After having collected enough samples, I can definitely say that the `XMLHttpRequest` technique to measure latencies is too inaccurate. Therefore, the test site [https://bot.incolumitas.com/latency.html](https://bot.incolumitas.com/latency.html) is not usable to detect tunnels such as Proxies or VPN's.