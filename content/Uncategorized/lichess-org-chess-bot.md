Title: Lichess.org chess bot!
Date: 2014-04-23 18:03
Author: Nikolai Tschacher
Category: Uncategorized
Tags: Uncategorized, Programming, Chess
Slug: lichess-org-chess-bot
Status: published

**22.05.2014: Updated the bot, should work better now**

Hi everyone!

I was in a coding mood during Easter and decided to write a small chess
bot with
[selenium](http://selenium-python.readthedocs.org/en/latest/ "selenium python")
and [stockfish](http://stockfishchess.org/ "stockfish engine") engine to
cheat a bit on
[lichess.org](http://en.lichess.org/ "lichess chess arena").

I think the code is pretty self explanatory and I won't discuss it in
depth here. You can tweak the config, the comments should explain what
the parameters do.

The config is in the beginning of the code, so modify it there. You
should maybe modify it to use your username and password. Make sure that
you download stockfish and install it. Then supply the correct path in
the 'stockfish\_binary' parameter.

As always: Have fun!

Some open issues:

+ Sometimes the last move fails because the bot won't to start a new game
  before it can checkmate
+ Promoting doesn't work yet :/

Here is the code:

    :::python
    __author__ = 'nikolai'
    __date__ = 'Easter 2014'

    config = {
        'username' : 'probably_a_spider', # the login username
        'password' : 'somepwd', # the login password
        'stockfish_binary' : '/home/nikolai/PycharmProjects/LichessBot/stockfish-dd-src/src/stockfish', # the path to your local stockfish binary
        #Set to true if the bot should play forever
        'pwn_forever' : True, # if the bot should play endlessly
        'min_per_side' : 1, # how long each player may play
        'increment' : 0, # the increment per move
        'thinking_time': .5, # How long stockfish is allowd to search, set to None and stockfish will search 0.75 seconds by default
        'thinking_skew': .2 # This is the maximal random derivative in decimal of the thinking time (0-1) (to not make the bot to appear to move in the same time intervals all the time)
    }

    from selenium import webdriver
    from selenium.webdriver import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
    import subprocess
    import os
    import time
    import sys
    import re
    import random

    def get(proc, poll=True):
        if poll:
            proc.stdin.write('isready\n')
        buf = ''
        while True:
            line = proc.stdout.readline().strip()
            buf += line
            if 'readyok' in line:
                return buf
            if 'bestmove' in line:
                return buf

    def init_stockfish():
        if os.path.exists(config['stockfish_binary']):
            proc = subprocess.Popen([config['stockfish_binary']], universal_newlines=True,
                                    stdout=subprocess.PIPE, stdin=subprocess.PIPE)

            greeting = get(proc)
            if not 'Stockfish' in greeting:
                raise ValueError('Couldnt execute stockfish')

            proc.stdin.write('uci\n')
            get(proc)
            # stolen from https://github.com/brandonhsiao/lichess-bot/blob/master/server.py
            proc.stdin.write('ucinewgame\n')
            proc.stdin.write('setoption name Hash value 128\n')
            proc.stdin.write('setoption name Threads value 4\n')
            proc.stdin.write('setoption name Best Book Move value true\n')
            proc.stdin.write('setoption name Aggressiveness value 200\n')
            proc.stdin.write('setoption name Cowardice value 0\n')
            proc.stdin.write('setoption name Contempt Factor value 50\n')
            return proc

    proc = init_stockfish()

    def make_move(thinking_time=.5, moves=[]):
        if moves:
            cmd = 'position startpos moves {}\n'.format(' '.join(moves))
            proc.stdin.write(cmd)
        proc.stdin.write('go infinite\n')
        try:
            time.sleep(float(thinking_time))
        except ValueError as ve:
            print(ve)
            sys.exit(0)
        proc.stdin.write('stop\n')
        out = get(proc, False)
        try:
            bestmove = re.search(r'bestmove\s(?P[a-h][1-8][a-h][1-8])', out).group('move')
            ponder = re.search(r'ponder\s(?P[a-h][1-8][a-h][1-8])', out).group('ponder')
        except AttributeError:
            return False
        return bestmove

    def newgame_stockfish():
        proc.stdin.write('ucinewgame\n')
        get(proc)

    def quit_stockfish():
        proc.stdin.write('quit\n')
        proc.terminate()

    def login():
        wd = webdriver.Firefox()
        wd.get('http://en.lichess.org/login')
        u, p = wd.find_element_by_name("username"), wd.find_element_by_name("password")
        u.send_keys(config['username'])
        p.send_keys(config['password'])
        p.submit()
        return wd

    def create_game(wd, min_per_side=config['min_per_side'], increment=config['increment']):
        wait = WebDriverWait(wd, 10)
        try:
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'a[title="Create a game"]')))
            element.click()
        except UnexpectedAlertPresentException:
            pass
        except Exception as e:
            print(e)

        WebDriverWait(wd, 5).until(EC.presence_of_element_located((By.ID, 'increment')));
        # Change the inputs with a bit of jQuery (but wait first until the dom bitch is loaded)
        wd.execute_script("$('#time').val('{}')".format(str(min_per_side)))
        wd.execute_script("$('#increment').val('{}')".format(str(increment)))
        time.sleep(1)
        wd.find_element_by_name('color').submit()


    def play(wd):
        def move(moves=[]):
            t = config['thinking_time'] or .75
            if config['thinking_skew']:
                t = t * (1 - random.randint(0, config['thinking_skew']*1000) / 1000)

            move = make_move(thinking_time=t, moves=moves)
            if move:
                print('[i]Bot is going to make move {} by calculating {} seconds'.format(move, float(t)))
                f, t = move[:2], move[2:]
                for i in range(6):
                    action = ActionChains(wd)
                    action.drag_and_drop(wd.find_element_by_id(f), wd.find_element_by_id(t))
                    action.perform()
                    try:
                        moved = wd.find_elements_by_css_selector('div.moved.lcs')
                        move1, move2 = moved[0].get_attribute('id'), moved[1].get_attribute('id')
                        if t == move1 or f == move1:
                            break
                    except:
                        break
                    time.sleep(.2)
                return move
            else:
                return False

        def get_last_move(moves=[]):
            WebDriverWait(wd, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.moved.lcs')))
            t = wd.find_element_by_css_selector('div.moved.lcs div.piece').find_element_by_xpath('..').get_attribute('id')
            f = [e.get_attribute('id') for e in wd.find_elements_by_css_selector('div.moved.lcs') if e.get_attribute('id') != t][0]
            # If last move was my last move, sleep a bit and try again to get the next move
            if moves:
                print(f+t, moves[-1])
                while f+t == moves[-1]:
                    # busy polling, that's very inefficient
                    time.sleep(.35)
                    t = wd.find_element_by_css_selector('div.moved.lcs div.piece').find_element_by_xpath('..').get_attribute('id')
                    f = [e.get_attribute('id') for e in wd.find_elements_by_css_selector('div.moved.lcs') if e.get_attribute('id') != t][0]
                    try:
                        wd.find_element_by_css_selector('div.table_with_clock.finished')
                        return False
                    except NoSuchElementException:
                        pass
            print('[i]Opponent moved {}'.format(f+t))
            return f+t

        try:
            # wait maximally 100 seconds for an opponent
            wait = WebDriverWait(wd, 100)
            # wait until the square a1 is present which means we got a board
            element = wait.until(EC.presence_of_element_located((By.ID,'a1')))
        except TimeoutException as te:
            print("No board found: {}".format(te))
            sys.exit(0)

        print('We got a board, games beginning...')

        moves = []
        # detect what color we play
        players  = wd.find_elements_by_css_selector('.player > a')
        is_black = False
        for e in players:
                is_black = config['username'] in e.get_attribute('href') and 'black' in e.get_attribute('class')
        print('[i]Bot is playing {}'.format(['white', 'black'][is_black]))
        if not is_black:
            moves.append(move())

        while True:
            print('[i] Moves played: {}'.format(moves), end='\n\n')

            last = get_last_move(moves)
            print('last move found was {}'.format(last))
            if last:
                moves.append(last)
            else:
                print('no last move appended. Leaving: {}'.format(last))
                return

            m = move(moves)
            if m:
                moves.append(m)
            else:
                return
            try:
                wd.find_element_by_css_selector('div.table_with_clock.finished')
                return
            except:
                pass

    def go_forever():
        wd = login()
        while True:
            create_game(wd)
            newgame_stockfish()
            play(wd)
            wd.get('http://en.lichess.org/')

        quit_stockfish()

    if __name__ == '__main__':
        if config['pwn_forever']:
            go_forever()
        else:
            wd = login()
            create_game(wd)
            play(wd)
