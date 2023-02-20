import sys
import socket
import signal
import threading

# create dictionary for account information storage
accounts = {}

# dictionary to map connected addresses to usernames
socket_to_user = {}

# active sockets
active_sockets = []

# current version command map
cmap = {
    "create" : 0,
    "ls" : 1,
    "login" : 2,
    "send" : 3,
    "delete" : 4,
    "deliver" : 5,
    "help" : 6,
}

# Define version of handling client commands
version = 1

def handle_client(clientsocket, addr):

    while True:

        try:
            request = clientsocket.recv(1024).decode()
        except OSError:
            break
        # Check if connection has ended/been closed
        if not request:
            if str(addr) in socket_to_user:
                accounts[socket_to_user[str(addr)]]["active"] = False
                accounts[socket_to_user[str(addr)]]["connection"] = None
                socket_to_user.pop(str(addr))
            print("Connection closed from client with address %s" % str(addr))
            active_sockets.remove(clientsocket)
            break

        request = request.split()

        # Check correct version in client code
        if (request[0] != str(version)):
            clientsocket.send("Incorrect client software version. Please use an updated version!".encode())
            break

        request.pop(0)

        # CREATE
        if request[0] == str(cmap['create']):
            
            create(clientsocket=clientsocket, request=request, addr=addr)

        # LIST 
        elif request[0] == str(cmap['ls']):
            ls(clientsocket=clientsocket, request=request)
        
        # LOGIN
        elif request[0] == str(cmap['login']):     
            login(clientsocket=clientsocket, request=request, addr=addr)

        # SEND
        elif request[0] == str(cmap['send']):
            send(clientsocket=clientsocket, request=request, addr=addr)

        # DELIVER
        elif request[0] == str(cmap['deliver']):
            deliver(clientsocket=clientsocket, request=request)
            
        # DELETE
        elif request[0] == str(cmap['delete']):
            delete(clientsocket=clientsocket, request=request, addr=addr)
            
        # HELP
        elif request[0] == str(cmap['help']):
            help(clientsocket=clientsocket)

        else:
            clientsocket.send("Invalid command\nValid commands: create list login send deliver delete help".encode())

def create(clientsocket, request, addr):

    # Make sure command is correct length
    if len(request) != 3:
        help(clientsocket=clientsocket)
        return -1

    username = request[1]
    password = request[2]

    if addr in socket_to_user:
        clientsocket.send("You are already logged into an account!".encode())

    elif username in accounts:
        clientsocket.send("Account with username already exists. Try again".encode())
    
    # If successful create and init a new account
    else:
        accounts[username] = {}
        accounts[username]["password"] = password
        accounts[username]["active"] = False
        accounts[username]["received_messages"] = []
        accounts[username]["connection"] = None
        clientsocket.send("Account successfully created".encode())

    return 0
            
def ls(clientsocket, request):

    if len(request) >= 3:
        help(clientsocket=clientsocket)
        return -1

    # check a list of accounts with wildcard if given
    if len(request) > 1:
        search_term = request[1]
        matching_accounts = [username for username in accounts if search_term in username]

    else:
        matching_accounts = list(accounts.keys())
    
    if matching_accounts:
        response = "\n".join(matching_accounts)
        clientsocket.send(response.encode())
    else:
        clientsocket.send("No matching accounts".encode())

    return 0

def login(clientsocket, request, addr):

    if len(request) != 3:
        help(clientsocket=clientsocket)
        clientsocket.send('\r\n\r\n'.encode())
        return -1
    
    username = request[1]
    password = request[2]

    # Check if logged in already
    if str(addr) in socket_to_user:
        clientsocket.send("You are already logged into an account!".encode())
        clientsocket.send("\r\n\r\n".encode())

    # Make sure correct account information is provided
    elif username in accounts and accounts[username]["password"] == password:
        accounts[username]["active"] = True
        accounts[username]["connection"] = clientsocket
        socket_to_user[str(addr)] = username
        clientsocket.send("Login successful\n".encode())

        # Deliver undelivered messages
        if len(accounts[username]["received_messages"]) >= 1:
            clientsocket.send("Account has undelivered messages: ".encode())
            deliver(clientsocket=clientsocket, request=request)
        
        else:
            clientsocket.send("\r\n\r\n".encode())

    else:
        clientsocket.send("Login unsuccessful".encode())
        clientsocket.send("\r\n\r\n".encode())

    return 0

def send(clientsocket, request, addr):
    if len(request) < 3:
        help(clientsocket=clientsocket)
        return -1

    # Check self socket status
    if (str(addr)) not in socket_to_user:
        clientsocket.send("Please login to send a message".encode())
    
    else:
        recipient = request[1]
        message = " ".join(request[2: ])

        #check user in sequence
        if recipient in accounts:
            # Check if logged in
            if accounts[recipient]['active'] == True:
                message_send = f"\nFrom {socket_to_user[str(addr)]}: Message: {message}"
                accounts[recipient]["connection"].send(message_send.encode())
                clientsocket.send("Message delivered!".encode())

            # Otherwise queue the message
            else:
                accounts[recipient]["received_messages"].append([socket_to_user[str(addr)], message])
                clientsocket.send("Recipient not online. Will deliver on demand :)".encode())
        else:
            clientsocket.send("Invalid: user not found".encode())

    return 0

def deliver(clientsocket, request):

    if len(request) != 3:
        help(clientsocket=clientsocket)
        clientsocket.send('\r\n\r\n'.encode())
        return -1
    
    username = request[1]
    password = request[2]

    if (username in accounts and accounts[username]["password"] == password):
    
        for item in accounts[username]["received_messages"]:
            message_send = f"\nFrom {item[0]}: Message: {item[1]}\n"
            clientsocket.send(message_send.encode())

        accounts[username]["received_messages"] = []
    
    else: 
        clientsocket.send("Nonexistent account or wrong password".encode())

    clientsocket.send('\r\n\r\n'.encode())
    return 0

def delete(clientsocket, request, addr):
    if len(request) != 3:
        help(clientsocket=clientsocket)
        clientsocket.send('\r\n\r\n'.encode())
        return -1

    username = request[1]
    password = request[2]
    
    # Check if another client is loggged in
    if username in accounts and accounts[username]["connection"] is not None and accounts[username]["connection"] != clientsocket:
        clientsocket.send("Another client is logged into this account!".encode())
        clientsocket.send("\r\n\r\n".encode())
    # Check if current user is logged in in any capacity
    elif (str(addr) in socket_to_user):
        if (socket_to_user[str(addr)] == username):
            clientsocket.send("You are logged into the account to be deleted. Logout first".encode())
        else:
            clientsocket.send("You are logged into a different account. Unable to delete".encode())

        clientsocket.send("\r\n\r\n".encode())
    # Aim to delete the account
    elif username in accounts and accounts[username]["password"] == password:
        clientsocket.send("Successfully deleted account\n".encode())
        if len(accounts[username]["received_messages"]) >= 1:
            clientsocket.send("Account had undelivered messages: \n".encode())
            deliver(clientsocket=clientsocket, request=request)
        
        else:
            clientsocket.send("\r\n\r\n".encode()) 

        accounts.pop(username)

    else:
        clientsocket.send("Account not found or incorrect password".encode())
        clientsocket.send("\r\n\r\n".encode())

    return 0

def help(clientsocket):
    clientsocket.send("""
    Usage: \n
    create <username> <password> \n
    ls [optional]<substring> \n
    login <username> <password> \n
    send <recipient> <message> \n
    delete <username> <password> \n
    deliver <username> <password> \n
    To logout, disconnect and reconnect to the sever!
    """.encode())

def handle_sigint(sig, frame):
    print('KeyboardInterrupt: closing server')
    # Perform cleanup operations here (e.g., closing sockets)
    for client in active_sockets:
        client.close()
    sys.exit(0)

# Startup Server
def main():

    #socket object creation
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #get information of local machine
    host = socket.gethostname()
    port = 8888

    #bind port
    serversocket.bind((host, port))

    #listen for connections
    serversocket.listen(5)

    # Set up signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, handle_sigint)

    print(f"Server running on port {port}")
    try:
        while True:

            # Accept incoming requests
            clientsocket, addr = serversocket.accept()
            active_sockets.append(clientsocket)
            print("Connection coming from %s" % str(addr))

            # Put client in its own thread
            client_thread = threading.Thread(target=handle_client, args=(clientsocket, addr))
            client_thread.start()
    except KeyboardInterrupt:
        serversocket.close()

if __name__ == "__main__":
    main()
