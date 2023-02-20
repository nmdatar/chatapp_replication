# Chat App

In this project, we implement a chat app with two different implementation. One using the gRPC framework, the other using Python's socket library.

## Part II: gRPC

### Protocol Buffers

The .proto file is where we defined our service by providing the methods that we want our service to provide. In our .proto file, we various methods (corresponding to functions required for the assignment) and set parameters for each method. For methods such as `login` and `logout` which only require a singular request and response, we set it as unary. For methods requiring multiple requests and/or responses from client/server, we set a streaming method. For example `list_accounts` requires the server to list a stream of accounts, we set it to be a server-side streaming method.

### Sever

The server.py program creates a gRPC server and listens for requests from the client to respond with the according method defined in the .proto file. The server.py program also implements the service defined in the .proto file to send back appropriate responses.

### Client

The client.py program creates a gRPC channel that connects to the server on a particular port and creates a stub, which gives us the ability to make RPC calls to the server, for the service/method it wants to call (as we defined in the .proto file). The user enters information in the commandline, which instructs the client.py program to make certain requests to the gRPC server, receive responses, and display those responses.

### Create Account, Login, Logout

Since the `CreateAccount` and `Login` function have overlapping abilities, I combined the two functions into one, the `Login` function. In the server, I created a dictionary called `usernames` on the server's RAM to store every user and their connectivity. The `Login` function checks if the user is registered, if not, it creates a new user and logs them in. Otherwise, it simply logs them in. The `Logout` receives the client currently logged in and disconnects them from the server and sets their connectivity in the `usernames` dictionary.

### List Accounts

Returns list of all usernames that match provided search term, otherwise returns all usernames in the dictionary

### Send Messages, Deliver Messages

I created a `ChatStream` in server.py which provides a bidirectional streaming RPC method between the server and client ( when client creates a thread for message streaming, this function is always called, or the server is always listening to client's requests). The function is constantly running to 1) identify if `self.retry_flag == username`, which indicates that there are queued messages to be sent (Deliver Message) or 2) if the dictionary stored new messages. In both cases, it sends messages the client by yielding a chatapp.Message object

With `ChatStream` running in the back, `SendMessage` stores message in `self.messages` if recipient is logged in (which `ChatStream` sends to recipient as we explained above), if not logged in, stores the message in the queued_messages list. `Retry` delivers the queued_message when the recipient is logged in.

### Delete Account

You delete the account if you are logged in. After you delete the account, all your messages and queued_messages (unsent messages) are deleted as well.

## Get Started

First, make sure you installed Pipenv, a virtual enviroment manager.

Install all dependencies via `pipenv install`

Enter the virtual enviroment via `pipenv shell`

Depending on the project, refer to either 'gRPC' or 'WebSocket'

### gRPC

Run Server `python3 chatapp_grpc/server.py`

Run Client `python3 chatapp_grpc/client.py`

### WebSocket

Run Server `python3 chatapp_websocket/server.py`

Run Client `python3 chatapp_websocket/client.py`
