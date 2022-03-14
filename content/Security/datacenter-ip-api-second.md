Title: How to find out if an IP address belongs to a Hosting / Cloud Provider?
Status: published
Date: 2022-03-09 17:45
Modified: 2022-03-14 14:48
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

Therefore, if a IP address can be traced to a datacenter / cloud provider, it can be conjured that the resulting traffic is of lower reputation, since it is very easy to rent hosting/network infrastructure in large quantities for any party. In reality, most website visitors that come from datacenter IP address ranges are probably in 99% of all cases bots.

In this blog article, a straightforward technical process is presented, that determines if an IP address belongs to a datacenter or not.

## Sources/Algorithms for checking whether an IP address belongs to a Hosting / Cloud Provider

### Idea 1: Lookup in Self-Published IP-Ranges from Datacenters

First, check if the IP is to be found in self-published IP-ranges (Often in CIDR format) from datacenter providers. Not every datacenter provider publishes their IP-ranges. And sometimes, the publishes IP ranges are incomplete. But it certainly makes sense to incorporate self-published datacenter IP ranges in the lookup process.

1. Amazon AWS publishes their IP ranges: [Amazon AWS IP ranges](https://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html)
2. Google Cloud also publishes their IP ranges: [Google Cloud IP ranges](https://www.gstatic.com/ipranges/cloud.json)
3. Counterexample: [Hetzner.com](https://www.hetzner.com/) does not publish IP ranges!
4. Counterexample: [OVH Cloud](https://www.ovhcloud.com/en/) also doesn't publish IP ranges...

This is how those published IP ranges look like (excerpt) from [Google Cloud](https://www.gstatic.com/ipranges/cloud.json):

```json
{
  "syncToken": "1647190988307",
  "creationTime": "2022-03-13T10:03:08.30788",
  "prefixes": [{
    "ipv4Prefix": "35.185.128.0/19",
    "service": "Google Cloud",
    "scope": "asia-east1"
  }, {
    "ipv4Prefix": "35.185.160.0/20",
    "service": "Google Cloud",
    "scope": "asia-east1"
  }, {
    "ipv4Prefix": "35.187.144.0/20",
    "service": "Google Cloud",
    "scope": "asia-east1"
  }, {
    "ipv4Prefix": "35.189.160.0/19",
    "service": "Google Cloud",
    "scope": "asia-east1"
  }, {
    "ipv4Prefix": "35.201.128.0/17",
    "service": "Google Cloud",
    "scope": "asia-east1"
  }
]
```

Obviously, self-published IP ranges are not sufficient. Most datacenters do not publish their complete set of IP ranges. Other sources have to be considered. One obvious source is `whois` data from Regional Internet registries (RIR). The task of RIRs is to:

> Manage the allocation and registration of Internet number resources within a region of the world. Internet number resources include IP addresses and autonomous system (AS) numbers.

### Idea 2: Whois/RDAP Lookups

If an IP address is not found in self-published IP ranges from datacenters, a [Whois/RDAP lookup](https://www.arin.net/resources/registry/whois/) of the IP address can be conducted. Example:

```bash
whois 105.226.177.72 | grep -E -i "(OrgName:|address:|OrgTechName:|descr:)"
```

If the name of the organization belongs to a datacenter, we have a match. This is a simple string matching approach.

Downside: Whois/RDAP lookups do not scale and it's an expensive operation in terms of time (A TCP/IP connection has to be established). Whois/RDAP servers could and will block a single server after many requests.

In fact, [ripe.net states the following](https://www.ripe.net/manage-ips-and-asns/db/support/querying-the-ripe-database):

> Please note that when searching for resources such as an IP address block or AS Number, contact information from related objects will automatically be returned as well. You can only query for a limited amount of personal information every day. After reaching that limit, you will be blocked from making further queries. To disable automatic queries for personal information, please use the "-r" flag, as explained in the Advanced Queries section.

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

# snip
"handle" : "AEA8-ARIN",
"vcardArray" : [ "vcard", [ [ "version", { }, "text", "4.0" ], [ "adr", {
"label" : "Amazon Web Services Elastic Compute Cloud, EC2\n410 Terry Avenue North\nSeattle\nWA\n98109-5210\nUnited States"
}, "text", [ "", "", "", "", "", "", "" ] ], [ "fn", { }, "text", "Amazon EC2 Abuse" ], [ "org", { }, "text", "Amazon EC2 Abuse" ], [ "kind", { }, "text", "group" ], [ "email", { }, "text", "abuse@amazonaws.com" ], [ "tel", {
"type" : [ "work", "voice" ]
}, "text", "+1-206-266-4064" ] ] ],
"roles" : [ "abuse" ],
"remarks" : [ {
"title" : "Registration Comments",
# snip
```

The [RIPE-NCC whois database is documented here](https://github.com/RIPE-NCC/whois/wiki/WHOIS-REST-API) and [on www.ripe.net](https://www.ripe.net/manage-ips-and-asns/db/support/documentation/ripe-database-documentation).

There also exists a good tutorial on [Querying the RIPE Database](https://www.ripe.net/manage-ips-and-asns/db/support/querying-the-ripe-database).

This is how a API request to the [RIPE-NCC whois database](https://github.com/RIPE-NCC/whois/wiki/WHOIS-REST-API) look like with curl. [Here is an example API lookup](https://www.ripe.net/manage-ips-and-asns/db/support/documentation/ripe-database-documentation/how-to-query-the-ripe-database/restful-api-queries/api-lookup) which looks up an [inetnum object](https://www.ripe.net/manage-ips-and-asns/db/support/documentation/ripe-database-documentation/rpsl-object-types/4-2-descriptions-of-primary-objects/4-2-4-description-of-the-inetnum-object) (API output modified for brevity):

```bash
curl -H 'Accept: application/json' 'https://rest.db.ripe.net/ripe/inetnum/193.0.0.0%20-%20193.0.7.255?unfiltered'

{
   "objects":{
      "object":[
         {
            "type":"inetnum",
            "link":{
               "type":"locator",
               "href":"https://rest.db.ripe.net/ripe/inetnum/193.0.0.0 - 193.0.7.255"
            },
            "source":{
               "id":"ripe"
            },
            "primary-key":{
               "attribute":[
                  {
                     "name":"inetnum",
                     "value":"193.0.0.0 - 193.0.7.255"
                  }
               ]
            },
            "attributes":{
               "attribute":[
                  {
                     "name":"inetnum",
                     "value":"193.0.0.0 - 193.0.7.255"
                  },
                  {
                     "name":"netname",
                     "value":"RIPE-NCC"
                  },
                  {
                     "name":"descr",
                     "value":"RIPE Network Coordination Centre"
                  },
                  {
                     "link":{
                        "type":"locator",
                        "href":"https://rest.db.ripe.net/ripe/organisation/ORG-RIEN1-RIPE"
                     },
                     "name":"org",
                     "value":"ORG-RIEN1-RIPE",
                     "referenced-type":"organisation"
                  },
                  {
                     "name":"descr",
                     "value":"Amsterdam, Netherlands"
                  },
                  {
                     "name":"remarks",
                     "value":"Used for RIPE NCC infrastructure."
                  },
                  {
                     "name":"country",
                     "value":"NL"
                  },
               ]
            }
         }
      ]
   }
}
```

You can also look up other whois data objects such as:

+ [AUT-NUM Object](https://www.ripe.net/manage-ips-and-asns/db/support/documentation/ripe-database-documentation/rpsl-object-types/4-2-descriptions-of-primary-objects/4-2-1-description-of-the-aut-num-object)
+ [DOMAIN Object](https://www.ripe.net/manage-ips-and-asns/db/support/documentation/ripe-database-documentation/rpsl-object-types/4-2-descriptions-of-primary-objects/4-2-2-description-of-the-domain-object)
+ [INET6NUM Object](https://www.ripe.net/manage-ips-and-asns/db/support/documentation/ripe-database-documentation/rpsl-object-types/4-2-descriptions-of-primary-objects/4-2-3-description-of-the-inet6num-object)
+ [ROUTE Object](https://www.ripe.net/manage-ips-and-asns/db/support/documentation/ripe-database-documentation/rpsl-object-types/4-2-descriptions-of-primary-objects/4-2-5-description-of-the-route-object)
+ [ROUTE6 Object](https://www.ripe.net/manage-ips-and-asns/db/support/documentation/ripe-database-documentation/rpsl-object-types/4-2-descriptions-of-primary-objects/4-2-6-description-of-the-route6-object)

Another API lookup example:

```bash
curl -H 'Accept: application/json' 'https://rest.db.ripe.net/ripe/route/193.0.0.0%20-%20193.0.7.255?unfiltered'
```


### Idea 3: RIPEstat API

Another excellent ressource from RIPE NCC is the [RIPEstat API](https://stat.ripe.net/docs/01.getting-started/#getting-started-with-ripestat).

What is RIPEstat?

> RIPEstat is a large-scale information service and the RIPE NCC’s open data platform. You can get essential information on IP address space and Autonomous System Numbers (ASNs) along with related statistics on specific hostnames and countries.

Potential downside: API calls are restricted. No possibility to download the database. Only for RIPE-NCC, not the other RIRs. Observation: Seems to be slow?!

For the purpose of finding datacenter IP ranges, the following API endpoints are especially interesting:

#### Endpoint: [Address Space Hierarchy](https://stat.ripe.net/docs/02.data-api/address-space-hierarchy.html)

> This data call returns address space objects (inetnum or inet6num) from the RIPE Database related to the queried resource.

Example:

```bash
curl --location --request GET "https://stat.ripe.net/data/address-space-hierarchy/data.json?resource=193.47.99.0/24"
{
    "data_call_name": "address-space-hierarchy",
    "data_call_status": "supported",
    "cached": false,
    "data": {
        "rir": "ripe",
        "resource": "193.47.99.0/24",
        "exact": [
            {
                "inetnum": "193.47.99.0 - 193.47.99.255",
                "netname": "HETZNER-PORTABLE-PI",
                "country": "DE",
                "org": "ORG-HOA1-RIPE",
                "admin-c": "HOAC1-RIPE",
                "tech-c": "HOAC1-RIPE",
                "status": "ASSIGNED PI",
                "mnt-by": "RIPE-NCC-END-MNTHOS-GUN",
                "mnt-domains": "HOS-GUN",
                "mnt-routes": "HOS-GUNMYLOC-MNT",
                "created": "2005-07-07T15:27:12Z",
                "last-modified": "2016-04-14T08:14:55Z",
                "source": "RIPE"
            }
        ],
        "more_specific": [],
        "query_time": "2022-03-14T13:34:32",
        "parameters": {
            "resource": "193.47.99.0/24"
        }
    },
    "query_id": "20220314133432-07794397-fd21-4a59-b335-af95bcab6d0d",
    "process_time": 116,
}
```

#### Endpoint: [Address Space Usage](https://stat.ripe.net/docs/02.data-api/address-space-usage.html)

> This data call shows the usage of a prefix or IP range according to the objects currently present in the RIPE database. The data returned lists the assignments and allocations covered by the queried resource as well statistics on the total numbers of IPs in the different categories.

Example: 

```bash
curl --location --request GET "https://stat.ripe.net/data/address-space-usage/data.json?resource=95.216.0.0/16"
{
    "data_call_name": "address-space-usage",
    "data_call_status": "supported",
    "cached": false,
    "data": {
        "query_time": "2022-03-13T00:00:00",
        "resource": "95.216.0.0/16",
        "assignments": [
            {
                "address_range": "95.216.0.0/26",
                "asn_name": "HETZNER-hel1-dc2",
                "status": "ASSIGNED PA",
                "parent_allocation": "95.216.0.0/15"
            },
            {
                "address_range": "95.216.0.64/26",
                "asn_name": "HETZNER-hel1-dc2",
                "status": "ASSIGNED PA",
                "parent_allocation": "95.216.0.0/15"
            },
            {
                "address_range": "95.216.0.128/26",
                "asn_name": "HETZNER-hel1-dc2",
                "status": "ASSIGNED PA",
                "parent_allocation": "95.216.0.0/15"
            },
            {
                "address_range": "95.216.0.192/26",
                "asn_name": "HETZNER-hel1-dc2",
                "status": "ASSIGNED PA",
                "parent_allocation": "95.216.0.0/15"
            }
            # snip
        ]
    }
}
```

#### Endpoint: [Announced Prefixes](https://stat.ripe.net/docs/02.data-api/announced-prefixes.html)

> This data call returns all announced prefixes for a given ASN. The results can be restricted to a specific time period.

Example: 

```bash
curl --location --request GET "https://stat.ripe.net/data/announced-prefixes/data.json?resource=24940&starttime=2020-12-12T12:00"
{
    "messages": [
        [
            "info",
            "Results exclude routes with very low visibility (less than 10 RIS full-feed peers seeing)."
        ]
    ],
    "version": "1.2",
    "data_call_name": "announced-prefixes",
    "data_call_status": "supported - connecting to ursa",
    "cached": false,
    "data": {
        "prefixes": [
            {
                "prefix": "185.209.124.0/22",
                "timelines": [
                    {
                        "starttime": "2020-12-12T16:00:00",
                        "endtime": "2022-03-14T08:00:00"
                    }
                ]
            },
            {
                "prefix": "185.171.224.0/22",
                "timelines": [
                    {
                        "starttime": "2020-12-12T16:00:00",
                        "endtime": "2022-03-14T08:00:00"
                    }
                ]
            },
            {
                "prefix": "185.228.8.0/23",
                "timelines": [
                    {
                        "starttime": "2020-12-12T16:00:00",
                        "endtime": "2022-03-14T08:00:00"
                    }
                ]
            },
            {
                "prefix": "195.248.224.0/24",
                "timelines": [
                    {
                        "starttime": "2020-12-12T16:00:00",
                        "endtime": "2022-03-14T08:00:00"
                    }
                ]
            }            
            # snip
        ]
    }
}
```

### Idea 4: ASN Lookups

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

### Idea 5: Download whois databases from Region Internet Registries (RIR)

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

Whois databases (which are in fact simple text files) do store information in records known as objects. These are blocks of text in a standard notation defined in the Routing Policy Specification Language (RPSL). An object has multiple fields, called attributes or keys, that each have a value. Below is an example of a route object: [Source](https://www.ripe.net/manage-ips-and-asns/db/support/querying-the-ripe-database)

```text
route:          5.9.0.0/16
descr:          HETZNER-RZ-FKS-BLK5
origin:         AS24940
mnt-by:         HOS-GUN
created:        2012-04-26T10:30:12Z
last-modified:  2012-04-26T10:30:12Z
source:         RIPE
remarks:        ****************************
remarks:        * THIS OBJECT IS MODIFIED
remarks:        * Please note that all data that is generally regarded as personal
remarks:        * data has been removed from this object.
remarks:        * To view the original object, please query the RIPE Database at:
remarks:        * http://www.ripe.net/whois
remarks:        ****************************
```

Querying those whois databases is still by far the best source of data in order to infer whether an IP belongs to a datacenter or not.

### Idea 6: Reverse DNS Lookups

Reverse DNS Lookups could also be an idea. Sometimes reverse DNS queries for an IP address reveal that the IP address belongs to a datacenter. Obvious downside: DNS queries are slow!

```bash
dig -x 167.99.241.135

;; AUTHORITY SECTION:
241.99.167.in-addr.arpa. 1800	IN	SOA	ns1.digitalocean.com. hostmaster.241.99.167.in-addr.arpa. 1647194251 10800 3600 604800 1800
```

## Conclusion

There are many different sources that are helpful when deciding whether an IP address belongs to a datacenter or not.

But the following steps are essential and most relevant:

1. Self published IP ranges from hosting providers need to be considered
2. The downloadable whois databases from RIR's such as RIPE-NCC or ARIN can be searched.
3. Manual task: A list of datacenters and hosting providers needs to be compiled. With this list of datacenter needles, the whois databases from the RIR's can be searched/grepped.

