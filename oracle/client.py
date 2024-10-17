import socket
import random
import time
import sys

random.seed(11)

def send_move(socket, move: bool):
    msg = b"BET" if move else b"PASS"
    socket.send(msg)

import random
import math

class BettingStrategy:
    def __init__(self):
        self.total_flips = 0
        self.prior_prob_90 = 0.8
        self.bad_windows_count = 0
        self.currently_in_bad_window = False
        self.current_bad_window_start = 100000000
        self.window_size_70 = 500

    def update_bayesian(self, hit):
        # bad window over
        if self.currently_in_bad_window and (self.total_flips > self.window_size_70 + self.current_bad_window_start):
            self.currently_in_bad_window = False
            self.bad_windows_count = self.bad_windows_count + 1
            self.prior_prob_90 = 0.9
        
        likelihood_90 = 0.9 if hit else 0.1
        likelihood_70 = 0.7 if hit else 0.3
        
        posterior_90 = (likelihood_90 * self.prior_prob_90) / ((likelihood_90 * self.prior_prob_90) + (likelihood_70 * (1 - self.prior_prob_90)))
        posterior_90 = min(posterior_90, 0.99)
        # print(f"hit: {hit}, prior_prob_90: {self.prior_prob_90}, posterior_90: {posterior_90}, current_bad_window_start: {self.current_bad_window_start}")
        if posterior_90 < 0.1 and not self.currently_in_bad_window:
            # bad window started around 50 turns ago
            self.current_bad_window_start = self.total_flips - 50
            self.bad_windows_count = self.bad_windows_count + 1
            self.currently_in_bad_window = True
        self.prior_prob_90 = (posterior_90 + self.prior_prob_90) / 2

    def should_bet(self):
        if self.currently_in_bad_window:
            return False
        if self.bad_windows_count >= 4:
            return True
        return self.prior_prob_90 > 0.6 or self.total_flips < 50

betting_strategy = BettingStrategy()

def strategy():
    should_bet = betting_strategy.should_bet()
    return should_bet

def recv_result(socket):
    data = socket.recv(1024).decode()
    hit = data[:3] == "HIT"
    betting_strategy.update_bayesian(hit)
    betting_strategy.total_flips += 1
    return hit

def main():
    host = 'localhost'
    port = 5555 if (len(sys.argv)<2) else int(sys.argv[1])

    client_socket = socket.socket()
    client_socket.connect((host, port))
    client_socket.send(b"PLAY VGA")
    client_socket.recv(4)

    i = 0
    while i<10000:
        time.sleep(0.001)
        send_move(client_socket, strategy())
        recv_result(client_socket)
        i += 1

if __name__ == '__main__':
    main()
