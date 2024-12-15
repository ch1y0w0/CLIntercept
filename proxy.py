#!/usr/bin/env python3

import socket
import select
import re
import os
from urllib.parse import urlparse
import sys
import argparse
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.application import Application

class HTTPProxyServer:

	def __init__(self, target=None, host='0.0.0.0', port=8080):
		"""Initialize the proxy server with an optional target, host, and port."""
		self.host = host
		self.port = port
		self.server_socket = None
		self.clients = []
		self.target = target
		self.user_input = ''
		self.bindings = KeyBindings()

		# Set up key bindings for prompt-toolkit
		self.bindings.add('esc')(self.handle_escape)
		self.bindings.add('enter')(self.handle_enter)

	def start(self):
		"""Start the proxy server and listen for incoming connections."""
		self.clear_screen()
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.bind((self.host, self.port))
		self.server_socket.listen(5)
		print(f"Proxy Server listening on {self.host}:{self.port}")

		while True:
			client_socket, client_address = self.server_socket.accept()
			self.clients.append(client_socket)
			self.handle_client(client_socket)  # Handle client sequentially

	def handle_client(self, client_socket):
		"""Handle communication with the client."""
		request = self.receive_request(client_socket)
		if request:
			url, parsed_url = self.parse_request(request)
			if url:
				if self.target and self.is_target(parsed_url):  # If target is set, filter requests
					self.clear_screen()
					print("HTTP Request Accepted:")
					print(request)
					self.user_action(client_socket, url, parsed_url, request)
				elif not self.target:  # If no target filter, show all packets
					self.clear_screen()
					print("HTTP Request:")
					print(request)
					self.user_action(client_socket, url, parsed_url, request)
				else:
					self.forward_request(client_socket, url, parsed_url, request)
			else:
				print("Error: Failed to parse the request.")
		else:
			print("Error: Failed to receive the request.")

	def user_action(self, client_socket, url, parsed_url, request):
		"""Allow the user to edit or decide whether to forward or drop the request."""
		self.user_input = request  # Set the current request for editing

		# Create a prompt for the user to edit the request
		print_formatted_text(f"\nEdit the HTTP request below (Press 'Esc' to discard, 'Enter' to forward):\n")
		self.edit_request(client_socket, url, parsed_url)

	def edit_request(self, client_socket, url, parsed_url):
		"""Allow user to edit the request."""
		application = Application(
			layout=prompt.PromptSession(self.user_input),
			key_bindings=self.bindings
		)
		application.run()

		if self.user_input:
			self.forward_request(client_socket, url, parsed_url, self.user_input)

	def handle_escape(self, event):
		"""Handle Escape key to discard changes."""
		self.user_input = ''
		print_formatted_text("\nEditing discarded. Dropping the packet.\n")

	def handle_enter(self, event):
		"""Handle Enter key to forward the edited request."""
		print_formatted_text(f"\nRequest forwarded: {self.user_input}")

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
			return request.decode('utf-8', errors='ignore') if request else None
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
			return url, parsed_url
		except Exception as e:
			print(f"Error parsing request: {e}")
		return None, None

	def forward_request(self, client_socket, url, parsed_url, request):
		"""Forward the HTTP request to the target server and send the response back."""
		try:
			target_host = parsed_url.hostname
			target_port = parsed_url.port or 80
			print(f"Forwarding request to {target_host}:{target_port}...")

			target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			target_socket.connect((target_host, target_port))

			# Forward the HTTP request to the destination server
			target_socket.sendall(request.encode('utf-8'))

			# Receive the response from the server
			response = self.receive_response(target_socket)
			if response:
				self.handle_response(client_socket, response, parsed_url)

			target_socket.close()
		except Exception as e:
			print(f"Error forwarding request: {e}")
		finally:
			client_socket.close()

	def handle_response(self, client_socket, response, parsed_url):
		"""Handle server response based on user input."""
		if self.target and self.is_target(parsed_url):  # If target is set, filter responses
			print(f"Response from target server:")
			print(response.decode('utf-8', errors='ignore'))
			user_action = input("Enter 'f' to forward, 'd' to drop the response: ").strip().lower()
			if user_action == 'f':
				print("Response forwarded to client.")
				client_socket.sendall(response)
			elif user_action == 'd':
				print("Packet Dropped")
			else:
				print("Invalid action. Dropping the packet by default.")
		elif not self.target:  # If no target filter, show all responses
			print(f"Response from server:")
			print(response.decode('utf-8', errors='ignore'))
			user_action = input("Enter 'f' to forward, 'd' to drop the response: ").strip().lower()
			if user_action == 'f':
				print("Response forwarded to client.")
				client_socket.sendall(response)
			elif user_action == 'd':
				print("Packet Dropped")
			else:
				print("Invalid action. Dropping the packet by default.")

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
		except Exception as e:
			print(f"Error receiving response: {e}")
		return None

	def is_target(self, parsed_url):
		"""Check if the received request is for the target."""
		return re.search(self.target, parsed_url.geturl()) is not None

	def clear_screen(self):
		"""Clear the terminal screen."""
		if sys.platform == "win32":
			os.system('cls')
		else:
			os.system('clear')

def parse_args():
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(description="Start a proxy server with optional target filter.")
	parser.add_argument('-t', '--target', type=str, help="Target URL pattern to filter requests and responses.")
	parser.add_argument('-H', '--host', type=str, default='0.0.0.0', help="Host to bind the proxy server.")
	parser.add_argument('-P', '--port', type=int, default=8080, help="Port to bind the proxy server.")
	return parser.parse_args()

if __name__ == "__main__":
	args = parse_args()
	target = args.target if args.target else None
	proxy = HTTPProxyServer(target=target, host=args.host, port=args.port)
	proxy.start()
