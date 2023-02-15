import sys
import socket
import select

#Create socket object
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# clientsocket.setblocking(False)
#Local machine name
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
    readable, writable, exceptional = select.select(inputs, [], [])
    for r in readable:
        
        if r is clientsocket:
            response = r.recv(1024)
            if response:
                print(response.decode())
            else: 
                print('socket closing...')
                clientsocket.close()
                sys.exit()
            
        elif r is sys.stdin:
                
                sys.stdout.write("-->\n")
                sys.stdout.flush()
                request = input("")
                request = request.split()


                # if request[0] == "create":
                #     # username = input("Enter a username: ")
                #     # password = input("Enter a password: ")
                #     clientsocket.send((request).encode())
                #     # Receive the response from the server
                #     response = clientsocket.recv(1024).decode()
                #     print(response)
                
                clientsocket.send((" ".join(request)).encode())

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

                # elif request[0] == 'delete':
                #     response = None
                #     while (response != ""):
                #         response = clientsocket.recv(1024).decode()
                #         print(response)

                else: 
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