import os
import socket
import argparse

from shared import *

parser = argparse.ArgumentParser(description='MirrorInputClient')
parser.add_argument('--host', type=str, default='127.0.0.1', help='Hostname')
parser.add_argument('--port', type=int, default=DEFAULT_SERVER_PORT, help='Port')

args = parser.parse_args()
print('args', args)

# connect to server
socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_connection.connect((args.host, args.port))

while True:
    msg = socket_connection.recv(1024)
    print(type(msg), msg)
