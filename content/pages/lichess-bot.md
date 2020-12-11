Title: Lichess Autoplay-Bot
Date: 2015-10-1 13:50
Modified: 2015-10-2 14:33
Author: Nikolai Tschacher
Slug: lichess-bot
Status: published

### Video of Bot in action

Here is another video of the bot in action. He plays **0-1** time controls. This means each player starts with 2 seconds and gets a one second
increment per move. I improved the mouse speed and computation speed, as well as the robustness of the TCP message parsing.

<iframe width="560" height="315" src="https://www.youtube.com/embed/ncF9mqd-iko" frameborder="0" allowfullscreen></iframe>

This is only a test video of the Bot. He doesn't play against stronger opponents in this video. I consider creating a video of the bot playing against stronger opponents (> 2200 ELO).

<iframe src="https://player.vimeo.com/video/141043509" width="500" height="280" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe> <p><a href="https://vimeo.com/141043509">Lichess Cheating Bot autoplay with Bullet time controls</a> from <a href="https://vimeo.com/user24568030">Incolumitas</a> on <a href="https://vimeo.com">Vimeo</a>.</p>

### Lichess Bot

The bot is programmed in Python. It gets the *game state* (such as moves and who's turn it is) by sniffing TCP messages.

This means that moves are being calculated as soon as the opponent move sent from lichess servers reaches our
LAN card.

### Download

Sources will **not** be published this time. This would spoil the fun for chess players. This was just a small project of mine to find the best techniques to cheat on websocket games...

If someone however is deeply interested in the bot, you can send me a message. I will consider giving you the sources. View
the contact page for this: [Contact Page]({filename}/pages/contact.md)
