Title: The art of cheating: Making a chess.com chess bot following an unusual approach!
Date: 2014-01-26 02:11
Author: Nikolai Tschacher
Category: C
Tags: C, Chess.com, Cheating, Firefox, Hooking, Chess, Lowlevel, Programming, Security
Slug: the-art-of-cheating-making-a-chess-com-chess-bot-using-a-unusual-approach
Status: published

### Table of contents

1.  **[Preface](#chap_preface)**: Giving first insight into the idea and
    why I think that hooking into a browser is a good idea.
2.  **[Many different ways to make browser game bots](#chap_dwmbgb)**:
    Discussion various techniques to write HTTP/WebSocket bots
3.  **[How does chess.com internally look like?](#chap_internals)**:
    Investigation of the client side behavior of
    [chess.com](http://chess.com)
4.  **[How the bot works](#chap_workings)**: Explaining how my shared
    library hooks firefox network functions
5.  **[Conclusion](#chap_concl)**: Summary of my discoveries
6.  **[Demo
    Video](https://vimeo.com/85060026 "Link to the demonstration of the bot")
    and another, [better demo
    video](https://vimeo.com/85083958 "demo video, better")**: You might
    only watch that video, but make sure you [read the explanation on
    the very bottom of this blog post!](#chap_demo)
7.  You may find the sources to the shared library (so) on my [github
    account](https://github.com/NikolaiT/chess-com-cheat/ "Link to chess.com cheat library").

### Preface {#chap_preface}

Usually I don't have good ideas in forms of flashes of genius. On the
contrary, I think that many endeavors and interesting projects might be
reasonable if realized, but often so, there's a huge amount of work
involved and *too* many variables and strategic decisions in the process
that could eventually render the project a failure. What I try to say: A
mediocre idea well engineered might be a good product. But a good idea
badly implemented and designed is usually just bad in it's final form.

Raw, abstract ideas exist in abundance. So does the will to make them
happen. But once in a while, I manage to overcome these two hindrances
and begin to build and shape my ideas into reality.

So around 10 days ago (yes it took me that long to make it) I went
jogging in the forest and my subconscious searched for different
possibilities to cheat in a chess browser game
([chess.com](http://chess.com "chess server") to be specific). I knew
that there were quite some different approaches. So before I get all to
technical, let's define the obstacle:

I want build a bot that plays automatic actions/moves on a online chess
server, whose communication is realized over HTTP 1/1 and
[WebSocket](http://tools.ietf.org/html/rfc6455) (https and wws
respectively), all TLS/SSL encrypted.

Additionally the following constraints need to be considered:

-   The bot should work *while the player is actually playing*. That
    means: Without any real action by a human, the bot won't do anything
    at all.
-   The engine that computes the moves is a local process. I chose
    [Stockfish](http://stockfishchess.org/): it has a pretty decent
    strength and is open source which makes it usable on Linux contrary
    to Houdini. If we want to use engine calculated information in the
    browser we need to get a channel to a local process. We can't
    integrate Stockfish originated data into the browser process space
    with memory injection methods, since it seems hard and I don't know
    how to do it (correctly). But we surely may interact with the local
    process in any other possible IPC way.

So this was my idea that overcame me in the woods while running: Why
should I even bother rebuilding the whole chess.com communication
protocol, when I can just *replace the moves I made ingame with engine
calculated equivalents?!*

Every move (like *a2a3* or *g7g8*) has identical lengths, so I need to
find the point where the packets (or messages in WebSockets RFC
terminology) are still decrypted (note that all traffic is TLS/SSL
layered) such that it's possible to update them, without dealing with
the hassle of TLS/SSL.

And there is only one place where I can do this: Inside of the browser
process space, in some networking function that sends and receives the
target packets. This was my idea. I knew that it must be possible to
find this *hook point* and to alter the packets somewhere.

But hell, I didn't knew that this approach was that hard to achieve!

So before I'll dive into the technical internals, I'll discuss the
different possible architectures and designs of cheating *in particular*
for a chess.com bot, but which are also perfectly applicable *to general
browser game automation*.

### Many different ways to make browser game bots! {#chap_dwmbgb}

1.  **A high level approach** would be to inject custom javascript into
    the DOM of a running browser session.  
    This piece of javascript then connects to a local server (e.g. to a
    simple server listening on localhost:SOMEPORT) that responses with a
    bot calculated move when requesting with the current game action
    history. A pretty nice example of this technique is [this video on
    youtube](http://www.youtube.com/watch?v=PW1vMXHJdnM "high level javascript bot")
    (I suppose it uses this design paradigm, but I don't know because
    there are no open sources to investigate further).  
    *Advantages*: Comparably easy implementation, because we don't need
    to tinker with packets and can directly attack the game logic. Works
    for all platforms and all browsers, because javascript is
    universally runnable.  
    *Drawbacks:* Maybe we can't build a connection to localhost due to
    the same-origin policy (Can we?) This would render this approach
    impossible, since we absolutely need a way to communicate with the
    local program that supplies us with engine moves. Then maybe a
    socket connection (although listening on localhost) might be slower
    than other
    [IPC](http://en.wikipedia.org/wiki/Inter-process_communication "inter process communication techniques")
    techniques, because of the TCP/IP stack overhead.
2.  **Another high level technique** would be to write a custom browser
    extension that intercepts the browser game traffic and injects bot
    calculated moves.  
    *Advantages*: We don't need to hassle with SSL/TLS decryption
    because our application is executed in the browser process.
    Furthermore it must be somehow possible to communicate with a local
    process that supplies the extension with engine knowledge.  
    *Disadvantages*: Platform and browser dependent code. When going
    down that road, I would need to write platform independent C code
    for different browsers. Additionally, it's questionable if we can
    speak to different processes, because of the browser sandboxes and
    their security policies.
3.  **Another approach: Low level network stack interception
    technique:** I could sniff on the network interface where the TCP
    packets of the communication sessions are exchanged with a
    appropriate API like
    [scapy](http://www.secdev.org/projects/scapy/ "awesome python security module")
    or [libpcap](http://www.tcpdump.org/ "the library behind tcpdump")
    (When writing C directly). Because the communication is encrypted
    with SSL/TLS, there needs to be a reliable way to decrpyt the TCP
    packets. This is not a trivial task, since different browsers use
    different ciphers/HMACS for TSL/SSL (they are determined in the
    [handshake](http://en.wikipedia.org/wiki/Transport_Layer_Security#TLS_handshake "SSL handshake protocol")).  
    This issue however is alleviated by the fact that some browsers can
    be started with a option (environment variable
    [SSLKEYLOGFILE](https://developer.mozilla.org/en-US/docs/NSS_Key_Log_Format))
    to dump the current key secrets of a SSL/TLS session to a file which
    my bot could use to decrypt/encrypt the traffic on the fly.  
    Once decrypted, I would modify the appropriate move values and
    replace the action I made, with the bot calculated move. Then I need
    to encrypt the packet again with the cipher specified in the
    SSLKEYLOGFILE. But this implies several issues as for example:  
    How can my sniffer/bot know which cipher was used? He only knows
    the current keys for the session, but not the ciphers. In the worst
    case, we need to also sniff the SSL/TLS handshake and connection
    start. This again is a very tedious process since the many quirks
    and combinations of a TLS session beginning.  
    Padding shouldn't be a bigger issue because the moves in the packet
    are just replaced and no additional data is injected or deleted. So
    the TCP packets should stay the same. We only need to recalculate
    the checksums.
4.  Another *thoroughly* low level approach: **Hooking [.so
    libraries](http://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html)!**
    This was my idea while running in the forest!  
    This might be the hardest approach in the investigation and
    research phase (It's not a easy task to find the correct hooking
    points in the HUGE chromium or firefox code base, but it looks like
    the [NSS library](https://developer.mozilla.org/en-US/docs/NSS) is a
    good starting point), but also the most elegant way, because we
    don't need to hassle with SSL/TLS quirks and can work with plaintext
    HTTP requestes/responses, when we find a good hook point. This
    approach, although very elegant and straightforward comes with huge
    drawbacks:  
    Hooking is very platform depended. On linux we could hook with
    kernel modules or the [LD\_PRELOAD
    trick](http://rafalcieslak.wordpress.com/2013/04/02/dynamic-linker-tricks-using-ld_preload-to-cheat-inject-features-and-investigate-programs/).
    On Windows we'd need other hooking techniques like IAT hooking,
    using the microsoft hooking library or something else. Additionally,
    we need to know the target architecutre (Differences between x86 and
    amd64). But from what I know now, this approach seems to be the best
    compared to the others, because we can work in the target process
    space (The browser userland process space itself) and we do not
    reassemble/decrypt packets ourselves (like in the previous
    technique). **Form grabbers are a related technique** used by
    blackhats for their trojans.
5.  **The traditional way**: Re-implement the high level browser game
    protocol by forging messages and HTTP Requests. This is not very
    elegant because our goal is to just modify packets. But when
    following this approach, we'd need to rebuilt the whole game logic
    (or at least many parts). This'd look something like the following:

        import requests

        login = requests.post('https://browsergame.com', {'login': user, 'password': pass})
        if login.read().success():
            requeset = request.get('https://browsergame.com/action.php?gamelogic=blabla')
            # Do implement game logic

6.  **The easy way:** Make a click bot! Just control the mouse
    programmatically and initiate actions like a human would.  
    Normally such bots learn where the chess board in the browser
    window is located in the browser window by comparing the pixel
    colors of the screen with the color of the chess squares (or
    whatever field you want to locate). Slightly more adanced would be
    to locate the html elements that represent the squares and
    recalculate the exact location based on viewport sizes and settings
    and rendering. But I don't know how it is actually made, do you have
    a idea?  
    Anyways, the huge majority of chess.com bots is of this
    architecture type. You can view them in action
    [here](http://www.youtube.com/watch?v=1SwOskkPnS0) or
    [here](http://www.youtube.com/watch?v=5osrRuz4tvM "high level chess.com bot")
    on youtube.  
    *Advantages*: Very easy to implement, very powerful technique, very
    good possibilities to evade anti cheating techniques (For instance,
    if *there were* cheating detection *besides* the ones who detect and
    doom very strong play as engine originated, these approaches would
    try to find out whether the current player is human by interpreting
    mouse movements and intervals between moves. But somewhere this
    information has to be gathered and sent to a server. We could just
    remove this submittal and therefore the server has no way to learn
    that we are cheaters).

### How does chess.com internals look like? {#chap_internals}

Having discussed the different architectures for a bot (Remember: I
chose the hooking technique!) it was time to learn more about the
target.

My plan was very ambitions, because I had very little experience with
hooking processes and hell, I didn't code in C or assembly for over 1.5
years, nor did I have much experience in the past. Muppets! Even now, I
know nothing about low level stuff at all.

So it was definitely time **to get my learning hat on** and to
investigate how [chess.com](http://chess.com) works.

I based a lot of my investigations on the [V8
debugger](https://code.google.com/p/v8/), the one integrated in the
Chrome browser dev tools. I am not much of a Google fan, but Jesus
fucking Christ, Chrome's Development tools (the stuff that pops up when
you click on *Inspect Element* in the context menu) is just a very well
crafted tool!

It's very fast, newer hangs or remarkably loads and there are so many
features whilst maintaining a very clear and concise interface. If you
don't know how to use it, I really suggest reading and spending a hour
on this tutorial (Do the assignments, otherwise what you learned won't
stick): [DevTools javascript debugger
tutorial](https://developers.google.com/chrome-developer-tools/docs/javascript-debugging).

So by using this debugger I found out that chess.com inner client side
machinery essentially consists of around 30k lines of javascript code.
There are three major files, LiveChessAdvanced.js, LiveChessBase.js,
LiveChessCore.js, you can see a excerpt in the screenshot below:

[caption id="attachment\_654" align="alignleft" width="640"][![Look into
the chess.com internals with the Chrome debugging
tools]({static}/uploads/2014/01/Screenshot-from-2014-01-26-055418-1024x515.png)]({static}/uploads/2014/01/Screenshot-from-2014-01-26-055418.png)
*Look into the chess.com internals with the Chrome debugging
tools*[/caption]

Furthermore all of chess.com's networking is handled by a file called
cometd.js, so chess.com makes use of the *Bayeux protocol*. You can
learn more about the javascript library on
[cometd.org](http://cometd.org/).

But why such a strange protocol?

HTTP 1.1 is a request response protocol, it's not suited to implement
complex game protocols.

This was quite a issue in the last years, because companies wanted to
bring complex applications (like browser games) to the browser and so
they implemented a range of techniques that circumvented these obstacles
by exploiting some HTTP quirks, like the fact that HTTP connections stay
open under specific circumstances, like loading javascript in chunks (A
form of long polling, it's basically just creating *script* elements in
excess and pointing their *src* attribute to the cometd server which
then sends back JavaScript (or JSONP) with events as its payload). Or
you can achieve alternatively the same with frames. All these techniques
are summarized under the umbrella term cometd, and [you should read
about them on
wikipedia](http://en.wikipedia.org/wiki/Comet_(programming)).

But in late 2011 the [WebSocket
standard](http://tools.ietf.org/html/rfc6455 "RFC for WebSocket") was
established in it's final form and nowadays we don't need to make use of
cometd techniques (At least I assume that WebSocket should replace these
techniques), because we can make bi-directional, full-duplex
(simultaneous communication in both directions) TCP like connections
using WebSockets. And this is exactly what chess.com does, it
exclusively uses WebSockets for their protocol, when the connection is
good enough.

But now comes the first quirk: I strongly assume that this cometd.js
library provides fallbacks for the case they detect that WebSockets
aren't working for some reason. This happend to me quite often:

My internet connection here is very messy and I have a speed limit of
around 60kps downstream and around 10kps upstream. I don't know if this
could be a reason, that [the
library](https://github.com/cometd/cometd "cometd on github") sometimes
changes protocols, but it certainly does. I first realized this, when I
was able to intercept the game traffic using the HttpHeaders firefox
plugin (that, like the name suggests, only captures HTTP traffic) and
then suddenly in the next game the captured traffic was empty. So I
concluded that the protocol responsible for the game traffic must be
chosen dynamically, for which the connection stability seems to be a
variable!

So enough written, **show me some protocol examples of chess.com** you
shout! Here you go:

This is a typical WebSocket JSON message from the server that updates
the game state of a game (This packet belongs to a game that I was
received while kibitzing, not one I played myself):

    [{"data":{"sid":"gserv","game":{"id":709324515,"gametype":"chess","time":{"basetime":600,"timeinc":0},"players":[{"uid":"DAHUANXIONG","status":"online","lag":2,"lagms":220,"lightning":2105,"blitz":2064,"standard":1361,"lightning960":1200,"blitz960":1200,"standard960":1200,"bughouse":1200,"ml":10,"title":null,"mod":false,"new":false,"country":"CN","av":true,"avatar":"//d1lalstwiwz2br.cloudfront.net/images_users/avatars/DAHUANXIONG_small.1.jpeg","clientfeatures":{"examineboard":true,"multiplegames":true,"clientname":"LC4Full v2013121801; Chrome/25; Windows"},"nonverified":true},{"uid":"Mrsinj","status":"playing","lag":2,"lagms":259,"gid":709324515,"lightning":2153,"blitz":2205,"standard":1200,"lightning960":1200,"blitz960":1200,"standard960":1200,"bughouse":1200,"ml":10,"title":null,"mod":false,"new":false,"country":"RS","av":true,"avatar":"//d1lalstwiwz2br.cloudfront.net/images_users/avatars/Mrsinj_s.1.jpg","clientfeatures":{"examineboard":false,"multiplegames":true,"clientname":"LC4Simple v2013121801; Chrome/32; Windows"}}]},"tid":"Game"},"channel":"/game/~1"}]

If you're not a fan of such unformatted, jammed JSON data, you should
inspect the code on a online JSON editor like
[www.jsoneditoronline.org](http://www.jsoneditoronline.org/).

A few interesting fields: *uid* identifies the players, *status* can be
*starting*, *in_progress*, *aborted* or *stopped*, *lag* and *lagms*
specify the lag of the player (How can you measure that?). Funny enough,
the protocol architect uses redundant information here, *lag* is just
the rounded version of *lagms*, but it doesn't bring other information.

*gid* is the global game id. For instance, you should be able to revisit
the upper game under the following link
*http://www.chess.com/livechess/game?id=709324515*. But this particular
message above is not of big interest, because it doesn't contain any
moves, it just provides some status information. The packets that are
sent on every move made look like the next message:

    [{"data":{"sid":"gserv","game":{"id":709324427,"status":"in_progress","seq":9,"players":[{"uid":"ImaginaryDunker","status":"playing","lag":1,"lagms":132,"gid":709324427},{"uid":"Alexander_Donchenko","status":"playing","lag":1,"lagms":115,"gid":709324427}],"moves":"gvYIlBIBvB0KBrZJow","clocks":[582,571],"draws":[],"squares":[0,0]},"tid":"GameState"},"channel":"/game/709324427"}]

Three fields are of particular importance,
*"moves":"gvYIlBIBvB0KBrZJow"*, *"clocks":[582,571]* and
*"status":"in_progress"*. They are pretty much self explanatory at this
point I suppose.

So let's finally **look at a typical game session** in terms of parsed
WebSocket messages. Please note that I might not include all messages
that are exchanged in a game session, simply because I don't care to
much for trivial information (like polling the server for specific
features). The bottom messages are the ones which count when you want to
understand a typical game session:

First of all, a connection message to the server is sent when the
browser connects to the server:

**1. Initial connection outbound message**

    [{"channel":"/meta/connect","connectionType":"ssl-websocket","advice":{"timeout":0},"id":"10","clientId":"6djua267g6n8ydja21m8yhztj3gtpx","ext":{"ack":-1,"timesync":{"tc":1390715596738,"l":661,"o":-17527952}}}]

I am not sure, that encoding/encryption the clientId is, but it didn't
matter for my purpose to write a bot. So when I expect a challenge from
another player, I receive such a packet:

**2. Game begins**

    [{"data":{"sid":"gserv","game":{"id":709341692,"status":"starting","seq":0,"players":[{"uid":"ponkhan","status":"playing","lag":2,"lagms":285,"gid":709341692},{"uid":"EatingSpiders","status":"playing","lag":1,"lagms":177,"gid":709341692}],"abortable":[true,true],"moves":"","clocks":[600,600],"draws":[],"repeated":true,"squares":[0,0]},"tid":"GameState"},"channel":"/game/709341692"}]

Noteworthy is the *status* "starting". As you can see, the *moves* value
is still empty. Then my adversary made a move and I receive again a
message in the style as above:

**3. First move received**

    [{"data":{"sid":"gserv","game":{"id":709341692,"status":"starting","seq":1,"players":[{"uid":"ponkhan","status":"playing","lag":3,"lagms":381,"gid":709341692},{"uid":"EatingSpiders","status":"playing","lag":1,"lagms":183,"gid":709341692}],"abortable":[true,true],"moves":"mC","clocks":[600,600],"draws":[],"squares":[0,0]},"tid":"GameState"},"channel":"/game/709341692"}]

Now *moves* isn't empty anymore, it contains *"mC"*, but what the heck
does it mean?

It's basically a encoding of chess.com for their move notation. I don't
know why the chose it, maybe it's represents a compression because it'd
use n/2 of the space where n is the number of bytes used in the
[algebraic chess
notation.](http://en.wikipedia.org/wiki/Algebraic_notation_(chess)).

But I honestly doubt it, because there are far better compression
methods for 64 possible squares (and some promotion combinations).

Maybe it's a way to stop stupid cheaters like me to pursue their
devilish deeds, but that can't be possible, since the method that
decoded/decrypts the move notation isn't more than a simple look-up
table:

Here is the relevant code part of the obfuscated javascript source in
LiveChessCore.js, at line 8577 (after applying Chrome's pretty print
functionality):

    (function() {
        zf9bd6 = function() {
            this.z6439d = {"a1": "a","a2": "i","a3": "q","a4": "y","a5": "G","a6": "O","a7": "W","a8": "4","b1": "b","b2": "j","b3": "r","b4": "z","b5": "H","b6": "P","b7": "X","b8": "5","c1": "c","c2": "k","c3": "s","c4": "A","c5": "I","c6": "Q","c7": "Y","c8": "6","d1": "d","d2": "l","d3": "t","d4": "B","d5": "J","d6": "R","d7": "Z","d8": "7","e1": "e","e2": "m","e3": "u","e4": "C","e5": "K","e6": "S","e7": "0","e8": "8","f1": "f","f2": "n","f3": "v","f4": "D","f5": "L","f6": "T","f7": "1","f8": "9","g1": "g","g2": "o","g3": "w","g4": "E","g5": "M","g6": "U","g7": "2","g8": "!","h1": "h","h2": "p","h3": "x","h4": "F","h5": "N","h6": "V","h7": "3","h8": "?"};
            this.ze8500 = {"_a": "a1","_i": "a2","_q": "a3","_y": "a4","_G": "a5","_O": "a6","_W": "a7","_4": "a8","_b": "b1","_j": "b2","_r": "b3","_z": "b4","_H": "b5","_P": "b6","_X": "b7","_5": "b8","_c": "c1","_k": "c2","_s": "c3","_A": "c4","_I": "c5","_Q": "c6","_Y": "c7","_6": "c8","_d": "d1","_l": "d2","_t": "d3","_B": "d4","_J": "d5","_R": "d6","_Z": "d7","_7": "d8","_e": "e1","_m": "e2","_u": "e3","_C": "e4","_K": "e5","_S": "e6","_0": "e7","_8": "e8","_f": "f1","_n": "f2","_v": "f3","_D": "f4","_L": "f5","_T": "f6","_1": "f7","_9": "f8","_g": "g1","_o": "g2","_w": "g3","_E": "g4","_M": "g5","_U": "g6","_2": "g7","_!": "g8","_h": "h1","_p": "h2","_x": "h3","_F": "h4","_N": "h5","_V": "h6","_3": "h7","_?": "h8"};
            this.z56f6c = "{";
            this.z87e36 = "~";
            this.zbba2c = "}";
            this.z7fd23 = "(";
            this.za93ff = "^";
            this.z536e1 = ")";
            this.z817b2 = "[";
            this.z00e3d = "_";
            this.ze4b5e = "]";
            this.z91a79 = "@";
            this.zc21d8 = "#";
            this.zaa236 = "$";
        };
        zf9bd6.prototype = {z0cd66: function(ze2e37, zbd29b, z2ba00) {
                var zed3d4 = this.z6439d[ze2e37];
                var z98075 = this.z6439d[zbd29b];
                if (z2ba00) {
                    var dir = zbd29b.charCodeAt(0) - ze2e37.charCodeAt(0);
                    if (z2ba00 == "q")
                        z98075 = (dir == -1) ? this.z56f6c : ((dir == +1) ? this.zbba2c : this.z87e36);
                    else 
                    if (z2ba00 == "n")
                        z98075 = (dir == -1) ? this.z7fd23 : ((dir == +1) ? this.z536e1 : this.za93ff);
                    else 
                    if (z2ba00 == "r")
                        z98075 = (dir == -1) ? this.z817b2 : ((dir == +1) ? this.ze4b5e : this.z00e3d);
                    else 
                    if (z2ba00 == "b")
                        z98075 = (dir == -1) ? this.z91a79 : ((dir == +1) ? this.zaa236 : this.zc21d8);
                }
                return zed3d4 + z98075;
            },zafc74: function(z32182) {
                var zed3d4 = z32182.charAt(0);
                var z98075 = z32182.charAt(1);
                var ze2e37 = this.ze8500["_" + zed3d4];
                var zbd29b;
                var z2ba00 = null;
                var z2b70d = ze2e37.charCodeAt(0);
                var z5b3be = null;
                if (z98075 == this.z56f6c) {
                    z5b3be = z2b70d - 1;
                    z2ba00 = "q";
                } else 
                if (z98075 == this.z87e36) {
                    z5b3be = z2b70d;
                    z2ba00 = "q";
                } else 
                if (z98075 == this.zbba2c) {
                    z5b3be = z2b70d + 1;
                    z2ba00 = "q";
                } else 
                if (z98075 == this.z7fd23) {
                    z5b3be = z2b70d - 1;
                    z2ba00 = "n";
                } else 
                if (z98075 == this.za93ff) {
                    z5b3be = z2b70d;
                    z2ba00 = "n";
                } else 
                if (z98075 == this.z536e1) {
                    z5b3be = z2b70d + 1;
                    z2ba00 = "n";
                } else 
                if (z98075 == this.z817b2) {
                    z5b3be = z2b70d - 1;
                    z2ba00 = "r";
                } else 
                if (z98075 == this.z00e3d) {
                    z5b3be = z2b70d;
                    z2ba00 = "r";
                } else 
                if (z98075 == this.ze4b5e) {
                    z5b3be = z2b70d + 1;
                    z2ba00 = "r";
                } else 
                if (z98075 == this.z91a79) {
                    z5b3be = z2b70d - 1;
                    z2ba00 = "b";
                } else 
                if (z98075 == this.zc21d8) {
                    z5b3be = z2b70d;
                    z2ba00 = "b";
                } else 
                if (z98075 == this.zaa236) {
                    z5b3be = z2b70d + 1;
                    z2ba00 = "b";
                }
                if (z5b3be != null) {
                    var zd2788 = ze2e37.charAt(1);
                    if (zd2788 == 7)
                        zbd29b = String.fromCharCode(z5b3be) + "8";
                    else 
                    if (zd2788 == 2)
                        zbd29b = String.fromCharCode(z5b3be) + "1";
                    else
                        return null;
                } else {
                    zbd29b = this.ze8500["_" + z98075];
                    if (!zbd29b)
                        return null;
                }
                var z3cbd9 = {};
                z3cbd9["fromArea"] = ze2e37;
                z3cbd9["toArea"] = zbd29b;
                z3cbd9["additionalInfo"] = z2ba00;
                return z3cbd9;
            },za902f: function(zcc2ef) {
                return this.z6439d[zcc2ef];
            },z398d0: function(zccfb6) {
                return this.ze8500["_" + zccfb6];
            }};
    })();

Before I forget it: Why the hell are you guys from chess.com obfuscating
your JS code? I mean it probably makes sense to pack and encrypt game
binaries of big games (that are still very fast cracked by talanted
crackers), but why blur Javascript? It's just too easy to reverse the
logic with existing tools such as DevTools or Firebug, so why even
bother?

No with the function above, we can look the move up which reveals "mC"
== "e3e5". So we now how to encode/decode the move notation. Let's
inspect the next message:

**4. Writing my first move (outgoing Message)**

    [{"channel":"/service/user","data":{"move":{"gid":709341692,"seq":1,"uid":"EatingSpiders","move":"YI","clock":600,"clockms":60000,"squared":false},"sid":"gserv","tid":"Move"},"id":"259","clientId":"6djua267g6n8ydja21m8yhztj3gtpx"}]

Nothing new here, this is just my browser that send the move "YI" to the
game server. You can look it up now on your own, since I have identified
the decoding mechanism above.

Now the next messages are just essentially like the previous two (with
status *in_progress* in place of the initial *starting*), always
receiving the opponents move and then I sending my move. So we have all
knowledge about the protocol that we need, now let's discuss how I
finally implemented my bot.

### How the bot is implemented {#chap_workings}

As discussed, I chose to hook into low level networking functions in the
browser. I chose firefox as my hooking target, because there already
exist quite many examples on how to hook networking functions in
firefox.

So the technique is basically known as the LD_PRELOAD trick. You can
learn about it on this short [stackoverflow.com
explanation](http://stackoverflow.com/questions/426230/what-is-the-ld-preload-trick).

There are other, better ways to hook library functions, I really
recommend you to read [this wonderful
article](http://www.codeproject.com/Articles/70302/Redirecting-functions-in-shared-ELF-libraries)
about *redirecting shared functions in ELF binaries*. But you should
have profound knowledge of the *ELF* format in order to follow;

First, I tried to hook directly into the specific HTTP and WebSocket
functions in the firefox network library called *netwerk* or
[necko](https://developer.mozilla.org/en/docs/Necko). But firefox is
written in C++ and therefore it's not so simple to use the LD_PRELOAD
trick, because the functions/class names are
[mangled](http://en.wikipedia.org/wiki/Name_mangling#Standardised_name_mangling_in_C.2B.2B).
I desperately tried to hook such C++ code and I also managed to to so in
a simple example. It looks something like below, but it couldn't
actually log some calls. Maybe because the function was never called.
Here I try to hook into the `GenerateCredentials()` function of the
`nsHttpBasicAuth` class. I assume the function fires when you enter
HttpAuth credentials in a browser.

    :::C
    #include 
    #include 
    #include 
    #include 

    #ifndef _GNU_SOURCE
    #define _GNU_SOURCE
    #endif

    namespace mozilla {
    namespace net {

    typedef unsigned short char16_t;
    typedef unsigned int uint32_t;
    typedef unsigned long PRUint32; 
    typedef PRUint32 nsresult;
    #define NS_IMETHODIMP NS_IMETHODIMP_(nsresult)

    class nsIHttpAuthenticator {

    };

    class nsISupports {

    };

    class nsHttpBasicAuth : public nsIHttpAuthenticator
    {
    public:
        nsHttpBasicAuth();
        virtual ~nsHttpBasicAuth();
        unsigned long GenerateCredentials(void *authChannel,
                                         const char *challenge,
                                         bool isProxyAuth,
                                         const char16_t *domain,
                                         const char16_t *user,
                                         const char16_t *password,
                                         nsISupports **sessionState,
                                         nsISupports **continuationState,
                                         uint32_t *aFlags,
                                         char **creds); 

    };  

    nsHttpBasicAuth::nsHttpBasicAuth()
    {
    }

    nsHttpBasicAuth::~nsHttpBasicAuth()
    {
    }

    unsigned long
    nsHttpBasicAuth::GenerateCredentials(void *authChannel,
                                         const char *challenge,
                                         bool isProxyAuth,
                                         const char16_t *domain,
                                         const char16_t *user,
                                         const char16_t *password,
                                         nsISupports **sessionState,
                                         nsISupports **continuationState,
                                         uint32_t *aFlags,
                                         char **creds) {
        fprintf(stdout, "[+] GenerateCredentials hooked!\n");
        // define the class member pointer tyep
        typedef unsigned long (nsHttpBasicAuth::*hookedMethod)(void *, const char *, bool, const char16_t *, const char16_t *, const char16_t *, nsISupports **, nsISupports **, uint32_t *, char **);
        static hookedMethod origMethod = 0;
        
        void *tmpPtr = dlsym(RTLD_NEXT, "_ZN7mozilla3net15nsHttpBasicAuth19GenerateCredentialsEPvPKcbPKtS6_S6_PPNS0_11nsISupportsES9_PjPPc");
        if (tmpPtr == NULL) {
            fprintf(stderr, "dlsym() couldn't located the symbol :( \n");
            exit(EXIT_FAILURE);
        }

        memcpy(&origMethod, &tmpPtr, sizeof(&tmpPtr));

        // call the original method
        unsigned long retVal = (this->*origMethod)(authChannel, challenge, isProxyAuth, domain, user, password, sessionState, continuationState, aFlags, creds);
        
        return retVal;
    }

    }
    }

Anyways, if I could get succeed in hooking C++ functions by overcoming
the mangling issues, I would directly hook into functions found in the
mozilla source tree
[/mozilla-central/source/netwerk/protocol/websocket/](http://mxr.mozilla.org/mozilla-central/source/netwerk/protocol/websocket/).
It would be enormously juicy to hook into the file
[WebSocketChannel.cpp](http://mxr.mozilla.org/mozilla-central/source/netwerk/protocol/websocket/WebSocketChannel.cpp).
For example the function `void WebSocketChannel::BeginOpen()` on line
1061 looks like a nice start. **Can anyone provide me a hooking example
for this function? That'd be awesome!**

So after some further research and giving up trying to hook C++
functions, I decided to hook into firefox's `PR_write()` and
`PR_read()` low level networking functions, implemented in plain C. If
you search for these functions in the internet, you will find lot's of
different example for form grabbers, techniques that are commonly used
by maleware writers.

After experimenting a little bit with these two functions, I figured out
that basically the whole freaking internet flows through them. For
instance, if you just open a browser without loading any site, a whole
bunch of meta protocols are squeezed through `PR_write()` and
`PR_read()`.

I assume that all possible protocols (like accessing cookies,
*about:blank*, *file:* and the like) are also handled these functions.
It's really funny what you're able to see when you hook into these
functions. To formulate it pregnant: Stuff that you thought to be
deleted after clearing the cache is happily appearing inside these two
functions...

Anyways, the basic C code that implements this hooking technique in form
of a shared library looks like the bottom code excerpt. You can always
visit [my public
repository](https://github.com/NikolaiT/chess-com-cheat), where you can
read the current state of the cheat code.


    :::C
    PRInt32 PR_Write(PRFileDesc *fd, const void *buf, PRInt32 amount) {
        static PRInt32 (*my_PR_write)(PRFileDesc *, const void *, PRInt32) = NULL;
        
        // Detect the client WebSocket connection attempt
        if (!(webSocketState.state & WEB_SOCKET_CONNECTION_REQUESTED) && amount > 600 && amount < 1200 && memContains((const char *)buf, amount, "Upgrade: websocket") 
            && memContains((const char *)buf, amount, "Origin: http://live.chess.com") && memContains((const char *)buf, amount, "Sec-WebSocket-Key:") &&
                 memContains((const char *)buf, amount, "Sec-WebSocket-Version: 13")) {
            webSocketState.state |= WEB_SOCKET_CONNECTION_REQUESTED; 
    #if DEBUG_LEVEL >= 1
            INFO_PRINT("Chess.com WebSocket client request detected", SH_RED);
    #endif
            // Also start up the Stockfish engine
            //INFO_PRINT("Starting the engine...", SH_BLUE);
            //initStockfish();
        }
        /*
         * When the WebSocket is open sniff for move packets that are between 230 and 240 bytes in size.
         * I observed that these synchronize with moves made and hence I assume these packetses transmit moves.
         * Now I just need do decrypt them and good is.
         */
        if ((webSocketState.state & WEB_SOCKET_CONNECTION_REQUESTED) && amount > 210 && amount < 260) {
    #if DEBUG_LEVEL >= 2
            INFO_PRINT("PR_Write() called and buffer size suggests that this packet represents a move!", SH_RED);
    #endif
            // Inject a engine made move and update the game state
            modifyMove((char *)buf, (size_t)amount);
        }

        my_PR_write = dlsym(RTLD_NEXT, "PR_Write");

        if (my_PR_write == NULL) {
            fprintf(stderr, "dlsym() failed for PR_Write\n");
            exit(EXIT_FAILURE);
        }

        PRInt32 retVal = (*my_PR_write)(fd, buf, amount);

        return retVal;
    }

    PRInt32 PR_Read(PRFileDesc *fd, void *buf, PRInt32 amount) {
        static PRInt32 (*my_PR_read)(PRFileDesc *, void *, PRInt32);

        /* 
         * There is a hell of a lot data that passes through this function. Hence we only want
         * to consume as few as possible processing power. We are only interested in data that
         * is in a specfic length range, since it seems that the WebSocket packets on live.chess.com
         * use pretty regular packet size.
         */

        /* 
         * Sniff for incoming live.chess.com WebSocket move data.
         */
        if ((webSocketState.state & WEB_SOCKET_CONNECTION_REQUESTED) && amount > 50 && memContains((const char *)buf, amount, "moves") != NULL) {
            couldRead = 1;
            collectGameState((char *)buf, amount);
    #if DEBUG_LEVEL >= 2
            INFO_PRINT("PR_Read() called with 'moves' keyword inside", SH_BLUE);
    #endif
        }
        
        my_PR_read = dlsym(RTLD_NEXT, "PR_Read");
        
        if (my_PR_read == NULL) {
            fprintf(stderr, "dlsym() failed for PR_Write\n");
            exit(EXIT_FAILURE);
        }

        PRInt32 retVal = (*my_PR_read)(fd, buf, amount);

        return retVal;
    }

I hope the above code is more or less self explanatory. But in case it's
not, here's a short summary of the rough algorithm that it computes:

**1.** The shared library (let's call it libpwh.so) is dynamically
loaded in a firefox process with the LD_PRELOAD trick. For instance:
`export LD_PRELOAD=$PWD/libpwh.so; /usr/bin/firefox`  
**2.** The functions `PR_Read()` and `PR_Write()` are hooked.  
**3.** As soon as a WebSocket request that indicates the beginning of a
new live.chess.com chess game is detected, the shared library (the above
code) initializes the [local Stockfish chess
engine](http://stockfishchess.org/ "chess engine") with the function
*int initStockfish()* {There should be enough time before the game
actually begins to pre-calculate some moves}.  
**3.1** When a JSON message like the following

    :::json
    [{"data":{"sid":"gserv","game":{"id":706548893,"status":"starting","seq":0,"players":[{"uid":"rocchen","status":"playing","lag":4,"lagms":415,"gid":706548893},{"uid":"workcentre7328","status":"playing","lag":2,"lagms":210,"gid":706548893}],"abortable":[true,true],"moves":"","clocks":[600,600],"draws":[],"repeated":true,"squares":[0,0]},"tid":"GameState"},"channel":"/game/706548893"}]

is intercepted, a game has begun. The needles that indicate such a
beginning are thus the players UID and the string *"status":"starting"*  
**4.** From now on, every outgoing packet (from `PR_Write()`), that
causes a move, must be updated with a chess engine move. This is done
with with function void `modifyMove()`, which in turns relies on a
correct game state. Such a outbound packet looks like (We have discussed
the protocol in the previous chapter):

    :::json
    [{"channel":"/service/user","data":{"move":{"gid":706662190,"seq":11,"uid":"rocchen","move":"9I","clock":76,"clockms":7661,"squared":false},"sid":"gserv","tid":"Move"},"id":"105","clientId":"4gzikii6gu01a1k7kvdcb7a1h2gh6"}]

**5.** Concurrently to step 4, the move made by the opponent is
synchronized with a local gameState struct variable. The opponent's move
is obtained in `PR_Read()` and the function void *collectGameState()*
keeps the move history current. The function *collectGameState()* also
stores the current game state in a C struct:

    :::C
    // This struct holds the current game state and all kids of game information as parsed and extracted of the live session
    typedef struct {
        char status[0x50]; // The status as defined by the protocol. Will be most likely 'playing' during a game.
        uint64_t gameID; // The global game id. Can be looked up after games to review the game.
        uint32_t moveNumber; // The number of moves I did
        char playerName[0x50]; // Me
        char opponentPlayerName[0x50]; // Poor opponent
        uint64_t remainingTimeMsSelf; // yeah does that matter?
        uint64_t remainingTimeMsOpponent; // probably more relevant
        uint16_t lagMsSelf; // i have a stupid connection here in my house
        uint16_t lagMsOpponent;
        char movesMade[0x100]; // in live.chess.com encoded version
        char movesMadeDecoded[0x400]; // the decoded version
        char currentMoveOpponent[0x3]; // last move of opponent
        char currentMoveSelf[0x3]; // my last move
        char currentMoveOpponentDecoded[0x6];
        char currentMoveSelfDecoded[0x6];
        char engineMoves[0x100];
        char engineSuggestion[0x6]; // The best move as suggested by the engine
    } _CHESS_COM_GAME_SESSION_STATE;

### Conclusion {#chap_concl}

Hooking is a dirty business and it's not the good idea I thought it was.
Therefore my idea was rather average and the implementation is pretty
bad. All in all, I am still satisfied, because it works!

It would be a probably good approach if I managed to hook directly into
[WebSocketChannel.cpp](http://mxr.mozilla.org/mozilla-central/source/netwerk/protocol/websocket/WebSocketChannel.cpp),
because I wouldn't need to cumbersomly pick my target messages in the
huge traffic that flows thourgh `PR_Read()`.

It's a really strange bot to use, because while my bot modifies packets,
**the javascript frontend can't properly deal with this fact and in
displays a huge mess!** This is really interesting because the frontend
(in flash and javascript) notes that I made a specific move and saves it
accordingly in their variables/objects, but suddenly the game server
says that I made in reality atotally different move (The one which was
injected by my code). So the poor frontend is heavily confused and
sometimes needs up to 10 moves to update the *real* moves into the
frontend browser window. You can observe this behaviour in the video.
It's really funny!

To be honest, my bot has still many open issues and sometimes the
firefox process crashes randomly. Maybe there's a memory leak somewhere,
because after several games someone eats up the whole heap and the whole
linux system crashes.

I am pretty sure it's not my malloc/calloc, because I strictly checked
to free() all allocated buffers. But on the other hand, I must be the
culprit, because without me hooking into firefox, everything works like
a charm.

Either I am to inexperienced or it *just is* hard, but I think making a
click bot (as discussed above) for browser games it a far better
approach, if the case you're strictly result oriented :)

### Demonstration videos {#chap_demo}

These two videos are of slightly low quality, but you can still
comfortably recolonize the chess game:

<!-- This version of the embed code is no longer supported. Learn more: https://vimeo.com/s/tnm -->
<object width="500" height="281">
<param name="allowfullscreen" value="true"></param><param name="allowscriptaccess" value="always"></param><param name="movie" value="http://vimeo.com/moogaloop.swf?clip_id=85060026&amp;force_embed=1&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=1&amp;color=00adef&amp;fullscreen=1&amp;autoplay=0&amp;loop=0"></param>

<embed src="http://vimeo.com/moogaloop.swf?clip_id=85060026&amp;force_embed=1&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=1&amp;color=00adef&amp;fullscreen=1&amp;autoplay=0&amp;loop=0" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" width="500" height="281">
</embed>
</object>

<!-- This version of the embed code is no longer supported. Learn more: https://vimeo.com/s/tnm -->
<object width="500" height="281">
<param name="allowfullscreen" value="true"></param><param name="allowscriptaccess" value="always"></param><param name="movie" value="http://vimeo.com/moogaloop.swf?clip_id=85083958&amp;force_embed=1&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=1&amp;color=00adef&amp;fullscreen=1&amp;autoplay=0&amp;loop=0"></param>

<embed src="http://vimeo.com/moogaloop.swf?clip_id=85083958&amp;force_embed=1&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=1&amp;color=00adef&amp;fullscreen=1&amp;autoplay=0&amp;loop=0" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" width="500" height="281">
</embed>
</object>

**Please note the following to understand the video**:
 I make random moves with the king. They are *not actually being submitted* to the
server, they are just shown so in the client side interface (That what
you can see in the browser). **The real moves are updated and modified
by the Stockfish engine and then injected into the WebSocket messages.**
That's also the reason sometimes the chessboard suddenly updates,
because the client side GUI recognizes that it showed the *false* moves.
Then you can see the real moves for a second again.
ou can see the real moves for a second again.
