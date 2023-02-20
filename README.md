# Chat App

Documentation for Design Project 1

Part A: Server Side

The server side sets up the clients to engage in a chat application with the following functionalities (which will be elaborated on further on). 

First, we have to set up the client request to be received by the server in the first place. This function, titled handle_client has two arguments (clientsocket, addr) which are the client socket name and client address respectively. We have two dictionaries set up for this. The dictionary enables the access of other account information that includes passwords, their online status, as well as their received messages. We use another dictionary entitled socket_to_user that maps a socket address to the given account name. The data will be received using the clientsocket.recv(1024) function which updates the accounts and socket_to_user dictionaries accordingly and closes if data is not present. 1024 will be the maximum amount of data (in bytes) that can be received at a time and therefore will have a buffer size of 1024 bytes 

Now, we will go into each of the action-oriented functions that we have created. 

Create: creates a new account with a provided username and password if the username doesn’t exist, otherwise returns error message
List: returns list of all usernames that match provided search term, otherwise returns all usernames in the dictionary 
Login: logs in the user with provided username and password if username exists, not logged in, and has the correct username password match. After logged in, it checks for undelivered messages, and if there are any, delivers them to user, otherwise returns error  
Send: sends message from sender to recipient if recipient exists and logged in, if not logged in, stores the message in the received_message list, otherwise returns error
Deliver: delivers any undelivered messages with the provided username and password if they exist and are logged in, otherwise returns error
Delete: deletes the account with the provided username and password if it exists and is not currently logged in by another client. if the account has undelivered messages, the function delivers them to the user, otherwise, it returns an error message. We have done this outside the login side so that undelivered messages are still accounted for on both sides despite the user not existing anymore (i.e. if the sender’s account got deleted as well as the receiver’s one). Although if the sender’s account got deleted and the messages are queued to send (which it will still do), structuring it this way also ensures that if the receiver’s account gets deleted, the messages in the queue will still send. 

If none of the above functions are recognized, then an error message will show saying that the request was not found. 

To tie things up, the overall script has been set up using TCP sockets for communication and a dictionary to store account names. It listens for a specific port that we have specified to look out for incoming connections from clients (which will be elaborated in the following section). Each new TCP socket will be created using the socket.socket() function, selectors.DefaultSelector to monitor new connections, and threading.Thread to handle simultaneous requests through multithreading to allow the requests to take place in a separate thread. This was done to enable the efficient processing and capabilities of many different clients. 

Part B: Client Side

On the client side, the user is allowed to send request to the server using commands in the following: 

Linking to the server involves the client socket object creation using socket.socket() with parameters AF_INET and SOCK_STREAM that specifies the address family of the socket as IPv4 and the TCP type respectively. We then connect to the server using the IP address and the port number specified on the server end using clientsocket.connect() with the aforementioned as the parameters. Here, the user will be prompted with a message to enter a command using a standard print() statement.

Firstly, our program has the select module that monitors the client socket and the standard input stream for incoming data. It checks if it comes from the server or the user (using select.select()) to decide what to do. If the message is from the server, the message will be decoded and printed using the print() statement. If from the user, we will proceed with the following:

The cmap dictionary maps user command strings to integers that are sent to the server. This is done to simplify the message protocol and reduce the amount of data that needs to be transmitted. The code also includes some special handling for the "login", "delete", and "deliver" commands. When any of these commands are entered by the user, the code waits for the server to send a response with a specific ending sequence of characters ("\r\n\r\n"). This is done to ensure that all messages have been delivered before continuing with the next command. 

Finally to tidy everything up, the command will be sent to the server using clientsocket.send(), display undelivered messages from the buffer to the user if command = login, deliver, or delete, and if not those three, the response is received and displayed using clientsocket.recv(). 

To recap the usability side of things that the user will input to the client, we will use the following format to send the aforementioned commands: 
-	Create username password
-	Delete username password
-	Deliver username message 


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
