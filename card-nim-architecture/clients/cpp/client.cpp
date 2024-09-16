
#include <iostream>
#include <string>
#include <sstream>

// these includes may need to be modified depending on your system
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

// change this to whatever you want
std::string bot_name = "C++ Client";

// here you can define custom solver logic
// for example: you could gut this struct and add arrays of cards, custom algorithms, and more
// this is consulted by primary loop in play_game
struct Bot {
	int last_card, max_card;
	Bot(int player_num, int num_stones, int num_cards) {
		last_card = 0;
		max_card = num_cards;
	}
	int calculate_move(int num_stones) {
		return ++last_card;
	}
};

// Everything below here is game logic and socket handling

int socket_id;
struct sockaddr_in server_address;

int get_state() {
	// send getstate request
	send(socket_id, "getstate", 8, 0);

	// read response
	char message[1024];
	read(socket_id, message, 1024);
	return std::stoi(message);
}

void send_move(int move) {
	std::string s = "sendmove " + std::to_string(move);
	send(socket_id, s.c_str(), s.length(), 0);
}

// this function contains the main game loop
void play_game() {
	int player_num, num_stones, num_cards;

	// read initial data
	char message[1024];
	read(socket_id, message, 1024);
	std::stringstream ss(message);
	ss >> player_num >> num_stones >> num_cards;

	// create bot
	Bot b(player_num, num_stones, num_cards);

	// the first player can make a move without getting state first
	// the second needs to make an initial request
	if (player_num == 2) {
		num_stones = get_state();
	}

	// game loop (getstate, sendmove, check if game over, repeat)
	while (num_stones > 0) {
		send_move(b.calculate_move(num_stones));
		usleep(1000);
		num_stones = get_state();
	}
}

// this function handles the socket connection process
void socket_connect(int port) {
	// create socket
	socket_id = socket(AF_INET, SOCK_STREAM, 0);
	if (socket_id < 0) {
		std::cout << "Error creating socket\n";
		exit(-1);
	}
	// set additional required connection info
	server_address.sin_family = AF_INET;
	server_address.sin_port = htons(port);
	// convert ip address to correct form
	inet_pton(AF_INET, "localhost", &server_address.sin_addr);
	// attempt connection
	if (connect(socket_id, (struct sockaddr *)&server_address, sizeof(server_address)) < 0) {
		std::cout << "Connection failed\n";
		exit(-1);
	}
	// send greeting
	send(socket_id, bot_name.c_str(), bot_name.length(), 0);
}

int main(int argc, char *argv[]) {
	// port is an optional command line argument
	socket_connect(argc == 2 ? std::stoi(argv[1]) : 4000);

	// main game loop
	play_game();
	return 0;
}
