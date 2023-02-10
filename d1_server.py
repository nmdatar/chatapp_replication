import sys
import socket
import selectors
import types 


#create dictionary for account information storage
accounts = {}

#create online users tracker
online_users = set()

#socket object creation
serversocket = socket.socekt(socket.AF_INET, socket.SOCK_STREAM)

#get information of local machine
host = socket.gesthomename()
port = 8888

#bind port
serversocket.bind((host, port))

#listen for connections
serversocket.listen(5)

while True:
    clientsocket, addr = serversocket.accept()
    print("Connection coming from %s" % str(addr))
    request = clientsocket.recv(1024).decode()
    request = request.split()

    if request[0] == "create_account":
        username = request[1]
        password = request[2]

        if username in accounts:
            clientsocket.send("Choose another username".encode())
        else:
            accounts[username] = password
            clientsocket.send("Account created".encode())
    elif request[0] == "list_accounts":
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

        if username in accounts and accounts[username] == password:
            online_users.add(username)
            clientsocket.send("Login successful".encode())
        else:
            clientsocket.send("Login unsuccessful".encode())

    elif request[0] == "logout":
        username = request[1]
        if username in online_users:
            online_users.remove(username)
            clientsocket.send("Logout successful".encode())
        else:
            clientsocket.send("Logout unsuccessful".encode())

    elif request[0] == "send_message":
        sender = request[1]  
        recipient = request[2]
        message = " ".join(request[3: ])

        #check user in sequence

        if recipient in accounts:
            if recipient in online_users:
                clientsocket.send("Message delivered".encode())
            else:
                #queue
                if recipient in message:
                    message[recipient].append((sender, message))
                else:
                    message[recipient] = [(sender, message)]
                    clientsocket.send("Message queued".encode())
        else:
            clientsocket.send("Invalid: user not found".encode())

    
    clientsocket.close()