Title: Datacenter IP Address API
Date: 2021-06-20 00:13
Author: Nikolai Tschacher
Slug: Datacenter-IP-API
Status: published

I maintain a public API to check whether an IP address belongs to a data center IP address range such as from Azure, AWS, Digitalocean and many other cloud providers. Please read the [full blog article]({filename}/Security/datacenter-ip-api.md) for more a through introduction.

+ API Version: v0.1
+ API Endpoint: **https://abs.incolumitas.com/datacenter?ip=1.2.3.4**
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
  fetch('https://abs.incolumitas.com/datacenter?ip=' + ip) 
  .then(response => response.json())
  .then(function(data) {
    document.getElementById('data').innerText = JSON.stringify(data, null, 2);
  })
})
</script>

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