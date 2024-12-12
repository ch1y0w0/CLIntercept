import socket
import ssl
import threading
import re

# Function to open the port and start listening for requests
def start_listening(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening on {host}:{port}")
    return server_socket

# Function to handle incoming requests and forward them
def handle_request(client_socket, client_address, use_ssl):
    request_data = receive_request(client_socket)
    print(f"Request from {client_address}:\n{request_data}")

    destination_host, destination_port, request = parse_request(request_data)
    if use_ssl:
        server_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), ssl_version=ssl.PROTOCOL_TLS)
    else:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_socket.connect((destination_host, destination_port))
    forward_request(server_socket, request)
    response = receive_response(server_socket)
    print(f"Response from {destination_host}:{destination_port}:\n{response}")

    forward_response(client_socket, response)

    client_socket.close()
    server_socket.close()

# Function to receive a request from the client
def receive_request(client_socket):
    request_data = b""
    while True:
        part = client_socket.recv(1024)
        request_data += part
        if len(part) < 1024:
            break
    return request_data.decode()

# Function to parse the request to get destination info and the request to forward
def parse_request(request_data):
    lines = request_data.split("\r\n")
    first_line = lines[0].split()
    method, url, _ = first_line

    # Check if the URL starts with http:// or https://, if not add http:// by default
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # Extract hostname and port from URL
    pattern = r'^(https?://)([^:/\s]+)(?::(\d+))?(/.*)?$'
    match = re.match(pattern, url)
    
    if not match:
        raise ValueError(f"Invalid URL in request: {url}")
    
    protocol, host, port, path = match.groups()
    
    # Set default port based on protocol
    if port is None:
        port = 443 if protocol == 'https://' else 80
    else:
        port = int(port)
    
    # Rebuild the request to send to the destination
    request = "\r\n".join(lines[1:])
    return host, port, request



# Function to forward the request to the destination server
def forward_request(server_socket, request_data):
    server_socket.sendall(request_data.encode())

# Function to receive the response from the server
def receive_response(server_socket):
    response_data = b""
    while True:
        part = server_socket.recv(1024)
        response_data += part
        if len(part) < 1024:
            break
    return response_data.decode()

# Function to forward the server's response to the client
def forward_response(client_socket, response_data):
    client_socket.sendall(response_data.encode())

# Main function to start the proxy server
def run_proxy_server(host='0.0.0.0', port=8080, use_ssl=True):
    server_socket = start_listening(host, port)
    
    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_request, args=(client_socket, client_address, use_ssl)).start()

# Run the proxy server
if __name__ == "__main__":
    run_proxy_server()
