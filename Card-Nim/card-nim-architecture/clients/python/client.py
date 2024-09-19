import sys
from functools import lru_cache
import socket
import time
import math

class TimeoutException(Exception):
    pass

class TimeoutException(Exception):
    pass

class Client():
    def __init__(self, port=4000):
        self.socket = socket.socket()
        self.port = port

        self.socket.connect(("localhost", port))

        # Send over the name
        self.socket.send("Python Client".encode("utf-8"))

        # Wait to get the ready message, which includes whether we are player 1 or player 2
        # and the initial number of stones in the form of a string "{p_num} {num_stones}"
        # This is important for calculating the opponent's move in the case where we go second
        init_info = self.socket.recv(1024).decode().rstrip()

        self.player_num = int(init_info.split(" ")[0])
        self.num_stones = int(init_info.split(" ")[1])
        self.num_cards = int(init_info.split(" ")[2])

    def lastDitchEffort(self, myCards, oppCards, stones):
        # Making a last ditch effort to choose a good card
        for card in myCards:
            if card > stones:
                continue
            leftover = stones - card
            if leftover in oppCards:
                continue
            return False, card, "last ditch effort"
        return False, max(myCards), "can't do anything"

    def whatCardToWin(self, myCards, oppCards, stones, time_limit=10):
        # Estimate cache size to be close to 100GB
<<<<<<< HEAD
        # Assuming each cache entry takes about 2 KB 
        cache_size = 100_000_000 // 2
=======
        # Assuming each cache entry takes about 1 KB 
        cache_size = 100_000_000
>>>>>>> 5e6cb28f6c6a00a5416ab8c23981344974faab9d

        start_time = time.time()

        @lru_cache(maxsize=cache_size)
        def memoized_search(memoMyCards, memoOppCards, stones):
<<<<<<< HEAD
            # print(f"searching myCards: {memoMyCards}, oppCards: {memoOppCards}, stones: {stones}")
=======
>>>>>>> 5e6cb28f6c6a00a5416ab8c23981344974faab9d
            if time.time() - start_time > time_limit:
                raise TimeoutException("Time limit exceeded")

            filteredOppCards = tuple(c for c in memoOppCards if c <= stones)
<<<<<<< HEAD
            filteredMyCards = tuple(c for c in memoMyCards if c <= stones)
=======
            filteredMyCards = tuple(c for c in memoMyCards if c <= stones and (stones - c) not in memoOppCards)
>>>>>>> 5e6cb28f6c6a00a5416ab8c23981344974faab9d

            if len(filteredOppCards) == 0:
                return True, min(memoMyCards), "all opp cards are greater than stones"
            if len(filteredMyCards) == 0:
                return False, min(memoMyCards), "all my cards are greater than stones"
            if stones in filteredMyCards:
                return True, stones, "found exact card"
<<<<<<< HEAD

            cards_to_iterate  = filteredMyCards
            if (len(filteredMyCards) * 2 < stones) and ((2 ** len(filteredMyCards)) * (2 ** len(filteredOppCards)) * stones > 10_000_000):
                # search space is probably too large, taking only the top 5 cards
                truncated_len = max(3, (10 - (len(filteredMyCards) // stones)))
                cards_to_iterate = filteredMyCards[:truncated_len]
            # print("   ")
            # print("***************************************************************************************************************************************")
            # print(f"searching filteredMyCards: {filteredMyCards}, filteredOppCards: {filteredOppCards}, stones: {stones}")
            for card in cards_to_iterate:
                myNewCards = tuple(c for c in memoMyCards if c != card)
                try:
                    # print(f"checking opponent card {card}")
                    oppResult = memoized_search(memoOppCards, myNewCards, stones - card)
                    # print(f"checking opponent card {card}, got result {oppResult}")
                    if oppResult[0] == False:
                        # print(oppResult)
                        # print(f"oppCards: {memoOppCards}, myCards: {memoMyCards}, leftover: {stones - card}")
                        # print(f"filteredOppCards: {filteredOppCards}, filteredMyCards: {filteredMyCards}, leftover: {stones - card}")
                        # print("found a losing condition for opponent")
                        # print("***************************************************************************************************************************************")
                        return True, card, "found a losing condition for opponent", f"oppResult: {oppResult}"
                except TimeoutException:
                    print("TIMEOUT EXCEPTION TIMEOUT EXCEPTION TIMEOUT EXCEPTION")
                    raise
            lastDitchResult = self.lastDitchEffort(memoMyCards, memoOppCards, stones)
            # print(f"Got last ditch result {lastDitchResult}")
            # print("***************************************************************************************************************************************")
=======
            for card in filteredMyCards:
                if (stones-card) < min(memoOppCards):
                    return True, card, "opponent doesn't have lower card"

            cards_to_iterate  = filteredMyCards
            if ((2 ** len(filteredMyCards)) * (2 ** len(filteredOppCards)) * stones > 10_000_000):
                # truncated_len = max(3, (10 - (stones // len(filteredMyCards))))
                truncated_len = min(int(0.5*math.log2(10e7/stones)), len(filteredMyCards))
                cards_to_iterate = filteredMyCards[:truncated_len]

            for card in cards_to_iterate:
                myNewCards = tuple(c for c in memoMyCards if c != card)
                try:
                    oppResult = memoized_search(memoOppCards, myNewCards, stones - card)
                    if oppResult[0] == False:
                        return True, card, "found a losing condition for opponent", f"oppResult: {oppResult}"
                except TimeoutException:
                    print("TIMEOUT EXCEPTION")
                    cards_leftover = [c for c in cards_to_iterate if c <= card]
                    return self.lastDitchEffort(cards_leftover, memoOppCards, stones)

            lastDitchResult = self.lastDitchEffort(memoMyCards, memoOppCards, stones)
>>>>>>> 5e6cb28f6c6a00a5416ab8c23981344974faab9d
            return lastDitchResult

        try:
            # Set the recursion limit to a high value to avoid hitting it
<<<<<<< HEAD
            sys.setrecursionlimit(100000)
=======
            sys.setrecursionlimit(1_000_000)
>>>>>>> 5e6cb28f6c6a00a5416ab8c23981344974faab9d
            result = memoized_search(myCards, oppCards, stones)
            return result
        except (TimeoutException, RecursionError) as e:
            # Making a last ditch effort to choose a good card
            return self.lastDitchEffort(myCards, oppCards, stones)
        

    def getstate(self):
        '''
        Query the server for the current state of the game and wait until a response is received
        before returning
        '''

        # Send the request
        self.socket.send("getstate".encode("utf-8"))

        # Wait for the response (hangs here until response is received from server)
        state_info = self.socket.recv(1024).decode().rstrip()

        # Currently, the only information returned from the server is the number of stones
        num_stones = int(state_info)

        return num_stones

    def sendmove(self, move):
        '''
        Send a move to the server to be executed. The server does not send a response / acknowledgement,
        so a call to getstate() afterwards is necessary in order to wait until the next move
        '''

        self.socket.send(f"sendmove {move}".encode("utf-8"))


    def generatemove(self):
        '''MyPlayer
        Given the state of the game as input, computes the desired move and returns it.
        NOTE: this is just one way to handle the agent's policy -- feel free to add other
          features or data structures as you see fit, as long as playgame() still runs!
        '''
        move = self.whatCardToWin(self.my_cards, self.opp_cards, self.num_stones)
        print(f"move: {move}, stones: {self.num_stones}")
<<<<<<< HEAD
        # if move == None:
        #     # Making a last ditch effort to choose a good card
        #     for card in myCards:
        #         if card > stones:
        #             continue
        #         leftover = stones - card
        #         if leftover in oppCards:
        #             continue
        #         move = False, card
        #         # print(f"move set to {card}")
        #         break
        # if move == None:
        #     move = False, max(self.my_cards)

=======
>>>>>>> 5e6cb28f6c6a00a5416ab8c23981344974faab9d
        return move[1]


    def playgame(self):
        '''
        Plays through a game of Card Nim from start to finish by looping calls to getstate(),
        generatemove(), and sendmove() in that order
        '''
        self.my_cards = tuple(i for i in range(self.num_cards, 0, -1))
        self.opp_cards = tuple(i for i in range(self.num_cards, 0, -1))

        while True:
            self.prev_stones = self.num_stones
            state = self.getstate()

            if int(state) <= 0:
                break
            self.num_stones = state
            opp_used = state - self.prev_stones
            self.opp_cards = tuple(x for x in self.opp_cards if x != opp_used)
            move = self.generatemove()
            self.my_cards = tuple(x for x in self.my_cards if x != move)


            self.sendmove(move)

            time.sleep(0.1)

        self.socket.close()


class IncrementPlayer(Client):
    '''
    Very simple client which just starts at the lowest possible move
    and increases its move by 1 each turn
    '''
    def __init__(self, port=4000):
        super(IncrementPlayer, self).__init__(port)
        self.i = 0

    # def generatemove(self, state):
    #     to_return = self.i
    #     self.i += 1

    #     return to_return

# class MyPlayer(Client):
#     '''
#     Your custom solver!
#     '''
#     def __init__(self, port=4000):
#         super(IncrementPlayer, self).__init__(port)

#     def generatemove(self, state):

#         move = None
        
#         '''
#         TODO: put your solver logic here!
#         '''

#         return move



if __name__ == '__main__':
    if len(sys.argv) == 1:
        port = 4000
    else:
        port = int(sys.argv[1])

    # oppCards = (50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)
    # myCards = (49, 48, 47, 46, 45, 43, 42, 41, 40, 39, 37, 36, 35, 34, 33, 31, 30, 29, 28, 26, 25, 24, 23, 22, 21, 20, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)
    # stones = 54
    # client = IncrementPlayer(port)
    # print(client.whatCardToWin(myCards, oppCards, stones))

    # Change IncrementPlayer(port) to MyPlayer(port) to use your custom solver
    client = IncrementPlayer(port)
    client.playgame()

