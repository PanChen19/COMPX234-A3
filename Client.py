import socket
import sys
# Function to run the client
def run_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))# Connect to the server
        print(sock.recv(1024).decode())

if __name__ == "__main__":
    if len(sys.argv) != 3: # Ensure the correct number of command-line argument
        print("Usage: python client.py <host> <port>")
    else:
        run_client(sys.argv[1], int(sys.argv[2]))# Start the client