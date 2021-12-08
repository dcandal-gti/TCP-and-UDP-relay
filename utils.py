class Result:
    def __init__(self, message, counter, rcv_timestamp, snd_timestamp, data_length, from_addr, to_addr):
        self.message = message
        self.counter = counter
        self.rcv_timestamp = rcv_timestamp
        self.snd_timestamp = snd_timestamp
        self.data_length = data_length
        self.from_addr = from_addr
        self.to_addr = to_addr
    def __str__(self):
        return f"[{self.message}]    {self.counter:07}    {self.data_length:05}    {self.from_addr:26}    {self.rcv_timestamp:.7f}    {self.to_addr:26}    {self.snd_timestamp:.7f}"


def read_results_files(prefix = ""):
    path = "results/"
    client_relay_to_app_results = []
    client_app_to_relay_results = []
    server_relay_to_app_results = []
    server_app_to_relay_results = []

    with open(path + prefix + "client-relay_relay-to-app.txt") as reader:
        for line in reader:
            values = line.split("    ")
            client_relay_to_app_results.append( Result(values[0], int(values[1]), float(values[4]), float(values[6]), int(values[2]), values[3], values[5]) )

    with open(path + prefix + "client-relay_app-to-relay.txt") as reader:
        for line in reader:
            values = line.split("    ")
            client_app_to_relay_results.append( Result(values[0], int(values[1]), float(values[4]), float(values[6]), int(values[2]), values[3], values[5]) )

    with open(path + prefix + "server-relay_relay-to-app.txt") as reader:
        for line in reader:
            values = line.split("    ")
            server_relay_to_app_results.append( Result(values[0], int(values[1]), float(values[4]), float(values[6]), int(values[2]), values[3], values[5]) )

    with open(path + prefix + "server-relay_app-to-relay.txt") as reader:
        for line in reader:
            values = line.split("    ")
            server_app_to_relay_results.append( Result(values[0], int(values[1]), float(values[4]), float(values[6]), int(values[2]), values[3], values[5]) )

    return client_relay_to_app_results, client_app_to_relay_results, server_relay_to_app_results, server_app_to_relay_results


if __name__ == "__main__":
    prefix = "UDP_"
    client_relay_to_app_results, client_app_to_relay_results, server_relay_to_app_results, server_app_to_relay_results = read_results_files(prefix)

    # for result in client_relay_to_app_results:
    #     print(result.__dict__)
    # for result in client_app_to_relay_results:
    #     print(result.__dict__)
    # for result in server_relay_to_app_results:
    #     print(result.__dict__)
    # for result in server_app_to_relay_results:
    #     print(result.__dict__)

    for server_app_to_relay_result, client_relay_to_app_result in zip(server_app_to_relay_results, client_relay_to_app_results):
        if (server_app_to_relay_result.counter != client_relay_to_app_result.counter or server_app_to_relay_result.data_length != client_relay_to_app_result.data_length):
            print(f"Los paquetes no cuadran!!!!: {server_app_to_relay_result.counter} - {client_relay_to_app_result.counter} - {server_app_to_relay_result.data_length} - {client_relay_to_app_result.data_length}")
        print(f"{(client_relay_to_app_result.rcv_timestamp - server_app_to_relay_result.snd_timestamp):.25f} - {client_relay_to_app_result.rcv_timestamp:.25f} - {server_app_to_relay_result.snd_timestamp:.25f}")
