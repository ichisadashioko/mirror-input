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


def unblock_listen():
    # start a new socket connection to the server to unblock the listen call
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((DEFAULT_SERVER_PORT, DEFAULT_SERVER_PORT))
    s.close()


def handle_keyboard_input(key, released=False):
    global PAUSE_FLAG, STOP_FLAG

    if key == pynput.keyboard.Key.esc:
        # Stop listener
        STOP_FLAG = True

        threading.Thread(target=unblock_listen).start()
        return False

    if key == pynput.keyboard.Key.space:
        event_type = None
        if released:
            event_type = KEY_RELEASE_CODE
        else:
            event_type = KEY_PRESS_CODE
        for client in client_list:
            if client.alive:
                client.message_queue.append({
                    'type': event_type,
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
                client.message_queue.append({
                    'type': event_type,
                    'key': key_char,
                })


def on_press(key):
    return handle_keyboard_input(key)


def on_release(key):
    return handle_keyboard_input(key, True)


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
    thread = threading.Thread(target=client.daemon_thread)
    client.daemon_thread_handle = thread
    thread.start()


keyboard_listener.stop()

# clean up the client list
for client in client_list:
    print(client.address)
    try:
        if client.alive:
            client.alive = False
            # client.socket.close()
            # TODO: wait for the thread to finish
    except Exception as e:
        traceback_str = traceback.format_exc()
        print(e)
        print(traceback_str)
