Title: Avoid Puppeteer or Playwright for Web Scraping
Date: 2021-05-20 22:26
Modified: 2021-05-24 14:50
Category: Scraping
Tags: web scraping, crawling, puppeteer, playwright, CDP
Slug: avoid-puppeteer-and-playwright-for-scraping
Author: Nikolai Tschacher
Summary: Here I explain why it is best to avoid puppeteer and playwright for web scraping.

I don't suggest to use Puppeteer and Playwright for web scraping.

The reasons are very simple: 

1. Both libraries use pre-shipped chromium binaries that are not used by the ordinary Internet users for normal web browsing. For example, the current `puppeteer@v9.0.0` release uses the chromium version `Chromium 91.0.4469.0 (r869685)`. I doubt that this exact subversion is used by a substantial part of Internet users for their everyday browsing. 
2. It is possible to detect that a browser is automated by those libraries based on many different behaviors that are unique to puppeteer or playwright.

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

## So what is the solution?

The problem is that every scraping developer is either using puppeteer or playwright to create their bots. Therefore, all that the detectors have to do is to detect puppeteer or playwright - they don't have to detect bot like behavior in general, it's enough to detect the standard browser automation library.

My suggestion is: **Ditch the browser automation frameworks altogether!**

Think about it: What do I really need for basic browser automation in order to scrape a website?

All that is required for robust browser automation is a straightforward way to find the coordinates for CSS selectors and a way to obtain the HTML code of the current website.

### Obtaining Coordinates for a CSS selector

Put differently, we need a way to implement the following function:

```JavaScript
function (css_selector: string) { return {x: number, y: number} }
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

Hereby, it's mandatory to simulate human organic mouse (or touchscreen) and typing interactions as closely as possible. Put differently, we want defend against the research that investigates the *suitability of behavioral biometrics to distinguish between computers and humans*.

[Recent research](BeCAPTCHA-Mouse: Synthetic Mouse Trajectories
and Improved Bot Detection) suggests several ways how to mimic human mouse movement behavior as closely as possible.

There are two papers of considerable interest here:

1. Paper 1) Analyzing key strokes: **TypeNet: Deep Learning Keystroke Biometrics**
2. Paper 2) Research how to mimic human mouse movements: **BeCAPTCHA-Mouse: Synthetic Mouse Trajectories and Improved Bot Detection**

In this blog post, I don't have the means to dig deep into the listed papers. So I am going to present the two main findings of those papers and I will develop a simplified function that mimics human mouse/keyboard interaction. They of course are not perfect, but this is not the goal here.

In my opinion, the main statement of paper 2) is 

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

And because images speak more than a thousands words.

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

How would I implement a human like typing function?

```Python
import pyautogui
import random
import time

def humanTyping(text, speed=0.5):
  """
  Types the text like a human.

  A pyautogui.keyDown('b') command without the matching 
  pyautogui.keyUp('b') results in the never ending pressing of said key.

  Key idea: Only the `keydown` events must be in order, not the `keyup` counterparts!

  Random sleeps are inserted between the key events.

  We only want to mix up the `keyup` events at most 2-3 keys ahead.
  """
  keyup = []

  for key in text:
    time.sleep(speed)
    pyautogui.keyDown(key)
    time.sleep(speed)
    keyup.append(key)
    if len(keyup) >= 2:
      random.shuffle(keyup)
      pyautogui.keyUp(keyup.pop())

  pyautogui.keyUp(keyup.pop())

def humanTyping2(text, speed=0.1):
  """
  Second Example
  """
  keyup = []

  for key in text:
    time.sleep(speed)
    pyautogui.keyDown(key)
    time.sleep(random.random() * .2)
    pyautogui.keyUp(key)

humanTyping2("test3000")
```

The most important observation: Often bots have a perfect sequence of `keydown X`, `keyup X`, `keydown Y`, `keyup Y` events, whereas humans press keys interleaved: `keydown X`, `keydown Y`, `keyup Y`, `keyup X`. Only the `keydown` events must be in order, not the `keyup` counterparts!

Of course the above algorithm is very bad and easily detectable. A real human key typing simulation involves collecting huge samples of real human typing behavior and then replaying them such that the four temporal delaying features resemble a real human being.

## Full Example

Now we have all parts ready to create a full example. I will show a small example how to solve the bot challenge that can be found here: [https://bot.incolumitas.com/#botChallenge](https://bot.incolumitas.com/#botChallenge).