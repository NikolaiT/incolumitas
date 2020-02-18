Title: Socks 5 client support for twisted
Date: 2014-02-05 22:24
Author: Nikolai Tschacher
Category: Programming
Tags: Python, Twisted, Socks5, Programming, Security
Slug: socks-5-client-support-for-twisted
Status: published

I recently forked
[twisted-socks](https://github.com/ln5/twisted-socks "twisted socks client")
to add SOCKS 5 support for my
[GoogleScraper](http://incolumitas.com/googlescraper-py/ "GoogleScraper")
in order to scraper Google pages asynchronously. Obviously I needed
SOCKS5 support to anonymize the parallel requests such that I can scrape
more pages simultaneously.

I tested the code for SOCKS4 and SOCKS4a with a local TOR proxy and
`twistd -n socks` and the SOCKS5 protocol with the [dante socks proxy
server](http://www.inet.no/dante/ "dante") on my VPS. So I guess the
basic functionality should be working by now. GSSAPI (Kerberos)
[support](https://tools.ietf.org/html/rfc1961) is planned.

Here is the socksclient code, which is also available on my github
repository:

    :::python
    # Copyright (c) 2011-2013, The Tor Project
    # See LICENSE for the license.

    # Updated on 25.01.14-28.01.14 to add SOCKS 5 support.
    # Cleaned some parts of the code and abstracted quite a bit to handle the most important SOCKS5
    # functionality like
    # - username/password authentication
    # - gssapi authentication (planned)
    # - CONNECT command (the normal case, there are others: UDP ASSOCIATE and BIND, but they aren't as important. Maybe I will add them
    #   in the future. If anyone wants to implement them, the basic structure is already here and the SOCKSv5ClientProtocol should be
    #   rather easy extensible (how the actual connection, listening for incoming connections (BIND) and opening a UDP connection (UDP ASSOCIATE)
    #   is done in the twisted world, is another question.
    # Added:
    # - SOCKSv4ClientFactory was renamed to SOCKSClientFactory and abstracted to handle all SOCKS 4/4a SOCKS5 (It is still ONE protocol, so one Factory should be logical correct)
    # - added SOCKS5ClientFactory
    # - SOCKSClientProtocol is the base class for all three protocols
    # - SOCKSv4aClientProtocol inherits from  SOCKSv4ClientProtocol. I made the deliberate choice to differ between SOCKS 4 and 4a, altough 4a has the exactly same functionality as 4,
    #   it might be the case that servers only speak version 4.
    # References:
    # A actively maintained, most recent version of PySocks from https://github.com/Anorov/PySocks
    # The original version of socksclient.py:

    # Author: Nikolai Tschacher
    # Contact: incolumitas.com

    import inspect
    import socket
    import re
    import struct
    from zope.interface import implements
    from twisted.internet import defer
    from twisted.internet.interfaces import IStreamClientEndpoint, IReactorTime
    from twisted.internet.protocol import Protocol, ClientFactory
    from twisted.internet.endpoints import _WrappingFactory

    class SOCKSError(Exception):
        def __init__(self, val):
            self.val = val
        def __str__(self):
            return repr(self.val)

    class SOCKSClientProtocol(Protocol):
        '''
        Base class for SOCKS protocols 4, 4a and 5
        '''
        buf = ''

        def noteTime(self, event):
            if self._timer:
                self._timestamps[event] = self._timer.seconds()

        def abort(self, errmsg):
            self.transport.loseConnection()
            self.handshakeDone.errback(SOCKSError('SOCKS %s: %s' % (self.proxy_config['version'], errmsg)))

        def isHostname(self, string):
            dns_label_regex = re.compile(r'^(?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?H", port)
            self.transport.write(msg)
            self.noteTime('RELAY_REQUEST_SENT')
            self.protocol_state = 'connection_requested'

        def verifySocksReply(self, data):
            where = 'SOCKS5 verifySocksReply'

            if len(data) < 10: # all hostname are longer than a IPv4 address
                self.abort('Too few data from server %s.' % where)
            else:
                version, reply, rsv, address_type = struct.unpack('!BBBB', data[:4])

                if version != 0x5:
                    self.abort('Invalid version')
                    return False

                if reply != 0x0:
                    self.abort('Server reply indicates failure. Reason: %s' % self.SOCKS5_ERRORS.get(reply, "Unknown error"))
                    return False

                if address_type == 0x1: # handle IPv4 address
                    self.bound_address, self.bound_port = socket.inet_ntoa(data[4:8]),  
                                                           struct.unpack('>H', data[8:10])[0]
                elif address_type == 0x3: # handle domain name
                    dns_name_len = ord(data[4:5])
                    self.bound_address, self.bound_port = data[5:dns_name_len],  
                                                          struct.unpack('>H', data[(5+dns_name_len):(5+dns_name_len+2)])[0]
                elif address_type == 0x4: # handle Ipv6 address
                    self.bound_address, self.bound_port = socket.inet_ntop(socket.AF_INET6, data[4:20]),  
                                                                       struct.unpack('>H', data[20:22])[0]

                self.protocol_state = 'connection_verified'
                return True

        def connectionMade(self):
            self.noteTime('CONNECTED')
            self.noteTime('NEGOTIATE_AUTH_METHOD')
            self.negotiateAuthenticationMethod()

        def dataReceived(self, data):
            self.buf += data

            if self.protocol_state == 'do_auth':
                self.authenticate(data)
            elif self.protocol_state == 'check_auth':
                self.checkAuth(data)

            if self.protocol_state == 'authenticated':
                host = self.postHandshakeEndpoint._host
                port = self.postHandshakeEndpoint._port
                self.sendRelayRequest(host, port)
            elif self.protocol_state == 'connection_requested':
                if self.verifySocksReply(data):
                    self.setupRelay()


    class SOCKSv4ClientProtocol(SOCKSClientProtocol):
        SOCKS4_ERRORS = {
            0x5B: "Request rejected or failed",
            0x5C: "Request rejected because SOCKS server cannot connect to identd on the client",
            0x5D: "Request rejected because the client program and identd report different user-ids"
        }
        def sendRelayRequest(self, host, port):
            username = self.proxy_config['version_specific']['username']
            ver, cmd, username = 0x4, 0x1, [b'\x00', username.encode()+b'\x00'][not not username]
            try:
                addr = socket.inet_aton(host)
            except socket.error:
                self.abort('Not a valid IPv4 address.')
                return False
            msg = struct.pack('!BBH', ver, cmd, port) + addr + username
            self.transport.write(msg)
            self.noteTime('REQUEST')

        def verifySocksReply(self, data):
            """
            Return True on success and False on need-more-data or error.
            In the case of an error, the connection is closed and the
            handshakeDone errback is invoked with a SOCKSError exception
            before False is returned.
            """
            if len(data) < 8:
                return False
            if ord(data[0]) != 0x0:
                self.abort('Expected 0 bytes')
                return False
            status = ord(data[1])
            if status != 0x5a:
                self.abort('Relay request failed. Reason=%s.' % self.SOCKS4_ERRORS.get(data[0], 'Unknown error'))
                return False
            return True

        def connectionMade(self):
            self.noteTime('CONNECT')
            self.noteTime('NEGOTIATE')
            self.sendRelayRequest(self.postHandshakeEndpoint._host, self.postHandshakeEndpoint._port)

        def dataReceived(self, data):
            self.buf += data
            if self.verifySocksReply(data):
                self.setupRelay()

    class SOCKSv4aClientProtocol(SOCKSv4ClientProtocol):
        '''Only extends SOCKS 4 to remotely resolve hostnames.'''

        def sendRelayRequest(self, host, port):
            username = self.proxy_config['version_specific']['username']
            ver, cmd, username = 0x4, 0x1, [b'\x00', username.encode()+b'\x00'][not not username]
            try:
                addr = socket.inet_aton(host)
            except socket.error:
                addr = '\x00\x00\x00\x01'
                dnsname = '%s\x00' % host
                msg = struct.pack('!BBH', ver, cmd, port) + addr + username + dnsname
            else:
                msg = struct.pack('!BBH', ver, cmd, port) + addr + username
            self.transport.write(msg)
            self.noteTime('REQUEST')

    class SOCKSClientFactory(ClientFactory):

        def __init__(self, proxy_config):
            self.proxy_config = proxy_config
            if self.proxy_config['version'] == '4':
                self.protocol = SOCKSv4ClientProtocol
            elif self.proxy_config['version'] == '4a':
                self.protocol = SOCKSv4aClientProtocol
            elif self.proxy_config['version'] == '5':
                self.protocol = SOCKSv5ClientProtocol

        def buildProtocol(self, addr):
            r = ClientFactory.buildProtocol(self, addr)
            r.proxy_config = self.proxy_config
            r.postHandshakeEndpoint = self.postHandshakeEndpoint
            r.postHandshakeFactory = self.postHandshakeFactory
            r.handshakeDone = self.handshakeDone
            r._timestamps = self._timestamps
            r._timer = self._timer
            return r

    class SOCKSWrapper(object):
        '''
        Generic class to wrap all 3 SOCKS protocol versions 4, 4a, 5 around a TCP connection
        '''
        implements(IStreamClientEndpoint)

        factory = SOCKSClientFactory

        def __init__(self, reactor, endpoint, proxy_config, timestamps=None):
            self._host = proxy_config['host']
            self._port = proxy_config['port']
            self._proxy_config = proxy_config

            self._reactor = reactor
            self._endpoint = endpoint
            self._timestamps = None
            self._timer = None
            if timestamps is not None:
                self._timestamps = timestamps
                self._timer = IReactorTime(reactor)

        def noteTime(self, event):
            if self._timer:
                self._timestamps[event] = self._timer.seconds()

        def connect(self, protocolFactory):
            """
            Return a deferred firing when the SOCKS connection is established.
            """

            def createWrappingFactory(f):
                """
                Wrap creation of _WrappingFactory since __init__() doesn't
                take a canceller as of Twisted 12.1 or something.
                """
                if len(inspect.getargspec(_WrappingFactory.__init__)[0]) == 3:
                    def _canceller(deferred):
                        connector.stopConnecting()
                        deferred.errback(
                            error.ConnectingCancelledError(
                                connector.getDestination()))
                    return _WrappingFactory(f, _canceller)
                else:                           # Twisted >= 12.1.
                    return _WrappingFactory(f)

            self.noteTime('START')
            try:
                # Connect with an intermediate SOCKS factory/protocol,
                # which then hands control to the provided protocolFactory
                # once a SOCKS connection has been established.
                f = self.factory(self._proxy_config)

                f.postHandshakeEndpoint = self._endpoint
                f.postHandshakeFactory = protocolFactory
                f.handshakeDone = defer.Deferred()
                f._timestamps = self._timestamps
                f._timer = self._timer
                wf = createWrappingFactory(f)
                self._reactor.connectTCP(self._host, self._port, wf)
                self.noteTime('SOCKET')
                return f.handshakeDone
            except:
                return defer.fail()

You can use the module for HTTP connection endpoints somehow like that

    :::python
    #!/usr/bin/env python

    # Copyright (c) 2011-2013, The Tor Project
    # See LICENSE for the license.

    import sys
    from urlparse import urlparse
    from twisted.internet import reactor, endpoints
    from socksclient import SOCKSv4ClientProtocol, SOCKSWrapper
    from twisted.web import client

    class TestClass:
        def __init__(self):
            self.npages = 0
            self.timestamps = {}

        def wrappercb(self, proxy):
            print "connected to proxy", proxy

        def clientcb(self, content):
            print "ok, got: %s" % content[:120]
            print "timetamps " + repr(self.timestamps)
            self.npages -= 1
            if self.npages == 0:
                reactor.stop()

        def sockswrapper(self, proxy_config, url):
            dest = urlparse(url)
            assert dest.port is not None, 'Must specify port number.'
            endpoint = endpoints.TCP4ClientEndpoint(reactor, dest.hostname, dest.port)
            return SOCKSWrapper(reactor, endpoint, proxy_config, timestamps=self.timestamps)


    def main():
        thing = TestClass()

        # Mandatory first argument is a URL to fetch over Tor (or whatever
        # SOCKS proxy that is running on localhost:9050).
        url = sys.argv[1]

        proxy_config = {
            'host': '127.0.0.1',
            'port': 1080,
            'version': '4',
            'version_specific': {
                'rdns': True, # Enforce resolving hostnames remotely (Only supported by version 4a and 5)
                'cmd': b'\x01', # this may be CONNECT, BIND and UDP in version 5. In 4 and 4a, it's always CONNECT or BIND
                'username': 'socksuser', # Enables simple username/password authentication mechanism in version 5
                'password': ''
            }
        }

        proxy_config2 = {
            'host': '212.224.92.182',
            'port': 7777,
            'version': '5',
            'version_specific': {
                'rdns': True, # Enforce resolving hostnames remotely (Only supported by version 4a and 5)
                'cmd': b'\x01', # this may be CONNECT, BIND and UDP in version 5. In 4 and 4a, it's always CONNECT or BIND
                'username': 'someuser', # Enables simple username/password authentication mechanism in version 5
                'password': 'somepass'
            }
        }
        # From http://fastproxyservers.org/socks5-servers.htm
        proxy_config3 = {
            'host': '202.84.44.129',
            'port': 1080,
            'version': '4',
            'version_specific': {
                'rdns': True, # Enforce resolving hostnames remotely (Only supported by version 4a and 5)
                'cmd': b'\x01', # this may be CONNECT, BIND and UDP in version 5. In 4 and 4a, it's always CONNECT or BIND
                'username': '', # Enables simple username/password authentication mechanism in version 5
                'password': ''
            }
        }

        f = client.HTTPClientFactory(url)
        f.deferred.addCallback(thing.clientcb)

        sw = thing.sockswrapper(proxy_config2, url)
        d = sw.connect(f)
        d.addCallback(thing.wrappercb)
        thing.npages += 1

        reactor.run()

    if '__main__' == __name__:
        main()
