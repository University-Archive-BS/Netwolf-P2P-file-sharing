import socket
import threading
import os

class Node:
    def __init__(self, cluster_path, port):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create a UDP socket
        self.host = socket.gethostbyname(socket.gethostname())
        self.upd_port = port
        self.udp_socket.bind((self.host, self.upd_port))
        self.ENCODING = 'utf-8'
        self.MESSAGE_LENGTH_SIZE = 64

        self.label = "N" + str(self.upd_port)
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
            if input_string == 'DISCONNECT': 
                break
            self.send_msg(input_string)

    def send_msg(self, msg):
        message = msg.encode(self.ENCODING)
        msg_length = len(message)
        msg_length = str(msg_length).encode(self.ENCODING)
        msg_length += b' ' * (self.MESSAGE_LENGTH_SIZE - len(msg_length))

        if self.upd_port == 7755:
            self.udp_socket.sendto(msg_length, (self.host, 6655))
            self.udp_socket.sendto(message, (self.host, 6655))
        else:
            self.udp_socket.sendto(msg_length, (self.host, 7755))
            self.udp_socket.sendto(message, (self.host, 7755))

    def server_handler(self):
        while True:
            data, address = self.udp_socket.recvfrom(self.MESSAGE_LENGTH_SIZE)
            message_length = int(data.decode(self.ENCODING))
            msg = self.udp_socket.recvfrom(message_length)[0].decode(self.ENCODING)            
            print(msg)

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
