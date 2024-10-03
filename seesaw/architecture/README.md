# See Saw Game 

## Problem Statement

 A seesaw is a board balanced at the center that children play on. We are going to explore a very special kind of seesaw onto which we put weights. If the seesaw tilts to the left, then all weights move by one meter to the left. Similarly for the right. When a seesaw tilts to one side, any weight at the end of that side will fall off, thus completely changing the torque on the seesaw.

Strange things can happen. For example, we can arrange a configuration in which a seesaw tilts left, then right, then left again. Further we can think of a game in which each player tries to get as many weights on his or her side as possible.

The game works in rounds: all players will be given the total length L of the seesaw board (which will always be an even number), the maximum weight available to the left side player LeftMax , and the maximum to the right side player RightMax . These maximums will both be positive whole numbers.

In each case the player will in fact be given all the weights from 1 kilogram to the maximum allowed. For example if LeftMax is 5, then the Left player will have weights 1, 2, 3, 4, 5.

Next the Left player places weights on the left side of the seesaw at meter locations, but no weight may be placed on top of another.

After Left is done, Right places weights on the Right side with the same restrictions.

Then the seesaw is allowed to tilt one way and the other. The weights that fall to the Left add to the score of Left. The weights that fall to the Right add to the score of Right. If the seesaw ever settles into a balanced state, then Le
ft gets all the remaining weights.

Each team will play a round as Left player and a round as Right player. The team with the greatest total score wins. 

Check link: https://cs.nyu.edu/courses/fall24/CSCI-GA.2965-001/seesaw.html

## Architecture
The architecture team supplies the length L (40 or less), MaxLeft (15 or less), and MaxRight (15 or less), based on my instructions on the day of the competition. Then the architecture team receives weight placement instructions from Left, displays them on the board, and supplies those locations to the Right team. The architecture team then receives weight placement instructions from Right, displays them on the botard, and simulates the evolution of the seasaw based on torque in which the seesaw tilts, weights move, some fall, etc. Finally, the architecture team records the final score of each round. 


## Starting Server

To begin the server, run:
```bash
php main.php <port> <length L> <max_left> <max_right>
```

This will create a socket for communication to and from the server at `hostname:port`.

## Playing the Game

This game is not a turn based event loop game. The left player has to place weights with no knowledge. Time limit for this is 120s

This weight will be given to the right player. Then right player sends his weight placement. Time limit for this is 120s.

The placement of weights should be given via an array.

The server simulates the torques and gives out the final score.

The boards are array indexed from [0 .. (board_length/2)-1]
- index 0 represents distance from fulcrum 0.5
- index 1 represents distance from fulcrum 1.5
- index 2 represents distance from fulcrum 2.5
- index i represents distance from fulcrum i+0.5

### Illegal Moves

Making an illegal move will result in the player immediately losing the game. This includes:

* Placing the same weight twice
* Sending array of size != boardlength/2;
* If the weights do not lie in the range of [0 .. max_left] or [0 .. max_right]  
## Client

The client will be sending your computation result to server. The requirements for the client are:
- `portnumber` : port no. of server to connect to.
- `is_first`: To tell which client goes first

Note: The client which give `is_first` will always be the left player.

Note: The right client will recieve output of the left client, check for its validity before operating on that array. 

The only function which is of concern is the `place` function:

for cpp client:
```cpp
vector<int> Client::place(vector<int> &other_board){
    ...
}
```

you can check if you are the first player, by checking `is_first` variable in you client member variable.

You can find starter code for each language under `clients/<language>/` folders.
Read the `readme.md` for instructions.

### requirements
`test_no_tipping.py` uses `SocketClient`, install `hps-nyu`:
```
pip install --user hps-nyu
```

## Contact Us
* Gokulkrishna Muthusamy - gm3314@nyu.edu
* Aditya - @nyu.edu