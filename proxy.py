import argparse
import socket
import select
import sys
import os
import re

def clear_screen():
	os.system('cls' if os.name == 'nt' else 'clear')

def parse_arguments():
	parser = argparse.ArgumentParser(description="Packet interceptor and controller.")
	parser.add_argument("-target", help="Specify the target IP to filter packets.", type=str, default=None)
	parser.add_argument("-ip", help="Specify the listening IP address.", type=str, default="127.0.0.1")
	parser.add_argument("-port", help="Specify the listening port.", type=int, default=8080)
	return parser.parse_args()

def extract_destination(data):
	try:
		# Decode HTTP headers and extract Host
		headers = data.decode(errors='replace').split("\r\n")
		for header in headers:
			if header.lower().startswith("host:"):
				host = header.split(":", 1)[1].strip()
				if ":" in host:
					dest_ip, dest_port = host.split(":")
					return dest_ip, int(dest_port)
				return host, 80  # Default to port 80 for HTTP
	except Exception as e:
		print(f"Error extracting destination: {e}")
	return None, None

def forward_packet(dest_ip, dest_port, data):
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as forward_socket:
			forward_socket.connect((dest_ip, dest_port))
			forward_socket.sendall(data)

			response = forward_socket.recv(4096)
			return response
	except Exception as e:
		return f"Error forwarding packet: {e}".encode()

def main():
	args = parse_arguments()
	target_ip = args.target
	listen_ip = args.ip
	listen_port = args.port

	print(f"Listening on {listen_ip}:{listen_port}")

	try:
		# Create a socket to listen for incoming connections
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.bind((listen_ip, listen_port))
		server_socket.listen(5)
		print("Server started. Waiting for connections...")

		while True:
			readable, _, _ = select.select([server_socket], [], [], 1)

			if server_socket in readable:
				client_socket, client_address = server_socket.accept()
				print(f"Connection received from {client_address}")

				try:
					while True:
						data = client_socket.recv(4096)
						if not data:
							break

						if target_ip and client_address[0] != target_ip:
							# Forward packet directly without user input
							client_socket.sendall(data)
							continue

						# Process the packet
						dest_ip, dest_port = extract_destination(data)
						if not dest_ip or not dest_port:
							print("Failed to extract destination. Dropping packet.")
							continue

						clear_screen()
						packet_details = f"Packet from {client_address}:{data.decode(errors='replace')}"
						print(packet_details)
						print(f"\nForward to {dest_ip}:{dest_port} or Drop? [F/D]")

						user_input = input("Enter your choice: ").strip().upper()

						if user_input == "F":
							response = forward_packet(dest_ip, dest_port, data)
							if response:

								clear_screen()
								print(f"Response from server:\n{response.decode(errors='replace')}\n")
								print("Forward response to client or Drop? [F/D]")
								response_input = input("Enter your choice: ").strip().upper()
								if response_input == "F":
									client_socket.sendall(response)
								elif response_input == "D":
									print("Response dropped.")
								else:
									print("Invalid option. Dropping response by default.")
						elif user_input == "D":
							print("Packet dropped.")
						else:
							print("Invalid option. Dropping packet by default.")

				except Exception as e:
					print(f"Error handling connection: {e}")
				finally:
					client_socket.close()
					print(f"Connection closed with {client_address}")

	except KeyboardInterrupt:
		print("Shutting down server...")
	except Exception as e:
		print(f"An error occurred: {e}")
	finally:
		server_socket.close()
		sys.exit(0)


if __name__ == "__main__":
	clear_screen()
	main()
