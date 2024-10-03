<?php
// ini_set('display_errors', 'On');
// ini_set('display_startup_errors', true);
// error_reporting(E_ALL);

include "GameController.php";
include "Board.php";
include "Draw.php";

// check command line arguments
if ($argc < 5 || !is_numeric($argv[1]) || !is_numeric($argv[2]) || 
    !is_numeric($argv[3]) || !is_numeric($argv[4])) {
    echo ("[ERROR] Please provide port number, length, max_left and maxright\n");
    echo ("[ERROR] Example command: php main.php 5000 15 6 7\n");
    exit(-1);
}

// start server
echo ("[SERVER] Starting server at localhost:$argv[1] with seesaw length: 
    $argv[2], max_left:$argv[3] and max_right:$argv[4]\n");

// for frontend
$slow = false;
$observed = false;

// game arguments
$board_length = (int)$argv[2];
$max_left = (int)$argv[3];
$max_right = (int)$argv[4];

foreach ($argv as $arg) {
    if ($arg == "-w") {
        $slow = true;
        echo "[SERVER] Slowing down game...\n";
    }
    if ($arg == "-o") {
        $observed = true;
        echo "[SERVER] Observing game...\n";
    }

}

$myController = new GameController("localhost", $argv[1]);
$myController->createConnection($board_length, $max_left, $max_right, $observed);


$myGame = new Board($board_length, $max_left, $max_right, $myController->player1, $myController->player2);

while (!$myGame->gameOver) {
    echo "----------------------------------------------------------------\n";

    $myGame->currentPlayer = 1;
    $sendingString = $myGame->generateSendingJSON();
    echo "[GAME] Stage: Sending data to player1 ... \n";
    $myController->send(1, $myGame->generateSendingString());

    echo "[GAME] Stage: Waiting board details from player1 ... \n";
    $time1 = microtime(true);
    $myGame->left_board = $myController->recvBoard(1);
    $time2 = microtime(true);
    $myGame->updateTime(1, $time2 - $time1);
    if($myGame->gameOver){
        break;
    }

    echo "[GAME] Stage: Sending data to player2 ... \n";
    $myGame->currentPlayer = 2;
    $myController->send(2, $myGame->generateSendingString());

    echo "[GAME] Stage: Waiting board details from player2 ... \n";
    $time1 = microtime(true);
    $myGame->right_board = $myController->recvBoard(2);
    $time2 = microtime(true);
    $myGame->updateTime(2, $time2 - $time1);

    if($myGame->gameOver){
        break;
    }

    $myGame->checkBoardValidity();
    if($myGame->gameOver){
        break;
    }

    print_r($myGame->left_board);
    print_r($myGame->right_board);

    $myGame->simulateGame();
    break;
}

// Game over, send final message to players
// $myController->send(1, $myGame->generateSendingString());
// $myController->send(2, $myGame->generateSendingString());
// draw($myGame, true, $moveString);
$myController->closeConnection();
