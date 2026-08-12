Title: botstop.io - Does your Browser look like a Bot?
Date: 2026-08-11 19:30
Modified: 2026-08-12 13:30
Category: Security
Tags: Bot Detection, Internet Bots, JavaScript
Slug: botstop-io
Author: Nikolai Tschacher
Status: published
Summary: I launched a new little project called botstop.io. You open the page and it instantly tells you whether your browser looks like a bot, then refines the verdict a moment later. No CAPTCHA, no puzzles, just passive signals.

After a long time without side projects, I finally shipped a new one: [botstop.io](https://botstop.io).

The idea is dead simple. You open the page and you instantly get a verdict: **human**, **suspicious** or **automated**. Most signals are available right away, so there is no reason to make you stare at a spinner. A few probes need a little longer, so the page keeps watching and quietly refines the verdict a couple of seconds later if new evidence comes in. That's it. No CAPTCHA, no clicking on fire hydrants.

Behind the scenes, the page passively collects a bunch of browser signals and runs a small anti-replay challenge inside an obfuscated JavaScript VM. I will not spell out the exact checks here, that would only help the people writing the bots. The same detection engine gates signups and logins at [ipapi.is](https://ipapi.is/), so botstop.io is basically a public playground for it.

A few things I care about in the design:

- Sitting still is not held against you. The page literally asks you to do nothing, so the absence of mouse and keyboard input is not a bot signal here. Only positive evidence counts: well known tells like `navigator.webdriver` plus a bunch of quieter ones I will not enumerate.
- The individual signals are never shown publicly, only the verdict and a score. If the site showed exactly which probes fired, it would be a free calibration tool for bot authors.

If you write scrapers or browser automation, point them at [botstop.io](https://botstop.io) and see what happens. Vanilla headless Chrome scores around 90 and gets flagged as automated. If you manage to look human with a bot, I would honestly love to hear how you did it in the comments.

If you want the theory behind all of this, I wrote about it in [On the Architecture of Bot Detection Services](https://incolumitas.com/2021/07/18/on-the-architecture-of-bot-detection-services/) and [Behavioral Analysis for Bot Detection](https://incolumitas.com/2021/04/11/bot-detection-with-behavioral-analysis/).
