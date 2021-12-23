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


def on_click(x, y, button, pressed):
    print(time.time(), 'on_click', x, y, button, pressed)


def on_move(x, y):
    print(time.time(), 'on_move', x, y)


mouse_listener = pynput.mouse.Listener(on_click=on_click, on_move=on_move)
mouse_listener.start()
mouse_listener.join()
