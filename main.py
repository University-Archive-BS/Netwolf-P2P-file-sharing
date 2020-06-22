from node import Node
import sys
import threading

UDP_PORT = 6431
DISCOVERY_PERIOD = 2

def main():
    # me = Node(cluster_path=sys.argv[1], port=UDP_PORT)
    me = Node(cluster_path=sys.argv[1], port=int(sys.argv[2]))
    me.run()

if __name__ == '__main__':
    main()