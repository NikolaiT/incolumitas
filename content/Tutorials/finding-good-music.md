Title: Programming to improve your life
Date: 2019-1-2 22:38
Modified: 2019-2-13 21:30
Category: Tutorials
Tags: music, tutorials, learning
Slug: programming-to-improve-your-life
Author: Nikolai Tschacher
Summary: Making use of programming skills

**In short**: I am fed up with bad music and music apps and streaming platforms such as Spotify, Soundcloud or Youtube.
That's why I search for objectively good music playlists on the Internet, download the songs from Youtube don't care about music supply for a couple of years.
My main issue with existing music platforms: Any algorithm giving me suggestions based on my past music taste doesn't factor in that I might in fact have a bad music taste.


I am now programming for almost 10 years. I have almost finished my M. Sc. in computer science. I developed many projects in a wide range of programming languages
in the past years, many projects which I abandoned early, too much blog post that were never completed.
So much buggy code, too many bad choices.

To be honest, I don't think I ever created a piece of software that I was truly satisfied with. I have come to terms that I am an average
programmer trying to make a living with it.

About three years ago, I caught myself listening to the same few songs again and again that I had saved on my smartphone.
Even though I would consider myself savy in many areas of information technology, streaming platforms like Spotify
or Soundcloud neaver managed to convince me.

Therefore, my usual approach was to download some songs from youtube that I already knew. I saved them to my phone and listened
them until I couldn't hear them anymore. Once in a while, I found fresh artists on youtube and I added them to my small 
collection of music.

I tried the free version of spotify, but the advertisements were too annoying for me. Furthermore, I couldn't imagine spending 10$ a month
for their service. Why bother paying for music when you can have it for free on youtube?

To be honest, not wanting to pay 10$ is a bad argument, since I pay for many other useless services much more money
(such as my amazon prime account, which I almost never use).

Nevertheless, something inside me wants to remain independent and free. I don't want to become enslaved by spotify and provide them with my valuable user data.
I don't want them to give money for such a mediocre business idea. So what is the alternative?

I heard there is also [youtube music](https://music.youtube.com/) now. Basically a version of youtube that is focused on music videos.
I briefly tried it out and it let me chose the artists and songs that I already was aware of.

That's not what I want. I want music that I don't know yet and that many people collectively like. **Any algorithm giving me suggestions
based on my past music taste doesn't factor in that I might in fact have a bad music taste.**

### Love for the Unknown

I want to find quality music I am not aware of yet. To summarize, my goals are the following:

* I don't want to be dependent on an active internet connection. More often than not, I reach my monthly data limit on my smartphone
 and can't listen too good music anymore. Further reasons: flights or foreign countries with roaming fees.
* I don't want to subsribe to a music service such as Spotify or Youtube Music. I dislike downloading apps and giving away user data.
* Advertisements are from hell and completely neutralises any happiness that stems from listening to cool songs. Therefore, I 
  must avoid free spotify or youtube music.
* I like to own the actual MP3 files.

So what do I need to do? 

1. I need to identify objective reliable sources of **what good music is**
2. I need to compile a list of the songs
3. A script to search and download the titles from youtube needs to be programmed.

 
### Finding sources

Have you tried browsing youtube for music? The algorithm is broken. It just doesn't work. It's not smarter than the user. And the 
user doesn't know what good music constitutes. *That's why he is searching*.

Because many people are much smarter and more experienced then me, let's aks them what they consider to be good music.

The more people commented, the better the playlist will be. For example [this reddit thread](https://www.reddit.com/r/AskReddit/comments/5rsyjw/what_song_is_a_1010_yet_hardly_anybody_has_heard/)
from 2017 is pure gold. 7100 comments and people [even made a playlist](https://play.google.com/music/preview/pl/AMaBXykqYrojBN3OnyGTPB5kiST-yZrtALFcPLtU3CTtRawBcb2kNNd9-rvIkR781-EICggcECLAOCdEsoNsSz4e-0ZgdNdUTQ==) from the top comments. This saves some work.

#### Approach: Search past reddit threads of the form "What is your favourite song?"

A good idea is to search the internet for recent (in the past two years) threads where people name their favourite songs.

* https://www.reddit.com/r/AskReddit/comments/5rsyjw/what_song_is_a_1010_yet_hardly_anybody_has_heard/
* https://www.reddit.com/r/AskReddit/comments/6iqvmw/what_is_your_favorite_song/
* https://www.reddit.com/r/AskReddit/comments/2akyrk/what_is_your_favourite_song_of_all_time/
* https://www.reddit.com/r/AskReddit/comments/16jtpa/what_is_the_most_beautiful_song_youve_ever_heard/ Old but still relevant
* https://www.reddit.com/r/SpotifyPlaylists/top/?t=all

And I searched especially for classical music because I am a huge noob in this part of music:

* https://www.reddit.com/r/AskReddit/comments/1gea1e/what_are_the_most_beautiful_pieces_of_classical/
* https://www.reddit.com/r/AskReddit/comments/1oppdn/whats_your_favorite_piece_of_classical_music_why/
* https://www.reddit.com/r/classicalresources/comments/13mteq/a_playlist_of_20_great_classical_works_for/
* https://open.spotify.com/playlist/4bAquhPmrdqGpfHWLwhloh
* https://www.reddit.com/r/classicalmusic/comments/85vsnq/most_moving_classical_pieces/

And then I also searched for all kinds of electronic music, house music, EDM, techno and so on:

* https://www.reddit.com/r/EDM/comments/7abjf8/what_is_your_favorite_edm_song_of_all_time/
* https://www.reddit.com/r/Techno/comments/20yce8/best_feel_good_techno_song_of_all_time/

Then I search for threads were people should name songs that *everyone knows but can't associate a name to it*.

* https://www.reddit.com/r/AskReddit/comments/848sz0/whats_a_1010_song_that_not_many_people_know_about/
* https://www.reddit.com/r/AskReddit/comments/5rsyjw/what_song_is_a_1010_yet_hardly_anybody_has_heard/

#### Compile meta list from existing playlist

* https://www.reddit.com/r/Music/comments/8lhw1o/i_made_a_spotify_playlist_of_the_best_songs_ever/
* https://open.spotify.com/playlist/6uYt5DwcyaOxxPUundboC2?si=RJn2frzTRwOVAKRJFWyZxA
* https://open.spotify.com/playlist/1cAHI20k456593GCBNqzw6
* https://www.reddit.com/r/Music/comments/79mpf3/i_made_a_spotify_playlist_from_the_reddit/
* https://open.spotify.com/playlist/79dEZteWKyQJTOyURURnyX
* https://open.spotify.com/playlist/7CseXkRUYWMS6jm0VafGlN?si=ifApvK9MSneaiDSLUj7NpQ

* Collaborative: https://open.spotify.com/user/haeltotoe/playlist/62SJFBkvpmR0Z6MIa9v13I?si=zteIfdJ9RbW0g6rIxNr3FA

#### Existing Google Play Lists: https://play.google.com

* https://play.google.com/music/preview/pl/AMaBXynbKSugHYaAeEOzFdDN1RXRtgQ99Bn6aUkTDEbmn3mEQ0rGmGYjBJuN5fGhDYefF1-O-iItTfzrHJ35DQiI8_R4J6bnfQ==


#### Use Github as a data source

For example [this javascript application](https://github.com/angrbrd/top5000-playlist/blob/master/TopSongs.csv) features a list of 5000 top songs mostly from the United States. The most recent songs date back to 2013. 
I won't use this list because there are too many generic pop songs in it.

This [personal gist](https://gist.github.com/manios/4515112) of a github user named manios is much better in my opinion, because the list directly includes Youtube links.
However, it is too opinionated.


### The End Result

Of course I needed to base my list on upvotes from reddit or trust random people from spotify.

 
