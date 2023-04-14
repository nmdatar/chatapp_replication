import sys
import socket
import select

class Client:
    def __init__(self) -> None:

        self.hosts = ['10.250.122.230', '10.250.122.230', '10.250.122.230']
        self.ports = [8888, 8889, 8890]
        self.version = 1
    
        self.cmap = {
            "create" : 0,
            "ls" : 1,
            "login" : 2,
            "send" : 3,
            "delete" : 4,
            "deliver" : 5,
            "help" : 6,
        }
        
        print("""\nEnter 'help' to see command usage :) \n""")
    
    def serve_client(self, host, port) -> None:

        try: 
            # Connect to the server
            self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientsocket.connect((host, port))
            self.inputs = [self.clientsocket, sys.stdin]
            print(f"Connecting to host: {host}, port: {port}")

        except ConnectionRefusedError:
            return
        
        while True:
            sys.stdout.write("\033[92mchatapp@love:~$\033[0m ")
            sys.stdout.flush()

            # Check if input from client vs server message sending
            readable, writable, exceptional = select.select(self.inputs, [], [])
            for r in readable:
                
                # If received message from server
                if r is self.clientsocket:
                    response = r.recv(1024)
                    if response:
                        print(response.decode())
                    else: 
                        print('Connection closed from server...')
                        self.clientsocket.close()
                        return
                        # clientsocket.close()
                        

                # If client provides a command input      
                elif r is sys.stdin:
                        
                        sys.stdout.write("-->\n")
                        sys.stdout.flush()
                        request = input("")
                        request = request.split()
                        if (request[0] in self.cmap):
                            request[0] = str(self.cmap[request[0]])
                        else:
                            request[0] = str(max(self.cmap.values()) + 1)
                        # send request to server
                        request = [str(self.version)] + request
                        self.clientsocket.send((" ".join(request)).encode())

                        # flush undelivered messages if login, delete, or deliver
                        if request[1] == str(self.cmap['login']) or request[1] == str(self.cmap['delete']) or request[1] == str(self.cmap['deliver']):
                            response = ""
                            while (response[-4:] != '\r\n\r\n'):
                                response = self.clientsocket.recv(1024).decode()
                                if response[-4:] == '\r\n\r\n':
                                    if len(response) > 4:
                                        print(response[:-4])
                                else:
                                    print(response)

                        else: 
                            response = self.clientsocket.recv(1024).decode()
                            print(response)
    def main(self) -> None:

        for host, port in zip(self.hosts, self.ports):
            self.serve_client(host=host, port=port)

        print('All servers down')
        sys.exit(0)



if __name__ == '__main__':
    
    client = Client()
    client.main()





