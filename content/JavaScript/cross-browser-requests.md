Title: Reliable Cross Domain Requests when the User leaves the Page
Date: 2020-12-10 21:58
Modified: 2020-12-13 11:00
Category: JavaScript
Tags: navigator.sendBeacon(), visibilitychange, onbeforeunload, cross domain request
Slug: reliable-cross-domain-requests-on-page-close
Author: Nikolai Tschacher

In this article, I demonstrate how to reliably communicate JSON data to a cross domain server after the user is about to end or interrupt the browsing session by either:

- switching the focus to another page
- switching from the browser to another applicaton
- closing the tab
- closing the browser

or any other means of terminating or interrupting the current browsing session. Mobile devices and desktop devices should be equally supported.

Why do I have this very specific requirement?

I am in the process of developing a JavaScript analytics application
and I need to record user interactions and send those user interactions from any
website to my remote server.

Put differently: I need to record user interactions up until the point where the user leaves the browsing session. The ideal event for this scenario is to attach an event listener to `visibilitychange`:

```JavaScript
document.addEventListener("visibilitychange", function() {
  if (document.visibilityState === 'hidden') {
    localStorage.setItem('triggeredOnPageClose', new Date());
  }
})
```

This event fires when the user loses focus of the current window and the page visiblity becomes hidden, for example when the user changes the tab.

However, is the above event also triggered when the user closes the page or closes the entire browser? In order to verify this scenario, we 
actually have to write a piece of data to the [browser's local storage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage), because 
we have no meaningful way to debug the occurence of this event otherwise.

So let's to the following steps:

1. Navigate to https://example.org in your browser
2. Paste the above code snippet in your browser console
3. Close the tab by clicking on the `x`
4. Navigate again to https://example.org
5. Read the local storage with `localStorage.getItem('triggeredOnPageClose')`
6. If you see the correct date as output, then `visibilitychange` is fired when closing the tab
7. Repeat steps 1-6 but instead close the entire browser application

After doing the above steps, I could confirm that the event `visibilitychange` is also triggered when closing the tab or closing the browser.

So during this blog article, we have to find a reliable mechanism to send JSON data to our remote server as soon as the above event occurs.

We have the following requirements:

+ CORS can be enabled on our server, thus CORS requests are allowed
+ Data transmission needs to be as reliable as possible. It would be very bad if recorded data is lost

### The test server

I use a simple express server to test my application. Below is the server code. It doesn't need much explanation. 
CORS support is enabled and the server mostly logs request data when a request arrives.

```JavaScript
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const port = 3333;

app.use(express.json());
app.use(cors());
app.use(bodyParser.json({ limit: '2mb' }));
app.use(bodyParser.text());

app.get('/t', (req, res) => {
  console.log(req.query);
  res.sendFile(path.join(__dirname, '../public/test.jpg'));
});

app.post('/t', (req, res) => {
  console.log(req.query);
  console.log(req.body);
  res.status(200).send('ok');
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
});
```

Let's assume the server listens on `https://myserver.com` from here on.

### Experimenting with different browser web Api's

Initially, I thought that sending JSON data to another server would be an ideal fit for the rather new [fetch()](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) web requests library.

I tried the following:

```JavaScript
// Using XMLHttpRequest or fetch
const cdRequestMethod = 'fetch';

function userLeavesPage(s) {
  const url = 'https://myserver.com/t?event=' + s + '-' + cdRequestMethod + '-' + (new Date()).getTime();

  if (cdRequestMethod === 'XMLHttpRequest') {
    // uses the XMLHttpRequest api
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", url);
    xmlhttp.setRequestHeader("Content-Type", "application/json");
    xmlhttp.send(JSON.stringify({message: 'test'}));
  } else if (cdRequestMethod === 'fetch') {
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({message: 'test'}),
    })
    .then(data => console.log(data));
  }
}

document.addEventListener("visibilitychange", function(event) {
  if (document.visibilityState === 'hidden') {
    userLeavesPage("visibilitychange:" + document.visibilityState);
  }
});
```

Whenever I switch to a different tab, the event `visibilitychange` is set to state `hidden` and the POST request is successfully sent 
both with `fetch()` and with `XMLHttpRequest`.

However, when I close the tab or I close the browser, the POST request is NOT sent. Previously we have established that this should not be the case, because the event `visibilitychange` is triggered when the tab or browser is closed. It seems like the browser is aborting all pending http requests when the browser or tab is being closed.

This is bad and we cannot accept that. After all, this would result in a loss of valuable analytics data.

Then I wanted to check other events. To get a better understanding of the different events in the DOM, I suggest to read [this blog article](https://www.igvita.com/2015/11/20/dont-lose-user-and-app-state-use-page-visibility/).

```JavaScript
window.addEventListener("beforeunload", function(event) {
  userLeavesPage("beforeunload");
});

window.addEventListener("unload", function(event) {
  userLeavesPage("unload");
});

window.addEventListener("pagehide", function(event) {
  userLeavesPage("pagehide");
});
```

I got all around mixed results. For example, `fetch()` would successfully send the data when attached to the event `beforeunload`, but `XMLHttpRequest` would fail to do so.

After a bit of frustration and searching around, I found that following explanation on [MDN page about the sendBeacon Api](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon).

> Ensuring that data has been sent during the unloading of a document has traditionally been difficult, because user agents typically ignore asynchronous XMLHttpRequests made in an unload handler.

They suggest to use `navigator.sendBeacon()` instead. MDN promises:

> The navigator.sendBeacon() method asynchronously sends a small amount of data over HTTP to a web server. It’s intended to be used in combination with the visibilitychange event (but not with the unload and beforeunload events).

This is our salvation! We can just use `navigator.sendBeacon()`! This Api is exactly made for our use case!

But does `navigator.sendBeacon()` also fire when the page is being closed when we attach to `visibilitychange`? Let's try it:

```JavaScript
document.addEventListener("visibilitychange", function() {
  if (document.visibilityState === 'hidden') {
    const url = 'https://myserver.com/t?event=' + (new Date()).getTime();
    navigator.sendBeacon(url, 'visibilitychange');
  }
})
```

Yes, this works properly. I tested the above snippet on my Linux OS with the most recent chrome browser (`Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36`) and on my mobile phone. In all 7 cases listed below, the above snippet sends the data correctly to my remote server. I tested the following cases for the event `visibilitychange`. All requests were sent to a remote server from a different origin with `navigator.sendBeacon()`:

1. One beacon is sent from the desktop browser when the tab is switched ✓
2. Two beacons are sent from the desktop browser when the tab is closed ✓
3. Two beacons are sent from the desktop browser when the browser is closed ✓
4. One beacon is sent from the smartphone browser when the tab is switched ✓
5. One beacon is sent from the smartphone browser when the tab is closed ✓
6. One beacon is sent from the smartphone browser when the browser is closed ✓
6. One beacon is sent from the smartphone browser when the sleep / power off button is pressed ✓
7. One beacon is sent from the smartphone browser when the home button is pressed ✓

Please do not ask me why the desktop chrome browser sends the beacon twice on case 2. and 3.

### Is `navigator.sendBeacon()` broken?

I found the [following interesting blog article](https://volument.com/blog/sendbeacon-is-broken) from a company whose main product is an analytics applicaton. They need a very reliable way to transmit data in a cross domain fashion amd tried the sendBeacon Api in production.

Their conclusion is the following:

> On this sample set, about 30% of browsers that claim to support the beacon API failed to deliver the data to our servers when the page was closed, which is the whole purpose of the sendBeacon call.

They state that all those fancy web Api's

- fetch()
- XMLHttpRequest
- navigator.sendBeacon()

are unreliable and broken if you want to send data at the end of a browsing sessions on the events
`visibilitychange`, `onbeforeunload` or `onunload`.

[This Github issue discussion](https://github.com/mdn/sprints/issues/3722) explains in depth why this is the case.

### Solution: Reliable cross domain communication with `<img>` tags?

The above article (https://volument.com/blog/sendbeacon-is-broken) suggested to use `<img>` tags to transmit data. The idea is to use the Image object to send analytics data:

```JavaScript
document.addEventListener("visibilitychange", function() {
  if (document.visibilityState === 'hidden') {
    const url = 'https://myserver.com/t?event=' + (new Date()).getTime();
    var image = new Image;
    image.src = url;
  }
})
```

I tested the exact same 7 steps as above:

1. One img request is sent from the desktop browser when the tab is switched ✓
2. One img request is sent from the desktop browser when the tab is closed ✓
3. One img request is sent from the desktop browser when the browser is closed ✓
4. One img request is sent from the smartphone browser when the tab is switched ✓
5. One img request is sent from the smartphone browser when the tab is closed ✓
6. One img request is sent from the smartphone browser when the browser is closed ✓
6. One img request is sent from the smartphone browser when the sleep / power off button is pressed ✓
7. One img request is sent from the smartphone browser when the home button is pressed ✓

According to my tests, it doesn't matter whether we use `navigator.sendBeacon()` or `<img>` requests. However, 
I only tested with two up-to-date browsers and **my sample size is by far not representative**. The best idea would be to conduct 
a statistically sound test under live conditions:

- Increase a counter on the server side when our analytics javascript is loaded. Add a uuid to the analytics javascript.
- The analytics javascript sends a initial request on page load with a uuid generated in the served javascript
- Decrease the counter when we receive a analytics request on the event `visibilitychange` with the matching uuid

Hint: Disregard all requests to our application that do not have a valid uuid.

After the above, we have three internal states assigned to the uuid:

1. flag javascript delivered
2. flag page load request received
3. flag analytics request received

With those flags we can state that the following: Assuming the javascript is delivered and a page load event is received,
but no analytics request ever arrives:

- either a malicous user intentionally crafted the two requests like that
- the browser failed to deliver the request on `visibilitychange`

After some more experiments with `<img>`, I came up with the following restrictions with `<img>` requests:

- Not more than ~7700 bytes of GET payload allowed for the `<img>` `src` attribute
- url data needs to be url safe base64 encoded
- because of caching, the same image url cannot be used twice, otherwise the request is not fired

In summary, the image requests were fired reliably. Furthermore, `<img>` tags probably 
are supported on more browsers than the relatively new `navigator.sendBeacon()` Api.

But, since my application sometimes has more than 7700 bytes (even in compressed form) to send, I would need to send data incrementally. As soon as lets say 15kb of bytes of data is collected, make the first <img> request. When the next 15kb of data is available, send the second batch. The rest of recorded user interaction is sent at the end when the event `visibilitychange` is triggered.

We just have to keep track of this web session with an counter, such that the server can merge the session as soon
as it is finished.