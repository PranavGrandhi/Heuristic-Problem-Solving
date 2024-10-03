
/**
 * A socket based client for the ``hps.servers.SocketServer`` class
 * Game: No Tipping
 * https://cs.nyu.edu/courses/fall21/CSCI-GA.2965-001/notipping.html
 */

import java.awt.*;
import java.io.*;
import java.net.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
// for json
import com.alibaba.fastjson.JSONObject;

public class Client {
    /**
     * A client class for ``hps.servers.SocketServer``
     *
     */
    public String host;
    public int port;
    public Socket socket;

    private BufferedReader input = null;
    private PrintWriter output = null;

    private int board_length;
    private int max_left;
    private int max_right;

    // ! TODO: Please change this to your team name
    public String name = "Java Client";
    public boolean isFirst = false;

    public Client(String host, int port, boolean first) throws IOException {
        /**
         * @param host: The hostname of the server
         * @param port: The port of the server
         */
        this.host = host;
        this.port = port;
        this.isFirst = first;

        System.out.println("[INFO] Crating connection to server ...");
        System.out.println("       Client Name: " + name);

        try {
            socket = new Socket(host, port);

            // Client takes input from socket
            input = new BufferedReader(new InputStreamReader(socket.getInputStream()));

            // And also sends its output to the socket
            output = new PrintWriter(socket.getOutputStream(), true);

            // socket.connect(new InetSocketAddress(host, port), 1000);

        } catch (IOException e) {
            System.out.println("[ERROR] Could not connect to server");
            System.out.println("[ERROR] " + e.getMessage());
            System.exit(1);
        }

    }

    public ArrayList<Integer> string_to_vector(String str){
        str = str.replace("[", "").replace("]", "").trim();

        String[] stringArray = str.split(",\\s*");
        ArrayList<Integer> integerList = new ArrayList<>();
        for (String s : stringArray) {
            integerList.add(Integer.parseInt(s));
        }

        return integerList;
    }

    public String vector_to_string(ArrayList<Integer> vec){
        StringBuilder result = new StringBuilder();
        result.append("[");

        // Loop through the ArrayList and append each element
        for (int i = 0; i < vec.size(); i++) {
            result.append(vec.get(i));
            if (i < vec.size() - 1) {
                result.append(", ");
            }
        }

        result.append("]");

        // Convert StringBuilder to string
        String formattedString = result.toString();
        return formattedString;
    }

    public void play_game() throws IOException {

        System.out.println("[INFO] Connected to server");
        System.out.println("[INFO] Sending greeting to server ...");

        // Send greeting json to server, name and is_first
        JSONObject greeting = new JSONObject();
        greeting.put("name", name);
        greeting.put("is_first", isFirst);

        this.send_data(greeting.toJSONString());

        // get initial game state from server
        String initialGameState = this.receive_data();
        System.out.println("[INFO] Received initial game state from server");
        System.out.println("[INFO] Parsing game state ...");

        // store game state from json, num_weights and board_length
        JSONObject initial_info = JSONObject.parseObject(initialGameState);

        System.out.println("[INFO] Starting game ...");
        JSONObject response = new JSONObject();

        System.out.println("[INFO] Received message:");
        String res = this.receive_data();

        response = JSONObject.parseObject(res);

        if (response.containsKey("game_over") && response.getBoolean("game_over")) {
            System.out.println("[GAME] Game over!");
            System.exit(0);
        }
        this.board_length = response.getInteger("board_length");
        this.max_left = response.getInteger("max_left");
        this.max_right = response.getInteger("max_right");
        
        ArrayList<Integer> other_board = new ArrayList<Integer>();
        if(this.isFirst == false){
            String left_board_string = response.getString("left_board");
            other_board = this.string_to_vector(left_board_string);
        }

        ArrayList<Integer> board = this.place(other_board);
        String sboard = vector_to_string(board);

        JSONObject j = new JSONObject();
        j.put("board", sboard);
        this.send_data(j.toJSONString());

    }

    // ! TODO: implement this method
    public ArrayList<Integer> place(ArrayList<Integer> other_board) {
        int length = this.board_length / 2;
        ArrayList<Integer> answer = new ArrayList<>(Collections.nCopies(length, 0));
        if(this.isFirst){
            answer.set(0, 1);
        }
        else{
            answer.set(length - 1, 1);
        }
        return answer;
    }

    public void send_data(String data) throws IOException {
        /**
         * Send data to the server
         *
         * @param data: The data to send to the server.
         */
        System.out.println("[INFO] Sending data to server ...");
        System.out.println("       " + data);
        output.println(data);
    }

    public String receive_data() throws IOException {
        /**
         * Receive data from the server
         *
         * @return The data received as a String from server.
         */

        String str = input.readLine();
        System.out.println("[INFO] Received data from server ...");
        System.out.println("       " + str);
        return str;
    }

    public void close_socket() throws IOException {
        /**
         * Close the connection
         */
        socket.close();
    }

    public static void main(String[] args) throws IOException {
        /**
         * @param args: The hostname and port of the server
         */

        int PORT = 5000;
        String HOST = "127.0.0.1";
        boolean FIRST = false;

        if (args.length == 0) {
            System.out.println("[INFO] Using default ip: localhost, port: 5000");
        } else {
            HOST = args[0];
            PORT = Integer.parseInt(args[1]);
            FIRST = Boolean.parseBoolean(args[2]);
            System.out.println("[INFO] Using ip: " + HOST + ", port: " + PORT);
        }

        Client client = new Client(HOST, PORT, FIRST);
        client.play_game();
    }
}
