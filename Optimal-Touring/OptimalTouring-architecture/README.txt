The file of sites' data should be named as “sites.txt”. Do not change OptimalTouring.py or helper.py. If you find any bugs, you could contact me with pvg2018@nyu.edu or vb1467@nyu.edu

If you want to play it by hand, just run OptimalTouring.py and follow the instructions

If you want to play it by program, you should follow example.py to build your program.
	1. You must import OptimalTouring
	2. You must create an OptimalTouring object
	3. sendMove(siteId=i) means you move to site i
		3.1. The move will only be free at 0:00 of each day
	4. sendMove(delayTime=x) means you stay/visit the current site for x minutes
	5. settlement() will terminate this game and print out the result
	6. getRevenue(), getSites(), getTime(), getLocation(), getDay(), getState() will give you the information
	7. After the game is done, you can call printPath() which will print the reward and the path

If you don't want to use python:
	1. Your program should be able to read the site by yourself.
	2. Your program should output a file like "myCode.txt" which contains all your moves and delay time.
	3. Enter the number of time you want to delay or the siteId you want to move in the line before "move" or "delay" command.
		3.1. For any detailed information, please read the annotation in helper.py.
	4. You can run helper.py to test if your output can be run properly.