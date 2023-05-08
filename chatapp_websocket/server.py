import os
import argparse
from typing import List, Dict, Tuple
import requests
import socket
import threading
import json
import time
import sqlite3

class Server:
    def __init__(self, host: str, port: int = 8000, id: int = 1, primary: bool = True, primary_host : str = 'localhost', primary_port : int = 8003) -> None:
        self.accounts = {} # all accounts that exist
        self.socket_to_user = {} # dictionary to map connected addresses to usernames
        self.active_sockets = [] # active sockets
        self.host = host
        self.port = port
        self.id = id
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.clients = {}
        self.generate_available = 0
        self.primary = primary
        self.internal_port = self.port + 1
        
        self.receive_port = self.port + 2
        self.receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.await_port = self.port + 3
        self.await_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.await_socket.bind((self.host, self.await_port))
        self.await_socket.listen(5)
        self.receive.bind((self.host, self.receive_port))
        self.receive.listen(5)

        self.create_database()
        self.load_database()
        print(self.accounts)

        # Change primary_host etc if it is a secondary server
        if not self.primary:
            self.primary_host = primary_host
            self.primary_port = primary_port
        else:
            self.primary_host = self.host
            self.primary_port = self.await_port

        self.backup_servers = {}
        
        print(f"Server started on {self.host}:{self.port}")

    def create_database(self) -> None:
        self.db_filename = f'./server{self.id}.db'
        conn = sqlite3.connect(self.db_filename)
        self.cursor = conn.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts'")
        if self.cursor.fetchone() is None:
            self.cursor.execute("CREATE TABLE accounts (row_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, UNIQUE(username, password))")
            conn.commit()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
        if self.cursor.fetchone() is None:
            self.cursor.execute("CREATE TABLE messages (row_id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, recipient TEXT, message TEXT, UNIQUE(sender, recipient, message))")
            conn.commit()

        self.cursor.close()
        conn.close()

    def load_database(self) -> None:
        conn = sqlite3.connect(self.db_filename)

        # Create a cursor object to execute SQL statements
        self.cursor = conn.cursor()

        # Retrieve all rows from the "accounts" table
        self.cursor.execute("SELECT * FROM accounts")
        rows = self.cursor.fetchall()

        for row in rows:
            username = row[1]
            password = row[2]
            self.create(username=username, password=password)

        conn = sqlite3.connect(self.db_filename)
        self.cursor = conn.cursor()

        self.cursor.execute("SELECT * FROM messages")
        rows = self.cursor.fetchall()
        for row in rows:
            sender = row[1]
            recipient = row[2]
            message = row[3]

            self.queue_message(sender=sender, recipient=recipient, message=message)

    def update_database(self, args) -> None:

        print('updating db')
        conn = sqlite3.connect(self.db_filename)
        self.cursor = conn.cursor()
        args = json.loads(args)

        update_type = args['update_type']

        if update_type == 'create':
            
            username = args['username']
            password = args['password']

            self.cursor.execute("INSERT OR IGNORE INTO accounts (username, password) VALUES (?, ?)", (username, password))

        elif update_type == 'delete':

            username = args['username']
            password = args['password']
            self.cursor.execute("DELETE FROM accounts WHERE username = ?", (username,))

        elif update_type == 'queue':

            sender = args['sender']
            recipient = args['recipient']
            message = args['message']

            self.cursor.execute("INSERT OR IGNORE INTO messages (sender, recipient, message) VALUES (?, ?, ?)", (sender, recipient, message))

        conn.commit()
        self.cursor.close()
        conn.close()

    def maintain_heartbeat_socket(self) -> None:
        self.internal = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.internal.bind((self.host, self.internal_port))
        self.internal.listen(5)

        while True:
            heartbeat_server, addr = self.internal.accept()
            heartbeat_server.close()

    def await_servers(self) -> None:
        while True:
            try: 
                new_server, addr = self.await_socket.accept()
                data = b''
                while True:
                    
                    chunk = new_server.recv(1024)
                    if not chunk:
                        break
                    data += chunk
                print('Received all data from connecting server')
                data = data.decode()
                msg = json.loads(data)
                id = msg.pop('id')
                self.backup_servers[id] = msg
                print(self.backup_servers)
                self.update_backups()
                

            except Exception:
                break
        

    def update_backups(self) -> None:
        msg = {}
        if self.id in self.backup_servers.keys():
            self.backup_servers.pop(self.id)
        
        msg['type'] = 'update'
        msg['backup_servers'] = self.backup_servers
        msg['primary_host'] = self.host
        msg['primary_port'] = self.internal_port
        msg = json.dumps(msg)
        self.send_backup_message(request=msg)

    def receive_updates(self) -> None:
        while not self.primary:
            
            try:
                main_server, addr = self.receive.accept()
                
                data = b''
                while True:
                    chunk = main_server.recv(1024)
                    if not chunk:
                        main_server.close()
                        break
                
                    data += chunk
                
                data = data.decode()
                msg = json.loads(data)
                request_type = msg['type']

                if request_type == 'update':
                    
                    self.primary_host = msg['primary_host']
                    self.primary_port = msg['primary_port']
                    self.backup_servers = msg['backup_servers']

                elif request_type == 'create':
                    username = msg['username']
                    password = msg['password']
                    self.create(username=username, password=password)
                
                elif request_type == 'delete':
                    username = msg['username']
                    password = msg['password']
                    self.delete(username=username, password=password)
                
                elif request_type == 'queue':
                    recipient = msg['recipient']
                    sender= msg['sender']
                    message = msg['message']
                    self.queue_message(sender=sender, recipient=recipient, message=message)

            except Exception:
                break

        return 

    def takeover(self) -> None:
        print("Taking Over ;)")
        self.backup_servers.pop(str(self.id))
        self.primary = True
        self.primary_host = self.host
        self.primary_port = self.internal_port
        self.update_backups()
        await_thread = threading.Thread(target=self.await_servers)
        await_thread.start()
        maintain_heartbeat_thread = threading.Thread(target=self.maintain_heartbeat_socket)
        maintain_heartbeat_thread.start()
    
    def heartbeat(self) -> None:
        while True:
            if not self.primary:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        s.connect((self.primary_host, self.primary_port))
                        s.close()
                except Exception as e:

                    if self.id == int(min(self.backup_servers.keys())):
                        self.takeover()
                        return 
                        
                    else:
                        print('Connected to new master: ', self.primary_host, self.primary_port)
                        time.sleep(2)

            time.sleep(2)
    
    def send_backup_message(self, request):
        for backup in self.backup_servers.values():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((backup['host'], backup['receive_port']))
                s.send(request.encode())
                s.close()


    def handle_client(self, client, addr) -> None:
        self.clients[client] = "active"
        print("waiting for responses")
        while True:
            try:
                request = client.recv(1024).decode().strip()
                request = request.split()
                if not request:
                    if str(addr) in self.socket_to_user:
                        self.accounts[self.socket_to_user[str(addr)]]["active"] = False
                        self.accounts[self.socket_to_user[str(addr)]]["connection"] = None
                        self.socket_to_user.pop(str(addr))
                    print("Connection closed from client with address %s" % str(addr))
                    client.close()
                    break
            except Exception:
                client.close()
                break
            
            response = []
            msg = {}

            if request[0] == "quit":
                self.clients.pop(client)
                print(f"Client {client} disconnected")

            elif request[0] == 'create':
                username = request[1]
                password = request[2]

                if addr in self.socket_to_user:
                    response.append("You are already logged into an account!")

                elif username in self.accounts:
                    response.append("Account with username already exists. Try again")
                
                else:
                    response.append("Account successfully created")
                    self.create(username=username, password=password)
                    if self.primary:
                        msg['type'] = 'create'
                        msg['username'] = username
                        msg['password'] = password
                        msg = json.dumps(msg)

                        self.send_backup_message(request=msg)
            
            elif request[0] == 'delete':
                username = request[1]
                password = request[2]
                
                # Check if another client is loggged in
                if username in self.accounts and self.accounts[username]["active"] and (str(addr) not in self.socket_to_user):
                    response.append("Someone is logged into this account")
                # Check if current user is logged in in any capacity
                elif (str(addr) in self.socket_to_user):
                    if (self.socket_to_user[str(addr)] == username):
                        response.append("You are logged into the account to be deleted. Logout first")
                    else:
                        response.append("You are logged into a different account. Unable to delete")
                
                elif username not in self.accounts or self.accounts[username]['password'] != password:
                    response.append("Account not found or incorrect password")
                
                else:
                    response.append("Successfully deleted account")
                    response += self.delete(username=username, password=password)

                    msg['type'] = 'delete'
                    msg['username'] = username
                    msg['password'] = password
                    msg = json.dumps(msg)
                    self.send_backup_message(request=msg)
            
            elif request[0] == 'login':
                username = request[1]
                password = request[2]
                response += self.login(username=username, password=password, client=client, addr=addr)

            elif request[0] == 'ls':
                request = " ".join(request)
                response += self.ls(request=request)

            elif request[0] == 'send':
                
                recipient = request[1]
                message = " ".join(request[2:])


                # Check self socket status
                if (str(addr)) not in self.socket_to_user:
                    response.append("Please login to send a message")

                elif recipient in self.accounts and self.accounts[recipient]['active'] == True:
                    message_send = f"\nFrom {self.socket_to_user[str(addr)]}: Message: {message}"
                    self.accounts[recipient]['connection'].send(message_send.encode())
                    response.append("Message delivered!")

                elif recipient not in self.accounts:
                    response.append('Invalid: user not found')

                else:
                    sender = self.socket_to_user[str(addr)]
                    response += self.queue_message(sender=sender, recipient=recipient, message=message)
                    msg['type'] = 'queue'
                    msg['recipient'] = recipient
                    msg['sender'] = sender
                    msg['message'] = message
                    msg = json.dumps(msg)
                    self.send_backup_message(request=msg)

            for msg in response:
                client.send(msg.encode())

                
    
    def create(self, username, password) -> None:
        """
        Args: clientsocket, request, addr
        
        Creates an account for a user
        """
        self.accounts[username] = {}
        self.accounts[username]["password"] = password
        self.accounts[username]["active"] = False
        self.accounts[username]["received_messages"] = []
        self.accounts[username]["connection"] = None

        args = {}
        args['update_type'] = 'create'
        args['username'] = username
        args['password'] = password
        args = json.dumps(args)
        self.update_database(args=args)

        print(f"account created u:{username} p:{password}")

    def delete(self, username, password) -> list:
        """
        Args: clientsocket connection, client equest, address of connection

        Deletes an account for each user

        """

        resp_msgs = []

        if len(self.accounts[username]["received_messages"]) >= 1:
            resp_msgs.append("Account had undelivered messages: \n")
            resp_msgs += self.deliver(username=username)

        args = {}
        args['update_type'] = 'delete'
        args['username'] = username
        args['password'] = password
        args = json.dumps(args)
        self.update_database(args)

        self.accounts.pop(username)
        print('deleted the account')
        return resp_msgs
        
    def deliver(self, username) -> list:

        """
        Args: Clientsocket connection, request,

        Delivers a message to each user when undelivered
        
        """

        resp_msgs = []
        
        for msg in self.accounts[username]["received_messages"]:
            msg = json.loads(msg)
            sender = msg['From']
            message = msg['message']
            message_send = f"\nFrom {sender}: Message: {message}\n"
            resp_msgs.append(message_send)

        self.accounts[username]["received_messages"] = []

        return resp_msgs
    
    def login(self, username, password, client, addr) -> list:
        """
        Args: clientsocket, request, address of connection
        Logins a user to an exisitng account
        """

        resp_msgs = []

        # Check if logged in already
        if str(addr) in self.socket_to_user:
            resp_msgs.append("You are already logged into an account!")

        # Make sure correct account information is provided
        elif username in self.accounts and self.accounts[username]["password"] == password:
            self.accounts[username]["active"] = True
            self.socket_to_user[str(addr)] = username
            self.accounts[username]['connection'] = client
            resp_msgs.append("Login successful")

            # Deliver undelivered messages
            if len(self.accounts[username]["received_messages"]) >= 1:
                resp_msgs.append("Account has undelivered messages: ")
                resp_msgs += self.deliver(username=username)

        else:
            resp_msgs.append("Login unsuccessful")

        return resp_msgs
    
    def ls(self, request) -> list:
        """
        Args: clientsocket, request of user
        Lists all existing accounts
        """

        resp_msgs = []
        request = request.split() 
        # check a list of accounts with wildcard if given
        if len(request) > 1:
            search_term = request[1]
            matching_accounts = [username for username in self.accounts if search_term in username]

        else:
            matching_accounts = list(self.accounts.keys())
        
        if matching_accounts:
            matching_accounts = "\n".join(matching_accounts)
            resp_msgs.append(matching_accounts)
        else: 
            resp_msgs.append('No matching accounts')

        return resp_msgs
    
    def queue_message(self, sender, recipient, message) -> list:
        """
        Args: clientsocket, request, addr
        Sends a message to each user
        """

        resp_msgs = []
        # queue message
        msg = {}
        msg['From'] = sender
        msg['message'] = message
        print(msg)
        msg = json.dumps(msg)
        self.accounts[recipient]["received_messages"].append(msg)
        resp_msgs.append("Recipient not online. Will deliver on demand :)")

        args = {}
        args['update_type'] = 'queue'
        args['sender'] = sender
        args['recipient'] = recipient
        args['message'] = message
        args = json.dumps(args)
        self.update_database(args=args)

        return resp_msgs

    def run(self) -> None:

        if self.primary:
            await_thread = threading.Thread(target=self.await_servers)
            await_thread.start()
            maintain_heartbeat_socket = threading.Thread(target=self.maintain_heartbeat_socket)
            maintain_heartbeat_socket.start()

        else:
            rec_thread = threading.Thread(target=self.receive_updates)
            rec_thread.start()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                msg = {}
                msg['host'] = self.host
                msg['id'] = self.id
                msg['receive_port'] = self.receive_port
                msg['primary_port'] = self.internal_port
                msg['port'] = self.port
                msg = json.dumps(msg)
                s.connect((self.primary_host, self.primary_port))
                s.sendall(msg.encode())
                s.close()

            time.sleep(2)
            heartbeat_thread = threading.Thread(target=self.heartbeat)
            heartbeat_thread.start()

        while True:
            client, addr = self.server.accept()
            print(f"New connection from {addr[0]}:{addr[1]}")

            if self.primary:
                client_thread = threading.Thread(target=self.handle_client, args=(client, addr))
                client_thread.start()
            else: 
                print('Client connected to non-primary server!')
                msg ='Tried to connect to a non-primary server. Failed.'
                client.send(msg.encode())
                client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server Connection")
    parser.add_argument('--host', help='IPV4 Host', type=str)
    parser.add_argument('--port', help='Port', type=int)
    parser.add_argument('--pr', help='Primary/Secondary server', action='store_true')
    parser.add_argument('--prhost', help='Primary Host', type=str)
    parser.add_argument('--prport', help='Primary Host', type=int)
    parser.add_argument('--id', help='Server ID', type=int)
    args = parser.parse_args()
    print(args)
    server = Server(host=args.host, port=args.port, primary=args.pr, id=args.id, primary_host=args.prhost, primary_port=args.prport)
    server.run()