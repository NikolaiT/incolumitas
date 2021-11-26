## Experimental Setup

### Proxy Server

Proxy Software: https://github.com/NikolaiT/3proxy-docker

`node proxy_server.js http://test:kvi42VVs74@137.184.169.202:9799`

`chromium-browser --proxy-server=http://localhost:8947 https://bot.incolumitas.com/proxy_detect.html`

Results

https://abs.incolumitas.com/showFile?fileName=proxy_test_4-10_137.184.169.202_2021-11-11T20:15:22.383Z.json
https://abs.incolumitas.com/showFile?fileName=proxy_test_4-10_137.184.169.202_2021-11-11T20:15:50.297Z.json
https://abs.incolumitas.com/showFile?fileName=proxy_test_4-10_137.184.169.202_2021-11-11T20:16:08.731Z.json
https://abs.incolumitas.com/showFile?fileName=proxy_test_4-10_137.184.169.202_2021-11-11T20:16:32.489Z.json

## Another Method

By attempting to make a connection to an IP address at which there is known to be no server. The proxy will accept the connection and then attempt to proxy it on. When the proxy finds no server to accept the connection it may return an error message or simply close the connection to the client. This difference in behavior is simple to detect. For example, most web browsers will generate a browser created error page in the case where they cannot connect to an HTTP server but will return a different error in the case where the connection is accepted and then closed.

```JavaScript
(function() {
  var t0 = performance.now();
  var t1 = null;
  var t_err = null;
  
  const socket = new WebSocket('wss://167.99.241.135:41544');
  
  socket.onerror = function (err) {
    console.log('onerror', err)
    t_err = performance.now();
  }
  
  socket.onopen = function () {
    console.log('onopen')
    t1 = performance.now();
  }
  
  setTimeout(function() {
    console.log('onopen', t1 - t0)
    console.log('onerror', t_err - t0)
  }, 1500);
})()
```

Test: Find out if and how the proxy fails. Is there a difference in error timeout?

Does the websocket even call the `onerror()` handler or does it call the `onopen()` handler?

https://github.com/NikolaiT/3proxy-docker


```JavaScript
var ts = []
for (var i = 0; i < 5; i++) {
  var t0 = performance.now()
  var img = new Image;

  img.onerror = function() {
    var elapsed = (performance.now() - t0)
    // close the socket before we return
    ts.push(parseFloat(elapsed.toFixed(3)))
  }

  var localhost = "https://0.0.0.0:" + (44435 + i) + "/sss34df.png";
  var urlInvalidPort = "https://167.99.241.135:" + (44435 + i) + "/sss34df.png";
  var urlInvalidRessource = "https://167.99.241.135/sss34df.png";

  img.src = localhost;
}
setTimeout(function() { console.log(ts) }, 1200);

// I am in Cologne / Germany

// Ressource does not exist! "https://IP:" + (44435 + i) + "/sdf.png";
// No DNS lookup, connection to port fails!

// With proxy in New York: [724.2, 726.4, 728.7, 728.9, 731.9, 733.5, 733.6]
//                          [733.5,739.4,751.2,753,753.1]	
//                          [707.6,724,725.3,739.4,741.6]	

// With proxy in Paris / France: [381.8, 385.5, 387.1, 413.6, 416.8, 417.5, 424.3]
//                               [286.1, 291, 304.3, 331.5, 332.7, 333.7, 343.7]
//                               [323.6,336.6,338.1,339.3,339.9]

// With proxy in Germany/Frankfurt: [195.6,197.2,220.5,227.3,236.9]	
//                                  [173.9,176.7,178.8,180.5,182.2]	
//                                  [181.3,191.6,193,195.5,201.8]	
//                                  [166.2,168.5,172.1,177,179.7]

// Without proxy to server in Germany: [42.6, 61.5, 61.8, 61.9, 66.9, 71.2, 76.6]
//                                     [54.5,55.4,71.2,72.4,73.3]	

// Without proxy to server in New York: [123.1, 130.2, 131.7, 134.9, 138.1]
//                                      [145, 145.5, 154.4, 155, 155.2]  

// Without proxy to server in Chile: [239.2, 246.6, 267, 277.6, 285.8]

// Without proxy to localhost: [17.1, 19.1, 20, 20.1, 20.2], 
// With proxy to localhost: [15.5, 19.8, 23.1, 23.2, 23.3]
```


### Using 0.0.0.0 as dest IP address, my Location: Germany / Cologne

```JavaScript
var ts = []
for (var i = 0; i < 5; i++) {
  var t0 = performance.now()
  var img = new Image;

  img.onerror = function() {
    var elapsed = (performance.now() - t0)
    ts.push(parseFloat(elapsed.toFixed(3)))
  }

  var localhost = "https://0.0.0.0:" + (44435 + i) + "/sss34df.png";
  img.src = localhost;
}
setTimeout(function() { console.log(ts) }, 1200);
```

https://en.wikipedia.org/wiki/0.0.0.0

Go to https://bot.incolumitas.com/proxy_detect.html

Without proxy to 0.0.0.0:  `[14.9, 17.9, 18.8, 18.9, 18.9], [10.2,13.6,14.8,15,15.3], [13.8,14.4,15.1,15.2,15.7]`

With proxy (Germany) to 0.0.0.0: `[93.2, 111.9, 125.5, 127.1, 132], [76.3,103.8,106,108.2,109.5], [106.9,110.1,112.9,114.9,119.1], [104.6,115.1,151,153.8,156.7], [89.6,91.2,97.5,100.7,102.6], [91.8,92.8,94.4,100.1,101.8]`

With proxy (France) to 0.0.0.0: `[221.5,221.7,226,229.5,230], [250.4,252.3,253.6,254.3,254.9], [197.7,228.6,234.4,243.9,252.4], [220.4,223,245.4,246.5,248.1], [210.2,210.7,231.6,248.3,266.4]`

IP `137.184.219.224`

With proxy (New York) to 0.0.0.0: `[268.7,268.9,271.3,273.1,273.6], [256,276.1,280.6,282.5,284.3], [264.6,269.4,270.2,281.9,282.9], [241.1,245.5,253.1,260.5,265.3], [255.6,260.2,261.9,265.4,265.5]`

## Latencies to Different special IPs

### Proxy in France, Chromium Browser

```
{"0.0.0.0":[[178.3,178.4,178.6,178.6,178.8]],"127.0.0.1":[[10,10.1,10.2,10.3,10.5]],"167.99.241.135":[[261.2,261.3,261.4,261.4,261.5]]}
```

https://abs.incolumitas.com/showFile?fileName=proxy_test_3-11_37.164.115.205_2021-11-13T14:30:14.291Z.json
https://abs.incolumitas.com/showFile?fileName=proxy_test_3-11_37.164.115.205_2021-11-13T14:30:49.572Z.json
https://abs.incolumitas.com/showFile?fileName=proxy_test_2-10_37.164.115.205_2021-11-13T14:34:12.917Z.json
https://abs.incolumitas.com/showFile?fileName=proxy_test_2-10_37.164.115.205_2021-11-13T14:34:30.389Z.json


### Chromium Browser, No Proxy

```
{"0.0.0.0":[3.8,3.9,3.9,3.9,3.9],"127.0.0.1":[4.4,4.5,4.6,4.7,4.7],"167.99.241.135":[28.4,28.5,28.6,28.6,28.7]}	
```

https://abs.incolumitas.com/showFile?fileName=proxy_test_0-8_80.187.122.64_2021-11-13T15:52:11.544Z.json

### Mobile Connection, Android Phone, No Proxy

```
```

### Mobile Connection, Android Phone, VPN

```
```

## Status Codes

https://httpbin.org/ip

https://httpbin.org/status/400

```JavaScript
fetch('https://httpbin.org/status/400')
  .then(response => response.text())
  .then(function(text) {
    console.log(text)
  })
  .catch(function (err) {
    console.log('err', err)
  })
```