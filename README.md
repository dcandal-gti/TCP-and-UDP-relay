# TCP and UDP relay

These scripts allow you to relay TCP or UDP traffic between two machines and take a network trace and meassurements of the data that is transmitted between them.

    +------------+             +--------------+             +--------------+             +------------+
    | Client APP |<----------->| Server relay |<----------->| Client relay |<----------->| Server APP |
    +------------+             +--------------+             +--------------+             +------------+
            CA_addr          SRA_addr    SRR_addr         CRR_addr    CRA_addr          SA_addr

The scripts "relay_tcp.py" and "relay_udp.py" alllow you to create two relays that interconnect two external applications. That is, the traffic that is sent by an application is transmitted to the other through the relays. Mesauraments and network traces are captured at those entities.

The scripts "sender_tcp.py", "receiver_tcp.py", "sender_udp.py" and "receiver_udp.py" are TCP and UDP clients and servers that can be used to test the relay scripts. The receiver scripts create a TCP or UDP socket and listen on an IP address and port that is configured through input arguments. The sender scripts create a socket that connects to the receiver's socket. The sender sends 10 messages to the receiver, which sends the received message back to the sender.


## Getting Started

### Prerequisites

You need to enable your user to capture traffic with tcpdump without superuser permissions. To do that, please run the script "tcpdump_without_sudo.sh".
  ```
  ./tcpdump_without_sudo.sh
  ```

### Usage

Consider the following entities:
- Server APP: The software that listens for the connection.
- Client APP: The software that establishes the connection with the Server APP.
- Client relay: Establishes a connection with the Server APP, and then listens for a connection with the Server relay.
- Server relay: Establishes a connection with the Client relay, and then listens for a connection with the Client APP.

For using the relay architecture, you need to run the software in the following order:
1. Server_APP
2. Client_relay: python3 relay_tcp.py/relay_udp.py -ca SA_ip SA_port CRR_ip
3. Server_relay: python3 relay_tcp.py/relay_udp.py -c SRA_ip SRA_port CRR_ip
4. Client_APP

Where SA_ip and SA_port are the IP address and port where the Server APP is listening, CRR_ip is the IP address where the Client relay is listening for traffic comming from the Server relay, and SRA_ip and SRA_port are the IP address and port where the Server relay is listening for the traffic comming from the Client APP.

We will take the following network architecture as an example:
- Server APP:   IP: 10.20.0.4, Listening at: 0.0.0.0:5000
- Client relay: IP: 10.20.0.3, Connects to: 10.20.0.4:5000,  Listening at: 0.0.0.0:60000
- Server relay: IP: 10.20.0.2, Connects to: 10.20.0.3:60000, Listening at: 0.0.0.0:5000
- Client APP:   IP: 10.20.0.1, Connects to: 10.20.0.2:5000

To recreate this architecture, you have to run:
1. Server_APP (ex: listening at 10.20.0.4:5000)
2. Client_relay: python3 relay_tcp.py/relay_udp.py -ca 10.20.0.4 5000 0.0.0.0 2>/dev/null
3. Server_relay: python3 relay_tcp.py/relay_udp.py -c 0.0.0.0 5000 10.20.0.3 2>/dev/null
4. Client_APP (ex: conecting to 10.20.0.2:5000)

To use the sender and receiver scripts, set as input arguments the ip address and port that the entity must use to bind or connect its socket. Considering the previous example:
- python3 receiver_tcp.py/receiver_udp.py 0.0.0.0 5000
- python3 sender_tcp.py/sender_udp.py 10.20.0.2 5000

## Copyright
Copyright ⓒ 2020 David Candal Ventureira dcandal@gti.uvigo.es.

This simulator is licensed under the GNU General Public License, version 3 (GPL-3.0). For more information see LICENSE.txt
