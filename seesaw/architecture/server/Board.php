<?php
include 'Player.php';

class Board
{
    public $boardLength;
    public $gameOver;
    public $gameOverReason;

    public $time_left;
    public $player1;
    public $player2;
    
    public $currentPlayer;
    public $left_board;
    public $right_board;
    public $max_left;
    public $max_right;
    
    public $leftTorque;
    public $rightTorque;
    public $winner;

    public function calculate_left_torque(){
        $torque = 0.0;
        for($i=0; $i<count($this->left_board); $i++){
            $torque = $torque + ($i+0.5)*$this->left_board[$i];
        }
        return $torque;
    }

    public function calculate_right_torque(){
        $torque = 0.0;
        for($i=0; $i<count($this->right_board); $i++){
            $torque = $torque + ($i+0.5)*$this->right_board[$i];
        }
        return $torque;
    }

    public function print_seesaw(){
        $left_board = $this->left_board;   
        $right_board = $this->right_board;
        $n = count($left_board);

        for($i=$n-1; $i>=0; $i--){
            echo "[$left_board[$i]] ";
        }
        echo "A";
        for($i=0; $i<=$n-1; $i++){
            echo " [$right_board[$i]]";
        }
        echo "\n";
    }

    public function checkBoardValidity(){
        // check validity of left board 
        $is_left_valid = true;
        $n = count($this->left_board);
        $visited = array_fill(0, $this->max_left, 0);
        for($i = 0; $i < $n; $i++){
            if($this->left_board[$i] > $this->max_left || $this->left_board[$i] < 0){
                $is_left_valid = false;
                break;
            }
            if($this->left_board[$i] !=0 && $visited[$this->left_board[$i]] == 1){
                $is_left_valid = false;
                break;
            }
            $visited[$this->left_board[$i]] = 1;
        }
        // check validity of right board
        $is_right_valid = true;
        $n = count($this->right_board);
        $visited = array_fill(0, $this->max_right, 0);
        for($i = 0; $i < $n; $i++){
            if($this->right_board[$i] > $this->max_right || $this->right_board[$i] < 0){
                $is_right_valid = false;
                break;
            }
            if($this->right_board[$i] !=0 && $visited[$this->right_board[$i]] == 1){
                $is_right_valid = false;
                break;
            }
            $visited[$this->right_board[$i]] = 1;
        }

        // check for the size of the array match
        if(count($this->left_board) != $this->boardLength/2){
            $is_left_valid = false;
        }

        if(count($this->right_board) != $this->boardLength/2){
            $is_right_valid = false;
        }

        if($is_left_valid == false && $is_right_valid == false){
            echo "BOTH INVALID OUTPUT\n";
            $this->gameOver = true;
        }else if($is_left_valid == false && $is_right_valid == true){
            echo "LEFT INVALID and RIGHT VALID\n";
            echo "RIGHT PLAYER WINS [ $this->player2 ]\n";
            $this->gameOver = true;
        }else if($is_left_valid == true && $is_right_valid == false){
            echo "LEFT VALID and RIGHT INVALID\n";
            echo "LEFT PLAYER WINS [ $this->player1 ]\n";
            $this->gameOver = true;
        }else{
            // do nothing.
            ;
        }
    }

    /**
     * This function simulates the game
     * 1. Calculate the torque.
     * 2. If torque is equal, add weights to left player and end game.
     * 3. Tip the torque to higher side and move the blocks.
     * 4. repeat.
     * 5. Check the weight of the players 
     */
    function simulateGame(){
        $left_score = 0;
        $right_score = 0;
        
        $left_board = $this->left_board;
        $right_board = $this->right_board;

        $timestamp = 0;
        echo "BEGINNING CONFIG \n";
        $this->print_seesaw();

        while(true){
            // calculate left torque
            $timestamp = $timestamp + 1;
            $leftTorque = $this->calculate_left_torque();
            $rightTorque = $this->calculate_right_torque();

            echo "---------------------------------------------------\n";
            echo "TimeStamp: $timestamp\n";
            echo "Left torque: $leftTorque\n";
            echo "Right torque: $rightTorque\n";

            // n is same for left and right board;
            $n = count($left_board);
            if($leftTorque == $rightTorque){
                for($i=0; $i < $n; $i++){
                    $left_score = $left_score + $left_board[$i];
                    $left_score = $left_score + $right_board[$i];
                }
                break;
            }elseif($leftTorque > $rightTorque){
                $left_score = $left_score + $left_board[$n-1];
                for($i= $n-1; $i >= 1; $i--){
                    $left_board[$i] = $left_board[$i-1];
                }
                $left_board[0] = $right_board[0];
                for($i=0; $i < $n-1 ; $i++){
                    $right_board[$i] = $right_board[$i+1];
                }
                $right_board[$n-1] = 0;
            }else{
                $right_score = $right_score + $right_board[$n-1];
                for($i=$n-1; $i >=1; $i--){
                    $right_board[$i] = $right_board[$i-1];
                }
                $right_board[0] = $left_board[0];
                for($i=0; $i<$n-1; $i++){
                    $left_board[$i] = $left_board[$i+1];
                }
                $left_board[$n-1] = 0;
            }

            $this->left_board = $left_board;
            $this->right_board = $right_board;

            // do a terminal print function
            $this->print_seesaw();
            echo "LEFT SCORE: $left_score \n";
            echo "RIGHT SCORE: $right_score \n";

        }

        echo "LEFT SCORE: $left_score \n";
        echo "RIGHT SCORE: $right_score \n";
        // print result;
        if($left_score == $right_score){
            echo "DRAW \n";
        }elseif($left_score < $right_score){
            echo "RIGHT PLAYER [$this->player2 ] WINS\n";
        }else{
            echo "LEFT PLAYER [ $this->player1 ] WINS\n";
        }
    }


    /**
     * 
     * @return string the information for players
     */
    function generateSendingString()
    {
        return json_encode($this->generateSendingJSON());
    }

    /**
     * 
     * @return the information for players
     */
    function generateSendingJSON()
    {
        $output = ['move_type' => "send_board", 'game_over' => ($this->gameOver ? "1" : "0"), 
            'board_length' => $this->boardLength, 'max_left' => $this->max_left, 'max_right' => $this->max_right,
            'left_board'=> json_encode($this->left_board)];
        return $output;
    }


    /**
     * Give player turn and the time he consumed, update the time of him.
     * 
     * @param $turn
     * @param $time
     */
    public function updateTime($player_num, $time)
    {
        $index = $player_num - 1;
        $player_name = ($player_num == 1) ? $this->player1 : $this->player2;
        $this->time_left[$index] -= $time;

        if ($this->time_left[$index] <= 0) {
            echo "[GAME OVER] Time limit Exceeded\n";
            if($player_num == 1){
                echo "WINNER IS RIGHT PLAYER [ $this->player2 ]\n";
            }else{
                echo "WINNER IS LEFT PLAYER [$this->player1]\n";
            }
            $this->gameOver = true;
        } else {
            echo "[PLAYER] " . $player_name . " has " . $this->time_left[$index] . " seconds left\n";
        }
    }

    function __construct($boardLength, $max_left, $max_right, $player1, $player2)
    {
        $this->gameOver = false;
        $this->boardLength = $boardLength;
        $this->player1 = $player1;
        $this->player2 = $player2;
        $this->max_left = $max_left;
        $this->max_right = $max_right;

        $this->left_board = array_fill(0, $boardLength/2, 0);
        $this->right_board = array_fill(0, $boardLength/2, 0);

        $this->time_left = array(120.0, 120.0);
    }
}
