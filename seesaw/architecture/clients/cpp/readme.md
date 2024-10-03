# C++ Client

## requirement

Place `json.hpp` in the same directory as `client.cpp`


## args

- `-f`: Indicates whether client should go first

- `-h HOST`: server ip to connect to, default 'localhost'

- `-p PORT`: server port to connect to, default `5000`


## Details of the place function
Operate on the following function
```cpp
vector<int> Client::place(vector<int> &other_board){
    ...
}
```

You can access the details of the length, max_left, max_right, via
```cpp
this->board_length;
this->max_left;
this->max_right;
```


## Sample command
```bash
g++ client.cpp -o client
# for left player
./client -p 5000 -f 
# for right player
./client -p 5000 
```