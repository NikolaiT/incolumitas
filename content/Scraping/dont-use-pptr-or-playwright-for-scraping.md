Title: Avoid Puppeteer or Playwright for Web Scraping
Date: 2021-05-20 22:26
Modified: 2021-05-25 14:50
Category: Scraping
Tags: web scraping, crawling, puppeteer, playwright, CDP
Slug: avoid-puppeteer-and-playwright-for-scraping
Author: Nikolai Tschacher
Summary: In this blog post I explain why it is best to avoid puppeteer and playwright for web scraping.

<a class="btn" href="https://github.com/NikolaiT/stealthy-scraping-tools" style="padding: 10px; font-weight: 600; font-size: 15px;">Stealthy-scraping-tools repo on GitHub</a>

## Introduction

I don't suggest to use Puppeteer and Playwright for web scraping.

The reasons are very simple: 

1. Both libraries use pre-shipped chromium binaries that are not used by the ordinary Internet users for normal web browsing. For example, the current `puppeteer@v9.0.0` release uses the chromium version `Chromium 91.0.4469.0 (r869685)`. I doubt that this exact subversion is used by a substantial part of Internet users for their everyday browsing. 
2. It is possible to detect that a browser is automated by those libraries based on many different behaviors that are unique to puppeteer or playwright.
3. Puppeteer/Playwright use Chromium. Most people use Google Chrome though. There are some [minor differences](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/chromium_browser_vs_google_chrome.md) between those two Chrome browsers. However, Chrome is used way more often than Chromium!!!

For example, puppeteer uses a [plethora of command line flags](https://github.com/puppeteer/puppeteer/blob/d01aa6c84a1e41f15ffed3a8d36ad26a404a7187/src/node/Launcher.ts#L160) that you normally would not use when you launch a browser:

```JavaScript
defaultArgs(options: BrowserLaunchArgumentOptions = {}): string[] {
  const chromeArguments = [
    '--disable-background-networking',
    '--enable-features=NetworkService,NetworkServiceInProcess',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-breakpad',
    '--disable-client-side-phishing-detection',
    '--disable-component-extensions-with-background-pages',
    '--disable-default-apps',
    '--disable-dev-shm-usage',
    '--disable-extensions',
    '--disable-features=Translate',
    '--disable-hang-monitor',
    '--disable-ipc-flooding-protection',
    '--disable-popup-blocking',
    '--disable-prompt-on-repost',
    '--disable-renderer-backgrounding',
    '--disable-sync',
    '--force-color-profile=srgb',
    '--metrics-recording-only',
    '--no-first-run',
    '--enable-automation',
    '--password-store=basic',
    '--use-mock-keychain',
    // TODO(sadym): remove '--enable-blink-features=IdleDetection'
    // once IdleDetection is turned on by default.
    '--enable-blink-features=IdleDetection',
  ];
  const {
    devtools = false,
    headless = !devtools,
    args = [],
    userDataDir = null,
  } = options;
  if (userDataDir)
    chromeArguments.push(`--user-data-dir=${path.resolve(userDataDir)}`);
  if (devtools) chromeArguments.push('--auto-open-devtools-for-tabs');
  if (headless) {
    chromeArguments.push('--headless', '--hide-scrollbars', '--mute-audio');
  }
  if (args.every((arg) => arg.startsWith('-')))
    chromeArguments.push('about:blank');
  chromeArguments.push(...args);
  return chromeArguments;
}
```

But there is more. The DOM and the window object of each page that is created with each call to `await browser.newPage()` sets up some puppeteer/playwright specific properties that are easy to detect. The easiest to detect is probably `navigator.webdriver` (even though I am not sure if puppeteer still uses this).

But aren't there npm modules such as [puppeteer-extra-plugin-stealth](https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth) that are specifically developed to hide the fact that puppeteer is used? 

Yes they exist, but they are very limited in their efficacy. It's just very hard to make puppeteer/playwright unseen once you use it.

And there is another reason why I suggest to keep the usage of the [Chrome DevTools](https://developer.chrome.com/docs/devtools/) protocol as low as possible if you want to scrape undetected: Each command is sent over a WebSocket channel to the browser and a response is sent back. There is some inherent latency involved! I am not sure about it, but I assume that it must be possible to detect the usgage of puppeteer functionality such as 

1. `page.waitForSelector(selector[, options])` [Source](https://github.com/puppeteer/puppeteer/blob/main/docs/api.md#pagewaitforselectorselector-options)
2. `page.waitForNavigation([options])` [Source](https://github.com/puppeteer/puppeteer/blob/main/docs/api.md#pagewaitfornavigationoptions)

because Bots usually do *some action* right after a certain selector emerges. Humans don't really care about xpath or css selectors.

If you stroll through the [puppeteer API page](https://github.com/puppeteer/puppeteer/blob/main/docs/api.md), you also see [stuff](https://github.com/puppeteer/puppeteer/blob/main/docs/api.md#pagegotourl-options) such as:

> NOTE Headless mode doesn't support navigation to a PDF document. See the [upstream issue](https://bugs.chromium.org/p/chromium/issues/detail?id=761295).

Another idea: Create a detection page that redirects the browser to a site serving a PDF document. If it cannot be deliverered, it might have been headless Chrome. Using express, such a headless Chrome trap could look like this:

```JavaScript
app.get('/headlessTrap', (req, res) => {
  // sends http header: Location: /example.pdf
  res.redirect('/example.pdf');
});

app.get('/example.pdf', (req, res) => {
  var data =fs.readFileSync(path.join(__dirname, 'public/dummy.pdf'));
  res.contentType("application/pdf");
  res.set('Refresh','1; url=/goal')
  res.status(666).send(data);
});

// when reaching this, not a bot
app.get('/goal', (req, res) => {
  res.set('Content-Type', 'text/html');
  res.send('<html><body><h1>All GOOD</h1></body></html>');
});
```

## So what is the solution?

The problem is that every scraping developer is either using puppeteer or playwright to create their bots. Therefore, all that the detectors have to do is to detect puppeteer or playwright - they don't have to detect bot like behavior in general, it's enough to detect the standard browser automation framework.

My suggestion is: **Ditch the browser automation frameworks altogether!**

Think about it: What do I really need for basic browser automation in order to scrape a website?

All that is required for robust browser automation is a straightforward way to find the coordinates for CSS selectors and a way to obtain the HTML code of the current website.

### Obtaining Coordinates for a CSS selector

Put differently, we need a way to implement the following function:

```JavaScript
function (css_selector: string) {
  return {x: number, y: number} 
}
```

All the clicks, filling out forms, scrolling and other browser automation is done with desktop level browser automation instead of puppeteer's `page.click()`, `page.type()` and so on.

We only require the [CDP](https://chromedevtools.github.io/devtools-protocol/) to translate CSS selectors into coordinates. 

That can be done with the help of the small CDP library `chrome-remote-interface`.

After saving the following script as `coords.js`, you may invoke it to obtain the absolute coordinates for any element by specifying a css selector.

`node coords.js 'div'`

```JavaScript
// coords.js

const CDP = require('chrome-remote-interface');

async function getCoords(css_selector) {
  let client;
  try {
    // connect to endpoint
    client = await CDP();
    // extract domains
    const { Runtime} = client;
    // enable events then start!
    await Promise.all([Runtime.enable()]);

    // get clientRect of links
    const result = await Runtime.evaluate({
      expression: `var targetCoordEl = document.querySelector('${css_selector}'); if (targetCoordEl) { JSON.stringify(targetCoordEl.getClientRects()); }`
    });

    // get offset screen positioning
    const screenPos = await Runtime.evaluate({
      expression: "JSON.stringify({offsetY: window.screen.height - window.innerHeight, offsetX: window.screen.width - window.innerWidth})"
    });

    let offset = JSON.parse(screenPos.result.value);
    let clientRect = null;

    try {
      clientRect = JSON.parse(result.result.value)["0"];
    } catch(err) {
      return null;
    }

    let retVal =  {
      x: offset.offsetX + clientRect.x,
      y: offset.offsetY + clientRect.y,
      width: clientRect.width,
      height: clientRect.height,
    };
    console.log(css_selector, retVal);
    return retVal;
  } catch (err) {
    console.error(err);
  } finally {
    if (client) {
      await client.close();
    }
  }
}

getCoords(process.argv[2]);
```

### Obtaining the HTML of the current page

Grabbing the HTML code of the current page can also be implemented in a straightforward fashion with the CDP. Save the following script as `page_source.js`.

```JavaScript
// page_source.js

const CDP = require('chrome-remote-interface');

async function getPageSource() {
  let client;
  try {
    // connect to endpoint
    client = await CDP();
    // extract domains
    const { Page, Runtime, DOM } = client;
    // enable events then start!
    await Promise.all([Page.enable(), Runtime.enable(), DOM.enable()]);

    // get the page source
    const rootNode = await DOM.getDocument({ depth: -1 });
    const pageSource = await DOM.getOuterHTML({
      nodeId: rootNode.root.nodeId
    });
    return pageSource.outerHTML;
  } catch (err) {
      console.error(err);
  } finally {
    if (client) {
      await client.close();
    }
  }
}

getPageSource().then((pageSource) => {
  console.log(pageSource);
})
```

### Controlling the Mouse and Keyboard

Of course it's also necessary to control the mouse and keyboard in order to navigate a website. The straightforward way would be to use puppeteer's keyboard and mouse interaction functionality such as `page.click()` or `page.type()`, however I strongly discourage to use them for reasons discussed above.

Instead, my suggestion is to use a proper desktop automation library such as `pyautogui` in case you want to use Python.

Hereby, it's mandatory to simulate human organic mouse (or touchscreen) and typing interactions as closely as possible. Put differently, we want to defend against the research that investigates the *suitability of behavioral biometrics to distinguish between computers and humans*.

[Recent research](https://arxiv.org/abs/2005.00890) suggests several ways how to mimic human mouse movement behavior as closely as possible.

There are two papers of considerable interest here:

1. Paper 1) Analyzing key strokes: **TypeNet: Deep Learning Keystroke Biometrics** [PDF](https://arxiv.org/abs/2101.05570)
2. Paper 2) Research how to mimic human mouse movements: **BeCAPTCHA-Mouse: Synthetic Mouse Trajectories and Improved Bot Detection** [PDF](https://arxiv.org/abs/2005.00890)

In this blog post, I don't have the means to dig deep into the listed papers. So I am going to present the two main findings of those papers and I will develop a simplified function that mimics human mouse/keyboard interaction. They of course are not perfect, but this is not the goal here.

In my opinion, the main statement of the BeCAPTCHA-Mouse paper is 

> By looking at typical mouse movements, we can observe some
> aspects typically performed by humans during mouse trajectories execution: an
> initial acceleration and final deceleration performed by the antagonist (activate
> the movement) and agonist muscles (opposing joint torque), and a fine-
> correction in the direction at the end of the trajectory when the mouse cursor
> gets close to the click button (characterized by a low velocity that serves to
> improve the precision of the movement). These aspects motivated us to use
> neuromotor analysis to find distinctive features in human mouse movements.
> Neuromotor-fine skills, that are unique of human beings are difficult to emulate
> for bots and could provide distinctive features in order to tell humans and bots
> apart.

And because images speak more than a thousands words:

<figure>
    <img src="{static}/images/becaptcha.png" alt="Mouse Movement Speed Profile" />
    <figcaption>Image taken from the BeCAPTCHA paper: Example of the mouse task determined by 8 keypoints: the crosses represent the keypoint where the user must click, red circles are the (x,y) coordinates obtained from the mouse device, and the black line is the mouse trajectory.<span style="font-size: 60%"></span></figcaption>
</figure>

This is my very amateurish way to implement the lesson taken from the BeCAPTCHA paper by using `pyautogui` for mouse movements. Store the following Python script as `mouse.py`.

```Python
import pyautogui
import random

def someWhereRandomClose(x, y, max_dist=120):
	"""
	Find a random position close to (x, y)
	with maximal dist @max_dist
	"""
	shape = pyautogui.size()
	cnt = 0

	while True:
		randX = random.randrange(1, max_dist)
		randY = random.randrange(1, max_dist)

		if random.random() > 0.5:
			randX *= -1

		if random.random() > 0.5:
			randY *= -1

		if x + randX in range(0, shape.width) and y + randY in range(0, shape.height):
			return (x + randX, y + randY)

		cnt += 1

		if cnt > 15:
			return (x, y)


def humanMove(x, y):
  """
  Moves like a human to the coordinate (x, y) and 
  clicks on the coordinate.

  Randomizes move time and the move type.

  Visits one intermediate coordiante close to the target before
  fine correcting and clicking on the target coordinates.
  """
  close_x, close_y = someWhereRandomClose(x, y, 100)

  # move to an intermediate target close to the destination
  # start fast, end slow
  pyautogui.moveTo(close_x, close_y, random.uniform(0.19, .75), pyautogui.easeOutQuad)

  # click on the main target
  pyautogui.moveTo(x, y, random.uniform(0.25, .65))
  pyautogui.click()


humanMove(800, 200)
humanMove(800, 400)
humanMove(1000, 600)
```

And what is the most important statement from the **TypeNet: Deep Learning Keystroke Biometrics** paper?

Honestly, this paper was hard to understand, since it discusses a lot of the technical aspects such as the ideal ML architecture and the best loss function such as *Contrastive loss*, *Triplet loss* or *Softmax loss*. 

But in my opinion, the graphic below explains the most relevant aspect that matters to this blog post's purpose.

<figure>
    <img src="{static}/images/key-features.png" alt="Mouse Movement Speed Profile" />
    <figcaption>Image taken from the TypeNet paper: Fig. 1. Example of the 4 temporal features extracted between two consecutive keys: Hold Latency (HL), Inter-key Latency (IL), Press Latency
(PL), and Release Latency (RL).<span style="font-size: 60%"></span></figcaption>
</figure>

There are four different temporal latencies that can be collected from free-text typing recordings:

1. Hold Latency (HL)
2. Inter-key Latency (IL)
3. Press Latency(PL)
4. Release Latency (RL)

The idea is that those four features bear biometric information about the person that types them.

Of course, in order to record those features, you must be able to listen to the [keydown](https://developer.mozilla.org/en-US/docs/Web/API/Document/keydown_event) and [keyup](https://developer.mozilla.org/en-US/docs/Web/API/Document/keyup_event) events, as it is the case with JavaScript in modern web browsers.

How does human typing in terms of `keydown` and `keyup` event actually look like? I recorded those events while typing the text *I am currently listening to "Nothing around us" from Mathame* and attached and absolute timestamp with `performance.now()` and this is what I got:

```JavaScript
[["kd","ShiftLeft","Shift",1,false,"0100",1,1798.375],["kd","KeyI","I",0,false,"0100",1,1876.685],["ku","ShiftLeft","Shift",1,false,"0000",1,1989.15],["ku","KeyI","i",0,false,"0000",1,2012.43],["kd","KeyA","a",0,false,"0000",1,2092.9],["kd","KeyM","m",0,false,"0000",1,2189.04],["ku","KeyA","a",0,false,"0000",1,2252.575],["ku","KeyM","m",0,false,"0000",1,2308.535],["kd","KeyC","c",0,false,"0000",1,2388.77],["kd","KeyU","u",0,false,"0000",1,2468.72],["ku","KeyC","c",0,false,"0000",1,2508.44],["ku","KeyU","u",0,false,"0000",1,2508.78],["kd","KeyR","r",0,false,"0000",1,2612.755],["ku","KeyR","r",0,false,"0000",1,2684.54],["kd","KeyR","r",0,false,"0000",1,2764.705],["kd","KeyE","e",0,false,"0000",1,2796.895],["ku","KeyR","r",0,false,"0000",1,2900.51],["kd","KeyN","n",0,false,"0000",1,2916.865],["ku","KeyE","e",0,false,"0000",1,2924.835],["kd","KeyT","t",0,false,"0000",1,3020.795],["ku","KeyN","n",0,false,"0000",1,3076.53],["kd","KeyL","l",0,false,"0000",1,3085.245],["ku","KeyT","t",0,false,"0000",1,3158.005],["ku","KeyL","l",0,false,"0000",1,3196.57],["kd","KeyY","y",0,false,"0000",1,3277.11],["kd","Space"," ",0,false,"0000",1,3364.82],["ku","KeyY","y",0,false,"0000",1,3405.69],["ku","Space"," ",0,false,"0000",1,3460.55],["kd","KeyL","l",0,false,"0000",1,3812.78],["kd","KeyL","l",0,false,"0000",1,3813.11],["ku","KeyL","l",0,false,"0000",1,3868.56],["ku","KeyL","l",0,false,"0000",1,3868.78],["kd","KeyI","i",0,false,"0000",1,3916.83],["kd","KeyI","i",0,false,"0000",1,3917.06],["ku","KeyI","i",0,false,"0000",1,4005.345],["ku","KeyI","i",0,false,"0000",1,4005.59],["kd","KeyS","s",0,false,"0000",1,4006.31],["kd","KeyS","s",0,false,"0000",1,4006.645],["kd","KeyT","t",0,false,"0000",1,4093.055],["kd","KeyT","t",0,false,"0000",1,4093.26],["ku","KeyS","s",0,false,"0000",1,4124.945],["ku","KeyS","s",0,false,"0000",1,4125.22],["kd","KeyI","i",0,false,"0000",1,4205.245],["kd","KeyI","i",0,false,"0000",1,4205.5],["ku","KeyT","t",0,false,"0000",1,4228.57],["ku","KeyT","t",0,false,"0000",1,4228.805],["kd","KeyN","n",0,false,"0000",1,4292.885],["kd","KeyN","n",0,false,"0000",1,4293.13],["ku","KeyI","i",0,false,"0000",1,4356.695],["ku","KeyI","i",0,false,"0000",1,4356.945],["ku","KeyN","n",0,false,"0000",1,4428.73],["ku","KeyN","n",0,false,"0000",1,4428.94],["kd","KeyG","g",0,false,"0000",1,4452.825],["kd","KeyG","g",0,false,"0000",1,4453.04],["kd","KeyI","i",0,false,"0000",1,4573.065],["kd","KeyI","i",0,false,"0000",1,4573.295],["ku","KeyG","g",0,false,"0000",1,4628.565],["ku","KeyG","g",0,false,"0000",1,4628.78],["kd","KeyN","n",0,false,"0000",1,4660.975],["kd","KeyN","n",0,false,"0000",1,4661.235],["ku","KeyI","i",0,false,"0000",1,4716.515],["ku","KeyI","i",0,false,"0000",1,4716.765],["kd","KeyG","g",0,false,"0000",1,4732.9],["kd","KeyG","g",0,false,"0000",1,4733.135],["ku","KeyN","n",0,false,"0000",1,4796.565],["ku","KeyN","n",0,false,"0000",1,4796.795],["ku","KeyG","g",0,false,"0000",1,4836.63],["ku","KeyG","g",0,false,"0000",1,4836.865],["kd","KeyT","t",0,false,"0000",1,5133.195],["kd","KeyT","t",0,false,"0000",1,5133.39],["kd","KeyO","o",0,false,"0000",1,5228.89],["kd","KeyO","o",0,false,"0000",1,5229.14],["ku","KeyT","t",0,false,"0000",1,5284.76],["ku","KeyT","t",0,false,"0000",1,5284.995],["kd","Space"," ",0,false,"0000",1,5285.655],["kd","Space"," ",0,false,"0000",1,5286.12],["ku","KeyO","o",0,false,"0000",1,5364.66],["ku","KeyO","o",0,false,"0000",1,5364.885],["ku","Space"," ",0,false,"0000",1,5365.44],["ku","Space"," ",0,false,"0000",1,5365.755],["kd","ShiftLeft","Shift",1,false,"0100",1,5829.575],["kd","ShiftLeft","Shift",1,false,"0100",1,5829.815],["kd","ShiftLeft","Shift",1,false,"0100",1,5830.415],["kd","Quote","\"",0,false,"0100",1,5884.835],["kd","Quote","\"",0,false,"0100",1,5885.03],["kd","Quote","\"",0,false,"0100",1,5885.485],["ku","Quote","\"",0,false,"0100",1,5964.7],["ku","Quote","\"",0,false,"0100",1,5964.9],["ku","Quote","\"",0,false,"0100",1,5965.36],["ku","ShiftLeft","Shift",1,false,"0000",1,6037.525],["ku","ShiftLeft","Shift",1,false,"0000",1,6049.935],["ku","ShiftLeft","Shift",1,false,"0000",1,6050.42],["kd","ShiftRight","Shift",2,false,"0100",1,6118.395],["kd","ShiftRight","Shift",2,false,"0100",1,6118.635],["kd","ShiftRight","Shift",2,false,"0100",1,6119.11],["ku","ShiftRight","Shift",2,false,"0000",1,6421.105],["ku","ShiftRight","Shift",2,false,"0000",1,6421.315],["ku","ShiftRight","Shift",2,false,"0000",1,6421.935],["kd","ShiftLeft","Shift",1,false,"0100",1,6591.365],["kd","ShiftLeft","Shift",1,false,"0100",1,6591.63],["kd","ShiftLeft","Shift",1,false,"0100",1,6599.805],["kd","KeyN","N",0,false,"0100",1,6700.895],["kd","KeyN","N",0,false,"0100",1,6701.105],["kd","KeyN","N",0,false,"0100",1,6701.52],["ku","ShiftLeft","Shift",1,false,"0000",1,6750.675],["ku","ShiftLeft","Shift",1,false,"0000",1,6750.89],["ku","ShiftLeft","Shift",1,false,"0000",1,6751.485],["ku","KeyN","n",0,false,"0000",1,6812.715],["ku","KeyN","n",0,false,"0000",1,6812.935],["ku","KeyN","n",0,false,"0000",1,6813.345],["kd","KeyT","t",0,false,"0000",1,6876.985],["kd","KeyT","t",0,false,"0000",1,6877.215],["kd","KeyT","t",0,false,"0000",1,6877.625],["ku","KeyT","t",0,false,"0000",1,7028.745],["ku","KeyT","t",0,false,"0000",1,7029],["ku","KeyT","t",0,false,"0000",1,7029.53],["kd","Backspace","Backspace",0,false,"0000",1,7284.965],["kd","Backspace","Backspace",0,false,"0000",1,7285.195],["kd","Backspace","Backspace",0,false,"0000",1,7285.65],["ku","Backspace","Backspace",0,false,"0000",1,7340.71],["ku","Backspace","Backspace",0,false,"0000",1,7351.655],["ku","Backspace","Backspace",0,false,"0000",1,7352.085],["kd","KeyO","o",0,false,"0000",1,7477.275],["kd","KeyO","o",0,false,"0000",1,7477.5],["kd","KeyO","o",0,false,"0000",1,7478],["kd","KeyT","t",0,false,"0000",1,7557.17],["kd","KeyT","t",0,false,"0000",1,7557.385],["kd","KeyT","t",0,false,"0000",1,7557.94],["ku","KeyO","o",0,false,"0000",1,7588.785],["ku","KeyO","o",0,false,"0000",1,7589.005],["ku","KeyO","o",0,false,"0000",1,7598.42],["kd","KeyH","h",0,false,"0000",1,7638.385],["kd","KeyH","h",0,false,"0000",1,7638.625],["kd","KeyH","h",0,false,"0000",1,7639.2],["ku","KeyT","t",0,false,"0000",1,7677.26],["ku","KeyT","t",0,false,"0000",1,7677.46],["ku","KeyT","t",0,false,"0000",1,7677.875],["ku","KeyH","h",0,false,"0000",1,7700.72],["ku","KeyH","h",0,false,"0000",1,7700.92],["ku","KeyH","h",0,false,"0000",1,7701.465],["kd","KeyI","i",0,false,"0000",1,7789.075],["kd","KeyI","i",0,false,"0000",1,7789.31],["kd","KeyI","i",0,false,"0000",1,7789.96],["kd","KeyN","n",0,false,"0000",1,7845.03],["kd","KeyN","n",0,false,"0000",1,7845.26],["kd","KeyN","n",0,false,"0000",1,7845.695],["ku","KeyI","i",0,false,"0000",1,7916.815],["ku","KeyI","i",0,false,"0000",1,7917.045],["ku","KeyI","i",0,false,"0000",1,7917.645],["kd","KeyG","g",0,false,"0000",1,7918.16],["kd","KeyG","g",0,false,"0000",1,7929.995],["kd","KeyG","g",0,false,"0000",1,7930.395],["ku","KeyN","n",0,false,"0000",1,8012.685],["ku","KeyN","n",0,false,"0000",1,8012.895],["ku","KeyN","n",0,false,"0000",1,8013.475],["ku","KeyG","g",0,false,"0000",1,8068.8],["ku","KeyG","g",0,false,"0000",1,8069],["ku","KeyG","g",0,false,"0000",1,8069.425],["kd","KeyA","a",0,false,"0000",1,8349.005],["kd","KeyA","a",0,false,"0000",1,8349.215],["kd","KeyA","a",0,false,"0000",1,8360.745],["kd","KeyR","r",0,false,"0000",1,8397.33],["kd","KeyR","r",0,false,"0000",1,8397.67],["kd","KeyR","r",0,false,"0000",1,8398.28],["kd","KeyO","o",0,false,"0000",1,8445.02],["kd","KeyO","o",0,false,"0000",1,8445.225],["kd","KeyO","o",0,false,"0000",1,8445.65],["kd","KeyU","u",0,false,"0000",1,8493.105],["kd","KeyU","u",0,false,"0000",1,8493.385],["kd","KeyU","u",0,false,"0000",1,8493.975],["ku","KeyO","o",0,false,"0000",1,8516.82],["ku","KeyO","o",0,false,"0000",1,8517.05],["ku","KeyO","o",0,false,"0000",1,8517.61],["ku","KeyU","u",0,false,"0000",1,8518.105],["ku","KeyU","u",0,false,"0000",1,8518.53],["ku","KeyU","u",0,false,"0000",1,8518.835],["ku","KeyA","a",0,false,"0000",1,8533],["ku","KeyA","a",0,false,"0000",1,8533.19],["ku","KeyA","a",0,false,"0000",1,8533.61],["ku","KeyR","r",0,false,"0000",1,8549.085],["ku","KeyR","r",0,false,"0000",1,8564.805],["ku","KeyR","r",0,false,"0000",1,8565.32],["kd","KeyN","n",0,false,"0000",1,8638.355],["kd","KeyN","n",0,false,"0000",1,8638.68],["kd","KeyN","n",0,false,"0000",1,8639.465],["kd","KeyD","d",0,false,"0000",1,8717.045],["kd","KeyD","d",0,false,"0000",1,8717.29],["kd","KeyD","d",0,false,"0000",1,8717.725],["ku","KeyN","n",0,false,"0000",1,8796.75],["ku","KeyN","n",0,false,"0000",1,8796.99],["ku","KeyN","n",0,false,"0000",1,8814.205],["ku","KeyD","d",0,false,"0000",1,8884.74],["ku","KeyD","d",0,false,"0000",1,8884.94],["ku","KeyD","d",0,false,"0000",1,8885.375],["kd","KeyU","u",0,false,"0000",1,8973.165],["kd","KeyU","u",0,false,"0000",1,8973.44],["kd","KeyU","u",0,false,"0000",1,8973.97],["ku","KeyU","u",0,false,"0000",1,9052.815],["ku","KeyU","u",0,false,"0000",1,9053.055],["ku","KeyU","u",0,false,"0000",1,9053.535],["kd","KeyS","s",0,false,"0000",1,9068.72],["kd","KeyS","s",0,false,"0000",1,9069.175],["kd","KeyS","s",0,false,"0000",1,9069.55],["kd","Space"," ",0,false,"0000",1,9133.025],["kd","Space"," ",0,false,"0000",1,9133.275],["kd","Space"," ",0,false,"0000",1,9133.715],["ku","KeyS","s",0,false,"0000",1,9173],["ku","KeyS","s",0,false,"0000",1,9173.215],["ku","KeyS","s",0,false,"0000",1,9173.73],["ku","Space"," ",0,false,"0000",1,9212.76],["ku","Space"," ",0,false,"0000",1,9225.385],["ku","Space"," ",0,false,"0000",1,9226.03],["kd","KeyF","f",0,false,"0000",1,9421.13],["kd","KeyF","f",0,false,"0000",1,9421.365],["kd","KeyF","f",0,false,"0000",1,9421.91],["kd","KeyF","f",0,false,"0000",1,9422.315],["ku","KeyF","f",0,false,"0000",1,9476.82],["ku","KeyF","f",0,false,"0000",1,9477.015],["ku","KeyF","f",0,false,"0000",1,9477.46],["ku","KeyF","f",0,false,"0000",1,9477.715],["kd","KeyR","r",0,false,"0000",1,9565.155],["kd","KeyR","r",0,false,"0000",1,9565.385],["kd","KeyR","r",0,false,"0000",1,9565.795],["kd","KeyR","r",0,false,"0000",1,9566.04],["kd","KeyO","o",0,false,"0000",1,9606.39],["kd","KeyO","o",0,false,"0000",1,9606.625],["kd","KeyO","o",0,false,"0000",1,9607.065],["kd","KeyO","o",0,false,"0000",1,9607.355],["ku","KeyO","o",0,false,"0000",1,9676.815],["ku","KeyO","o",0,false,"0000",1,9677.015],["ku","KeyO","o",0,false,"0000",1,9691.495],["ku","KeyO","o",0,false,"0000",1,9692.19],["ku","KeyR","r",0,false,"0000",1,9700.965],["ku","KeyR","r",0,false,"0000",1,9701.205],["ku","KeyR","r",0,false,"0000",1,9701.85],["ku","KeyR","r",0,false,"0000",1,9702.405],["kd","KeyM","m",0,false,"0000",1,9733.16],["kd","KeyM","m",0,false,"0000",1,9733.385],["kd","KeyM","m",0,false,"0000",1,9733.9],["kd","KeyM","m",0,false,"0000",1,9734.34],["ku","KeyM","m",0,false,"0000",1,9836.835],["ku","KeyM","m",0,false,"0000",1,9837.075],["ku","KeyM","m",0,false,"0000",1,9838.42],["ku","KeyM","m",0,false,"0000",1,9838.965],["kd","ShiftLeft","Shift",1,false,"0100",1,9949.645],["kd","ShiftLeft","Shift",1,false,"0100",1,9949.885],["kd","ShiftLeft","Shift",1,false,"0100",1,9950.5],["kd","ShiftLeft","Shift",1,false,"0100",1,9950.92],["kd","KeyM","M",0,false,"0100",1,10005.665],["kd","KeyM","M",0,false,"0100",1,10005.915],["kd","KeyM","M",0,false,"0100",1,10025.13],["kd","KeyM","M",0,false,"0100",1,10025.61],["ku","ShiftLeft","Shift",1,false,"0000",1,10037.575],["ku","ShiftLeft","Shift",1,false,"0000",1,10037.85],["ku","ShiftLeft","Shift",1,false,"0000",1,10038.865],["ku","ShiftLeft","Shift",1,false,"0000",1,10039.455],["ku","KeyM","m",0,false,"0000",1,10141.195],["ku","KeyM","m",0,false,"0000",1,10141.51],["ku","KeyM","m",0,false,"0000",1,10142.325],["ku","KeyM","m",0,false,"0000",1,10142.79],["kd","KeyA","a",0,false,"0000",1,10163.5],["kd","KeyA","a",0,false,"0000",1,10164.015],["kd","KeyA","a",0,false,"0000",1,10164.405],["kd","KeyA","a",0,false,"0000",1,10164.775],["kd","KeyT","t",0,false,"0000",1,10229.145],["kd","KeyT","t",0,false,"0000",1,10229.375],["kd","KeyT","t",0,false,"0000",1,10229.85],["kd","KeyT","t",0,false,"0000",1,10230.11],["ku","KeyA","a",0,false,"0000",1,10284.885],["ku","KeyA","a",0,false,"0000",1,10285.08],["ku","KeyA","a",0,false,"0000",1,10304.3],["ku","KeyA","a",0,false,"0000",1,10304.72],["kd","KeyH","h",0,false,"0000",1,10326.93],["kd","KeyH","h",0,false,"0000",1,10327.25],["kd","KeyH","h",0,false,"0000",1,10327.81],["kd","KeyH","h",0,false,"0000",1,10328.205],["ku","KeyT","t",0,false,"0000",1,10360.765],["ku","KeyT","t",0,false,"0000",1,10360.96],["ku","KeyT","t",0,false,"0000",1,10361.375],["ku","KeyT","t",0,false,"0000",1,10361.625],["ku","KeyH","h",0,false,"0000",1,10421.27],["ku","KeyH","h",0,false,"0000",1,10421.605],["ku","KeyH","h",0,false,"0000",1,10422.53],["ku","KeyH","h",0,false,"0000",1,10422.865],["kd","KeyM","m",0,false,"0000",1,10597.02],["kd","KeyM","m",0,false,"0000",1,10597.255],["kd","KeyM","m",0,false,"0000",1,10597.755],["kd","KeyM","m",0,false,"0000",1,10598.025],["ku","KeyM","m",0,false,"0000",1,10717.02],["ku","KeyM","m",0,false,"0000",1,10717.26],["ku","KeyM","m",0,false,"0000",1,10740.125],["ku","KeyM","m",0,false,"0000",1,10740.54],["kd","KeyE","e",0,false,"0000",1,10741.085],["kd","KeyE","e",0,false,"0000",1,10741.71],["kd","KeyE","e",0,false,"0000",1,10742.335],["kd","KeyE","e",0,false,"0000",1,10742.94],["ku","KeyE","e",0,false,"0000",1,10852.88],["ku","KeyE","e",0,false,"0000",1,10853.11],["ku","KeyE","e",0,false,"0000",1,10853.7],["ku","KeyE","e",0,false,"0000",1,10854.45]]
```

A lot of data, but it's possible to observe many very interesting things in real human typing behvaior.

How would I implement a straightforward human like typing function?

```Python
import pyautogui
import random
import time

def tinySleep():
  time.sleep(random.uniform(0.005, 0.07))


def doubleHit(key1, key2):
  """
  Sometimes press two keys down at the same time and randomize the 
  order of the corresponding key up events to resemble 
  human typign closer.
  """
  pyautogui.keyDown(key1)
  tinySleep()
  pyautogui.keyDown(key2)
  tinySleep()
  if random.random() > 0.5:
    pyautogui.keyUp(key1)
    tinySleep()
    pyautogui.keyUp(key2)
  else:
    pyautogui.keyUp(key2)
    tinySleep()
    pyautogui.keyUp(key1)


def humanTyping(text, speed=(0.015, 0.1)):
  """
  Mostly the keydown/keyup pairs are in order, but
  sometimes we want two keydown's at the same time.

  text: the text to be written in a human fashion.

  speed: the gap between key presses in seconds. Random number between
    (low, high)
  """
  i = 0
  while i <= len(text):
    time.sleep(random.uniform(*speed))
    if random.random() < .3 and i+1 < len(text):
      doubleHit(text[i], text[i+1])
      i += 2
    else:
      pyautogui.keyDown(text[i])
      tinySleep()
      pyautogui.keyUp(text[i])
      i += 1

    if i >= len(text):
      break

humanTyping("this is a test")
```

The most important observation: Often bots have a perfect sequence of `keydown X`, `keyup X`, `keydown Y`, `keyup Y` events, whereas humans press keys interleaved: `keydown X`, `keydown Y`, `keyup Y`, `keyup X`. Only the `keydown` events must be in order, not the `keyup` counterparts!

Of course the above algorithm is very bad and easily detectable. A real human key typing simulation involves collecting huge samples of real human typing behavior and then replaying them such that the four temporal delaying features resemble a real human being.

There are many biometric features to be found in the temporal aspects of human typing. Some examples:

+ Humans often have to correct spelling mistakes in their texts by using the backspace key or the mouse to select text to be edited. Bot's don't do that.
+ When two identical keys are pressed such as in *coffee*, then the first *f* and first *e* take longer time to type compared to the second character.
+ The tyiping speed within words is faster than between words 
+ There is a cognitive break between sentences, paragraphs, chapters, ...
+ Complicated words are more frequently re-written than easy words 

## Full Example Step by Step

Now we have all parts ready to create a full example. I will show the code for a small example how to solve the bot challenge that can be found here: [https://bot.incolumitas.com/#botChallenge](https://bot.incolumitas.com/#botChallenge).

The most recent example code can be found [here](https://github.com/NikolaiT/stealthy-scraping-tools/blob/main/example.py).

Run it with:

```bash
pipenv shell
```

And then run:

```python
python example.py
```

Below is the full Python source code. Please keep in mind that I most likely will 
not keep this blog post updated, consult the GitHub repository instead!

```Python
import time
import os
import random
import json
import subprocess
from mouse import humanMove
from typing import humanTyping

"""
You might have to adjust some coordinates. 

I used a dual screen setup and I started the browser on the
left screen.

You can obtain the coordinates of your current mouse pointer with 
the bash command on Linux `xdotool getmouselocation`
"""


def getPageSource():
  cmd = f'/usr/bin/node page_source.js'
  ps = subprocess.check_output(cmd, shell=True)
  return ps


def getCoords(selector, randomize_within_bcr=True):
  """
  Example: `node coords.js "li:nth-of-type(3) a"`
  """
  cmd = f'/usr/bin/node coords.js "{selector}"'
  coords = subprocess.check_output(cmd, shell=True)
  parsed = json.loads(coords)

  x = parsed['x']
  y = parsed['y']

  if randomize_within_bcr:
    x += random.randrange(0, int(parsed['width']))
    y += random.randrange(0, int(parsed['height']))

  return x, y


def startBrowser():
  os.system('google-chrome --remote-debugging-port=9222 --start-maximized --disable-notifications &')
  time.sleep(4)

  # visit https://bot.incolumitas.com/#botChallenge
  humanMove(168, 79)
  time.sleep(random.uniform(0.5, 1.5))
  humanTyping('bot.incolumitas.com\n', speed=(0.005, 0.008))
  time.sleep(random.uniform(1.5, 2.5))


def main():
  startBrowser()

  # click link to get to the challenge
  coords = getCoords('li:nth-of-type(3) a')
  print('Clicking on coordinates ' + str(coords))
  humanMove(*coords)
  time.sleep(random.uniform(0.5, 1.0))

  # enter username
  username = getCoords('input[name="userName"]')
  humanMove(*username, clicks=2)
  time.sleep(random.uniform(0.25, 1.25))
  humanTyping('IamNotABotISwear\n', speed=(0.005, 0.008))

  time.sleep(random.uniform(0.5, 1.0))

  # enter email
  email = getCoords('input[name="eMail"]')
  humanMove(*email, clicks=3)
  time.sleep(random.uniform(0.25, 1.25))
  humanTyping('bot@spambot.com\n', speed=(0.005, 0.008))

  time.sleep(random.uniform(0.5, 1.0))

  # agree to the terms
  terms = getCoords('input[name="terms"]')
  humanMove(*terms)

  # select cats
  cat = getCoords('#bigCat')
  humanMove(*cat)

  # submit
  submit = getCoords('#submit')
  humanMove(*submit)

  # press the final enter
  time.sleep(random.uniform(2.5, 3.4))
  humanTyping('\n', speed=(0.005, 0.008))

  # finally get the page source
  text = getPageSource()
  print('Got {} bytes of page soure'.format(len(text)))


if __name__ == '__main__':
  main()
```