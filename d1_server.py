import sys
import socket
import selectors
import types 
import threading

lock = threading.Lock()

#create dictionary for account information storage
accounts = {}
socket_to_user = {}

def handle_client(clientsocket, addr):

    while True:

        request = clientsocket.recv(1024).decode()

        if not request:
            if str(addr) in socket_to_user:
                accounts[socket_to_user[str(addr)]]["active"] = False
                accounts[socket_to_user[str(addr)]]["connection"] = None
            socket_to_user.pop(str(addr))
            print("Connection closed from client with address %s" % str(addr))
            break

        request = request.split()

        if request[0] == "create":
            username = request[1]
            password = request[2]

            if username in accounts:
                clientsocket.send("Account with username already exists. Try again".encode())
            else:
                accounts[username] = {}
                accounts[username]["password"] = password
                accounts[username]["active"] = False
                accounts[username]["received_messages"] = []
                accounts[username]["connection"] = None
                clientsocket.send("Account successfully created".encode())

        # LIST
            
        elif request[0] == "list":
            #check wildcard
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
        
        elif request[0] == "login":
            username = request[1]
            password = request[2]

            if username in accounts and accounts[username]["password"] == password:
                accounts[username]["active"] = True
                accounts[username]["connection"] = clientsocket
                socket_to_user[str(addr)] = username
                clientsocket.send("Login successful\n".encode())

                for item in accounts[username]["received_messages"]:
                    message_send = f"From {item[0]}: Message: {item[1]}"
                    clientsocket.send(message_send.encode())
            
                accounts[username]["received_messages"] = []
            else:
                clientsocket.send("Login unsuccessful".encode())

        # elif request[0] == "logout":
        #     username = request[1]
        #     if username in online_users:
        #         online_users.remove(username)
        #         clientsocket.send("Logout successful".encode())
        #     else:
        #         clientsocket.send("Logout unsuccessful".encode())

        elif request[0] == "send_message":

            if (str(addr)) not in socket_to_user:
                clientsocket.send("Please login to send a message".encode())
            
            else:
                # sender = request[1]  
                recipient = request[1]
                message = " ".join(request[2: ])

                #check user in sequence

                if recipient in accounts:
                    if accounts[recipient]['active'] == True:
                        message_send = f"From {socket_to_user[str(addr)]}: Message: {message}"
                        accounts[recipient]["connection"].send(message_send.encode())
                        clientsocket.send("Message delivered!".encode())
                    else:
                        #queue
                        # if recipient in message:
                        #     message[recipient].append((sender, message))
                        # else:
                        #     message[recipient] = [(sender, message)]
                        #     clientsocket.send("Message queued".encode())
                        accounts[recipient]["received_messages"].append([socket_to_user[str(addr)], message])
                else:
                    clientsocket.send("Invalid: user not found".encode())

        elif request[0] == "delete":

            username = request[1]
            password = request[2]
                
            if (str(addr) in socket_to_user):
                if (socket_to_user[str(addr)] == username):
                    clientsocket.send("You are logged into the account to be deleted. Logout and try again".encode())
                else:
                    clientsocket.send("You are logged into a different account. Unable to delete".encode())

            elif username in accounts and accounts[username]["password"] == password:
                if len(accounts[username]["received_messages"]) >= 1:
                    clientsocket.send("Account has undelivered messages: \n".encode())
                    for item in accounts[username]["received_messages"]:
                        message_send = f"From {item[0]}: Message: {item[1]}\n"
                        clientsocket.send(message_send.encode())

                    accounts[username]["received_messages"] = []
                accounts.pop(username)
                clientsocket.send("Successfully deleted account".encode())
            else:
                clientsocket.send("Account not found or incorrect password".encode())

        else:
            clientsocket.send("Invalid command\nUsage: create list login logout send delete\n".encode())

# #create online users tracker
# online_users = set()

#socket object creation
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#get information of local machine
host = socket.gethostname()
port = 8888

#bind port
serversocket.bind((host, port))

#listen for connections
serversocket.listen(5)
print(f"Server running on port {port}")
while True:
    clientsocket, addr = serversocket.accept()
    print(f"{clientsocket.fileno()}")
    print("Connection coming from %s" % str(addr))
    # request = clientsocket.recv(1024).decode()
    # request = request.split()
    # CREATE

    client_thread = threading.Thread(target=handle_client, args=(clientsocket, addr))
    client_thread.start()

