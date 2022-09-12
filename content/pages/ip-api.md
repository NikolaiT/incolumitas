Title: IP Address API
Date: 2022-09-11 22:00
Author: Nikolai Tschacher
Slug: IP-API
Status: published
Sortorder: 5

The IP Address API returns useful information for each submitted IP address such as which company/organization has ownership of the IP address, to which ASN the IP address belongs to and the geographic location (geolocation) of IP addresses. Furthermore, it allows you to derive security information for each IP address, for example whether an IP address belongs to a hosting provider (`is_datacenter`), is a TOR exit node (`is_tor`), if a IP address is a proxy (`is_proxy`) or belongs to an abuser (`is_abuser`).

This API uses the following sources:

1. Public whois records from regional Internet address registries such as RIPE NCC, APNIC, ARIN and so on
2. Public BGP information (to find ASN information and their associated routes/prefixes)
3. Public blocklists such as [firehol/blocklist-ipset](https://github.com/firehol/blocklist-ipsets)
4. The API uses several proprietary datacenter/hosting detection algorithms
5. The API uses IP threat data from public honeypots
6. IP geolocation information (Geolocation is accurate to the country level)

| <!-- -->    | <!-- -->    |
|-------------|-------------|
| **Author**         | Nikolai Tschacher ([incolumitas.com](https://incolumitas.com/))     |
| **API Access**         | Free & unlimited (fair use)         |
| **API Version**         | **v0.9.4 (11th September 2022)**         |
| **API Endpoint**         | [**https://api.incolumitas.com/?ip=3.5.140.2**](https://api.incolumitas.com/?ip=3.5.140.2)         |
| **Total Tracked Hosting Providers**         |    **[1566 hosting providers]({filename}/pages/datacenters.md)**      |
| **Number of Ipv4 Addresses**         |    **578,607** IPv4 CIDR ranges (1,124,037,736 Addresses in total)      |
| **Number of Ipv6 Addresses**         |    **491,415** IPv6 CIDR ranges (1.3398119786246428e+33 Addresses in total)      |

## Live API

<div class="ipAPIDemo">
  <label style="font-weight: 600; font-size: 16px" for="ip">IP Address / ASN:</label>
  <input style="padding: 8px; margin-left: 4px; margin-right: 4px" type="text" id="ip" name="ip" value="13.34.52.117">
  <input class="orange_button" style="" type="submit" value="Make API Request" placeholder="IP Address or ASN">

  <div>
    <p><strong>Examples:</strong>
      <a class="api-example" data-query="165.227.176.0" href="#">165.227.176.0</a> —
      <a class="api-example" data-query="43.181.128.0" href="#">43.181.128.0</a> —
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
  let url = query ? 'https://api.incolumitas.com/datacenter?ip=' + query : 'https://api.incolumitas.com/datacenter';

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

## API Features

+ **Ready for Production**: This API can be used in production and is stable
+ **Many datacenters supported:** [Thousands of different hosting providers and counting]({filename}/pages/datacenters.md) - From Huawei Cloud Service to ServerMania Inc. Find out whether the IP address is hosted by looking at the `is_datacenter` property!
+ **Always updated**: The API database is automatically several times per week. IP data is gathered from many sources:
    + Self published IP ranges from large cloud providers
    + Public whois data from regional internet registries (RIR's) such as RIPE NCC or APNIC
    + Many other data sources such as public [BGP data](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
    + Open Source IP blocklists
+ **AS (Autonomous System) support**: The API provides autonomous system information for each looked-up IP address
+ **Company Support**: The API provides organisational information for each network of each looked up IP address
+ **Bulk IP Lookups**: You can lookup up to 100 IP addresses per API call

## API Response Format

The JSON API response **will always include the following information**

+ `ip` - `string` - the IP address that was looked up
+ `rir` - `string` - to which [Regional Internet Registry](https://en.wikipedia.org/wiki/Regional_Internet_registry) the looked up IP address belongs
+ `is_bogon` - `boolean` - Whether the IP address is bogon. For example, the loopback IP `127.0.0.1` is a special/bogon IP address
+ `is_datacenter` - `boolean` - whether the IP address belongs to a datacenter
+ `is_tor` - `boolean` - is true if the IP address belongs to the TOR network
+ `is_proxy` - `boolean` - whether the IP address is a proxy
+ `is_abuser` - `boolean` - is true if the IP address committed abusive actions
+ `company` - `object` - Company information for the looked up IP address. The `company` object includes the following attributes:
    + `name` - `string` - The name of the company
    + `domain` - `string` - The domain name of the company
    + `network` - `string` - The network for which the company has ownership
+ `asn` - `object` - ASN information for the looked up IP address. The `asn` object includes the following information:
    + `asn` - `int` - The AS number
    + `route` - `string` - The IP route as CIDR in this AS
    + `descr` - `string` - An informational description of the AS
    + `country` - `string` - The country where the AS is situated in
    + `active` - `string` - Whether the AS is active (active = at least one route administred by the AS)
    + `website` - `string` - The website of the organization to which this AS belongs
    + `org` - `string` - The organization responisible for this AS
    + `type` - `string` - The type for this ASN, this is either `hosting`, `education`, `government`, `banking` or `business`
+ `location` - `object` - Geolocation information for the looked up IP address. The `location` object includes the following attributes:
    + `country` - `string` - The ISO 3166-1 alpha-2 country code to which the IP address belongs. This is the country specific geolocation of the IP address.
+ `elapsed_ms` - `float` - how much internal processing time was spent in ms (Example: `1.71`)

If the IP address belongs to a datacenter/hosting provider, the API response will also include the following keys:

+ `datacenter` - `object` - Datacenter/hosting information for the looked up IP address. The `datacenter` object includes the following attributes:
    + `datacenter` - `string` - to which datacenter the IP address belongs. For a full list of datacenters, check the [api.incolumitas.com/info endpoint](https://api.incolumitas.com/info) (Example: `"Amazon AWS"`)
    + `cidr` - `string` - to which datacenter network the IP address belongs (Example: `"13.34.52.96/27"`)

### GET - `/` - Lookup a single IP address or ASN

This GET endpoint allows to lookup a single IPv4 or IPv6 IP address by specifying the query parameter `ip`. Example: `ip=142.250.186.110`. You can also lookup **ASN** numbers by specifying the query `ip=AS209103`.

| <!-- -->         | <!-- -->                                           |
|------------------|----------------------------------------------------|
| **Endpoint**       | /                                  |
| **Method**       | `GET`                                  |
| **Parameter**       | `ip` - The IP address or ASN to lookup                                 |
| **Example** | [https://api.incolumitas.com/?ip=3.5.140.2](https://api.incolumitas.com/?ip=3.5.140.2)
| **ASN Example** | [https://api.incolumitas.com/?ip=AS42831](https://api.incolumitas.com/?ip=AS42831)

### POST - `/` - Lookup up to 100 IP addresses in one API call

You can also make a bulk API lookup with up to 100 IP addresses (Either IPv4 or IPv6) in one single request.

| <!-- -->         | <!-- -->                                           |
|------------------|----------------------------------------------------|
| **Endpoint**       | /                                  |
| **Method**       | `POST`                                  |
| **Content-Type**       | `Content-Type: application/json`                                  |
| **Parameter**       | `ips` - An array of IPv4 and IPv6 addresses to lookup                                 |

For example, in order to lookup the IP addresses

+ `162.158.0.0`
+ `2406:dafe:e0ff:ffff:ffff:ffff:dead:beef`
+ `162.88.0.0`
+ `20.41.193.225`

you can use the following POST API request with curl:

```bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"ips": ["162.158.0.0", "2406:dafe:e0ff:ffff:ffff:ffff:dead:beef", "162.88.0.0", "20.41.193.225"]}' \
  https://api.incolumitas.com/
```

## Sources for IP Address Ranges

Where do I get the [CIDR](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) address ranges for the datacenters?

Most datacenters publish their own IP ranges, such as AWS or Google Cloud. But often, those IP address ranges are not complete. For that reason, other means of lookup have to be used, such as [consulting whois data from Regional Internet Registries](https://en.wikipedia.org/wiki/WHOIS) or searching through [ASN databases](https://en.wikipedia.org/wiki/Autonomous_system_(Internet)).

The API provides a proprietary datacenter/hosting discovery algorithm that makes use of:

1. Self reported IP ranges from cloud providers
2. Publicly accessible whois data from regional internet registries such as ARIN or APNIC
3. Daily published AS information from backbone Internet routers

## Change Log

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
