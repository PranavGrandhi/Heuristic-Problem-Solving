#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

void send_move(int socket_id, bool move) {
	const char *msg = move ? "BET" : "PASS";
	send(socket_id, msg, strlen(msg)+1, 0);
}

bool recv_result(int socket_id) {
	char message[1024];
	read(socket_id, message, 4);
	if (strncmp(message, "HIT", 3)==0) {
		return true;
	} else {
		return false;
	}
}

int socket_connect(int port) {
	int socket_id = socket(AF_INET, SOCK_STREAM, 0);
	if (socket_id < 0) {
		printf("Error creating socket.\n");
		exit(1);
	}
	struct sockaddr_in server_address;
	server_address.sin_family = AF_INET;
	server_address.sin_port = htons(port);
	inet_pton(AF_INET, "127.0.0.1", &server_address.sin_addr);
	if (connect(socket_id, (struct sockaddr *)&server_address, sizeof(server_address)) < 0) {
		printf("Connection failed\n");
		exit(-1);
	}
	return socket_id;
}

bool strategy() {
	// FIXME
	return true
}

int main(int argc, char *argv[]) {
	// port is an optional command line argument
	int socket_id = socket_connect(argc == 2 ? atoi(argv[1]) : 5555);

	// Your team name here
	const char *start_message = "PLAY C++ Client";
	send(socket_id, start_message, strlen(start_message)+1, 0);
	char ack[4];
	read(socket_id, ack, 4);

	int i = 0;
	while (i < 10000) {
		send_move(socket_id, strategy());
		recv_result(socket_id);
		i++;
	}

	return 0;
}
