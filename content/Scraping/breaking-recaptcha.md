Title: Breaking Google's Recaptcha
Date: 2019-3-1 16:00
Category: Scraping
Tags: puppeteer, recatpcha, scraping
Slug: breaking-googles-recaptcha
Author: Nikolai Tschacher
Summary: A captcha is a mechanism to distinguish human users from automated programs (bot). There are many service providers in the Internet that have a major incentive to prevent bots from (ab)using their systems.

A captcha is a mechanism to distinguish human users from automated programs (bot). There are many service providers in the Internet that have a major incentive to prevent bots from (ab)using their systems.

Imagine if there was a reliable method to break Google's famous [reCAPTCHA v2 or the new reCAPTCHA v3](https://developers.google.com/recaptcha/docs/versions) ([[released](https://webmasters.googleblog.com/2018/10/introducing-recaptcha-v3-new-way-to.html) in late 2018). The following scenarios would be possible:

1. Mass creation of accounts on sites such as [Reddit.com](https://www.reddit.com/) in order to build *fake Internet personas*. After letting those fake bots randomly post on subreddits trivial but undetectable comments, you can slowly let those bots start to **manipulate the public opinion** by downvoting, upvoting or posting political comments. This scenario is already reality and I don't actually want to know how strong the public opinion will be manipulated in the upcoming 2020 elections in the United States.

2. You could create fake gmail accounts automatically. Of course gmail requires you to have a valid phone number for each new account. Because phone numbers are a limited resource, this will be your bottleneck. Services such as [SMSPva](http://smspva.com/) allow you to register virtual phone numbers from any country. This plus an automated way to solve captchas allows you to create gmail accounts en masse and proceed to spam with the highly trusted gmail.com MX domain.

### Current State of Research

There were a couple of papers in the past years that investigated Google's anti bot defenses. It is clear that the defenses are not solely based on solving a captcha puzzle, the system processes many sources of human behavior in order to make a final statement about the *humanness* of the interacting agent. Examples are:

+ Can the program that sends the HTTP requests execute javascript?
+ Check that the user agent string is valid. Also check that the technical capabilities reported by the browser matches to what is advertised in the user agent string (very important!)
+ See if the browser has valid plugins, valid screen resolution, time zone of the client/browser
+ Monitor execution time of javascript
+ Number of mouse clicks, whether the mouse movement is organic or not, number of clicks
+ How much time between actions passed
+ Keyboard strokes or touch actions
+ A wide range of browser specific functions and CSS rules, canvas rendering properties
+ State is saved in a server side tracking cookie
+ Is the browser automated by browser automation software such as selenium or [puppeteer](https://github.com/GoogleChrome/puppeteer)? There are many different technical details that leak that you are using browser automation software. [This github repository](https://github.com/paulirish/headless-cat-n-mouse) and [this blog post](https://intoli.com/blog/not-possible-to-block-chrome-headless/) discusses them in detail. 


For example, we at [scrapeulous.com](https://scrapeulous.com/) use the following code to prevent search engines from detecting that we are automating browsers:

```js
// This is where we'll put the code to get around the tests.
async function evadeChromeHeadlessDetection(page) {
    // Pass the Webdriver Test.
    await page.evaluateOnNewDocument(() => {
        const newProto = navigator.__proto__;
        delete newProto.webdriver;
        navigator.__proto__ = newProto;
    });

    // Pass the Chrome Test.
    await page.evaluateOnNewDocument(() => {
        // We can mock this in as much depth as we need for the test.
        const mockObj = {
            app: {
                isInstalled: false,
            },
            webstore: {
                onInstallStageChanged: {},
                onDownloadProgress: {},
            },
            runtime: {
                PlatformOs: {
                    MAC: 'mac',
                    WIN: 'win',
                    ANDROID: 'android',
                    CROS: 'cros',
                    LINUX: 'linux',
                    OPENBSD: 'openbsd',
                },
                PlatformArch: {
                    ARM: 'arm',
                    X86_32: 'x86-32',
                    X86_64: 'x86-64',
                },
                PlatformNaclArch: {
                    ARM: 'arm',
                    X86_32: 'x86-32',
                    X86_64: 'x86-64',
                },
                RequestUpdateCheckStatus: {
                    THROTTLED: 'throttled',
                    NO_UPDATE: 'no_update',
                    UPDATE_AVAILABLE: 'update_available',
                },
                OnInstalledReason: {
                    INSTALL: 'install',
                    UPDATE: 'update',
                    CHROME_UPDATE: 'chrome_update',
                    SHARED_MODULE_UPDATE: 'shared_module_update',
                },
                OnRestartRequiredReason: {
                    APP_UPDATE: 'app_update',
                    OS_UPDATE: 'os_update',
                    PERIODIC: 'periodic',
                },
            },
        };

        window.navigator.chrome = mockObj;
        window.chrome = mockObj;
    });

    // Pass the Permissions Test.
    await page.evaluateOnNewDocument(() => {
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.__proto__.query = parameters =>
            parameters.name === 'notifications'
                ? Promise.resolve({state: Notification.permission})
                : originalQuery(parameters);

        // Inspired by: https://github.com/ikarienator/phantomjs_hide_and_seek/blob/master/5.spoofFunctionBind.js
        const oldCall = Function.prototype.call;
        function call() {
            return oldCall.apply(this, arguments);
        }
        Function.prototype.call = call;

        const nativeToStringFunctionString = Error.toString().replace(/Error/g, "toString");
        const oldToString = Function.prototype.toString;

        function functionToString() {
            if (this === window.navigator.permissions.query) {
                return "function query() { [native code] }";
            }
            if (this === functionToString) {
                return nativeToStringFunctionString;
            }
            return oldCall.call(oldToString, this);
        }
        Function.prototype.toString = functionToString;
    });

    // Pass the Plugins Length Test.
    await page.evaluateOnNewDocument(() => {
        // Overwrite the `plugins` property to use a custom getter.
        Object.defineProperty(navigator, 'plugins', {
            // This just needs to have `length > 0` for the current test,
            // but we could mock the plugins too if necessary.
            get: () => [1, 2, 3, 4, 5]
        });
    });

    // Pass the Languages Test.
    await page.evaluateOnNewDocument(() => {
        // Overwrite the `plugins` property to use a custom getter.
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    });

    // Pass the iframe Test
    await page.evaluateOnNewDocument(() => {
        Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
            get: function() {
                return window;
            }
        });
    });

    // Pass toString test, though it breaks console.debug() from working
    await page.evaluateOnNewDocument(() => {
        window.console.debug = () => {
            return null;
        };
    });
}
```

The code above is directly suited for the browser automation library puppeteer. You can also pass certain configuration parameters to chromium in order to increase the speed of web scraping. For example in the search engine scraping library [se-scraper](https://github.com/NikolaiT/se-scraper) we use the following flags to increase browsing speed:

```js
// pass those to the puppeteer constructor
var ADDITIONAL_CHROME_FLAGS = [
    '--disable-infobars',
    '--window-position=0,0',
    '--ignore-certifcate-errors',
    '--ignore-certifcate-errors-spki-list',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--disable-gpu',
    '--window-size=1920x1080',
    '--hide-scrollbars',
];
```

All this information is collected by reCAPTCHA system from Google. The longer a user appears human, the weaker the captcha problems become.

### Attacks on reCAPTCHA

In early 2019, researches from the University of Maryland have published [uncaptcha2](https://github.com/ecthros/uncaptcha2), a method to break Google's audio reCAPTCHA with up to **90% accuracy**.

In short, in each reCAPTCHA v2 offers for reasons of accessibility two methods to solve an captcha: 

1. Solving some image related task such as finding a fucking fire hydrant
2. Listen to an audio challenge and type in the words you hear

In turns out that the public speech recognition API's offered for free from services such as **Google Speech-To-Text API (the Irony)** or **Microsoft Bing Voice Recognition API** are capable of solving the audio captcha with a acceptance rate up to 90%.

This means that those systems are broken by design.

### Future with reCAPTCHA v3

I haven't used reCAPTCHA v3 myself, but Google completely shifts the center of focus away from direct user interaction to a more system-dependent approach.

reCAPTCHA v3 can be configured on all forms and inputs where human people can interact with a web application. It then collects data in the background and feeds a machine learning application that learns how to distinguish spammers from legit users.

Developers can see which elements are interacted in what way in a Google Administration Panel and can then decide what behavior can be considered non-abusive.

Google returns a score between 0 and 1 that determines how likely the action originates from a bot. The developer has then the responsibility to decide how to act given a certain score.
 

### Sources

1. https://github.com/ecthros/uncaptcha2
2. Bock, Kevin, et al. "unCaptcha: a low-resource defeat of recaptcha's audio challenge." Proceedings of the 11th USENIX Conference on Offensive Technologies. USENIX Association, 2017.
3. [I'm not a human: Breaking the Google reCAPTCHA - Black Hat](https://www.blackhat.com/docs/asia-16/materials/asia-16-Sivakorn-Im-Not-a-Human-Breaking-the-Google-reCAPTCHA-wp.pdf)
4. [Introducing reCAPTCHA v3: the new way to stop bots](https://webmasters.googleblog.com/2018/10/introducing-recaptcha-v3-new-way-to.html)