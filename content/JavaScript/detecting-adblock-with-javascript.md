Title: Detecting uBlock Origin and Adblock Plus with JavaScript only
Date: 2020-12-27 20:47
Modified: 2022-10-15 22:31
Category: JavaScript
Tags: Adblock Plus, uBlock Origin, Adblock Detection, JavaScript
Slug: detecting-uBlock-Origin-and-Adblock-Plus-with-JavaScript-only
Author: Nikolai Tschacher
Summary: There are many resources in the Internet that show how to detect uBlock Origin and Adblock Plus. However, after some research, it became clear that most detection methods are unreliable and cease to exist after a while. In this blog article, a reliable detection method for uBlock Origin and Adblock Plus is demonstrated. No external libraries. Just plain and simple JavaScript.

**Edit (15th October 2022):**

+ [For the code, visit the GitHub page of this article](https://github.com/NikolaiT/adblock-detect-javascript-only)
+ Alternatively, install the Adblock detection script [from npm](https://www.npmjs.com/package/adblock-detect-javascript-only) with the command `npm i adblock-detect-javascript-only`

In case this will stop working in the next days / weeks, I will make the selection of filter dynamic and random. Put differently: If you whitelist a filter such as `pp34.js?sv=` (uBlock Origin) or `&ad_height=` (EasyList - uBlock Origin and Adblock Plus), I will make a random selection of a filter / list entry in the following block-lists:

+ Adblock EasyList: [https://github.com/easylist/easylist/blob/master/easylist/easylist_general_block.txt](https://github.com/easylist/easylist/blob/master/easylist/easylist_general_block.txt)
+ uBlock Origin uAssets: [https://github.com/uBlockOrigin/uAssets/blob/master/filters/filters-2022.txt](https://github.com/uBlockOrigin/uAssets/blob/master/filters/filters-2022.txt)

<script type="text/javascript">
/**
 * Author: Nikolai Tschacher
 * Updated: 15.10.2022
 * Website: https://incolumitas.com/
 *
 * Detect uBlock Origin, Adblock Plus and Ghostery with JavaScript only
 *
 * Usage: detectAdblock().then((res) => { console.log(res) });
 *
 */
function detectAdblock() {
  const adblockTests = {
    // https://github.com/uBlockOrigin/uAssets/blob/master/filters/filters-2022.txt
    uBlockOrigin: {
      url: 'https://incolumitas.com/data/pp34.js?sv=',
      id: '837jlaBksSjd9jh',
    },
    // https://github.com/easylist/easylist/blob/master/easylist/easylist_general_block.txt
    adblockPlus: {
      url: 'https://incolumitas.com/data/neutral.js?&adserver=',
      id: 'hfuBadsf3hFAk',
    },
  };

  function canLoadRemoteScript(obj) {
    return new Promise(function (resolve, reject) {
      var script = document.createElement('script');

      script.onload = function () {
        if (document.getElementById(obj.id)) {
          resolve(false);
        } else {
          resolve(true);
        }
      }

      script.onerror = function () {
        resolve(true);
      }

      script.src = obj.url;
      document.body.appendChild(script);
    });
  }

  return new Promise(function (resolve, reject) {
    let promises = [
      canLoadRemoteScript(adblockTests.uBlockOrigin),
      canLoadRemoteScript(adblockTests.adblockPlus),
    ];

    Promise.all(promises).then((results) => {
      resolve({
        uBlockOrigin: results[0],
        adblockPlus: results[1],
      });
    }).catch((err) => {
      reject(err);
    });
  });
}

detectAdblock().then((res) => {
  var ublockEl = document.getElementById('ublock_origin');
  var adblockEl = document.getElementById('adblock_plus');

  if (res.uBlockOrigin) {
    ublockEl.innerHTML = 'You are using uBlock Origin! (' + res.uBlockOrigin + ')';
  } else {
    ublockEl.style.backgroundColor = '#63ff85';
    ublockEl.innerHTML = 'You are not using uBlock Origin (' + res.uBlockOrigin + ')';
  }

  if (res.adblockPlus) {
    adblockEl.innerHTML = 'You are using Adblock Plus! (' + res.adblockPlus + ')';
  } else {
    adblockEl.style.backgroundColor = '#63ff85';
    adblockEl.innerHTML = 'You are not using Adblock Plus (' + res.adblockPlus + ')';
  }
});
</script>

<strong>Adblock Plus Detected:</strong> <span id="adblock_plus" style="border: 3px #4f4f4f solid;
    padding: 10px;
    background-color: #ff6363;
    margin-top: 20px;
    display: block;
    width: 300px;"></span>

<strong>uBlock Origin Detected:</strong> <span id="ublock_origin" style="border: 3px #4f4f4f solid;
    padding: 10px;
    background-color: #ff6363;
    margin-top: 10px;
    display: block;
    width: 300px;"></span>

### Update Adblock / uBlock Origin Detection on August 27th 2022

This is the **newest** detection code:

```js
/**
 * Author: Nikolai Tschacher
 * Updated: 15.10.2022
 * Website: https://incolumitas.com/
 * 
 * Detect uBlock Origin, Adblock Plus and Ghostery with JavaScript only
 * 
 * Usage: detectAdblock().then((res) => { console.log(res) });
 * 
 */
function detectAdblock() {
  const adblockTests = {
    // https://github.com/uBlockOrigin/uAssets/blob/master/filters/filters-2022.txt
    uBlockOrigin: {
      url: 'https://incolumitas.com/data/pp34.js?sv=',
      id: '837jlaBksSjd9jh',
    },
    // https://github.com/easylist/easylist/blob/master/easylist/easylist_general_block.txt
    adblockPlus: {
      url: 'https://incolumitas.com/data/neutral.js?&adserver=',
      id: 'hfuBadsf3hFAk',
    },
  };

  function canLoadRemoteScript(obj) {
    return new Promise(function (resolve, reject) {
      var script = document.createElement('script');

      script.onload = function () {
        if (document.getElementById(obj.id)) {
          resolve(false);
        } else {
          resolve(true);
        }
      }

      script.onerror = function () {
        resolve(true);
      }

      script.src = obj.url;
      document.body.appendChild(script);
    });
  }

  return new Promise(function (resolve, reject) {
    let promises = [
      canLoadRemoteScript(adblockTests.uBlockOrigin),
      canLoadRemoteScript(adblockTests.adblockPlus),
    ];

    Promise.all(promises).then((results) => {
      resolve({
        uBlockOrigin: results[0],
        adblockPlus: results[1],
      });
    }).catch((err) => {
      reject(err);
    });
  });
}
```

Usage:

```js
detectAdblock().then((res) => { console.log(res) });
```

### Introduction

[uBlock Origin](https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm?hl=en) and [Adblock Plus](https://adblockplus.org/) are famous anti advertisement browser extensions. Adblock software filter advertisement content from websites. Some folks consider the blocking of ads to be unethical, since publishers lose revenue. Other people regard the blocking of advertisements as their good right. I personally tend to be on the side of the latter group, since ads are way to obnoxious in general ([Especially on YouTube](https://incolumitas.com/2020/12/16/removing-youtube-ads-from-android-phone/)).

On the technical side, uBlock Origin and Adblock Plus are designed quite straightforward. They make use of large text based filter lists and compare the items of those lists with the contents of HTML nodes or URLs. If there is a match, the HTML element is removed or the URL is not loaded. An example for such a list would be the well known [Easy List](https://easylist-downloads.adblockplus.org/easylist.txt). The filter lists for uBlock Origin can be [found on their GitHub repo](https://github.com/uBlockOrigin/uAssets/tree/master/filters).

However, sometimes it is necessary to be able to detect that an Adblocker is active. Ideally, the detection should **work by using vanilla JavaScript only**. In this blog post, I will show several different techniques to detect the presence of Adblock software.

All code snippets were tested with **Firefox/84.0** and **Chrome/86.0.4240.75**.
On the Firefox browser, Adblock Plus is running. uBlock Origin is activated on Chrome.

### Attempt 1: Detect Adblock with a baiting div node

With this technique, the idea is to create an `<div>` element dynamically and set the class attribute to `adsbox`. If an Adblocker is active, it should automatically remove this div element, because the class name is flagged as suspicious.

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

The same technique was tried with other [CSS class names](https://stackoverflow.com/questions/4869154/how-to-detect-adblock-on-my-website), but nothing worked reliably.

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

### A first solution: Dynamically creating a `<script>` tag

Dynamically creating a `<script>` tag is a better idea, since `<script>` tags are supported in every browser
and the issues with CORS and the same origin policy do not apply.

The following solution works reliably in both Firefox and Chrome. Both Adblock plugins could be detected with the below snippet:

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

1. Every time the above script is executed without a active Adblock software, a HTTP request is made and a script is downloaded. This costs network bandwidth resources.
2. If the `badURL` is no longer an URL that is on the Adblock filter list, the technique ceases to work. Therefore, the validity of the `badURL` needs to be ensured.

### The ultimate solution: Making a request to a non-existent baiting resource

Assuming that most browsers do not have adblock software installed, we want a detection method that is fast and doesn't waste resources.
However, the solution presented above does waste unnecessary resources: On a browser without adblock, every time the function is executed, the browser loads the advertisement script.

One idea would be to take a non-existent URL that is universally detected by adblock software, but will not properly load in the case when there is no adblock software installed.

This is the ultimate adblock detection solution. You can paste it in your developer console and it should be able to detect any adblock software. It also supports a fallback to `XMLHttpRequest` in case the `fetch()` API is not available.

```JavaScript
// Author: Nikolai Tschacher
// Date: 28.12.2020
// Website: https://incolumitas.com/
(function detectAdblockWithInvalidURL(callback) {
  var flaggedURL = 'pagead/js/adsbygoogle.js';

  if (window.fetch) {
    var request = new Request(flaggedURL, {
      method: 'HEAD',
      mode: 'no-cors',
    });
    fetch(request)
      .then(function(response) {
        if (response.status === 404) {
          callback(false);
        }
      })
      .catch(function(error) {
        callback(true);
      });
  } else {
    var http = new XMLHttpRequest();
    http.open('HEAD', flaggedURL, false);

    try {
      http.send();
    } catch (err) {
      callback(true);
    }

    if (http.status === 404) {
      callback(false);
    }
  }
})(function(usingAdblock) {
  console.log("Using Adblocker: " + usingAdblock);
})
```
