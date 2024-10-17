## Flaky Oracle Challenge: Architecture

Challenge date: 10/17/24\
Architecture Team: BFG(Paul Clarke and Shyam Iyer)

#### Client Protocol
This week's architecture requires you to write a TCP client to talk to an oracle server, oracle.py. \
Two example clients are provided in client.py and client.cpp. 

Protocol Overview:

	<--	"PLAY [TeamName]"
	--> "ACK"
	(game begins)
	<-- "BET" or "PASS"
	--> "HIT" or "MISS"
		...
	After 10000 rounds, the client is disconnected.

#### Using oracle.py
    python oracle.py [-d] [-p port] [-k keyfile]\
Options:\
	-d: print debug messages instead of the TUI\
	-p: select a port\
	-k: select a keyfile

Keyfiles:
	A keyfile specifies when the oracle goes into "flaky" mode, where the probability of hit
    is 0.7. 

On the day of the
competition, the keyfile will be unknown, but for testing you can provide one.\
They are four lines long, with each line containing a number representing
the start of a "flaky region." \
The numbers must be at least 500 apart from each
other and between 0 and 9500.

Example:

	300
	900
	2024
	9000

Good luck and have fun!
