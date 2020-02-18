Title: Cross platform Lichess Cheat
Date: 2015-08-12 23:24
Modified: 2015-1-10 14:01
Author: Nikolai Tschacher
Category: Chess
Tags: Software, Python, Programming, Chess
Slug: cross-platform-lichess-cheat
Status: published

Edit: Cheat updated on 1.10.2015
--------------------------------

**Visit [Lichess Bot Projects Page]({static}/pages/lichess-bot.md) for the newest information for this bot!**
The description and code below will probably not work anymore!

***

Hello Everyone

Once in a while I like to [play Chess on lichess](http://lichess.org).
But sometimes I get beat up tot harshly, such that I want to take some
revenge :D. Recently I created a new cheat for lichess. You can find the
whole source code on my [lichess cheat github
repository.](https://github.com/NikolaiT/lichess_cheat) If you want to
use the cheat, please follow the following tutorial:

1.  Download and install Python 3.4 (or newer) for your operating system
    from here: [python web site](https://www.python.org/downloads/)
2.  Add Python to your system path such that you can open python file
    from anywhere (This step depends on what operating system you are
    using)
3.  Then download the python cheat from
    [here](https://github.com/NikolaiT/lichess_cheat). It is the file
    with the **.py** suffix
4.  Then execute the python cheat file where you downloaded it. Just go
    to the directory where you saved it and enter in a shell: ``python
    cheat_server.py`
5.  Open your browser (tested with chrome and firefox) and add the HTTP
    proxy server in the network settings that is outputted in the Bash
    shell when you executed `python cheat_server.py`
6.  Then login to lichess and start a new game in which you want to
    cheat. The cheat should now show you the best moves with a red
    border around the chess squares
7.  

For a **video tutorial**l watch the following video: *will follow soon*

For all who are interested in the working of the cheat: You need to know
Python and Javascript. Python code downloads the stockfish engine and
starts a interactive process and communicates with the stockfish binary
over UCI. Then the engine is exposed via a simple web server that the
Javascript cheat makes use of.

Previous cheats didn't intercept the network traffic between the lichess
server and the browser. But new versions make use of [the proxy.py
module](https://github.com/abhinavsingh/proxy.py). Using a proxy has
many advantages such as being able to modify any javascript logic.

Have a nice one.

Cheers

The code
--------

### Javascript cheat to paste in the Browser Console after Python Cheat was run

    :::javascript
    /**
     *
     * https://github.com/NikolaiT/lichess_cheat
     *
     * Just copy paste this file into your browsers javascript console.
     * Make sure the cheat_server.py is running on your localhost before!
     *
     * Author = Nikolai Tschacher
     * Date = Summer 2015
     * Contact = incolumitas.com
     */

    (function() {

     var allMoves = '';
     var incrementTime = parseInt(/\+([0-9]+)/g.exec($('span.setup').text())[1]);
     var ply = -1;
     var uci = null;
     var playerColor = $('.cg-board').hasClass('orientation-black') ? 'black' : 'white';
     var debug = true;

      function addEngineProposalClass() {
          $("")
              .prop("type", "text/css")
              .html("  
             .engineProposal {  
                 border-color: #FF4D4D;  
                 border-width: 3px;  
                 border-style: solid;  
             };  
             .enginePonderProposal {  
                 border-color: #5CADFF;  
                 border-width: 2px;  
                 border-style: solid;  
             }")
              .appendTo("head");
      }

      function highlightEngineProposal(engineMove) {
          var bfrom = engineMove.best.slice(0, 2),
              bto = engineMove.best.slice(2, 4),
              pfrom = engineMove.ponder.slice(0, 2),
              pto = engineMove.ponder.slice(2, 4);

          $('.cg-square').removeClass('engineProposal');
          $('.cg-square').removeClass('enginePonderProposal');

          $('.cg-square.' + bfrom).addClass('engineProposal');
          $('.cg-square.' + bto).addClass('engineProposal');

          $('.cg-square.' + pfrom).addClass('enginePonderProposal');
          $('.cg-square.' + pto).addClass('enginePonderProposal');
      }

      function getLastMove() {

          function getMove(s) { return s.match(/[a-h][0-8]/g); };

          try {
            var to = getMove($('.cg-square.last-move.occupied').attr('class'));
            var from = getMove($('.cg-square.last-move').not('.occupied').attr('class'));
          } catch (e) {
            return '';
          }

          return from+to;
      }

      function getRemainingTime() {
        var time = $('.clock_' + playerColor + ' .time').text();
        var minutes = parseInt(/^([0-9]*?):/g.exec(time)[1]);
        return minutes * 60 + parseInt(time.slice(-2));
      }

      function getEngineMoveByAllMoves() {
          var bestMoves = '';

          $.ajax({
            // /allMoves/e2e4 e7e5/incrementTime/1/remainingTime/60/
          url: "http://localhost:8888/allMoves/" + allMoves + "/incrementTime/" + incrementTime + "/remainingTime/" + getRemainingTime() + "/",
          success: function(html) {
            bestMoves = html;
          },
          async:false
          });

          return {
            'best': bestMoves.slice(0, 4),
            'ponder': bestMoves.slice(5,9)
          };
      }

      function isMyTurn() {
          return (playerColor === 'white' && (ply % 2 === 0)) ||
              (playerColor === 'black' && (ply % 2 === 1));
      }


      function showEngineMove() {
          if (isMyTurn()) {
              engineMoves = getEngineMoveByAllMoves();
              highlightEngineProposal(engineMoves);
          }
      }

      addEngineProposalClass();

      if (playerColor === 'black') {
        uci = '';
        ply++;
      }

      setInterval(function() {
          var lastMove = getLastMove();

          if (uci !== lastMove) {
            // new next move!
            uci = lastMove;
            ply++;
            allMoves += (' ' + uci);

            if (debug) {
              console.log(playerColor);
              console.log("My turn: " + isMyTurn());
              console.log(allMoves);
              console.log(ply);
              console.log(uci);
            }
            showEngineMove();

          }

      }, 75);

    })();


### This python file downloads and runs stockfish and must be run first

    :::python
    #!/usr/bin/env python3

    # https://github.com/NikolaiT/lichess_cheat
    # Implements a RESTful Api to the stockfish engine.
    # You may call this RESTful API with a request as the follows:
    # http://localhost:8888/allMoves/e2e4 e7e5/incrementTime/1/remainingTime/60/
    # All times are in seconds.

    __author__ = 'Nikolai Tschacher'
    __contact__ = 'incolumitas.com'
    __date__ = 'Summer 2015'

    import subprocess
    import os
    import time
    import sys
    import re
    import random
    import urllib.request
    from urllib.parse import unquote
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import socketserver
    import zipfile
    import pprint

    config = {
      'stockfish_download_link': 'https://stockfish.s3.amazonaws.com/stockfish-6-{}.zip',
        'stockfish_binary' : '', # the path to your local stockfish binary
      'pwd': os.path.dirname(os.path.realpath(__file__)),
      'debug': True,
      'thinking_time': 1,
      'max_thinking_time': 2, # in seconds
    }

    def unzip(source_filename, dest_dir):
      """
      Taken from:
      http://stackoverflow.com/questions/12886768/how-to-unzip-file-in-python-on-all-oses
      """
      with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
          # Path traversal defense copied from
          # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
          words = member.filename.split('/')
          path = dest_dir
          for word in words[:-1]:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir, ''): continue
            path = os.path.join(path, word)
          zf.extract(member, path)

    def install_stockfish():
      """
      Grabs the latest stockfish binary and installs it besides the script.
      """
      dl = config.get('stockfish_download_link')
      binary_path = ''

      if os.name == 'nt':
        dl = dl.format('windows')
        binary_path = os.path.join(config.get('pwd'), 'Windows\\stockfish-6-64.exe')
      elif os.name == 'posix' and sys.platform.startswith('linux'):
        dl = dl.format('linux')
        binary_path = os.path.join(config.get('pwd'), 'stockfish-6-linux/Linux/stockfish-6-linux/Linux/stockfish_6_x64')
      elif sys.platform.startswith('darwin'):
        dl = dl.format('mac')
        binary_path = os.path.join(config.get('pwd'), 'stockfish-6-mac/Mac/stockfish-6-64')
      else:
        exit('System {} is not supported.'.format(os.name))

      if not os.path.exists(binary_path):
        save_in = os.path.join(config.get('pwd'), 'stockfish.zip')
        request = urllib.request.URLopener()
        request.retrieve(dl, save_in)
        unzip(save_in, config.get('pwd'))
        os.unlink(save_in)

        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
          os.system('chmod +x {}'.format(binary_path))

      config['stockfish_binary'] = binary_path

      if config.get('debug', False):
        pprint.pprint(config)


    class StockfishEngine():
      """Implements all engine related stuff"""

      def __init__(self, stockfish_plays_white=True):
        """
        Sets the engine up.

        stockfish_plays_white determines whether stockfish is white or black. If
        stockfish is white, it needs to make the first move.

        thinking_time controls how much time stockfish is given to calculate its moves.
        max_thinking_time determines the maximum thinking time the engine has.
        """
        self.max_thinking_time = config.get('max_thinking_time', 2)
        self.thinking_time = config.get('thinking_time', 1)
        self.stockfish_plays_white = stockfish_plays_white
        self.proc = None
        self.moves = []
        self.fen = ''

        self.init_stockfish()

      def get(self, poll=True, sleep_time=0):
        if poll:
          self.proc.stdin.write('isready\n')
        buf = ''
        while True:
          time.sleep(sleep_time)
          line = self.proc.stdout.readline().strip()
          buf += line
          if 'readyok' in line:
            return buf
          if 'bestmove' in line:
            return buf

      def init_stockfish(self):
        if os.path.exists(config['stockfish_binary']):
          self.proc = subprocess.Popen([config['stockfish_binary']], universal_newlines=True,
                      stdout=subprocess.PIPE, stdin=subprocess.PIPE)

          greeting = self.get(self.proc)
          if not 'Stockfish' in greeting:
            raise ValueError('Couldnt execute stockfish')

          self.proc.stdin.write('uci\n')
          self.get()
          # stolen from https://github.com/brandonhsiao/lichess-bot/blob/master/server.py
          self.proc.stdin.write('ucinewgame\n')
          self.get()
          # some of theese options are not supported. Doesn't harm us...
          self.proc.stdin.write('setoption name Hash value 128\n')
          self.proc.stdin.write('setoption name Threads value 4\n')
          self.proc.stdin.write('setoption name Best Book Move value true\n')
          self.proc.stdin.write('setoption name Aggressiveness value 200\n')
          self.proc.stdin.write('setoption name Cowardice value 0\n')
          self.proc.stdin.write('setoption name Contempt Factor value 50\n')
        else:
          raise ValueError('No stockfish binary path given')

      def whos_move_is_it(self):
        return 'white' if (len(self.moves) % 2 == 0) else 'black'

      def start_move_calculation(self, remaining_time=None, increment_time=None):
        """
        When remaining_time and increment_time are given, the best move
        is calculated considering the remaining time. If not, the thinking_time
        given in the config is considered.
        """
        if remaining_time and increment_time:
          remaining_time, increment_time = int(remaining_time) * 1000, int(increment_time) * 1000
          if self.whos_move_is_it() == 'white':
            cmd = 'go wtime {} winc {}\n'.format(remaining_time, increment_time)
          else:
            cmd = 'go btime {} binc {}\n'.format(remaining_time, increment_time)

          self.proc.stdin.write(cmd)
          out = self.get(poll=False)
        else:
          self.proc.stdin.write('go infinite\n')
          sleep_time = self.thinking_time if self.max_thinking_time < self.thinking_time else self.max_thinking_time
          try:
            time.sleep(float(sleep_time))
          except ValueError as ve:
            print(ve)
            sys.exit(0)
          self.proc.stdin.write('stop\n')
          out = self.get(poll=False)

        try:
          bestmove = re.search(r'bestmove\s(?P[a-h][1-8][a-h][1-8])', out).group('move')
          ponder = re.search(r'ponder\s(?P[a-h][1-8][a-h][1-8])', out).group('ponder')
        except AttributeError:
          return False

        return bestmove, ponder

      def newgame_stockfish(self, stockfish_plays_white=True, fen='',
                  all_moves=None, remaining_time=None, increment_time=None):
        self.stockfish_plays_white = stockfish_plays_white
        self.moves = []

        if fen:
          self.fen = fen
          self.proc.stdin.write('position fen {}\n'.format(fen))
          return self.start_move_calculation(remaining_time, increment_time)

        if all_moves is not None:
          self.moves = all_moves.split(' ')
          if all_moves:
            self.proc.stdin.write('position startpos moves {}\n'.format(all_moves))
          else:
            self.proc.stdin.write('position startpos\n')

          return self.start_move_calculation(remaining_time, increment_time)

      def quit_stockfish(self):
        self.proc.stdin.write('quit\n')
        self.proc.terminate()


    class StockfishServer(BaseHTTPRequestHandler):

        def get_param(self, names):
          if not isinstance(names, tuple):
            raise ValueError('variable "names" must be a tuple')

          ns = {}
          for name in names:
            try:
              ns[name] = re.search(r'{name}/(?P<{name}>[^/]*?)/'.format(name=name), self.path).group(name)
            except:
              ns[name] = None

          return ns

        def do_GET(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            if self.path.startswith('/lastPosFen/'):
              fen = self.get_param(('lastPosFen', )).get('lastPosFen', '')
              best, ponder = engine.newgame_stockfish(fen=unquote(fen))
              self.wfile.write(bytes(best + ' ' + ponder, "utf-8"))
            elif self.path.startswith('/allMoves/'):
              params = self.get_param(('allMoves', 'remainingTime', 'incrementTime'))
              if config.get('debug', False):
                pprint.pprint(params)
              best, ponder = engine.newgame_stockfish(
                              all_moves=unquote(params['allMoves']),
                              remaining_time=params['remainingTime'],
                              increment_time=params['incrementTime'])
              self.wfile.write(bytes(best + ' ' + ponder, "utf-8"))

    def run(engine, server_class=HTTPServer, handler_class=StockfishServer):
        server_address = ('', 8888)
        httpd = server_class(server_address, handler_class)
        print('[+] Running CheatServer.py on {}:{}'.format(server_address[0], server_address[1]))
        httpd.engine = engine
        httpd.serve_forever()


    if __name__ == '__main__':
      install_stockfish()
      engine = StockfishEngine()
      run(engine)
