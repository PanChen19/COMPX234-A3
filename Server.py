import socket
import threading
import time
# Create a dictionary to store tuples
tuple_space = {}
# A lock to control concurrent access to the tuple space to avoid issues when multiple clients modify it simultaneously
tuple_lock = threading.Lock()
def handle_client(conn, addr):
    global read_count
    with conn:
         # Wrap the connection into a text stream to read each line from the client
        file = conn.makefile()# Remove leading/trailing whitespace
        for line in file:
            try:
                message = line.strip()
                if len(message) < 5:
                    continue# Skip invalid messages (too short)
                cmd_type = message[4]
                rest = message[6:]
               # If it's a READ or GET operation
                if cmd_type in ("R", "G"):
                    key = rest  # The key is the command argument
                    with tuple_lock:
                        # Check if the key exists in the tuple space
                        if key in tuple_space:
                            val = tuple_space[key]
                            if cmd_type == "R":
                                response = f"OK ({key}, {val}) read"  # For READ, return key-value
                                read_count += 1  # Increment read success count
                            else:
                                response = f"OK ({key}, {val}) removed"  # For GET, return and remove the key
                                del tuple_space[key]
                                get_count += 1  # Increment get success count
                        else:
                            response = f"ERR {key} does not exist"  # If key doesn't exist, return error
                            error_count += 1  # Increment error count

                # If it's a PUT operation
                elif cmd_type == "P":
                    try:
                        k, v = rest.split(" ", 1)  # Split the rest into key and value
                    except ValueError:
                        response = "ERR invalid format"  # If splitting fails, return error
                        error_count += 1
                    else:
                        # If key-value length exceeds limit (970 bytes), return error
                        if len(k) + len(v) + 1 > 970:
                            response = "ERR input too long"  # Input too long error
                            error_count += 1
                        else:
                            with tuple_lock:
                                # If the key already exists, return error
                                if k in tuple_space:
                                    response = f"ERR {k} already exists"
                                    error_count += 1
                                else:
                                    tuple_space[k] = v  # Add the key-value pair to the tuple space
                                    response = f"OK ({k}, {v}) added"  # Success message
                                    put_count += 1  # Increment put success count

                # If the command is invalid
                else:
                    response = "ERR invalid command"
                    error_count += 1

                # Encode the response to match the protocol and send it back to the client
                response_encoded = f"{len(response)+4:03d} {response}\n"
                conn.sendall(response_encoded.encode())  # Send the response

            except Exception as e:
                print(f"[Error] from {addr}: {e}")  # Print error message if any exception occurs
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