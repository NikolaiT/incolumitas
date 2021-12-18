Title: On High-Precision JavaScript Timers
Status: published
Date: 2021-12-18 20:40
Category: Security
Tags: spectre, meltdown, cache-attacks, high-precision-timing, JavaScript
Slug: on-high-precision-javascript-timers
Author: Nikolai Tschacher
Summary: I in this blog post, I am investigating the current state of high precision JavaScript timers. High precision timing techniques were mostly used to launch CPU-level cache attacks such as Spectre and Meltdown from the browser. I am interested in other use cases though...

## Introduction

I in this blog post, I am investigating the current state of high precision JavaScript timers. High precision timing techniques were mostly used to launch CPU-level cache attacks such as [Spectre](https://spectreattack.com/spectre.pdf) and [Meltdown](https://meltdownattack.com/meltdown.pdf) from the browser. However, I am not (that) interested in cache attacks, I need high precision JavaScript timing techniques (amongst other endeavours) mostly to detect proxies and VPN usage.

However, those papers are deeply amazing. I do not think that it get's much better in the field of IT Security. The sheer human creativity demonstrated by finding those attack vectors is simply outstanding.

---

Firefox and Google Chrome reduced the precision of `performance.now()` significantly:

1. [Google Chrome reduced](https://developer.chrome.com/blog/cross-origin-isolated-hr-timers/) the `performance.now()` precision to 100 microseconds (`100µs` or `0.1ms`)
1. [Firefox reduced](https://developer.mozilla.org/en-US/docs/Web/API/Performance/now#reduced_time_precision) the `performance.now()` precision even more to 1000 microseconds (`1000µs` or `1ms`)

*Those bastards!*

High precision timers are used to launch side-channel and timing attacks. In recent years, low level vulnerabilities such as Spectre, Meltdown, Rowhammer emerged. They all have in common that the attacker needs the ability to have a high resolution timers. 

The awesome [Google Security Blog](https://security.googleblog.com/2021/03/a-spectre-proof-of-concept-for-spectre.html) explains on the page [Spectre Proof-Of-Concept website](https://leaky.page/timer.html) why:

> Before we run the Spectre proof of concept, we need a way to observe the side-effects of the transient execution. The most popular one is a cache side channel. By timing a memory access, we can infer if a chosen address is in the cache (if the access is fast) or needs to be loaded from memory (if the access is slow). Later, we will use a Spectre gadget to access a JavaScript array using a secret value as the index. Testing which array index got cached will allow us to recover that secret value.

So I learned that:

+ Timing memory accesses reveals if a chosen address is in the cache or not
+ A fast memory access means that the accessed address is cached
+ A slow memory access means that the accessed address needs to be loaded from the memory
+ In order to measure the tiny difference in access times, we need High-Precision JavaScript Timers

And then they go on...

> To be able to measure these small timing differences we need a high-precision timer. There is a great paper on this topic by Michael Schwarz, Clémentine Maurice, Daniel Gruss, and Stefan Mangard: "Fantastic Timers and Where to Find Them: High-Resolution Microarchitectural Attacks in JavaScript". One example they show is the use of a SharedArrayBuffer as a monotonic clock: increment a counter in a worker thread and read it from a second thread as a high precision timestamp. SharedArrayBuffers in particular are nowadays only available if the site is cross-origin isolated but there are many more timers described in that paper.

Unfortunately, the `SharedArrayBuffer` is no longer allowed by default. MDN says about [SharedArrayBuffer](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer#security_requirements):

> Shared memory and high-resolution timers were effectively disabled at the start of 2018 in light of Spectre. 

and if you still want to use `SharedArrayBuffer`, you will need to do the following:

> As a baseline requirement, your document needs to be in a secure context. For top-level documents, two headers will need to be set to cross-origin isolate your site: `Cross-Origin-Opener-Policy` with `same-origin` as value (protects your origin from attackers) and `Cross-Origin-Embedder-Policy` with `require-corp` as value (protects victims from your origin)

So my next idea is to try to make use of the other high precision timers presented in the paper cited above: [Fantastic Timers and Where to Find Them: High-Resolution Microarchitectural Attacks in JavaScript](https://pure.tugraz.at/ws/portalfiles/portal/17611474/fantastictimers.pdf).

Do the proposed techniques from early 2017 still work? In the next sections, I am going to test some of the techniques presented by the authors (On Ubuntu 18.04, `Chromium 95.0.4638.69`).

## Base precision of `performance.now()`

My setup:

```Bash
$ chromium-browser --version

Chromium 95.0.4638.69 Built on Ubuntu , running on Ubuntu 18.04
```

First of all, I want to confirm that the precision/resolution of `performance.now()` is really `100µs` or `0.1ms` on `Chromium 95.0.4638.69`.

This is accomplished by the below JavaScript snippet. I am collecting 10.000 `performance.now()` samples in a for-loop and I look how many unique samples are among those 10.000 collected samples, which gives me the precision.

```JavaScript
'use strict';
// The performance.now() method returns a DOMHighResTimeStamp, measured in milliseconds.
var samples = [];
var t0 = performance.now();

for (var i = 0; i < 10000; i++) {
  samples.push(performance.now());
}

var t1 = performance.now();

let diff1 = t1 - t0;
let diff2 = samples[samples.length - 1] - samples[0];

console.log('#1 Elapsed measured by performance.now(): ' + diff1 + 'ms');
console.log('#2 Elapsed measured by collected samples: ' + diff2 + 'ms');

console.log('Number of samples: ' + samples.length);
let s = new Set(samples);
console.log('Number of unique samples / measuring steps: ' + s.size);

console.log('Granularity/Precision #1 of performance.now(): ' + diff1 / s.size + 'ms');
console.log('Granularity/Precision #2 of performance.now(): ' + diff2 / s.size + 'ms');
```

As expected, the precision is almost exactly `100µs` or `0.1ms`.

```
#1 Elapsed measured by performance.now(): 15.20000000006985ms
#2 Elapsed measured by collected samples: 15.20000000006985ms
Number of samples: 10000
Number of unique samples / measuring steps: 146
Granularity/Precision #1 of performance.now(): 0.10410958904157432ms
Granularity/Precision #2 of performance.now(): 0.10410958904157432ms
```

## Building a Timer by (ab)using Web Workers

JavaScript's concurrency model is based on a single-threaded event loop. Multithreading was introduced into JavaScript with *web workers*, which run in parallel and have their own event loop.

Here, I am creating an **implicit timer** by attempting to abuse web workers to derive highly accurate timestamps. Put differently, we throw `performance.now()` into the trash and create our own timer!

Or more nuanced: We create a web worker thread and let it stupidly increase a counter and consider it an approximation of a monotomic timer.

But the [Fantastic Timers Paper](https://pure.tugraz.at/ws/portalfiles/portal/17611474/fantastictimers.pdf) lists some caveats:

> Web workers cannot post messages to other web workers (including themselves). They can only post messages to the main thread and web workers they spawn, so called sub workers.
Posting messages to the main thread again blocks the main thread’s event loop,
leaving sub web workers as the only viable option.

<a 
  class="btn"
  href="https://bot.incolumitas.com/timers/web_worker_timer.html">
Live Example of High-Precision Web Worker Timer
</a>

And this is how our implicit timer works:

1. If the worker receives a message from the main thread, it sends back its current counter value. 

2. Otherwise, the worker continuously *requests* the current counter value from the sub worker.

3. The sub worker increments the counter on each request and sends the current
value back to the worker.

And in code:

`web_worker_timer.html`:
```html
<html>
  <head></head>
  <body>
    <script>
      var ts = new Worker('subworker.js');
      var elapsed = null;

      function counter(e) {
        var count = e.data;
        if (count > 0) {
          document.write('Counter: ' + count + '<br>');
          let precision = elapsed / count;
          document.write('Precision: ' + precision + ' ms<br>');
        }
      }

      ts.addEventListener('message', counter);

      var t0 = performance.now()
      ts.postMessage(0);

      // setTimeout() acts as a method that
      // we want to time
      setTimeout(function() {
        ts.postMessage(0);
        elapsed = (performance.now() - t0);
        document.write('Elapsed Time: ' + elapsed + '<br>');
      }, 1000)
    </script>
  </body>
</html>
```

`subworker.js`:

```js
var sub = new Worker('subworker2.js');

sub.postMessage(0);

var count = 0;

sub.onmessage = msg;
onmessage = msg;

function msg(event) {
  if (event.data != 0) {
    count = event.data;
    sub.postMessage(0);
  } else {
    self.postMessage(count);
  }
}
```

`subworker2.js`:

```js
var count = 0;

onmessage = function(event) {
  count++;
  postMessage(count);
}
```

But what is the precision I am able to obtain with the above method?

```
Elapsed Time: 1000.2000000001863
Counter: 10844
Precision: 0.09223533751384971 ms
```

So this is bad news. I only manage to obtain the same precision as `performance.now()` gives us. Fail!

The authors from the [Fantastic Timers Paper](https://pure.tugraz.at/ws/portalfiles/portal/17611474/fantastictimers.pdf) claim that the achieved resolution is up to 15 μs. I only manage to get around `90µs - 100µs` with my somewhat old laptop from 2014.

However, on [browserstack.com](https://browserstack.com/), when using a real device, I manage to get results around `40µs / 50µs`, thus beating `performance.now()`

```
Elapsed Time: 1041.89999
Counter: 19083
Precision: 0.0545 ms
```

Therefore, with fast devices, the claimed `15 μs` are probably realistic!

## Recovering the high resolution of `performance.now()`

[Fantastic Timers Paper](https://pure.tugraz.at/ws/portalfiles/portal/17611474/fantastictimers.pdf) claims:

> As the underlying clock source has a high resolution, the
difference between two clock edges varies only as much as the underlying clock.
This property gives us a very accurate time base to build upon. As the time
between two edges is always constant, we interpolate the time between them.

The idea is as follows:

1. Clock interpolation requires calibration before being able to return accurate
timestamps.

2. For this purpose, a busy-wait loop to increment a
counter between two clock edges is used.

3. The time it takes to increment the counter once equals the resolution
that is recoverable. It can be approximated by dividing the interval
of two clock edges by the number of interpolation steps.


```html
<html>
  <head></head>
  <body>
    <script>
      function calibrate() {
        var counter = 0, next;

        for (var i = 0; i < 10; i++) {
          next = wait_edge();
          counter += count_edge();
        }

        next = wait_edge();

        return (wait_edge() - next) / (counter / 10.0);
      }

      function wait_edge() {
        var next, last = performance.now();

        while((next = performance.now()) == last) {

        }

        return next;
      }

      function count_edge() {
        var last = performance.now(), count = 0;

        while (performance.now() == last) {
          count++;
        }

        return count;
      }

      var sleep = function(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
      }

      async function measure() {
        var start = wait_edge();
        await sleep(1000);
        var count = count_edge();
        document.write(count + '<br>');
        return (performance.now() - start) - count * calibrate();
      }

      measure().then((res) => document.write(res));
    </script>
  </body>
</html>
```