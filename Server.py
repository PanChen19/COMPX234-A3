import socket
import threading
# Function to start the server and listen on the specified port
def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Create a TCP server socket
    server.bind(('', port)) # Bind the server to the specified port
    server.listen() # Start listening for client connections
    print(f"Server listening on port {port}...")# Print server listening message

    while True:
        conn, addr = server.accept()# Accept incoming client connections
        threading.Thread(target=handle_client, args=(conn, addr)).start()# Handle each connection in a separate thread

def handle_client(conn, addr):
    with conn:
        print(f"New connection from {addr}")
        conn.sendall(b"Welcome to the tuple space server!\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2: # Ensure the correct number of command-line arguments
        print("Usage: python server.py <port>")
    else:
        start_server(int(sys.argv[1])) # Start the server with the specified port