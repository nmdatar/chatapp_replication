import threading
import random
import sys 
import time 
import socket

#things to have
#run / random
#send
#receive
#log

#todo
#listen
#shutdown


class Machine(threading.Thread):
    def __init__(self, id, clock_rate, ip_address):
        threading.Thread.__init__(self)
        self.id = id
        self.clock_rate = clock_rate
        self.networks_queue = []
        self.sockets = []
        self.logical_clock = 0
        self.log_file = open(f"vm_{id}".log", "w")
        for ip in ip_addresses:
            if ip != self.id:
                self.connect_to(ip)
    
    def connect(self, ip):
        ws = websocket.WebSocket()
        ws.connect(f"ws://{ip}:8000")
        self.sockets.append(ws)

    def update_logical_clock(self, time):
        self.logical_clock = max(self.logical_clock, time) + 1

    def log(self, event):
        timestamp = time.time()
        self.log_file.write(f"{event} at {timestamp}, logical clock={self.logical_clock}\n")

    def receive(self, message):
        self.update_logical_clock(message["time"])
        self.network_queue.append(message)
        self.log_event(f"Received message {message} from {message['from']}, network queue size={len(self.network_queue)}")

    def send(self, message):
        for socket in self.sockets:
            socket.send(message)
        self.update_logical_clock(self.logical_clock)
        self.log_event(f"Sent message {message} to {len(self.sockets)} machine(s)")

    def run(self):
        while True:
            time.sleep(1 / self.clock_rate)
            if len(self.network_queue) > 0:
                message = self.network_queue.pop(0)
                self.update_logical_clock(message["time"])
                self.log_event(f"Processed message {message}, network queue size={len(self.network_queue)}")
            else:
                event = random.randint(1, 10)
                if event == 1:
                    message = {"from": self.id, "time": self.logical_clock}
                    self.send_message(str(message))
                elif event == 2:
                    message = {"from": self.id, "time": self.logical_clock}
                    self.send_message(str(message))
                elif event == 3:
                    message = {"from": self.id, "time": self.logical_clock}
                    self.send_message(str(message))
                else:
                    self.update_logical_clock(self.logical_clock)
                    self.log_event(f"Internal event, logical clock={self.logical_clock}")




