Title: How to find the ASN for any IP Address?
Date: 2022-07-31 20:34
Category: Programming
Tags: autonomous system, ASN, API, Security
Slug: Find-the-ASN-for-any-IP-Address
Summary: In the Internet, each IP Address belongs to an autonomous system (AS). In this blog article, it is demonstrated how any IP address can be mapped to an AS number. The necessary information and sources to map each IP Address to an Autnomous System is provided as well, since they were not easy to find.
Author: Nikolai Tschacher
Status: Published

## ASN Lookup Demo

<div class="ipAPIDemo">
  <label style="font-weight: 600; font-size: 15px" for="ip">Enter IP address to find its ASN</label>
  <input style="padding: 6px;" type="text" id="ip" name="ip" value="13.34.52.117">
  <input class="orange_button" type="submit" value="Lookup ASN">

  <div>
    <p><strong>Lookup Examples:</strong>
      <a class="api-example" data-query="AS209103" href="#">AS209103</a> —
      <a class="api-example" data-query="AS7359" href="#">AS7359</a> —
      <a class="api-example" data-query="AS10846" href="#">AS10846</a>
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
    if (data) {
      try {
        delete data.is_datacenter;
        delete data.datacenter;
      } catch (err) {}
    }
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

<a 
  class="orange_button" 
  href="https://incolumitas.com/pages/Datacenter-IP-API/">
ASN API Page
</a>

## Introduction

The Internet consists of many independent systems which are called **Autonomous Systems (AS)**. Those autonomous systems are assigned a number, the **ASN**. An autonomous system belongs to a single administrative organisation that defines a coherent routing policy to the rest of the Internet (And especially to the neighboring autonomous systems). The [Border Gateway Protocol (BGP)](https://en.wikipedia.org/wiki/Border_Gateway_Protocol) implements AS routing policies.

You can think of autonomous systems as a subset of the Internet that follows a common routing policy and that is controlled by one administrative entity (Such as a large ISP or a public organization such as an University). Each IPv4 and IPv6 address belongs to exactly one autonomous system. Furthermore, each autonomous system can have multiple IPv4 and IPv6 address ranges assigned to it.

AS numbers are either 16-bit integers or 32-bit integers. So for example, `AS34953` is an autonomous system number that belongs to the organization `RELAIX RelAix Networks GmbH` (Which is actually the organsiation responsible for providing Internet to the train from which I am writing this blog article):

```JavaScript
{
  asn: 34953,
  cidr: '46.183.96.0/21',
  descr: 'RELAIX RelAix Networks GmbH, DE',
  country: 'DE'
}
```

Now the questions begs to be answered what IP ranges are *owned* by this autonomous system (AS)? Of course, it is possible to obtain this information (I will soon reveal how). For now, let's see what IP ranges belong to the organization `RELAIX RelAix Networks GmbH`:

```JavaScript
{
  "asn": 34953,
  "descr": "RELAIX RelAix Networks GmbH, DE",
  "country": "de",
  "prefixes": [
    "5.145.128.0/20",
    "5.199.240.0/20",
    "45.146.172.0/22",
    "46.183.96.0/21",
    "88.218.160.0/22",
    "93.159.248.0/21",
    "129.192.10.0/24",
    "129.192.11.0/24",
    "161.51.255.0/24",
    "185.164.96.0/22",
    "185.217.62.0/24",
    "185.221.208.0/22",
    "185.243.232.0/23",
    "193.22.100.0/23",
    "193.28.5.0/24",
    "193.32.64.0/24",
    "195.242.220.0/24"
  ],
  "prefixesIPv6": [
    "2001:678:184::/48",
    "2001:67c:13b0::/48",
    "2001:67c:2054::/48",
    "2a00:fe0::/32",
    "2a0c:3000::/32",
    "2a0d:ae80::/32",
    "2a10:d900::/32"
  ],
  "active": true,
  "elapsed_ms": 0.06
}
```

As you can see, the autonomous system `AS34953` has IP ranges from totally different IPv4 `/8` address blocks. This might seem counterintuitive, but due to the rarity of IPv4 addresses, it is not uncommon to have different `/8` IPv4 ranges in a single AS.

<figure>
    <img src="{static}/images/ASN-Connections-In-RIPE-NCC.jpg" alt="ASN-Connections-In-RIPE-NCC" />
    <figcaption>Visualizations of ASN Connections in RIPE NCC
    <span style="font-size: 70%">(Source: <a href="https://thyme.apnic.net/BGP/RIPE/#">https://thyme.apnic.net/BGP/RIPE/#</a>)</span>
    </figcaption>
</figure>

**Why are autonomous systems relevant in IT security?**

In defensive IT Security, you often want to block offending IP addresses in order to stop spammers and ongoing attacks from hackers or botnets. Advanced or institutional attackers often own large blocks of IP addresses, therefore blocking single IP addresses is often not going to cut it. This problem becomes especially apparent with the gradual adoption of IPv6, where you can practically obtain huge ranges of IPv6 addresses without much effort.

By obtaining the ASN for each of the attacking IP addresses, it can potentially be learned that the attacker is launching her attack from only few distinct autonomous systems. Then as a first and drastic measure, an entire or multiple ASN's can be blocked in order to quickly chocke an ongoing attack.

Furthermore, an autonomous system can often be mapped to a country, which gives geographical location information for an IP address, which may further help to contextualize an ongoing attack.

Furthermore, by knowing the AS organization of an IP address, it is also possible to draw futher conclucsions: Is the organization an large and established ISP? Is it a company with a good reputation? Or is it a unknown business with a reputation for a leniant policy regarding spammers?

## How can IP addresses be mapped to Autonmous System Numbers (ASN)?

The management & coordination of administrative tasks of the whole Internet is divided among different Regional Internet Registries (RIR) such as 

1. ARIN
2. APNIC
3. RIPE NCC
4. AFRINIC
5. LACNIC

[APNIC](https://www.apnic.net/) is the Regional Internet Registry responsible for the Asia-Pacific region. Luckily for us, APNIC makes BGP routing data publicly available. The data is originating from Internet Exchange points such as from [DIX-IE (formerly NSPIXP2) in Tokyo, Japan](https://thyme.apnic.net/current/) or [Bhutan Telecom's router located at the LINX in London](https://thyme.apnic.net/london/)).

The APNIC hosted page [https://thyme.apnic.net/](https://thyme.apnic.net/) has an overview of all publicly available BGP routing table data that APNIC hosts, from which we can also download the required information to map AS numbers to IP addresses.

For the task to map any IPv4 and IPv6 address to an ASN, we need the following three files:

1. [IPv4 prefixes and their origin ASNs](https://thyme.apnic.net/current/data-raw-table) - This file includes the mapping of all IPv4 Addresses to ASNs 
2. [IPv6 prefixes and their origin ASNs](https://thyme.apnic.net/current/ipv6-raw-table) - This file includes the mapping of all IPv6 Addresses to ASNs
3. [ASN to name mapping for ASNs visible on the Internet today](https://thyme.apnic.net/current/data-used-autnums) - This file maps the ASN to it's stringified version, which basically is the humanly readable version of the ASN (descriptive name, usually includes information about the responsible organization).

After downloading those three files (Downloading the data once a day is more than enough!), all the information necessary to map any IP address to an ASN is obtained. You can write your own ASN lookup tool that finds the ASN for an IP address.

Of course it's also possible do the inverse and to find all the IPv4 / IPv6 prefixes for a given ASN.


## Conclusion

It was shown how ASN information can be obtained for any IP address and it was also explained why AS data adds usual information in many different IT Security use cases. Furthermore, a regularely updated website with the current mapping from IP addresses to ASNs was provided: [https://thyme.apnic.net/current/](https://thyme.apnic.net/current/).

A question to my readers: However, in case this website ceases to publish up-to-date ASN to IP mappings, where else could this information be obtained? Do other large Regional Internet Registries such as [ARIN](https://www.arin.net/) or [RIPE NCC](https://www.ripe.net/) provide equivalent information?

[Link to the ASN API Page]({filename}/pages/ip-address-api.md)








