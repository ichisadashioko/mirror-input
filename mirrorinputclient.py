import os
import socket
import argparse

import pynput
import pynput.keyboard
import pynput.mouse

from shared import *


keyboard_controller = pynput.keyboard.Controller()
mouse_controller = pynput.mouse.Controller()


def execute_input_message(message):
    # TODO handle this
    # if message['type'] == SCREEN_INFO_CODE:
    #     screen_width, screen_height = get_screen_info()
    #     if (message['width'] != screen_width) or (message['height'] != screen_height):
    #         print('ERROR: screen dims do not match')
    #         raise Exception('screen dims do not match')

    if message['type'] == KEY_PRESS_CODE:
        key_char = message['key']
        if key_char == ' ':
            keyboard_controller.press(pynput.keyboard.Key.space)
        elif key_char in ALLOWED_KEYS:
            keyboard_controller.press(key_char)
    elif message['type'] == KEY_RELEASE_CODE:
        key_char = message['key']
        if key_char == ' ':
            keyboard_controller.release(pynput.keyboard.Key.space)
        elif key_char in ALLOWED_KEYS:
            keyboard_controller.release(key_char)
    elif message['type'] == LEFT_MOUSE_DOWN_CODE:
        mouse_controller.position = (message['x'], message['y'])
        mouse_controller.press(pynput.mouse.Button.left)
    elif message['type'] == LEFT_MOUSE_UP_CODE:
        mouse_controller.position = (message['x'], message['y'])
        mouse_controller.release(pynput.mouse.Button.left)
    elif message['type'] == RIGHT_MOUSE_DOWN_CODE:
        mouse_controller.position = (message['x'], message['y'])
        mouse_controller.press(pynput.mouse.Button.right)
    elif message['type'] == RIGHT_MOUSE_UP_CODE:
        mouse_controller.position = (message['x'], message['y'])
        mouse_controller.release(pynput.mouse.Button.right)
    elif message['type'] == MOUSE_MOVE_CODE:
        mouse_controller.position = (message['x'], message['y'])


parser = argparse.ArgumentParser(description='MirrorInputClient')
parser.add_argument('host', type=str, default=None, help='hostname', nargs='?')
parser.add_argument('port', type=int, default=DEFAULT_SERVER_PORT, help='port', nargs='?')

args = parser.parse_args()
print('args', args)

socket_connection = None
if args.host is None:
    # auto-detect host
    for i in range(255):
        hostname = f'192.168.0.{i}'
        try:
            socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('connecting to', hostname, args.port)
            socket_connection.connect((hostname, args.port))
        except:
            socket_connection = None
            continue
else:
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('connecting to', args.host, args.port)
    socket_connection.connect((args.host, args.port))

if socket_connection is None:
    print('Unable to connect to server')
    exit(1)

# connect to server
print('connected')


while True:
    msg = socket_connection.recv(1024)
    if len(msg) == 0:
        # TODO could we receive a message with length 0 that the server sends to keep the connection alive?
        print('connection closed')
        break

    # print(type(msg), msg)
    print(time.time(), len(msg), end='\r')
    messages, remaining_bytes = deserialize_messages(msg)
    # print(messages, len(remaining_bytes), remaining_bytes)
    for message in messages:
        execute_input_message(message)
    # TODO handle remaining_bytes
