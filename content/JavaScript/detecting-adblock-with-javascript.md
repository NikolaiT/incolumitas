Title: Detecting uBlock Origin and Adblock Plus with JavaScript only
Date: 2020-12-27 20:47
Category: JavaScript
Tags: Adblock Plus, uBlock Origin, Adblock Detection, JavaScript
Slug: detecting-uBlock-Origin-and-Adblock-Plus-with-JavaScript-only
Author: Nikolai Tschacher
Summary: There are many resources in the Internet that show how to detect uBlock Origin and Adblock Plus. However, after some research, it became clear that most detection methods are unreliable and cease to exist after a while. In this blog article, a reliable detection method for uBlock Origin and Adblock Plus is demonstrated. No external libraries. Just plain and simple JavaScript.

[uBlock Origin](https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm?hl=en) and [Adblock Plus](https://adblockplus.org/) are famous anti advertisement browser extensions. Adblocking software filter advertisement content from websites. Some folks consider ad blocking to be unethical, since publishers lose revenue. Some consider the blocking of advertisements their good right. I personally tend to be on the side of the latter group, since ads are way to obnoxious in general ([Especially on YouTube](https://incolumitas.com/2020/12/16/removing-youtube-ads-from-android-phone/)).

On the technical side, uBlock Origin and Adblock Plus are designed quite straightforward. They make use of large text based filter lists and compare the items of that list with the contents of HTML Nodes or URLs. If there is a match, the HTML element is removed or the URL is not loaded. An example for such a list would be the well known filter list named [Easy List](https://easylist-downloads.adblockplus.org/easylist.txt). The filter lists for uBlock Origin can be [found on their GitHub repo](https://github.com/uBlockOrigin/uAssets/tree/master/filters).

However, sometimes it is necessary to be able to detect that an Adblocker is active. Ideally, the detection should **work by using vanilla JavaScript only**. In this blog post, I will show several different techniques to detect the presence of adblock software.

All code snippets were tested with **Firefox/84.0** and **Chrome/86.0.4240.75**.
On the Firefox browser, Adblock Plus is running. uBlock Origin is activated on Chrome.

### Attempt 1: Detect Adblock with a baiting div node

With this technique, the idea is to create an `<div>` element dynamically and set the class attribute to `adsbox`. If an adblocker is active, it should automatically remove this div element, because the class name is flagged as suspicious.

The technique is being used in the [fingerprint.js library](https://github.com/fingerprintjs/fingerprintjs/blob/master/src/sources/adblock.ts).

Try it out by pasting the code below in your browser JavaScript console.

```JavaScript
(function detectWithAdsDiv() {
  var detected = false;

  const ads = document.createElement('div');
  ads.innerHTML = '&nbsp;';
  ads.className = 'adsbox';

  try {
    document.body.appendChild(ads);
    var node = document.querySelector('.adsbox');
    detected = !node || node.offsetHeight === 0;
  } finally {
    ads.parentNode.removeChild(ads);
  }

  console.log('Using Adblocker: ' + detected);
})();
```

This technique did **not work** on both tested browsers. Therefore, the above code is obsolete.

The same technique was tried with other [CSS class names](https://stackoverflow.com/questions/4869154/how-to-detect-adblock-on-my-website), but nothing worked.

### Attempt 2: Detect Adblock by downloading suspicious ad scripts

After some searching in the Internet, I found the [following blog post](https://jonathanmh.com/how-to-detect-ad-blockers-adblock-ublock-etc/).

The idea is the following: The author tried to make a `fetch()` request to a advertisement script, if the request is getting blocked, there must be an active Adblocker in the background.

For testing purposes, a `goodURL` is picked that should not get blocked, since it is a widely used JavaScript library for interactive content. On the other side, the `badURL` is a URL that points to a Google Advertising script. The `badURL` is listed in the Adblock filter list.

```JavaScript
var goodURL = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.min.js';
var badURL = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';
```

The code from the mentioned blog post was a bit modified. But essentially, it boils down to the following:

```JavaScript
var badURL = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';

(function detectWithFetch() {
  var t0 = performance.now();

  var myRequest = new Request(badURL, {
    method: 'HEAD',
    mode: 'no-cors',
  });
  
  fetch(myRequest)
    .then(response => response.text())
    .then(function(data) {
      console.log('Not Using Adblock');
    })
    .catch(function(e){
      console.log(e)
      console.log('Using Adblock');
    })
    .finally(function(e) {
      var t1 = performance.now();
      console.log('Took ' + (t1-t0).toFixed(2) + 'ms');
    })
})();
```

Unfortunately, this **also does not work reliably**. There are a couple of reasons why the above technique is not ideal:

1. The `fetch()` API is still not supported in all browsers because it is relatively new
2. `fetch()` tends to have issues with CORS requests

### The solution: Dynamically creating a `<script>` tag

Dynamically creating a `<script>` tag is a better idea, since `<script>` tags are supported in every browser
and the issues with CORS and the same origin policy do not apply.

The following solution works reliably in both Firefox and Chrome. Both Adblock Plugins could be detected with the below snippet:

```JavaScript
var badURL = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';

(function detectWithScriptTag() {
  var t0 = performance.now();

  var script = document.createElement('script');

  script.onload = function() {
    var elapsed = (performance.now() - t0).toFixed(2) + 'ms';
    console.log("Not using Adblocker, script loaded in " + elapsed);
    // delete script node
    script.parentNode.removeChild(script);
  };

  script.onerror = function() {
    var elapsed = (performance.now() - t0).toFixed(2) + 'ms';
    console.error("Using Adblocker, script failed to load after " + elapsed);
  }

  script.src = badURL;
  document.body.appendChild(script);
})();
```
After pasting the above snippet into the developer console, we see the error **net::ERR_BLOCKED_BY_CLIENT** which indicates that uBlock Origin
intercepted the request and aborted it. It can also be seen that the request took only 7.96ms, which is way too fast for a legit HTTP request.

<figure>
    <img src="{static}/images/uBlock-detected.png" alt="uBlock Origin detected" />
    <figcaption>The extension uBlock Origin is being detected in Chrome</figcaption>
</figure>

When using the above technique in production, several points need to be considered:

1. Every time the above script is executed without a Adblock software, a HTTP request is made and a script is downloaded. This costs resources.
2. If the `badURL` is no longer a URL that is on the adblock filter list, the technique ceases to work. Therefore, the validity of the `badURL` needs to be ensured.