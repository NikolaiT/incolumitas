Title: Browser Red Pills: Why are you browsing my website from AWS Lambda?
Status: published
Date: 2021-01-17 21:21
Category: Security
Tags: red pill, Bot, Advanced Bots, JavaScript, Puppeteer, Playwright
Slug: detecting-bots-with-browser-red-pills
Author: Nikolai Tschacher
Summary: Advanced bots use modern browsers and automation frameworks such as puppeteer and playwright. It becomes increasingly hard to distinguish bots from real human traffic, therefore, new methods are required.

**Please Note: This blog post is not finished yet. Research is still ongoing.**

### Introduction

Nowadays, advanced web bots become more powerful each passing day. With the help of browser automation frameworks such as [puppeteer](https://github.com/puppeteer/puppeteer) and [playwright](https://github.com/microsoft/playwright), fully fledged Chrome browsers are deployed to the cloud and programmed to automate many different work flows that are too tedious and repetitive for normal humans.

Those advanced web bots are employed for many different use cases:

+ Scraping SERP data from Search Engines such as Google, Bing or Baidu
+ Price Data scraping from sites such as Ebay or Amazon in order to gain an competitive edge
+ Advertisement Fraud: Make bots click on Advertisement Links and cash in the ad impression payout
+ Sneaker Bots: Automatically buying highly sought after goods such as limited edition Nike sneakers
+ Social Media Bots (such as Twitter Bots): Misleading and spreading false information with the aim to manipulate the consuming masses

The general tendency is very clear: A lot of behavior in the Internet is completely automated. This trend will most likely prevail and there is a [constant battle between bot programmers and anti-bot companies](https://incolumitas.com/pages/BotOrNot/).

In my humble opinion, as long as bot traffic is not causing Denial of Service issues or leading to any direct damage, it should not be legally sanctioned. After all, public data is public for a reason. So for example: Scraping public data from a site without using excessive bandwith and without causing bursts is okay. On the other hand, influencing people by creating misleading comments is not okay.

Therefore, there is a constant demand for detecting bad bot behavior. The range of available techniques is vast. Mostly however, the detection techniques can be grouped into the following categories:

+ IP Address reputation techniques
+ Browser Fingerprinting
+ Browsing Behavioral Analysis

### The Idea

For economical reasons, most bot programmers do not use their own personal computer to run their bots. The reason is obvious: The personal computer does not scale horizontally and it's unpractical to let it run constantly.

Therefore, bot owners usually rent cloud computational resources to host their bots. A popular solution is to automatically [spawn AWS EC2 instances in a docker swarm](https://github.com/NikolaiT/Crawling-Infrastructure) and to assign a certain amount of resources to each container.

Another popular approach is to use serverless computation infrastructure such as [AWS Lambda](https://aws.amazon.com/lambda/) or Microsoft Azure.

The exact method does not matter. What is common to all approaches: Each crawler gets assigned as little resources as necessary in order to save infrastructure costs.

This is in stark contrast to most human website visitors: Real humans are using their browser on their computer and rendering a website usually takes only a fraction of all available computational resources.

### Motivation

The motivation to write this blog post originates from a paper from Stanford Professor Dan Boneh and several other researchers. The paper's title is ["Tick Tock: Building Browser Red Pills from Timing Side Channels"](https://crypto.stanford.edu/~dabo/pubs/abstracts/browserRedPills.html). The paper is a really great read and I highly suggest you guys to read it.

In the paper, Boneh et. al try to find browser based techniques using only JavaScript to show that the browser is running in a virtualized environment such as within VirtualBox or VMware.

They propose different JavaScript functions of two different classes:

1. **Baseline Operations**: Those classes of algorithms are assumed to take the same execution time on bare metal computational environments as on virtual machines
2. **Differential Operations**: Those algorithms have significant execution times in virtual machines compared to normal machines.

The authors propose several techniques for the above two classes of algorithms and they successfully demonstrate that it is possible
to recognize that the Browser is running in a virtual machine with high statistical confidence.

The purpose of this blog post is to take this concept from the above paper and to find algorithms for the two algorithm classes 
that are able to tell a normal computing device (such as Laptop, Smartphone, Tablet) apart from generic cloud usage.

Put differently: Due to the restricted computational resources allocated for cloud based web pots, I suspect that it is possible to find certain algorithms that have significant different execution times compared to normal devices usually used by humans.

### Other Researches thinking into the same Direction

[Antoine Vastel](https://antoinevastel.com/) wrote in his [PhD thesis](https://tel.archives-ouvertes.fr/tel-02343930/document) submitted on 24th October 2019:

> I propose to investigate red pills, sequences of instructions that aim at detecting if a
browser is running in a virtualized environment, for bot detection. Indeed, since crawling
at scale requires a large infrastructure, a significant fraction of crawlers likely runs on
virtual machines from public cloud providers. Ho et al. proposed several red pills
capable of detecting if the host system is a virtual machine from within the browser.

> Nevertheless, the paper has been published in 2014 and has not been evaluated on popular
public cloud providers. Moreover, the underlying implementations of some of the APIs
used in the red pills may have evolved, which can impact the accuracy of the red pills.
Thus, I argue there is a need for evaluating these red pills on the main public cloud
providers and developing new red pills techniques.

### The Targeted Environment

The goal of this blog article is to detect that a browser is running in serverless cloud infrastructure.
It is assumed that the serverless environment is assigned `1500MB` of memory. 

For simplicity's sake, we will try to detect that a browser is running from withing AWS Lambda. And it should be possible
to distinguish AWS Lambda from at least the following devices:

1. Normal Laptops
2. Tablets
3. Smart Phones

The above devices must be reasonably modern, let's say not older than 6 years.

So what environmental restrictions does [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html) have?

A good start is to look at the [limits of the AWS Lambda Environment](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html).

The essential question we need to ask ourselves: **What is the best way to trigger the AWS Lambda imposed limits with JavaScript without reaching the computational limits on commonly used standard devices to browser the web (Laptop, Tablets, Smartphone)?**

It appears that AWS Lambda [does not have good GPU support](https://towardsdatascience.com/why-we-dont-use-lambda-for-serverless-machine-learning-d00038e1b242).

As of 1th December 2020, it is possible to allocate [up to 10GB of RAM and 6 vCPU cores](https://aws.amazon.com/about-aws/whats-new/2020/12/aws-lambda-supports-10gb-memory-6-vcpu-cores-lambda-functions/) for Lambda Functions. vCPU cores are allocated proportionally to the amount of RAM (between 128 MB and 10,240 MB).

### Other Detection Methods

Our goal is to detect that a browser is running from within a serverless cloud infrastructure. 

There are several other detection methods that come into mind:

### Implementation Idea

This is the basic algorithm that will be used in this blog post:

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

The text baseline writes a random text into the DOM.

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

The memory baseline. This algorithm writes `40000` times a random number 
into the memory and reads it back.

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

Console Write Differential Operation.

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

This operation writes a 500 byte random string to local storage and reads it back 
into an array. It is assumed that this operation has different running times on different computers.

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

This algorithm tests the communication latency
between the CPU and graphics card. It is assumed that generic cloud infrastructure 
does not have a GPU available for each of their users. However, most normal users 
have a GPU in their device. Therefore, it should be possible to see differentiable run times.

Due to the size of this algorithm, there will be a [link only here](https://bot.incolumitas.com/redpill/webgl.html).

### Visualization of Results

<script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"></script>

#### Memory Baseline Operation

<canvas id="bl_memory" width="600" height="400"></canvas>
<script>
var options = {
  type: 'line',
  data: {
    labels: [
   0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10,
  11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
  22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
  33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
  44, 45, 46, 47, 48, 49
],
    datasets: [
	    {
	      label: 'Baseline Memory Local',
	      data: [
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
],
      	borderWidth: 1,
        borderColor: 'rgba(255, 0, 0, 0.3)',
    	},	
			{
				label: 'Baseline Memory AWS Lamda',
				data: [
  13.095000000248547,   8.78999999986263,  8.949999999458669,
  12.715000000753207,  9.115000000747386,  9.425000000192085,
  19.864999999981592,  8.724999999913052,   9.13500000001477,
  11.300000000119326,  8.765000000039436,  17.25999999985106,
    9.13500000001477, 10.854999999992287,  8.914999999888096,
   9.360000000015134, 17.010000000027503,  8.964999999989232,
  20.645000000058644,  8.885000000191212, 13.204999999970823,
   9.434999999939464,   9.06499999996413,  8.935000000064974,
  17.075000000204454, 17.014999999901192,  8.755000000064683,
   8.619999999837091,   9.17499999991378,  8.765000000039436,
  16.079999999874417,  8.835000000090076, 17.459999999800857,
  12.999999999919964, 13.665000000173677,   8.95500000001448,
     8.7149999999383,  9.149999999863212,  8.855000000039581,
   9.310000000141372, 14.300000000048385,  13.12499999994543,
   9.144999999989523,   9.02999999993881,  9.014999999862994,
   9.270000000014988,  9.045000000014625, 12.759999999843785,
  16.129999999975553,   9.90500000011707
],
				borderWidth: 1,
        borderColor: 'rgba(0, 255, 0, 0.3)',
			}
    ],
  }, 
  options: {
    scales: {
        yAxes: [{
            ticks: {
                beginAtZero: true
            }
        }]
    }
  }
}
var ctx = document.getElementById('bl_memory').getContext('2d');
new Chart(ctx, options);
</script>

#### Text Baseline Operation

<canvas id="bl_text" width="600" height="400"></canvas>
<script>
var options = {
  type: 'line',
  data: {
    labels: [
   0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10,
  11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
  22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
  33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
  44, 45, 46, 47, 48, 49
],
    datasets: [
	    {
	      label: 'Baseline Text Local',
	      data: [
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
],
      	borderWidth: 1,
        borderColor: 'rgba(255, 0, 0, 0.3)',
    	},	
			{
				label: 'Baseline Text AWS Lambda',
				data: [
   37.06499999998414,  35.89000000010856,  39.91500000006454,
   39.90499999986241, 39.980000000014115,  43.83000000007087,
   39.23999999983607,  41.23499999991509,   39.4699999999375,
  42.519999999967695,  40.01499999981206, 37.794999999960055,
   39.43500000013955, 41.245000000117216, 37.055000000009386,
   44.55000000007203,  39.76999999986219, 39.760000000114815,
   41.62499999983993,  39.49000000011438,  37.60499999998501,
   40.59999999981301, 39.344999999912034, 41.434999999864885,
   39.14000000008855, 39.729999999963184,  39.04499999998734,
    39.5250000001397, 40.015000000039436, 39.879999999811844,
   40.26500000009037,  35.55499999993117,  39.42000000006374,
    40.1400000000649, 41.005000000041036, 39.060000000063155,
    41.3300000000163, 43.435000000044965,  39.63500000008935,
   39.95499999996355,  40.38500000001477,  39.80500000011489,
   39.64999999993779, 42.374999999992724,   39.8649999999634,
   35.60499999980493, 39.774999999963256,  35.95499999983076,
   39.82500000006439, 34.795000000030996
],
				borderWidth: 1,
        borderColor: 'rgba(0, 255, 0, 0.3)',
			}
		]
  }, 
  options: {
    scales: {
        yAxes: [{
            ticks: {
                beginAtZero: true
            }
        }]
    }
  }
}
var ctx = document.getElementById('bl_text').getContext('2d');
new Chart(ctx, options);
</script>


#### Console Differential Operation

<canvas id="do_console" width="600" height="400"></canvas>
<script>
var options = {
  type: 'line',
  data: {
    labels: [
   0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10,
  11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
  22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
  33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
  44, 45, 46, 47, 48, 49
],
    datasets: [
	    {
	      label: 'Differential Operation Console Local',
	      data: [
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
],
      	borderWidth: 1,
        borderColor: 'rgba(255, 0, 0, 0.3)',
    	},	
			{
				label: 'Differential Operation Console AWS Lambda',
				data: [
  280.05499999994754,  236.0200000000532, 272.27499999980864,
   306.4050000000407,  237.0650000000296,  263.9000000001488,
  206.92000000008193, 191.82500000010805, 280.94000000010055,
   251.5600000001541, 251.96999999980108, 183.69499999994332,
   261.7199999999684,  260.3750000000673,  192.5250000001597,
  245.05999999996675, 130.85000000000946, 123.81500000014967,
   207.2849999999562,  260.9099999999671, 178.47499999993488,
  221.73500000008062, 250.30500000002576, 224.66999999983273,
  240.76000000013664,  205.5249999998523,    246.75000000002,
   206.9850000000315, 339.81500000004417, 272.23000000003594,
  157.10500000000138, 204.81500000005326, 220.00499999990097,
  166.55999999989035,  218.3599999998478, 161.90000000005966,
   201.0400000001482, 225.19000000011147, 221.56500000005508,
  136.72999999994317, 246.03000000001884,  182.9400000001442,
  157.69999999997708,  297.7899999998499,  251.4099999998507,
  226.83499999993728, 164.45500000008906,  152.4850000000697,
  121.30000000024665,  271.9350000002123
],
				borderWidth: 1,
        borderColor: 'rgba(0, 255, 0, 0.3)',
			}
		]
  }, 
  options: {
    scales: {
        yAxes: [{
            ticks: {
                beginAtZero: true
            }
        }]
    }
  }
}
var ctx = document.getElementById('do_console').getContext('2d');
new Chart(ctx, options);
</script>


#### Local Storage Differential Operation

<canvas id="do_localstorage" width="600" height="400"></canvas>
<script>
var options = {
  type: 'line',
  data: {
    labels: [
   0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10,
  11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
  22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
  33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
  44, 45, 46, 47, 48, 49
],
    datasets: [
	    {
	      label: 'Differential Operation Localstorage Local',
	      data: [
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
],
      	borderWidth: 1,
        borderColor: 'rgba(255, 0, 0, 0.3)',
    	},	
			{
				label: 'Differential Operation Localstorage AWS Lambda',
				data: [
   19.11500000005617, 21.079999999983556,  16.65000000002692,
   20.10999999993146,  19.28000000020802,  18.71500000015658,
  28.279999999995198, 19.170000000030996,  19.61499999993066,
  19.054999999980282,  19.11500000005617, 19.594999999981155,
  22.795000000087384, 19.244999999955326,   19.1899999999805,
   19.21500000003107,   21.7649999999594,  21.58499999995911,
   21.72500000006039, 21.869999999807987, 22.890000000188593,
  27.434999999968568,  19.21500000003107, 20.009999999956563,
  16.810000000077707, 21.989999999959764,  19.81999999998152,
    19.1899999999805, 18.929999999954816, 19.880000000057407,
  22.940000000062355, 22.085000000060973, 21.610000000009677,
  19.534999999905267, 19.924999999830106, 22.590000000036525,
   18.58999999990374, 17.119999999977153,  20.20000000015898,
  21.140000000059445, 18.964999999980137,  18.90000000003056,
  21.415000000160944, 20.430000000033033, 14.715000000023792,
  23.519999999962238,  18.87999999985368,  21.08500000008462,
   18.40500000002976, 19.489999999905194
],
				borderWidth: 1,
        borderColor: 'rgba(0, 255, 0, 0.3)',
			}
		]
  }, 
  options: {
    scales: {
        yAxes: [{
            ticks: {
                beginAtZero: true
            }
        }]
    }
  }
}
var ctx = document.getElementById('do_localstorage').getContext('2d');
new Chart(ctx, options);
</script>


#### WebGL Differential Operation

<canvas id="do_webgl" width="600" height="400"></canvas>
<script>
var options = {
  type: 'line',
  data: {
    labels: [
   0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10,
  11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
  22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
  33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
  44, 45, 46, 47, 48, 49
],
    datasets: [
	    {
	      label: 'Differential Operation WebGL Local',
	      data: [
   205.8599999999584, 164.30999999997198, 151.09999999999957,
   166.5050000000008, 163.05000000002678, 141.15500000002612,
  166.55500000003087, 159.93499999997596, 165.31499999999255,
   156.6450000000117, 162.33999999997195, 193.82499999993286,
  157.66999999995335,   196.544999999972,  174.0499999999372,
  186.08499999997719,  154.7750000000434, 179.27000000000248,
  131.03999999995608, 190.90499999998656, 146.65499999992448,
   146.9950000000324, 173.29999999998336, 155.68500000017593,
  159.53500000020426, 157.53000000006523,  175.3950000000657,
  136.48999999992384, 169.66500000003748, 154.68500000014274,
  161.88000000011016, 194.89999999981933, 170.10499999994977,
  160.80999999996948, 168.57499999997572,  166.4449999999249,
   180.7499999999891, 151.15000000000123,  169.2899999999895,
  163.70000000006257, 182.30999999997266,  167.1150000000523,
  162.94499999995082, 148.23499999982914, 176.09499999994682,
  165.60000000012565, 167.57499999994252, 189.99000000007982,
  167.17000000008397, 174.82999999998583
],
      	borderWidth: 1,
        borderColor: 'rgba(255, 0, 0, 0.3)',
    	},	
			{
				label: 'Differential Operation WebGL AWS Lambda',
				data: [
   854.829999996582, 878.7300000003597, 873.0300000006537,
  863.5950000025332, 866.7700000096374, 871.6849999982514,
  867.2549999955663, 837.3700000047393, 879.4600000001083,
  878.1399999988935, 860.7549999960611, 855.2949999957491,
  868.0599999988772, 880.7199999955628, 860.8800000019983,
  859.3499999988126, 864.4700000022567, 858.4999999948195,
  857.7550000045449, 865.4550000082963, 842.7250000077038,
  854.6750000041357, 853.7799999976414, 861.3900000127614,
  862.1300000049814, 865.2100000035716, 853.7000000014814,
   860.530000005383, 854.5000000030996, 850.7299999964744,
  875.0750000017433,  845.565000005081, 852.9399999970337,
    854.36499998832,  841.245000005074, 863.7799999942217,
  870.0650000027963, 901.4749999987544, 868.7799999970593,
   879.560000003039, 885.2350000015576, 860.0699999951757,
  883.0899999975372, 842.4200000008568, 876.2749999950756,
  863.1449999957113, 860.8500000027561, 867.0449999954144,
  876.0250000050291,  866.150000008929
],
				borderWidth: 1,
        borderColor: 'rgba(0, 255, 0, 0.3)',
      },
	    {
	      label: 'do_webgl phone',
        data: [850, 836, 799, 804, 810, 859, 733, 896, 793, 799, 803, 821, 807, 779, 759, 724, 906,
        726, 846, 833, 830, 778, 770, 842, 814, 804, 783, 829, 754, 914, 748, 817, 828, 812, 810],
      	borderWidth: 1,
        borderColor: 'rgba(0, 0, 255, 0.3)',
    	},
		]
  }, 
  options: {
    scales: {
        yAxes: [{
            ticks: {
                beginAtZero: true
            }
        }]
    }
  }
}
var ctx = document.getElementById('do_webgl').getContext('2d');
new Chart(ctx, options);
</script>


### Other Sources

[Hacker News Discussion of other Red Pill techniques](https://news.ycombinator.com/item?id=20481291)