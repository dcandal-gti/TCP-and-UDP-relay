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
#     __builtins__.print(bcolors.OKBLUE + str(text) + bcolors.OKBLUE)

# Input arguments ########################################
parser = argparse.ArgumentParser()
parser.add_argument("ip", help="IP address for binding the receiver TCP socket")
parser.add_argument("port", help="Port for binding the receiver TCP socket", type=int)
parser.add_argument("-b", "--buffer_size", help="The buffer size for incoming and outgoing sockets", type=int, default=1500)
args = parser.parse_args()
print(args)
##########################################################

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect( (args.ip, args.port) )
sleep(0.1)

for i in range(10):
    message_timestamp = time()
    bytearray_message_timestamp = struct.pack('<d', message_timestamp)
    sock.sendall(bytearray_message_timestamp)
    timestamp_envio = time()
    print(f"[SEND] TS mensaje: {message_timestamp:.7f}    Envío: {timestamp_envio:.7f}    Desfase envio: {(timestamp_envio - message_timestamp):.7f}")
    sleep(0.001)
    data = sock.recv(args.buffer_size)
    message_timestamp = struct.unpack('<d', data)[0]
    print(f"[RECV] TS mensaje: {message_timestamp:.7f}")

# Close socket
sock.sendall(bytearray("exit", "utf8"))
print(f"[SEND] End!")
sock.close()