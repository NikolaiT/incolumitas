Title: Remove Youtube Ads from your Android Phone
Date: 2020-12-16 19:14
Modified: 2020-12-18 19:32
Category: Tutorials
Tags: youtube, ads, adblock, ublockorigin
Slug: removing-youtube-ads-from-android-phone
Author: Nikolai Tschacher
Summary: I am a heavy user of Youtube. I use it to listen to podcasts while cooking or in order to watch the latest documentaries before going to sleep. But lately, the extremley aggressive advertisement of Youtube sparked enough motivation within myself to remove Youtube ads for good. Google overdid it. I have enough.

This guide works both for Android and IPhone users. It will show you how to get rid of Youtube ads on your smarthone in five easy steps.

Google makes it technically not possible to remove Youtube ads in the native youtube app from your smartphone. You have no other option than to watch up to ten advertisement clips for every video. Those ads can be extremely annnoying.

At the time of writing, Youtube is playing more ads than the worst private cable TV channel ever did. This is no longer acceptable!

Google is hording enormeous amounts of wealth and they monopolize the Internet search market and advertisement. While I can understand that content creators want to be payed, I will not tolerate those extremely annoying ads any longer.

I endured this for a very long time, but enough is enough. In this blog article, I provide a step by step instruction how to get rid of Youtube ads for good.

So what do I want?

1. I want Youtube videos without any ads
2. I don't want to install some shady third party app on my phone
3. Youtube needs to me more or less easy to use as it is in the native app
4. Bonus: I want to continue watching/listening to Youtube when my phone is in sleep mode. For example I often listen to podcasts while walking around.

### Tutorial: Remove Youtube Ads with Firefox and uBlock Origin

I came up with following solution: I will install the Firefox mobile browser and then add the uBlock Origin extension to the Firefox browser. This will remove all ads on all websites, including Youtube!

What follows are instructions that you can follow in order to remove all ads from YouTube:

**Step 1:** Install Firefox from the Android Playstore.

<figure>
    <img class="smallimg" src="{static}/images/android/install-firefox.png" alt="Install Firefox from the playstore" />
    <figcaption>Install Firefox from the Android Playstore</figcaption>
</figure>

**Step 2:** After Firefox is installed, open the Firefox browser.

**Step 3:** In Firefox -> Click on the "three point menu" at the bottom right -> Addons ->  Addon manager -> enable uBlock Origin

<figure>
    <img class="smallimg" src="{static}/images/android/firefox-menu.png" alt="Open the firefox menu" />
    <figcaption>Open the browser settings...</figcaption>
</figure>

<figure>
    <img class="smallimg" src="{static}/images/android/firefox-addons.png" alt="Open the addons manager" />
    <figcaption>...And add uBlock Origin from the addons menu</figcaption>
</figure>

**Step 4:** After uBlock Origin is enabled, you can navigate to Youtube (or any other website) and enjoy it without any ads!

**Step 5:** Add Youtube from Firefox as a shortcut to you Android home screen. Replace it with the native Youtube app icon so that you never have to use the native Youtube app with ads again.

<figure>
    <img class="smallimg" src="{static}/images/android/youtube-homescreen.png" alt="Add a Youtube shortcut to the homescreen" />
    <figcaption>Add a firefox Youtube shortcut to the homescreen</figcaption>
</figure>

Using Youtube from Firefox is not quite as fast as the native app, but in my experience, not worrying about extremely annoying ads is much better than to use the native app! And Youtube from within the firefox browser is reasonably fast enough! There are no major issues and the content is exactly the same - Just without ads.

### Native Youtube App

Unfortunately, [it is not possible](https://adlock.com/blog/how-to-block-youtube-ads-on-android/) to block advertisements from the native Youtube app.

> To remove ads from applications that use secure connections (e.g., HTTPS), the ad blocker must launch a MITM attack, replacing the application’s security certificates with its certificate.

The issue is that the Android API level 24 distrust user certificates and thus there is no way to remove ads on the fly.

> But since the latest Android update for Nougat, all applications targeting API level 24 and above (YouTube is one of these applications) distrust certificates hosted in the user’s trust store. This means that the videos on the YouTube app will not play if we try to replace its security certificate with our own to remove ads.