Title: JavaScript Reverse Engineering - Imperva Advanced Bot Protection
Status: draft
Date: 2021-07-19 22:58
Category: Security
Tags: Reverse Engineering, Imperva, Bot Protection
Slug: javascript-reverse-engineering-imperva-advanced-bot-protection
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

After adding a breakpoint on XHR or fetch when the url contains `immo-1-17` (see image below),

<figure>
  <img src="{static}/images/breakpoint.png" alt="XHR or fetch breakpoint" />
  <figcaption>XHR or fetch breakpoint when url contains `immo-1-17`</figcaption>
</figure>

and then navigating to the url [https://www.immobilienscout24.de/Suche/de/nordrhein-westfalen/koeln/wohnung-mieten?](https://www.immobilienscout24.de/Suche/de/nordrhein-westfalen/koeln/wohnung-mieten?) and continuing a lot of uninteresting XHR fetch breakpoints we finally arrive at the site that performs the bot check

<figure>
  <img src="{static}/images/botcheck.png" alt="botcheck" />
  <figcaption>botcheck - the page where we want to intercept XHR or fetch calls</figcaption>
</figure>

On this page we pause on the breakpoint and inspect the contents of the debugger. This is the obfuscated code that sends the bot detection message to the endpoint `https://www.immobilienscout24.de/assets/immo-1-17`:

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

The variable `_0x3f2e6a` contains a large `p` value along some other stuff:

```JavaScript
"{"solution":{"interrogation":{"p":"qeQsQGYRDuY+QSnzobwvDumrlyM1yU9PjDxgTG6KWG7mr/8OIyu472f5w6vM6J1m/zPRRZ…"
```

I assume that `p` contains information about the client that helps the server decide whether `p` is a bot or not.

The next step is to find out how `p` is encrypted or encoded.

When I look at the enormous call stack, there is quite some tinkering work to do:

<figure>
  <img src="{static}/images/imperva.png" alt="Reverse Engineering Imperva" />
  <figcaption>Huge call stack :/</figcaption>
</figure>

## Improving the Readability - De-Obfuscation

When looking at the damn obfuscated code, you can see that a lot of strings are obfuscated with this lookup table:

```JavaScript
var strings = ['extractCookie', 'Unable\x20to\x20find\x20a\x20challenge\x20script\x20with\x20`src`\x20attribute\x20`', 'ontimeout', 'type', 'userAgent', 'Module', 'renewTime', 'Yosemite', 'split', 'runAutomationCheck', '500', 'Symbol', '[object\x20Int16Array]', 'TokenResponse', '700', '_IDE_Recorder', 'progress', 'charCodeAt', 'media', 'onTimeout', 'Lion/Mountain\x20Lion', 'getSeconds', 'sent', 'callback', 'FileReader', 'reese84_performance', 'COOKIE_NAME', 'marks', 'setPrototypeOf', '/assets/immo-1-17', 'ops', 'content-type', 'now', 'reese84_', 'response', 'initializeProtection', 'external', 'submitCaptcha', 'Failed\x20to\x20construct\x20\x27Promise\x27:\x20Please\x20use\x20the\x20\x27new\x27\x20operator,\x20this\x20object\x20constructor\x20cannot\x20be\x20called\x20as\x20a\x20function.', 'push', 'onmessage', 'started', 'Response', 'formData', 'byteLength', 'Linux', 'Invalid\x20status\x20code', '__proto__', 'DateTimer', '[object\x20Array]', 'Generator\x20is\x20already\x20executing.', '_remaining', 'MacIntel', 'navigator', 'could\x20not\x20read\x20FormData\x20body\x20as\x20blob', 'findChallengeScript', '_asap', 'run', 'documentElement', 'automationCheck', 'getAllResponseHeaders', 'function', 'default', 'CaptchaPayload', 'web', 'number', 'duration', 'clearMeasures', 'credentials', 'scheduler', 'getToken', 'hash', 'measures', '[object\x20Uint8ClampedArray]', 'start', 'Network\x20request\x20failed', ';\x20samesite=none;\x20secure', 'setItem', 'bodyUsed', '(^|\x20)', 'substring', 'promise', ';\x20max-age=', 'substr', '_bodyBlob', 'Post', 'entries', '=;\x20path=/;\x20expires=Thu,\x2001\x20Jan\x201970\x2000:00:01\x20GMT', '[object\x20Uint32Array]', 'application/x-www-form-urlencoded;charset=UTF-8', 'open', ';\x20domain=', 'hasOwnProperty', 'appendChild', 'keys', 'toUpperCase', '_willSettleAt', 'getElementById', 'trim', '300', 'iterator', 'json', 'setTimeout\x20has\x20not\x20been\x20defined', 'interrogation', 'enableFull', 'submitCaptcha\x20timed\x20out', 'online', 'return\x20this', 'then', '\x27:\x20', 'tokenExpiryCheck', 'binding', 'removeChild', 'You\x20must\x20pass\x20a\x20resolver\x20function\x20as\x20the\x20first\x20argument\x20to\x20the\x20promise\x20constructor', 'addEventListener', 'statusText', 'loading', 'toString', 'bind', 'interrogate', 'redirect', 'replace', 'INPUT', 'Request', 'addListener', '_setScheduler', 'cookie', 'could\x20not\x20read\x20FormData\x20body\x20as\x20text', 'toLowerCase', 'listeners', 'Protection\x20has\x20not\x20started.', 'buildCookie', 'polyfill\x20failed\x20because\x20global\x20object\x20is\x20unavailable\x20in\x20this\x20environment', 'fire', 'platform', 'getAttribute', 'mode', 'isArray', 'stringify', 'return', '__esModule', 'window', 'You\x20must\x20pass\x20an\x20array\x20to\x20race.', 'prependListener', 'update', 'tokenEncryptionKeySha2', '[object\x20Promise]', 'clearMarks', '_bodyFormData', ';\x20path=/', 'measure', '__fx', 'Mavericks', 'url', 'observe', 'waitingOnToken', '__s', 'You\x20cannot\x20resolve\x20a\x20promise\x20with\x20itself', 'map', 'process.binding\x20is\x20not\x20supported', 'Recaptcha', 'findScriptBySource', 'stack', 'lax', 'clearTimeout\x20has\x20not\x20been\x20defined', '_enumerate', 'test', 'arrayBuffer', '_instanceConstructor', 'GET', 'setToken', '_subscribers', 'port2', 'blob', 'object', '[object\x20Uint8Array]', 'reese84interrogator', 'PRIMARY_COOKIE', '[object\x20Int8Array]', 'audio', '[object\x20Uint16Array]', 'runOnLoop', 'document', 'lax', 'race', 'runOnContext', 'CaptchaProvider', 'buffer', 'old_token', '__web', 'visibilitychange', 'bingbot|msnbot|bingpreview|adsbot-google|googlebot|mediapartners-google|sogou|baiduspider|yandex.com/bots|yahoo.ad.monitoring|yahoo!.slurp', '[object\x20process]', 'pop', 'browser', 'pow', 'reeseSkipExpirationCheck', '[object\x20Float64Array]', 'onload', 'Chrome', 'responseType', '_start', '_state', 'hostname', 'process.chdir\x20is\x20not\x20supported', '_result', 'env', '=;\x20path=/;\x20expires=Thu,\x2001\x20Jan\x201970\x2000:00:01\x20GMT;\x20domain=', 'x-d-token', 'isPrototypeOf', 'renewInSec', 'legacy', 'FormData', 'fromTokenResponse', 'all', 'Snow\x20Leopard', 'prependOnceListener', 'startInternal', 'create', 'ROTL', 'port1', 'Internet\x20Explorer', 'parse', 'Promise', '_bodyArrayBuffer', 'triggerTimeMs', 'onerror', 'removeListener', 'argv', 'debug', 'withCredentials', 'set', 'setTimeout', 'Solution', 'solve', 'postbackUrl', 'Sequentum', 'responseURL', 'RecoverableError', '_initBody', 'getElementsByTagName', 'bon', 'next', 'interrogatorFactory', 'retry', 'updateToken', '\x20[\x20', 'name', 'cast', 'SECONDARY_COOKIE', 'isSearchEngine', 'RobustScheduler', 'src', 'Invalid\x20character\x20in\x20header\x20field\x20name', ';\x20samesite=lax', 'constructor', 'fromCharCode', '_setAsap', 'text/plain;\x20charset=utf-8', 'Safari', 'string', 'log', 'undefined', '_bodyText', '___dTL', 'callGlobalCallback', 'currentToken', 'readAsArrayBuffer', 'max', 'Protection', 'postMessage', '__awaiter', 'WinNT', 'has', 'script', 'nodeName', '', 'emit', 'text', 'finally', 'reject', 'data-advanced', 'Chromium', 'trys', 'title', 'uate', 'stopInternal', 'stripQuery', 'cookieDomain', 'version', 'timerId', 'vertx', 'currentTokenError', 'error', 'getItem', 'setSeconds', '_script_fn', 'total', 'call', 'include', '_bodyInit', 'polyfill', 'method', 'fonts', 'fun', 'stop', 'stable\x20error:\x20', 'require', 'array', 'application/json;\x20charset=utf-8', 'x-d-test', 'httpClient', 'min', '__generator', '[object\x20Int32Array]', 'fromJson', 'once', 'getOwnPropertyNames', 'Get', 'done', 'resolve', '_unwrapped', 'label', 'value', 'timer', 'shift', 'referrer', 'Win64', 'getTime', 'Request\x20error\x20for\x20\x27POST\x20', 'result', 'timerFactory', 'toHexStr', '_eachEntry', 'token', 'fetch', 'BonServer', 'clone', 'AutomationPayload', 'location', 'catch', 'summary', 'exports', 'URLSearchParams', 'currentTokenExpiry', 'forEach', 'apply', 'responseText', 'COOKIE_NAME_SECONDARY', 'status', 'prototype', 'clearTimeout', 'get', 'reeseRetriedAutoload', 'append', 'tion', 'slice', 'toStringTag', 'OPTIONS', 'join', 'headers', 'deleteCookie', 'MutationObserver', 'eval', 'search', 'none_secure', 'length', 'reduce', '_settledAt', 'mark', '_script_', 'onProtectionLoaded', '_onerror', 'nextTick', 'throw', 'HEAD', 'indexOf', 'Windows', 'match', '600', 'Non-ok\x20status\x20code:\x20', 'setCookie', 'defineProperty', 'unsupported\x20BodyInit\x20type', 'createElement', 'Headers', 'runLater', '400', 'appendQueryParam', 'off'];
var a0_0x1f86 = function(_0x6de5ff, _0x39e540) {
    _0x6de5ff = _0x6de5ff - 0x0;
    var _0x1f8625 = strings[_0x6de5ff];
    return _0x1f8625;
};
```

So as first measure to improve readability, we can replace all 1088 calls to `a0_0x1f86()` with the string value. The following script does that:

```JavaScript
const fs = require('fs');

// Replace all calls to the function `a0_0x1f86` in the obfuscated code
var a0_0x39e5 = ['extractCookie', 'Unable\x20to\x20find\x20a\x20challenge\x20script\x20with\x20`src`\x20attribute\x20`', 'ontimeout', 'type', 'userAgent', 'Module', 'renewTime', 'Yosemite', 'split', 'runAutomationCheck', '500', 'Symbol', '[object\x20Int16Array]', 'TokenResponse', '700', '_IDE_Recorder', 'progress', 'charCodeAt', 'media', 'onTimeout', 'Lion/Mountain\x20Lion', 'getSeconds', 'sent', 'callback', 'FileReader', 'reese84_performance', 'COOKIE_NAME', 'marks', 'setPrototypeOf', '/assets/immo-1-17', 'ops', 'content-type', 'now', 'reese84_', 'response', 'initializeProtection', 'external', 'submitCaptcha', 'Failed\x20to\x20construct\x20\x27Promise\x27:\x20Please\x20use\x20the\x20\x27new\x27\x20operator,\x20this\x20object\x20constructor\x20cannot\x20be\x20called\x20as\x20a\x20function.', 'push', 'onmessage', 'started', 'Response', 'formData', 'byteLength', 'Linux', 'Invalid\x20status\x20code', '__proto__', 'DateTimer', '[object\x20Array]', 'Generator\x20is\x20already\x20executing.', '_remaining', 'MacIntel', 'navigator', 'could\x20not\x20read\x20FormData\x20body\x20as\x20blob', 'findChallengeScript', '_asap', 'run', 'documentElement', 'automationCheck', 'getAllResponseHeaders', 'function', 'default', 'CaptchaPayload', 'web', 'number', 'duration', 'clearMeasures', 'credentials', 'scheduler', 'getToken', 'hash', 'measures', '[object\x20Uint8ClampedArray]', 'start', 'Network\x20request\x20failed', ';\x20samesite=none;\x20secure', 'setItem', 'bodyUsed', '(^|\x20)', 'substring', 'promise', ';\x20max-age=', 'substr', '_bodyBlob', 'Post', 'entries', '=;\x20path=/;\x20expires=Thu,\x2001\x20Jan\x201970\x2000:00:01\x20GMT', '[object\x20Uint32Array]', 'application/x-www-form-urlencoded;charset=UTF-8', 'open', ';\x20domain=', 'hasOwnProperty', 'appendChild', 'keys', 'toUpperCase', '_willSettleAt', 'getElementById', 'trim', '300', 'iterator', 'json', 'setTimeout\x20has\x20not\x20been\x20defined', 'interrogation', 'enableFull', 'submitCaptcha\x20timed\x20out', 'online', 'return\x20this', 'then', '\x27:\x20', 'tokenExpiryCheck', 'binding', 'removeChild', 'You\x20must\x20pass\x20a\x20resolver\x20function\x20as\x20the\x20first\x20argument\x20to\x20the\x20promise\x20constructor', 'addEventListener', 'statusText', 'loading', 'toString', 'bind', 'interrogate', 'redirect', 'replace', 'INPUT', 'Request', 'addListener', '_setScheduler', 'cookie', 'could\x20not\x20read\x20FormData\x20body\x20as\x20text', 'toLowerCase', 'listeners', 'Protection\x20has\x20not\x20started.', 'buildCookie', 'polyfill\x20failed\x20because\x20global\x20object\x20is\x20unavailable\x20in\x20this\x20environment', 'fire', 'platform', 'getAttribute', 'mode', 'isArray', 'stringify', 'return', '__esModule', 'window', 'You\x20must\x20pass\x20an\x20array\x20to\x20race.', 'prependListener', 'update', 'tokenEncryptionKeySha2', '[object\x20Promise]', 'clearMarks', '_bodyFormData', ';\x20path=/', 'measure', '__fx', 'Mavericks', 'url', 'observe', 'waitingOnToken', '__s', 'You\x20cannot\x20resolve\x20a\x20promise\x20with\x20itself', 'map', 'process.binding\x20is\x20not\x20supported', 'Recaptcha', 'findScriptBySource', 'stack', 'lax', 'clearTimeout\x20has\x20not\x20been\x20defined', '_enumerate', 'test', 'arrayBuffer', '_instanceConstructor', 'GET', 'setToken', '_subscribers', 'port2', 'blob', 'object', '[object\x20Uint8Array]', 'reese84interrogator', 'PRIMARY_COOKIE', '[object\x20Int8Array]', 'audio', '[object\x20Uint16Array]', 'runOnLoop', 'document', 'lax', 'race', 'runOnContext', 'CaptchaProvider', 'buffer', 'old_token', '__web', 'visibilitychange', 'bingbot|msnbot|bingpreview|adsbot-google|googlebot|mediapartners-google|sogou|baiduspider|yandex.com/bots|yahoo.ad.monitoring|yahoo!.slurp', '[object\x20process]', 'pop', 'browser', 'pow', 'reeseSkipExpirationCheck', '[object\x20Float64Array]', 'onload', 'Chrome', 'responseType', '_start', '_state', 'hostname', 'process.chdir\x20is\x20not\x20supported', '_result', 'env', '=;\x20path=/;\x20expires=Thu,\x2001\x20Jan\x201970\x2000:00:01\x20GMT;\x20domain=', 'x-d-token', 'isPrototypeOf', 'renewInSec', 'legacy', 'FormData', 'fromTokenResponse', 'all', 'Snow\x20Leopard', 'prependOnceListener', 'startInternal', 'create', 'ROTL', 'port1', 'Internet\x20Explorer', 'parse', 'Promise', '_bodyArrayBuffer', 'triggerTimeMs', 'onerror', 'removeListener', 'argv', 'debug', 'withCredentials', 'set', 'setTimeout', 'Solution', 'solve', 'postbackUrl', 'Sequentum', 'responseURL', 'RecoverableError', '_initBody', 'getElementsByTagName', 'bon', 'next', 'interrogatorFactory', 'retry', 'updateToken', '\x20[\x20', 'name', 'cast', 'SECONDARY_COOKIE', 'isSearchEngine', 'RobustScheduler', 'src', 'Invalid\x20character\x20in\x20header\x20field\x20name', ';\x20samesite=lax', 'constructor', 'fromCharCode', '_setAsap', 'text/plain;\x20charset=utf-8', 'Safari', 'string', 'log', 'undefined', '_bodyText', '___dTL', 'callGlobalCallback', 'currentToken', 'readAsArrayBuffer', 'max', 'Protection', 'postMessage', '__awaiter', 'WinNT', 'has', 'script', 'nodeName', '', 'emit', 'text', 'finally', 'reject', 'data-advanced', 'Chromium', 'trys', 'title', 'uate', 'stopInternal', 'stripQuery', 'cookieDomain', 'version', 'timerId', 'vertx', 'currentTokenError', 'error', 'getItem', 'setSeconds', '_script_fn', 'total', 'call', 'include', '_bodyInit', 'polyfill', 'method', 'fonts', 'fun', 'stop', 'stable\x20error:\x20', 'require', 'array', 'application/json;\x20charset=utf-8', 'x-d-test', 'httpClient', 'min', '__generator', '[object\x20Int32Array]', 'fromJson', 'once', 'getOwnPropertyNames', 'Get', 'done', 'resolve', '_unwrapped', 'label', 'value', 'timer', 'shift', 'referrer', 'Win64', 'getTime', 'Request\x20error\x20for\x20\x27POST\x20', 'result', 'timerFactory', 'toHexStr', '_eachEntry', 'token', 'fetch', 'BonServer', 'clone', 'AutomationPayload', 'location', 'catch', 'summary', 'exports', 'URLSearchParams', 'currentTokenExpiry', 'forEach', 'apply', 'responseText', 'COOKIE_NAME_SECONDARY', 'status', 'prototype', 'clearTimeout', 'get', 'reeseRetriedAutoload', 'append', 'tion', 'slice', 'toStringTag', 'OPTIONS', 'join', 'headers', 'deleteCookie', 'MutationObserver', 'eval', 'search', 'none_secure', 'length', 'reduce', '_settledAt', 'mark', '_script_', 'onProtectionLoaded', '_onerror', 'nextTick', 'throw', 'HEAD', 'indexOf', 'Windows', 'match', '600', 'Non-ok\x20status\x20code:\x20', 'setCookie', 'defineProperty', 'unsupported\x20BodyInit\x20type', 'createElement', 'Headers', 'runLater', '400', 'appendQueryParam', 'off'];

// this part of code shuffles the `a0_0x39e5` array
(function(_0x6de5ff, _0x39e540) {
    var _0x1f8625 = function(_0x44ecba) {
        while (--_0x44ecba) {
            _0x6de5ff['push'](_0x6de5ff['shift']());
        }
    };
    _0x1f8625(++_0x39e540);
}(a0_0x39e5, 0x80));

// this is the function that we replace with the string literals
var a0_0x1f86 = function(_0x6de5ff, _0x39e540) {
    _0x6de5ff = _0x6de5ff - 0x0;
    var _0x1f8625 = a0_0x39e5[_0x6de5ff];
    return _0x1f8625;
};

var botCode = fs.readFileSync('imperva-obfuscated.js').toString();

var regex = /a0_0x1f86\('(0x[0-9a-f]*)'\)/gm
num = 0;

var newbotCode = botCode.replace(regex, function(e, match) {
  num++;
  var decoded = a0_0x1f86(match);
  console.log(e, match, decoded)
  return JSON.stringify(decoded);
});

console.log(num);

fs.writeFileSync('imperva-obfuscated-better-1.js', newbotCode);
```

This is the [slightly more readable file]({filename}/data/imperva-obfuscated-better-1.js) that has all calls to `a0_0x1f86()` replaced with string literals.

Now I understand the structure of the obfuscated script a bit better.

It consists of two parts

1. [A challenge script]({filename}/data/imperva-challenge-script.js) which probably does some cryptographic proof of work operations 
2. [And the second part]({filename}/data/imperva-second-part.js) that submits the challenge solution to the server and performs some browser checks (with already improved readability having replaced `a0_0x1f86()` with strings)

The challenge script looks quite weird and does a lot of strange operations. An excerpt:

```JavaScript
var rr = q_[FN.substr(1394, 20)] && q_[FN.substr(1394, 20)]();
DP[FN.substr(962, 12)] = rr ? rr[AR.substr(1524, 9)] ? true : false : null;
DP[FN.substr(1648, 9)] = q_[AR.substr(1209, 12)](q_[KJ.substr(2137, 9)]);
DP[FN.substr(2236, 10)] = q_[AR.substr(1209, 12)](q_[AR.substr(919, 10)]);
DP[KJ.substr(1824, 10)] = q_[AR.substr(1209, 12)](q_[KJ.substr(477, 10)]);
DP[KJ.substr(1014, 14)] = Sf(q_);
DP[AR.substr(833, 32)] = q_[AR.substr(1209, 12)](q_[FN.substr(262, 32)]);
DP[KJ.substr(658, 25)] = q_[AR.substr(1209, 12)](q_[KJ.substr(1603, 25)]);
DP[KJ.substr(1085, 28)] = q_[AR.substr(1209, 12)](q_[KJ.substr(1350, 28)]);
DP[KJ.substr(683, 22)] = q_[AR.substr(1209, 12)](q_[nA.substr(5, 21)]);
DP[KJ.substr(1057, 23)] = q_[AR.substr(1209, 12)](q_[AR.substr(268, 23)]);
DP[AR.substr(1876, 16)] = q_[AR.substr(1209, 12)](q_[FN.substr(1950, 16)]);
DP[FN.substr(1864, 19)] = q_[AR.substr(1209, 12)](q_[FN.substr(327, 19)]);
DP[KJ.substr(11, 18)] = q_[AR.substr(1209, 12)](q_[FN.substr(1623, 18)]);
DP[AR.substr(409, 30)] = q_[AR.substr(1209, 12)](q_[KJ.substr(533, 30)]);
DP[FN.substr(236, 26)] = q_[AR.substr(1209, 12)](q_[AR.substr(1290, 26)]);
DP[AR.substr(1000, 17)] = fx(q_[AR.substr(1209, 12)](q_[AR.substr(1673, 17)]));
DP[AR.substr(55, 8)] = q_[AR.substr(1209, 12)](q_[FN.substr(1100, 8)]);
DP[KJ.substr(806, 8)] = q_[AR.substr(1209, 12)](q_[AR.substr(1282, 8)]);
DP[nA.substr(237, 24)] = q_[AR.substr(1209, 12)](q_[FN.substr(1061, 24)]);
DP[AR.substr(1661, 12)] = q_[AR.substr(1209, 12)](q_[KJ.substr(1264, 12)]);
DP[FN.substr(1887, 6)] = q_[AR.substr(1209, 12)](q_[FN.substr(1734, 6)]);
DP[AR.substr(865, 7)] = q_[AR.substr(1209, 12)](q_[nA.substr(79, 7)]);
```

But having replaced the `a0_0x1f86('0xd6')` like calls with string literals helps already tremendously.

When I open a blank page and execute the [challenge script]({filename}/data/imperva-challenge-script.js) only, I see that the window object has a `window.reese84interrogator` function emerging.

<figure>
  <img src="{static}/images/reese84interrogator.png" alt="reese84interrogator" />
  <figcaption>Running the challenge script prepares the `reese84interrogator` function</figcaption>
</figure>

But where is this challenge functionality made use of?

In the second part I can see that a factory function creates a new `reese84interrogator` object with two parameters:

```JavaScript
_0xd1c0ad["interrogatorFactory"] = function(_0x39fb82) {
  return new window[("reese84interrogator")](_0x36099f,_0x39fb82);
}
```

whereas `_0x39fb82` seems to be a timer object that the interrogator needs.

I can't make sense of the other variable `var _0x36099f = _0x2482a0(0x6);`.

`interrogatorFactory` in turn is used in the `solve` function.

```JavaScript
_0x4815b1['prototype']["solve"] = function() {
  return _0x216cea(this, void 0x0, void 0x0, function() {
      var _0x2df399, _0x135bf1;
      return _0x17068c(this, function(_0xfa7469) {
          switch (_0xfa7469["label"]) {
          case 0x0:
              return _0x2df399 = _0x50eceb["interrogatorFactory"](this["timer"]),
              [0x4, new Promise(_0x2df399["interrogate"])];
          case 0x1:
              return _0x135bf1 = _0xfa7469["sent"](),
              [0x2, new _0x4631eb(_0x135bf1,'stable')];
          }
      });
  });
}
```

The `interrogate` property of the instantiated `reese84interrogator` object is passed to a promise:

```JavaScript
new Promise(_0x2df399["interrogate"])
```

The time `this["timer"]` is instantiated earlier as 

```JavaScript
this['timer'] = _0x1e36b0["timerFactory"]();
```

`solve` again is called in the function `getToken` without any parameters:

```JavaScript
_0x4815b1["prototype"]["getToken"] = function() {
  return _0x216cea(this, void 0x0, void 0x0, function() {
    var _0x82dbd5, _0x552e1b, _0x473a9f, _0x38410d;
    return _0x17068c(this, function(_0x335c46) {
        switch (_0x335c46["label"]) {
        case 0x0:
            _0x82dbd5 = _0x599402(),
            _0x335c46['label'] = 0x1;
        case 0x1:
            return _0x335c46['trys']["push"]([0x1, 0x3, , 0x4]),
            [0x4, this['solve']()];
        case 0x2:
            return _0x473a9f = _0x335c46["sent"](),
            _0x552e1b = new _0x421603(_0x473a9f,_0x82dbd5 ? _0x82dbd5["token"] : null,null,this['timer']["summary"]()),
            [0x3, 0x4];
        case 0x3:
            return _0x38410d = _0x335c46['sent'](),
            _0x552e1b = new _0x421603(null,_0x82dbd5 ? _0x82dbd5["token"] : null,"stable error: " + _0x38410d['st'] + '\x20' + _0x38410d['sr'] + '\x20' + _0x38410d['toString']() + '\x0a' + _0x38410d["stack"],null),
            [0x3, 0x4];
        case 0x4:
            return [0x4, this['bon']['validate'](_0x552e1b)];
        case 0x5:
            return [0x2, _0x335c46["sent"]()];
        }
    });
  });
}
```

But this all is not so interesting. What I know as of know:

The obfuscated code consists of two parts:

1. A challenge part that adds the `reese84interrogator` function to the `window` object. `reese84interrogator` points to the function `function M9(lr, on) {` which again starts all the [challenge madness]({filename}/data/imperva-challenge-script.js).

2. I know that the second part of the obfuscated code makes use of this `reese84interrogator` object and sends the challenge result to the server.

The question however remains? What the heck is the purpose of the `reese84interrogator` challenge?
How does it prove that the client is not automated and not a bot?

Is it some kind of crypto challenge?

