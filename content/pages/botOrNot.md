Title: BotOrNot
Date: 2021-01-13 00:13
Author: Nikolai Tschacher
Slug: BotOrNot
Status: published

<a class="btn" href="https://bot.incolumitas.com">Visit the BotOrNot detection page!</a>

I am currently putting a lot of effort into researching how to distinguish web based bots from real human beings.

We are approaching an age where (certain) [captchas can be solved](https://incolumitas.com/2021/01/02/breaking-audio-recaptcha-with-googles-own-speech-to-text-api/) better by AI than by real humans.

Creating advanced bots is a multidimensional problem.

In order to not be detected, there are several areas where an advanced bot attempts to behave as closely as possible like a human:

+ The browsing fingerprint of a bot needs to be stable and as generic as possible.
+ Advanced bots need to route their traffic through a residential or mobile proxy network. The toughest bot creators among us create their [own mobile proxy farm](https://proxidize.com/).
+ Advanced bots are often based on puppeteer or playwright. Those web automation frameworks are configured slightly different then ordinary browsers. Advanced bots [try to fix those artifacts](https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth#readme).
+ Behavior based detection. Humans behave like a chaotic system. Some humans more than others. But that is not the point I am trying to make here. Humans move their mouse, keyboard, and scrolling wheel like humans. Bots do not. Advanced bots try to do that though!

I have many funny ideas. 

For example, some folks are running their puppeteer bots in AWS infrastructure (or other cloud infra). 
AWS infrastructure often has certain ports open. A fingerprint of open ports can be obtained. 
[Port scanning is possible with JavaScript in browsers](https://incolumitas.com/2021/01/10/browser-based-port-scanning/).
Therefore, a website could port scan the local network of your bot and if it looks like an AWS host, ban you (of course only if you exhibit other bot heuristics...)

<figure>
    <img src="/images/catAndMouse.webp" alt="cat and mouse bot game" style="width:400px" />
    <figcaption>
      Bonus Gif: The cat & mouse game between bots and anti-bot companies is not always that harmonic
    </figcaption>
</figure>
