Title: Browser Red Pills: Why are you browsing my website from AWS Lambda?
Status: draft
Date: 2021-01-16 21:21
Category: Security
Tags: red pill, Bot, Advanced Bots, JavaScript, Puppeteer, Playwright
Slug: detecting-bots-with-browser-red-pills
Author: Nikolai Tschacher
Summary: Advanced bots use modern browsers and automation frameworks such as puppeteer and playwright. It becomes increasingly hard to distinguish bots from real human traffic, therefore, new methods are required.

### Introduction

Nowadays, advanced web bots are becoming extremely powerful. With the help of browser automation frameworks such as [puppeteer](https://github.com/puppeteer/puppeteer) and [playwright](https://github.com/microsoft/playwright), fully fledged Chrome browsers are deployed to the cloud and programmed to automate many different work flows that are too tedious and repetitive for normal humans.

Those advanced web bots are employed for many differ scenarios:

+ Scraping SERP data from Search Engines such as Google, Bing or Baidu
+ Price Data scraping from sites such as Ebay or Amazon in order to gain an competitive edge
+ Advertisement Fraud: Clicking on Advertisement Links
+ Sneaker Bots: Automatically buying highly sought after goods such as limited Nike sneakers
+ Social Media Bots (such as Twitter Bots): Misleading and spreading false information with the aim to manipulate the consuming masses

The general tendency is very clear: A lot of behavior in the Internet is completely automated. This trend will most likely prevail and there is a [constant battle between bot programmers and anti bot companies](https://incolumitas.com/pages/BotOrNot/).

In my humble opinion, as long as bot traffic is not causing Denial of Service issues or causing any direct damage, it should not be legally sanctioned. After all, public data is public for a reason. So for example: Scraping public data from a site with limited bandwith and without causing bursts is okay. Influencing people by creating misleading comments is bad.

Therefore, there is a constant demand for detecting bad bot behavior. The range of available techniques is vast. Mostly however, the detection techniques can be grouped into the following categories:

+ IP Address reputation
+ Browser Fingerprinting
+ Behavioral Analysis

### The Idea

For economical reasons, most bot programmers do not use their own personal computer to run their bots. The reason is obvious: The personal computer does not scale and cannot be constantly online.

Therefore, bot owners usually rent cloud computational resources to host their bot. A popular solution is to automatically [spawn AWS EC2 instances in a docker swarm](https://github.com/NikolaiT/Crawling-Infrastructure) and to assign a certain amount of resources to each container.

Another popular approach is to use serverless computation such as [AWS Lambda](https://aws.amazon.com/lambda/) or Microsoft Azure.

The exact method does not matter. What is common to all approaches: Each crawler gets assigned as little resources as necessary in order to save infrastructure costs.

This is in stark contrast to most human website visitors: They are using their browser on their computer and rendering a website usually takes only a fraction of all available computational resources.

### Influence

Antoine Vastel wrote in his thesis submitted on 24th October 2019:

> I propose to investigate red pills, sequences of instructions that aim at detecting if a
browser is running in a virtualized environment, for bot detection. Indeed, since crawling
at scale requires a large infrastructure, a significant fraction of crawlers likely runs on
virtual machines from public cloud providers. Ho et al. proposed several red pills
capable of detecting if the host system is a virtual machine from within the browser.
Nevertheless, the paper has been published in 2014 and has not been evaluated on popular
public cloud providers. Moreover, the underlying implementations of some of the APIs
used in the red pills may have evolved, which can impact the accuracy of the red pills.
Thus, I argue there is a need for evaluating these red pills on the main public cloud
providers and developing new red pills techniques.

### Implementation Idea

The Red Pill template

```JavaScript
function redpill() {
  var baseStart = performance.now();
  baselineOperation();
  var baseTime = performance.now() - baseStart;
  console.log('baseTime: ' + baseTime);

  var diffStart = performance.now();
  differentialOperation();
  var diffTime = performance.now() - diffStart;
  console.log('diffTime: ' + diffTime);

  return diffTime / baseTime ;
}
```

### Baseline Operations

The text baseline:

```JavaScript
function textBaseline() {
  var addString = "Writes lots of text:"
  addString += Math.floor(Math.random() * 10000);

  var pNode = document.createElement("p");
  document.body.appendChild(pNode);

  for (var i = 0; i < 500; i++) {
    pNode.innerHTML = pNode.textContent + addString;
  }
}

var baseStart = performance.now();
textBaseline();
var baseTime = performance.now() - baseStart;
console.log('baseTime: ' + baseTime);
```

The memory baseline:

```JavaScript
function memoryBaseline() {
  var RANDOM = Math.floor(Math.random() * 1000000);

  var array = new Array();
  for (var i = 0; i < 40000; i++) {
    array.push(new Number(RANDOM));
  }

  for (var i = 0; i < 40000; i++) {
    array.pop();
  }
}

var baseStart = performance.now();
memoryBaseline();
var baseTime = performance.now() - baseStart;
console.log('baseTime: ' + baseTime);
```

### Differential Operations

Console Write Differential Operation

```JavaScript
function consoleOperation() {
  var error_str = "Error: Writing to Console: " + Math.floor(Math.random() * 10000);
  for (var i = 0; i < 2000; i++) {
    console.log(error_str);
  }
}

var diffStart = performance.now();
consoleOperation();
var diffTime = performance.now() - diffStart;
console.log('diffTime: ' + diffTime);
```

Local Storage Differential Operation

Local Storage. HTML 5 introduces the local storage feature, which allows websites to store several
megabytes of data persistently on disk. Similar to our
console red pills, we created six different versions of local storage red pills.

These six versions randomly generate and write a string to local storage for 100, 200, 400,
800, 1600, and 3200 repetitions; each string is 500 character longs. After all strings have been written to local
storage, the operation then iterates over the local storage
and reads each String back into an array. We measure
this operation’s time from before the first write (but after
all the strings are generated) to after the last string is read
from local storage.

```JavaScript
function localStorageOperation() {
  var randomStr = "x".repeat(495) + Math.random().toString().slice(2, 7);
  var data = new Array();
  for (var i = 0; i < 1000; i++) {
    localStorage.setItem('lsDO' + i, randomStr);
  }

  for (var i = 0; i < 1000; i++) {
    data.push(localStorage.getItem('lsDO' + i));
  }
}

var diffStart = performance.now();
localStorageOperation();
var diffTime = performance.now() - diffStart;
console.log('diffTime: ' + diffTime);
```

ReadPixels Differential Operation CPU - GPU Communication

Finally, we constructed two more red pills by leveraging
the WebGL API, which allows webpages to create com-
plex graphics and games through OpenGL.

We constructed a red pill that tests the communication latency
between the CPU and graphics card of a website’s visitor.
This red pill renders and randomly rotates ten triangles with a basic mesh pattern (default shaders and texture) multiple times. After each render call, we used We-
bGL’s readPixels() method to load the pixel bitmap from
the visitor’s GPU into an array (the visitor’s main mem-
ory). We tested this differential operation with 40, 80,
160, and 320 render (readPixels) calls. We measured this
operation’s time from the start of the first readPixels call
to after the last readPixels call.


```JavaScript
function webGLOperation() {
}

var diffStart = performance.now();
webGLOperation();
var diffTime = performance.now() - diffStart;
console.log('diffTime: ' + diffTime);
```


### Data Local OS

bl_memory.html

```
bl_memory.html [
   36.43499999998312,  17.12499999999295,  17.31000000000904,
  19.140000000021473, 17.165000000005648,   17.6050000000032,
   21.27500000000282, 19.634999999993852,  17.45499999998401,
   19.34500000001549,  16.14000000000715,  16.91500000001156,
  17.760000000009768, 17.380000000002838, 16.390000000001237,
  14.525000000020327, 22.500000000007958,   20.6500000000176,
   17.41000000001236, 22.305000000017117, 17.394999999993388,
   17.19499999998675, 17.034999999992806, 18.585000000001628,
   17.35999999999649, 18.660000000011223, 17.780000000016116,
  18.124999999997726,  26.61000000000513,  14.90000000001146,
  15.895000000000437,  17.77500000002874, 18.970000000024356,
  19.054999999980282,  18.74499999996715, 15.405000000043856,
   17.45499999998401, 19.099999999980355, 18.705000000011296,
  16.675000000020646,  15.73999999999387,  21.00999999998976,
  18.224999999972624, 18.190000000004147, 20.525000000020555,
   17.56000000000313, 16.265000000032614,  16.25500000000102,
   18.03499999999758, 18.020000000035452
]
```

bl_text.html

```
bl_text.html [
   42.11500000008073, 43.679999999994834, 41.200000000003456,
   40.68500000005315,  45.10000000004766,  41.66999999995369,
   43.13000000001921,  45.03499999998439,  47.60499999997592,
    45.0149999999212,  42.34499999995478,  44.12000000002081,
   40.93000000000302,  46.08500000006188, 43.895000000020445,
  38.904999999999745,  42.45500000001812,  44.61000000003423,
   41.18500000004133, 42.374999999992724,   43.8649999999825,
   43.50499999998192,  43.32499999998163,  44.91500000005999,
   43.03000000004431, 45.745000000010805,  44.80999999998403,
   45.16999999998461, 43.400000000019645, 42.955000000006294,
   46.49500000004991,  42.50999999999294,  40.56500000001506,
  44.475000000034015,  44.90499999997155,  44.09999999995762,
   42.53500000004351,  45.43499999999767,  43.43000000005759,
   42.39499999994223, 44.089999999982865,  41.59000000004198,
   46.06999999998607,  47.10499999998774, 42.430000000081236,
   48.18000000000211, 44.510000000059335,  42.96999999996842,
   43.97000000005846, 45.649999999909596
]
```

do_console.html

```
do_console.html [
  165.11000000002696,  154.6650000000227, 162.59999999999764,
  177.55499999998392, 178.28499999995984, 165.11000000002696,
  157.62999999992644, 165.31499999996413, 159.43000000004304,
  153.81999999999607,  182.8249999999798,  157.6350000000275,
  151.70499999999265, 163.01999999996042, 153.80000000004657,
  153.13999999989392, 154.56499999993412, 152.85999999991873,
  161.71999999994568, 162.93499999994765, 166.89999999994143,
  152.48000000008233, 148.12500000005002, 161.64000000003398,
  160.59000000007018, 162.30499999994663,  155.3399999999101,
  159.84500000001844, 155.90499999996155, 149.13500000000113,
  151.25000000000455, 170.18499999994674, 147.96000000001186,
  157.48499999995147,   157.615000000078,    156.58499999995,
  139.79500000004919,  154.3699999999717,  155.5749999999989,
   143.5550000001058, 153.16999999981817, 150.71000000011736,
  162.87499999998545, 161.70999999985725,  157.9300000000785,
   164.3549999998868, 163.56499999983498,  157.4950000001536,
  156.34000000000015,  153.7550000000465
]
```

do_localstorage.html

```
do_localstorage.html [
   42.50000000001819,  46.99500000015178, 47.795000000178334,
   54.47499999991123,  46.26500000017586,  47.15999999984888,
   47.19000000000051,  50.50000000005639,  47.21500000005108,
   52.86999999998443,  48.74499999982618, 38.105000000086875,
  44.390000000021246, 47.410000000127184, 46.965000000000146,
   49.38500000002932,   45.4650000001493,  46.13499999982196,
  50.975000000107684,  45.54000000007363,  52.20499999995809,
   45.74999999999818,  47.16499999994994,  48.54000000000269,
   43.53999999989355,  49.18499999985215,  47.52499999995052,
   47.09000000002561,  46.68500000002496,   48.2600000000275,
   45.03500000009808, 47.480000000177824,  46.52000000010048,
  54.575000000113505,   43.7050000000454,  52.79999999993379,
  50.695000000132495, 49.854999999979555,  48.07499999992615,
  49.409999999852516,  48.99000000000342,  47.12000000017724,
   47.93499999982487, 51.120000000082655,  47.00500000012653,
  54.694999999810534,  40.65500000001521,  45.22999999994681,
  50.585000000182845,  44.64000000007218
]
```

### Data AWS Lambda

restart browser between runs!


do_console.html

```
do_console.html [
  243.94500000016706, 139.3050000006042, 180.92000000069675, 196.53000000107568, 154.8399999992398, 170.00499999994645,
  222.2299999993993, 221.41000000010536, 212.79999999933352, 153.79500000017288, 227.1550000004936, 242.37499999981083,
  258.2750000001397, 291.1649999987276,
]
```

do_localstorage.html

```
do_localstorage.html [
  16.929999999774736, 16.60999999876367, 17.174999999042484, 17.50499999980093, 17.259999998714193, 8.885000001100707,
  13.940000000729924, 11.860000000524451,
]
```

bl_memory.html

```
bl_memory.html [
  14.605000000301516, 17.459999999118736, 10.355000000345171, 18.195000000559958, 17.015000001265435, 21.99500000097032,
]
```

bl_text.html

```
bl_text.html [
  39.59000000031665, 39.5699999990029, 39.94499999862455, 40.070000000923756, 45.180000000982545, 41.884999998728745,
  39.844999999331776, 39.96000000006461, 39.51500000039232, 40.235000000393484,
]
```
