Title: Reverse Engineering Imperva's Advanced Bot Protection
Status: draft
Date: 2021-07-19 22:58
Category: Security
Tags: Reverse Engineering, Imperva, Bot Protection
Slug: reverse-engineering-Imperva-advanced-bot-protection
Author: Nikolai Tschacher
Summary: Imperva's advanced bot protection JavaScript is a hard nut to crack. Luckily I am stupid enough to give it a try.

For example, when I look for apartments on the German real estate search engine [immobilienscout24.de](https://www.immobilienscout24.de/), I am sometimes presented a bot detection challenge that performs a check passively in the background.

This is the [heavily obfuscated JavaScript file]({filename}/data/imperva.js) that does the bot detection work in the background. I am heavily assuming that the [above JavaScript]({filename}/data/imperva.js) is [Imperva's](https://www.imperva.com/products/advanced-bot-protection-management/) bot detection client side solution.

Why do I think that?

I found the string `reese84` in several places in the obfuscated JavaScript file and when I googled it I found the following [blog post on Imperva's community](https://community.imperva.com/communities/community-home/digestviewer/viewthread?GroupId=49&MessageKey=a36d2983-770a-4419-8980-1cd834b91bcf&CommunityKey=39c6092a-d67a-4bc2-8134-bfbb25fc43af&tab=digestviewer) page.

I spent around 30 minutes trying to understand what it does, but I only know that the script performs some checks and sends the following payload back to the server, where `p` is a 30KB long base64 encoded binary blob:

```json
{
   "solution":{
      "interrogation":{
         "p":"h6R2UwMDY2NnRfZ18oNUBwVTJKVWtNZnFqc2ZndX5NaHZyOGpf...[truncated]",
         "st":1626613924,
         "sr":113884550,
         "cr":994722218
      },
      "version":"stable"
   },
   "old_token":null,
   "error":null,
   "performance":{
      "interrogation":1006
   }
}
```

The next steps in reverse engineering would be to find out what exactly `p` contains. Look at the place in the obfuscated JavaScript where `p` becomes encrypted/encoded and dump the clear text contents. Then I know what data is sent and I can therefore spoof it.

But before I am doing that, I have a different idea:

I want to know what web API's and JavaScript functions the obfuscated script is calling. I want to know what functionality of the browser it leverages. I hope to understand how invasive the library's nature is by doing that.

So the idea is to write a simple hooking wrapper that prints out what invasive API was called. Something like that should just work fine for the `navigator` object:

```JavaScript
(function() {
  var props = {
    "userAgent": window.navigator.userAgent,
    "platform": window.navigator.platform,
    "hardwareConcurrency": window.navigator.hardwareConcurrency,
    "languages": window.navigator.languages,
    "language": window.navigator.language,
    "webdriver": window.navigator.webdriver,
    "deviceMemory": window.navigator.deviceMemory,
  }

  function logAccess(key, value) {
    Object.defineProperty(window.navigator, key, {
      get: function() {
        console.log("navigator." + key + " accessed");
        return value;
      },
    });
  }

  for (var key in props) {
    logAccess(key, props[key]);
  }
})();
```

But what if I want to log all accesses to all properties of the `window` object?

```JavaScript
var func = window.btoa;
Object.defineProperty(window, 'btoa', {
  get: function() {
    console.log("btoa() accessed");
    return func;
  }
});
```


## Debugging by breaking on XHR or fetch

After adding a generic breakpoint on XHR or fetch, this is the obfuscated code that sends the bot detection message to the server:

```JavaScript
function _0x4367d8(_0x273cd6, _0x5d9b80, _0x1662f3, _0x10df38) {
    return _0x3466c4(this, void 0x0, void 0x0, function() {
        var _0x4e20fe, _0x3f2e6a, _0x342756, _0x2ea22e, _0x3914e0, _0x2e5c6e, _0x35aad0;
        return _0x2ae227(this, function(_0x19379a) {
            switch (_0x19379a['label']) {
            case 0x0:
                return _0x19379a[a0_0x5181('0x108')][a0_0x5181('0x72')]([0x0, 0x2, , 0x3]),
                _0x4e20fe = window[a0_0x5181('0x22')][a0_0x5181('0x4f')],
                _0x3f2e6a = JSON[a0_0x5181('0x9b')](_0x1662f3, function(_0x779ed8, _0x585808) {
                    return void 0x0 === _0x585808 ? null : _0x585808;
                }),
                _0x342756 = {
                    'Accept': a0_0x5181('0xb2'),
                    'Content-Type': 'text/plain;\x20charset=utf-8'
                },
                _0x10df38 && (_0x342756['x-d-test'] = _0x10df38),
                _0x2ea22e = 'd=' + _0x4e20fe,
                _0x3914e0 = _0x922252[a0_0x5181('0xc9')](_0x5d9b80, _0x2ea22e),
                [0x4, _0x273cd6(_0x3914e0, {
                    'body': _0x3f2e6a,
                    'headers': _0x342756,
                    'method': _0x20d6d1['Post']
                })];
            case 0x1:
                if ((_0x2e5c6e = _0x19379a['sent']())['ok'])
                    return [0x2, _0x2e5c6e[a0_0x5181('0x11')]()];
                throw new Error(a0_0x5181('0x59') + _0x2e5c6e['status']);
            case 0x2:
                throw _0x35aad0 = _0x19379a[a0_0x5181('0xf6')](),
                new _0x884c03(a0_0x5181('0x159') + _0x5d9b80 + a0_0x5181('0xde') + _0x35aad0);
            case 0x3:
                return [0x2];
            }
        });
    });
}
```

The variable `_0x3f2e6a` contains a large `p`  value along some other stuff:

```json
"{"solution":{"interrogation":{"p":"qeQsQGYRDuY+QSnzobwvDumrlyM1yU9PjDxgTG6KWG7mr/8OIyu472f5w6vM6J1m/zPRRZ…"
```

I assume that `p` contains information about the client that helps the server decide whether `p` is a bot or not.

The next step is to find out how `p` is encrypted or encoded.

When I look at the enormous call stack, there is quite some tinkering work to do:

<figure>
  <img src="{static}/images/imperva.png" alt="Reverse Engineering Imperva" />
  <figcaption>Huge call stack :/</figcaption>
</figure>