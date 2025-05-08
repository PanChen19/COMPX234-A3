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
                if not message:
                    continue# Skip invalid messages (too short)
                
                # Basic echo response for now
                response = f"ECHO: {message}"
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