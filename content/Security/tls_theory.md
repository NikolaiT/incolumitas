Title: Fingerprinting TLS - Core differences between TLS 1.2 and TLS 1.3
Date: 2022-01-18 12:46
Modified: 2022-02-02 18:35
Category: Security
Tags: TLS Fingerprinting, TLS 1.2, TLS 1.3
Slug: fingerprinting-TLS
Summary: In this blog post, I highlight the core differences between TLS 1.2 and TLS 1.3 and investigate how we can use several properties of the protocol to obtain fingerprinting entropy from TLS clients.
Author: Nikolai Tschacher
Status: Published


<a 
  class="orange_button" 
  href="https://tls.incolumitas.com/fps">
Get your TLS Fingerprint here
</a>

 — 

<a 
  class="orange_button" 
  href="https://tls.incolumitas.com/stats">
  View TLS Fingerprint Statistics
</a>

## Goal of this Article

The goal of this blog post is twofold:

1. To gain a **better understanding** of the TLS 1.2 and TLS 1.3 protocol.
2. Finding stable entropy sources in the TLS handshake to **fingerprint TLS clients**. A TLS fingerprint allows me to infer what kind of TLS client library or operating system a client is using. 

For instance, correlating TLS handshake data with the advertised HTTP User-Agent gives us information to **detect malicious bots**. For example, many advanced bots use Linux operating systems but claim to be macOS or Windows devices in the HTTP User-Agent. If there is a mismatch in the TLS fingerprint induced OS and the User-Agent advertised OS, this could be a sign that the client lies about its configuration.

## Fingerprinting TLS - A new Tool

In this section, I present a simple tool that extracts properties / entropy from the TLS handshake and forms a TLS fingerprint. Such a TLS fingerprint may be used to identify devices / TLS implementations. This tool will be able to collect statistical data and correlate the entropy with the `User-Agent` transmitted in HTTP headers. After this data collection process, I can answer questions such as:

1. Does this TLS fingerprint belong to the operating system that is claimed by the User Agent?
2. How unique is the TLS fingerprint of the client in question?
3. Based on past observations and collected TLS client data, is this fingerprint a legit one?
4. To what TLS implementation does this fingerprint belong?

**Live TLS Entropy Detection:** This is your last seen TLS handshake data - Taken from the initial Client Hello handshake message:

<pre style="overflow: auto;" id="tls_fp">
...loading (JavaScript required)
</pre>

<script>
fetch('https://tls.incolumitas.com/fps')
  .then(response => response.json())
  .then(function(data) {
    document.getElementById('tls_fp').innerText = JSON.stringify(data, null, 2);
  })
</script>

Your User-Agent (`navigator.userAgent`) says that you are 

<pre style="overflow: auto;" id="userAgent">
</pre>

<script>
document.getElementById('userAgent').innerText = navigator.userAgent;
</script>

## TLS Fingerprint Definition

What fields/data from the TLS handshake constitutes the TLS fingerprint? Put differently: What sources of entropy do I use to build the TLS fingerprint?

Currently, I use the following data sources from the initial client `ClientHello` TLS handshake message:

+ **TLS Cipher Suites** - The preference-ordered list of [supported cipher suites](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-4) of the client. (Example: `"19018,4865,4866,4867,49195,49199,49196,49200,52393,52392,49171,49172,156,157,47,53"`)
+ **Client Hello Version** - The supported TLS version (Example: `"TLS 1.2"`)
+ **EC Point Formats** - The [EC point formats](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-9) the client supports (Example: `"0,1,2"`)
+ **Extensions** - The list of [supported extensions](https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml#tls-extensiontype-values-1) (Example: `"56026,0,23,65281,10,11,35,16,5,13,18,51,45,43,27,17513,31354"`)
+ **Record Version** - The TLS record version, which is mostly `1.0` (Example: `"TLS 1.0"`)
+ **Signature Algorithms** - The list of supported client [signature algorithms](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-16) (Example: `"1027,2052,1025,1283,2053,1281,2054,1537"`)
+ **Supported Groups** - The list of the [supported groups](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-8) of the client (Example: `"56026,29,23,24"`)

Some TLS clients will randomize some TLS parameters for each new handshake. This is a small problem, but not substantial. For example, my own laptop/browser sends the following `ClientHello` and a slightly different in the next `ClientHello`:

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

As you can observe, the first element of `ciphers`, `extensions` and `supported_groups` seems to be chosen at random, which results in a different `sha3_384` fingerprint.

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

**Solution:** I will only consider non-Reserved and non-Unassigned values for `ciphers`, `extensions` and `supported_groups` in the TLS fingerprint.

## Recommended Reading List

So you want to start fingerprinting TLS connections? It's plenty of fun. For me, the following reading list was very helpful:

1. [Slides - The Generation and Use of TLS Fingerprints](https://resources.sei.cmu.edu/asset_files/Presentation/2019_017_001_539902.pdf) - Cisco is doing advanced TLS fingerprinting and they [open sourced](https://github.com/cisco/joy) some of their TLS fingerprinting methodology and fingerprint database. They are also talking in a blog article named [TLS Fingerprinting in the Real World
](https://blogs.cisco.com/security/tls-fingerprinting-in-the-real-world) about the subject.
2. A rather new paper by researchers from the Technical University of Munich named [TLS Fingerprinting Techniques](https://www.net.in.tum.de/fileadmin/TUM/NET/NET-2020-04-1/NET-2020-04-1_04.pdf) is also a highly suggested read about TLS fingerprinting.
3. Another great read is a blog article named [TLS Fingerprinting with JA3 and JA3S from Salesforce](https://engineering.salesforce.com/tls-fingerprinting-with-ja3-and-ja3s-247362855967) which explains in-depth how Salesforce's JA3 and JA3S TLS fingerprinting works. The code for [JA3 and JA3S is open sourced](https://github.com/salesforce/ja3).

## Introduction

TLS stands for *Transport Layer Security* and is the successor of the deprecated Secure Sockets Layer (SSL) protocol. TLS is a client / server protocol that allows connections to be cryptographically *secure*.

TLS and SSL are application layer protocols, which means that they are situated above the Transport Layer (such as TCP and UDP) and of course also above the Network Layer (with IPv4 and Ipv6 being the most prominent protocols in the Network Layer). This means that a TLS connection establishment occurs after the TCP/IP handshake and before messages exchanges from protocols such as FTP or HTTP. 

Nevertheless, TLS is a protocol on the same application layer level as the protocols FTP or HTTP. This is often confusing, since we often speak of SFTP (Secure FTP) and HTTPS (Hypertext Transfer Protocol Secure). Are those completely new protocols then? Yes and no! HTTPS is the same as HTTP, but the protocol is encapsulated by a secure channel that is established by TLS.

[The TLS Wikipedia Article](https://en.wikipedia.org/wiki/Transport_Layer_Security#Description) explains this in a very good way:

> TLS and SSL do not fit neatly into any single layer of the OSI model or the TCP/IP model. TLS runs "on top of some reliable transport protocol (such as TCP), which would imply that it is above the transport layer. It serves encryption to higher layers, which is normally the function of the presentation layer. However, applications generally use TLS as if it were a transport layer, even though applications using TLS must actively control initiating TLS handshakes and handling of exchanged authentication certificates.

TLS is a Internet Engineering Task Force (IETF) standard and was first defined in 1999. Nowadays, the most relevant TLS versions are TLS 1.2 and TLS 1.3, both are defined in seperate RFCs:

1. TLS 1.2 is defined in [RFC 5246](https://datatracker.ietf.org/doc/html/rfc5246) and dates back to August 2008.
2. TLS 1.3 was released 10 years later in August 2018. TLS 1.3 is defined in [RFC 8446](https://datatracker.ietf.org/doc/html/rfc8446) and is the latest major TLS release.

But what security properties does the TLS protocol offer exactly?

- A TLS connection is secure / confidential because every transmitted byte is encrypted by a symmetric cryptographical algorithm. The symmetric key is generated freshly for each new protocol instance, which gives us *forward secrecy*. Put differently, with the help of the Diffie-Hellman key exchange, a common secret is derived between client and server.

- The identity of the server can be authenticated with public-key cryptography. The client can verify the authenticity of the server by verifying the server certificate. Whereas authentication for the server is mandatory, it is optional for the client.

- A TLS connection is reliable, since each message is protected by a message authentication code (MAC), which prevents undetected loss and modification of data in transmission (For example by a man-in-the-middle attacker).

# TLS 1.2 - An RFC 5246 Summary

In the following sections, I will summarize the most important aspects of [RFC 5246](https://datatracker.ietf.org/doc/html/rfc5246). Some text sessions are direct quotes from [RFC 5246](https://datatracker.ietf.org/doc/html/rfc5246). Most of it is summarized and extended.

The RFC states that TLS is a protocol that provides privacy and data integrity between two communication partners. The TSL protocol is composed of two layers:

1. the TLS Record Protocol and 
2. the TLS Handshake Protocol.

The TLS Record Protocol provides connection security with two basic properties:

1. The connection is private. This is done with symmetric data encryption. The symmetric key is negociated with the TLS Handshake Protocol.
2. The connection is reliable. The messages integrity is protected with a keyed MAC.


The TLS Record Protocol is the underlying protocol of every TLS message, also the messages of the TLS Handshaking Protocol.

The TLS Handshake Protocol provides connection security that has three basic properties:

1. **Authenticaton**: The peer's identity can be authenticated using asymmetric, or
  public key, cryptography. This authentication is optional, but is usually required for
  the TLS server.

2. **Man-in-the-middle resistance**: The negotiation of a shared secret is secure and unavailable to eavesdroppers.
  The secret cannot be obtained by an man-in-the-middle attacker.

3. **Integrity** :The negotiation is reliable: no attacker can modify the
  negotiation communication without being detected.

One advantage of TLS is that it is application protocol independent.
Higher-level protocols can layer on top of the TLS protocol transparently.

## The TLS 1.2 Record Protocol

The TLS Record Protocol is a layered protocol.

[RFC 5246](https://datatracker.ietf.org/doc/html/rfc5246) states:

> At each layer, messages may include fields for length, description, and content.
  The Record Protocol takes messages to be transmitted, fragments the
  data into manageable blocks, optionally compresses the data, applies
  a MAC, encrypts, and transmits the result.  Received data is
  decrypted, verified, decompressed, reassembled, and then delivered to
  higher-level clients.

TLS 1.2 makes use of four protocols that are described in this
document: The handshake protocol, the alert protocol, the change
cipher spec protocol, and the application data protocol.

TLS has three subprotocols:

1. A subprotocol that is used to allow peers to agree upon
security parameters for the record layer
2. One to authenticate themselves
3. And one to instantiate negotiated security parameters, and to report error
conditions to each other.

The Handshake Protocol is responsible for negotiating a session,
which consists of the following items:

1. **session identifier** -  An arbitrary byte sequence chosen by the server to identify an
  active or resumable session
2. **peer certificate** - X509v3 certificate of the peer.
3. **compression method** - The algorithm used to compress data prior to encryption.
4. **cipher spec** - Specifies the pseudorandom function (PRF) used to generate keying
  material, the bulk data encryption algorithm (such as null, AES,
  etc.) and the MAC algorithm (such as HMAC-SHA1).
5. **master secret** - 48-byte secret shared between the client and server.
6. **is resumable** - A flag indicating whether the session can be used to initiate new
  connections.
  
These items are then used to create security parameters for use by
the record layer when protecting raw application data.  Connections
can be reused using the same session through the resumption
feature.

Then there is the **Change Cipher Spec Protocol** message: This message is sent by both the client and the
server to notify the other party that subsequent records will be
protected under the newly negotiated ciphers and keys.

The **Alert Protocol** messages convey the severity of the message
(warning or fatal) and a description of the alert.  Alert messages
with a level of fatal result in the immediate termination of the
connection.

## TLS 1.2 Handshake Protocol Overview

The cryptographic parameters for each TLS session are produced by the
TLS Handshake Protocol, which operates on top of the TLS record
layer. When a TLS client and server start a new protocol iteration, they do the following:

1. Client and server agree on a protocol version
2. They select cryptographic algorithms
3. They optionally authenticate each other
4. And they use public-key encryption techniques to generate shared secrets

The TLS Handshake Protocol consists of the following steps:

In a first step, client and server exchange hello messages to agree on algorithms, exchange random
values, and check for session resumption.
  
Then they exchange the necessary cryptographic parameters to allow the client and server to agree on a premaster secret.

After that, they exchange certificates and cryptographic information to allow the client and server to authenticate themselves. In practice, only the server is authenticated.

Both generate a master secret from the premaster secret and exchanged random values.

Client and server provide security parameters to the record layer.

Finally, the protocol allows the client and server to verify that their peer has calculated the same security parameters and that the handshake occurred without tampering.

This is how the full TLS handshake occurs in more detail:

The client sends a `ClientHello` message to
which the server must respond with a `ServerHello` message (else a
fatal error will occur and the connection will terminate). The `ClientHello` and
`ServerHello` establish the following attributes: Protocol Version,
Session ID, Cipher Suite, and Compression Method.  Additionally, two
random values are generated and exchanged: `ClientHello.random` and
`ServerHello.random`.

The actual key exchange uses up to four messages: the server
Certificate, the `ServerKeyExchange`, the client Certificate, and the
`ClientKeyExchange`.

Following the hello messages, the server will send its certificate in
a Certificate message if it is to be authenticated.  Additionally, a
`ServerKeyExchange` message may be sent, if it is required, for example if
the server has no certificate, or if its certificate is for signing
only. If the server is authenticated, it may request a certificate
from the client.

Next, the server will send the `ServerHelloDone` message, indicating
that the hello-message phase of the handshake is complete.  The
server will then wait for a client response.  If the server has sent
a `CertificateRequest` message, the client MUST send the Certificate
message.  The `ClientKeyExchange` message is now sent, and the content
of that message will depend on the public key algorithm selected
between the `ClientHello` and the `ServerHello`.  If the client has sent
a certificate with signing ability, a digitally-signed
CertificateVerify message is sent to explicitly verify possession of
the private key in the certificate.

At this point, a `ChangeCipherSpec` message is sent by the client, and
the client copies the pending Cipher Spec into the current Cipher
Spec.  The client then immediately sends the Finished message under
the new algorithms, keys, and secrets.  In response, the server will
send its own `ChangeCipherSpec` message, transfer the pending to the
current Cipher Spec, and send its Finished message under the new
Cipher Spec.  At this point, the handshake is complete, and the
client and server may begin to exchange application layer data.
Application data is not allowed to be sent prior to the
completion of the first handshake (before a cipher suite other than
TLS_NULL_WITH_NULL_NULL is established).

This is the full TLS Handshake Protocol Overview (\* Indicates optional or situation-dependent messages):



      Client                                               Server

      ClientHello                  -------->
                                                      ServerHello
                                                     Certificate*
                                               ServerKeyExchange*
                                              CertificateRequest*
                                   <--------      ServerHelloDone
      Certificate*
      ClientKeyExchange
      CertificateVerify*
      [ChangeCipherSpec]
      Finished                     -------->
                                               [ChangeCipherSpec]
                                   <--------             Finished
      Application Data             <------->     Application Data



When the client and server decide to resume a previous session, the message flow is as follows:

The client sends a ClientHello using the Session ID of the session to
be resumed. The server then checks its session cache for a match.
If a match is found, and the server is willing to re-establish the
connection under the specified session state, it will send a
`ServerHello` with the same Session ID value.  At this point, both
client and server MUST send `ChangeCipherSpec` messages and proceed
directly to Finished messages.  Once the re-establishment is
complete, the client and server can exchange application
layer data. If a Session ID match is not
found, the TLS client and server perform a full handshake.

Session resumption, abbreviated handshake:


      Client                                                Server

      ClientHello                   -------->
                                                       ServerHello
                                                [ChangeCipherSpec]
                                    <--------             Finished
      [ChangeCipherSpec]
      Finished                      -------->
      Application Data              <------->     Application Data


# Core Improvements of TLS 1.3 compared to TLS 1.2

Excellent articles on the most important differences between TLS 1.2 and TLS 1.3 can be found in

+ an article from 2018 from Cloudflare Inc. named [A Detailed Look at RFC 8446 (a.k.a. TLS 1.3)](https://blog.cloudflare.com/rfc-8446-aka-tls-1-3/), which is an excellent read on that topic

+ and another great article from thesslstore.com named [TLS 1.2 vs. TLS 1.3 – What’s the difference?](https://www.thesslstore.com/blog/tls-1-3-everything-possibly-needed-know/)

This section is heavily based on those two articles.

<figure>
    <img src="{static}/images/tls-comp.png" alt="TLS 1.2 vs TLS 1.3" />
    <figcaption>Visual comparison of TLS 1.2 and TLS 1.3 (<a href="https://www.embeddedcomputing.com/technology/security/advantages-to-using-tls-1-3-faster-more-efficient-more-secure">Image source</a>)</figcaption>
</figure>


The core improvements from TLS 1.3 over its predecessor TLS 1.2 are:

+ *Removal of legacy ciphers:* TLS 1.3 eliminates support for outmoded algorithms and ciphers
+ *RSA removed:* TLS 1.3 eliminates RSA key exchange, mandates Perfect Forward Secrecy
+ *Reduced handshake complexity:* Reduces the number of negotiations in the handshake
+ *Less ciphers:* Reduces the number of algorithms in a cipher suite to only 2
+ *No more block ciphers:* TLS 1.3 eliminates block mode ciphers and mandates AEAD bulk encryption
+ TLS 1.3 uses HKDF cryptographic extraction and key derivation
+ *Reduced RTTs:* TLS 1.3 offers 1-RTT mode and Zero Round Trip Resumption
+ *More secure:* TLS 1.3 signs the entire handshake, an improvement of TLS 1.2
+ *More curves:* TLS 1.3 supports additional elliptic curves


**TLS 1.2 is slow:** TLS 1.2 remained unchanged since TLS was first standardized in 1999, which means that it still requires two additional round-trips between client and server before the connection is encrypted. This is one reason why a new TLS version was in the planning.

**Design goals for TLS 1.3:** There were several underlying design goals that drove the development of TLS 1.3 in an open process:

+ Reducing the number of TLS handshake RTTs
+ Encrypting the whole TLS handshake instead of the partial handshake as in TLS 1.2
+ Increase the resilience against cross-protocol attacks
+ Removing legacy features, especially legacy ciphers

The two main advantages from TLS 1.3 on TLS 1.2 are increased performance and improved security.

**Deprecation of the RSA key exchange in TLS 1.3:** In the RSA key exchange, the shared secret is decided by the client. The client encrypts the chosen secret with the server's public key (obtained from the server certificate) and sends it to the server. The RSA key exchange has an important downside: It is not forward secret because it doesn’t offer an ephemeral key mode.

Forward secrecy is the property that prevents attackers from decrypting traffic that was recorded in the past, if they manage to get hold of the RSA private key from the server.

Put differently: If an attacker finds out the RSA private key of the server, they can decrypt all past and future traffic between the client and server. Obtaining the server RSA private key was possible through the [Heartbleed vulnerability](https://heartbleed.com/), therefore it is not an hypothetical example. RSA usage is dangerous!

Another reason for the deprecation of RSA is the difficulty of implementing RSA encryption properly, as the infamous [Bleichenbacher attacks](https://en.wikipedia.org/wiki/Daniel_Bleichenbacher) (*million-message attacks*) against RSA have shown. Those attacks are also known under the name [Oracle padding attacks](https://www.thesslstore.com/blog/bleichenbachers-cat-rsa-key-exchange/).

For that reason, TLS 1.3 only supports the ephemeral Diffie-Hellman key exchange, where the client and server generate new public/private key pairs for each instance of the TLS handshake. Then they establish a shared secret by combining their respective public key parts. Because a new key pair is generated for each instance, the handshake is ephemeral and is forward secret. 

Another advantage of deprecating RSA as key exchange option: Client and server may only use the ephemeral Diffie-Hellman key exchange, so the client can save one RTT by sending the requisite randoms and inputs needed for key generation directly, without having to agree with the server whether RSA or DH should be used.

This leads to...

**1-RTT handshake:** Due to the simpler cipher negotiation model and reduced set of key agreement options (no RSA, no user defined DH parameters), the parameters supported by the server are easier to guess (ECDHE with X25519 or P-256 for example). This allows the client to simply send DH key shares in the first message instead of waiting until the server has confirmed which key shares it supports. 

This leads to a one RTT handshake that looks like the following:

<figure>
    <img src="{static}/images/Single-Round-Trip-Handshake-1.png" alt="TLS 1.3 simplified handshake" />
    <figcaption>The TLS 1.3 simplified handshake (<a href="https://www.thesslstore.com/blog/tls-1-3-everything-possibly-needed-know/">Image taken from the www.thesslstore.com blog</a>)</figcaption>
</figure>


**0-RTT handshake resumption:** With TLS 1.3, clients can send encrypted data in the first message. In TLS 1.2, there are two different ways to resume a connection:

1. session ids 
2. session tickets

In TLS 1.3, there is a new session-resumption mode called PSK resumption, which allows for almost-instantaneous session resumption for visitors that have recently connected to your TLS server.

In this mode, the client and server derive a shared secret called the "resumption main secret" which is stored on the server. The session ticket is sent to the client and used when a new TLS session is created.

The next time the client connects to the server, it can take the secret from the previous session and use it to encrypt application data that is sent to the server (alongside sending the session ticket). The server validates the session ticket and the session resumes.


**TLS 1.3 reduces choice in cryptographic schemes:** TLS 1.3 reduces Diffie-Hellman parameters to ones that are known to be secure. Furthermore, TLS 1.3 also reduces heavily the choice of symmetric ciphers used for decryption and their mode of operation. In fact, TLS 1.3 removed all CBC-mode ciphers or insecure stream ciphers such as RC4. The only symmetric crypto that is still allowed in TLS 1.3 are AEAD (authenticated encryption with additional data) ciphers, which means that encryption and integrity occur in one and the same operation.

Among others, TLS 1.3 mandated the removal of the following TLS 1.2 ciphers:

+ RC4 Stream Cipher
+ RSA Key Exchange
+ SHA-1 Hash Function
+ CBC (Block) Mode Ciphers
+ MD5 Algorithm
+ Various non-ephemeral Diffie-Hellman groups
+ EXPORT-strength ciphers
+ DES
+ 3DES

**Removing PKCS#1 v1.5 padding:** As discussed above, [Bleichenbacher attacks](https://en.wikipedia.org/wiki/Daniel_Bleichenbacher) worked against RSA signatures used in TLS 1.2, with the underlying difficulty of implementing RSA padding correctly. In TLS 1.3, the newer design RSA-PSS obsoleted PKCS#1 v1.5 padding.

**Signing the whole handshake:** The TLS server uses a digital signature to prove that they key exchange was not tampered. In TLS 1.2, the server signature only covers part of the handshake, especially not the part where the server negotiates which symmetric cipher should be used. This lead to a number of vulnerabilities such as FREAK and LogJam, where a man-in-the-middle attacker can downgrade the chosen ciphers to pick intentionally weak ciphers (export ciphers). In TLS 1.3, the server signs the entire handshake transcript.

<figure>
    <img src="{static}/images/FREAK.png" alt="TLS 1.2 vs FREAK" />
    <figcaption>The TLS FREAK downgrade attack (<a href="https://blog.cloudflare.com/rfc-8446-aka-tls-1-3/">Image taken from the Cloudflare blog</a>)</figcaption>
</figure>

**General protocol simplification:** In previous TLS protocols, the entire ciphersuite was negotiated including many crypto attributes:

- certificate types that are supported
- hash function used (SHA1, SHA256, ...)
- MAC function (HMAC with SHA1, SHA256, ...)
- key exchange algorithm (RSA, ECDHE, ...)
- cipher (e.g., AES, RC4, ...) and cipher mode, if applicable (e.g., CBC)

This lead to a combinational explosion of crypto ciphe code points that had to be maintained by the Internet Assigned Numbers Authority (IANA). There is the [IANA page](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-parameters-4) that hosts a [CSV file](https://www.iana.org/assignments/tls-parameters/tls-parameters-4.csv) that includes all the ciphers currently used in TLS 1.2. It's a huge file!

TLS 1.3 on the other hand only allows peers to negotiate:

+ Cipher + HKDF Hash
+ Key Exchange
+ Signature Algorithm

As discussed above, this has the side effect that the handshake only needs one RTT instead of two RTTs.

**Simplified Cipher Suites:** 

Due to this massive elimination of cipher suites in TLS 1.3, the size of possible cipher suites went down.

A TLS 1.2 cipher had the following format:

<figure>
    <img src="{static}/images/TLS-1.2-Cipher-Suite.png" alt="TLS 1.2 ciphersuite" />
    <figcaption>TLS 1.2 ciphersuite (<a href="https://www.thesslstore.com/blog/tls-1-3-everything-possibly-needed-know/">Image taken from the www.thesslstore.com blog</a>)</figcaption>
</figure>

And this is how a TLS 1.3 ciphersuite looks. Much easier, right?!

<figure>
    <img src="{static}/images/TLS-1.3-cipher-suite.png" alt="TLS 1.3 ciphersuite" />
    <figcaption>Much simpler TLS 1.3 ciphersuite (<a href="https://www.thesslstore.com/blog/tls-1-3-everything-possibly-needed-know/">Image taken from the www.thesslstore.com blog</a>)</figcaption>
</figure>

There were an awful lot of [TLS 1.2 ciphersuite choices](https://www.iana.org/assignments/tls-parameters/tls-parameters-4.csv). 

With TLS 1.3, we have only the following recommended secure choices:

+ TLS_AES_256_GCM_SHA384
+ TLS_CHACHA20_POLY1305_SHA256
+ TLS_AES_128_GCM_SHA256
+ TLS_AES_128_CCM_8_SHA256
+ TLS_AES_128_CCM_SHA256

