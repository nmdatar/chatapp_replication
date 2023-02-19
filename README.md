# Chat App

In this project, we implement a chat app with two different implementation. One using the gRPC framework, the other using Python's socket library.

## Get Started

First, make sure you installed Pipenv, a virtual enviroment manager.

Install all dependencies via `pipenv install`

Enter the virtual enviroment via `pipenv shell`

Depending on the project, refer to either 'gRPC' or 'WebSocket'

### gRPC

Run Server `python3 chatapp_grpc/server.py`

Run Client `python3 chatapp_grpc/client.py`

### WebSocket

Run Server `python3 chatapp_websocket/server.py`

Run Client `python3 chatapp_websocket/client.py`
