Title: Reliable Cross Domain Requests when the User leaves the Page
Date: 2020-12-10 21:58
Category: JavaScript
Tags: Navigator.sendBeacon(), visibilitychange, onbeforeunload, cross domain request
Slug: reliable-cross-domain-requests-on-page-close
Author: Nikolai Tschacher

In this article I demonstrate how to reliably communicate any kind of data (in my case I need to transmit JSON data)
to a cross domain server after the user is about to end the browsing session by either:

- switching the focus to another page
- switching from the browser to another applicaton
- closing the tab
- closing the browser

or any other means of terminating or interrupting the current browsing session.

Mobile devices and desktop devices should be both supported.

Why do I have this very specific requirement?

I am in the process of developing a JavaScript analytics application
and I need to record user interactions and send those user interactions from any
website to my remote server.

I need to record user interactions up until the point where the user leaves the browsing session.

The ideal event for to use when the user is about to end the browsing session is to attach an event listener to `visibilitychange`:

```JavaScript
document.addEventListener("visibilitychange", function() {
  if (document.visibilityState === 'hidden') {
    // send data to my remote server somehow
    // lets suppose the server listens on http://localhost:3333
  }
})
```

This event fires when the user loses focus of the current window, the page visiblity becomes hidden.

However, the event `visibilitychange` is NOT FIRED when the user closes the tab or closes the entire browser. 
This is bad. We absolutely need to catch all the events that terminate or interrupt the session on the monitored page.

So in this blog article, we have to solve the following two problems:

1. Find an appropriate event that fires when the user interruptes or closes the current browsing session
2. Find a reliable mechanism to send JSON data to our remote server as soon as the above event occurs.

We have the following requirements:

+ Cross Domain Requests must be possible
+ CORS can be enabled on our server, thus CORS requests are allowed
+ Data transmission needs to be as reliable as possible. It would be very bad if recorded data is lost.

### Finding the correct event

As discussed above, `visibilitychange` is not sufficient for our purpose. This event is not fired when the user either 

- closes the browser
- closes the current tab

But we still want to store the recorded user interactions up to that point on our remote server.

### The test server

I use a simple express server to test my application. This is the server code:

```JavaScript
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const port = 3333;

app.use(express.json());
app.use(cors());
app.use(bodyParser.json({ limit: '2mb' }));
app.use(bodyParser.text());

app.post('/', (req, res) => {
  console.log(req.body);
  res.status(200).json({message: 'ok'});
});

app.get('/', (req, res) => {
  console.log(req.query);
  res.status(200).json({message: 'ok'});
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})
```

### Trying fetch() and XMLHttpRequest

Initially, I thought this would be an ideal fit for the rather new [fetch()](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) web requests library.

I tried the following:

```JavaScript

const data = { username: 'example' };

function postData(data) {
  fetch('http://localhost:3333', {
    method: 'POST', // or 'PUT'
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  .then(response => response.json())
  .then(data => {
    console.log('Success:', data);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}

postData(data);
```

and to my surprise, the request was not reliably sent on the events
`visibilitychange`, `onbeforeunload`, `onunload`.

So for example, the following code does NOT ALWAYS work:

```JavaScript
document.addEventListener("onbeforeunload", function() {
  postData({foo: "bar"});
})
```

Then I tried the good old `XMLHttpRequest` and my experiments showed that `XMLHttpRequest` was not more reliable!

I found the following explanation on MDN: https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon

> Ensuring that data has been sent during the unloading of a document has traditionally been difficult, because user agents typically ignore asynchronous XMLHttpRequests made in an unload handler.

They suggest to use `Navigator.sendBeacon()` instead. MDN promises:

> The navigator.sendBeacon() method asynchronously sends a small amount of data over HTTP to a web server. It’s intended to be used in combination with the visibilitychange event (but not with the unload and beforeunload events).

This is our salvation! We can just use `Navigator.sendBeacon()`! This Api is exactly made for our use case!

However, after implementing `Navigator.sendBeacon()`, that didn't work at all!

My OS (Linux) and the most recent chrome browser sometimes would not send requests fired with `Navigator.sendBeacon()`.

This is the code snippet I tried and which is supposed to work [according to MDN](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon).

```JavaScript
document.addEventListener("visibilitychange", function() {
  console.log('visibilitychange fired');
  if (document.visibilityState === 'hidden') {
    navigator.sendBeacon('http://localhost:3333', 'visibilitychange: ' + new Date());
  }
})
```

However, the event `visibilitychange` is not fired when a tab is closed or when the browser is closed. But we absolutely need to send 
data whenever a user closes the current page. Therefore, we cannot use the event `visibilitychange`. 

However, when we use the event `onbeforeunload`, the following code is not guaranteed to work. More accurately: With my system configuration, the data is never sent.

```JavaScript
document.addEventListener("onbeforeunload", function() {
  console.log('onbeforeunload fired');
  navigator.sendBeacon('http://localhost:3333', 'onbeforeunload: ' + new Date());
})
```

To get a better understanding of the different events in the DOM, I suggest to read [this blog article](https://www.igvita.com/2015/11/20/dont-lose-user-and-app-state-use-page-visibility/).

I found the [following explanation](https://volument.com/blog/sendbeacon-is-broken) from a company whose main product is an analytics applicaton. They need a very reliable way to transmit data in a cross domain fashion.

Their conclusion is the following:

> On this sample set, about 30% of browsers that claim to support the beacon API failed to deliver the data to our servers when the page was closed, which is the whole purpose of the sendBeacon call.

All those fancy web Api's

- fetch()
- XMLHttpRequest
- Navigator.sendBeacon()

are horribly unreliable and broken if you want to reliably send data at the end of a browsing sessions on the events
`visibilitychange`, `onbeforeunload` or `onunload`.

[This discussion](https://github.com/mdn/sprints/issues/3722) on Github explains in depth why this is the case.

### Solution: Reliable cross domain communication with `<img>` tags

The above article (https://volument.com/blog/sendbeacon-is-broken) suggested to use `<img>` tags to transmit data instead!

I thought, whatever, let's give it a try:

The idea is to use the Image object to send my analytics data:

```JavaScript
var image = new Image;
image.src = 'http://localhost:3333?d=' + 'v'.repeat(7700);
```

After some experiments, I came up with the following restrictions:

- Not more than ~7700 bytes of GET payload allowed for the `<img>` `src` attribute
- url data needs to be url safe base64 encoded

However, the image requests were fired very reliably! I didn't have the previous issues anymore. 
Requests wouldn't magically disappear. This is exactly what I wanted. Furthermore, `<img>` tags probably 
are supported on way more browsers than the relatively new `Navigator.sendBeacon()` Api.

But, since my application sometimes has more than 7700 bytes (even in compressed form) to send,
I needed to send data incrementally.

As soon as lets say 15kb of bytes of data is collected, make the first <img> request. When the next 15kb of data is available, send the second batch.

Send the rest of recorded user interaction on end when the event `visibilitychange` is triggered.

We just have to keep track of this web session with an counter, such that the server can merge the session as soon
as it is finished.