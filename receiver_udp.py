import socket
from time import time
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
parser.add_argument("ip", help="IP address for binding the receiver UDP socket")
parser.add_argument("port", help="Port for binding the receiver UDP socket", type=int)
parser.add_argument("-b", "--buffer_size", help="The buffer size for incoming and outgoing sockets", type=int, default=1500)
args = parser.parse_args()
print(args)
##########################################################

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind( (args.ip, args.port) )

while True:
    try:
        data, addr = sock.recvfrom(args.buffer_size)
        timestamp = time()
        message_timestamp = struct.unpack('<d', data)[0]
        print(f"[RECV] TS mensaje: {message_timestamp:.7f}    Recep: {timestamp:.7f}    Desfase: {(timestamp-message_timestamp):.7f}")
        sock.sendto(data, addr)
        print(f"[SEND] TS mensaje: {message_timestamp:.7f}")
    except:
        if data == b'exit':
            sock.close()
            print(f"[RECV] End!")
            break
