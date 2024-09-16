<?php
	// check command line arguments
	if ($argc < 4 || !is_numeric($argv[1]) || !is_numeric($argv[2]) || !is_numeric($argv[3])) {
		echo("[ERROR] Please provide port number, number of stones, number of cards\n");
		echo("[ERROR] Example command: php server.php 4000 30\n");
		exit(-1);
	}

	// start server
	echo("[LOG] Starting server at localhost:$argv[1] with $argv[2] stones and $argv[3] cards\n");

	// open, bind, and begin listening on socket
	$socket = socket_create(AF_INET, SOCK_STREAM, 0); // Address Family IPv4, TCP, system chooses protocol
	socket_bind($socket, 'localhost', $argv[1]); // bind to localhost on port $argv[1]
	socket_listen($socket, 3); // allow 3 connections to queue

	$connections;
	$observed = false;
	if ($argc == 5 && $argv[4] == "-o") {
		// log status
		echo("[LOG] Waiting for Observer\n");

		// blocking call waiting for connection
		$connections[0] = socket_accept($socket);

		// extra communication to identify client (see comment below for more details on websocket exchange)
		$identification = socket_read($connections[0], 4096); // number of bytes to read
		if (strpos($identification, "Sec-WebSocket-Key:") !== false) {
			preg_match('#Sec-WebSocket-Key: (.*)\r\n#', $identification, $matches);
			$key = base64_encode(pack('H*', sha1($matches[1] . '258EAFA5-E914-47DA-95CA-C5AB0DC85B11')));
			$headers = "HTTP/1.1 101 Switching Protocols\r\n";
			$headers .= "Upgrade: websocket\r\n";
			$headers .= "Connection: Upgrade\r\n";
			$headers .= "Sec-WebSocket-Version: 13\r\n";
			$headers .= "Sec-WebSocket-Accept: $key\r\n\r\n";
			socket_write($connections[0], $headers, strlen($headers));
			$observed = true;
		}
	}

	// wait for two connections to continue
	$is_websocket;
	$name;
	for ($i = 1; $i <= 2; $i++) {
		// log status
		echo("[LOG] Waiting for Player $i\n");

		// blocking call waiting for connection
		$connections[$i] = socket_accept($socket);

		// do extra communication to identify client
		// if a websocket is being used we need to do a handshake
		// all other clients can send whatever they want as long as it doesn't contain "Sec-WebSocket-Key:"
		// identification code based on https://medium.com/@cn007b/super-simple-php-websocket-example-ea2cd5893575
		$identification = socket_read($connections[$i], 4000);
		if (strpos($identification, "Sec-WebSocket-Key:") !== false) {
			preg_match('#Sec-WebSocket-Key: (.*)\r\n#', $identification, $matches);
			$key = base64_encode(pack('H*', sha1($matches[1] . '258EAFA5-E914-47DA-95CA-C5AB0DC85B11')));
			$headers = "HTTP/1.1 101 Switching Protocols\r\n";
			$headers .= "Upgrade: websocket\r\n";
			$headers .= "Connection: Upgrade\r\n";
			$headers .= "Sec-WebSocket-Version: 13\r\n";
			$headers .= "Sec-WebSocket-Accept: $key\r\n\r\n";
			socket_write($connections[$i], $headers, strlen($headers));
			$is_websocket[$i] = true;
			$name[$i] = "Webclient-$i";

			// log connection
			echo("[LOG] Player $i connected via websocket\n\n");
		} else {
			$is_websocket[$i] = false;
			$name[$i] = str_replace(array(" ", "\r", "\n"), '', $identification);

			// log connection
			echo("[LOG] Player $i connected via TCP\n\n");
		}
	}

	// send a message to a client over a socket or websocket
	function send_message($client, $message, $is_web) {
		if ($is_web) {
			socket_write($client, chr(129) . chr(strlen($message)) . $message);
		} else {
			socket_send($client, $message, strlen($message), 0);
		}
	}

	// compliant masking and decoding based on https://gist.github.com/dg/6205452
	function web_decode($frame) {
		$decoded_frame = "";
		for ($i = 6; $i < strlen($frame); $i++) {
			$decoded_frame .= $frame[$i] ^ $frame[2 + ($i - 2) % 4];
		}
		return $decoded_frame;
	}

	// initialize game
	$num_stones = $argv[2];
	$num_cards = $argv[3];
	$cards[1] = array_fill(1, $num_cards, true);
	$cards[2] = array_fill(1, $num_cards, true);
	$current_player = 1;

	// send initial data to both players
	send_message($connections[1], "1 $num_stones $num_cards\n", $is_websocket[1]);
	send_message($connections[2], "2 $num_stones $num_cards\n", $is_websocket[2]);

	// send initial data to observer
	if ($observed) {
		send_message($connections[0], "$name[1] $name[2] $num_stones $num_cards\n", true);
	}

	// both players now have 2 minutes each remaining (120 seconds)
	$time_remaining[1] = 120 * 1000000000;
	$time_remaining[2] = 120 * 1000000000;
	$time_start = hrtime(true);

	// play game
	while ($num_stones > 0) {
		// print status
		echo("[LOG] Waiting for Player $current_player to send a command\n");
		$print_time = $time_remaining[$current_player] / 1000000000.0;
		echo("[INFO] $print_time seconds remaining\n\n");

		// blocking operation waiting for command
		// set a timeout on this operation
		// we will be nice here and round up to account for latency.
		// Ex. if a player has 73.4 seconds remaining, we will give them 74
		socket_set_option($connections[$current_player], SOL_SOCKET, SO_RCVTIMEO,
			array('sec' => intval($time_remaining[$current_player] / 1000000000), 'usec'=> 0));
		$command = socket_read($connections[$current_player], 1024);

		// in the event of a timeout, forcefully end the game
		// this is done by sending 0 to the current player, -1 to the other player, closing the socket, and exiting
		if (!$command) {
			// send messages to players and close socket
			send_message($connections[$current_player], "0\n", $is_websocket[$current_player]);
			$current_player = ($current_player == 2 ? 1 : 2);
			send_message($connections[$current_player], "-1\n", $is_websocket[$current_player]);

			// send update to observer
			if ($observed) {
				send_message($connections[0], "$num_stones 0\n", true);
			}

			socket_close($socket);

			// log results
			echo("[LOG] TIMEOUT\n");
			echo("[INFO] PLAYER $current_player WINS!\n\n");

			// exit program
			exit;
		}

		// if coming from a websocket, decode recieved packet
		if ($is_websocket[$current_player]) {
			$command = web_decode($command);
		}

		// split and interpret command
		$command = str_replace(array("\r", "\n"), '', $command);
		$command_parts = explode(" ", $command);

		// perform actions based on command and log results
		if ($command_parts[0] == "getstate") {
			// send message
			send_message($connections[$current_player], "$num_stones\n", $is_websocket[$current_player]);
			
			// log results
			echo("[LOG] -- SENDING STATE --\n");
			echo("[INFO] Stones Remaining: $num_stones\n");
			echo("[INFO] Current Player: $current_player\n");
			echo("[INFO] Player's hand:");
			for($i = 1; $i <= $num_cards; $i++) {
				if ($cards[$current_player][$i]) {echo(" $i");}
			}
			echo("\n");
			echo("[INFO] Move time remaining: $time_remaining[$current_player] microseconds\n\n");
		} else if ($command_parts[0] == "sendmove" && $cards[$current_player][$command_parts[1]]) {
			// apply timer
			$time_remaining[$current_player] -= hrtime(true) - $time_start;

			// apply move
			$num_stones -= $command_parts[1];
			$cards[$current_player][$command_parts[1]] = false;

			// log results
			echo("[LOG] -- APPLYING MOVE --\n");
			echo("[INFO] Player $current_player takes $command_parts[1] stones\n");
			echo("[INFO] Remaining stones: $num_stones\n\n");

			// send update to observer
			if ($observed) {
				send_message($connections[0], "$num_stones $time_remaining[$current_player]\n", true);
			}

			// Alternate players and display the message if the game isn't over
			$current_player = ($current_player == 2 ? 1 : 2);
			if ($num_stones > 0) {
				echo("[INFO] ===[PLAYER $current_player's TURN]===\n");
			}

			// start timer for next player
			$time_start = hrtime(true);
		} else {
			// log command
			echo("[LOG] Invalid command: \"$command\"\n\n");
		}
		// update player time remaining
		$time_remaining[$current_player] -= hrtime(true) - $time_start;
		$time_start = hrtime(true);
	}

	// send both players either 0 or negative number of stones left
	// useful for graceful quitting
	send_message($connections[1], "$num_stones\n", $is_websocket[1]);
	send_message($connections[2], "$num_stones\n", $is_websocket[2]);

	// print result
	if ($num_stones == 0) {
		$current_player = ($current_player == 2 ? 1 : 2);
		echo("[INFO] PLAYER $current_player WINS!\n\n");
	} else {
		echo("[INFO] PLAYER $current_player WINS!\n\n");
	}

	// close socket
	socket_close($socket);
?>