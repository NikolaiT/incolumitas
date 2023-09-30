Title: IP Address API
Date: 2022-09-11 22:00
Modified: 2023-09-25 22:00
Author: Nikolai Tschacher
Slug: IP-API
Status: published
Sortorder: 5

| <!-- -->    | <!-- -->    |
|-------------|-------------|
| **Author**         | Nikolai Tschacher ([incolumitas.com](https://incolumitas.com/))     |
| **Pro Version**         | [ipapi.is](https://ipapi.is/)          |
| **GitHub**         | [IP API GitHub Page](https://github.com/NikolaiT/IP-Address-API)          |
| **API Version**         | **v0.12.1 (25th September 2023)**         |
| **API Endpoint**         | [https://api.incolumitas.com/?q=3.5.140.2](https://api.incolumitas.com/?q=3.5.140.2)         |
| **Total Tracked Hosting Providers**         |    **[52951 hosting providers]({filename}/pages/datacenters.md)**      |
| **Number of Ipv4 Addresses**         |    **378,753** IPv4 CIDR ranges (836,818,346 Addresses in total)      |
| **Number of Ipv6 Addresses**         |    **307,202** IPv6 CIDR ranges (4.4379867697277937e+33 Addresses in total)      |

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
      <a class="api-example" data-query="107.152.214.169" href="#">107.152.214.169</a> —
      <a class="api-example" data-query="2a02:0f58:0004:0300:0216:3eff:fec2:a1f" href="#">2a02:0f58:0004:0300:0216:3eff:fec2:a1f</a>
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

## Change Log

### 3th August 2023

+ The self-made geolocation database is available for download on the [GitHub Repository](https://github.com/NikolaiT/IP-Address-API)
+ Several data points were added to API:
  + `is_mobile` flag that determines if the IP address belongs to a mobile provider
  + `continent` in the `location` object that specifies the continent as 2 letter code
  + added `type` to the `company` object
+ I added a lot of hosting IP ranges to the API
+ The `asn` and `company` type field (`type`) is much more accurate in the most recent version
+ You can now use the IP API in your professional projects: [ipapi.is](https://ipapi.is/)

### 2nd April 2023

+ API is now running on 3 parallel clusters and can serve roughly 30 million request per day.
+ For March 2023, the time was wrong for the fields `local_time` and `local_time_unix` (Mostly because of DST). This was fixed for good now.
+ Added `is_dst` field to `geolocation` object. It is true if DST is active in the IP address timezone.
+ Added `timezone` field to the `geolocation` object. It represents the timezone of the IP address time. Example: `Europe/Berlin`
+ Fixed erroneous output in `geolocation` object for IPv6
+ Renamed field `possible_other_location` to `other` in the `geolocation` object. This was done in order to save space.
+ Added proprietary list mostly for `is_datacenter` and `is_abuser`

### 11th December 2022

+ Now serving daily 1M requests
+ Introduced the `is_vpn` flag (Mostly using [github.com/X4BNet/lists_vpn](https://github.com/X4BNet/lists_vpn) as data source)
+ Added self published cloud IP ranges from `Alibaba Cloud`, `SAP Cloud`, `Servicenow Cloud`
+ Upgraded to more powerful server (16GB RAM, 4vCPU)
+ **TODO:** Run Node.js HTTP Express.js Server on Multiple CPU Cores in order to deal with high load

### 2nd December 2022

+ Many thousands of new cloud/hosting providers being tracked
+ Added [iCloud Private Relay IP ranges](https://mask-api.icloud.com/egress-ip-ranges.csv)
+ Geolocation time's was wrong because of DST change in North America
+ Updated whole database

### 30th October 2022

+ Better geolocation information
+ Updated whole database
+ Updated this API documentation page

### 30th September 2022

+ Moved the API to a dedicated server. There will be much fewer service disruptions from now on
+ Added more detailed geolocation information
+ Updated whole database
+ Added LACNIC organization information
+ Added field `type` to `asn` objects. Possible `asn` `type` values: `hosting`, `education`, `goverment`, `banking`, `business`, `isp`
+ Updated this API documentation page
+ Info: The API has passed 10 Million requests

### 11th September 2022

+ Updated this API documentation page to reflect that the API is no longer only a datacenter IP address API, but a more generic and powerful IP API

### 21th August 2022

+ Added country specific geolocation information
+ Updated datacenter ranges and added new datacenters
+ Now providing company information for almost all active networks in the Internet
+ Providing organization and abuse meta information for each of the 79247 active ASN's

### 30th July 2022

+ Added hundreds of new datacenters (Now 496 datacenters in the database)
+ Added basic country geolocation for each IP (In the attribute `location`)
+ Server is now faster and has more RAM (no more downtime)
+ Updated this documentation page

### 26th July 2022

+ Updated this documentation page
+ The API provides now AS (Autonomous System) information for each looked up IP address (in the attribute `asn`)
+ The API provides information about the Regional Internet Registry to which the looked up IP belongs (in the attribute `rir`)
+ Added a huge amount of new hosting providers / datacenters to the API

### 5th June 2022

+ Added [APNIC whois data](https://www.apnic.net/) to database
+ Updated database in general
+ added API endpoint [/info](https://api.incolumitas.com/info)

### 20th March 2022

+ Improved API
+ Remove the `service` attribute in API output. Only attribute that identifies the cloud provider is now `datacenter`
+ Add bulk IP lookup mode. Allow up to 100 ips in bulk lookup mode. Only return datacenter IP addresses. Uses POST method. Ignore Invalid IPs

### 14th March 2022 and 15th March 2022

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

### 11th March 2022

+ Added bulk IP lookup mode, up to 100 IP addresses can be queried with one API request
+ Added fast IPv6 lookup support (Speedup of factor `883x`, average lookup time now  `0.056ms` instead of `49.99ms`)

### 9th March 2022

+ Added `cidr` attribute to the API output
+ Improved API performance for IPv4 (IPv6 still pending), the performance is now 1500x times faster on average (Average lookup time before: `100.37ms`, average lookup time now `0.068ms`)

### 8th March 2022

+ Added cloud service providers / hosting providers / VPN service providers: `Linode`, `Mullvad VPN`, `B2 Net Solutions Inc.`, `scaleway.com`, `Vultr Holdings, LLC`, `The Constant Company, LLC`, `QuadraNet Enterprises LLC`, `Zscaler, Inc.`, `CloudCone, LLC`, `Psychz Networks`,  `BuyVM Services (buyvm.net)`,  `DataCamp Limited`,  `ColoCrossing`,  `IT7 Networks Inc.`,  `G-Core Labs S.A.`,  `AlmaHost Ltd`,  `Reg.Ru Hosting`,  `Packethub S.A.`,  `Clouvider Limited`,  `24Shells Inc`,  `Performive LLC`,  `Packet Host, Inc.`,  `veesp.com vps clients`,  `tzulo, inc.`,  `Cluster Logic Inc`,  `Owl Limited`,  `HIVELOCITY, Inc.`, `SysEleven SysEleven GmbH`
+ Added lookup time in `ms` to the API output as attribute `elapsed_ms`
+ Updated this API page
+ Updated all IP address ranges

### 6th November 2021

+ Updated all IP address ranges
+ Add cloud provider `m247 Ltd`, `servers.com Inc.`, `Leaseweb Usa Inc.`, often used for proxies/fraud
+ Checking for common datacenter in `whois` lookup

### 29th September 2021

+ Updated all IP address ranges
+ Added dedicated API endpoint: <https://api.incolumitas.com/datacenter?ip=3.5.140.2>
+ Old API Endpoint: <https://abs.incolumitas.com/datacenter?ip=1.2.3.4>

## IP Address API

This IP address API returns useful meta-information for IP addresses. For example, the API response includes the organization of the IP address, ASN information and geolocation intelligence and WHOIS data.

Furthermore, the API response allows to derive **security information** for each IP address, for example whether an IP address belongs to a hosting provider (`is_datacenter`), is a TOR exit node (`is_tor`), if an IP address is a proxy (`is_proxy`) or VPN (`is_vpn`) or belongs to an abuser (`is_abuser`).

This API strongly emphasizes **hosting detection**. A complicated hosting detection algorithm was developed to achieve a high detection rate. [Thousands of different hosting providers](https://ipapi.is/hosting-detection.html) are tracked. Whois records, public hosting IP ranges from hosting providers and a proprietary hosting discovery algorithm are used to decide whether an IP address belongs to a hosting provider or not.

## Quickstart

Lookup any IP address: [https://api.ipapi.is/?q=3.5.140.2](https://api.ipapi.is/?q=3.5.140.2)

Lookup your own IP address: [https://api.ipapi.is/](https://api.ipapi.is/)

Usage with JavaScript:

```JavaScript
fetch('https://api.ipapi.is/?q=23.236.48.55')
  .then(res => res.json())
  .then(res => console.log(res));
```

Usage with `curl`:

```bash
curl 'https://api.ipapi.is/?q=32.5.140.2'
```

For a full documentation, please visit the [documentation page](https://ipapi.is/developers.html).

In order to download the databases, please visit the [GitHub repository](https://github.com/NikolaiT/IP-Address-API).
