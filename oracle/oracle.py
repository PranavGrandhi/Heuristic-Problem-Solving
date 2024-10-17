import argparse
import socket
import random
import sys
import os
import atexit
import time

debug_mode = False
def debug(*args, **kwargs):
    if debug_mode:
        print(*args, **kwargs)

############################## UI and Competition ###################################

class Competition:
    def __init__(self):
        # (score, team_name)
        self.hiscores = []
        self.current_game = None
        self.previous_score = None

def CSI(*args):
    out = bytearray()
    for arg in args:
        out += b"\x1b["
        out += arg.encode('utf-8')
    sys.stdout.buffer.write(out)
    sys.stdout.flush()

def printflush(string):
    print(string, end="", flush=True)

def draw_ui_initial():
    tui_w, tui_h = os.get_terminal_size()
    current_game_row = int(tui_h / 2 - 2)
    CSI("H", "J", "?25l")
    CSI("38;2;0;0;0m", "48;2;0;255;255m", "2K");
    CSI("{}G".format(int(tui_w/2) - 7))
    printflush("ORACLEMATIC")
    CSI("2;1H", "38;2;255;255;255m", "48;2;0;32;128m", "2K");
    for y in range(1, tui_h+1):
        CSI("E ", "{}G ".format(tui_w)) # side borders
    CSI("2K") # bottom border

    CSI("2;{}H".format(int(tui_w/2)-7))
    printflush("High Scores")
    CSI("{};{}H".format(current_game_row, int(tui_w/2)-7), "2K");
    printflush("Current Game")
    CSI("0m")

def draw_ui(competition):
    tui_w, tui_h = os.get_terminal_size()
    current_game_row = int(tui_h / 2 - 2)
    CSI("3;2H")
    for i, score in enumerate(competition.hiscores):
        if (i >= (current_game_row-3)):
            break
        printflush("{:6} {: <12d} {}".format("{}.".format(i+1), score[0], score[1])) 
        CSI("E", "2G")

    CSI("0m", "{};2H".format(current_game_row+1))
    if competition.current_game:
        g = competition.current_game
        printflush("Team name: {:<16}\n".format(g.team_name))
        CSI("E", "2G")
        printflush("Turn #: {:04d}\n".format(g.turn))
        CSI("E", "2G")
        printflush("Current score: {:<10d}\n".format(g.score))
        CSI("E", "2G")
        tl = int(g.time_left)
        printflush("Time remaining: {}:{}\n".format(tl//60, tl%60))
    else:
        print("Waiting for connection...")

############################# Game and server logic ############################

def read_key_file(key_file):
    with open(key_file, 'r') as f:
        res = [ int(x) for x in f.readlines() ]
    return res

class Game:
    def __init__(self, team_name, key_file=None):
        self.team_name = team_name
        # must be non-overlapping, that is, at least 500 apart
        if key_file:
            self.key = read_key_file(key_file)
        else:
            self.key = [ 100, 600, 1100, 2000 ]
        self.turn = 0
        self.flaky = (0 in self.key)
        self.score = 0
        self.active_bet = False
        self.time_left = 120.001
        random.seed(12)

    def Pass(self):
        self.active_bet = False

    def bet(self):
        self.active_bet = True

    def next_turn(self):
        self.turn += 1
        self.active_bet = False
        if (self.turn - 500) in self.key:
            self.flaky = False
        if self.turn in self.key:
            self.flaky = True

    def flip(self):
        threshold = 0.7 if self.flaky else 0.9
        result = (random.random() <= threshold)
        if self.active_bet:
            if result:
                self.score += 100
            else:
                self.score -= 700
        self.next_turn() 
        return result

def game_with_client(competition, client_socket, addr):
    game = competition.current_game
    while game.turn<10000:
        turn = game.turn
        if debug_mode:
            debug("turn {}: score {}.".format(game.turn, game.score))
        else:
            draw_ui(competition)
        try:
            begin = time.time()
            msg = client_socket.recv(8)
            game.time_left -= (time.time() - begin)
            if game.time_left < 0:
                break
            if msg[:3] == b'BET':
                action = True
                game.bet()
            elif msg[:4] == b'PASS':
                action = False
                game.Pass()
            elif msg == b'':
                debug(f"{addr} disconnected.")
                break;
            else:
                debug("Invalid message, ignored:", msg.decode())
                # no flip until we get a valid message
                continue
        except Exception as e:
            debug(f"Player error: {addr}: {e}")
            break

        # update score, increment game.turn
        result = game.flip()
        # hit: the oracle predicted right. If you bet, you won
        # miss: the oracle predicted wrong. If you bet, you lost
        resp = b"HIT" if result else b"MISS"
        client_socket.send(resp)
        
    client_socket.close()

def exitroutine():
    # reset colors; restore cursor
    CSI("J", "0m", "?25h");

def main():
    global debug_mode
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5555)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-k', '--keyfile')
    args = parser.parse_args()
    if args.debug:
        debug_mode = True

    competition = Competition()
    if not debug_mode:
        draw_ui_initial()
        draw_ui(competition)
    atexit.register(exitroutine)
    host = '0.0.0.0'
    port = args.port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # allow restarting server on the same port
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    while True:
        debug(f"Listening on {host}:{port}...")
        client_socket, addr = server.accept()
        debug("New incoming connection...", end = " ", flush=True)
        msg = client_socket.recv(64)
        if msg[:4] == b"PLAY":
            if len(msg) > 5 and msg[5:].decode().strip():
                game = Game(msg[5:].decode().strip(), args.keyfile)
            else:
                game = Game("Team {}".format(len(competition.hiscores)), args.keyfile)

            competition.current_game = game
            client_socket.send(b"ACK") 
            debug("The game begins!")
            game_with_client(competition, client_socket, addr)
            competition.hiscores.append((game.score, game.team_name))
            competition.previous_score = game.score
            competition.hiscores.sort(reverse=True)
            competition.current_game = None
            if not debug_mode:
                draw_ui(competition)
        else:
            debug("Invalid message")
            pass

if __name__=='__main__':
    main()
