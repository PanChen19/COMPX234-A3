import socket
import sys
# Function to format the request from the client, ensuring it matches the protocol
def format_request(line):
    line = line.strip()  # Remove leading/trailing whitespace
    if not line:  # If the line is empty, return None
        return None
    parts = line.split(" ", 2)  # Split the line into command and arguments
    if parts[0] == "PUT" and len(parts) == 3:  # If it's a PUT command
        cmd = "P"
        k, v = parts[1], parts[2]  # Extract the key and value
        content = f"{cmd} {k} {v}"  # Format the content according to the protocol
    elif parts[0] in ("READ", "GET") and len(parts) == 2:  # If it's a READ or GET command
        cmd = "R" if parts[0] == "READ" else "G"
        k = parts[1]
        content = f"{cmd} {k}"  # Format the content according to the protocol
    else:
        return None  # If the command is invalid, return None

    if len(content) > 995:  # If the message is too long, return None
        return None
    msg = f"{len(content)+4:03d} {content}"  # Construct the final message
    return msg, line  # Return the formatted message and the original line

# Function to run the client
def run_client(host, port, file_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))  # Connect to the server
        with open(file_path, 'r', encoding='utf-8') as f:  # Open the input file
            for line in f:
                result = format_request(line)  # Format each line in the file
                if result is None:
                    print(f"{line.strip()}: ERR invalid or too long")  # If the command is invalid, print an error
                    continue
                request_msg, original_line = result  # Get the formatted request
                sock.sendall((request_msg + '\n').encode())  # Send the request to the server
                response = sock.recv(1024).decode().strip()  # Receive the response from the server
                print(f"{original_line.strip()}: {response[4:]}")  # Print the server's response (after removing the first 4 characters which are the length)

if __name__ == "__main__":
    if len(sys.argv) != 4:  # Ensure the correct number of command-line arguments
        print("Usage: python client.py <host> <port> <file>")
    else:
        run_client(sys.argv[1], int(sys.argv[2]), sys.argv[3])  # Start the client