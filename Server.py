import socket
import threading
import time
# Create a dictionary to store tuples
tuple_space = {}
# A lock to control concurrent access to the tuple space to avoid issues when multiple clients modify it simultaneously
tuple_lock = threading.Lock()
def handle_client(conn, addr):
    with conn:
         # Wrap the connection into a text stream to read each line from the client
        file = conn.makefile()# Remove leading/trailing whitespace
        for line in file:
            try:
                message = line.strip()
                if len(message) < 5:
                    continue# Skip invalid messages (too short)
                
               # Basic tuple space operations
                with tuple_lock:
                    if message.startswith("PUT "):
                        _, k, v = message.split(" ", 2)
                        tuple_space[k] = v
                        response = f"OK ({k}, {v}) added"
                    elif message.startswith("GET "):
                        _, k = message.split(" ", 1)
                        if k in tuple_space:
                            v = tuple_space.pop(k)
                            response = f"OK ({k}, {v}) removed"
                        else:
                            response = f"ERR {k} does not exist"
                    elif message.startswith("READ "):
                        _, k = message.split(" ", 1)
                        if k in tuple_space:
                            response = f"OK ({k}, {tuple_space[k]}) read"
                        else:
                            response = f"ERR {k} does not exist"
                    else:
                        response = "ERR invalid command"
                
                conn.sendall(f"{len(response):03d} {response}\n".encode())
            
            except Exception as e:
                print(f"[Error] from {addr}: {e}")
                break
# Function to start the server and listen on the specified port
def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Create a TCP server socket
    server.bind(('', port)) # Bind the server to the specified port
    server.listen() # Start listening for client connections
    print(f"Server listening on port {port}...")# Print server listening message

    while True:
        conn, addr = server.accept()# Accept incoming client connections
        threading.Thread(target=handle_client, args=(conn, addr)).start()# Handle each connection in a separate thread

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2: # Ensure the correct number of command-line arguments
        print("Usage: python server.py <port>")
    else:
        start_server(int(sys.argv[1])) # Start the server with the specified port