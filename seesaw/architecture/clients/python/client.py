import json
from random import choice
from hps.clients import SocketClient
from time import sleep
import argparse
import ast
import random
import math

HOST = "localhost"
PORT = 5000

import random
import math

def simulate_seesaw(left_weights, right_weights, board_length):
    left = left_weights.copy()
    right = right_weights.copy()
    half_length = board_length // 2
    left_score = 0
    right_score = 0

    while True:
        left_torque = sum((i + 0.5) * w for i, w in enumerate(left) if w > 0)
        right_torque = sum((i + 0.5) * w for i, w in enumerate(right) if w > 0)
        
        if left_torque > right_torque:
            # Tilt left
            left_score += left[-1]  # Leftmost weight falls off
            left = [right[0]] + left[:-1]
            right = right[1:] + [0]
        elif right_torque > left_torque:
            # Tilt right
            right_score += right[-1]  # rightmost weight falls off
            right = [left[0]] + right[:-1]
            left = left[1:] + [0]
        else:
            # Balanced
            break
        
        # If all weights have fallen off, end the simulation
        if sum(left) == 0 and sum(right) == 0:
            break

    # Add remaining weights to left_score (as per game rules)
    left_score += (sum(left) + sum(right))

    return left_score, right_score

def calculate_score(right_weights, left_weights, board_length):
    _, right_score = simulate_seesaw(left_weights, right_weights, board_length)
    return right_score

def generate_initial_solution(max_right, board_length):
    half_length = board_length // 2
    weights = list(range(1, max_right + 1))
    solution = [0] * half_length
    
    # Randomly select positions for weights
    positions = random.sample(range(half_length), min(len(weights), half_length))
    
    for i, pos in enumerate(positions):
        if i < len(weights):
            solution[pos] = weights[i]
    
    return solution

def get_neighbor(solution, max_right, board_length):
    neighbor = solution.copy()
    index1, index2 = random.sample(range(board_length // 2), 2)
    neighbor[index1], neighbor[index2] = neighbor[index2], neighbor[index1]
    return neighbor

def simulated_annealing(left_weights, max_right, board_length, initial_temperature=10000, cooling_rate=0.995, iterations=100000):
    current_solution = generate_initial_solution(max_right, board_length)
    current_score = calculate_score(current_solution, left_weights, board_length)
    best_solution = current_solution
    best_score = current_score
    temperature = initial_temperature

    for _ in range(iterations):
        neighbor = get_neighbor(current_solution, max_right, board_length)
        neighbor_score = calculate_score(neighbor, left_weights, board_length)

        if neighbor_score > current_score or random.random() < math.exp((neighbor_score - current_score) / temperature):
            current_solution = neighbor
            current_score = neighbor_score

        if current_score > best_score:
            best_solution = current_solution
            best_score = current_score

        temperature *= cooling_rate

    return best_solution

def right_player(left_weights, max_right, board_length):
    return simulated_annealing(left_weights, max_right, board_length)

class NoTippingClient(object):
    def __init__(self, name, is_first):
        self.first_resp_recv = False
        self.name = name
        self.client = SocketClient(HOST, PORT)
        self.client.send_data(json.dumps({"name": self.name, "is_first": is_first}))
        response = json.loads(self.client.receive_data())
        # self.board_length = response['board_length']
        # self.max_left = response['max_left']
        # self.max_right = response['max_right']
        self.is_first = is_first

    def play_game(self):
        print("[INFO] Starting game ...")
        response = {}

        response = json.loads(self.client.receive_data())
        if "game_over" in response and response["game_over"] == "1":
            print("Game Over!")
            exit(0)

        other_board = []

        self.board_length = response["board_length"]
        self.max_left = response["max_left"]
        self.max_right = response["max_right"]
        if self.is_first == False:
            other_board = ast.literal_eval(response["left_board"])

        board = self.place(other_board)
        sboard = str(board)

        self.client.send_data(json.dumps({"board": sboard}))

    # TODO: complete the function here
    def place(self, other_board):
        length = self.board_length // 2
        solution = [0] * length
        if self.is_first:
            # solution = [0,0,1,5,2,0,3,4,7,6]
            starting_index = max(0, length - self.max_left)
            starting_weight = max(1, self.max_right - length)
            for i in range(starting_index, length):
                solution[i] = starting_weight
                starting_weight = starting_weight + 1
        else:
            solution = right_player(other_board, self.max_right, self.board_length)
        print(solution)
        return solution


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--first",
        action="store_true",
        default=False,
        help="Indicates whether client should go first",
    )
    parser.add_argument("--ip", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--name", type=str, default="Python Demo Client")
    args = parser.parse_args()

    HOST = args.ip
    PORT = args.port

    player = NoTippingClient(args.name, args.first)
    player.play_game()
