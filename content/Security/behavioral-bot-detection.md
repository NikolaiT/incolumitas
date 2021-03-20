Title: Behavioral Analysis for Bot Detection
Date: 2021-03-20 23:39
Category: Security
Tags: Behavioral Analysis, Bot Detection, 
Slug: bot-detection-with-behavioral-analysis
Author: Nikolai Tschacher
Summary: Behavioral analysis is an interesting approach to detect bots. It surely is not the panacea for bot detection, but it certainly is an useful extension in your bot hunting tool belt.

## Introduction

Bots are programs created by humans to automate repetitive tasks in the Internet. In the widest sense, the emergence of bots is a manifestation of the process of worldwide automatization that we currently experience in our modern times.

Some Examples of Bots:

1. Sometimes bots only scrape Google or Amazon
2. Some bots [buy highly sought after Nike sneakers](https://antoinevastel.com/javascript/2019/08/31/sneakers-supreme-bots.html) immediately after release
3. Other bots purchase PlayStation 5 consoles from official vendor stores as soon as they are restocked. This happens before legitimate users have a change to buy a PS5 console (Scalping)
4. Other bots automate banking transactions in order to disintermediate banks

My conjecture is: Automated programs behave not the same as real human beings.

What to I mean with that from a technical perspective?

The idea is to record the following JavaScript events from every website user:

+ Events indicating page load - [load](https://developer.mozilla.org/en-US/docs/Web/API/Window/load_event) / [DOMContentLoaded](https://developer.mozilla.org/en-US/docs/Web/API/Window/DOMContentLoaded_event)
+ User switches the tab - [visibilitychange](https://developer.mozilla.org/en-US/docs/Web/API/Document/visibilitychange_event)
+ Mouse events - [mousedown / mouseup](https://developer.mozilla.org/en-US/docs/Web/API/Element/mousedown_event) and [mousemove](https://developer.mozilla.org/en-US/docs/Web/API/Element/mousemove_event)
+ Scroll events - [scroll](https://developer.mozilla.org/en-US/docs/Web/API/Element/scroll)
+ Mobile Touch Events - [touchstart / touchend](https://developer.mozilla.org/en-US/docs/Web/API/Touch_events) and [touchmove](https://developer.mozilla.org/en-US/docs/Web/API/Document/touchmove_event)
+ Keyboard events - [keydown / keyup](https://developer.mozilla.org/en-US/docs/Web/API/Document/keydown_event)
+ Events indicating the unloading of the page - [pagehide](https://developer.mozilla.org/en-US/docs/Web/API/Window/pagehide_event) / [unload](https://developer.mozilla.org/en-US/docs/Web/API/Window/unload_event) / [beforeunload](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event)

Each of the above events is assigned a timestamp obtained with `performance.now()`.

The above process yields a time series of behavioral interaction data such as for example:

```JavaScript
[
  ["dcl",1,665.72],["s",0,3265,1,730.785],["s",0,3265,1,897.025],["s",0,3286,1,984],["lo",1,1039.395],["s",0,3540,1,1040.78],["s",0,3561,1,1051.26],["s",0,3561,1,1062.775],["m",1053,199,2973,300,0,"0000",1,1488.325],["m",1050,201,2970,302,0,"0000",1,1496.05],["m",1019,214,2939,315,0,"0000",1,1512.66],["m",951,243,2871,344,0,"0000",1,1529.29],["m",845,277,2765,378,0,"0000",1,1546.015],["m",717,313,2637,414,0,"0000",1,1562.555],["m",585,337,2505,438,0,"0000",1,1578.15],
  ["m",463,357,2383,458,0,"0000",1,1595.69],["m",361,373,2281,474,0,"0000",1,1611.97],["m",291,375,2211,476,0,"0000",1,1628.015],["m",247,369,2167,470,0,"0000",1,1645.06],["m",241,363,2161,464,0,"0000",1,1662.015],["m",241,350,2161,451,0,"0000",1,1679.215],["m",257,323,2177,424,0,"0000",1,1695.82],["m",295,287,2215,388,0,"0000",1,1712.785],["m",355,263,2275,364,0,"0000",1,1729.085],["m",445,247,2365,348,0,"0000",1,1746.455],["m",561,247,2481,348,0,"0000",1,1762.92],["m",697,253,2617,354,0,"0000",1,1778.59],["m",817,269,2737,370,0,"0000",1,1795.34],["m",915,283,2835,384,0,"0000",1,1812.275],["m",983,293,2903,394,0,"0000",1,1829.455],["m",1025,305,2945,406,0,"0000",1,1845.63],["m",1045,313,2965,414,0,"0000",1,1863.225],["m",1047,314,2967,415,0,"0000",1,2086.09]
  ,["m",1047,317,2967,418,0,"0000",1,2095.995],["m",1047,319,2967,420,0,"0000",1,2113.245],["m",1046,323,2966,424,0,"0000",1,2129.86],["m",1046,324,2966,425,0,"0000",1,2146.645],["m",1046,329,2966,430,0,"0000",1,2162.54],["m",1045,333,2965,434,0,"0000",1,2179.16],["m",1045,334,2965,435,0,"0000",1,2198.62],["m",1041,335,2961,436,0,"0000",1,2423.58],["m",1030,335,2950,436,0,"0000",1,2431.07],["m",1005,329,2925,430,0,"0000",1,2446.315],["m",887,299,2807,400,0,"0000",1,2463.15],["m",793,269,2713,370,0,"0000",1,2479.685],["m",695,245,2615,346,0,"0000",1,2496.445],["m",617,221,2537,322,0,"0000",1,2512.475],["m",553,193,2473,294,0,"0000",1,2530.245],["m",507,173,2427,274,0,"0000",1,2545.655],["m",475,155,2395,256,0,"0000",1,2563.26],["m",459,147,2379,248,0,"0000",1,2579.82],
  ["m",458,145,2378,246,0,"0000",1,2596.655],["m",456,143,2376,244,0,"0000",1,2671.46],["m",449,140,2369,241,0,"0000",1,2679.625],["m",434,137,2354,238,0,"0000",1,2695.88],["m",415,135,2335,236,0,"0000",1,2712.485],["m",398,132,2318,233,0,"0000",1,2729.495],["m",382,130,2302,231,0,"0000",1,2746.1],["m",369,126,2289,227,0,"0000",1,2762.54],["m",357,121,2277,222,0,"0000",1,2779.69],["m",353,117,2273,218,0,"0000",1,2796.41],["m",347,112,2267,213,0,"0000",1,2813.59],["m",342,104,2262,205,0,"0000",1,2829.67],["m",340,94,2260,195,0,"0000",1,2846.54],["m",340,82,2260,183,0,"0000",1,2863.09],["m",340,74,2260,175,0,"0000",1,2879.195],["m",340,68,2260,169,0,"0000",1,2896.52],
  ["m",343,63,2263,164,0,"0000",1,2913.185],["m",349,56,2269,157,0,"0000",1,2929.87],["m",356,49,2276,150,0,"0000",1,2945.855],["m",360,42,2280,143,0,"0000",1,2962.555],["m",363,38,2283,139,0,"0000",1,2979.245],["m",363,36,2283,137,0,"0000",1,2995.905],["m",363,35,2283,136,0,"0000",1,3013.1],["m",363,32,2283,133,0,"0000",1,3030.145],["m",364,30,2284,131,0,"0000",1,3045.57],
  ["m",365,24,2285,125,0,"0000",1,3063.08],["m",367,18,2287,119,0,"0000",1,3079.46],["m",369,11,2289,112,0,"0000",1,3096.24],["m",371,4,2291,105,0,"0000",1,3112.335],["m",371,2,2291,103,0,"0000",1,3126.395],
  ["bu",1,5056.1],["ph",false,1,5105.305],["vc","hidden",1,5105.48],["ul",1,5105.625],["wsEnd",null,5105.625]
]
```

where

1. `s` stands for `scroll` event
2. `m` stands for `mousemove`
3. `dcl` is the `domcontentloaded` event
4. `vc` is the `visibilitychange` event
5. The last array element is always the timestamp obtained with `performance.now()`. So for example in the frame `["s",0,3561,1,1062.775]`, 1062.775 is the timestamp.


## How to Detect Bots with Behavioral Analysis?

Humans behave like a chaotic systems.

Humans move their mouse, keyboard, touch screen and scrolling wheel in an organic fashion. Bots still have a hard time to mimic mouse movements and touchscreen taps like real humans.

A simple process to distinguish bots from real humans based on behavioral data could look like the following:

1. The first step is to collect and extract certain features from a huge set of recorded behavioral data samples. 
2. The next (and way harder) step is to label the data set as either human or bot-like. This requires to have enough samples from both categories.
3. The last step requires to train a neuronal network. This allows us to accurately classify live behavior samples just in time.

That is way easier said than done. However, there are some companies such as [biocatch](https://www.biocatch.com/) and [perimeterx](https://www.perimeterx.com/) that are already using this approach since years.

But what exactly makes mouse or touch event interaction in a browser *human*? What are features that are extremely hard to emulate mechanically? Some rough ideas (replace *mouse* with touch events in case of mobile devices):

- The mouse is used as a reading aid (observe yourself *right now*)
- The start and stop speed of the mouse between points of interest
- The trajectory of mouse movements
- The distribution of events over time. Humans look at the screen, process the information visually and react physically. This pattern repeats all the time. The latency in such reaction patterns is intrinsically human.
- Time interval between `mousedown` and `mouseup` events
- The interval between `keydown` and `keyup` events depends heavily on the writing skills of the human
- Timing statistics when typing: Pressing two identical letters almost always is faster in the second letter.
- Mouse follows the eye focus point
- Scrolling speed correlates with reading speed
- spikes in behavioral data when a website requires interaction
- mouse moves to the top (tabs) when navigating away (not in mobile)
- mobile only: sometimes screen dimensions plummets 180 degrees on auto-rotate
- on disinterest, mouse races very fast to the "close tab" button
- Areas of interest in text are highlighted
- ...?

The established method to distinguish humans from bots is the good old captcha. However, we are approaching an age where [captchas can be solved](https://incolumitas.com/2021/01/02/breaking-audio-recaptcha-with-googles-own-speech-to-text-api/) better by AI than by real humans.


## Limitations of Behavioral Bot Detection

There are some limitations regarding bot detection with behavioral analysis:

1. Behavioral analysis takes some sampling time before there is enough data to properly classify the recorded behavior. Put differently: When only considering behavioral analysis, bots can wreak havoc in the first initial seconds after page load (Let's say 0 - 5 seconds).

2. What happens when a bot injects behavioral data that was recorded somewhere else (for example on the attackers own website)? Without knowing the intent of the behavioral data, it is impossible to detect that the recorded behavior is human but from *somewhere else*.

3. Sometimes there just is no behavioral data to analyze. Sometimes Internet users open a web page for later (for example with the middle pointer of the mouse) but never chose to interact with the website.