Title: How to find out if an IP address belongs to a Hosting / Cloud Provider?
Status: published
Date: 2022-03-09 17:45
Modified: 2022-03-13 22:48
Category: Security
Tags: API, Datacenter, Hosting, Cloud-Provider, IP API, Bot-Detection, VPN-Detection, IP-Intelligence, IP-Lookup
Slug: find-out-if-an-IP-address-belongs-to-a-hosting-provider
Author: Nikolai Tschacher
Summary: It is not entirely trivial to find out if an IP address belongs to a datacenter / cloud provider. In this blog article, I try to find an algorithm that outputs with high confidence if an IPv4 / Ipv6 address belongs to a hosting provider or not.

<a class="orange_button" href="https://incolumitas.com/pages/Datacenter-IP-API/">Also check the Datacenter IP address API site</a>

## Introduction

In the field of IT-Security, it is often paramount to find the *reputation* of an IP address.
The reputation of an IP address is an abstract construct, but it consists of several factors:

1. How trustworthy is the underlying network provider / ISP? Is it known for spam and fraud?
2. How easy is it for third parties to send traffic in the name of it's network? Put differenty: Can I purchase hosting services from said provider?
3. How stringent are the steps to obtain an IP address in a legal sense? For example, in order to obtain a mobile SIM card, in many countries of the world, [you need to identify with your passport upon mobile contract settlement](https://prepaid-data-sim-card.fandom.com/wiki/Registration_Policies_Per_Country).
4. Where is the IP address located geographically? There are countries with an higher reputation and countries with lower reputation.

The reputation of an IP address boils down to the question:

> How hard is it for anonymous third parties to obtain IP addresses (preferrably in large quantities) from a network without having to undergo a strict identification process (in a legal sense - showing an ID card or passport)?

Datacenters and cloud providers such as [DigitalOcean](https://www.digitalocean.com/), [Hetzner](https://www.hetzner.com/), [OVH](https://www.ovhcloud.com/en/), [Amazon AWS](https://aws.amazon.com/) and [Microsoft Azure](https://azure.microsoft.com/en-us/) allow third parties to rent hosting infrastructure and thus give them access to their network. Those data centers make it relatively easy for third-parties to send traffic from their network.

For example, there are many projects that make use of the Amazon AWS infrastructure to proxy traffic through their network. One such example is the [Ge0rg3/requests-ip-rotator](https://github.com/Ge0rg3/requests-ip-rotator) library, which allows to *utilize AWS API Gateway's large IP pool as a proxy to generate pseudo-infinite IPs for web scraping and brute forcing.*

Therefore, if a IP address can be traced to a datacenter / cloud provider, it can be conjured that the resulting traffic is of lower reputation, since it is very easy to rent hosting/network infrastructure in large quantities. In reality, most website visitors with a datacenter IP address are probably in 99% of the cases bots.

In this blog article, a straightforward technical process is developed, that determines if an IP address belongs to a datacenter or not.

## An Algorithm that checks if an IP address belongs to a Hosting / Cloud Provider

#### Lookup in Self-Published IP-Ranges from Datacenters

First, check if the IP is to be found in self-published IP-ranges (Often in CIDR format) from datacenter providers. Not every datacenter provider publishes their IP-ranges. And sometimes, the publishes IP ranges are incomplete. But it certainly makes sense to incorporate self-published datacenter IP ranges.

1. Amazon AWS publishes their IP ranges: [Amazon AWS IP ranges](https://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html)
2. Google Cloud also publishes their IP ranges: [Google Cloud IP ranges](https://www.gstatic.com/ipranges/cloud.json)
3. Counterexample: [Hetzner.com](https://www.hetzner.com/) does not publish their IP ranges!


Obviously, self-published IP ranges are not sufficient. Most datacenters do not publish their complete set of IP ranges. Other sources have to be considered. One obvious source is `whois` data.

#### Whois/RDAP Lookups

If an IP address is not found in self-published IP ranges from datacenters, a [Whois/RDAP lookup](https://www.arin.net/resources/registry/whois/) of the IP address is conducted (Example: `whois 105.226.177.72 | grep -E -i "(OrgName:|address:|OrgTechName:|descr:)"`). If the name of the organization belongs to a datacenter, we have a match. This is a simple string matching approach.

Downside: Whois/RDAP lookups do not scale and it's an expensive operation in terms of time (A TCP/IP connection has to be established). Whois/RDAP servers could and will block a single API server after many requests.

Whois lookups can be improved when you specify the whois database manually, so it's possible to load balance to some extent:

```bash
$ whois -h whois.radb.net 138.197.186.3

route:      138.197.176.0/20
changed:    noc@digitalocean.com 20180515  #16:51:53Z
member-of:  RS-Digitalocean
origin:     AS14061
source:     RADB
descr:      DigitalOcean
mnt-by:     MAINT-AS14061
```

You can also make direkt RDAP queries:

```bash
curl https://rdap.arin.net/registry/ip/18.236.125.255
```

The [RIPE-NCC whois database is documented here](https://github.com/RIPE-NCC/whois/wiki/WHOIS-REST-API) and [here](https://www.ripe.net/manage-ips-and-asns/db/support/documentation/ripe-database-documentation).

This is how a API request to the [RIPE-NCC whois database](https://github.com/RIPE-NCC/whois/wiki/WHOIS-REST-API) looks like:

```bash
curl -i -H "Accept: application/json" -H "Content-Type: application/json" https://rest.db.ripe.net/RIPE/inetnum/18.236.125.255
```

Other third party API's such as the one from `whois.radb.net` may be used:

```
curl 'https://rest.db.ripe.net/search.json?query-string=77.247.84.129'
whois -h whois.radb.net 77.247.84.129
echo '77.247.84.129' | nc whois.radb.net 43
```

#### ASN Lookups

Some Regional Internet Registries publish lists of AS numbers and the associated companies.

[Example ASN list for RIPE-NCC](https://ftp.ripe.net/ripe/asnames/).

Excerpt:

```text
[...]
24928 NORDEAPL-AS Nordea Bank Polska SA, PL
24929 NGCS IT arte Sp. z o.o., PL
24931 DEDIPOWER Pulsant Limited, GB
24933 MINXS-AS MILLENNIUMS.NET GmbH, DE
24935 ATE-AS AVENIR TELEMATIQUE SAS, FR
24936 RIM2000M-AS Plusinfo OOO, RU
24937 UNTN PJSC "Ukrtelecom", UA
24938 TELECITYREDBUS-IT TELECITYGROUP INTERNATIONAL LIMITED, GB
24939 IVV ivv Informationsverarbeitung fuer Versicherungen GmbH, DE
24940 HETZNER-AS Hetzner Online GmbH, DE
24941 -Reserved AS-, ZZ
24944 ARENA-AS Arena Bilgisayar San. ve Tic A.S, TR
24945 ASN-VNTP Telecommunication Company Vinteleport Ltd., UA
24947 OZ-IP-Transit Parsun Network Solutions PTY LTD, AU
24949 BTCML-AXA-AS AXA Technology Services UK Limited, GB
24950 SOFIASAT-AS Venus REIT OOD, BG
[...]
```

The idea is to lookup well known database names in this ASN lists and then perform a search such as:

```bash
echo 'AS24940' | nc whois.radb.net 43
```

#### Download whois databases from Region Internet Registries (RIR)

There are six regional internet registries:

1. RIPE NCC (Established in 1992)
2. APNIC (Established in 1993)
3. ARIN (Established in 1997)
4. LACNIC (Established in 1999)
5. NRO (Established in 2003)
6. AFRINIC (Established in 2004)

Almost all of them publish `whois` databases on their FTP servers.

The whois databases for the RIRs can be found here (**Careful**, some of those links download large files):

+ [AFRINIC whois database](https://ftp.afrinic.net/pub/dbase/afrinic.db.gz)
+ [APNIC whois database](https://ftp.apnic.net/apnic/whois/)
+ [LACNIC whois database](https://ftp.lacnic.net/lacnic/dbase/lacnic.db.gz)
+ [ARIN whois database](https://ftp.arin.net/pub/rr/arin.db.gz)
+ [RIPE-NCC whois database](https://ftp.ripe.net/ripe/dbase/ripe.db.gz)

The [RIPE-NCC database](https://ftp.ripe.net/ripe/dbase/ripe.db.gz) is quite large:

```bash
curl -I https://ftp.ripe.net/ripe/dbase/ripe.db.gz

HTTP/1.1 200 OK
Date: Sun, 13 Mar 2022 21:07:26 GMT
Server: Apache
Last-Modified: Sun, 13 Mar 2022 01:57:42 GMT
ETag: "16382ea0-5da0fe3b0d490"
Accept-Ranges: bytes
Content-Length: 372780704
Content-Type: application/x-gzip
```

Uncompressed, the RIPE-NCC database is 5.5GB large. 

Whois databases (which are in fact simple text files) do not follow any standard format, so the informational content varies along different RIRs.

But this is still by far the best source of data in order to infer whether an IP belongs to a datacenter or not.

#### Reverse DNS Lookups

Reverse DNS Lookups could also be an idea. Sometimes reverse DNS queries for an IP address reveal that the IP address belongs to a datacenter. Obvious downside: DNS queries are slow!

```bash
dig -x 167.99.241.135

;; AUTHORITY SECTION:
241.99.167.in-addr.arpa. 1800	IN	SOA	ns1.digitalocean.com. hostmaster.241.99.167.in-addr.arpa. 1647194251 10800 3600 604800 1800
```



