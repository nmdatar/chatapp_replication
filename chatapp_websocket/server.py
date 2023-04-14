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
        self.server_connections = [('10.250.122.230', 8889), ('10.250.122.230', 9001), ('10.250.122.230', 10001)]

        # current version command map
        self.cmap = {
            "create" : 0,
            "ls" : 1,
            "login" : 2,
            "send" : 3,
            "delete" : 4,
            "deliver" : 5,
            "help" : 6,
            "receive" : 7,
        }
        self.primary = primary
        self.primary_address = primary_address
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket object creation
        self.host = socket.gethostname()
        self.port = port
        self.internal_port = port + 1
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)


    def handle_client(self, clientsocket, addr) -> None:
        
        while True:

            try:
                request = clientsocket.recv(1024).decode()
                print(request)
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
            response = self.process_request(request=request, addr=addr)
            for resp in response:
                clientsocket.send(resp.encode())


    def process_request(self, request, addr) -> list:
        resp = []
        # CREATE
        if request[0] == str(self.cmap['create']):
            resp = self.create(request=request, addr=addr)
            print(resp)

        # LIST 
        elif request[0] == str(self.cmap['ls']):
            resp = self.ls(request=request)
        
        # LOGIN
        elif request[0] == str(self.cmap['login']):     
            resp = self.login(request=request, addr=addr)
            resp += ['\r\n\r\n']

        # SEND
        elif request[0] == str(self.cmap['send']):
            resp = self.send(request=request, addr=addr)

        # DELIVER
        elif request[0] == str(self.cmap['deliver']):
            resp = self.deliver(request=request)
            resp += ['\r\n\r\n']
            
        # DELETE
        elif request[0] == str(self.cmap['delete']):
            resp = self.delete(request=request, addr=addr)
            resp += ['\r\n\r\n']
            
        # HELP
        elif request[0] == str(self.cmap['help']):
            resp = self.help()

        elif request[0] == str(self.cmap['receive']):
            print('hello there')
            resp = self.receive(addr=addr)

        else:
            print(request)
            resp = ["Invalid command\nValid commands: create list login send deliver delete help bruhh"]
            resp += ['\r\n\r\n']

        return resp

    def receive(self, addr) -> list:
        resp_msgs = []
        if str(addr) in self.socket_to_user:
            username = self.socket_to_user[str(addr)]
            for msg in self.accounts[username]["received_messages"]:
                resp_msgs.append(msg)

        return resp_msgs

    def create(self, request, addr) -> list:
        """
        Args: clientsocket, request, addr
        
        Creates an account for a user
        """
        resp_msgs = []

        # Make sure command is correct length
        if len(request) != 3:
            resp_msgs.append(self.help())
            return resp_msgs
            

        username = request[1]
        password = request[2]

        if addr in self.socket_to_user:
            resp_msgs.append("You are already logged into an account!")

        elif username in self.accounts:
            resp_msgs.append("Account with username already exists. Try again")
        
        # If successful create and init a new account
        else:
            self.accounts[username] = {}
            self.accounts[username]["password"] = password
            self.accounts[username]["active"] = False
            self.accounts[username]["received_messages"] = []
            self.accounts[username]["connection"] = None


            resp_msgs.append("Account successfully created")

        return resp_msgs
                
    def ls(self, request) -> list:
        """
        Args: clientsocket, request of user
        Lists all existing accounts
        """

        resp_msgs = []

        if len(request) >= 3:
           
            resp_msgs.append(self.help())
            return resp_msgs
            
        # check a list of accounts with wildcard if given
        if len(request) > 1:
            search_term = request[1]
            matching_accounts = [username for username in self.accounts if search_term in username]

        else:
            matching_accounts = list(self.accounts.keys())
        
        if matching_accounts:
            response = "\n".join(matching_accounts)
            resp_msgs.append(response)
        else: 
            resp_msgs.append('No matching accounts')

        return resp_msgs

    def login(self, request, addr) -> list:
        """
        Args: clientsocket, request, address of connection
        Logins a user to an exisitng account
        """

        resp_msgs = []

        if len(request) != 3:
        
            resp_msgs.append(self.help())
            return resp_msgs
        
        username = request[1]
        password = request[2]

        # Check if logged in already
        if str(addr) in self.socket_to_user:
            resp_msgs.append("You are already logged into an account!")

        # Make sure correct account information is provided
        elif username in self.accounts and self.accounts[username]["password"] == password:
            self.accounts[username]["active"] = True
            self.socket_to_user[str(addr)] = username

            resp_msgs.append("Login successful\n")

            # Deliver undelivered messages
            if len(self.accounts[username]["received_messages"]) >= 1:
                resp_msgs.append("Account has undelivered messages: ")
                resp_msgs += self.deliver(request=request)

        else:
            resp_msgs.append("Login unsuccessful")

        return resp_msgs

    def send(self, request, addr) -> list:
        """
        Args: clientsocket, request, addr
        Sends a message to each user
        """

        resp_msgs = []

        if len(request) < 3:
            resp_msgs.append(self.help())
            return resp_msgs

        # Check self socket status
        if (str(addr)) not in self.socket_to_user:
            resp_msgs.append("Please login to send a message")
        
        else:
            recipient = request[1]
            message = " ".join(request[2: ])

            #check user in sequence
            if recipient in self.accounts:
                # Check if logged in
                if self.accounts[recipient]['active'] == True:
                    message_send = f"\nFrom {self.socket_to_user[str(addr)]}: Message: {message}"
                    self.accounts[recipient]["received_messages"].append(message_send)
                    resp_msgs.append("Message delivered!")

                # Otherwise queue the message
                else:
                    self.accounts[recipient]["received_messages"].append([self.socket_to_user[str(addr)], message])
                    resp_msgs.append("Recipient not online. Will deliver on demand :)")
            else:
                resp_msgs.append('Invalid: user not found')

        return resp_msgs

    def deliver(self, request) -> list:

        """
        Args: Clientsocket connection, request,

        Delivers a message to each user when undelivered
        
        """

        resp_msgs = []

        if len(request) != 3:
            resp_msgs.append(self.help())
            return resp_msgs
        
        username = request[1]
        password = request[2]

        if (username in self.accounts and  self.accounts[username]["password"] == password):
        
            for item in self.accounts[username]["received_messages"]:
                message_send = f"\nFrom {item[0]}: Message: {item[1]}\n"
                resp_msgs.append(message_send)

            self.accounts[username]["received_messages"] = []
        
        else: 
            resp_msgs.append("Nonexistent account or wrong password")

        return resp_msgs

    def delete(self, request, addr) -> list:
        """
        Args: clientsocket connection, client equest, address of connection

        Deletes an account for each user

        """

        resp_msgs = []

        if len(request) != 3:
            resp_msgs.append(self.help())
            return resp_msgs

        username = request[1]
        password = request[2]
        
        # Check if another client is loggged in
        if username in self.accounts and self.accounts[username]["active"] and (str(addr) not in self.socket_to_user):
            resp_msgs.append("Someone is logged into this account")
        # Check if current user is logged in in any capacity
        elif (str(addr) in self.socket_to_user):
            if (self.socket_to_user[str(addr)] == username):
                resp_msgs.append("You are logged into the account to be deleted. Logout first")
            else:
                resp_msgs.append("You are logged into a different account. Unable to delete")

        # Aim to delete the account
        elif username in self.accounts and self.accounts[username]["password"] == password:
            resp_msgs.append("Successfully deleted account\n")
            if len(self.accounts[username]["received_messages"]) >= 1:
                resp_msgs.append("Account had undelivered messages: \n")
                self.deliver(request=request)

            self.accounts.pop(username)

        else:
            resp_msgs.append("Account not found or incorrect password")

        return resp_msgs

    def help(self) -> str:
        return """
        Usage: \n
        create <username> <password> \n
        ls [optional]<substring> \n
        login <username> <password> \n
        send <recipient> <message> \n
        delete <username> <password> \n
        deliver <username> <password> \n
        To logout, disconnect and reconnect to the server!
        """

    def secondary_receive(self) -> None:
        
        try:
            while True:
                primary_socket, primary_addr = self.internal_socket.accept()
                request = primary_socket.recv(1024).decode()
                self.process_request(request)
        except KeyboardInterrupt:
            self.internal_socket.close()
        

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
        if not self.primary:
            self.internal_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.internal_socket.bind((self.host, self.internal_port))
            self.internal_socket.listen(5)
            listen_as_secondary = threading.Thread(target=self.secondary_receive)
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
    parser.add_argument('--id', type=int, help='The id of the server (for lowest-id election policy)')
    args = parser.parse_args()
    port = args.port
    primary = args.primary
    if not primary:
        primary_address = args.primary_address
        server = Server(port=port, primary=primary, primary_address=primary_address)
    else:
        server = Server(port=port, primary=primary)
        
    server.main()
