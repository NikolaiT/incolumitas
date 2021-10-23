Title: Datacenter IP Address API
Date: 2021-09-29 00:13
Author: Nikolai Tschacher
Slug: Datacenter-IP-API
Status: published

I maintain a public API to check whether an IP address belongs to a data center IP address range such as Azure, AWS, Digitalocean, Google Cloud Platform and many other cloud providers. Please read the [full blog article]({filename}/Security/datacenter-ip-api.md) for more a through introduction.

+ API Version: v0.2 (29th September 2021)
+ API Endpoint: **https://api.incolumitas.com/datacenter?ip=3.5.140.2**
+ Supported Datacenters: Amazon AWS, Microsoft Azure, Google Cloud, IBM Cloud, OVH, Digital Ocean, Hetzner Online, CloudFlare, Oracle Cloud, Tor Network
+ IPv6 Support: Yes


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

## ChangeLog

+ Add cloud provider `m247 Ltd`, `servers.com Inc.`, `Leaseweb Usa Inc.`, often used for proxies/fraud

#### 29th September 2021

+ Updated all IP address ranges
+ Added dedicated API endpoint: https://api.incolumitas.com/datacenter?ip=3.5.140.2
+ Old API Endpoint: https://abs.incolumitas.com/datacenter?ip=1.2.3.4


## API Usage

You can reach the API endpoint with this URL: **https://api.incolumitas.com/datacenter?ip=**

If you pass the IP address `3.5.140.2` to the API by calling [https://api.incolumitas.com/datacenter?ip=3.5.140.2](https://api.incolumitas.com/datacenter?ip=3.5.140.2), you'll obtain the result:

```json
{
  "ip": "3.5.140.2",
  "region": "ap-northeast-2",
  "service": "AMAZON",
  "network_border_group": "ap-northeast-2"
}
```

Alternatively, you can also lookup IPv6 addresses. Try the url [https://api.incolumitas.com/datacenter?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef](https://api.incolumitas.com/datacenter?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef), which yields:

```json
{
  "ip": "2406:dafe:e0ff:ffff:ffff:ffff:dead:beef",
  "region": "ap-east-1",
  "service": "AMAZON",
  "network_border_group": "ap-east-1"
}
```

If you don't specify any IP address with the `ip=` query parameter and you invoke [https://api.incolumitas.com/datacenter](https://api.incolumitas.com/datacenter) directly, the client's own IP address will be used for lookup. In my case, I get the following output:

```json
{
  "ip": "84.155.231.57",
  "service": "No match for this IP address"
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

#### More Examples for the IP Address Datacenter API

In the following section, I will show examples for looking up IP addresses belonging to the three biggest cloud providers AWS, Azure and GCP:

Looking up an Azure IP address: [https://api.incolumitas.com/datacenter?ip=20.41.193.225](https://api.incolumitas.com/datacenter?ip=20.41.193.225)

```json
{
  "ip": "20.41.193.225",
  "name": "AzurePortal",
  "region": "",
  "regionId": 0,
  "platform": "Azure",
  "systemService": "AzurePortal"
}
```

Looking up an AWS IP address: [https://api.incolumitas.com/datacenter?ip=3.5.140.2](https://api.incolumitas.com/datacenter?ip=3.5.140.2)

```json
{
  "ip": "3.5.140.2",
  "region": "ap-northeast-2",
  "service": "AMAZON",
  "network_border_group": "ap-northeast-2"
}
```

Looking up an GCP IP address: [https://api.incolumitas.com/datacenter?ip=23.236.48.55](https://api.incolumitas.com/datacenter?ip=23.236.48.55)

```json
{
  "ip": "23.236.48.55",
  "service": "GCP"
}
```

And looking up a AWS IPv6 address: [https://api.incolumitas.com/datacenter?ip=2600:1F18:7FFF:F800:0000:ffff:0000:0000](https://api.incolumitas.com/datacenter?ip=2600:1F18:7FFF:F800:0000:ffff:0000:0000):

```json
{
  "ip": "2600:1F18:7FFF:F800:0000:ffff:0000:0000",
  "region": "us-east-1",
  "service": "AMAZON",
  "network_border_group": "us-east-1"
}
```

As you can see from the example lookups above, sometimes the API gives additional meta data information for a specific IP address such as regional and data center information.

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