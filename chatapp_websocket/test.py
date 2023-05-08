import time
import threading
from server import Server

def start_server(host, port, primary, server_id, primary_host=None, primary_port=None):
    server = Server(host=host, port=port, primary=primary, id=server_id, primary_host=primary_host, primary_port=primary_port)
    server.run()

def main():
    # Start the primary server
    primary_host = '127.0.0.1'
    primary_port = 8000
    primary_thread = threading.Thread(target=start_server, args=(primary_host, primary_port, True, 1))
    primary_thread.daemon = True
    primary_thread.start()
    time.sleep(2)

    # Start backup server 1
    backup_host_1 = '127.0.0.1'
    backup_port_1 = 8001
    backup_thread_1 = threading.Thread(target=start_server, args=(backup_host_1, backup_port_1, False, 2, primary_host, primary_port))
    backup_thread_1.daemon = True
    backup_thread_1.start()
    time.sleep(2)

    # Start backup server 2
    backup_host_2 = '127.0.0.1'
    backup_port_2 = 8002
    backup_thread_2 = threading.Thread(target=start_server, args=(backup_host_2, backup_port_2, False, 3, primary_host, primary_port))
    backup_thread_2.daemon = True
    backup_thread_2.start()
    time.sleep(2)

    # Simulate primary server failure
    print("Simulating primary server failure...")
    primary_thread.join(timeout=0.1)
    time.sleep(5)

    # Check if the backup server with the lowest ID has taken over
    print("Checking if backup server 1 has taken over...")
    backup_server_1 = Server(host=backup_host_1, port=backup_port_1, primary=False, id=2, primary_host=primary_host, primary_port=primary_port)
    assert backup_server_1.primary == True, "Backup server 1 did not take over"
    print("Backup server 1 has taken over")

if __name__ == "__main__":
    main()
