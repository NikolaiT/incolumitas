Title: Browser based Port Scanning and a Dive into the Chromium Code Base
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

### The Idea

When creating a WebSocket object `var ws = new WebSocket("ws://127.0.0.1:8888/")` that points to local HTTP server started with the command `python -m http.server --bind 127.0.0.1 8888`, we get the JavaScript error message in the console:

```text
WebSocket connection to 'ws://127.0.0.1:8888/' failed: Error during WebSocket handshake: Unexpected response code: 404
```

When creating a WebSocket object `var ws = new WebSocket("ws://127.0.0.1:8889/")` with a URL that points to non-existant service on port 8889 , we get the following error in the developer console

```text
WebSocket connection to 'ws://127.0.0.1:8889/' failed: Error in connection establishment: net::ERR_CONNECTION_REFUSED
```

Boom. Problem solved. We can distinguish based on error message whether a port is open or not.

Not so fast. 

When trying to grab the error details with 

```JavaScript
// outputs: Error: null
var errorMessage = null;
try {
  var ws = new WebSocket("ws://127.0.0.1:8889/")
} catch (err) {
  // this code will never run
  errorMessage = err.toString();
}
  console.log('Error: ' + errorMessage)
```

we get a meager output of `Error: null`. The error that is shown in the console, is not accessible via JavaScript!

But since we are plenty smart, maybe try to get error details with `WebSocket.onerror` event handler:

```JavaScript
var ws = new WebSocket("ws://127.0.0.1:8889/")

ws.onerror = function(error) {
  console.error("WebSocket error observed:", error);
};
```

However, the `error` object does not differ depending on the two cases. Based on the `error` object, it is not possible to determine 
whether the port was open or not!

The same applies to `<img>` tags.

The following code will not reveal error information that helps us to infer whether the port was open or not:

```JavaScript
var img = new Image();

img.onerror = function (error) {
  console.error("Image error observed:", error);
};

img.onload = img.onerror;
img.src = "http://127.0.0.1:8889/";
```

There is simply not much information in the `onerror` kind of event messages.

What to do? 

Yes you guessed correctly.

We will check if we can detect open ports by measuring the response times ;)

### About Timing things in JavaScript

One problem is that `performance.now()` has reduced accuracy: [Hacker news article](https://news.ycombinator.com/item?id=16103270) about `performance.now()` accuracy.

The following snippet tests `performance.now()` accuracy:

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

To measure network and socket timeouts, we need single digit millisecond accuracy. According to the hacker news link above, chrome has accuracy of **accurate to 100us**. This is more than enough for our use case.

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

This is very weird and inconsistent behavior. It seems like there is only a consistent pattern in the first 7 requests, then the open/closed property doesn't seem to correlate anymore.

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

What we see here, is that closed ports seem to be taking more time than open ports. 

[Those slides](https://datatracker.ietf.org/meeting/96/materials/slides-96-saag-1/) explain exactly what counter measures are employed against browser based port scanning. There is definitely throttling happening here.

### Statistics with Image Tags

Port scanning with Image tags on Chrome with `N=20` and service `python -m http.server --bind localhost 8888`.

<canvas id="chromeImage" width="600" height="400"></canvas>
<script>
var options = {
  type: 'line',
  data: {
    labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    datasets: [
	    {
	      label: 'Open Port Timings',
	      data: [14.095,7.125,8.28,6.8,7.2,20.73,8.78,9.685,10.2,6.895,8.265,7.17,7.17,9.405,27.39,8.255,16.39,6.69,12.01,7.56],
      	borderWidth: 1,
        borderColor: 'rgba(255, 0, 0, 0.3)',
    	},	
			{
				label: 'Closed Port Timings',
				data: [5.065,5.235,3.59,3.72,4.775,7.215,11.62,6.74,3.785,3.81,7.875,3.725,5.33,4.325,5.765,3.785,3.865,4.42,3.675,3.44],
				borderWidth: 1,
        borderColor: 'rgba(0, 255, 0, 0.3)',
			}
		]
  },
  options: {
  	scales: {
    	yAxes: [{
        ticks: {
					reverse: false
        }
      }]
    }
  }
}
var ctx = document.getElementById('chromeImage').getContext('2d');
new Chart(ctx, options);
</script>

Another sample of port scanning with Image tags on Chrome with `N=30` with a different service than `python -m http.server --bind localhost 8888`.

<canvas id="chromeImage2" width="600" height="400"></canvas>
<script>
var options = {
  type: 'line',
  data: {
    labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
    datasets: [
	    {
	      label: 'Open Port Timings',
	      data: [5.75,4.705,4.6,4.905,4.23,4.155,4.13,8.07,6.185,5.46,4.095,4.695,4.01,7.535,3.745,4.27,4.305,4.43,4.475,4.185,4.035,4.14,3.85,4.11,3.985,4.035,4.02,3.885,4,3.895],
      	borderWidth: 1,
        borderColor: 'rgba(255, 0, 0, 0.3)',
    	},	
			{
				label: 'Closed Port Timings',
				data: [4.73,3.455,2.78,3.495,3.095,2.785,2.885,6.165,2.75,2.755,4.29,2.905,2.82,24.025,2.705,3.55,2.735,2.68,2.81,3.13,2.89,3.06,2.825,3.44,2.575,2.8,3.07,3.18,4.005,2.845],
				borderWidth: 1,
        borderColor: 'rgba(0, 255, 0, 0.3)',
			}
		]
  },
  options: {
  	scales: {
    	yAxes: [{
        ticks: {
					reverse: false
        }
      }]
    }
  }
}
var ctx = document.getElementById('chromeImage2').getContext('2d');
new Chart(ctx, options);
</script>

Another a third example of port scanning with Image tags on Chrome with `N=30` with `nginx` running as a service on `localhost:3333`.

<canvas id="chromeImageNginx" width="600" height="400"></canvas>
<script>
var options = {
  type: 'line',
  data: {
    labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
    datasets: [
	    {
	      label: 'Open Port Timings',
	      data: [9.69,5.635,6.295,5.76,6.235,6.49,13.84,6.815,7.58,5.13,7.47,6.135,5.83,7.015,10.5,12.74,7.24,4.795,4.47,7.07,4.075,4.285,17.995,4.865,5.075,4.48,4.52,4.68,4.585,6.03],
      	borderWidth: 1,
        borderColor: 'rgba(255, 0, 0, 0.3)',
    	},
			{
				label: 'Closed Port Timings',
				data: [5.785,5.445,3.725,4.795,3.69,11.235,4.315,3.59,7.745,3.31,2.89,3.83,3.345,3.625,5.955,3.91,4.68,2.91,2.805,4.545,3.145,7.875,3.905,4.4,2.83,2.965,3.125,2.89,17.82,3.68],
				borderWidth: 1,
        borderColor: 'rgba(0, 255, 0, 0.3)',
			}
		]
  },
  options: {
  	scales: {
    	yAxes: [{
        ticks: {
					reverse: false
        }
      }]
    }
  }
}
var ctx = document.getElementById('chromeImageNginx').getContext('2d');
new Chart(ctx, options);
</script>


But what happens when the scanned service (open port) is not a HTTP server? What if it is, lets say a unrelated TCP service?
This time, we will simply use `netcat` to simulate an arbitrary TCP service. There is no response from `netcat` on any incoming message.

We use the command `ncat -l 4444 --keep-open --exec "/bin/cat"` to launch a simple echo server.

<canvas id="netcatExample" width="600" height="400"></canvas>
<script>
var options = {
  type: 'line',
  data: {
    labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
    datasets: [
	    {
	      label: 'Open Port Timings',
	      data: [9.94,5.955,6.285,5.495,9.68,5.665,6.715,9.57,9.135,6.835,6.165,6.18,5.21,5.64,5.415,5.065,5.465,5.21,5.265,13.48,6.78,6.855,5.25,7.405,5.435,4.93,5.695,5.125,5.77,4.93],
      	borderWidth: 1,
        borderColor: 'rgba(255, 0, 0, 0.3)',
    	},
			{
				label: 'Closed Port Timings',
				data: [4.805,4.255,4.055,7.98,4.07,4.31,3.75,3.67,4.775,4.385,4.165,4.51,3.73,3.825,3.925,3.82,4,6.3,3.765,5.615,5.59,4.18,3.855,5.805,5.155,8.605,3.65,3.815,3.72,4.325],
				borderWidth: 1,
        borderColor: 'rgba(0, 255, 0, 0.3)',
			}
		]
  },
  options: {
  	scales: {
    	yAxes: [{
        ticks: {
					reverse: false
        }
      }]
    }
  }
}
var ctx = document.getElementById('netcatExample').getContext('2d');
new Chart(ctx, options);
</script>

### Conclusion

As the plots above demonstrate, it does not matter if the scanned service is a toy HTTP server, real HTTP server (nginx) or any TCP service (netcat), we will see that the measured timings are significantly longer on open services!

### Other Port Scanning Techniques

The script below conducts port scanning with image tags and the `fetch()` API. 
Another possibility would be to use `<iframe>` or `<script>` tags.

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