Title: On High-Precision JavaScript Timers
Status: draft
Date: 2021-01-12 12:40
Category: Security
Tags: spectre, meltdown, cache-attacks, high-precision-timing, JavaScript
Slug: on-high-precision-javascript-timers
Author: Nikolai Tschacher
Summary: The current state of high precision JavaScript timers.

In this blog article I am investigating high-precision JavaScript timers.

Firefox and Google Chrome reduced the precision of `performance.now()` significantly:

1. [Google Chrome reduced](https://developer.chrome.com/blog/cross-origin-isolated-hr-timers/) the `performance.now()` precision to 100 microseconds (`100µs` or `0.1ms`)
1. [Firefox reduced](https://developer.mozilla.org/en-US/docs/Web/API/Performance/now#reduced_time_precision) the `performance.now()` precision to 1000 microseconds (`1000µs` or `1ms`)


High precision timers are used to launch side-channel and timing attacks. In recent years, low level vulnerabilities such as Spectre, Meltdown, Rowhammer emerged. They all have in common, that the attacker needs the ability to have a high resolution timer. 

The awesome [Spectre-Proof-of-Concept web page](https://security.googleblog.com/2021/03/a-spectre-proof-of-concept-for-spectre.html) presents:

[https://leaky.page/timer.html](https://leaky.page/timer.html):

> Before we run the Spectre proof of concept, we need a way to observe the side-effects of the transient execution. The most popular one is a cache side channel. By timing a memory access, we can infer if a chosen address is in the cache (if the access is fast) or needs to be loaded from memory (if the access is slow). Later, we will use a Spectre gadget to access a JavaScript array using a secret value as the index. Testing which array index got cached will allow us to recover that secret value.

> To be able to measure these small timing differences we need a high-precision timer. There is a great paper on this topic by Michael Schwarz, Clémentine Maurice, Daniel Gruss, and Stefan Mangard: "Fantastic Timers and Where to Find Them: High-Resolution Microarchitectural Attacks in JavaScript". One example they show is the use of a SharedArrayBuffer as a monotonic clock: increment a counter in a worker thread and read it from a second thread as a high precision timestamp. SharedArrayBuffers in particular are nowadays only available if the site is cross-origin isolated but there are many more timers described in that paper.

So my first idea is to try to make use of the high precision timers presented in the above cited paper from early 2017: [Fantastic Timers and Where to Find Them: High-Resolution Microarchitectural Attacks in JavaScript](https://pure.tugraz.at/ws/portalfiles/portal/17611474/fantastictimers.pdf).

Do they still work?