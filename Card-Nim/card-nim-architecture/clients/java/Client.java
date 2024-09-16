import java.net.*;
import java.io.*;

public class Client {
    // Initialize socket and input output streams
    private Socket socket            = null;
    private BufferedReader input   	 = null;
    private PrintWriter out     	 = null;

    // Track game variables
    private int player_num;
    private int num_stones;
    private int num_cards;
    private int counter = 1;
  
    // Constructor to put ip address and port
    public Client(String address, int port) {
        // Establish a connection
        try {
            socket = new Socket(address, port);
            System.out.println("Connected");
  
            // Client takes input from socket
            input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
  
            // And also sends its output to the socket
            out = new PrintWriter(socket.getOutputStream(), true);
        } catch(UnknownHostException u) {
            System.out.println(u);
        } catch(IOException i) {
            System.out.println(i);
        }
    }

    public static void main(String args[]) throws IOException {
    	int portNumber;
    	if (args.length == 0) {
    		System.out.println("Connecting on default port 4000");
    		portNumber = 4000;
    	}
    	else {
    		portNumber = Integer.parseInt(args[0]);
    		System.out.println(String.format("Connecting on specified port %d", portNumber));
    	}
        Client client = new Client("127.0.0.1", portNumber);
        client.run();
    }

    public void run() throws IOException {
    	// Send our name to server
        out.println("Java Client");

        // Then wait for the ready messsage from the server once both clients are connected
        String readyMessage = input.readLine();
        
        player_num = Integer.parseInt(readyMessage.split(" ")[0]);
        num_stones = Integer.parseInt(readyMessage.split(" ")[1]);
        num_cards = Integer.parseInt(readyMessage.split(" ")[2]);

        System.out.println(String.format("Initial number of stones: %d", num_stones));
        System.out.println(String.format("Initial number of cards: %d", num_cards));

        while (num_stones > 0) {
        	int state = getstate();
        	int move = generatemove(state);

        	sendmove(move);

        	num_stones = state;

        	try {
			    Thread.sleep(100);
			}
			catch(InterruptedException ex) {
			    Thread.currentThread().interrupt();
			}
        }

    }

    public int getstate() throws IOException {
    	/*
		Query the server for the current state of the game and wait until a response is received
        before returning it as an integer
    	*/

    	// Send the getstate request to the server
    	out.println("getstate");

    	// Wait for the response
    	String state_info = input.readLine();

    	int state = Integer.parseInt(state_info);

    	return state;
    }

    public void sendmove(int move) throws IOException {
    	/*
		Send a move to the server to be executed. The server does not send a response / acknowledgement,
        so a call to getstate() afterwards is necessary in order to wait until the next move
    	*/

    	// Send a properly formatted sendmove request to server
    	out.println(String.format("sendmove %d", move));
    }

    public int generatemove(int state) throws IOException {
    	/*
		Given the state of the game as input, computes the desired move and returns it.
        
        TODO: modify this with your custom logic!
    	*/

    	// Currently just increments a counter an returns that move -- you should probably
    	// do something a bit more sophisticated!

    	int move = counter;
    	counter = counter + 1;

    	return move;
    }

}
