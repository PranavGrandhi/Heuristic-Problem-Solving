import sys
import socket
import time

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


    def generatemove(self, state):
        '''
        Given the state of the game as input, computes the desired move and returns it.
        NOTE: this is just one way to handle the agent's policy -- feel free to add other
          features or data structures as you see fit, as long as playgame() still runs!
        '''

        raise NotImplementedError

    def playgame(self):
        '''
        Plays through a game of Card Nim from start to finish by looping calls to getstate(),
        generatemove(), and sendmove() in that order
        '''

        while True:
            state = self.getstate()

            if int(state) <= 0:
                break

            move = self.generatemove(state)

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

    def generatemove(self, state):
        to_return = self.i
        self.i += 1

        return to_return

class MyPlayer(Client):
    '''
    Your custom solver!
    '''
    def __init__(self, port=4000):
        super(IncrementPlayer, self).__init__(port)

    def generatemove(self, state):

        move = None
        
        '''
        TODO: put your solver logic here!
        '''

        return move



if __name__ == '__main__':
    if len(sys.argv) == 1:
        port = 4000
    else:
        port = int(sys.argv[1])

    # Change IncrementPlayer(port) to MyPlayer(port) to use your custom solver
    client = IncrementPlayer(port)
    client.playgame()

