Title: On High-Precision JavaScript Timers
Status: published
Date: 2021-12-05 20:40
Category: Security
Tags: spectre, meltdown, cache-attacks, high-precision-timing, JavaScript
Slug: on-high-precision-javascript-timers
Author: Nikolai Tschacher
Summary: I in this blog post, I am investigating the current state of high precision JavaScript timers. High precision timing techniques were mostly used to launch CPU-level cache attacks such as Spectre and Meltdown from the browser. I am interested in other use cases though...

## Introduction

I in this blog post, I am investigating the current state of high precision JavaScript timers. High precision timing techniques were mostly used to launch CPU-level cache attacks such as [Spectre](https://spectreattack.com/spectre.pdf) and [Meltdown](https://meltdownattack.com/meltdown.pdf) from the browser. However, I am not (that) interested in cache attacks, I need high precision JavaScript timing techniques (amongst other endeavours) mostly  to detect proxies and VPN usage.

However, those papers are deeply amazing. I do not think that it get's much more better in IT Security. The sheer human creativity demonstrated by finding those attack paths is outstanding.

---

My setup:

```Bash
$ chromium-browser --version

Chromium 95.0.4638.69 Built on Ubuntu , running on Ubuntu 18.04
```

Firefox and Google Chrome reduced the precision of `performance.now()` significantly:

1. [Google Chrome reduced](https://developer.chrome.com/blog/cross-origin-isolated-hr-timers/) the `performance.now()` precision to 100 microseconds (`100µs` or `0.1ms`)
1. [Firefox reduced](https://developer.mozilla.org/en-US/docs/Web/API/Performance/now#reduced_time_precision) the `performance.now()` precision even more to 1000 microseconds (`1000µs` or `1ms`)


High precision timers are used to launch side-channel and timing attacks. In recent years, low level vulnerabilities such as Spectre, Meltdown, Rowhammer emerged. They all have in common that the attacker needs the ability to have a high resolution timers. 

The awesome [Google Security Blog](https://security.googleblog.com/2021/03/a-spectre-proof-of-concept-for-spectre.html) explains on the page [Spectre Proof-Of-Concept website](https://leaky.page/timer.html) why:

> Before we run the Spectre proof of concept, we need a way to observe the side-effects of the transient execution. The most popular one is a cache side channel. By timing a memory access, we can infer if a chosen address is in the cache (if the access is fast) or needs to be loaded from memory (if the access is slow). Later, we will use a Spectre gadget to access a JavaScript array using a secret value as the index. Testing which array index got cached will allow us to recover that secret value.

So I learned that:

+ Timing memory accesses reveals if a chosen address is in the cache or not
+ Fast memory accesses means that the accessed address is cached
+ Slow memory accesses means that the accessed address needs to be loaded from the memory
+ In order to measure the tiny difference in access times, we need High-Precision JavaScript Timers

And then they go on...

> To be able to measure these small timing differences we need a high-precision timer. There is a great paper on this topic by Michael Schwarz, Clémentine Maurice, Daniel Gruss, and Stefan Mangard: "Fantastic Timers and Where to Find Them: High-Resolution Microarchitectural Attacks in JavaScript". One example they show is the use of a SharedArrayBuffer as a monotonic clock: increment a counter in a worker thread and read it from a second thread as a high precision timestamp. SharedArrayBuffers in particular are nowadays only available if the site is cross-origin isolated but there are many more timers described in that paper.

Unfortunately, the `SharedArrayBuffer` is no longer allowed by default. MDN says about [SharedArrayBuffer](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer#security_requirements):

> Shared memory and high-resolution timers were effectively disabled at the start of 2018 in light of Spectre. 

and if you still want to use `SharedArrayBuffer`, you will need to do the following:

> As a baseline requirement, your document needs to be in a secure context. For top-level documents, two headers will need to be set to cross-origin isolate your site: `Cross-Origin-Opener-Policy` with `same-origin` as value (protects your origin from attackers) and `Cross-Origin-Embedder-Policy` with `require-corp` as value (protects victims from your origin)


So my first idea is to try to make use of the high precision timers presented in the above cited paper from early 2017: [Fantastic Timers and Where to Find Them: High-Resolution Microarchitectural Attacks in JavaScript](https://pure.tugraz.at/ws/portalfiles/portal/17611474/fantastictimers.pdf).

Do they still work? In the next sections I am going to test some of the techniques presented by this paper.

## Base precision/resolution of performance.now()

First of all, I want to confirm that the precision/resolution of `performance.now()` is really `100µs` or `0.1ms`.

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

As expected, the precision is almost exactly `100µs`.

```
#1 Elapsed measured by performance.now(): 18.199999999254942ms
#2 Elapsed measured by collected samples: 18.199999999254942ms
Number of samples: 10000
Number of unique samples / measuring steps: 183
Granularity/Precision #1 of performance.now(): 0.09945355190849695ms
Granularity/Precision #2 of performance.now(): 0.09945355190849695ms
```