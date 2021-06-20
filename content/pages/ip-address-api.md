Title: Datacenter IP Address API
Date: 2021-06-20 00:13
Author: Nikolai Tschacher
Slug: IP-API
Status: published

I maintain a public API to lookup whether an IP address belongs to a data center IP address range such as from Azure, AWS, Digitalocean and many more cloud providers. Please read the [full blog article]({filename}/Security/datacenter-ip-api.md) for more details.

| API Version | API Endpoint                               | Supported Datacenters                                                                                                            |
|-------------|--------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| v0.1        | [https://abs.incolumitas.com/datacenter?ip=](https://abs.incolumitas.com/datacenter?ip=) | Amazon AWS, Microsoft Azure, Google Cloud, IBM Cloud, OVH, Digital Ocean, Hetzner Online, CloudFlare, Oracle Cloud, Tor Network  |

## API Usage

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

As you can see from the example lookups above, sometimes the API gives additional meta data information for a specific IP address such as regional and data center information.