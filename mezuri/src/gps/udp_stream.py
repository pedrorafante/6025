import socket
 
UDP_IP = "192.168.137.100"
UDP_PORT = 8500

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT)) 
sock.settimeout(5)

while True:
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print("received message: %s" % data)
    except socket.timeout:
        print("Failed reading")
        pass
