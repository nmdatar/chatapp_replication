import unittest
import threading
import socket
import time
import sys

# Import server code
from server import handle_client, active_sockets, accounts

# Define the test server host and port
HOST = "127.0.0.1"
PORT = 5000

# Define a test client to send messages to the test server
class TestClient:

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send(self, message):
        self.socket.sendall(message.encode())
        response = self.socket.recv(1024).decode()
        return response

    def close(self):
        self.socket.close()

# Define the unit test
class chattest(unittest.test):

    # Start the test server before running each test
    def setup(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()

        # Start the server in a new thread
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.start()

    # Stop the test server after running each test
    def stop(self):
        self.server_socket.close()
        self.server_thread.join()

    # Function to run the test server in a separate thread
    def run_server(self):
        while True:
            clientsocket, addr = self.server_socket.accept()
            active_sockets.append(clientsocket)
            threading.Thread(target=handle_client, args=(clientsocket, addr)).start()

    # Test the create account functionality
    def test_create(self):
        client = TestClient(HOST, PORT)
        response = client.send("1 create testuser testpassword\n")
        self.assertEqual(response, "Account successfully created")

        response = client.send("1 create testuser testpassword\n")
        self.assertEqual(response, "Account with username already exists. Try again")

        response = client.send("1 create anotheruser anotherpassword\n")
        self.assertEqual(response, "Account successfully created")

        client.close()

    # Test the login functionality
    def test_login(self):
        client = TestClient(HOST, PORT)
        response = client.send("1 login testuser testpassword\n")
        self.assertEqual(response, "Login unsuccessful")

        response = client.send("1 create testuser testpassword\n")
        self.assertEqual(response, "Account successfully created")

        response = client.send("1 login testuser testpassword\n")
        self.assertEqual(response, "Login successful\n")

        response = client.send("1 login testuser wrongpassword\n")
        self.assertEqual(response, "Login unsuccessful")

        client.close()

    # Test the send message functionality
    def test_send_message(self):
        client1 = TestClient(HOST, PORT)
        client2 = TestClient(HOST, PORT)

        response = client1.send("1 create testuser testpassword\n")
        self.assertEqual(response, "Account successfully created")

        response = client2.send("1 create anotheruser anotherpassword\n")
        self.assertEqual(response, "Account successfully created")

        response = client1.send("1 login testuser testpassword\n")
        self.assertEqual(response, "Login successful\n")

        response = client1.send("1 send anotheruser Hello\n”)
        self.assertEqual(response, “Message delivered!\n”)
