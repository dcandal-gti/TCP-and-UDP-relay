import socket
from time import time, sleep
import argparse
import multiprocessing
from signal import signal, SIGINT
from os import makedirs, path
from utils import Result
from subprocess import Popen as sp_Popen, PIPE as sp_PIPE, call as sp_call

# Input arguments ########################################
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description = '''\
        +------------+             +--------------+             +--------------+             +------------+
        | Client APP |<----------->| Server relay |<----------->| Client relay |<----------->| Server APP |
        +------------+             +--------------+             +--------------+             +------------+
                CA_addr          SRA_addr    SRR_addr         CRR_addr    CRA_addr          SA_addr

        Entities:
            - Server APP: The software that listens for the connection.
            - Client APP: The software that establishes the connection with the Server APP.
            - Client relay: Establishes a connection with the Server APP, and then listens for a connection with the Server relay.
            - Server relay: Establishes a connection with the Client relay, and then listens for a connection with the Client APP.

        Network architecture example:
            - Server APP:   IP: 10.20.0.4, Listening at: 0.0.0.0:5000
            - Client relay: IP: 10.20.0.3, Connects to: 10.20.0.4:5000,  Listening at: 0.0.0.0:60000
            - Server relay: IP: 10.20.0.2, Connects to: 10.20.0.3:60000, Listening at: 0.0.0.0:5000
            - Client APP:   IP: 10.20.0.1, Connects to: 10.20.0.2:5000

        To recreate this architecture, run the software in this order:
        1.- Server_APP (listening at 10.20.0.4:5000)
        2.- Client_relay: python3 relay_tcp.py -ca SA_ip SA_port CRR_ip  (ej: python3 relay_tcp.py -ca 10.20.0.4 5000 0.0.0.0 2>/dev/null)
        3.- Server_relay: python3 relay_tcp.py -c SRA_ip SRA_port CRR_ip (ej: python3 relay_tcp.py -c 0.0.0.0 5000 10.20.0.3 2>/dev/null)
        4.- Client_APP (conecting to 10.20.0.2:5000)
    '''
)
parser.add_argument("-ca", "--client_app", help="If seelected, the relay app acts as client to the external app", action="store_true", default=False)
parser.add_argument("-c", "--client", help="If selected, the relay app acts as client to the other relay app", action="store_true", default=False)

parser.add_argument("app_IP", help="IP address for receiving/transmitting traffic to the external app (depending of if the relay is the client or server for this connection)")
parser.add_argument("app_port", help="Port for receiving/transmitting traffic to the external app (depending of if the relay is the client or server for this connection)", type=int)
parser.add_argument("relay_IP", help="IP address of the server relay host")
parser.add_argument("--relay_port", help="The port used at the server relay app for receiving traffic", type=int, default=50000)

parser.add_argument("-b", "--buffer_size", help="The buffer size for incoming and outgoing sockets", type=int, default=1500)
args = parser.parse_args()
print(args)
##########################################################


# Network setup ################################################################################################################################
def setup_relay_socket():# Configuración de las conexiones para el relay del tráfico
    relay_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.AF_INET==IPv4, socket.SOCK_STREAM=TCP
    if args.client:
        relay_sock.connect( (args.relay_IP, args.relay_port) )
        relay = relay_sock
    else:
        relay_sock.bind( (args.relay_IP, args.relay_port) )
        relay_sock.listen(1)
        connection_relay, _ = relay_sock.accept()
        relay = connection_relay
    return relay, relay_sock

def setup_app_socket():# Configuración de las conexiones con la app de la que se quiere reenviar tráfico
    app_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.AF_INET==IPv4, socket.SOCK_STREAM=TCP
    if args.client_app:
        app_sock.connect( (args.app_IP, args.app_port) )
        app = app_sock
    else:
        app_sock.bind( (args.app_IP, args.app_port) )
        app_sock.listen(1)
        connection_app, _ = app_sock.accept()
        app = connection_app
    return app, app_sock

def run_tcpdump(app_port, relay_port):
    if not path.exists('results'):
        makedirs('results')
    process1 = sp_Popen(f"tcpdump -i any tcp port {relay_port} -w results/TCP_{'client-relay' if args.client_app else 'server-relay'}_relay.pcap".split(), stdout=sp_PIPE, stderr=sp_PIPE)
    process2 = sp_Popen(f"tcpdump -i any tcp port {app_port} -w results/TCP_{'client-relay' if args.client_app else 'server-relay'}_app.pcap".split(), stdout=sp_PIPE, stderr=sp_PIPE)
    return process1, process2

def kill_tcpdump(tcpdump_processes):
    sleep(1)
    for p in tcpdump_processes:
        p.terminate()
# End of traffic processing ####################################################################################################################


# Traffic processing ###########################################################################################################################
def relay_traffic(from_, to_, results, message=""):
    counter = 0
    while True:
        data = from_.recv(args.buffer_size)
        rcv_timestamp = time()
        if data:
            to_.sendall(data)
            snd_timestamp = time()
            #results.append(Result(message, counter, rcv_timestamp, snd_timestamp, len(data), str(from_.getsockname()), str(to_.getpeername())))
            results.append(Result(message, counter, rcv_timestamp, snd_timestamp, len(data), f"{str(from_.getpeername())}->{str(from_.getsockname())}", f"{str(to_.getsockname())}->{str(to_.getpeername())}"))
            counter += 1
# End of traffic processing ####################################################################################################################


# Misc #########################################################################################################################################
class MySigIntHandler:
    def __init__(self, app, app_sock, relay, relay_sock, relay_to_app, app_to_relay, relay_to_app_results, app_to_relay_results, tcpdump_processes):
        self.app = app
        self.app_sock = app_sock
        self.relay = relay
        self.relay_sock = relay_sock
        self.relay_to_app = relay_to_app
        self.app_to_relay = app_to_relay
        self.lock = multiprocessing.Lock()
        self.closing = False
        self.relay_to_app_results = relay_to_app_results
        self.app_to_relay_results = app_to_relay_results
        self.tcpdump_processes = tcpdump_processes

    def __call__(self, signo, frame):
        with self.lock:
            if not self.closing:
                # Closing
                self.closing = True
                self.app.close()
                self.app_sock.close()
                self.relay.close()
                self.relay_sock.close()
                if self.relay_to_app.is_alive():
                    self.relay_to_app.terminate()
                if self.app_to_relay.is_alive():
                    self.app_to_relay.terminate()
                kill_tcpdump(self.tcpdump_processes)
                # Saving results
                if not path.exists('results'):
                    makedirs('results')
                print("\n")
                with open(f"{'results/TCP_' + ('client-relay' if args.client_app else 'server-relay')}_relay-to-app.txt", 'w') as out:
                    for result in self.relay_to_app_results:
                        print(str(result))
                        out.write(str(result) + "\n")
                with open(f"{'results/TCP_' + ('client-relay' if args.client_app else 'server-relay')}_app-to-relay.txt", 'w') as out:
                    for result in self.app_to_relay_results:
                        print(str(result))
                        out.write(str(result) + "\n")
            
# End of misc #########################################################################################################################################


def main():
    tcpdump_processes = run_tcpdump(args.app_port, args.relay_port)
    relay, relay_sock = setup_relay_socket()
    app, app_sock = setup_app_socket()

    relay_to_app_results = multiprocessing.Manager().list()
    app_to_relay_results = multiprocessing.Manager().list()
    relay_to_app = multiprocessing.Process(target=relay_traffic, args=(relay, app, relay_to_app_results, "relay->app",))
    app_to_relay = multiprocessing.Process(target=relay_traffic, args=(app, relay, app_to_relay_results, "app->relay",))
    relay_to_app.start()
    app_to_relay.start()

    signal(SIGINT, MySigIntHandler(app, app_sock, relay, relay_sock, relay_to_app, app_to_relay, relay_to_app_results, app_to_relay_results, tcpdump_processes))

    relay_to_app.join()
    app_to_relay.join()
    app.close()
    relay.close()

if __name__ == "__main__":
    main()