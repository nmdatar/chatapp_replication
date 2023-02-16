import sys
import socket
import select

#Create socket object
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 8888

# Connect to the server
clientsocket.connect((host, port))

inputs = [clientsocket, sys.stdin]
print("""Enter request (create <username> <password> list [optional]<search_term>\n): """)
# Account creation request from user
while True:
    sys.stdout.write("$ ")
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
                print('socket closing...')
                clientsocket.close()
                sys.exit()

        # If client provides a command input      
        elif r is sys.stdin:
                
                sys.stdout.write("-->\n")
                sys.stdout.flush()
                request = input("")
                request = request.split()
                
                # send request to server
                clientsocket.send((" ".join(request)).encode())

                # flush undelivered messages if login, delete, or deliver
                if request[0] == "login" or request[0] == 'delete' or request[0] == 'deliver':
                    response = ""
                    responses = []
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