Title: Browser based port scanning and a dive into the Chromium code base
Date: 2021-01-10 16:06
Category: Security
Tags: browser, port scanning, JavaScript
Slug: browser-based-port-scanning
Author: Nikolai Tschacher
Summary: In this article, a simple technique to conduct port scanning from within the browser is developed. Modern JavaScript is used. 

### Goal

The goal of this article is to conduct port scanning with JavaScript. The domain `localhost` should be scanned. It is assumed, that our origin is a `https` site, such as for example `https://incolumitas.com`.

A Ubuntu 18.04 Linux system with a recent chrome browser will be used (Chrome/86.0.4240.75).

Port scanning from within the browser [recently caused quite some uproar](https://news.ycombinator.com/item?id=23246170), when a security researcher observed that Ebay is port scanning the local network. Here is another article that goes into [much more technical detail](https://blog.nem.ec/2020/05/24/ebay-port-scanning/) as the previous one and tries to debug and reverse engineer the port scanning source code from ThreatMatrix.

### Resources

One problem is that `performance.now()` has reduced accuracy: [Hacker news article](https://news.ycombinator.com/item?id=16103270) about `performance.now()` accuracy.

### Test performance.now() resolution

```JavaScript
const results = []
let then = 0
for(let i = 0; i < 500; i++) {
    const now = performance.now()
    if (Math.abs(now - then) > 1e-6) {
        results.push(now)
        then = now
    }
}
console.log(results.join("\n"))
```

Based on the script above, it seems that the accuracy is fine grained enough to test network timing.

To measure network and socket timeouts, we need single digit millisecond accuracy. According to the hacker news link above, chrome has accuracy of *accurate to 100us*. This is more than enough.

### Port Scanning with Web Sockets

My first try was to use [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) to conduct localhost port scanning. I came up with the following JavaScript that measures WebSocket connection timeouts:

```JavaScript
// start local server with
// python -m http.server --bind 127.0.0.1 8888
var checkPort = function(port) {
  var t0 = performance.now()
  // a random appendix to the URL to prevent caching
  var random = Math.random().toString().replace('0.', '').slice(0, 7)
  var ws = new WebSocket("ws://127.0.0.1:" + port + '/' + random)
  var status = null;

  ws.onerror = function() {
    status = 'onerror: ' + (performance.now() - t0)
  }

  ws.onclose = function() {
    status = 'onclose: ' + (performance.now() - t0)
  }
  
  setTimeout(() => {
    console.log(status)
    ws.close()
  }, 200)
}
checkPort(8888)
```

The idea is the following: I want to test if the above snippet yields significantly different timeouts for a URL that 
points to a open TCP service compared to URL with a port where no service is running.

First, I started a simple HTTP server on the port 8888 with the command 

```bash
python -m http.server --bind 127.0.0.1 8888
```

The I launched the browser, navigated to `incolumitas.com` and pasted the above script into the console.

When creating a WebSocket object (`var ws = new WebSocket("ws://127.0.0.1:8888/")`) that points to a normal and running HTTP server `ws://127.0.0.1:8888/`, we get the JavaScript error message:

```text
WebSocket connection to 'ws://127.0.0.1:8888/' failed: Error during WebSocket handshake: Unexpected response code: 404
```

When creating a WebSocket object (`var ws = new WebSocket("ws://127.0.0.1:8889/")`) with a URL that points to a closed port `ws://127.0.0.1:8889/`, we get:

```text
WebSocket connection to 'ws://127.0.0.1:8889/' failed: Error in connection establishment: net::ERR_CONNECTION_REFUSED
```

Unfortunately, we cannot access the Error message in a try/catch block. The browser does not give us error information :/

After repeating this step 10 times (open browser, navigate to site, paste code, close browser), I got the following timeouts :

```
onclose: 13.179999999920256
onclose: 9.160000000520085
onclose: 17.110000000684522
onclose: 7.840000000214786
onclose: 8.205000000089058
onclose: 15.51000000017666
onclose: 7.150000000365253
onclose: 13.845000000401342
onclose: 17.30500000030588
onclose: 9.01499999963562
```

And then I did the same process with the port 8889, where no service is running. I got the following timeouts after 10 runs:

```
onclose: 7.255000000441214
onclose: 5.694999999832362
onclose: 8.78999999986263
onclose: 6.68500000028871
onclose: 11.080000000220025
onclose: 6.844999999884749
onclose: 8.659999999508727
onclose: 7.13999999970838
onclose: 8.420000000114669
onclose: 5.494999999427819
```

There is a slight difference in timings, but it's not really significant. Based on timing, you cannot really distinguish whether a port is open or not.

But why did I do this process manually?  Why did I restart the browser after each measurement taken?

The reason is, that Chromium  makes it impossible to determine whether a port is open or closed, when trying to create WebSockets to intentionally invalid services.

Furthermore, once a socket is created for a `(host, port)` pair, this socket is shared among normal HTTP connections. The document ["WebSocket Throttling Design"]((https://docs.google.com/document/d/1a8sUFQsbN5uve7ziW61ATkrFr3o9A-Tiyw8ig6T3puA/edit#)) states:

> The new WebSocket stack re-uses the HTTP stack for its handshake.

and 

> The major issue with this design as it stands is that proxy connections for WebSockets share the ConnectionPoolManager with direct connections.

### A Dive into the Chromium WebSocket Source Code

For example, you can look into the [Chrome WebSocket source code](https://chromium.googlesource.com/chromium/src/+/master/net/websockets/websocket_stream.cc):

Those are interesting sections in the file `websocket_stream.cc`. There a timeout interval variable is defined. The mechanism is intended *to make it hard for JavaScript programs to recognize the timeout cause*.

```C++
// The timeout duration of WebSocket handshake.
// It is defined as the same value as the TCP connection timeout value in
// net/socket/websocket_transport_client_socket_pool.cc to make it hard for
// JavaScript programs to recognize the timeout cause.
const int kHandshakeTimeoutIntervalInSeconds = 240;
```

This is the `Start()` method that starts a WebSocket connection.

```C++
void Start(std::unique_ptr<base::OneShotTimer> timer) {
  DCHECK(timer);
  base::TimeDelta timeout(base::TimeDelta::FromSeconds(
      kHandshakeTimeoutIntervalInSeconds));
  timer_ = std::move(timer);
  timer_->Start(FROM_HERE, timeout,
                base::BindOnce(&WebSocketStreamRequestImpl::OnTimeout,
                                base::Unretained(this)));
  url_request_->Start();
}
```

So what kind of timer is in the variable `timer_` ? 

```C++
  // A timer for handshake timeout.
  std::unique_ptr<base::OneShotTimer> timer_;
```

A brief look into [/master/base/timer/timer.h](https://chromium.googlesource.com/chromium/src/+/master/base/timer/timer.h) reveals what this timer does: 

> As the names suggest, OneShotTimer calls you back once after a time delay expires.

Therefore, this time is used to fire when a timeout occurs in the WebSocket connection.


Then, we have a look into [websocket_transport_client_socket_pool.cc](https://github.com/chromium/chromium/blob/master/net/socket/websocket_transport_client_socket_pool.cc) and we see the method 

```C++
void WebSocketTransportClientSocketPool::InvokeUserCallbackLater(
    ClientSocketHandle* handle,
    CompletionOnceCallback callback,
    int rv) {
  DCHECK(!pending_callbacks_.count(handle));
  pending_callbacks_.insert(handle);
  base::ThreadTaskRunnerHandle::Get()->PostTask(
      FROM_HERE,
      base::BindOnce(&WebSocketTransportClientSocketPool::InvokeUserCallback,
                     weak_factory_.GetWeakPtr(), handle, std::move(callback),
                     rv));
}
```

This method `InvokeUserCallbackLater()` is invoked in all the cases:

- When a WebSocket connection is successful
- when a WebSocket connection is unsuccessful, because the port is closed,
- when a WebSocket connection is unsuccessful, because the service does not speak the same protocol...

#### Top Down Approach

However, we are interested in the logic that aborts the control flow when the connection could not be established. 

Put differently, where does the chrome source code decide that on this port is not running a valid web socket service?

So we have to scan the chrome [WebSocket source code](https://github.com/chromium/chromium/tree/master/net/websockets) for the generation of this error message: `Error during WebSocket handshake: Unexpected response code: 404`.

After a quick search in the [GitHub chrome source code mirror](https://github.com/chromium/chromium/), we find the location to be in the file [websocket_basic_handshake_stream.cc]() on line 464:

```C++
switch (response_code) {
  case HTTP_SWITCHING_PROTOCOLS:
    return ValidateUpgradeResponse(headers);

  // We need to pass these through for authentication to work.
  case HTTP_UNAUTHORIZED:
  case HTTP_PROXY_AUTHENTICATION_REQUIRED:
    return OK;

  // Other status codes are potentially risky (see the warnings in the
  // WHATWG WebSocket API spec) and so are dropped by default.
  default:
    // A WebSocket server cannot be using HTTP/0.9, so if we see version
    // 0.9, it means the response was garbage.
    // Reporting "Unexpected response code: 200" in this case is not
    // helpful, so use a different error message.
    if (headers->GetHttpVersion() == HttpVersion(0, 9)) {
      OnFailure("Error during WebSocket handshake: Invalid status line",
                ERR_FAILED, base::nullopt);
    } else {
      OnFailure(base::StringPrintf("Error during WebSocket handshake: "
                                    "Unexpected response code: %d",
                                    headers->response_code()),
                ERR_FAILED, headers->response_code());
    }
    result_ = HandshakeResult::INVALID_STATUS;
    return ERR_INVALID_RESPONSE;
}
```

The method `OnFailure()` is called, which is defined in the file [websocket_stream.cc](https://chromium.googlesource.com/chromium/src/+/master/net/websockets/websocket_stream.cc) on line 151:

```C++
void OnFailure(const std::string& message,
                int net_error,
                base::Optional<int> response_code) override {
  if (api_delegate_)
    api_delegate_->OnFailure(message, net_error, response_code);
  failure_message_ = message;
  failure_net_error_ = net_error;
  failure_response_code_ = response_code;
}
```

It does not look like the method `OnFailure()` is delayed or fired with a timer. Therefore, it should be possible to notify timing differences.

### Statistically significant Tests

Well, now we have learned the following two things:

+ When we reuse sockets in chrome, we will get skewed results. It is mandatory to either restart the browser, or maybe it suffices to close the socket with `ws.close()`. 
+ `OnFailure()` is not artificially delayed. Therefore, there should be slight differences in timing when making a WebSocket connection to a closed port compared to a open port.

The following program attempts to connect 150 times to a open port and 150 times to a (likely) closed port.

After each attempt, the socket is closed, before a new connection is made.

```JavaScript
var timePort = function(port) {
  return new Promise((resolve, reject) => {
    var t0 = performance.now()
    // a random appendix to the URL to prevent caching
    var random = Math.random().toString().replace('0.', '').slice(0, 7)
    var ws = new WebSocket("ws://127.0.0.1:" + port + '/' + random)
  
    ws.onerror = function() {
      var elapsed = (performance.now() - t0)
      // close the socket before we return
      ws.close()
      resolve(parseFloat(elapsed.toFixed(3)))
    }
  })
}

const port = 8888;
const N = 30;

(async () => {
  var timings = [];
  for (var i = 0; i < N; i++) {
    timings.push(await timePort(port))
  }
  timings.sort((a, b) => a - b);
  console.log(timings)
})();
```

The response times are plotted in a histogram, to visually show that there is a significant difference in response times. I used chartjs:

<script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"></script>
<canvas id="chartJSContainer" width="600" height="400"></canvas>
<script>
var options = {
  type: 'line',
  data: {
    labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
    datasets: [
	    {
	      label: 'Open Port Timings',
	      data: [11.345, 11.525, 11.555, 11.77, 12.11, 12.86, 13.84, 16.055, 38.735, 43.125, 75.77, 91.45, 535.255, 940.86, 1100.415, 1568.03, 1702.405, 1768.775, 1866.21, 2055.645, 2437.4, 2690.86, 3011.965, 3118.07, 3157.795, 3471.12, 4395.175, 4439.105, 4596.1, 4986.875],
      	borderWidth: 1,
        borderColor: 'rgba(255, 0, 0, 0.3)',
    	},	
			{
				label: 'Closed Port Timings',
				data: [7.86, 10.035, 10.135, 10.275, 10.42, 10.74, 11.45, 17.12, 23.925, 25.935, 80.505, 212.785, 376.305, 663.645, 961.385, 1093.705, 1659.905, 1734.135, 2137.24, 3128.94, 3190.47, 3231.12, 3257.18, 3812.22, 3993.54, 4244.75, 4251.375, 4472.14, 4707.59, 4746.89],
				borderWidth: 1,
        borderColor: 'rgba(0, 255, 0, 0.3)',
			}
		]
  },
  options: {
  	scales: {
    	yAxes: [{
      type: 'logarithmic',
        ticks: {
					reverse: false
        }
      }]
    }
  }
}
var ctx = document.getElementById('chartJSContainer').getContext('2d');
new Chart(ctx, options);
</script>

And then I did the same for the Firefox browser (but only with 12 measurements):

<canvas id="chartFirefox" width="600" height="400"></canvas>
<script>
var options = {
  type: 'line',
  data: {
    labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    datasets: [
	    {
	      label: 'Firefox: Open Port Timings',
	      data: [ 48, 334, 501, 752, 1165, 1601, 2447, 3659, 5481, 8211, 12318, 18464],
      	borderWidth: 1,
        borderColor: 'rgba(255, 0, 0, 0.3)',
    	},
			{
				label: 'Firefox: Closed Port Timings',
				data: [ 34, 368, 551, 817, 1215, 1820, 2719, 4071, 6102, 9644, 13714, 20561],
				borderWidth: 1,
        borderColor: 'rgba(0, 255, 0, 0.3)',
			}
		]
  },
  options: {
  	scales: {
    	yAxes: [{
      type: 'logarithmic',
        ticks: {
					reverse: false
        }
      }]
    }
  }
}
var ctx = document.getElementById('chartFirefox').getContext('2d');
new Chart(ctx, options);
</script>

### Port Scanning Script

The script below conducts port scanning with image tags and the `fetch()` API.

```JavaScript
// start server with
// python -m http.server --bind localhost 8888

var sampleSize = 5;

var checkPort = function (url, how) {
  return new Promise((resolve) => {
    // do not allow any form of caching
    const randomUrl = url + '/' + Math.random().toString().replace('0.', '') + '.png';
    if (!how) {
      how = 'fetch';
    }

    if (how === 'image') {
      var img = new Image();
      var t0 = performance.now();
      img.onerror = function () {
        resolve((performance.now() - t0))
      };
      img.src = randomUrl;
    } else if (how === 'fetch') {
      var t0 = performance.now();
      var myRequest = new Request(randomUrl, {
        method: 'HEAD',
        mode: 'no-cors',
      });

      fetch(myRequest).then((res) => {
        // never reached
        resolve((performance.now() - t0))
      }).catch((err) => {
        resolve((performance.now() - t0))
      })
    }
  })
};

// statistic significant sample
async function runSample(url) {
  let requests = [];
  for (let i = 0; i < sampleSize; i++) {
    requests.push(checkPort(url, 'fetch'))
  }
  var times = await Promise.all(requests);
  return times.reduce((a, b) => a + b) / times.length
}

(async () => {
  // this port is up
  var averageTimeOpen = await runSample('http://localhost:9222')

  // this port is down
  var averageTimeClosed = await runSample('http://localhost:9873')

  console.log('Average Time of Open Port: ' + averageTimeOpen)
  console.log('Average Time of Closed Port: ' + averageTimeClosed)
})();
```

### Analysis

For some strange reason, the above script gives very confusing results in Chrome and Firefox.

The timing results are not consistent, therefore we cannot make a statement whether the port is open or not. 