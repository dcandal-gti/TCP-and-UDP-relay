import socket
from time import time, sleep
import struct
import argparse

# def print(text):
#     class bcolors:
#         HEADER = '\033[95m'
#         OKBLUE = '\033[94m'
#         OKCYAN = '\033[96m'
#         OKGREEN = '\033[92m'
#         WARNING = '\033[93m'
#         FAIL = '\033[91m'
#         ENDC = '\033[0m'
#         BOLD = '\033[1m'
#         UNDERLINE = '\033[4m'
#     __builtins__.print(bcolors.OKGREEN + str(text) + bcolors.OKGREEN)

# Input arguments ########################################
parser = argparse.ArgumentParser()
parser.add_argument("ip", help="IP address for binding the receiver TCP socket")
parser.add_argument("port", help="Port for binding the receiver TCP socket", type=int)
parser.add_argument("-b", "--buffer_size", help="The buffer size for incoming and outgoing sockets", type=int, default=1500)
args = parser.parse_args()
print(args)
##########################################################

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind( (args.ip, args.port) )
sock.listen(1)
connection, client_address = sock.accept()

while True:
    try:
        data = connection.recv(args.buffer_size)
        timestamp = time()
        if data:
            message_timestamp = struct.unpack('<d', data)[0]
            print(f"[RECV] TS mensaje: {message_timestamp:.7f}    Recep: {timestamp:.7f}    Desfase: {(timestamp-message_timestamp):.7f}")
            connection.sendall(data)
            print(f"[SEND] TS mensaje: {message_timestamp:.7f}")
    except:
        if data == b'exit':
            print(f"[RECV] End!")
            connection.close()
            sock.close()
            break
