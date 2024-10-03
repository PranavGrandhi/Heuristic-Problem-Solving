#include <cstring>
#include <stdio.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string>

#include <iostream>
#include <string>
#include <sstream>

// these includes may need to be modified depending on your system
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <getopt.h>

// json library for modern cpp
#include "json.hpp"

using namespace std;
using json = nlohmann::json;

int buffer_size = 4096;

/*
 * A socket based client for the ``hps.servers.SocketServer`` class
 * Game: No Tipping. https://cs.nyu.edu/courses/fall21/CSCI-GA.2965-001/notipping.html
 */
class Client
{
public:
    string ip_address;
    int port;
    int client_sock;
    string name;

    // Game information
    int board_length;
    int max_left;
    int max_right;

    ~Client();
    Client(string, int, bool);
    void close_socket();
    void send_data(string);
    string receive_data(int);
    string receive_large(int, int);


    // variables
    bool is_first = false;

    //Game functions
    string vector_to_string(vector<int> &vec);
    vector<int> string_to_vector(string &data);
    vector<int> place(vector<int> &other_board);
    void play_game();

    // pair<int, int> place(vector<int>);
    // int remove(vector<int>);
    bool isGameOver(vector<int>);
};

/*
 *  Client Constructor
 *  Arguments:
 *  string ip_address:
 *      the host name of the server
 *  int port:
 *      the port of the server
 */
Client::Client(string ip_address, int port, bool is_first)
{
    this->ip_address = ip_address;
    this->port = port;
    this->is_first = is_first;

    // ! TODO: Please change this to your team name
    this->name = "Client C++";

    cout << "[INFO] Crating connection to server ..." << endl;
    cout << "       Client Name: " << this->name << endl;

    struct sockaddr_in address;
    int sock = 0;
    struct sockaddr_in serv_addr;

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        cout << "[ERROR] Error creating socket\n";
        exit(-1);
    }

    // memset(&serv_addr, '0', sizeof(serv_addr));

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    if (inet_pton(AF_INET, ip_address.c_str(), &serv_addr.sin_addr) < 0)
    {
        cout << "\n[ERROR] Invalid address/ Address not supported \n";
        exit(-1);
    }

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    {
        cout << "\n[ERROR] Connection failed\n";
        exit(-1);
    }

    cout << "[INFO] Socket connected ..." << endl;

    this->client_sock = sock;

    // send name to server
    json greeting = {
        {"name", this->name},
        {"is_first", is_first},
        // {"board", "[1, 2, 3, 4, 5]"},
    };
    cout << "[INFO] Sending greeting to server ..." << endl;
    this->send_data(greeting.dump());

    // receive initial data from server
    cout << "[INFO] Receiving initial data from server ..." << endl;
    json response = json::parse(this->receive_data(buffer_size));
    cout << "       " << response.dump(2) << endl;
    // this->board_length = response["board_length"];
    // this->max_left = response["max_left"];
    // this->max_right = response["max_right"];
}

std::string Client::vector_to_string(std::vector<int>& vec) {
    std::stringstream ss;
    ss << "[";  // Start with opening bracket
    
    for (size_t i = 0; i < vec.size(); ++i) {
        ss << vec[i];  // Add the vector element
        if (i != vec.size() - 1) {
            ss << ", ";  // Add a comma and space between elements, but not after the last one
        }
    }
    
    ss << "]";  // End with closing bracket
    return ss.str();  // Convert the stream to a string and return
}

std::vector<int> Client::string_to_vector(std::string& str) {
    std::vector<int> vec;
    std::string cleanedStr = str.substr(1, str.size() - 2); // Remove brackets
    std::stringstream ss(cleanedStr);
    std::string item;

    while (std::getline(ss, item, ',')) { // Split by comma
        vec.push_back(std::stoi(item)); // Convert to int and add to vector
    }

    return vec;
}

// * Game logics
void Client::play_game()
{
    cout << "[INFO] Starting game ..." << endl;
    json response;

    string res = this->receive_data(buffer_size);

    response = json::parse(res);
    if (response.find("game_over") != response.end() && response["game_over"] == "1")
    {
        cout << "[GAME] Game over!" << endl;
        exit(0);
    }
    
    this->board_length = response["board_length"];
    this->max_left = response["max_left"];
    this->max_right = response["max_right"];

    vector<int> other_board;
    if(is_first == false){
        std::string left_board_string = response["left_board"];
        other_board = string_to_vector(left_board_string);
    }

    vector<int> board = place(other_board);
    std::string sboard = vector_to_string(board);

    // sent it to server
    json j;
    j["board"] = sboard; 

    this->send_data(j.dump());
}


// The functions handled by user
vector<int> Client::place(vector<int> &other_board){
    int n = this->board_length/2;
    vector<int> solution(n, 0);
    if(is_first){
        solution[0] = 1;
        return solution;
    }
    solution[n-1] = 1;
    return solution; 
}


// * Below are socket handling functions
/*
 *  Client Connect to Server
 *  Arguments:
 *      string data:
 *          the string of data to send
 */
void Client::send_data(string data)
{
    cout << "[INFO] Sending data to server ..." << endl;
    cout << "       " << data << endl;
    send(client_sock, data.c_str(), strlen(data.c_str()), 0);
}

/*
 *  Client Close Connection
 */
void Client::close_socket()
{
    cout << "[INFO] Closing connection ..." << endl;
    close(client_sock);
}

/*
 *  Client Receive Data
 *  Args:
 *      int buffer_size:
 *          the size of the buffer of data to receive
 *  Return:
 *      the string of data sent by server
 */
string Client::receive_data(int buffer_size)
{
    char *buffer = (char *)malloc(sizeof(*buffer) * buffer_size);
    memset(buffer, 0, buffer_size);
    string data;
    int valread = read(client_sock, buffer, buffer_size);
    if (valread >= 1)
    {
        data.append(buffer);
    }
    free(buffer);

    cout << "[INFO] Received data from server ..." << endl;
    cout << "       " << data << endl;

    return data;
}

/*
 *  Client Receive Large Chunk of Data
 *  Arguments:
 *      int buffer_size:
 *          the size of the buffer of data to receive
 *      int timeout:
 *          This method fetches chunks of data from the server until socket
 *          times out.
 *  Return:
 *      the string of data sent by server
 */
string Client::receive_large(int buffer_size, int timeout)
{
    string data;
    struct timeval tv;
    tv.tv_sec = timeout;
    tv.tv_usec = 0;
    setsockopt(client_sock, SOL_SOCKET, SO_RCVTIMEO, (const char *)&tv, sizeof(struct timeval));
    fd_set fdset;
    FD_ZERO(&fdset);
    FD_SET(client_sock, &fdset);

    while (true)
    {
        if (select(client_sock + 1, &fdset, NULL, NULL, &tv) == 0)
        {
            break;
        }
        data.append(receive_data(buffer_size));
    }
    tv.tv_sec = 0;
    tv.tv_usec = 0;
    setsockopt(client_sock, SOL_SOCKET, SO_RCVTIMEO, (const char *)&tv, sizeof(struct timeval));
    return data;
}

/*
 *  Client Destructor
 */
Client::~Client()
{
    close(client_sock);
}

int main(int argc, char *argv[])
{

    string HOST = "127.0.0.1";
    int PORT = 5000;
    bool FIRST = false;

    int c;
    static struct option long_options[] = {
        {"host", optional_argument, 0, 'h'},
        {"port", optional_argument, 0, 'p'},
        {"first", no_argument, 0, 'f'},
        {0, 0, 0, 0}};
    while (true)
    {
        int option_index = 0;
        c = getopt_long(argc, argv, "h:p:f",
                        long_options, &option_index);
        if (c == -1)
            break;
        switch (c)
        {
        case 'p':
            // printf("option -p with value `%s', `%d'\n", optarg, optarg);
            PORT = atoi(optarg);
            break;
        case 'h':
            // printf("option -h with value `%s, `%d''\n", optarg, optarg);
            HOST = optarg;
            break;
        case 'f':
            // printf("option -f\n");
            FIRST = true;
            break;
        case '?':
            break;
        default:
            printf("?? getopt returned character code 0%o ??\n", c);
        }
    }

    // creat a client object, connects to server and send initial message
    // ! TODO: Please change the client name in the constructor
    Client client(HOST, PORT, FIRST);
    client.play_game();
}