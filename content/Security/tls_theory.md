Title: Fingerprinting TLS - Core differences between TLS 1.2 and TLS 1.3
Date: 2022-01-18 12:46
Modified: 2022-01-19 20:46
Category: Security
Tags: TLS Fingerprinting, TLS 1.2, TLS 1.3
Slug: fingerprinting-TLS
Summary: In this blog post, I highlight the core differences between TLS 1.2 and TLS 1.3 and investigate how we can use several properties of the protocol to obtain fingerprinting entropy from TLS clients.
Author: Nikolai Tschacher
Status: Published

## Goal of this Article

The goal of this blog post is twofold:

1. To gain a **better understanding** of the TLS 1.2 and TLS 1.3 protocol.
2. Finding stable entropy sources to **fingerprint TLS client connections**. A TLS fingerprint allows me to infer what kind of TLS client library or operating system a client is using. Correlating TLS handshake data with the advertised HTTP User-Agent gives us information to **detect malicious bots**. For example, many advanced bots use Linux operating systems but claim to be macOS or Windows devices in the HTTP User-Agent. If there is a mismatch in the TLS fingerprint induced OS and the User-Agent advertised OS, grounds for suspicion rise.

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

## TLS 1.2 Theory

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

### The TLS Record Protocol

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

### TLS Handshake Protocol Overview

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

-  The list of supported symmetric encryption algorithms has been pruned of all algorithms that are considered legacy
-  A zero round-trip time (0-RTT) mode was added, saving a round trip at connection setup for some application data, at the cost of certain security properties.
-  Static RSA and Diffie-Hellman cipher suites have been removed; all public-key based key exchange mechanisms now provide forward secrecy.
-  The handshake state machine has been significantly restructured to be more consistent and to remove superfluous messages such as ChangeCipherSpec (except when needed for middlebox compatibility).
-  Elliptic curve algorithms are now in the base spec, and new signature algorithms, such as EdDSA, are included.  TLS 1.3 removed point format negotiation in favor of a single point format for each curve.

## Fingerprinting TLS - A new Tool

In this section I present a simple tool that extracts properties / entropy from the TLS handshake and forms a TLS fingerprint. Such a TLS fingerprint may be used to identify devices. I will also collect statistical data and correlate the entropy with the User-Agent transmitted in HTTP headers. After this data collection process, I can answer questions such as:

1. Does this TLS fingerprint belong to the operating system that is claimed by the User Agent?
2. How unique is the TLS fingerprint of the client in question?