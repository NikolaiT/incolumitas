Title: FireHOL API
Date: 2021-10-25 00:13
Author: Nikolai Tschacher
Slug: FireHOL-API
Status: published
Sortorder: 6

According to Wikipedia, [FireHOL](https://en.wikipedia.org/wiki/FireHOL) is a

> FireHOL is a shell script designed as a wrapper for iptables written to ease the customization of the Linux kernel's firewall netfilter.

I maintain a public API to check whether an IP address is flagged on the huge [FireHOL IP blacklists](https://github.com/firehol/blocklist-ipsets) repository. I was missing a public API, so I decided to make one. Please use the API responsible!

+ API Version: v0.1 (25th October 2021)
+ API Endpoint: **https://api.incolumitas.com/firehol?ip=3.5.140.2**
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
  fetch('https://api.incolumitas.com/firehol?ip=' + ip) 
  .then(response => response.json())
  .then(function(data) {
    document.getElementById('data').innerText = JSON.stringify(data, null, 2);
  })
})
</script>

## ChangeLog

#### 25th October 2021

+ Released initial version 0.1


## API Usage

You can reach the API endpoint with this URL: [**https://api.incolumitas.com/firehol?ip=3.5.140.2**](https://api.incolumitas.com/firehol?ip=3.5.140.2)

If you pass the IP address `3.5.140.2` to the API by calling [https://api.incolumitas.com/firehol?ip=3.5.140.2](https://api.incolumitas.com/firehol?ip=3.5.140.2), you'll obtain the result:

```json
{
  "firehol_webclient": "3.5.140.2 is NOT in set firehol_webclient.",
  "firehol_proxies": "3.5.140.2 is NOT in set firehol_proxies.",
  "firehol_level4": "3.5.140.2 is NOT in set firehol_level4.",
  "firehol_level3": "3.5.140.2 is NOT in set firehol_level3.",
  "firehol_level2": "3.5.140.2 is NOT in set firehol_level2.",
  "firehol_level1": "3.5.140.2 is NOT in set firehol_level1.",
  "firehol_anonymous": "3.5.140.2 is NOT in set firehol_anonymous.",
  "firehol_abusers_30d": "3.5.140.2 is NOT in set firehol_abusers_30d.",
  "firehol_abusers_1d": "3.5.140.2 is NOT in set firehol_abusers_1d.",
  "firehol_webserver": "3.5.140.2 is NOT in set firehol_webserver."
}
```

Alternatively, you can also lookup IPv6 addresses. Try the url [https://api.incolumitas.com/firehol?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef](https://api.incolumitas.com/firehol?ip=2406:dafe:e0ff:ffff:ffff:ffff:dead:beef), which yields:

```json
{}
```

If you don't specify any IP address with the `ip=` query parameter and you invoke [https://api.incolumitas.com/firehol](https://api.incolumitas.com/firehol) directly, the client's own IP address will be used for lookup. In my case, I get the following output:

```json
{
  "firehol_webserver": "60.137.20.231 is NOT in set firehol_webserver.",
  "firehol_webclient": "60.137.20.231 is NOT in set firehol_webclient.",
  "firehol_proxies": "60.137.20.231 is NOT in set firehol_proxies.",
  "firehol_level4": "60.137.20.231 is NOT in set firehol_level4.",
  "firehol_level3": "60.137.20.231 is NOT in set firehol_level3.",
  "firehol_level2": "60.137.20.231 is NOT in set firehol_level2.",
  "firehol_level1": "60.137.20.231 is NOT in set firehol_level1.",
  "firehol_anonymous": "60.137.20.231 is NOT in set firehol_anonymous.",
  "firehol_abusers_30d": "60.137.20.231 is NOT in set firehol_abusers_30d.",
  "firehol_abusers_1d": "60.137.20.231 is NOT in set firehol_abusers_1d."
}
```

because my private ISP IP address obviously is not blacklisted by fireHOL.

Usage with JavaScript:

```JavaScript
fetch('https://api.incolumitas.com/firehol') 
.then(response => response.json())
.then(function(data) {
  console.log(data)
})
```

The IP address ranges for the cloud providers are kept up to date and the IP ranges are pulled from the upstream sources every 4 hours.


#### More Examples for the fireHOL API

In the following section, I will show examples for looking up flagged IP addresses.

Looking up **TOR exit node** addresses which [you can obtain from here](https://check.torproject.org/exit-addresses). Example TOR IP address: [https://api.incolumitas.com/firehol?ip=109.70.100.28](https://api.incolumitas.com/firehol?ip=109.70.100.28)

```json
{
  "firehol_proxies": "109.70.100.28 is in set firehol_proxies.",
  "firehol_level4": "109.70.100.28 is in set firehol_level4.",
  "firehol_level3": "109.70.100.28 is in set firehol_level3.",
  "firehol_level2": "109.70.100.28 is NOT in set firehol_level2.",
  "firehol_level1": "109.70.100.28 is NOT in set firehol_level1.",
  "firehol_anonymous": "109.70.100.28 is in set firehol_anonymous.",
  "firehol_abusers_30d": "109.70.100.28 is in set firehol_abusers_30d.",
  "firehol_abusers_1d": "109.70.100.28 is in set firehol_abusers_1d.",
  "firehol_webserver": "109.70.100.28 is in set firehol_webserver.",
  "firehol_webclient": "109.70.100.28 is in set firehol_webclient."
}
```

Another example for a malicious IP address comes from the [feodotracker abuse.ch tracker](https://feodotracker.abuse.ch/blocklist/), more specifically from the [feodotracker.rules](https://feodotracker.abuse.ch/downloads/feodotracker.rules). The API call is: [https://api.incolumitas.com/firehol?ip=52.73.70.149](https://api.incolumitas.com/firehol?ip=52.73.70.149)

```json
{
  "firehol_webclient": "52.73.70.149 is NOT in set firehol_webclient.",
  "firehol_proxies": "52.73.70.149 is NOT in set firehol_proxies.",
  "firehol_level4": "52.73.70.149 is NOT in set firehol_level4.",
  "firehol_level3": "52.73.70.149 is NOT in set firehol_level3.",
  "firehol_level2": "52.73.70.149 is NOT in set firehol_level2.",
  "firehol_level1": "52.73.70.149 is NOT in set firehol_level1.",
  "firehol_anonymous": "52.73.70.149 is NOT in set firehol_anonymous.",
  "firehol_abusers_30d": "52.73.70.149 is NOT in set firehol_abusers_30d.",
  "firehol_abusers_1d": "52.73.70.149 is NOT in set firehol_abusers_1d.",
  "firehol_webserver": "52.73.70.149 is in set firehol_webserver."
}
```

## What ipsets are supported by the API?

Currently, the API supports ipsets from the following [repository](https://github.com/firehol/blocklist-ipsets):

| ipset               | description                                                                                                                                                                                  |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| firehol_abusers_1d  | An ipset made from blocklists that track abusers in the last 24 hours.                                                                                                                       |
| firehol_abusers_30d | An ipset made from blocklists that track abusers in the last 30 days.                                                                                                                        |
| firehol_anonymous   | A firewall blacklist composed from IP lists, providing maximum protection with minimum false positives. Suitable for basic protection on all internet facing servers, routers and firewalls. |
| firehol_level1      | A firewall blacklist composed from IP lists, providing maximum protection with minimum false positives. Suitable for basic protection on all internet facing servers, routers and firewalls. |
| firehol_level2      | An ipset made from blocklists that track attacks, during about the last 48 hours.                                                                                                            |
| firehol_level3      | An ipset made from blocklists that track attacks, spyware, viruses. It includes IPs than have been reported or detected in the last 30 days.                                                 |
| firehol_level4      | An ipset made from blocklists that track attacks, but may include a large number of false positives.                                                                                         |
| firehol_webclient   | An IP blacklist made from blocklists that track IPs that a web client should never talk to. This list is to be used on top of firehol_level1.                                                |
| firehol_webserver   | A web server IP blacklist made from blocklists that track IPs that should never be used by your web users.                                                                                   |

The API database is updated every day with the updated ipsets from the repository [repository](https://github.com/firehol/blocklist-ipsets).