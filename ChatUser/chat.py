import base64
import socket
import time


txt=input("Username: ")
message = '{:type :online, :username "%s"}' % txt
message = base64.b64encode(bytes(message,'utf-8'))
user_id = '435hhr6h-4fsg-35fw-hddr-4ivi68fjvb12'
receiver = ':all'
port = 42424
multicast_group = '230.185.192.108'
start_message = "|".join([str(time.time()), user_id, receiver, str(message.decode('utf-8'))])
start_message = base64.b64encode(bytes(start_message, 'utf-8'))

address = (multicast_group, port)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", port))
mreq = socket.inet_aton(multicast_group) + socket.inet_aton('0.0.0.0')
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

sock.sendto(start_message, address)
sock.settimeout(20)


