import socket

# Define the IP address and port of the ESP32
ip_address = "192.168.1.100"
port = 2390

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the local port
sock.bind(('', port))

# Send a string to the ESP32
message = "Hello, ESP32!"
sock.sendto(message.encode('utf-8'), (ip_address, port))

# Receive a string from the ESP32
data, addr = sock.recvfrom(1024)

# Print the received string
print(data.decode('utf-8'))

# Close the socket
sock.close()
