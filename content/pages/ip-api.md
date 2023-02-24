Title: IP Address API
Date: 2022-09-11 22:00
Modified: 2023-02-19 22:00
Author: Nikolai Tschacher
Slug: IP-API
Status: published
Sortorder: 5

| <!-- -->    | <!-- -->    |
|-------------|-------------|
| **Author**         | Nikolai Tschacher ([incolumitas.com](https://incolumitas.com/))     |
| **API Access**         | Free & unlimited (fair use)         |
| **API Version**         | **v0.9.12 (19th February 2023)**         |
| **API Endpoint**         | [https://api.incolumitas.com/?q=3.5.140.2](https://api.incolumitas.com/?q=3.5.140.2)         |
| **Total Tracked Hosting Providers**         |    **[13852 hosting providers]({filename}/pages/datacenters.md)**      |
| **Number of Ipv4 Addresses**         |    **244,808** IPv4 CIDR ranges (596,712,692 Addresses in total)      |
| **Number of Ipv6 Addresses**         |    **286,094** IPv6 CIDR ranges (2.3149930027397343e+33 Addresses in total)      |

## Live API

<div class="ipAPIDemo">
  <label style="font-weight: 600; font-size: 16px" for="ip">IP Address / ASN:</label>
  <input style="padding: 8px; margin-left: 4px; margin-right: 4px" type="text" id="ip" name="ip" value="13.34.52.117">
  <input class="orange_button" style="" type="submit" value="Make API Request" placeholder="IP Address or ASN">

  <div>
    <p><strong>Examples:</strong>
      <a class="api-example" data-query="165.227.176.0" href="#">165.227.176.0</a> —
      <a class="api-example" data-query="43.181.128.0" href="#">43.181.128.0</a> —
      <a class="api-example" data-query="143.81.28.0" href="#">143.81.28.0</a> —
      <a class="api-example" data-query="20.1.28.0" href="#">20.1.28.0</a> —
      <a class="api-example" data-query="194.126.177.0" href="#">194.126.177.0</a> —
      <a class="api-example" data-query="AS209103" href="#">AS209103</a> —
      <a class="api-example" data-query="23.236.48.55" href="#">23.236.48.55</a> —</br>
      <a class="api-example" data-query="2600:1F18:7FFF:F800:0000:ffff:0000:0000" href="#">2600:1F18:7FFF:F800:0000:ffff:0000:0000</a> —
      <a class="api-example" data-query="107.174.138.172" href="#">107.174.138.172</a> —
      <a class="api-example" data-query="107.152.214.169" href="#">107.152.214.169</a>
    </p>
  </div>

  <pre id="wrapper">
    <code id="data"class="JSON hljs">{
  "message": "Please make an API request",
}</code>
  </pre>
</div>

<script>
var el = document.getElementById('data');
hljs.highlightBlock(el);

function makeApiRequest(query) {
  let url = query ? 'https://api.incolumitas.com/?q=' + query : 'https://api.incolumitas.com/';

  fetch(url)
  .then(response => response.json())
  .then(function(data) {
    var el = document.getElementById('data');
    el.innerHTML = JSON.stringify(data, null, 2);
    hljs.highlightBlock(el);
    if (!query) {
      document.getElementById('ip').value = data.ip;
    }
  })
}

let linkNodes = document.querySelectorAll('a.api-example');

for (let node of linkNodes) {
  node.addEventListener('click', function(evt) {
    evt.preventDefault();
    let query = evt.target.getAttribute('data-query');
    document.getElementById('ip').value = query;
    makeApiRequest(query);
  });
}

makeApiRequest('');

document.querySelector('.ipAPIDemo input[type="submit"]').addEventListener('click', function(evt) {
  var ip = document.getElementById('ip').value;
  makeApiRequest(ip)
})
</script>

# Documentation

1. [Quickstart](#quickstart)
2. [Introduction](#introduction)
3. [API Features](#api-features)
    - [ASN Database](#asn-database)
    - [Hosting IP Ranges Database](#hosting-ip-ranges-database)
4. [API Response Format](#api-response-format)
    - [Top Level API Output](#response-format-top-level-api-output)
    - [The `datacenter` object](#response-format-the-datacenter-object)
    - [The `company` object](#response-format-the-company-object)
    - [The `asn` object](#response-format-the-asn-object)
    - [The `location` object](#response-format-the-location-object)
5. [API Endpoints](#api-endpoints)
    - [GET Endpoint](#get-endpoint---lookup-a-single-ip-address-or-asn)
    - [POST Endpoint](#post-endpoint---query-up-to-100-ip-addresses-in-one-api-call)

---

This IP address API returns useful meta-information for IP addresses. For example, the API response includes the organization of the IP address, ASN information and geolocation intelligence and WHOIS data.

Furthermore, the API response allows to derive **security information** for each IP address, for example whether an IP address belongs to a hosting provider (`is_datacenter`), is a TOR exit node (`is_tor`), if an IP address is a proxy (`is_proxy`) or VPN (`is_vpn`) or belongs to an abuser (`is_abuser`).

This API strongly emphasises **datacenter/hosting detection**. A complicated hosting detection algorithm was developed to achieve a high detection rate. [Thousands of different hosting providers](https://incolumitas.com/pages/Hosting-Providers-List/) are tracked. Whois records, public hosting IP ranges from hosting providers and a proprietary hosting discovery algorithm are used to decide whether an IP address belongs to a datacenter or not.

The API includes accurate and rich ASN meta-data. For instance, the API output contains whois information for each active ASN and the ASN type is derived by analyzing the company that owns the AS.

## Quickstart

Lookup any IP address: [https://api.incolumitas.com/?q=3.5.140.2](https://api.incolumitas.com/?q=3.5.140.2)

Lookup your own IP address: [https://api.incolumitas.com/](https://api.incolumitas.com/)

Usage with JavaScript:

```JavaScript
fetch('https://api.incolumitas.com/?q=23.236.48.55')
  .then(res => res.json())
  .then(res => console.log(res));
```

Usage with Curl:

```bash
curl 'https://api.incolumitas.com/?q=32.5.140.2'
```

## Introduction

The IP adddress API makes use of the following data sources:

1. Public whois records from regional Internet address registries such as [RIPE NCC](https://www.ripe.net/), [APNIC](https://www.apnic.net/), [ARIN](https://www.arin.net/) and so on
2. [Public BGP Routing Table Data](https://thyme.apnic.net/current/) for ASN lookups
3. Public blocklists such as [firehol/blocklist-ipset](https://github.com/firehol/blocklist-ipsets)
4. The API uses several proprietary datacenter/hosting detection algorithms
5. Other open source projects that try to find hosting IP addresses such as [github.com/client9/ipcat](https://github.com/client9/ipcat), [github.com/Umkus/ip-index](https://github.com/Umkus/ip-index) or [https://github.com/X4BNet/lists_vpn](github.com/X4BNet/lists_vpn) are also considered
6. The API uses IP threat data from various honeypots
7. IP geolocation information from several different geolocation providers is used. By using more than one geolocation source, a more accurate location can be interpolated.

## API Features

- **Ready for production**: This API can be used in production and is stable
- **Many datacenters supported:** [Thousands of different hosting providers and counting](https://incolumitas.com/pages/Hosting-Providers-List/) - From Huawei Cloud Service to ServerMania Inc. Find out whether the IP address is hosted by looking at the `is_datacenter` property!
- **Always updated**: The API database is automatically updated several times per week.
- **ASN support**: The API provides autonomous system information for each looked up IP address
- **Company Support**: The API provides organisational information for each network of each looked up IP address
- **Bulk IP Lookups**: You can lookup up to 100 IP addresses per API call

### ASN Database

For offline ASN data access, the [**ASN Database**](https://ipapi.is/asn.html) is provided. The ASN database includes all assigned and allocated AS numbers by IANA and respective meta information. The database is updated several times per week. For active ASN's (at least one route/prefix assigned to the AS), the database includes rich meta information. For example, the provided information for the ASN `50673` would be:

```JavaScript
"50673": {
  "asn": "50673",
  "org": "Serverius Holding B.V.",
  "domain": "serverius.net",
  "abuse": "abuse@serverius.net",
  "type": "hosting",
  "created": "2010-09-07",
  "updated": "2022-11-15",
  "rir": "ripe",
  "descr": "SERVERIUS-AS, NL",
  "country": "NL",
  "active": true,
  "prefixes": [
    "2.59.183.0/24",
    "5.56.133.0/24",
    // many more IPv4 prefixes ...
  ],
  "prefixesIPv6": [
    "2001:67c:b0::/48",
    "2a00:1ca8::/32",
    // many more IPv6 prefixes ...
  ]
},
```

The database is in JSON format. The key is the ASN as `int` and the value is an object with AS meta information such as the one above.

[Click here to download the ASN Database](https://github.com/NikolaiT/IP-Address-API)

**How to download & parse the database?**

Download and unzip the ASN database:

```bash
cd /tmp
curl -O https://raw.githubusercontent.com/NikolaiT/IP-Address-API/main/databases/fullASN.json.zip
unzip fullASN.json.zip
```

And parse with nodejs:

```JavaScript
let asnDatabase = require('./fullASN.json');
for (let asn in asnDatabase) {
  console.log(asn, asnDatabase[asn]);
}
```

### Hosting IP Ranges Database

Furthermore, the **Hosting IP ranges Database** is provided for offline and scalable access. This database contains all known datacenter IP ranges in the Internet. A proprietary algorithm was developed to determine if a network belongs to a hosting provider.

The file format of the database is tab separated text file (.tsv), where each line of the file contains the `company`, `network` and `domain` of the hosting provider.

Example excerpt of the database:

```text
Linode, LLC 178.79.160.0 - 178.79.167.255 www.linode.com
OVH Sp. z o. o. 178.32.191.0 - 178.32.191.127 www.ovh.com
myLoc managed IT AG 46.245.176.0 - 46.245.183.255 www.myloc.de
```

[Click here to download the Hosting IP Ranges Database](https://github.com/NikolaiT/IP-Address-API)

**How to download & parse the database?**

Download and unzip the Hosting Ranges database:

```bash
cd /tmp
curl -O https://raw.githubusercontent.com/NikolaiT/IP-Address-API/main/databases/hostingRanges.tsv.zip
unzip hostingRanges.tsv.zip
```

And parse with nodejs:

```JavaScript
const fs = require('fs');

let hostingRanges = fs.readFileSync('hostingRanges.tsv').toString().split('\n');
for (let line of hostingRanges) {
  let [company, network, domain] = line.split('\t');
  console.log(company, network, domain);
}
```

## API Response Format

The API output format is explaind by walking through an example. Most of the returned information is self-explanatory.

This is how a typical API response looks like. The IP `107.174.138.172` was queried with the API call [https://api.incolumitas.com/?q=107.174.138.172](https://api.incolumitas.com/?q=107.174.138.172):

```json
{
  "ip": "107.174.138.172",
  "rir": "ARIN",
  "is_bogon": false,
  "is_datacenter": true,
  "is_tor": true,
  "is_proxy": false,
  "is_vpn": false,
  "is_abuser": true,
  "company": {
    "name": "ColoCrossing",
    "domain": "colocrossing.com",
    "network": "107.172.0.0 - 107.175.255.255",
    "whois": "https://api.incolumitas.com/?whois=107.172.0.0"
  },
  "datacenter": {
    "datacenter": "ColoCrossing",
    "domain": "www.colocrossing.com",
    "network": "107.172.0.0 - 107.175.255.255"
  },
  "asn": {
    "asn": 36352,
    "route": "107.174.138.0/24",
    "descr": "AS-COLOCROSSING, US",
    "country": "us",
    "active": true,
    "org": "ColoCrossing",
    "domain": "www.colocrossing.com",
    "abuse": "abuse@colocrossing.com",
    "type": "hosting",
    "created": "2005-12-12",
    "updated": "2013-01-08",
    "rir": "arin",
    "whois": "https://api.incolumitas.com/?whois=AS36352"
  },
  "location": {
    "country": "United States of America",
    "country_code": "us",
    "state": "New York",
    "city": "Buffalo",
    "latitude": "42.882500",
    "longitude": "-78.878800",
    "zip": "14202",
    "timezone": "-05:00",
    "local_time": "2023-02-05 12:06:33.322-0500",
    "local_time_unix": 1675598793.322
  },
  "elapsed_ms": 3.07
}
```

In the following section, the different parts of the API response are explained in-depth.

### Response Format: Top Level API Output

The top level API output looks as follows:

```json
{
  "ip": "107.174.138.172",
  "rir": "ARIN",
  "is_bogon": false,
  "is_datacenter": true,
  "is_tor": true,
  "is_proxy": false,
  "is_vpn": false,
  "is_abuser": true,
  "elapsed_ms": 2.4
}
```

The explanation for the top level API fields is as follows:

- `ip` - `string` - the IP address that was looked up, here it was `107.174.138.172`
- `rir` - `string` - to which [Regional Internet Registry](https://en.wikipedia.org/wiki/Regional_Internet_registry) the IP address belongs. Here it belongs to `ARIN`, which is the RIR responsible for North America
- `is_bogon` - `boolean` - Whether the IP address is bogon. [Bogon IP Addresses](https://en.wikipedia.org/wiki/Bogon_filtering) is the set of IP Addresses not assigned/allocated to IANA and any RIR (Regional Internet Resgistry). For example, the loopback IP `127.0.0.1` is a special/bogon IP address. The IP address `107.174.138.172` is not bogon, hence it is set to `false` here.
- `is_datacenter` - `boolean` - whether the IP address belongs to a datacenter. Here, we have the value `true`, since `107.174.138.172` belongs to the hosting provider `ColoCrossing`.
- `is_tor` - `boolean` - is true if the IP address belongs to the TOR network. This is the case here. Tor detection is accurate, so you can rely on the value of `is_tor`. The API detects most TOR exit nodes reliably.
- `is_proxy` - `boolean` - whether the IP address is a proxy. This is not the case here. In general, the flag `is_proxy` only covers a subset of all proxies in the Internet.
- `is_vpn` - `boolean` - whether the IP address is a VPN. This is not the case with the IP `107.174.138.172`. In general, the flag `is_vpn` only covers a subset of all VPN's in the Internet. It is not possible to detect all VPN exit nodes passively.
- `is_abuser` - `boolean` - is true if the IP address committed abusive actions, which was the case with `107.174.138.172`. Various IP blocklists and threat intelligence feeds are used to populate the `is_abuser` flag.
- `elapsed_ms` - `float` - how much internal processing time was spent in milliseconds (ms). This lookup only took `2.4ms`, which is quite fast.

### Response Format: The `datacenter` object

```json
"datacenter": {
  "datacenter": "ColoCrossing",
  "domain": "www.colocrossing.com",
  "network": "107.172.0.0 - 107.175.255.255"
},
```

If the IP address belongs to a datacenter/hosting provider, the API response will include a `datacenter` object with the following attributes:

- `datacenter` - `string` - to which datacenter the IP address belongs. For a full list of datacenters, check the [info endpoint](https://api.incolumitas.com/info). In this case, the datacenter's name is `ColoCrossing`.
- `domain` - `string` - The domain name of the company
- `network` - `string` - the network this IP address belongs to (In the above case: `107.172.0.0 - 107.175.255.255`)

Most IP's don't belong to a hosting provider. In those cases, the `datacenter` object will not be present in the API output.

For a couple of large cloud providers, such as Google Cloud, Amazon AWS, DigitalOcean or Microsoft Azure (and some others), the `datacenter` object is more detailed.

[Amazon AWS](https://aws.amazon.com/) example:

```json
{
  "ip": "3.5.140.2",
  "datacenter": {
    "datacenter": "Amazon AWS",
    "network": "3.5.140.0/22",
    "region": "ap-northeast-2",
    "service": "EC2",
    "network_border_group": "ap-northeast-2"
  }
}
```

[DigitalOcean](https://www.digitalocean.com/) example:

```json
{
  "ip": "167.99.241.130",
  "datacenter": {
    "datacenter": "DigitalOcean",
    "code": "60341",
    "city": "Frankfurt",
    "state": "DE-HE",
    "country": "DE",
    "network": "167.99.240.0/20"
  },
}
```

[Linode](https://www.linode.com/) example:

```json
{
  "ip": "72.14.182.54",
  "datacenter": {
    "datacenter": "Linode",
    "name": "US-TX",
    "city": "Richardson",
    "country": "US",
    "network": "72.14.182.0/24"
  },
}
```

### Response Format: The `company` object

```json
"company": {
  "name": "ColoCrossing",
  "domain": "colocrossing.com",
  "network": "107.172.0.0 - 107.175.255.255",
  "whois": "https://api.incolumitas.com/?whois=107.172.0.0"
},
```

Most IP addresses can be associated with an organization or company. The API uses whois database information to infer which organization is the owner of a certain IP address. Most API lookups will have an `company` object with the following attributes:

- `name` - `string` - The name of the company
- `domain` - `string` - The domain name of the company
- `network` - `string` - The network for which the company has ownership
- `whois` - `string` - An url to the whois information for the network of this IP address

### Response Format: The `asn` object

```json
"asn": {
  "asn": 36352,
  "route": "107.174.138.0/24",
  "descr": "AS-COLOCROSSING, US",
  "country": "us",
  "active": true,
  "org": "ColoCrossing",
  "domain": "www.colocrossing.com",
  "abuse": "abuse@colocrossing.com",
  "type": "hosting",
  "created": "2005-12-12",
  "updated": "2013-01-08",
  "rir": "arin",
  "whois": "https://api.incolumitas.com/?whois=AS36352"
},
```

Most IP addresses can be associated with an Autonomeous System (AS). The `asn` object provides the following attributes:

- `asn` - `int` - The AS number
- `route` - `string` - The IP route as CIDR in this AS
- `descr` - `string` - An informational description of the AS
- `country` - `string` - The country where the AS is situated in (administratively)
- `active` - `string` - Whether the AS is active (active = at least one route administred by the AS)
- `org` - `string` - The organization responisible for this AS
- `domain` - `string` - The domain of the organization to which this AS belongs
- `abuse` - `string` - The email address to which abuse complaints for this organization should be sent
- `type` - `string` - The type for this ASN, this is either `hosting`, `education`, `goverment`, `banking`, `business` or `isp`
- `created` - `string` - When the ASN was established
- `updated` - `string` - The last time the ASN was updated
- `rir` - `string` - To which Regional Internet Registry the ASN belongs
- `whois` - `string` - An url to the whois information for this ASN

For inactive autonomeous systems, most of the above information is not available.

### Response Format: The `location` object

```json
"location": {
  "country": "United States of America",
  "country_code": "us",
  "state": "New York",
  "city": "Buffalo",
  "latitude": "42.882500",
  "longitude": "-78.878800",
  "zip": "14202",
  "timezone": "-05:00",
  "local_time": "2023-02-05 12:06:33.322-0500",
  "local_time_unix": 1675598793.322
},
```

The API provides geolocation information for the looked up IP address. The `location` object includes the following attributes:

- `country` - `string` - The full name of the country for this IP address
- `country_code` - `string` - The ISO 3166-1 alpha-2 country code to which the IP address belongs. This is the country specific geolocation of the IP address.
- `state` - `string` - The state / administrative area for the IP address
- `city` - `string` - The city to which the IP address belongs
- `latitude` - `string` - The latitude for the IP address
- `longitude` - `string` - The longitude for the IP address
- `zip` - `string` - The zip code for this IP
- `timezone` - `string` - The timezone for this IP
- `local_time` - `string` - The local time for this IP in human readable format
- `local_time_unix` - `string` - The local time for this IP as unix timestamp
- `possible_other_location` - `array` - (Optional) -  If there are multiple possible geographical locations, the attribute `possible_other_location` is included in the API response. It contains an array of ISO 3166-1 alpha-2 country codes which represent the possible other geolocation countries.

Country level geolocation accuracy is quite good, since the API provides information from several different geolocation service providers.

## API Endpoints

The IP API currently has two endpoints.

### GET Endpoint - Lookup a single IP Address or ASN

This GET endpoint allows to lookup a single IPv4 or IPv6 IP address by specifying the query parameter `q`. Example: `q=142.250.186.110`. You can also lookup **ASN** numbers by specifying the query `q=AS209103`

- **Endpoint** - [https://api.incolumitas.com/](https://api.incolumitas.com/)
- **Method** - `GET`
- **Parameter** - `q` - The IP address or ASN to lookup
- **Example** - [https://api.incolumitas.com/?q=3.5.140.2](https://api.incolumitas.com/?q=3.5.140.2)
- **ASN Example** - [https://api.incolumitas.com/?q=AS42831](https://api.incolumitas.com/?q=AS42831)

### POST Endpoint - Query up to 100 IP Addresses in one API call

You can also make a bulk API lookup with up to 100 IP addresses (Either IPv4 or IPv6) in one single request.

- **Endpoint** - [https://api.incolumitas.com/](https://api.incolumitas.com/)
- **Method** - `POST`
- **Content-Type** - `Content-Type: application/json`
- **Parameter** - `ips` - An array of IPv4 and IPv6 addresses to lookup

For example, in order to lookup the IP addresses

- `162.158.0.0`
- `2406:dafe:e0ff:ffff:ffff:ffff:dead:beef`
- `162.88.0.0`
- `20.41.193.225`

you can use the following POST API request with `curl`:

```bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"ips": ["162.158.0.0", "2406:dafe:e0ff:ffff:ffff:ffff:dead:beef", "162.88.0.0", "20.41.193.225"]}' \
  https://api.incolumitas.com/
```


## Change Log

#### 11th December 2022

+ Now serving daily 1M requests
+ Introduced the `is_vpn` flag (Mostly using [github.com/X4BNet/lists_vpn](https://github.com/X4BNet/lists_vpn) as data source)
+ Added self published cloud IP ranges from `Alibaba Cloud`, `SAP Cloud`, `Servicenow Cloud`
+ Upgraded to more powerful server (16GB RAM, 4vCPU)
+ **TODO:** Run Node.js HTTP Express.js Server on Multiple CPU Cores in order to deal with high load

#### 2nd December 2022

+ Many thousands of new cloud/hosting providers being tracked
+ Added [iCloud Private Relay IP ranges](https://mask-api.icloud.com/egress-ip-ranges.csv)
+ Geolocation time's was wrong because of DST change in North America
+ Updated whole database

#### 30th October 2022

+ Better geolocation information
+ Updated whole database
+ Updated this API documentation page

#### 30th September 2022

+ Moved the API to a dedicated server. There will be much fewer service disruptions from now on
+ Added more detailed geolocation information
+ Updated whole database
+ Added LACNIC organization information
+ Added field `type` to `asn` objects. Possible `asn` `type` values: `hosting`, `education`, `goverment`, `banking`, `business`, `isp`
+ Updated this API documentation page
+ Info: The API has passed 10 Million requests

#### 11th September 2022

+ Updated this API documentation page to reflect that the API is no longer only a datacenter IP address API, but a more generic and powerful IP API

#### 21th August 2022

+ Added country specific geolocation information
+ Updated datacenter ranges and added new datacenters
+ Now providing company information for almost all active networks in the Internet
+ Providing organisation and abuse meta information for each of the 79247 active ASN's

#### 30th July 2022

+ Added hundreds of new datacenters (Now 496 datacenters in the database)
+ Added basic country geolocation for each IP (In the attribute `location`)
+ Server is now faster and has more RAM (no more downtime)
+ Updated this documentation page

#### 26th July 2022

+ Updated this documentation page
+ The API provides now AS (Autonomous System) information for each looked up IP address (in the attribute `asn`)
+ The API provides information about the Regional Internet Registrity to which the looked up IP belongs (in the attribute `rir`)
+ Added a huge amount of new hosting providers / datacenters to the API

#### 5th June 2022

+ Added [APNIC whois data](https://www.apnic.net/) to database
+ Updated database in general
+ added API endpoint [/info](https://api.incolumitas.com/info)

#### 20th March 2022

+ Improved API
+ Remove the `service` attribute in API output. Only attribute that identifies the cloud provider is now `datacenter`
+ Add bulk IP lookup mode. Allow up to 100 ips in bulk lookup mode. Only return datacenter IP addresses. Uses POST method. Ignore Invalid IPs

#### 14th March 2022 and 15th March 2022

+ Added **39,246** IPv4 and **360,372** IPv6 CIDR ranges ranges to the database from AFRINIC, RIPE-NCC, APNIC, ARIN and LACNIC whois databases.
+ Some Examples: [Lookup of Cloudflare IP](https://api.incolumitas.com/datacenter?ip=104.28.48.132), [Lookup of M247 Ltd IP](https://api.incolumitas.com/datacenter?ip=193.27.14.71)
, [Lookup of Packethub S.A. IP](https://api.incolumitas.com/datacenter?ip=185.153.176.242),  [Lookup of Leaseweb IP](https://api.incolumitas.com/datacenter?ip=178.162.192.22)
+ Added the following datacenters to the API: `XT Global Networks LTD`, `OVH`, `myLoc`,
`ServiHosting Networks S.L.`, `Clouvider Limited`,
`Hetzner Online`, `GoDaddy Operating Company, LLC.`,
`Claranet limited`, `Selectel Ltd.`, `M247 Ltd`,
`Imperva, Inc.`, `Beget`, `trueserver.nl`, `1&1 Internet`,
`DediPath`, `iomart Hosting Ltd`,
`Aruba S.p.a`, `Strato AG`, `DataCamp Limited`,
`Rackspace, Inc.`, `Reg.Ru Hosting`, `Heficed`, `LeaseWeb`,
`Mittwald`, `The Constant Company, LLC`,
`American Internet Services`, `Hostinger`,
`PlusServer GmbH`, `Equinix, Inc.`, `GHOSTnet GmbH`,
`It7 Networks Inc`,
`xservers.ro`, `Cloudflare`, `IBM Cloud`,
`iWeb Technologies Inc.`,
`SysEleven SysEleven GmbH`, `G-Core Labs S.A.`,
`Tencent Cloud`, `Choopa, LLC.`, `DigitalOcean`,
`Webair Internet Development Inc`, `Hostway`,
`Phoenix NAP, LLC`, `Contabo GmbH`, `A2 Hosting`,
`Zenlayer`, `Optimate Server`, `LogicWeb Inc.`,
`Packethub S.A.`, `MULTACOM Inc.`, `veesp.com vps clients`,
`Sakura Internet Inc.`, `Zscaler, Inc.`,
`Vultr Holdings LLC`, `Enzu Inc.`, `24Shells Inc`,
`GZ Systems (PureVPN)`, `HIVELOCITY, Inc.`, `Transip Bv.`,
`Host Europe`, `Internap Corporation`, `IP Exchange GmbH`,
`Datapipe`, `Savvis`,
`home.pl S.A.`, `Redstation Limited`, `hosting.ua`,
`Daou Technology`, `Linode`, `Amazon AWS`,
`kinx.net`, `Dreamscape`, `Xneelo (Pty) Ltd`,
`Fiber Grid Inc`, `Performive LLC`, `Microsoft Azure`,
`UCloud`, `Hostgator`, `Hostwinds.com`, `Namecheap`,
`Stackpath, LLC`, `ALL INKL`,
`Online SAS (Scaleway)`, `ServerCentral`,
`Quadranet, Inc`, `FDC Servers`,
`ColoCrossing`, `Aptum Technologies`, `Sharktech Inc.`,
`Wholesale Internet, Inc`, `Dreamhost`,
`Pair Networks`, `ServerHub`, `Psychz Networks`,
`CoreSpace,Inc.`, `Cologix, Inc.`,
`Colocation America Inc`, `ServerMania Inc.`, `Peak10`,
`Google Cloud`, `Fasthosts Internet Ltd`,
`latisys`, `Mullvad VPN`, `InMotion`, `Unified Layer`,
`Fastly, Inc.`, `Ubiquity Hosting`.

#### 11th March 2022

+ Added bulk IP lookup mode, up to 100 IP addresses can be queried with one API request
+ Added fast IPv6 lookup support (Speedup of factor `883x`, average lookup time now  `0.056ms` instead of `49.99ms`)

#### 9th March 2022

+ Added `cidr` attribute to the API output
+ Improved API performance for IPv4 (IPv6 still pending), the performance is now 1500x times faster on average (Average lookup time before: `100.37ms`, average lookup time now `0.068ms`)

#### 8th March 2022

+ Added cloud service providers / hosting providers / VPN service providers: `Linode`, `Mullvad VPN`, `B2 Net Solutions Inc.`, `scaleway.com`, `Vultr Holdings, LLC`, `The Constant Company, LLC`, `QuadraNet Enterprises LLC`, `Zscaler, Inc.`, `CloudCone, LLC`, `Psychz Networks`,  `BuyVM Services (buyvm.net)`,  `DataCamp Limited`,  `ColoCrossing`,  `IT7 Networks Inc.`,  `G-Core Labs S.A.`,  `AlmaHost Ltd`,  `Reg.Ru Hosting`,  `Packethub S.A.`,  `Clouvider Limited`,  `24Shells Inc`,  `Performive LLC`,  `Packet Host, Inc.`,  `veesp.com vps clients`,  `tzulo, inc.`,  `Cluster Logic Inc`,  `Owl Limited`,  `HIVELOCITY, Inc.`, `SysEleven SysEleven GmbH`
+ Added lookup time in `ms` to the API output as attribute `elapsed_ms`
+ Updated this API page
+ Updated all IP address ranges

#### 6th November 2021

+ Updated all IP address ranges
+ Add cloud provider `m247 Ltd`, `servers.com Inc.`, `Leaseweb Usa Inc.`, often used for proxies/fraud
+ Checking for common datacenter in `whois` lookup

#### 29th September 2021

+ Updated all IP address ranges
+ Added dedicated API endpoint: <https://api.incolumitas.com/datacenter?ip=3.5.140.2>
+ Old API Endpoint: <https://abs.incolumitas.com/datacenter?ip=1.2.3.4>
