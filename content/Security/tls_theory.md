Title: Fingerprinting TLS - Core differences between TLS 1.2 and TLS 1.3
Date: 2022-01-18 12:46
Category: Security
Tags: TLS, TLS 1.2, TLS 1.3
Slug: core-differences-between-tls1-2-and-tls1-3
Summary: In this blog post, I highlight the core differences between TLS 1.2 and TLS 1.3 and investigate how we can use several properties of the protocol to obtain fingerprinting entropy from TLS clients.
Author: Nikolai Tschacher
Status: Published

**This article is in the process of being created. Hold tight a couple of days! A new tool (TLS fingerprinting) is in the process of being created!**

## Introduction

TLS stands for *Transport Layer Security* and is the successor of the deprecated Secure Sockets Layer (SSL) protocol. TLS is a client / server protocol that allows connections to be cryptographically *secure*.

TLS and SSL are application layer protocols, which means that they are situated above the Transport Layer (such as TCP and UDP) and of course also above the Network Layer (with IPv4 and Ipv6 being the most prominent protocols in the Network Layer). This means that a TLS connection establishment occurs after the TCP/IP handshake. 

Therefore, TLS is a protocol on the same application layer level as the protocols FTP or HTTP. This is often confusing, since we often speak of SFTP (Secure FTP) and HTTPS (Hypertext Transfer Protocol Secure). Are those new protocols then? Yes and no! HTTPS is the same as HTTP, but the protocol is piped through the secure channel that is established by TLS.

[The TLS Wikipedia Article](https://en.wikipedia.org/wiki/Transport_Layer_Security#Description) explains this in a very good way:

> TLS and SSL do not fit neatly into any single layer of the OSI model or the TCP/IP model.[4][5] TLS runs "on top of some reliable transport protocol (e.g., TCP),"[6] which would imply that it is above the transport layer. It serves encryption to higher layers, which is normally the function of the presentation layer. However, applications generally use TLS as if it were a transport layer,[4][5] even though applications using TLS must actively control initiating TLS handshakes and handling of exchanged authentication certificates.

TLS is a Internet Engineering Task Force (IETF) standard and was first defined in 1999. 

- TLS 1.2 is defined in [RFC 5246](https://datatracker.ietf.org/doc/html/rfc5246) and dates back to August 2008.
- TLS 1.3 was released 10 years later in August 2018. TLS 1.3 is defined in [RFC 8446](https://datatracker.ietf.org/doc/html/rfc8446) and is the latest major TLS release.

But what security properties does the TLS protocol offer exactly?

- A TLS connection is secure / confidential because every transmitted byte is encrypted by a symmetric cryptographical algorithm. The symmetric key is generated freshly for each new protocol instance, which gives us *forward secrecy*. Put differently, with the help of the Diffie-Hellman key exchange, a common secret is derived between client and server.

- The identity of the server can be authenticated with public-key cryptography. The client can verify the authenticity of the server by verifying the server certificate. Whereas authentication for the server is mandatory, it is optional for the client.

- A TLS connection is reliable, since each message is protected by a message authentication code (MAC), which prevents undetected loss and modification of data in transmission (For example by a man-in-the-middle attacker).

## Protocol Walk-Through

To be done.

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