Title: MTU/MSS vs VPN
Date: 2021-10-16 12:46
Modified: 2021-10-25 18:46
Category: Security
Tags: vpn, vpn-detection
Slug: mtu-vs-vpn
Summary: Analyzing MTU/MSS tells us whether a incoming TCP/IP connection is tunneled over an VPN.
Author: Nikolai Tschacher
Status: Draft

https://medium.com/@ValdikSS/detecting-vpn-and-its-configuration-and-proxy-users-on-the-server-side-1bcc59742413

https://blog.cloudflare.com/path-mtu-discovery-in-practice/


Find IP ranges belonging to a ASN

```
echo '!as9009'|nc whois.radb.net 43

whois -h whois.radb.net '!gas9009'

whois -h whois.radb.net -- '-i origin AS9009'
```

https://www.peeringdb.com/asn/9009

https://stackoverflow.com/questions/57620307/where-to-get-full-list-of-registered-asn-autonomous-system-number

http://ftp.arin.net/info/asn.txt

https://www.iana.org/numbers

https://bgp.potaroo.net/cidr/autnums.html

https://en.wikipedia.org/wiki/Great_Firewall#Blocking_methods


https://www.zeitgeist.se/2013/11/26/mtu-woes-in-ipsec-tunnels-how-to-fix/

https://security.stackexchange.com/questions/95688/website-knows-that-im-connected-via-openvpn

https://www.hindawi.com/journals/scn/2019/7924690/

https://en.wikipedia.org/wiki/Layer_2_Tunneling_Protocol


## Detecting VPNs with MSS

### OpenVPN

OpenVPN in default mode uses MSS=1361

Enumerate different OpenVPN settings

- connection protocol (IPv4, IPv6)
- transport protocol (UDP, TCP)
- cipher, 
- MAC
- compression 

as they affect MSS.

cat /etc/openvpn/server/server.conf
```
auth SHA512
cipher AES-256-CBC
```

Changing the Android Client

android openvpn, aes-256-gcm, no compression, TCP transport, mss 1361, https://abs.incolumitas.com/showFile?fileName=proxy_test_6-10_139.59.136.53_2021-10-31T21:48:03.810Z.json

android openvpn, aes-256-gcm, no compression, UDP transport, mss 1361, https://abs.incolumitas.com/showFile?fileName=proxy_test_6-10_139.59.136.53_2021-10-31T21:54:02.529Z.json

android openvpn, aes-256-gcm, no compression, compression, UDP transport, mss 1361, https://abs.incolumitas.com/showFile?fileName=proxy_test_6-10_139.59.136.53_2021-10-31T21:56:10.535Z.json

android openvpn, force es-256-cbc, no compression, UDP transport, mss 1289, https://abs.incolumitas.com/showFile?fileName=proxy_test_6-10_139.59.136.53_2021-10-31T21:58:05.415Z.json

android openvpn, aes-256-gcm, compression, UDP transport, mss 1361, https://abs.incolumitas.com/showFile?fileName=proxy_test_6-10_139.59.136.53_2021-10-31T22:02:25.432Z.json

---

cat /etc/openvpn/server/server.conf
```
auth SHA256
cipher AES-128-GCM
```

android openvpn, aes-256-gcm, UDP transport, mss 1361, https://abs.incolumitas.com/showFile?fileName=proxy_test_6-10_139.59.136.53_2021-10-31T22:02:25.432Z.json

ubuntu openvpn3, AES-128-GCM, SHA256, UDP transport, mss 1361, https://abs.incolumitas.com/showFile?fileName=proxy_test_6-10_139.59.136.53_2021-10-31T22:02:25.432Z.json


=> MSS seems to stay 1361 regardless of OS.

Confirmed on iOS apple iPhone: 

mss 1361, https://abs.incolumitas.com/showFile?fileName=proxy_test_4-9_139.59.136.53_2021-10-31T22:39:56.116Z.json

Maybe it's not the VPN client that determines the MSS, maybe it's the VPN server?


```
AES-128-CBC  (128 bit key, 128 bit block)
AES-128-CFB  (128 bit key, 128 bit block, TLS client/server mode only)
AES-128-CFB1  (128 bit key, 128 bit block, TLS client/server mode only)
AES-128-CFB8  (128 bit key, 128 bit block, TLS client/server mode only)
AES-128-GCM  (128 bit key, 128 bit block, TLS client/server mode only)
AES-128-OFB  (128 bit key, 128 bit block, TLS client/server mode only)
AES-192-CBC  (192 bit key, 128 bit block)
AES-192-CFB  (192 bit key, 128 bit block, TLS client/server mode only)
AES-192-CFB1  (192 bit key, 128 bit block, TLS client/server mode only)
AES-192-CFB8  (192 bit key, 128 bit block, TLS client/server mode only)
AES-192-GCM  (192 bit key, 128 bit block, TLS client/server mode only)
AES-192-OFB  (192 bit key, 128 bit block, TLS client/server mode only)
AES-256-CBC  (256 bit key, 128 bit block)
AES-256-CFB  (256 bit key, 128 bit block, TLS client/server mode only)
AES-256-CFB1  (256 bit key, 128 bit block, TLS client/server mode only)
AES-256-CFB8  (256 bit key, 128 bit block, TLS client/server mode only)
AES-256-GCM  (256 bit key, 128 bit block, TLS client/server mode only)
AES-256-OFB  (256 bit key, 128 bit block, TLS client/server mode only)
ARIA-128-CBC  (128 bit key, 128 bit block)
ARIA-128-CFB  (128 bit key, 128 bit block, TLS client/server mode only)
ARIA-128-CFB1  (128 bit key, 128 bit block, TLS client/server mode only)
ARIA-128-CFB8  (128 bit key, 128 bit block, TLS client/server mode only)
ARIA-128-GCM  (128 bit key, 128 bit block, TLS client/server mode only)
ARIA-128-OFB  (128 bit key, 128 bit block, TLS client/server mode only)
ARIA-192-CBC  (192 bit key, 128 bit block)
ARIA-192-CFB  (192 bit key, 128 bit block, TLS client/server mode only)
ARIA-192-CFB1  (192 bit key, 128 bit block, TLS client/server mode only)
ARIA-192-CFB8  (192 bit key, 128 bit block, TLS client/server mode only)
ARIA-192-GCM  (192 bit key, 128 bit block, TLS client/server mode only)
ARIA-192-OFB  (192 bit key, 128 bit block, TLS client/server mode only)
ARIA-256-CBC  (256 bit key, 128 bit block)
ARIA-256-CFB  (256 bit key, 128 bit block, TLS client/server mode only)
ARIA-256-CFB1  (256 bit key, 128 bit block, TLS client/server mode only)
ARIA-256-CFB8  (256 bit key, 128 bit block, TLS client/server mode only)
ARIA-256-GCM  (256 bit key, 128 bit block, TLS client/server mode only)
ARIA-256-OFB  (256 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-128-CBC  (128 bit key, 128 bit block)
CAMELLIA-128-CFB  (128 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-128-CFB1  (128 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-128-CFB8  (128 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-128-OFB  (128 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-192-CBC  (192 bit key, 128 bit block)
CAMELLIA-192-CFB  (192 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-192-CFB1  (192 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-192-CFB8  (192 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-192-OFB  (192 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-256-CBC  (256 bit key, 128 bit block)
CAMELLIA-256-CFB  (256 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-256-CFB1  (256 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-256-CFB8  (256 bit key, 128 bit block, TLS client/server mode only)
CAMELLIA-256-OFB  (256 bit key, 128 bit block, TLS client/server mode only)
SEED-CBC  (128 bit key, 128 bit block)
SEED-CFB  (128 bit key, 128 bit block, TLS client/server mode only)
SEED-OFB  (128 bit key, 128 bit block, TLS client/server mode only)
SM4-CBC  (128 bit key, 128 bit block)
SM4-CFB  (128 bit key, 128 bit block, TLS client/server mode only)
SM4-OFB  (128 bit key, 128 bit block, TLS client/server mode only)
```

cipher DES-CBC, "tcp_mss": 1361, https://abs.incolumitas.com/showFile?fileName=proxy_test_5-10_139.59.136.53_2021-11-01T17:49:37.559Z.json

cipher AES-192-GCM, "tcp_mss": 1361, https://abs.incolumitas.com/showFile?fileName=proxy_test_5-10_139.59.136.53_2021-11-01T18:01:33.803Z.json

AES-128-CBC, "tcp_mss": 1361, https://abs.incolumitas.com/showFile?fileName=proxy_test_5-10_139.59.136.53_2021-11-01T18:07:48.500Z.json


```
sudo pkill -f "openvpn3"
```

### WireGuard

Server:

Install from here: https://github.com/angristan/wireguard-install

Client: 

https://www.wireguard.com/

https://www.wireguard.com/install/


normal setup with Android Google Pixel 4a as client: 

"tcp_mss": 1240, https://abs.incolumitas.com/showFile?fileName=proxy_test_6-9_188.166.113.36_2021-11-01T10:57:10.546Z.json

"tcp_mss": 1240, https://abs.incolumitas.com/showFile?fileName=proxy_test_5-9_188.166.113.36_2021-11-01T11:11:59.658Z.json

"tcp_mss": 1240, https://abs.incolumitas.com/showFile?fileName=proxy_test_6-9_188.166.113.36_2021-11-01T11:04:54.950Z.json


https://www.wireguard.com/#simple-network-interface


### LibreSwan

IKEv2 on Ubuntu

L2TP/IPSec PSK

https://github.com/hwdsl2/setup-ipsec-vpn


Setup the client: https://github.com/hwdsl2/setup-ipsec-vpn/blob/master/docs/clients.md#android

```
IPsec VPN server is now ready for use!

Connect to your new VPN with these details:

Server IP: 143.198.148.168
IPsec PSK: ZADinRi2aMXmatZiZjr6
Username: vpnuser
Password: CZoWMMqpcK2bS2Zx

Write these down. You'll need them to connect!

IKEv2 setup successful. Details for IKEv2 mode:

VPN server address: 143.198.148.168
VPN client name: vpnclient

Client configuration is available at:
/root/vpnclient.p12 (for Windows & Linux)
/root/vpnclient.sswan (for Android)
/root/vpnclient.mobileconfig (for iOS & macOS)

*IMPORTANT* Password for client config files:
cLjv6ULyecgUHvv83q
Write this down, you'll need it for import!

Next steps: Configure IKEv2 VPN clients. See:
https://git.io/ikev2clients
```

LibreSwan, "tcp_mss": 1240, https://abs.incolumitas.com/showFile?fileName=proxy_test_4-9_143.198.148.168_2021-11-01T15:06:03.297Z.json

LibreSwan, "tcp_mss": 1240, https://abs.incolumitas.com/showFile?fileName=proxy_test_4-9_143.198.148.168_2021-11-01T15:06:03.297Z.json

LibreSwan, "tcp_mss": 1240, https://abs.incolumitas.com/showFile?fileName=proxy_test_3-9_143.198.148.168_2021-11-01T15:12:57.695Z.json

LibreSwan.pcap, LibreSwan, "tcp_mss": 1240, https://abs.incolumitas.com/showFile?fileName=proxy_test_4-9_143.198.148.168_2021-11-01T15:19:55.545Z.json

LibreSwan2.pcap, LibreSwan, "tcp_mss": 1240, https://abs.incolumitas.com/showFile?fileName=proxy_test_3-9_143.198.148.168_2021-11-01T15:20:48.358Z.json


### Analyze TCP/IP handshake on server side

TCP/IP handshake

```
tcpdump "tcp[tcpflags] & (tcp-syn|tcp-ack) != 0 and (src 188.166.113.36 or dst 188.166.113.36)"
```

All TCP/IP traffic Wireguard

```
tcpdump "src 188.166.113.36 or dst 188.166.113.36" -w wgTraffic.pcap
```

All TCP/IP traffic OpenVPN

```
tcpdump "src 188.166.113.36 or dst 188.166.113.36" -w wgTraffic.pcap
```

All TCP/IP traffic LibreSwan

```
tcpdump "src 143.198.148.168 or dst 143.198.148.168" -w LibreSwan.pcap
```

Download files from server:

```
scp -i ~/.ssh/root_new_server -r root@167.99.241.135:/root/vpn-capture/ .
```