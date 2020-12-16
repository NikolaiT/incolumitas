Title: Remove Youtube Ads from your Android Phone
Date: 2020-12-16 19:14
Category: Tutorials
Tags: youtube, ads, adblock, ublockorigin
Slug: removing-youtube-ads-from-android-phone
Author: Nikolai Tschacher
Summary: I am a heavy user of Youtube. I use it to listen to podcasts while cooking or in order to watch the latest documentaries before going to sleep. But lately, the extremley aggressive advertisement of Youtube sparked enough motivation within myself to remove Youtube ads for good. Google overdid it. I have enough.

This guide works both for Android and IPhone users.

Google makes it technically not possible to remove Youtube ads in the native youtube app from your smartphone. You have no other option than to watch up to ten advertisement clips for every video and those ads can be extremely annnoying. At the time of writing, Youtube is playing more ads than the worst privately help cable TV channel ever did. This is no longer acceptable.

Google is hording enormeous amounts of wealth and they monopolize the Internet search market and advertisement. While I can understand that content creators want to be payed, I will not tolerate any longer those extremely annoying ads. 

I endured this for a very long time, but enough is enough. In this blog article, I provide a step by step instruction how to get rid of Youtube ads for good.

So what do I want?

1. I want Youtube videos without any ads
2. I don't want to install some shady third party app on my phone
3. Youtube needs to me more or less easy to use as in the native app

### Native Youtube App

Unfortunately, [it is not possible](https://adlock.com/blog/how-to-block-youtube-ads-on-android/) to block advertisements from the native Youtube app.

> To remove ads from applications that use secure connections (e.g., HTTPS), the ad blocker must launch a MITM attack, replacing the application’s security certificates with its certificate.

The issue is that Androids API level 24 distrust user certificates.

> But since the latest Android update for Nougat, all applications targeting API level 24 and above (YouTube is one of these applications) distrust certificates hosted in the user’s trust store. This means that the videos on the YouTube app will not play if we try to replace its security certificate with our own to remove ads.

### Tutorial: Remove Youtube Ads with Firefox and uBlock Origin

I came up with following solution: I will just use the firefox browser and I will add the uBlock Origin extension to the firefox browser.
This will kill all apps on all websites, including Youtube!

Those are the instructions you will have to follow in order to remove ads from YouTube:

1. Install Firefox from the Android Playstore
2. After Firefox is installed, open the browser.
3. In Firefox -> click on the three point menu at the bottom right -> Addons ->  addon manager -> enable uBlock Origin
4. After uBlock Origin is enabled, you can navigate to Youtube and enjoy it without any ads!
5. Add the Youtube website loaded in Firefox as a Shortcut to you Android home screen. Replace it with the native Youtube app icon.

Of course, using Youtube from firefox is not quite as fast as the native app, but in my experience not worrying about extremely annoying app is much better than to use the native app!

And Youtube from within the firefox browser is reasonably fast enough! There are no major issues and the content is exactly the same - Just without ads.