# Python Client

## requirement

Install `hps-nyu` to use the SocketClient.
```
pip install --user hps-nyu
```

## about the place function
The function to be concerned with
```python
def place(self, other_board):
    ...
```

You can access the needed data via
```python
self.board_length 
self.max_left
self.max_right
```

## args
- `--first`: Indicates whether client should go first

- `--ip`: server ip to connect to, default 'localhost'

- `--port`: server port to connect to, default `5000`

- `--name`: name of the client, change the default to your team name on line `82`

## sample command
```bash
# for left player
python3 client.py --first --port 5000
# for right player
python3 client.py --port 5000
```