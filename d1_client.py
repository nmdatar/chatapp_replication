import sys
import socket
import selectors
import types 

#Create socket object
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# clientsocket.setblocking(False)
#Local machine name
host = socket.gethostname()
port = 8888

# Connect to the server
clientsocket.connect((host, port))
print("""Enter request (create <username> <password> list [optional]<search_term>\n): """)
# Account creation request from user
while True:
    request = input("$ ")
    request = request.split()


    # if request[0] == "create":
    #     # username = input("Enter a username: ")
    #     # password = input("Enter a password: ")
    #     clientsocket.send((request).encode())
    #     # Receive the response from the server
    #     response = clientsocket.recv(1024).decode()
    #     print(response)
    
    clientsocket.send((" ".join(request)).encode())
    response = clientsocket.recv(1024).decode()
    print(response)

    # elif request[0] == "list":
    #     search_term = ""
    #     if len(request) > 1:
    #         search_term = request[1]
    #     clientsocket.send(("list_accounts" + search_term).encode())
    #     response = clientsocket.recv(1024).decode()
    #     print(response)

# Close the connection
clientsocket.close()