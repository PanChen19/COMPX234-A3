import socket
import threading
import time
# Create a dictionary to store tuples
tuple_space = {}
# A lock to control concurrent access to the tuple space to avoid issues when multiple clients modify it simultaneously
tuple_lock = threading.Lock()
# Global variables to track statistics like client count, operation count, count for each operation, error count
client_count = 0
operation_count = 0
read_count = 0
get_count = 0
put_count = 0
error_count = 0
def handle_client(conn, addr):
    global client_count, operation_count, read_count, get_count, put_count, error_count
    client_count += 1  # Increment client count when a new client connects
    with conn:
         # Wrap the connection into a text stream to read each line from the client
        file = conn.makefile()# Remove leading/trailing whitespace
        for line in file:
            try:
                message = line.strip()
                operation_count += 1  # Increment operation count for each request
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
# Function to periodically print server statistics (every 10 seconds)
def print_summary():
    while True:
        time.sleep(10)  # Wait for 10 seconds
        with tuple_lock:
            num_tuples = len(tuple_space)  # Count the number of tuples in the tuple space
            total_key_len = sum(len(k) for k in tuple_space)  # Total length of all keys
            total_val_len = sum(len(v) for v in tuple_space.values())  # Total length of all values
            avg_key = total_key_len / num_tuples if num_tuples else 0  # Average key length
            avg_val = total_val_len / num_tuples if num_tuples else 0  # Average value length
            avg_tuple = (total_key_len + total_val_len) / num_tuples if num_tuples else 0  # Average tuple size

        # Print server statistics
        print(f"[Summary]")
        print(f" Tuples: {num_tuples}")  # Number of tuples in tuple space
        print(f" Avg tuple size: {avg_tuple:.2f}, key: {avg_key:.2f}, value: {avg_val:.2f}")  # Average tuple size, key, and value
        print(f" Clients: {client_count}")  # Number of clients connected
        print(f" Total ops: {operation_count}, READ: {read_count}, GET: {get_count}, PUT: {put_count}")  # Operation statistics
        print(f" Errors: {error_count}")  # Number of errors
        print("-" * 40)
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