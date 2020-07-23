import socket
import threading
import os
import time
import json
import sys

ENCODING = 'utf-8'
MESSAGE_LENGTH_SIZE = 64
class Node:
    def __init__(self, cluster_path, port):
        self.host = socket.gethostbyname(socket.gethostname())
        
        self.upd_port = port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.host, self.upd_port))    

        self.discovery_period = 3

        self.label = "N" + str(self.upd_port)
        if not os.path.exists(self.label):
            os.mkdir(self.label)        

        file = open(cluster_path, 'r')
        self.cluster = []
        for line in file:
            info = list(line.split())
            if int(info[0]) != self.upd_port:
                self.cluster.append(info[0])
        self.cluster.append(str(self.upd_port))
        file.close()

    def client_handler(self):
        while True:
            input_string = input()
            if input_string == 'DISCONNECT': 
                break
            elif len(input_string.split()) != 2:
                print("[ERROR]: Invalid request.")
            elif input_string.split()[0] != "GET":
                print("[ERROR]: Invalid request.")
            else:
                self.send_udp_msg(input_string)

    def send_udp_msg(self, msg=None, isDiscovery=False, port=False):
        if isDiscovery:
            message = json.dumps(self.cluster).encode(ENCODING)
            msg_length = len(message)
            msg_length = str(msg_length).encode(ENCODING)
            msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))
            for node in self.cluster:
                if int(node) != self.upd_port:
                    self.udp_socket.sendto(msg_length, (self.host, int(node)))
                    self.udp_socket.sendto(message, (self.host, int(node)))
        elif port != False:
            message = msg.encode(ENCODING)
            msg_length = len(message)
            msg_length = str(msg_length).encode(ENCODING)
            msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))

            self.udp_socket.sendto(msg_length, (self.host, port))
            self.udp_socket.sendto(message, (self.host, port))
        else:
            message = msg.encode(ENCODING)
            msg_length = len(message)
            msg_length = str(msg_length).encode(ENCODING)
            msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))

            for node in self.cluster:
                if int(node) != self.upd_port:
                    self.udp_socket.sendto(msg_length, (self.host, int(node)))
                    self.udp_socket.sendto(message, (self.host, int(node)))

    def server_handler(self):
        while True:
            data, address = self.udp_socket.recvfrom(MESSAGE_LENGTH_SIZE)
            message_length = int(data.decode(ENCODING))
            msg = self.udp_socket.recvfrom(message_length)[0].decode(ENCODING)   

            if msg.split()[0] == "GET":
                print(f"[MESSAGE]: N{str(address[1])} wants {msg.split()[1]}.")  
                if os.path.isfile('./' + self.label + '/' + msg.split()[1]):
                    port = self.get_free_port()
                    tcp_server = threading.Thread(target=self.file_server, args=(port,))
                    tcp_server.start()
                    self.send_udp_msg(msg=f"[MESSAGE]: {self.label} has {msg.split()[1]} and the TCP port is: {str(port)}", port=address[1])
            elif msg.split()[0] == "[MESSAGE]:":
                print(msg)
                tcp_client = threading.Thread(target=self.file_receiver, args=(msg.split()[3], int(msg.split()[-1])))
                tcp_client.start()
            elif str(self.upd_port) in json.loads(msg):
                for node in json.loads(msg):
                    if not node in self.cluster:
                        self.cluster.append(node)
            else:
                print(msg)

 
    def discovery_sender_handler(self):
        self.send_udp_msg(isDiscovery=True)
        threading.Timer(self.discovery_period, self.discovery_sender_handler).start()

    def run(self):
        udp_client = threading.Thread(target=self.client_handler)
        udp_client.start()

        udp_server = threading.Thread(target=self.server_handler)
        udp_server.daemon = True
        udp_server.start()

        discovery_sender = threading.Thread(target=self.discovery_sender_handler)
        discovery_sender.daemon = True
        discovery_sender.start()

        try:
            udp_client.join()
            udp_server._stop()
            discovery_sender._stop()
        except:
            sys.exit("Good luck!")

    def get_free_port(self):
        tmp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmp_socket.bind(('', 0))
        address, port = tmp_socket.getsockname()
        tmp_socket.close()
        return port

    def file_server(self, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, port))
        server.listen()

        connection, address = server.accept()
        message_length = int(connection.recv(MESSAGE_LENGTH_SIZE).decode(ENCODING))
        file_name = connection.recv(message_length).decode(ENCODING)

        f = open('./' + self.label + '/' + file_name,'rb')
        l = f.read(MESSAGE_LENGTH_SIZE)
        while (l):
            connection.send(l)
            l = f.read(MESSAGE_LENGTH_SIZE)
        f.close()
        print('[MESSAGE]: Finish sending ' + file_name + '.')
        
        connection.close()
        server.close()

    def file_receiver(self, file_name, port):
        receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receiver.connect((self.host, port))
        self.send_tcp_msg(file_name, receiver)

        f = open('./' + self.label + '/' + file_name, 'wb')
        while True:
            try:
                data = receiver.recv(MESSAGE_LENGTH_SIZE)
                if not data:
                    break
                f.write(data)
            except:
                pass

        f.close()
        print('[MESSAGE]: Finish receiving ' + file_name + '.')

        receiver.close()

    def send_tcp_msg(self, msg, conn):
        message = msg.encode(ENCODING)
        msg_length = len(message)
        msg_length = str(msg_length).encode(ENCODING)
        msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))

        conn.send(msg_length)
        conn.send(message)