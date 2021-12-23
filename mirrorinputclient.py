import os
import socket
import argparse

from shared import *

parser = argparse.ArgumentParser(description='MirrorInputClient')
parser.add_argument('--host', type=str, default=DEFAULT_HOST, help='Hostname')
parser.add_argument('--port', type=int, default=DEFAULT_SERVER_PORT, help='Port')

args = parser.parse_args()
print('args', args)

# connect to server
socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('connecting to', args.host, args.port)
socket_connection.connect((args.host, args.port))
print('connected')

while True:
    msg = socket_connection.recv(1024)
    print(type(msg), msg)
    messages, remaining_bytes = deserialize_messages(msg)
    print(messages, len(remaining_bytes), remaining_bytes)
