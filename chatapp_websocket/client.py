import sys
import socket
import select

#Create socket object
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '10.250.196.39'
port = 8888
version = 1
# Connect to the server
clientsocket.connect((host, port))

inputs = [clientsocket, sys.stdin]
cmap = {
    "create" : 0,
    "ls" : 1,
    "login" : 2,
    "send" : 3,
    "delete" : 4,
    "deliver" : 5,
    "help" : 6,
}
print("""\nEnter 'help' to see command usage :) \n""")
# Account creation request from user
while True:
    sys.stdout.write("\033[92mchatapp@love:~$\033[0m ")
    sys.stdout.flush()

    # Check if input from client vs server message sending
    readable, writable, exceptional = select.select(inputs, [], [])
    for r in readable:
        
        # If received message from server
        if r is clientsocket:
            response = r.recv(1024)
            if response:
                print(response.decode())
            else: 
                print('Connection closed from server...')
                # clientsocket.close()
                sys.exit(0)

        # If client provides a command input      
        elif r is sys.stdin:
                
                sys.stdout.write("-->\n")
                sys.stdout.flush()
                request = input("")
                request = request.split()
                if (request[0] in cmap):
                    request[0] = str(cmap[request[0]])
                else:
                    request[0] = str(max(cmap.values()) + 1)
                # send request to server
                request = [str(version)] + request
                clientsocket.send((" ".join(request)).encode())

                # flush undelivered messages if login, delete, or deliver
                if request[1] == str(cmap['login']) or request[1] == str(cmap['delete']) or request[1] == str(cmap['deliver']):
                    response = ""
                    while (response[-4:] != '\r\n\r\n'):
                        response = clientsocket.recv(1024).decode()
                        if response[-4:] == '\r\n\r\n':
                            if len(response) > 4:
                                print(response[:-4])
                        else:
                            print(response)

                else: 
                    response = clientsocket.recv(1024).decode()
                    print(response)

# Close the connection
clientsocket.close()
