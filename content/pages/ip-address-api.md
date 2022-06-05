Title: Datacenter IP Address API
Date: 2021-09-29 00:13
Modified: 2022-06-05 16:13
Author: Nikolai Tschacher
Slug: Datacenter-IP-API
Status: published
Sortorder: 5

The Datacenter IP Address API can be used to check whether an IP address belongs to a data center IP address range such as Azure, AWS, Digitalocean, Google Cloud Platform and many other cloud providers. Please read the [full blog article]({filename}/Security/datacenter-ip-api.md) for a thorough introduction.

And please consider reading another blog article:  ["How to find out if an IP address belongs to a Hosting / Cloud Provider?"]({filename}/Security/datacenter-ip-api-second.md) - This blog article contains a detailed explanation how to use public data sources such as whois data to determine if an IP address belongs to a datacenter.


| <!-- -->    | <!-- -->    |
|-------------|-------------|
| **Author**         | Nikolai Tschacher (incolumitas.com)     |
| **API Access**         | Free & unlimited (fair use)         |
| **API Version**         | **v0.8 (5th June 2022)**         |
| **API Endpoint**         | [**https://api.incolumitas.com/datacenter?ip=3.5.140.2**](https://api.incolumitas.com/datacenter?ip=3.5.140.2)         |
| **Supported Datacenters**         | Amazon AWS, Microsoft Azure, Google Cloud, IBM Cloud, OVH, Digital Ocean, Hetzner Online, CloudFlare, Oracle Cloud, Tor Network and many more         |
| **IPv6 Support**         | Yes         |


Key Features:

+ **Always updated**: The API database is automatically updated every day. Data is gathered from many sources: Self published IP ranges from large cloud providers, whois lookups and many other sources
+ **Pretty fast**: The API is very performant. On average, an IP lookup takes `0.042ms` (server side time consumed)
+ **Bulk IP Lookups**: You can lookup up to 100 IP addresses per API call

## Live API

<div class="ipAPIDemo">
  <label style="font-weight: 600; font-size: 15px" for="ip">IP Address:</label>
  <input style="padding: 6px;" type="text" id="ip" name="ip" value="13.34.52.117"><br><br>
  <input class="orange_button" type="submit" value="Make API Request">
  <pre id="data">{
  "message": "Please make an API request",
}</pre>
</div>

<script>
document.querySelector('.ipAPIDemo input[type="submit"]').addEventListener('click', function(evt) {
  var ip = document.getElementById('ip').value;
  fetch('https://api.incolumitas.com/datacenter?ip=' + ip) 
  .then(response => response.json())
  .then(function(data) {
    document.getElementById('data').innerText = JSON.stringify(data, null, 2);
  })
})
</script>


## API Endpoints

### Endpoint /datacenter

| <!-- -->         | <!-- -->                                           |   
|------------------|----------------------------------------------------|
| **Endpoint**       | /datacenter                                  |
| **Parameter**       | `ip` - The IPv4 or IPv6 address to lookup                                 |
| **Description**  | If the provided IP address belongs to a datacenter, the API will return all meta data for the datacenter. The attribute `is_datacenter` will be set to `true`.   |
| **Live API Call** | [https://api.incolumitas.com/datacenter?ip=13.34.52.117](https://api.incolumitas.com/datacenter?ip=13.34.52.117)    


### Endpoint /info

| <!-- -->         | <!-- -->                                           |   
|------------------|----------------------------------------------------|
| **Endpoint**       | /info                                  |
| **Description**  | Returns all datacenters that are currently present in the API. The number of IPv4 (`total_ipv4`) and IPv6 (`total_ipv6`) addresses for each datacenter will also be provided.   |
| **Live API Call** | [https://api.incolumitas.com/info](https://api.incolumitas.com/info)    


## Change Log

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


## API Usage Documentation

You can reach the API endpoint with this URL: **https://api.incolumitas.com/datacenter?ip=**

If you pass the IP address `3.5.140.2` to the API by calling [https://api.incolumitas.com/datacenter?ip=3.5.140.2](https://api.incolumitas.com/datacenter?ip=3.5.140.2), you'll obtain the result:

```json
{
  "ip": "3.5.140.2",
  "is_datacenter": true,
  "ip_data_source": "self_published_ip_ranges",
  "cidr": "3.5.140.0/22",
  "region": "ap-northeast-2",
  "datacenter": "Amazon AWS",
  "service": "AMAZON",
  "network_border_group": "ap-northeast-2",
  "other_matches": [
    {
      "ip_data_source": "self_published_ip_ranges",
      "cidr": "3.5.140.0/22",
      "region": "ap-northeast-2",
      "datacenter": "Amazon AWS",
      "service": "EC2",
      "network_border_group": "ap-northeast-2"
    }
  ],
  "elapsed_ms": 1.15
}
```

Alternatively, you can also lookup IPv6 addresses. Try the url [https://api.incolumitas.com/datacenter?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef](https://api.incolumitas.com/datacenter?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef), which yields:

```json
{
  "ip": "2406:dafe:e0ff:ffff:ffff:ffff:dead:beef",
  "is_datacenter": true,
  "ip_data_source": "self_published_ip_ranges",
  "cidr": "2406:dafe:e000::/40",
  "region": "ap-east-1",
  "datacenter": "Amazon AWS",
  "service": "AMAZON",
  "network_border_group": "ap-east-1",
  "elapsed_ms": 1.34
}
```

If you don't specify any IP address with the `ip=` query parameter and you invoke [https://api.incolumitas.com/datacenter](https://api.incolumitas.com/datacenter) directly, the client's own IP address will be used for lookup. In my case, I get the following output:

```json
{
  "ip": "84.157.228.82",
  "is_datacenter": false,
  "elapsed_ms": 0.28
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
  "ip_data_source": "self_published_ip_ranges",
  "cidr": "20.41.193.224/27",
  "name": "AzurePortal",
  "datacenter": "Microsoft Azure",
  "region": "",
  "regionId": 0,
  "platform": "Azure",
  "systemService": "AzurePortal",
  "other_matches": [
    {
      "datacenter": "Microsoft Azure",
      "asn": "8075",
      "cidr": "20.40.0.0/13",
      "ip_data_source": "whois_database"
    }
  ],
  "elapsed_ms": 16.2
}
```

#### Looking up AWS IP Address

Looking up an AWS IP address: [https://api.incolumitas.com/datacenter?ip=3.5.140.2](https://api.incolumitas.com/datacenter?ip=3.5.140.2)

```json
{
  "ip": "3.5.140.2",
  "is_datacenter": true,
  "ip_data_source": "self_published_ip_ranges",
  "cidr": "3.5.140.0/22",
  "region": "ap-northeast-2",
  "datacenter": "Amazon AWS",
  "service": "AMAZON",
  "network_border_group": "ap-northeast-2",
  "other_matches": [
    {
      "ip_data_source": "self_published_ip_ranges",
      "cidr": "3.5.140.0/22",
      "region": "ap-northeast-2",
      "datacenter": "Amazon AWS",
      "service": "EC2",
      "network_border_group": "ap-northeast-2"
    }
  ],
  "elapsed_ms": 1.16
}
```

#### Looking up GCP IP Address

Looking up an GCP IP address: [https://api.incolumitas.com/datacenter?ip=23.236.48.55](https://api.incolumitas.com/datacenter?ip=23.236.48.55)

```json
{
  "ip": "23.236.48.55",
  "is_datacenter": true,
  "datacenter": "Google Cloud",
  "asn": "15169",
  "cidr": "23.236.48.0/20",
  "ip_data_source": "whois_database",
  "other_matches": [
    {
      "ip_data_source": "self_published_ip_ranges",
      "cidr": "23.236.48.0/20",
      "datacenter": "Google Cloud"
    }
  ],
  "elapsed_ms": 27.27
}
```

#### Looking up AWS IPv6 Address

And looking up a AWS IPv6 address: [https://api.incolumitas.com/datacenter?ip=2600:1F18:7FFF:F800:0000:ffff:0000:0000](https://api.incolumitas.com/datacenter?ip=2600:1F18:7FFF:F800:0000:ffff:0000:0000):

```json
{
  "ip": "2600:1F18:7FFF:F800:0000:ffff:0000:0000",
  "is_datacenter": true,
  "ip_data_source": "self_published_ip_ranges",
  "cidr": "2600:1f18:7fff:f800::/56",
  "region": "us-east-1",
  "datacenter": "Amazon AWS",
  "service": "ROUTE53_HEALTHCHECKS",
  "network_border_group": "us-east-1",
  "elapsed_ms": 0.38
}
```

As you can see from the example lookups above, the API gives additional meta data information for a specific IP address such as regional and data center information.

## Supported Datacenters / Cloud Services

Currently, the API supports IP address ranges from the following [cloud providers](https://udger.com/resources/datacenter-list):

| # | Cloud Provider | Number of IPv4 Addresses | Number of IPv6 Addresses| API support |
|------------|------------|------------|------------|------------|
|1| [Amazon AWS](https://aws.amazon.com/) | 147,119,660 | 4,722,366,482,869,645,000,000|✓|
|2| [Microsoft Azure](https://azure.microsoft.com/) | 104,291,502 | 1,208,925,819,614,629,200,000,000|✓|
|3| [Alibaba Cloud](https://www.alibabacloud.com/) | 57,117,523 | 633,825,300,114,114,700,000,000,000,000|✓|
|4| [Google Cloud](https://cloud.google.com/) | 50,488,912 | 633,825,300,114,114,700,000,000,000,000|✓|
|5| [Akamai Technologies](https://www.akamai.com/) | 42,869,267 | 1,208,925,819,614,629,200,000,000|✓|
|6| [One.com A/S](https://www.one.com/) | 24,263,967 | 79,228,162,514,264,340,000,000,000,000|✓|
|7| [OVH](http://www.ovh.com/) | 16,857,348 | 18,446,744,073,709,552,000|✓|
|8| [IBM Cloud](https://www.ibm.com/cloud) | 14,186,547 | 1,208,925,819,614,629,200,000,000|✓|
|9| [Savvis](http://www.savvis.net/) | 10,154,984 | 4,835,703,278,458,517,000,000,000|✓|
|10| [Hetzner Online](https://www.hetzner.com/) | 9,809,532 | 19,807,040,628,566,084,000,000,000,000|✓|
|11| [Cloudflare](https://www.cloudflare.com/) | 9,173,180 | 79,228,162,514,264,340,000,000,000,000|✓|
|12| [Liquid Web](https://www.liquidweb.com/) | 8,873,676 | 1,208,925,819,614,629,200,000,000|✓|
|13| [Tencent Cloud](https://intl.cloud.tencent.com/) | 7,908,768 | 0|✓|
|14| [DigitalOcean](https://www.digitalocean.com/) | 6,418,707 | 79,228,162,514,264,340,000,000,000,000|✓|
|15| [Huawei Cloud Service](https://www.huaweicloud.com/) | 5,326,661 | 1,208,925,819,614,629,200,000,000|✓|
|16| [LeaseWeb](https://www.leaseweb.com/) | 4,490,190 | 79,228,162,514,264,340,000,000,000,000|✓|
|17| [1&1 Internet](http://www.1and1.com/) | 4,328,725 | 309,485,009,821,345,100,000,000,000|✓|
|18| [Sakura Internet Inc.](http://www.sakura.ne.jp/) | 3,960,886 | 1,208,925,819,614,629,200,000,000|✓|
|19| [Equinix, Inc.](http://www.equinix.com/) | 3,351,217 | 1,208,925,819,614,629,200,000,000|✓|
|20| [M247 Ltd](https://m247.com/) | 2,836,520 | 1,208,925,819,614,629,200,000,000|✓|
|21| [Rackspace, Inc.](https://www.rackspace.com/) | 2,713,478 | 1,208,925,819,614,629,200,000,000|✓|
|22| [Cloudinnovation](http://cloudinnovation.org/) | 2,414,334 | 18,446,744,073,709,552,000|✓|
|23| [Claranet limited](https://www.claranet.com/) | 2,403,812 | 18,446,744,073,709,552,000|✓|
|24| [Energy Group Networks](https://egihosting.com/) | 2,380,800 | 1,208,925,819,614,629,200,000,000|✓|
|25| [Fiber Grid Inc](https://fibergrid.eu/) | 2,236,926 | 0|✓|
|26| [Selectel](https://selectel.com/) | 2,060,047 | 309,485,009,821,345,100,000,000,000|✓|
|27| [PlusServer GmbH](https://www.plusserver.com/) | 2,009,405 | 1,208,925,819,614,629,200,000,000|✓|
|28| [Oracle Cloud](https://www.oracle.com/cloud/) | 1,966,602 | 0|✓|
|29| [Online SAS (Scaleway)](https://www.scaleway.com/) | 1,933,543 | 39,614,081,257,132,170,000,000,000,000|✓|
|30| [GoDaddy Operating Company, LLC.](https://www.godaddy.com/) | 1,641,253 | 79,228,162,514,264,340,000,000,000,000|✓|
|31| [GHOSTnet GmbH](http://www.ghostnet.de/) | 1,512,934 | 18,446,744,073,709,552,000|✓|
|32| [Linode](https://www.linode.com/) | 1,496,005 | 1,208,925,819,614,629,200,000,000|✓|
|33| [DreamHost](https://www.dreamhost.com/) | 1,458,751 | 1,208,925,819,614,629,200,000,000|✓|
|34| [Aruba S.p.a](https://www.aruba.it/) | 1,455,713 | 1,208,925,819,614,629,200,000,000|✓|
|35| [ServiHosting Networks S.L.](http://servihosting.es/) | 1,437,324 | 633,825,300,114,114,700,000,000,000,000|✓|
|36| [Gmo Internet, Inc](https://www.gmo.jp/) | 1,404,828 | 1,208,925,819,614,629,200,000,000|✓|
|37| [Internap Corporation](http://www.internap.com/) | 1,329,755 | 18,446,744,073,709,552,000|✓|
|38| [Choopa, LLC.](https://www.choopa.com/) | 1,292,249 | 1,208,925,819,614,629,200,000,000|✓|
|39| [Contabo GmbH](https://contabo.de/) | 1,272,788 | 79,228,162,514,264,340,000,000,000,000|✓|
|40| [Strato AG](https://www.strato.de/) | 1,247,353 | 1,208,925,819,614,629,200,000,000|✓|
|41| [iomart Hosting Ltd](http://www.rapidswitch.com/) | 1,241,441 | 79,228,162,514,264,340,000,000,000,000|✓|
|42| [UCloud](https://www.ucloud.cn/) | 1,088,546 | 1,208,925,819,614,629,200,000,000|✓|
|43| [Aptum Technologies](https://aptum.com/) | 1,044,480 | 309,485,009,821,345,100,000,000,000|✓|
|44| [Host Europe](https://www.hosteurope.de/) | 944,211 | 79,228,162,514,264,340,000,000,000,000|✓|
|45| [ColoCrossing](https://www.colocrossing.com/) | 852,736 | 0|✓|
|46| [home.pl S.A.](https://home.pl/) | 808,037 | 1,208,925,819,614,629,200,000,000|✓|
|47| [Quadranet, Inc](https://www.quadranet.com/) | 681,471 | 2,417,851,639,229,258,300,000,000|✓|
|48| [A2 Hosting](http://www.mittwald.de/) | 608,289 | 79,228,162,514,264,340,000,000,000,000|✓|
|49| [Fastly, Inc.](https://www.fastly.com/) | 607,764 | 1,208,925,819,614,629,200,000,000|✓|
|50| [Daou Technology](http://www.daouidc.com/) | 583,200 | 79,228,162,514,264,340,000,000,000,000|✓|
|51| [Lumen](https://www.lumen.com/) | 577,124 | 1,208,925,819,614,629,200,000,000|✓|
|52| [DediPath](https://dedipath.com/) | 541,787 | 18,446,744,073,709,552,000|✓|
|53| [It7 Networks Inc](https://www.it7.net/) | 504,601 | 1,208,925,819,614,629,200,000,000|✓|
|54| [DataCamp Limited](https://datacamp.co.uk/) | 493,795 | 633,825,300,114,114,700,000,000,000,000|✓|
|55| [Hostway](https://hostway.com/) | 466,074 | 1,208,925,819,614,629,200,000,000|✓|
|56| [trueserver.nl](http://trueserver.nl/) | 460,446 | 1,208,925,819,614,629,200,000,000|✓|
|57| [IP Exchange GmbH](http://www.ip-exchange.de/) | 454,862 | 1,208,925,819,614,629,200,000,000|✓|
|58| [G-Core Labs S.A.](https://gcorelabs.com/) | 445,565 | 19,342,813,113,834,067,000,000,000|✓|
|59| [Locaweb Serviços de Internet S/A](http://www.locaweb.com.br/) | 445,440 | 1,208,925,819,614,629,200,000,000|✓|
|60| [myLoc](https://www.myloc.de/) | 444,435 | 1,208,925,819,614,629,200,000,000|✓|
|61| [Reg.Ru Hosting](https://www.reg.ru/hosting/) | 436,212 | 1,208,925,819,614,629,200,000,000|✓|
|62| [Hostinger](https://www.hostinger.com/) | 423,636 | 1,208,925,819,614,629,200,000,000|✓|
|63| [X server Co., Ltd.](https://www.xserver.co.jp/) | 404,791 | 1,208,925,819,614,629,200,000,000|✓|
|64| [netcup GmbH](https://www.netcup.de/) | 391,516 | 1,208,925,819,614,629,200,000,000|✓|
|65| [Zscaler, Inc.](https://www.zscaler.com/) | 369,756 | 79,228,162,514,264,340,000,000,000,000|✓|
|66| [Zenlayer](https://www.zenlayer.com/) | 367,399 | 633,825,300,114,114,700,000,000,000,000|✓|
|67| [CoreSpace,Inc.](https://corespace.com/) | 358,144 | 79,228,162,514,264,340,000,000,000,000|✓|
|68| [Transip B.V](https://www.transip.nl/) | 356,869 | 1,208,925,819,614,629,200,000,000|✓|
|69| [kinx.net](https://www.kinx.net/) | 344,831 | 1,208,925,819,614,629,200,000,000|✓|
|70| [XT Global Networks LTD](http://www.xtglobal.vg/) | 341,000 | 79,228,162,514,264,340,000,000,000,000|✓|
|71| [Hostwinds.com](https://www.hostwinds.com/) | 335,610 | 633,825,300,114,114,700,000,000,000,000|✓|
|72| [Datapipe](http://www.datapipe.com/) | 330,471 | 1,208,925,819,614,629,200,000,000|✓|
|73| [Combell NV](https://www.combell.com/) | 326,766 | 1,208,925,819,614,629,200,000,000|✓|
|74| [Arsys](https://www.arsys.es/) | 302,352 | 1,208,925,819,614,629,200,000,000|✓|
|75| [Xneelo](https://xneelo.co.za/) | 300,544 | 18,446,744,073,709,552,000|✓|
|76| [Imperva, Inc.](https://www.imperva.com/) | 287,718 | 79,228,162,514,264,340,000,000,000,000|✓|
|77| [ServerCentral](http://www.servercentral.net/) | 286,780 | 633,825,300,114,114,700,000,000,000,000|✓|
|78| [DomainFactory](https://www.df.eu/) | 282,475 | 1,208,925,819,614,629,200,000,000|✓|
|79| [latisys](http://www.latisys.com/) | 279,869 | 633,825,300,114,114,700,000,000,000,000|✓|
|80| [iWeb Technologies Inc.](https://iweb.com/) | 262,142 | 79,228,162,514,264,340,000,000,000,000|✓|
|81| [TimeWeb](https://timeweb.com/) | 246,624 | 1,208,925,819,614,629,200,000,000|✓|
|82| [Stackpath, LLC](https://www.stackpath.com/) | 241,266 | 1,208,925,819,614,629,200,000,000|✓|
|83| [Infomaniak](https://www.infomaniak.com/) | 227,220 | 1,208,925,819,614,629,200,000,000|✓|
|84| [Input Output Flood LLC](https://ioflood.com/) | 226,560 | 79,228,162,514,264,340,000,000,000,000|✓|
|85| [Heficed](https://www.heficed.com/) | 215,780 | 1,208,925,819,614,629,200,000,000|✓|
|86| [Servers Australia](https://www.serversaustralia.com.au/) | 211,790 | 1,208,925,819,614,629,200,000,000|✓|
|87| [Dreamscape](https://www.dreamscapenetworks.com/) | 201,547 | 4,951,760,157,141,521,000,000,000,000|✓|
|88| [Clouvider Limited](https://www.clouvider.com/) | 198,184 | 1,208,925,819,614,629,200,000,000|✓|
|89| [Node4](https://www.node4.co.uk/) | 184,331 | 18,446,744,073,709,552,000|✓|
|90| [Performive LLC](https://performive.com/) | 174,839 | 1,208,925,819,614,629,200,000,000|✓|
|91| [Wholesale Internet, Inc](https://www.wholesaleinternet.net/) | 157,497 | 1,208,925,819,614,629,200,000,000|✓|
|92| [Rackray](http://www.rackray.eu/) | 157,078 | 1,208,925,819,614,629,200,000,000|✓|
|93| [LogicWeb Inc.](https://www.logicweb.com/) | 156,658 | 633,825,300,114,114,700,000,000,000,000|✓|
|94| [Redstation Limited](http://redstation.com/) | 152,921 | 1,208,925,819,614,629,200,000,000|✓|
|95| [SysEleven GmbH](https://www.syseleven.de/en/) | 149,797 | 1,208,925,819,614,629,200,000,000|✓|
|96| [Fortress Integrated Technologies](https://www.dedicatednow.com/) | 147,310 | 1,208,925,819,614,629,200,000,000|✓|
|97| [Steadfast](https://www.steadfast.net/) | 147,200 | 1,208,925,819,614,629,200,000,000|✓|
|98| [Duocast B.V.](https://duocast.nl/) | 144,704 | 18,446,744,073,709,552,000|✓|
|99| [HopOne](http://www.hopone.net/) | 137,216 | 1,208,925,819,614,629,200,000,000|✓|
|100| [tzulo, inc.](http://www.tzulo.com/) | 136,192 | 4,951,760,157,141,521,000,000,000,000|✓|
|101| [Mittwald](http://www.mittwald.de/) | 135,185 | 309,485,009,821,345,100,000,000,000|✓|
|102| [Namecheap](https://www.namecheap.com/) | 130,809 | 79,228,162,514,264,340,000,000,000,000|✓|
|103| [LightEdge Solutions, Inc.](https://www.lightedge.com/) | 123,392 | 4,951,760,157,141,521,000,000,000,000|✓|
|104| [Sharktech Inc.](https://sharktech.net/) | 121,856 | 0|✓|
|105| [Enzu Inc.](https://www.enzu.com/) | 119,976 | 1,208,925,819,614,629,200,000,000|✓|
|106| [24Shells Inc](https://www.24shells.net/) | 111,356 | 633,825,300,114,114,700,000,000,000,000|✓|
|107| [The Constant Company, LLC](https://www.constant.com/) | 100,598 | 0|✓|
|108| [Unified Layer](https://www.unitedlayer.com/) | 91,904 | 1,208,925,819,614,629,200,000,000|✓|
|109| [DinaHosting S.L.](https://dinahosting.com/) | 88,450 | 4,722,366,482,869,645,000,000|✓|
|110| [SuperHosting.BG](https://www.superhosting.bg/) | 84,764 | 1,208,925,819,614,629,200,000,000|✓|
|111| [veesp.com vps clients](https://veesp.com/) | 79,915 | 79,228,162,514,264,340,000,000,000,000|✓|
|112| [Serverplan srl](https://www.serverplan.com/) | 78,120 | 1,208,925,819,614,629,200,000,000|✓|
|113| [First Colo](https://www.first-colo.net/) | 76,521 | 18,446,744,073,709,552,000|✓|
|114| [Hivelocity](https://www.hivelocity.net/) | 76,031 | 79,228,162,514,264,340,000,000,000,000|✓|
|115| [VSHosting](https://www.vshosting.cz/) | 72,500 | 1,208,925,819,614,629,200,000,000|✓|
|116| [Krystal Hosting](https://krystal.uk/) | 65,897 | 633,825,300,114,114,700,000,000,000,000|✓|
|117| [GZ Systems (PureVPN)](https://www.purevpn.com/) | 62,592 | 0|✓|
|118| [Media Temple](https://mediatemple.net/) | 62,464 | 0|✓|
|119| [BuyVM (frantech)](https://buyvm.net/) | 60,159 | 1,208,925,819,614,629,200,000,000|✓|
|120| [InMotion](https://www.inmotionhosting.com/) | 57,855 | 633,825,300,114,114,700,000,000,000,000|✓|
|121| [Phoenix NAP, LLC](https://phoenixnap.com/) | 56,039 | 1,208,925,819,614,629,200,000,000|✓|
|122| [cloudsigma](https://www.cloudsigma.com/) | 46,576 | 1,208,925,819,614,629,200,000,000|✓|
|123| [Kamatera](https://www.kamatera.com/) | 45,286 | 1,208,925,819,614,629,200,000,000|✓|
|124| [Hostpoint](https://www.hostpoint.ch/en) | 42,999 | 4,951,760,157,141,521,000,000,000,000|✓|
|125| [Packethub S.A.](https://www.packethub.net/) | 41,536 | 1,208,925,819,614,629,200,000,000|✓|
|126| [World4You Internet Services GmbH](https://www.world4you.com/) | 37,030 | 633,825,300,114,114,700,000,000,000,000|✓|
|127| [Beget](https://beget.com/en) | 33,792 | 0|✓|
|128| [Synergy Wholesale](https://synergywholesale.com/) | 30,450 | 1,208,925,819,614,629,200,000,000|✓|
|129| [Amsio B.V.](https://www.amsio.com/) | 28,203 | 0|✓|
|130| [ServerHub](https://www.serverhub.com/) | 27,647 | 79,228,162,514,264,340,000,000,000,000|✓|
|131| [Hosting Ukraine](https://www.ukraine.com.ua/) | 26,873 | 18,446,744,073,709,552,000|✓|
|132| [Digital Pacific](https://www.digitalpacific.com.au/) | 24,048 | 0|✓|
|133| [Hurricane Electic](http://www.he.net/) | 21,557 | 1,208,925,819,614,629,200,000,000|✓|
|134| [20i](https://www.20i.com/) | 21,229 | 4,722,366,482,869,645,000,000|✓|
|135| [Umbrellar](https://www.umbrellar.com/) | 19,497 | 0|✓|
|136| [hosting.ua](http://hosting.ua/) | 12,349 | 1,208,925,819,614,629,200,000,000|✓|
|137| [Hostgator](https://www.hostgator.com/) | 12,340 | 0|✓|
|138| [HostDime](https://www.hostdime.com/) | 5,426 | 633,825,300,114,114,700,000,000,000,000|✓|
|139| [Psychz Networks](https://www.psychz.net/) | 5,112 | 0|✓|
|140| [Optimate Server](http://optimate-server.de/) | 5,108 | 18,446,744,073,709,552,000|✓|
|141| [Webair Internet Development Inc](https://www.webair.com/) | 4,863 | 633,825,300,114,114,700,000,000,000,000|✓|
|142| [ALL INKL](https://all-inkl.com/) | 4,350 | 0|✓|
|143| [FDC Servers](https://www.fdcservers.net/) | 3,325 | 0|✓|
|144| [Cologix, Inc.](http://www.cologix.com/) | 3,069 | 0|✓|
|145| [Peak10](http://www.peak10.com/) | 2,048 | 0|✓|
|146| [MULTACOM Inc.](http://multacom.com/) | 2,045 | 316,912,650,057,057,350,000,000,000,000|✓|
|147| [Colocation America Inc](http://www.colocationamerica.com/) | 1,536 | 0|✓|
|148| [HostPapa](https://www.hostpapa.com/) | 1,531 | 0|✓|
|149| [Vultr Holdings LLC](https://www.vultr.com/) | 1,309 | 309,485,009,821,345,100,000,000,000|✓|
|150| [Bluehosting](https://www.bluehosting.cl/) | 1,024 | 0|✓|
|151| [Fasthosts Internet Ltd](https://www.fasthosts.co.uk/) | 1,024 | 2,417,851,639,229,258,300,000,000|✓|
|152| [Bluehost Inc.](https://www.bluehost.com/) | 1,022 | 309,485,009,821,345,100,000,000,000|✓|
|153| [Ubiquity Hosting](https://www.ubiquityhosting.com/) | 767 | 0|✓|
|154| [AlmaHost Ltd](https://almahost.co.uk/) | 512 | 0|✓|
|155| [TierPoint](https://www.tierpoint.com/) | 512 | 1,208,925,819,614,629,200,000,000|✓|
|156| [ServerMania Inc.](https://www.servermania.com/) | 512 | 0|✓|
|157| [Mullvad VPN](https://mullvad.net/) | 507 | 1,208,925,819,614,629,200,000,000|✓|
|158| [American Internet Services](https://nfinit.com/) | 63 | 79,228,162,514,264,340,000,000,000,000|✓|
|159| [Server Central Network](https://www.servercentral.com/) | 0 | 18,446,744,073,709,552,000|✓|


The API database is updated every 4 hours with the official source of the IP address ranges of the cloud provides listed above (with a ✓). For some cloud providers such as OVH or Hetzner there is no official IP address range source, so I have to rely on [third party sources](https://bgp.he.net/search?search%5Bsearch%5D=OVH&commit=Search).

## Sources for Datacenter IP Address Ranges

Where do I get the [CIDR](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) address ranges for the datacenters?

Most datacenters publish their own IP ranges, such as AWS or Google Cloud. But often, those IP address ranges are not complete. For that reason, other means of lookup have to be used, such as [whois lookups](https://en.wikipedia.org/wiki/WHOIS) or searching through [ASN](https://en.wikipedia.org/wiki/Autonomous_system_(Internet)) databases.

This API follows the following lookup logic:

1. First, check if the IP is to be found in the published IP ranges from the providers.
2. If the first step farils, a lookup of the IP address with `whois 105.226.177.72` is conducted. If the orgname belongs to a datacenter, we have a match. Simple string matching.
3. If the above whois lookup did not produce a datacenter match, we lookup the autonomous system `OriginAS: AS21928` and we perform a simple grep `cat ripe-asn.txt | grep -E -i "^13335\s"` in the ASN lists to check if the ASN belongs to a large cloud provider.

Other techniques are pursuited, if the above algorithm doesn't yield a match.

