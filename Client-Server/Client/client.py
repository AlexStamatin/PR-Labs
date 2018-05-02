import socket


# Use TCP/IP for transport
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the given `address` and `port`
server_address = ('localhost', 8080)
print('Connecting to 127.0.0.1:8080')
client_socket.connect(server_address)
try:

    # Read input
    while 1:
        print('Enter command:\n')
        mess = input('>>')
        client_socket.sendall(mess.encode())
        # Recieve 1kB of data from the server
        data = client_socket.recv(1024)
        print('Response: ' + data.decode() + '\n')

finally:
    print('Closing socket')
    client_socket.close()