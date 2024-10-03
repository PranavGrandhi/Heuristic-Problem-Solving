# Java Client

## requirement

Place `fastjson-1.2.78.jar` in the same directory as `Client.java`.


## args

Include all args or none.

- `<host>` : host to connect to, default 'localhost'

- `<port>` : port to connect to, default `5000`

- `<bool:first>` : indicates whether client should go first

## details about place function
The function you need to operate on:
```java
    public ArrayList<Integer> place(ArrayList<Integer> other_board) {
        ...
    }
```
You can access the details of the length, max_left, max_right, via
```java
this.board_length;
this.max_left;
this.max_right;
```

## Sample command
```bash
javac -cp fastjson-1.2.78.jar Client.java
# for the left player
java -cp fastjson-1.2.78.jar:. Client localhost 5000 true
# for the right player
java -cp fastjson-1.2.78.jar:. Client localhost 5000 false
```


## script
- compile : `javac -cp fastjson-1.2.78.jar Client.java`

Please add the arguments accordingly in the run.sh before running.
- run: `java -cp fastjson-1.2.78.jar:. Client`