Title: API to Check if an IP Address belongs to a Datacenter / Cloud Provider
Status: published
Date: 2021-06-20 17:45
Category: Security
Tags: API, IP-Address, Datacenter, Cloud
Slug: check-if-IP-belongs-to-datacenter
Author: Nikolai Tschacher
Summary: For security reasons, it's often helpful to check if an IP Address belongs to a datacenter or cloud computing provider such as Amazon AWS or Microsoft Azure. Therefore, I have developed a simple API that helps you to check if an IP address belongs to a datacenter / cloud provider.

## Introduction

The emergence of cloud providers enabled bot programmers and spammers to make use of cheap and scalable cloud computing infrastructure. As a business and website owner, it's in your best interest that your visitors are organic human beings and not automated programs that leverage the functionality of your website.

Consider the scenario where you own a Ecommerce business and you want to sell a limited edition of your product and you know in advance that the demand for the product will far outnumber the supply (As it happened on the [Playstation 5 release](https://www.businessinsider.com/playstation-5-launch-day-us-europe-flooded-by-reseller-bots-2020-11)).

Those bots are called **Resell bots** and they are able to buy your limited edition product as soon as it appears on the page in order to resell it later on Ebay for a higher price.

Often those bots are hosted on Amazon AWS, Digitalocean or Hetzner cloud computing infrastructure (To name a few hosting providers).

When you can infer that the IP address of a visitor on your website belongs to a datacenter / cloud provider you can decide to block this IP. Put differently: What normal human being is using a cloud provider IP address when browsing the Internet?

## API for IP Address Datacenter / Cloud Provider Check

Now it's time to introduce the API that allows you to check if a certain IP belongs to a datacenter / cloud provider.

API Endpoint: **https://abs.incolumitas.com/datacenter?ip=**

Example: [https://abs.incolumitas.com/datacenter?ip=3.5.140.2](https://abs.incolumitas.com/datacenter?ip=3.5.140.2)

Result: 

```json
{
  "ip": "3.5.140.2",
  "region": "ap-northeast-2",
  "service": "AMAZON",
  "network_border_group": "ap-northeast-2"
}
```

If you don't specify any IP address with the `ip=` query parameter and you invoke **https://abs.incolumitas.com/datacenter** directly, the client's own IP address will be checked. In my case, I get the following output:

```json
{
  "ip": "84.155.231.57",
  "service": "No match for this IP address"
}
```

because my private ISP IP Address obviously doesn't belong to a datacenter.

Usage with JavaScript:

```JavaScript
fetch('https://abs.incolumitas.com/datacenter') 
.then(response => response.json())
.then(function(data) {
  console.log(data)
})
```

## What datacenters / cloud providers are supported?

Currently, the API supports the following cloud providers:

| Cloud Provider                     | Number of IP Addresses | API support |
|------------------------------------|------------------------|-------------|
| Amazon AWS                         | 124,353,848            | ✓           |
| Microsoft Azure                    | 12,175,189             | ✓           |
| Google Cloud                       | 13,257,728             | ✓           |
| Alibaba Cloud                      | 7,303,168              | ❌           |
| Tencent Cloud                      | 4,704,256              | ❌           |
| SoftLayer Technologies / IBM Cloud | 4,841,056              | ✓           |
| OVH                                | 4,200,608              | ✓           |
| Digital Ocean, Inc                 | 2,643,216              | ✓           |
| Hetzner Online                     | 2,022,193              | ✓           |
| Oracle Cloud                       | 1,183,744              | ✓           |
| TOR                                | ?                      | ✓           |

The API database is updated every 4 hours with the published IP address ranges of the cloud provides. For some cloud providers such as OVH or Hetzner there is no official source, so I have to rely on [third party sources](https://bgp.he.net/search?search%5Bsearch%5D=OVH&commit=Search).
