import socket
import threading
import select
from urllib.parse import urlparse

class HTTPProxyServer:
	def __init__(self, host='0.0.0.0', port=8080):
		self.host = host
		self.port = port
		self.server_socket = None
		self.clients = []

	def start(self):
		"""Start the proxy server and listen for incoming connections."""
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.bind((self.host, self.port))
		self.server_socket.listen(5)
		print(f"Proxy Server listening on {self.host}:{self.port}")
		
		while True:
			client_socket, client_address = self.server_socket.accept()
			print(f"Accepted connection from {client_address}")
			self.clients.append(client_socket)
			client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
			client_thread.daemon = True
			client_thread.start()

	def handle_client(self, client_socket):
		"""Handle communication with the client."""
		request = self.receive_request(client_socket)
		if request:
			parsed_url = self.parse_request(request)
			if parsed_url:
				self.forward_request(client_socket, parsed_url, request)
			else:
				print("Error: Failed to parse the request.")
		else:
			print("Error: Failed to receive the request.")

	def receive_request(self, client_socket):
		"""Receive HTTP request from the client."""
		try:
			request = b""
			while True:
				ready = select.select([client_socket], [], [], 5)
				if ready[0]:
					data = client_socket.recv(4096)
					if not data:
						break
					request += data
				else:
					break
			if request:
				return request.decode('utf-8', errors='ignore')
			else:
				print("No data received.")
		except Exception as e:
			print(f"Error receiving request: {e}")
		return None

	def parse_request(self, request):
		"""Parse the HTTP request to extract the target URL."""
		try:
			lines = request.split('\r\n')
			first_line = lines[0]
			method, url, _ = first_line.split()
			parsed_url = urlparse(url)
			return parsed_url
		except Exception as e:
			print(f"Error parsing request: {e}")
		return None

	def forward_request(self, client_socket, parsed_url, request):
		"""Forward the HTTP request to the target server and send the response back."""
		try:
			target_host = parsed_url.hostname

			target_port = parsed_url.port or 80
			target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			target_socket.connect((target_host, target_port))

			# Forward the HTTP request to the destination server
			target_socket.sendall(request.encode('utf-8'))

			# Receive the response from the server
			response = self.receive_response(target_socket)
			if response:

				# Send the server's response back to the client
				client_socket.sendall(response)
			target_socket.close()
		except Exception as e:
			print(f"Error forwarding request: {e}")
		finally:
			client_socket.close()

	def receive_response(self, target_socket):
		"""Receive the HTTP response from the target server."""
		try:
			response = b""
			while True:
				data = target_socket.recv(4096)
				if not data:
					break
				response += data
			return response
			print(response)
		except Exception as e:
			print(f"Error receiving response: {e}")
		return None

if __name__ == "__main__":
	proxy = HTTPProxyServer(host='0.0.0.0', port=8080)
	proxy.start()
