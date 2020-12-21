Title: Abusing image tags for cross domain requests
Date: 2020-12-15 20:50
Category: Security
Tags: cross-domain-requests, cors, browser
Slug: abusing-img-tags-for-cross-domain-requests
Author: Nikolai Tschacher
Summary: Cross domain requests with `<img>` tags are not bound to the same origin policy. I will shed light on several possibilities how malicious web site owners can potentially abuse cross domain request done with `<img>` and `script` tags created with JavaScript.

I am currently in the process of developing an analytics application in JavaScript. One of my requirements is to transmit analytics data right before the user leaves the surveyed website. A common strategy is to send the analytics data when the event `visibilitychange` is fired and the `visibilityState` changes to `hidden`:


```JavaScript
document.addEventListener("visibilitychange", function() {
  if (document.visibilityState === 'hidden') {
    // somehow send analytics data back home
    // for example like this:
    navigator.sendBeacon(url, JSON.stringify(data));
  }
}
```

However, other people that also rely on a stable cross browser transmission solution pointed out that `navigator.sendBeacon` is not the most reliable method. See for example this blog post: [Beacon API is broken](https://volument.com/blog/sendbeacon-is-broken).

This is why some people suggest to use the good old `<img>` tag to transmit data. The idea is to transmit your data in the query string of an GET request similar to this:

```JavaScript
var image = new Image;
image.src = 'https://example.org?data=someDataToStore';
```

The advantage is that requests originating from an `<img>` tag are not suspectible to the same origin policy. This means that cross domain requests are allowed. An alternative to `<img>` tags is to use an script to make an cross origin request:

```JavaScript
function addScript(src) {
  var script = document.createElement('script');
  script.setAttribute('src', src);
  document.body.appendChild(script);
}
```

The same origin policy is very important to maintain browser security. It prevents us to make http request to other domains than the domain of the origin of the webpage. For example, JavaScript loaded from the domain `example.org` cannot make an `fetch()` request to any other domain than itself (except domains where the `Access-Control-Allow-Origin` header is accordingly configured).

Since requesting scripts will only work when the requested resource is served with the `content-type: application/javascript; charset=utf-8` response header and images are only obtained when the response header content type is something like `content-type: image/webp`, we have no possibility to get the response contents of a cross domain request.

However, the request is nevertheless fired. The browser can only judge about Cross-Origin Read Blocking (CORB) after the requested server sent an response. Put differently: In order to falsify if the response is acceptable, a request needs to be made in the first place. But making arbitrary GET request can be dangerous by itself.

### Abusing `<img>` requests

Let's assume we have a small business niche website `nichebusiness.com` with 500 unique users a day. What would happen if every user's browser executes the following JavaScript:

```JavaScript
var image = new Image;
image.src = 'https://google.com/search?q=nichebusiness.com%20someHighRankingKeyword';
```

What happens here? We make a google search with the query **nichebusiness.com someHighRankingKeyword**. The idea is to manipulate the Google search algorithm.
The hope is that a steady search volume of 500 Google searches a day with our own domain and a desired SEO keyword somehow influences Google's algorithm. There are probably way better ways to improve the SEO of a website (and also more ethical ways), but I am just trying to make the point that those `<img>` request could potentially have an harmful impact.

But does Google even serve the SERP response if an `<img>` tag launches a Google search? After all, there are many headers set by the browser, when a image is requested. 

After rebuilding the image request done by the browser, I can confirm that Google answers with a valid SERP response. The search is not rejected based on the request headers. See the reconstructed request below:

```JavaScript
const got = require('got');
const fs = require('fs');

(async () => {
  let headers = {
    connection: 'keep-alive',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    dnt: '1',
    accept: 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-dest': 'image',
    referer: 'https://example.org/',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'de-DE,de;q=0.9,en-DE;q=0.8,en-US;q=0.7,en;q=0.6',
    'if-none-match': 'W/"875-176475a2ebc"',
    'if-modified-since': 'Wed, 09 Dec 2020 11:54:21 GMT'
  };
  let live = 'https://www.google.com/search?q=nichebusiness.com%20someHighRankingKeyword';
  const response = await got(live, {headers: headers, https: { rejectUnauthorized: false}});
  fs.writeFileSync('google_serp.html', response.body);
})();
```

### Conclusion

There are many other ways how such cross domain image requests could potentially be abused:

1. Promote your own YouTube video by increasing views. Make an request to `https://www.youtube.com/watch?v={someVideo}` in the `<img>` tag.
2. Drain your competitors Google Ads volume by making request to your competitors ad links.
3. Invoking any other action that can be reached by a GET request.