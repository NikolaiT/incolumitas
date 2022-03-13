Title: Datacenter IP Address API
Date: 2021-09-29 00:13
Modified: 2022-03-07 00:13
Author: Nikolai Tschacher
Slug: Datacenter-IP-API
Status: published
Sortorder: 5

I maintain a public API to check whether an IP address belongs to a data center IP address range such as Azure, AWS, Digitalocean, Google Cloud Platform and many other cloud providers. Please read the [full blog article]({filename}/Security/datacenter-ip-api.md) for more a through introduction.

The purpose of this API is simple: This API allows you to check whether an IP address belongs to an datacenter or not.


| <!-- -->    | <!-- -->    |
|-------------|-------------|
| **Author**         | Nikolai Tschacher (incolumitas.com)     |
| **API Access**         | Free & unlimited (fair use)         |
| **API Version**         | **v0.5 (11th March 2022)**         |
| **API Endpoint**         | [**https://api.incolumitas.com/datacenter?ip=3.5.140.2**](https://api.incolumitas.com/datacenter?ip=3.5.140.2)         |
| **Supported Datacenters**         | Amazon AWS, Microsoft Azure, Google Cloud, IBM Cloud, OVH, Digital Ocean, Hetzner Online, CloudFlare, Oracle Cloud, Tor Network and many more         |
| **IPv6 Support**         | Yes         |

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


## Datacenter/Cloud IP API Key Features

+ **Always updated**: The API database is automatically updated every day. Data is gathered from many sources: Self published IP ranges from large cloud providers, whois lookups and many other sources
+ **Pretty fast**: The API is very performant. On average, an IP lookup takes `0.042ms` (server side time consumed)
+ **Bulk IP Lookups**: You can lookup up to 100 IP addresses per API call


## ChangeLog

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
  "cidr": "3.5.140.0/22",
  "region": "ap-northeast-2",
  "service": "AMAZON",
  "network_border_group": "ap-northeast-2",
  "other_matches": [
    {
      "cidr": "3.5.140.0/22",
      "region": "ap-northeast-2",
      "service": "S3",
      "network_border_group": "ap-northeast-2"
    },
    {
      "cidr": "3.5.140.0/22",
      "region": "ap-northeast-2",
      "service": "EC2",
      "network_border_group": "ap-northeast-2"
    }
  ],
  "lookup_method": "public_ip_ranges",
  "elapsed_ms": 0.08
}
```

Alternatively, you can also lookup IPv6 addresses. Try the url [https://api.incolumitas.com/datacenter?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef](https://api.incolumitas.com/datacenter?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef), which yields:

```json
{
  "ip": "2406:dafe:e0ff:ffff:ffff:ffff:dead:beef",
  "is_datacenter": true,
  "cidr": "2406:dafe:e000::/40",
  "region": "ap-east-1",
  "service": "AMAZON",
  "network_border_group": "ap-east-1",
  "lookup_method": "public_ip_ranges",
  "elapsed_ms": 16.14
}
```

If you don't specify any IP address with the `ip=` query parameter and you invoke [https://api.incolumitas.com/datacenter](https://api.incolumitas.com/datacenter) directly, the client's own IP address will be used for lookup. In my case, I get the following output:

```json
{
  "ip": "46.114.160.242",
  "is_datacenter": false,
  "lookup_method": "public_ip_ranges",
  "elapsed_ms": 0.29
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

### More Examples for the IP Address Datacenter API

In the following section, I will show examples for looking up IP addresses belonging to the three biggest cloud providers AWS, Azure and GCP:

#### Looking up Azure IP Address

Looking up an Azure IP address: [https://api.incolumitas.com/datacenter?ip=20.41.193.225](https://api.incolumitas.com/datacenter?ip=20.41.193.225)

```json
{
  "ip": "20.41.193.225",
  "is_datacenter": true,
  "cidr": "20.41.193.224/27",
  "name": "AzurePortal",
  "service": "Azure",
  "region": "",
  "regionId": 0,
  "platform": "Azure",
  "systemService": "AzurePortal",
  "other_matches": [
    {
      "cidr": "20.41.193.224/27",
      "name": "AzurePortal.SouthIndia",
      "service": "Azure",
      "region": "southindia",
      "regionId": 22,
      "platform": "Azure",
      "systemService": "AzurePortal"
    }
  ],
  "lookup_method": "public_ip_ranges",
  "elapsed_ms": 0.12
}
```

#### Looking up AWS IP Address

Looking up an AWS IP address: [https://api.incolumitas.com/datacenter?ip=3.5.140.2](https://api.incolumitas.com/datacenter?ip=3.5.140.2)

```json
{
  "ip": "3.5.140.2",
  "is_datacenter": true,
  "cidr": "3.5.140.0/22",
  "region": "ap-northeast-2",
  "service": "AMAZON",
  "network_border_group": "ap-northeast-2",
  "other_matches": [
    {
      "cidr": "3.5.140.0/22",
      "region": "ap-northeast-2",
      "service": "S3",
      "network_border_group": "ap-northeast-2"
    },
    {
      "cidr": "3.5.140.0/22",
      "region": "ap-northeast-2",
      "service": "EC2",
      "network_border_group": "ap-northeast-2"
    }
  ],
  "lookup_method": "public_ip_ranges",
  "elapsed_ms": 0.09
}
```

#### Looking up GCP IP Address

Looking up an GCP IP address: [https://api.incolumitas.com/datacenter?ip=23.236.48.55](https://api.incolumitas.com/datacenter?ip=23.236.48.55)

```json
{
  "ip": "23.236.48.55",
  "is_datacenter": true,
  "cidr": "23.236.48.0/20",
  "service": "GCP",
  "lookup_method": "public_ip_ranges",
  "elapsed_ms": 0.11
}
```

#### Looking up AWS IPv6 Address

And looking up a AWS IPv6 address: [https://api.incolumitas.com/datacenter?ip=2600:1F18:7FFF:F800:0000:ffff:0000:0000](https://api.incolumitas.com/datacenter?ip=2600:1F18:7FFF:F800:0000:ffff:0000:0000):

```json
{
  "ip": "2600:1F18:7FFF:F800:0000:ffff:0000:0000",
  "is_datacenter": true,
  "cidr": "2600:1f18:7fff:f800::/56",
  "region": "us-east-1",
  "service": "ROUTE53_HEALTHCHECKS",
  "network_border_group": "us-east-1",
  "lookup_method": "public_ip_ranges",
  "elapsed_ms": 0.21
}
```

As you can see from the example lookups above, the API gives additional meta data information for a specific IP address such as regional and data center information.

## What cloud providers are supported by the API?

Currently, the API supports IP address ranges from the following [cloud providers](https://udger.com/resources/datacenter-list):

| Cloud Provider                     | Number of IP Addresses | API support |
|------------------------------------|------------------------|-------------|
| Amazon AWS                         | 124,353,848            | ✓           |
| Microsoft Azure                    | 12,175,189             | ✓           |
| Google Cloud                       | 13,257,728             | ✓           |
| Alibaba Cloud                      | 7,303,168              | ✗           |
| SoftLayer Technologies / IBM Cloud | 4,841,056              | ✓           |
| Tencent Cloud                      | 4,704,256              | ✗           |
| OVH                                | 4,200,608              | ✓           |
| Digital Ocean, Inc                 | 2,643,216              | ✓           |
| Rackspace, Inc.                    | 2,178,902              | ✗           |
| Hetzner Online                     | 2,022,193              | ✓           |
| CloudFlare Inc                     | 1,801,984              | ✓           |
| Aptum Technologies                 | 1,786,472              | ✗           |
| Ubiquity Hosting                   | 1,443,840              | ✗           |
| Oracle Cloud                       | 1,183,744              | ✓           |
| Tor Network                        | ?                      | ✓           |

The API database is updated every 4 hours with the official source of the IP address ranges of the cloud provides listed above (with a ✓). For some cloud providers such as OVH or Hetzner there is no official IP address range source, so I have to rely on [third party sources](https://bgp.he.net/search?search%5Bsearch%5D=OVH&commit=Search).

### Sources for Datacenter IP Address Ranges

Where do I get the [CIDR](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) address ranges for the datacenters? 

Most datacenters publish their own IP ranges, such as AWS or Google Cloud. But often, those IP address ranges are not complete. For that reason, other means of lookup have to be used, such as [whois lookups](https://en.wikipedia.org/wiki/WHOIS) or searching through [ASN](https://en.wikipedia.org/wiki/Autonomous_system_(Internet)) databases.

This API follows the following lookup logic:

1. First, check if the IP is to be found in the published IP ranges from the providers.
2. If the first step farils, a lookup of the IP address with `whois 105.226.177.72 | grep -E -i "(OrgName:|address:|OrgTechName:|descr:)"` is conducted. If the orgname belongs to a datacenter, we have a match. Simple string matching.
3. If the above whois lookup did not produce a datacenter match, we lookup the autonomous system `OriginAS: AS21928` and we perform a simple grep `cat ripe-asn.txt | grep -E -i "^13335\s"` in the ASN lists to check if the ASN belongs to a large cloud provider.

Other techniques are pursuited, if the above algorithm doesn't yield a match.

