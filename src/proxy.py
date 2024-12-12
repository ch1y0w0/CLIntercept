#!/usr/bin/env python3

import socket

# Start listening on specified host and port
def listen(host, port):

	# Create a socket object
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Bind the socket to the host and port
	server_socket.bind((host, port))

	# Enable the server to accept connections (backlog set to 5)
	server_socket.listen(5)

	print(f"Listening on {host}:{port}...")

	return server_socket

# Get incoming packets
def get_request(s_sock):

	# Accept incoming connections
	client_socket, client_address = s_sock.accept()
	print(f"Connection from {client_address}")

	# Receive the HTTP request from the client
	http_request = client_socket.recv(1024).decode()

	# Close the client connection
	client_socket.close()

	return http_request

if __name__ == "__main__":
	sock = listen("127.0.0.1", 8080)
	while True:
		request = get_request(sock)
		print(request)

		a = input()
		if a == 'a':
			continue