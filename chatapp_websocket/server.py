import sys
import socket
import signal
import threading
import argparse

class Server:
    def __init__(self, primary: bool, port: int = 8888, primary_address: str = '') -> None:
        self.accounts = {} # all accounts that exist
        self.socket_to_user = {} # dictionary to map connected addresses to usernames
        self.active_sockets = [] # active sockets
        self.version = 1 # server version No.

        # current version command map
        self.cmap = {
            "create" : 0,
            "ls" : 1,
            "login" : 2,
            "send" : 3,
            "delete" : 4,
            "deliver" : 5,
            "help" : 6,
        }
        self.primary = primary
        self.primary_address = primary_address
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket object creation
        self.host = socket.gethostname()
        self.port = port
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)


    def handle_client(self, clientsocket, addr) -> None:
        
        while True:

            try:
                request = clientsocket.recv(1024).decode()
            except OSError:
                break
            # Check if connection has ended/been closed
            if not request:
                if str(addr) in self.socket_to_user:
                    self.accounts[self.socket_to_user[str(addr)]]["active"] = False
                    self.accounts[self.socket_to_user[str(addr)]]["connection"] = None
                    self.socket_to_user.pop(str(addr))
                print("Connection closed from client with address %s" % str(addr))
                self.active_sockets.remove(clientsocket)
                break

            request = request.split()

            # Check correct version in client code
            if (request[0] != str(self.version)):
                clientsocket.send("Incorrect client software version. Please use an updated version!".encode())
                break

            request.pop(0)

            # CREATE
            if request[0] == str(self.cmap['create']):
                
                self.create(clientsocket=clientsocket, request=request, addr=addr)

            # LIST 
            elif request[0] == str(self.cmap['ls']):
                self.ls(clientsocket=clientsocket, request=request)
            
            # LOGIN
            elif request[0] == str(self.cmap['login']):     
                self.login(clientsocket=clientsocket, request=request, addr=addr)

            # SEND
            elif request[0] == str(self.cmap['send']):
                self.send(clientsocket=clientsocket, request=request, addr=addr)

            # DELIVER
            elif request[0] == str(self.cmap['deliver']):
                self.deliver(clientsocket=clientsocket, request=request)
                
            # DELETE
            elif request[0] == str(self.cmap['delete']):
                self.delete(clientsocket=clientsocket, request=request, addr=addr)
                
            # HELP
            elif request[0] == str(self.cmap['help']):
                self.help(clientsocket=clientsocket)

            else:
                clientsocket.send("Invalid command\nValid commands: create list login send deliver delete help".encode())

    def create(self, clientsocket, request, addr) -> int:
        """
        Args: clientsocket, request, addr
        
        Creates an account for a user
        """
        # Make sure command is correct length
        if len(request) != 3:
            help(clientsocket=clientsocket)
            return -1

        username = request[1]
        password = request[2]

        if addr in self.socket_to_user:
            clientsocket.send("You are already logged into an account!".encode())

        elif username in self.accounts:
            clientsocket.send("Account with username already exists. Try again".encode())
        
        # If successful create and init a new account
        else:
            self.accounts[username] = {}
            self.accounts[username]["password"] = password
            self.accounts[username]["active"] = False
            self.accounts[username]["received_messages"] = []
            self.accounts[username]["connection"] = None
            clientsocket.send("Account successfully created".encode())

        return 0
                
    def ls(self, clientsocket, request) -> None:
        """
        Args: clientsocket, request of user
        Lists all existing accounts
        """
        if len(request) >= 3:
            help(clientsocket=clientsocket)
            return -1

        # check a list of accounts with wildcard if given
        if len(request) > 1:
            search_term = request[1]
            matching_accounts = [username for username in self.accounts if search_term in username]

        else:
            matching_accounts = list(self.accounts.keys())
        
        if matching_accounts:
            response = "\n".join(matching_accounts)
            clientsocket.send(response.encode())
        else:
            clientsocket.send("No matching accounts".encode())

        return 0

    def login(self, clientsocket, request, addr) -> int:
        """
        Args: clientsocket, request, address of connection
        Logins a user to an exisitng account
        """

        if len(request) != 3:
            help(clientsocket=clientsocket)
            clientsocket.send('\r\n\r\n'.encode())
            return -1
        
        username = request[1]
        password = request[2]

        # Check if logged in already
        if str(addr) in self.socket_to_user:
            clientsocket.send("You are already logged into an account!".encode())
            clientsocket.send("\r\n\r\n".encode())

        # Make sure correct account information is provided
        elif username in self.accounts and self.accounts[username]["password"] == password:
            self.accounts[username]["active"] = True
            self.accounts[username]["connection"] = clientsocket
            self.socket_to_user[str(addr)] = username
            clientsocket.send("Login successful\n".encode())

            # Deliver undelivered messages
            if len(self.accounts[username]["received_messages"]) >= 1:
                clientsocket.send("Account has undelivered messages: ".encode())
                self.deliver(clientsocket=clientsocket, request=request)
            
            else:
                clientsocket.send("\r\n\r\n".encode())

        else:
            clientsocket.send("Login unsuccessful".encode())
            clientsocket.send("\r\n\r\n".encode())

        return 0

    def send(self, clientsocket, request, addr) -> int:
        """
        Args: clientsocket, request, addr
        Sends a message to each user
        """
        if len(request) < 3:
            help(clientsocket=clientsocket)
            return -1

        # Check self socket status
        if (str(addr)) not in self.socket_to_user:
            clientsocket.send("Please login to send a message".encode())
        
        else:
            recipient = request[1]
            message = " ".join(request[2: ])

            #check user in sequence
            if recipient in self.accounts:
                # Check if logged in
                if self.accounts[recipient]['active'] == True:
                    message_send = f"\nFrom {self.socket_to_user[str(addr)]}: Message: {message}"
                    self.accounts[recipient]["connection"].send(message_send.encode())
                    clientsocket.send("Message delivered!".encode())

                # Otherwise queue the message
                else:
                    self.accounts[recipient]["received_messages"].append([self.socket_to_user[str(addr)], message])
                    clientsocket.send("Recipient not online. Will deliver on demand :)".encode())
            else:
                clientsocket.send("Invalid: user not found".encode())

        return 0

    def deliver(self, clientsocket, request) -> int:

        """
        Args: Clientsocket connection, request,

        Delivers a message to each user when undelivered
        
        """

        if len(request) != 3:
            help(clientsocket=clientsocket)
            clientsocket.send('\r\n\r\n'.encode())
            return -1
        
        username = request[1]
        password = request[2]

        if (username in self.accounts and  self.accounts[username]["password"] == password):
        
            for item in  self.accounts[username]["received_messages"]:
                message_send = f"\nFrom {item[0]}: Message: {item[1]}\n"
                clientsocket.send(message_send.encode())

            self.accounts[username]["received_messages"] = []
        
        else: 
            clientsocket.send("Nonexistent account or wrong password".encode())

        clientsocket.send('\r\n\r\n'.encode())
        return 0

    def delete(self, clientsocket, request, addr):
        """
        Args: clientsocket connection, client equest, address of connection

        Deletes an account for each user

        """
        if len(request) != 3:
            help(clientsocket=clientsocket)
            clientsocket.send('\r\n\r\n'.encode())
            return -1

        username = request[1]
        password = request[2]
        
        # Check if another client is loggged in
        if username in self.accounts and self.accounts[username]["connection"] is not None and  self.accounts[username]["connection"] != clientsocket:
            clientsocket.send("Another client is logged into this account!".encode())
            clientsocket.send("\r\n\r\n".encode())
        # Check if current user is logged in in any capacity
        elif (str(addr) in  self.socket_to_user):
            if (self.socket_to_user[str(addr)] == username):
                clientsocket.send("You are logged into the account to be deleted. Logout first".encode())
            else:
                clientsocket.send("You are logged into a different account. Unable to delete".encode())

            clientsocket.send("\r\n\r\n".encode())
        # Aim to delete the account
        elif username in self.accounts and self.accounts[username]["password"] == password:
            clientsocket.send("Successfully deleted account\n".encode())
            if len(self.accounts[username]["received_messages"]) >= 1:
                clientsocket.send("Account had undelivered messages: \n".encode())
                self.deliver(clientsocket=clientsocket, request=request)
            
            else:
                clientsocket.send("\r\n\r\n".encode()) 

            self.accounts.pop(username)

        else:
            clientsocket.send("Account not found or incorrect password".encode())
            clientsocket.send("\r\n\r\n".encode())

        return 0

    def help(self, clientsocket) -> None:
        clientsocket.send("""
        Usage: \n
        create <username> <password> \n
        ls [optional]<substring> \n
        login <username> <password> \n
        send <recipient> <message> \n
        delete <username> <password> \n
        deliver <username> <password> \n
        To logout, disconnect and reconnect to the server!
        """.encode())

    def handle_secondary(self) -> None:
        pass

    def handle_sigint(self, sig, frame) -> None:
        print('KeyboardInterrupt: closing server')
        # Perform cleanup operations here (e.g., closing sockets)
        for client in self.active_sockets:
            client.close()
        sys.exit(0)

    # Startup Server
    def main(self) -> None:

        # Set up signal handler for SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, self.handle_sigint)

        print(f"Server running on host: {self.host}, port: {self.port}")
        try:
            while True:

                # Accept incoming requests
                clientsocket, addr = self.serversocket.accept()
                self.active_sockets.append(clientsocket)
                print("Connection coming from %s" % str(addr))

                # Put client in its own thread
                client_thread = threading.Thread(target=self.handle_client, args=(clientsocket, addr))
                client_thread.start()
        except KeyboardInterrupt:
            self.serversocket.close()

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print('Usage: python3 server.py port[required]')
    #     sys.exit(0)
    # port = int(sys.argv[1])
    parser = argparse.ArgumentParser(description="Spinup a server")
    parser.add_argument('-p', '--port', type=int, help='Give the port number you want the server to listen on')
    parser.add_argument('--primary', action='store_true', help='Define if this is a primary server')
    parser.add_argument('--primary_address', type=str, help='Give the address of primary server if secondary')
    args = parser.parse_args()
    port = args.port
    primary = args.primary
    if not primary:
        primary_address = args.primary_address
        server = Server(port=port, primary=primary, primary_address=primary_address)
    else:
        server = Server(port=port, primary=primary)
        
    server.main()
