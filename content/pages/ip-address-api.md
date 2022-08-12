Title: Datacenter IP Address API
Date: 2021-09-29 00:13
Modified: 2022-08-13 20:00
Author: Nikolai Tschacher
Slug: Datacenter-IP-API
Status: published
Sortorder: 5

The Datacenter IP Address API can be used to check whether an IP address belongs to a datacenter/hosting IP address range such as Azure, AWS, Digitalocean, Google Cloud Platform and many other cloud providers. Please read the [full blog article]({filename}/Security/datacenter-ip-api.md) for a thorough introduction. And please consider reading another blog article:  ["How to find out if an IP address belongs to a Hosting / Cloud Provider?"]({filename}/Security/datacenter-ip-api-second.md)

It is not trivial to determine if an IPv4 or IPv6 address belongs to a hosting provider. Therefore, this API will not be free from false positives. However, by using an intelligent datacenter detection algorithm (which uses public whois data and BGP/ASN data from Regional Internet Registries), most (somehwat prominent) hosting provideres can be found.

What is a datacenter / hosting provider?

> It is an organisation that allows third party users to control server capacities with (usually) publicly accessable IP address ranges.


| <!-- -->    | <!-- -->    |
|-------------|-------------|
| **Author**         | Nikolai Tschacher (incolumitas.com)     |
| **API Access**         | Free & unlimited (fair use)         |
| **API Version**         | **v0.9.2 (13th August 2022)**         |
| **API Endpoint**         | [**https://api.incolumitas.com/datacenter?ip=3.5.140.2**](https://api.incolumitas.com/datacenter?ip=3.5.140.2)         |
| **Supported Datacenters**         | Amazon AWS, Microsoft Azure, Google Cloud, IBM Cloud, OVH, Digital Ocean, Hetzner Online, CloudFlare, Oracle Cloud, Tor Network [and many other hosting providers](https://api.incolumitas.com/info)         |
| **Total Tracked Hosting Providers**         |    **[1358 hosting providers]({filename}/pages/datacenters.md)**      |
| **Number of Ipv4 Addresses**         |    **197,932** IPv4 CIDR ranges (514,549,716 Addresses in total)      |
| **Number of Ipv6 Addresses**         |    **391,206** IPv6 CIDR ranges (1.182433118801632e+33 Addresses in total)      |


## Live API

<div class="ipAPIDemo">
  <label style="font-weight: 600; font-size: 15px" for="ip">IP Address or ASN:</label>
  <input style="padding: 6px;" type="text" id="ip" name="ip" value="13.34.52.117"><br><br>
  <input class="orange_button" type="submit" value="Make API Request">

  <div>
    <p><strong>Examples:</strong>
      <a class="api-example" data-query="43.181.128.0" href="#">43.181.128.0</a> —
      <a class="api-example" data-query="194.126.177.0" href="#">194.126.177.0</a> —
      <a class="api-example" data-query="AS209103" href="#">AS209103</a> —
      <a class="api-example" data-query="23.236.48.55" href="#">23.236.48.55</a> —
      <a class="api-example" data-query="2600:1F18:7FFF:F800:0000:ffff:0000:0000" href="#">2600:1F18:7FFF:F800:0000:ffff:0000:0000</a>
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

## Key API Features

+ **Ready for Production**: This API can be used in production and is stable
+ **Many datacenters supported:** [Thousands of different hosting providers and counting]({filename}/pages/datacenters.md) - From Huawei Cloud Service to ServerMania Inc.
+ **Always updated**: The API database is automatically updated every week. IP data is gathered from many sources:
    + Self published IP ranges from large cloud providers
    + Public whois data from regional internet registries (RIR's) such as RIPE NCC or APNIC
    + Many other data sources such as public [BGP data](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
+ **AS (Autonomous System) support**: The API provides Autonomous System information for every IP address looked up
+ **Pretty fast**: The API is very performant. On average, an IP lookup takes `0.042ms` (server side time consumed)
+ **Bulk IP Lookups**: You can lookup up to 100 IP addresses per API call


## API Endpoints

The API has exactly **three endpoints**:

1. `/datacenter` - **GET** - Used to lookup a **single IP address** by specifying the parameter `ip`. You can also lookup **ASN** numbers by looking up a ASN (Example: `ip=AS209103`).
2. `/datacenter` - **POST** - Used to lookup **up to 100 different IP addresses** by specifying the POST parameter `ips`.
3. `/info` - **GET** - This API endpoint returns statistical information about all datacenters in the API.

The `/datacenter` endpoints (both GET and POST) return information about the IP addresses specified in the `ip` (GET) or `ips` (POST) parameters.

The JSON API response **will always include the keys** (Even if the looked up IP address was not a match):

+ `ip` - `string` - the IP address that was looked up
+ `is_datacenter` - `boolean` - whether the IP address belongs to a datacenter
+ `asn` - `object` - ASN information for the looked up IP address. The `asn` object includes the following information:
    + `asn` - `int` - The AS number 
    + `cidr` - `string` - The IP range as CIDR within the AS
    + `descr` - `string` - An informational description of the AS
    + `country` - `string` - The country where the AS is situated in
+ `rir` - `string` - to which [Regional Internet Registry](https://en.wikipedia.org/wiki/Regional_Internet_registry) the looked up IP address belongs
+ `elapsed_ms` - `float` - how much internal processing time was spent in ms (Example: `1.71`)

If there is a datacenter match, the API response will always include the following keys:

+ `src` - `string` - the data source that claims that this IP belongs to a datacenter (Example: `whois`)
+ `datacenter` - `string` - to which datacenter the IP address belongs. For a full list of datacenters, check the [api.incolumitas.com/info endpoint](https://api.incolumitas.com/info) (Example: `"Amazon AWS"`)
+ `cidr` - `string` - the CIDR range that this IP address belongs to (Example: `"13.34.52.96/27"`)

### GET - `/datacenter` - Lookup a single IP address or ASN

This GET endpoint allows to lookup a single IPv4 or IPv6 IP address by specifying the query parameter `ip`. Example: `ip=142.250.186.110`. You can also lookup **ASN** numbers by specifying the query `ip=AS209103`.

| <!-- -->         | <!-- -->                                           |   
|------------------|----------------------------------------------------|
| **Endpoint**       | /datacenter                                  |
| **Method**       | `GET`                                  |
| **Parameter**       | `ip` - The IP address or ASN to lookup                                 |
| **Description**  | If the provided IP address belongs to a datacenter, the API will return all meta data for the datacenter. The attribute `is_datacenter` will be set to `true`.   |
| **Example** | [https://api.incolumitas.com/datacenter?ip=3.5.140.2](https://api.incolumitas.com/datacenter?ip=3.5.140.2)
| **ASN Example** | [https://api.incolumitas.com/datacenter?ip=AS42831](https://api.incolumitas.com/datacenter?ip=AS42831)

### POST - `/datacenter` - Lookup up to 100 IP addresses in one API call

You can also make a bulk API lookup with up to 100 IP addresses (Either IPv4 or IPv6) in one single request. 

**Please note:** The API will return only matches for those IP addresses that belong to a datacenter. This approach saves networking bandwith.

| <!-- -->         | <!-- -->                                           |   
|------------------|----------------------------------------------------|
| **Endpoint**       | /datacenter                                  |
| **Method**       | `POST`                                  |
| **Content-Type**       | `Content-Type: application/json`                                  |
| **Parameter**       | `ips` - An array of IPv4 and IPv6 addresses to lookup                                 |
| **Description**  | The API will return datacenter lookups for each of the IP addresses provided. Only IP addresses that have a datacenter match will be returned in the API response.  |

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
  https://api.incolumitas.com/datacenter
```

### GET - `/info` - Obtain statistical information about all datacenters present in the API

In order to get statistical information about all datacenters / hosting providers currently present in the API database, you can query the `/info` GET endpoint.

| <!-- -->         | <!-- -->                                           |   
|------------------|----------------------------------------------------|
| **Endpoint**       | /info                                  |
| **Method**       | `GET`                                  |
| **Description**  | Returns all datacenters that are currently present in the API. The number of IPv4 (`total_ipv4`) and IPv6 (`total_ipv6`) addresses for each datacenter will also be provided.   |
| **Example** | [https://api.incolumitas.com/info](https://api.incolumitas.com/info)    


## API Usage Documentation

You can reach the API endpoint with this URL: **https://api.incolumitas.com/datacenter?ip=**

If you pass the IP address `3.5.140.2` to the API by calling [https://api.incolumitas.com/datacenter?ip=3.5.140.2](https://api.incolumitas.com/datacenter?ip=3.5.140.2), you'll obtain the result:

```json
{
  "ip": "3.5.140.2",
  "is_datacenter": true,
  "src": "selfPublished",
  "cidr": "3.5.140.0/22",
  "region": "ap-northeast-2",
  "datacenter": "Amazon AWS",
  "service": "AMAZON",
  "network_border_group": "ap-northeast-2",
  "rir": "arin",
  "asn": {
    "asn": 16509,
    "cidr": "3.5.140.0/22",
    "descr": "AMAZON-02, US",
    "country": "us"
  },
  "location": {
    "country": "us"
  },
  "elapsed_ms": 0.16
}
```

Alternatively, you can also lookup IPv6 addresses. Try the url [https://api.incolumitas.com/datacenter?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef](https://api.incolumitas.com/datacenter?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef), which yields:

```json
{
  "ip": "2406:dafe:e0ff:ffff:ffff:ffff:dead:beef",
  "is_datacenter": true,
  "src": "selfPublished",
  "cidr": "2406:dafe:e000::/40",
  "region": "ap-east-1",
  "datacenter": "Amazon AWS",
  "service": "AMAZON",
  "network_border_group": "ap-east-1",
  "rir": "APNIC",
  "asn": null,
  "location": {
    "country": "not found"
  },
  "elapsed_ms": 0.69
}
```

If you don't specify any IP address with the `ip=` query parameter and you invoke [https://api.incolumitas.com/datacenter](https://api.incolumitas.com/datacenter) directly, the client's own IP address will be used for lookup. In my case, I get the following output (censored):

```json
{
  "ip": "86.56.xx.xx",
  "is_datacenter": false,
  "rir": "ripe ncc",
  "asn": {
    "asn": 20880,
    "cidr": "86.56.xx.xx/17",
    "descr": "xxx",
    "country": "de"
  },
  "location": {
    "country": "de"
  },
  "elapsed_ms": 7.79
}
```

because my private ISP IP address obviously doesn't belong to any datacenter.

Usage with JavaScript:

```JavaScript
fetch('https://api.incolumitas.com/datacenter') 
  .then(response => response.json())
  .then(function(data) {
    console.log(data)
  })
```

The IP address ranges for the cloud providers are kept up to date and the IP ranges are pulled from the upstream sources every 4 hours.

### Bulk IP Lookup

You can also lookup up to 100 IP addresses at once with a bulk API lookup mode.

For that, you will need to make a POST request. See this example with `curl`:

```bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"ips": ["162.158.0.0", "2406:dafe:e0ff:ffff:ffff:ffff:dead:beef", "162.88.0.0", "20.41.193.225"]}' \
  https://api.incolumitas.com/datacenter
```

The HTTP method needs to be `POST` and the API endpoint is the same: **https://api.incolumitas.com/datacenter**.

Only the IP addresses that have a match (`is_datacenter` equals `true`) will returned by the API. All other IP addresses will be omitted in order to save network bandwith. Duplicate IPs will be removed.

Example with JavaScript:

```JavaScript
const ips = ["162.158.0.0", "2406:dafe:e0ff:ffff:ffff:ffff:dead:beef", "162.88.0.0", "20.41.193.225"];

fetch('https://api.incolumitas.com/datacenter', {
  method: 'POST',
  headers: {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ips: ips})
}).then(res => res.json())
  .then(res => console.log(res));
```

### More Examples for the IP Address Datacenter API

In the following section, I will show examples for looking up IP addresses belonging to the three biggest cloud providers AWS, Azure and GCP:

#### Looking up Azure IP Address

Looking up an Azure IP address: [https://api.incolumitas.com/datacenter?ip=20.41.193.225](https://api.incolumitas.com/datacenter?ip=20.41.193.225)

```json
{
  "ip": "20.41.193.225",
  "is_datacenter": true,
  "src": "selfPublished",
  "cidr": "20.41.193.224/27",
  "name": "AzurePortal",
  "datacenter": "Microsoft Azure",
  "region": "",
  "regionId": 0,
  "platform": "Azure",
  "systemService": "AzurePortal",
  "rir": "arin",
  "asn": {
    "asn": 8075,
    "cidr": "20.40.0.0/13",
    "descr": "MICROSOFT-CORP-MSN-AS-BLOCK, US",
    "country": "us"
  },
  "location": {
    "country": "us"
  },
  "elapsed_ms": 0.19
}
```

#### Looking up AWS IP Address

Looking up an AWS IP address: [https://api.incolumitas.com/datacenter?ip=3.5.140.2](https://api.incolumitas.com/datacenter?ip=3.5.140.2)

```json
{
  "ip": "3.5.140.2",
  "is_datacenter": true,
  "src": "selfPublished",
  "cidr": "3.5.140.0/22",
  "region": "ap-northeast-2",
  "datacenter": "Amazon AWS",
  "service": "AMAZON",
  "network_border_group": "ap-northeast-2",
  "rir": "arin",
  "asn": {
    "asn": 16509,
    "cidr": "3.5.140.0/22",
    "descr": "AMAZON-02, US",
    "country": "us"
  },
  "location": {
    "country": "us"
  },
  "elapsed_ms": 0.14
}
```

#### Looking up GCP IP Address

Looking up an GCP IP address: [https://api.incolumitas.com/datacenter?ip=23.236.48.55](https://api.incolumitas.com/datacenter?ip=23.236.48.55)

```json
{
  "ip": "23.236.48.55",
  "is_datacenter": true,
  "datacenter": "Google Cloud",
  "cidr": "23.236.48.0/20",
  "src": "whois",
  "rir": "arin",
  "asn": {
    "asn": 15169,
    "cidr": "23.236.48.0/20",
    "descr": "GOOGLE, US",
    "country": "us"
  },
  "location": {
    "country": "us"
  },
  "elapsed_ms": 0.17
}
```

#### Looking up AWS IPv6 Address

And looking up a AWS IPv6 address: [https://api.incolumitas.com/datacenter?ip=2600:1F18:7FFF:F800:0000:ffff:0000:0000](https://api.incolumitas.com/datacenter?ip=2600:1F18:7FFF:F800:0000:ffff:0000:0000):

```json
{
  "ip": "2600:1F18:7FFF:F800:0000:ffff:0000:0000",
  "is_datacenter": true,
  "src": "selfPublished",
  "cidr": "2600:1f18:7fff:f800::/56",
  "region": "us-east-1",
  "datacenter": "Amazon AWS",
  "service": "ROUTE53_HEALTHCHECKS",
  "network_border_group": "us-east-1",
  "rir": "ARIN",
  "asn": {
    "asn": 14618,
    "cidr": "2600:1f18:6000::/35",
    "descr": "AMAZON-AES, US",
    "country": "us"
  },
  "location": {
    "country": "not found"
  },
  "elapsed_ms": 0.54
}
```

As you can see from the example lookups above, the API gives additional meta data information for a specific IP address such as regional and data center information.

## Sources for Datacenter IP Address Ranges

Where do I get the [CIDR](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) address ranges for the datacenters?

Most datacenters publish their own IP ranges, such as AWS or Google Cloud. But often, those IP address ranges are not complete. For that reason, other means of lookup have to be used, such as [consulting whois data from Regional Internet Registries](https://en.wikipedia.org/wiki/WHOIS) or searching through [ASN data](https://en.wikipedia.org/wiki/Autonomous_system_(Internet)) databases.

This API uses a proprietary datacenter/hosting discovery algortithm that uses:

1. Self reported IP ranges from cloud providers
2. Publicly accessible whois data from regional internet registries such as ARIN or APNIC
3. Daily published AS and netmask information from backbone Internet routers

## Change Log

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
+ Added dedicated API endpoint: https://api.incolumitas.com/datacenter?ip=3.5.140.2
+ Old API Endpoint: https://abs.incolumitas.com/datacenter?ip=1.2.3.4