Title: TLS Fingerprint API
Date: 2022-02-17 20:30
Modified: 2022-08-04 14:00
Author: Nikolai Tschacher
Slug: TLS-Fingerprint
Status: published
Sortorder: 8

| <!-- -->         | <!-- -->                                      |
|------------------|-----------------------------------------------|
| **Author**       | Nikolai Tschacher                             |
| **API Version**  | v0.3                                          |
| **Version Date** | 6th June 2022                            |
| **API Access**   | Free                                          |
| **Download**     | Closed Source (Upon request only)             |


## TLS Fingerprint API Demo

**API Endpoint:** [https://tls.incolumitas.com/fps](https://tls.incolumitas.com/fps)

This is your last seen TLS fingerprint - Taken from the initial TLS Client Hello handshake message:

<pre id="wrapper">
  <code id="tls_fp" class="JSON hljs">...loading (JavaScript required)</code>
</pre>

<script>
var el = document.getElementById('tls_fp');
hljs.highlightBlock(el);

fetch('https://tls.incolumitas.com/fps')
  .then(response => response.json())
  .then(function(data) {
    document.getElementById('tls_fp').innerHTML = JSON.stringify(data, null, 2);
    hljs.highlightBlock(el);
  })
</script>

Your User-Agent (`navigator.userAgent`) says that you are 

<pre style="overflow: auto;" id="userAgent">
</pre>

<script>
document.getElementById('userAgent').innerText = navigator.userAgent;
</script>


## TLS Fingerprint API

The TLS fingerprinting API allows you to get your [TLS fingerprint](https://tls.incolumitas.com/fps). It can be used for various purposes such as:

1. Networking traffic analyisis 
2. Malware detection
3. Bot detection

## Endpoint `/fps`

The `/fps` endpoint returns the most recent TLS fingerprint from the requesting client. Internally, the client's public IP address is used to lookup matching TLS fingerprints. Since clients generate many TLS sessions over time, only the most recent TLS fingerprint is returned by default.

| Endpoint         | Description                                      |
|------------------|-----------------------------------------------|
|  <a href="https://tls.incolumitas.com/fps">tls.incolumitas.com/fps</a>          | This endpoint returns the most recent TLS fingerprint for the requesting client. | 
| <a href="https://tls.incolumitas.com/fps?detail=1">tls.incolumitas.com/fps?detail=1</a> | Request a detailed/verbose version of the TLS fingerprint for the current connection.                                                                                                                                                                                   |
| <a href="https://tls.incolumitas.com/fps?all=1"> tls.incolumitas.com/fps?all=1 </a>    | Request all TLS fingerprints for this client that exist in server memory (The server is restarted periodically).   All the fingerprints that match the client's IP address will be returned.                                                                            |


#### Example for endpoint `/fps`

Example by using `curl`:

```bash
curl 'https://tls.incolumitas.com/fps'
```

returns the following JSON response from the API:

```json
{
  "num_fingerprints": 55,
  "sha3_384": "5cfe8ec2fdc3fc735e78aedd401c4e45a3ea465b4e851d4c964969c2ed953664f227114ae4c48103a41093548b2a0891",
  "tls_fp": {
    "ciphers": "4867,4866,4865,52393,52392,52394,49200,49196,49192,49188,49172,49162,159,107,57,65413,196,136,157,61,53,192,132,49199,49195,49191,49187,49171,49161,158,103,51,190,69,156,60,47,186,65,49169,49159,5,4,49170,49160,22,10,255",
    "client_hello_version": "TLS 1.2",
    "ec_point_formats": "0",
    "extensions": "43,51,0,11,10,13,16",
    "record_version": "TLS 1.0",
    "signature_algorithms": "2054,1537,1539,2053,1281,1283,2052,1025,1027,513,515",
    "supported_groups": "29,23,24,25"
  },
  "user-agent": "curl/7.79.1",
  "utc_now": "2022-06-06 11:23:03.245922"
}
```


## Endpoint `/stats`

The `/stats` endpoint returns statistics over all stored TLS connections on the server side. Due to performance reasons, only the most recent 50MB of TLS data are considered in `/stats` lookups. Thus, the database is of reduced accuracy and statistical significance.

| Endpoint         | Description                                      |
|------------------|-----------------------------------------------|
| <a href="https://tls.incolumitas.com/stats">tls.incolumitas.com/stats</a>        | Lists all TLS statistics.                                                                                                                                                                                                                                               |
| <a href="https://tls.incolumitas.com/stats?bo=1">tls.incolumitas.com/stats?bo=1</a>   | Get statistics only for TLS fingerprints with associated User-Agents                                                                                                                                                                                                    |


# Introduction

On this page, a server-side tool is presented, which extracts entropy from the TLS handshake in order to form a TLS fingerprint.

Such a TLS fingerprint may be used to identify devices / TLS protocol implementations. It is able to collect statistical data and correlate the TLS entropy with the `User-Agent` transmitted in HTTP headers. After this data collection process, questions such as:

1. Does the TLS fingerprint belong to the operating system that is claimed by the User Agent?
2. How unique is the TLS fingerprint among all clients?
3. Based on past observations and collected TLS client data, is this fingerprint a legit one?
4. To which TLS implementation does this fingerprint belong?


# TLS Fingerprint Definition

What fields from the TLS handshake is considered in the TLS fingerprint? Put differently: What sources of entropy does this tool use to build the TLS fingerprint?

Currently, the following data sources from the initial client `ClientHello` TLS handshake message are used:

+ **TLS Cipher Suites** - The preference-ordered list of [supported cipher suites](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-4) of the client. (Example: `"19018,4865,4866,4867,49195,49199,49196,49200,52393,52392,49171,49172,156,157,47,53"`)
+ **Client Hello Version** - The supported TLS version (Example: `"TLS 1.2"`)
+ **EC Point Formats** - The [EC point formats](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-9) the client supports (Example: `"0,1,2"`)
+ **Extensions** - The list of [supported extensions](https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml#tls-extensiontype-values-1) (Example: `"56026,0,23,65281,10,11,35,16,5,13,18,51,45,43,27,17513,31354"`)
+ **Record Version** - The TLS record version, which is mostly `1.0` (Example: `"TLS 1.0"`)
+ **Signature Algorithms** - The list of supported client [signature algorithms](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-16) (Example: `"1027,2052,1025,1283,2053,1281,2054,1537"`)
+ **Supported Groups** - The list of the [supported groups](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-8) of the client (Example: `"56026,29,23,24"`)

Some TLS clients will randomize some TLS parameters for each new handshake. This is a small problem, but not a substantial one. For example, the following `ClientHello` differs slightly to the next `ClientHello` message:

```json
{
  "num_fingerprints": 10,
  "sha3_384": "a14851b3e6b9daa564f285c983ab929318875eeac94c56d02268bfb00ca37427e7d7d677140284f7aa4da36e0a8979de",
  "timestamp": 1643713939.2002213,
  "tls_fp": {
    "ciphers": "31354,4865,4866,4867,49195,49199,49196,49200,52393,52392,49171,49172,156,157,47,53",
    "client_hello_version": "TLS 1.2",
    "ec_point_formats": "0",
    "extensions": "14906,0,23,65281,10,11,35,16,5,13,18,51,45,43,27,17513,10794",
    "record_version": "TLS 1.0",
    "signature_algorithms": "1027,2052,1025,1283,2053,1281,2054,1537",
    "supported_groups": "47802,29,23,24"
  },
  "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
}
```

As it can be observed, the first element of `ciphers`, `extensions` and `supported_groups` seems to be chosen at random, which results in a different `sha3_384` fingerprint.

```json
{
  "num_fingerprints": 12,
  "sha3_384": "f18a2ee62ee0548fb09c5a31d4bbc61845cc53055c1640e381201d779a80a94e0d870fd48c2fc39fb5b15715ea731d95",
  "timestamp": 1643713950.4840238,
  "tls_fp": {
    "ciphers": "14906,4865,4866,4867,49195,49199,49196,49200,52393,52392,49171,49172,156,157,47,53",
    "client_hello_version": "TLS 1.2",
    "ec_point_formats": "0",
    "extensions": "64250,0,23,65281,10,11,35,16,5,13,18,51,45,43,27,17513,60138,21",
    "record_version": "TLS 1.0",
    "signature_algorithms": "1027,2052,1025,1283,2053,1281,2054,1537",
    "supported_groups": "35466,29,23,24"
  },
  "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
}
```

**Solution:** Only non-Reserved and non-Unassigned values for `ciphers`, `extensions` and `supported_groups` in the TLS fingerprint will be considered.


# Recommended Reading List

So you want to start fingerprinting TLS connections? It's plenty of fun. The following reading list is highly recommended:

1. [Slides - The Generation and Use of TLS Fingerprints](https://resources.sei.cmu.edu/asset_files/Presentation/2019_017_001_539902.pdf) - Cisco is doing advanced TLS fingerprinting and they [open sourced](https://github.com/cisco/joy) some of their TLS fingerprinting methodology and fingerprint database. They are also talking in a blog article named [TLS Fingerprinting in the Real World
](https://blogs.cisco.com/security/tls-fingerprinting-in-the-real-world) about the subject.
2. A rather new paper by researchers from the Technical University of Munich named [TLS Fingerprinting Techniques](https://www.net.in.tum.de/fileadmin/TUM/NET/NET-2020-04-1/NET-2020-04-1_04.pdf) is also a highly suggested read about TLS fingerprinting.
3. Another great read is a blog article named [TLS Fingerprinting with JA3 and JA3S from Salesforce](https://engineering.salesforce.com/tls-fingerprinting-with-ja3-and-ja3s-247362855967) which explains in-depth how Salesforce's JA3 and JA3S TLS fingerprinting works. The code for [JA3 and JA3S is open sourced](https://github.com/salesforce/ja3).


# TODO

- Add tool support for TLS 1.3
- Setup nginx to use TLS 1.3 on the server side
- Think about including the server response in the fingerprint as [JA3S](https://engineering.salesforce.com/tls-fingerprinting-with-ja3-and-ja3s-247362855967) does it: *After some time we found that, though servers will respond to different clients differently, they will always respond to the same client the same.*