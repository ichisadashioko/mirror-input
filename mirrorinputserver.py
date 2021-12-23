import os
import io
import time
import threading
import traceback
import argparse
import collections

import socket
import socketserver

import mss

import pynput
import pynput.keyboard
import pynput.mouse

from shared import *


client_list = []

PAUSE_FLAG = True
STOP_FLAG = False

keyboard_state_dict = collections.defaultdict(lambda: False)

# create a thread that listen to keyboard input


def unblock_listen():
    # start a new socket connection to the server to unblock the listen call
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((DEFAULT_HOST, DEFAULT_SERVER_PORT))
    s.close()


def on_press(key):
    global PAUSE_FLAG, STOP_FLAG

    if key == pynput.keyboard.Key.esc:
        # Stop listener
        STOP_FLAG = True

        threading.Thread(target=unblock_listen).start()
        return False

    if key == pynput.keyboard.Key.space:
        if keyboard_state_dict[key]:
            return

        keyboard_state_dict[key] = True
        for client in client_list:
            if client.alive:
                client.message_queue.append({
                    'type': KEY_PRESS_CODE,
                    'key': ' ',
                })

    key_char = None

    try:
        key_char = key.char
    except AttributeError:
        pass

    if key_char is None:
        return

    key_char = key_char.lower()
    if key_char == PAUSE_KEY:
        PAUSE_FLAG = not PAUSE_FLAG
        print(time.time(), 'PAUSE_FLAG:', PAUSE_FLAG)
    elif key_char in ALLOWED_KEYS:
        if keyboard_state_dict[key_char]:
            return

        keyboard_state_dict[key_char] = True
        for client in client_list:
            if client.alive:
                client.message_queue.append({
                    'type': KEY_PRESS_CODE,
                    'key': key_char,
                })


def on_release(key):
    if key == pynput.keyboard.Key.space:
        keyboard_state_dict[key] = False
        for client in client_list:
            if client.alive:
                client.message_queue.append({
                    'type': KEY_RELEASE_CODE,
                    'key': ' ',
                })

    key_char = None

    try:
        key_char = key.char
    except AttributeError:
        pass

    if key_char is None:
        return

    key_char = key_char.lower()
    if key_char in ALLOWED_KEYS:
        keyboard_state_dict[key_char] = False
        for client in client_list:
            if client.alive:
                client.message_queue.append({
                    'type': KEY_RELEASE_CODE,
                    'key': key_char,
                })


keyboard_listener = pynput.keyboard.Listener(on_press=on_press, on_release=on_release)
keyboard_listener.start()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((DEFAULT_HOST, DEFAULT_SERVER_PORT))

while (not STOP_FLAG) and (not os.path.exists('stop')):
    print('Waiting for connection...')
    server_socket.listen(1)
    client_socket, client_address = server_socket.accept()

    print(time.time(), 'Accepted connection from', client_address)

    client = MirrorInputClient(client_socket, client_address)
    client_list.append(client)
    thread = threading.Thread(target=handle_client_thread, args=(client,))
    client.daemon_thread_handle = thread
    thread.start()


keyboard_listener.stop()

# clean up the client list
for client in client_list:
    print(client.address)
    try:
        if client.alive:
            client.alive = False
            client.socket.close()
            # TODO: wait for the thread to finish
    except Exception as e:
        traceback_str = traceback.format_exc()
        print(e)
        print(traceback_str)
