import socket
import threading
import os

ENCODING = 'utf-8'
MESSAGE_LENGTH_SIZE = 64
class Node:
    def __init__(self, cluster_path, port):
        self.host = socket.gethostbyname(socket.gethostname())
        
        self.upd_port = port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.host, self.upd_port))

        self.tcp_port = self.get_free_tcp_port()
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((self.host, self.tcp_port))

        self.label = "N" + str(self.upd_port)
        if not os.path.exists(self.label):
            os.mkdir(self.label)        

        file = open(cluster_path, 'r')
        self.cluster = []
        for line in file:
            info = list(line.split())
            self.cluster.append(info)
        file.close()

    def client_handler(self):
        while True:
            input_string = input()
            print(input_string.split()[0])
            if input_string == 'DISCONNECT': 
                break
            elif len(input_string.split()) != 2:
                print("[ERROR]: Invalid request.")
            elif input_string.split()[0] != "GET":
                print("[ERROR]: Invalid request.")
            else:
                self.send_msg(input_string)

    def send_msg(self, msg):
        message = msg.encode(ENCODING)
        msg_length = len(message)
        msg_length = str(msg_length).encode(ENCODING)
        msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))

        if self.upd_port == 7755:
            self.udp_socket.sendto(msg_length, (self.host, 6655))
            self.udp_socket.sendto(message, (self.host, 6655))
        else:
            self.udp_socket.sendto(msg_length, (self.host, 7755))
            self.udp_socket.sendto(message, (self.host, 7755))

    def server_handler(self):
        while True:
            data, address = self.udp_socket.recvfrom(MESSAGE_LENGTH_SIZE)
            message_length = int(data.decode(ENCODING))
            msg = self.udp_socket.recvfrom(message_length)[0].decode(ENCODING)            
            print(msg)

            if os.path.isfile('./' + self.label + '/' + msg):
                self.send_msg(self.label + ": " + msg + " exists.")

    def discovery_handler(self):
        pass

    def run(self):
        client = threading.Thread(target=self.client_handler)
        client.start()

        server = threading.Thread(target=self.server_handler)
        server.start()

        # server.join()
        # discovery = threading.Thread(target=self.discovery_handler, args=(client, ))
        # discovery.start()

    def get_free_tcp_port(self):
        tmp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmp_socket.bind(('', 0))
        address, port = tmp_socket.getsockname()
        tmp_socket.close()
        return port