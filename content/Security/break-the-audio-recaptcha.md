Title: Solving the Google Audio ReCaptcha with Google's own Speech to Text API
Date: 2021-01-02 19:16
Category: Security
Tags: uncaptcha3, ReCaptcha, Google, Speech to Text API
Slug: breaking-audio-recaptcha-with-googles-own-speech-to-text-api
Author: Nikolai Tschacher
Summary: In this project, I make use of a method from 2019 that demonstrates how to solve the audio ReCaptcha with Googel's own Speech to Text API. This method still works, which is quite astonishing.

<div><a class="btn" style="width: 240px" href="https://github.com/NikolaiT/uncaptcha3">Link to GitHub repository</a></div>

### Introduction

This blog article uses research from the authors of [uncaptcha2](https://github.com/ecthros/uncaptcha2). The original [scientific uncaptcha paper](https://uncaptcha.cs.umd.edu/papers/uncaptcha_woot17.pdf) proposes a method to solves Google's Audio ReCaptcha with Google's own Speech-to-Text API.

Yes you read that correctly: **It is possible to solve the Audio version of ReCaptcha v2 with Google's own [Speech-to-Text API](https://cloud.google.com/speech-to-text).**

<figure>
    <img class="smallimg" src="{static}/images/homer.webp" alt="Home being Homer" />
    <figcaption>No description needed. <span style="font-size: 70%">(Source: https://i.giphy.com/media/xT5LMzIK1AdZJ4cYW4/giphy.webp)</span></figcaption>
</figure>

Since the release of [uncaptcha2](https://github.com/ecthros/uncaptcha2) is from **Janunary 18, 2019**,
their Proof of Concept code does not work anymore (as the authors predicted correctly).

This blog post attempts to keep the proof of concept up to date and working.

### How does it work?

Everyone knows and hates ReCaptcha. It looks like this:

<figure>
    <img class="smallimg" src="{static}/images/ReCaptcha.png" alt="ReCaptcha" />
    <figcaption>The ReCaptcha we all love</figcaption>
</figure>

For the inclusion of visually impaired people, there is also an audio version of the ReCaptcha.

<figure>
    <img class="smallimg" src="{static}/images/AudioReCaptcha.png" alt="AudioReCaptcha" />
    <figcaption>The audio version. <a href="{static}/images/audioReCaptcha.mp3">This is how it sounds</a></figcaption>
</figure>

The idea is very simple: You grab the mp3 file of the audio ReCaptcha and you submit it to Google's own Speech to Text API.

**Google will return the correct answer in over 97% of all cases.**

### Proof of Concept

<iframe width="1280" height="360" src="https://www.youtube.com/embed/Ft8zfK7XfYw" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
