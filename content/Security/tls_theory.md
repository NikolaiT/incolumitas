Title: Fingerprinting TLS - Core differences between TLS 1.2 and TLS 1.3
Date: 2022-01-18 12:46
Modified: 2022-01-22 18:35
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

## Goal of this Article

The goal of this blog post is twofold:

1. To gain a **better understanding** of the TLS 1.2 and TLS 1.3 protocol.
2. Finding stable entropy sources in the TLS handshake to **fingerprint TLS clients**. A TLS fingerprint allows me to infer what kind of TLS client library or operating system a client is using. 

For instance, correlating TLS handshake data with the advertised HTTP User-Agent gives us information to **detect malicious bots**. For example, many advanced bots use Linux operating systems but claim to be macOS or Windows devices in the HTTP User-Agent. If there is a mismatch in the TLS fingerprint induced OS and the User-Agent advertised OS, this could be a sign that the client lies about its configuration.

## Fingerprinting TLS - A new Tool

In this section I present a simple tool that extracts properties / entropy from the TLS handshake and forms a TLS fingerprint. Such a TLS fingerprint may be used to identify devices. This tool will be able to collect statistical data and correlate the entropy with the User-Agent transmitted in HTTP headers. After this data collection process, I can answer questions such as:

1. Does this TLS fingerprint belong to the operating system that is claimed by the User Agent?
2. How unique is the TLS fingerprint of the client in question?
3. Based on past observations and collected TLS client data, is this fingerprint a legit one?
4. To what TLS implementation does this fingerprint belong?

**Live TLS Entropy Detection:** This is your last seen TLS handshake data (From the initial Client Hello handshake message):

<pre style="overflow: auto;" id="tls_fp">
...loading
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

## TLS 1.2 RFC 5246 Summary

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

### The TLS 1.2 Record Protocol

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

### TLS 1.2 Handshake Protocol Overview

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


## Core Differences Between TLS 1.2 and TLS 1.3

In the following section, I will highlight the core differences between TLS 1.2 and TLS 1.3.  An article from 2018 from Cloudflare Inc. named (A Detailed Look at RFC 8446 (a.k.a. TLS 1.3))[https://blog.cloudflare.com/rfc-8446-aka-tls-1-3/] is an excellent read on that topic and my summary is based on this article.

<figure>
    <img src="{static}/images/tls-comp.png" alt="TLS 1.2 vs TLS 1.3" />
    <figcaption>TLS 1.2 vs TLS 1.3 (<a href="https://www.embeddedcomputing.com/technology/security/advantages-to-using-tls-1-3-faster-more-efficient-more-secure">Image source</a>)</figcaption>
</figure>


**TLS 1.2 is slow:** The TLS 1.2 remained unchanged since TLS was first standardized in 1999, which means that it still requires two additional round-trips between client and server before the connection is encrypted. This is one reason why a new TLS version was in the planning.

**Design goals for TLS 1.3:** There were several underlying design goals that drove the development of TLS 1.3 in an ope process:

+ Reducing the number of TLS handshake RTTs
+ Encrypting the whole TLS handshake
+ Increase the resilience against cross-protocol attacks
+ Removing legacy features, especially legacy ciphers

The two main advantages of TLS 1.3 versus TLS 1.2 are increased performance and improved security.

**Deprecation of the RSA key exchange in TLS 1.3:** In the RSA key exchange, the shared secret is decided by the client. The client encrypts the chosen secret with the server's public key (obtained from the server certificate) and sends it to the server. The RSA key exchange has a important downside: It is not forward secret. Forward secrecy is the property that prevents attackers from decrypting traffic that was recorded in the past if they manage to get hold of the RSA private key on the server. Put differently: If an attacker finds out the RSA private key of the server, they can decrypt all past and future traffic between the client and server.

Another reason for the deprecation of RSA is the difficulty of implementing RSA encryption properly, as the infamous [Bleichenbacher attacks](https://en.wikipedia.org/wiki/Daniel_Bleichenbacher) (*million-message attacks*) against RSA have shown.

For that reason, TLS 1.3 only supports the ephemeral Diffie-Hellman key exchange, where the client and server generate new public/private key pairs for each instance of the TLS handshake. Then they establish a shared secret by combining their respective public key parts. Because a new key pair is generated for each instance, the handshake is ephemeral and is forward secret. 

**TLS 1.3 reduces choice in cryptographic schemes:** TLS 1.3 reduces Diffie-Hellman parameters to ones that are known to be secure. Furthermore, TLS 1.3 also reduces heavily the choice of symmetric ciphers used for decryption and their mode of operation. In fact, TLS 1.3 removed all CBC-mode ciphers or insecure stream ciphers such as RC4. The only symmetric crypto that is still allowed in TLS 1.3 are AEAD (authenticated encryption with additional data) ciphers, which means that encryption and integrity occur in one and the same operation.

**Removing PKCS#1 v1.5 padding:** As discussed above, [Bleichenbacher attacks](https://en.wikipedia.org/wiki/Daniel_Bleichenbacher) worked against RSA signatures used in TLS 1.2, with the underlying difficulty of implementing RSA padding correctly. In TLS 1.3, the newer design RSA-PSS obsoleted PKCS#1 v1.5 padding.

**Signing the whole handshake:** The TLS server uses a digital signature to prove that they key exchange was not tampered. In TLS 1.2, the server signature only covers part of the handshake, especially not the part where the server negotiates which symmetric cipher should be used. This lead to a number of vulnerabilities such as FREAK and LogJam, where a man-in-the-middle attacker can downgrade the chosen ciphers to pick intentionally weak ciphers (export ciphers). In TLS 1.3, the server signs the entire handshake transcript.

<figure>
    <img src="{static}/images/FREAK.png" alt="TLS 1.2 vs FREAK" />
    <figcaption>The TLS FREAK downgrade attack (<a href="https://blog.cloudflare.com/rfc-8446-aka-tls-1-3/">Image taken from the Cloudflare Blog</a>)</figcaption>
</figure>


**More protocol simplification:** In previous TLS protocols, the entire ciphersuite was negotiated including many crypto attributes:

- certificate types that are supported
- hash function used (SHA1, SHA256, ...)
- MAC function (HMAC with SHA1, SHA256, ...)
- key exchange algorithm (RSA, ECDHE, ...)
- cipher (e.g., AES, RC4, ...) and cipher mode, if applicable (e.g., CBC)

This lead to a combinational explosion of crypto ciphe code points that had to be maintained by the Internet Assigned Numbers Authority (IANA).

TLS 1.3 on the other hand only allows peers to negotiate:

+ Cipher + HKDF Hash
+ Key Exchange
+ Signature Algorithm

This has the side effect that the handshake only needs one RTT instead of two RTTs.

**1-RTT handshake:** Due to the simpler cipher negotiation model and reduced set of key agreement options (no RSA, no user defined DH parameters), the parameters supported by the server are easier to guess (ECDHE with X25519 or P-256 for example). This allows the client to simply send DH key shares in the first message instead of waiting until the server has confirmed which key shares it supports. This leads to a one RTT handshake.

**0-RTT handshake resumption:** With TLS 1.3, clients can send encrypted data in the first message. In TLS 1.2, there are two different ways to resume a connection:

1. session ids 
2. session tickets

In TLS 1.3, there is a new session-resumption mode called PSK resumption. In this mode, the client and server derive a shared secret called the "resumption main secret" which is stored on the server. The session ticket is sent to the client and used when a new TLS session is created.

The next time the client connects to the server, it can take the secret from the previous session and use it to encrypt application data that is sent to the server (alongside sending the session ticket).