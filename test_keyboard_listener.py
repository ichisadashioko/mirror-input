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


def handle_keyboard_input(key, released=False):
    global PAUSE_FLAG, STOP_FLAG
    print(time.time(), key, released)

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
    print('key_char', key_char)


def on_press(key):
    return handle_keyboard_input(key)


def on_release(key):
    return handle_keyboard_input(key, True)


keyboard_listener = pynput.keyboard.Listener(on_press=on_press, on_release=on_release)
keyboard_listener.start()
keyboard_listener.join()
