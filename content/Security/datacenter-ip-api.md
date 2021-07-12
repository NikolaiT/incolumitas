Title: API to Check if an IP Address belongs to a Datacenter / Cloud Provider
Status: published
Date: 2021-06-20 17:45
Category: Security
Tags: API, IP-Address-Check, Datacenter, Cloud-Provider
Slug: check-if-an-IP-Address-belongs-to-a-datacenter
Author: Nikolai Tschacher
Summary: For security reasons, it's often helpful to check if an IP Address belongs to a datacenter or cloud computing provider such as Amazon AWS or Microsoft Azure. Therefore, I have developed a simple public API that helps you to check if an IP address belongs to a datacenter / cloud provider.

<a class="orange_button" href="https://incolumitas.com/pages/Datacenter-IP-API/">Visit the dedicated page for the API</a>

## Introduction

The emergence of cloud providers enabled bot programmers and spammers to make use of cheap and scalable cloud computing infrastructure for their bots. As a business and website owner, it's in your best interest that your visitors are organic human beings and not automated programs that leverage the functionality of your website.

Consider the scenario where you own a ecommerce business and you want to sell a limited edition of your product and you know in advance that the demand for the product will far outnumber the supply (As it happened with the [Playstation 5 release](https://www.businessinsider.com/playstation-5-launch-day-us-europe-flooded-by-reseller-bots-2020-11)).

Those bots are called **resell bots** and they buy your limited edition product as soon as it appears on the page in order to resell it later on Ebay for a higher price.

But there are much more use cases for malicious bots: Adfraud, scraping bots, price/stock monitoring bots, credential stuffing bots and many other use cases.

Often those bots are hosted on Amazon AWS, Digitalocean or Hetzner cloud computing infrastructure (To name a few hosting providers).

When you can infer that the IP address of a visitor on your website belongs to a datacenter / cloud provider you can decide to block this IP.

**Put differently:** What normal human being is using a cloud provider IP address when browsing the Internet?

## API for IP Address Datacenter / Cloud Provider Check

Now it's time to introduce the API that allows you to check if a certain IP belongs to a datacenter / cloud provider.

You can reach the API endpoint with this URL: **https://abs.incolumitas.com/datacenter?ip=**

If you pass the IP address `3.5.140.2` to the API by calling [https://abs.incolumitas.com/datacenter?ip=3.5.140.2](https://abs.incolumitas.com/datacenter?ip=3.5.140.2), you'll obtain the result:

```json
{
  "ip": "3.5.140.2",
  "region": "ap-northeast-2",
  "service": "AMAZON",
  "network_border_group": "ap-northeast-2"
}
```

Alternatively, you can also lookup IPv6 addresses. Try the url [https://abs.incolumitas.com/datacenter?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef](https://abs.incolumitas.com/datacenter?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef), which yields:

```json
{
  "ip": "2406:dafe:e0ff:ffff:ffff:ffff:dead:beef",
  "region": "ap-east-1",
  "service": "AMAZON",
  "network_border_group": "ap-east-1"
}
```

If you don't specify any IP address with the `ip=` query parameter and you invoke [https://abs.incolumitas.com/datacenter](https://abs.incolumitas.com/datacenter) directly, the client's own IP address will be used for lookup. In my case, I get the following output:

```json
{
  "ip": "84.155.231.57",
  "service": "No match for this IP address"
}
```

because my private ISP IP address obviously doesn't belong to a datacenter.

Usage with JavaScript:

```JavaScript
fetch('https://abs.incolumitas.com/datacenter') 
.then(response => response.json())
.then(function(data) {
  console.log(data)
})
```

The IP address ranges for the cloud providers are kept up to date and the IP ranges are pulled from the upstream sources every 4 hours.

#### More Examples for the IP Address Datacenter API

In the following section, I will show examples for looking up IP addresses belonging to the three biggest cloud providers AWS, Azure and GCP:

Looking up an Azure IP address: [https://abs.incolumitas.com/datacenter?ip=20.41.193.225](https://abs.incolumitas.com/datacenter?ip=20.41.193.225)

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

Looking up an AWS IP address: [https://abs.incolumitas.com/datacenter?ip=3.5.140.2](https://abs.incolumitas.com/datacenter?ip=3.5.140.2)

```json
{
  "ip": "3.5.140.2",
  "region": "ap-northeast-2",
  "service": "AMAZON",
  "network_border_group": "ap-northeast-2"
}
```

Looking up an GCP IP address: [https://abs.incolumitas.com/datacenter?ip=23.236.48.55](https://abs.incolumitas.com/datacenter?ip=23.236.48.55)

```json
{
  "ip": "23.236.48.55",
  "service": "GCP"
}
```

And looking up a AWS IPv6 address: [https://abs.incolumitas.com/datacenter?ip=2600:1F18:7FFF:F800:0000:ffff:0000:0000](https://abs.incolumitas.com/datacenter?ip=2600:1F18:7FFF:F800:0000:ffff:0000:0000):

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
