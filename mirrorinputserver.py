import os
import io
import time
import threading
import traceback
import argparse

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

# create a thread that listen to keyboard input


def handle_keyboard_input(key, released=False):
    global PAUSE_FLAG, STOP_FLAG

    if key == pynput.keyboard.Key.esc:
        # Stop listener
        STOP_FLAG = True
        return False

    key_char = None

    try:
        key_char = key.char
    except AttributeError:
        pass

    if key_char is None:
        return

    key_char = key_char.lower()
    if key_char == PAUSE_KEY:
        if released:
            PAUSE_FLAG = not PAUSE_FLAG
            print(time.time(), 'PAUSE_FLAG:', PAUSE_FLAG)
    elif key_char in ALLOWED_KEYS:
        event_type = None
        if released:
            event_type = KEY_RELEASE_CODE
        else:
            event_type = KEY_PRESS_CODE
        for client in client_list:
            if client.alive:
                client.message_queue.add({
                    'type': event_type,
                    'key': key_char,
                })


def on_press(key):
    return handle_keyboard_input(key)


def on_release(key):
    return handle_keyboard_input(key, True)


keyboard_listener = pynput.keyboard.Listener(on_press=on_press, on_release=on_release)
keyboard_listener.start()
keyboard_listener.join()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', DEFAULT_SERVER_PORT))

while (not STOP_FLAG) and (not os.path.exists('stop')):
    server_socket.listen()
    client_socket, client_address = server_socket.accept()

    print(time.time(), 'Accepted connection from', client_address)

    client = MirrorInputClient(client_socket, client_address)
    client_list.append(client)
    thread = threading.Thread(target=client.daemon_thread)
    thread.start()


keyboard_listener.stop()
