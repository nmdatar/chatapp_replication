import sys
import socket
import selectors
import types
import threading

# create dictionary for account information storage
accounts = {}

# dictionary to map connected addresses to usernames
socket_to_user = {}

# current version command map
cmap = {
    "create": 0,
    "list": 1,
    "login": 2,
    "send": 3,
    "delete": 4,
    "deliver": 5,
    "help": 6,
}

# Define version of handling client commands
version = 1


def handle_client(clientsocket, addr):

    while True:

        request = clientsocket.recv(1024).decode()

        # Check if connection has ended/been closed
        if not request:
            if str(addr) in socket_to_user:
                accounts[socket_to_user[str(addr)]]["active"] = False
                accounts[socket_to_user[str(addr)]]["connection"] = None
                socket_to_user.pop(str(addr))
            print("Connection closed from client with address %s" % str(addr))
            break

        request = request.split()

        # Check correct version in client code
        if (request[0] != str(version)):
            print(request[0])
            clientsocket.send(
                "Incorrect client software version. Please use an updated version!".encode())
            break

        request.pop(0)

        # CREATE
        if request[0] == str(cmap['create']):

            # Make sure command is correct length
            if len(request) != 3:
                help(clientsocket=clientsocket)
                continue

            username = request[1]
            password = request[2]

            if addr in socket_to_user:
                clientsocket.send(
                    "You are already logged into an account!".encode())

            elif username in accounts:
                clientsocket.send(
                    "Account with username already exists. Try again".encode())

            # If successful create and init a new account
            else:
                accounts[username] = {}
                accounts[username]["password"] = password
                accounts[username]["active"] = False
                accounts[username]["received_messages"] = []
                accounts[username]["connection"] = None
                clientsocket.send("Account successfully created".encode())

        # LIST
        elif request[0] == str(cmap['list']):

            if len(request) >= 3:
                help(clientsocket=clientsocket)
                continue

            # check a list of accounts with wildcard if given
            if len(request) > 1:
                search_term = request[1]
                matching_accounts = [
                    username for username in accounts if search_term in username]

            else:
                matching_accounts = list(accounts.keys())

            if matching_accounts:
                response = "\n".join(matching_accounts)
                clientsocket.send(response.encode())
            else:
                clientsocket.send("No matching accounts".encode())

        # LOGIN
        elif request[0] == str(cmap['login']):

            if len(request) != 3:
                help(clientsocket=clientsocket)
                clientsocket.send('\r\n\r\n'.encode())
                continue

            username = request[1]
            password = request[2]

            # Check if logged in already
            if str(addr) in socket_to_user:
                clientsocket.send(
                    "You are already logged into an account!".encode())

            # Make sure correct account information is provided
            elif username in accounts and accounts[username]["password"] == password:
                accounts[username]["active"] = True
                accounts[username]["connection"] = clientsocket
                socket_to_user[str(addr)] = username
                clientsocket.send("Login successful".encode())

                # Deliver undelivered messages
                if len(accounts[username]["received_messages"]) >= 1:
                    clientsocket.send(
                        "Account has undelivered messages: ".encode())
                    deliver(username=username, password=password,
                            clientsocket=clientsocket)

            else:
                clientsocket.send("Login unsuccessful".encode())

            clientsocket.send("\r\n\r\n".encode())

        # SEND
        elif request[0] == str(cmap['send']):

            if len(request) < 3:
                help(clientsocket=clientsocket)
                continue

            # Check self socket status
            if (str(addr)) not in socket_to_user:
                clientsocket.send("Please login to send a message".encode())

            else:
                recipient = request[1]
                message = " ".join(request[2:])

                # check user in sequence
                if recipient in accounts:
                    # Check if logged in
                    if accounts[recipient]['active'] == True:
                        message_send = f"\nFrom {socket_to_user[str(addr)]}: Message: {message}"
                        accounts[recipient]["connection"].send(
                            message_send.encode())
                        clientsocket.send("Message delivered!".encode())

                    # Otherwise queue the message
                    else:
                        accounts[recipient]["received_messages"].append(
                            [socket_to_user[str(addr)], message])
                        clientsocket.send(
                            "Recipient not online. Will deliver on demand :)".encode())
                else:
                    clientsocket.send("Invalid: user not found".encode())

        # DELIVER
        elif request[0] == str(cmap['deliver']):

            if len(request) != 3:
                help(clientsocket=clientsocket)
                clientsocket.send('\r\n\r\n'.encode())
                continue

            username = request[1]
            password = request[2]
            deliver(username=username, password=password,
                    clientsocket=clientsocket)
            clientsocket.send('\r\n\r\n'.encode())

        # DELETE
        elif request[0] == str(cmap['delete']):

            if len(request) != 3:
                help(clientsocket=clientsocket)
                clientsocket.send('\r\n\r\n'.encode())
                continue

            username = request[1]
            password = request[2]

            # Check if another client is loggged in
            if username in accounts and accounts[username]["connection"] is not None and accounts[username]["connection"] != clientsocket:
                clientsocket.send(
                    "Another client is logged into this account!".encode())

            # Check if current user is logged in in any capacity
            elif (str(addr) in socket_to_user):
                if (socket_to_user[str(addr)] == username):
                    clientsocket.send(
                        "You are logged into the account to be deleted. Logout first".encode())
                else:
                    clientsocket.send(
                        "You are logged into a different account. Unable to delete".encode())

            # Aim to delete the account
            elif username in accounts and accounts[username]["password"] == password:
                if len(accounts[username]["received_messages"]) >= 1:
                    clientsocket.send(
                        "Account has undelivered messages: \n".encode())
                    deliver(username=username, password=password,
                            clientsocket=clientsocket)
                accounts.pop(username)
                clientsocket.send("Successfully deleted account".encode())
            else:
                clientsocket.send(
                    "Account not found or incorrect password".encode())

            clientsocket.send("\r\n\r\n".encode())

        # HELP
        elif request[0] == str(cmap['help']):
            help(clientsocket=clientsocket)

        else:
            clientsocket.send(
                "Invalid command\nValid commands: create list login send deliver delete help".encode())


def deliver(username, password, clientsocket):

    if (username in accounts and accounts[username]["password"] == password):

        for item in accounts[username]["received_messages"]:
            message_send = f"\nFrom {item[0]}: Message: {item[1]}\n"
            clientsocket.send(message_send.encode())

        accounts[username]["received_messages"] = []

    else:
        clientsocket.send("Nonexistent account or wrong password".encode())


def help(clientsocket):
    clientsocket.send("""
    Usage: \n
    create <username> <password> \n
    list [optional]<substring> \n
    login <username> <password> \n
    send <recipient> <message> \n
    delete <username> <password> \n
    deliver <username> <password> \n
    To logout, disconnect and reconnect to the sever!
    """.encode())


def run():

    # socket object creation
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get information of local machine
    host = socket.gethostname()
    port = 8888

    # bind port
    serversocket.bind((host, port))

    # listen for connections
    serversocket.listen(5)
    print(f"Server running on port {port}")
    try:
        while True:

            # Accept incoming requests
            clientsocket, addr = serversocket.accept()
            print("Connection coming from %s" % str(addr))

            # Put client in its own thread
            client_thread = threading.Thread(
                target=handle_client, args=(clientsocket, addr))
            client_thread.start()
    except KeyboardInterrupt:
        pass

    serversocket.close()


if __name__ == "__main__":
    run()
