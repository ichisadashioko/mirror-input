import io
import socket
import traceback
import time

import mss

DEFAULT_HOST = '127.0.0.1'
DEFAULT_SERVER_PORT = 65432

START_KEY = 'o'
PAUSE_KEY = 'p'

ALLOWED_KEYS = [
    'w', 'a', 's', 'd',
    'q', 'e', 'r',
]

KEY_PRESS_CODE = 0
KEY_RELEASE_CODE = 1
LEFT_MOUSE_DOWN_CODE = 2
LEFT_MOUSE_UP_CODE = 3
RIGHT_MOUSE_DOWN_CODE = 4
RIGHT_MOUSE_UP_CODE = 5
MOUSE_MOVE_CODE = 6
SCREEN_INFO_CODE = 7


def get_screen_info():
    with mss.mss() as sct:
        screen_region = sct.monitors[1]
        return screen_region['width'], screen_region['height']


def serialize_message(message):
    byte_buffer = io.BytesIO()
    if message['type'] == SCREEN_INFO_CODE:
        byte_buffer.write(SCREEN_INFO_CODE.to_bytes(1, 'little'))
        byte_buffer.write(message['width'].to_bytes(4, 'little'))
        byte_buffer.write(message['height'].to_bytes(4, 'little'))
    elif message['type'] == KEY_PRESS_CODE:
        byte_buffer.write(KEY_PRESS_CODE.to_bytes(1, 'little'))
        byte_buffer.write(message['key'].encode('utf-8'))
    elif message['type'] == KEY_RELEASE_CODE:
        byte_buffer.write(KEY_RELEASE_CODE.to_bytes(1, 'little'))
        byte_buffer.write(message['key'].encode('utf-8'))
    elif message['type'] == LEFT_MOUSE_DOWN_CODE:
        byte_buffer.write(LEFT_MOUSE_DOWN_CODE.to_bytes(1, 'little'))
        byte_buffer.write(message['x'].to_bytes(4, 'little'))
        byte_buffer.write(message['y'].to_bytes(4, 'little'))
    elif message['type'] == LEFT_MOUSE_UP_CODE:
        byte_buffer.write(LEFT_MOUSE_UP_CODE.to_bytes(1, 'little'))
        byte_buffer.write(message['x'].to_bytes(4, 'little'))
        byte_buffer.write(message['y'].to_bytes(4, 'little'))
    elif message['type'] == RIGHT_MOUSE_DOWN_CODE:
        byte_buffer.write(RIGHT_MOUSE_DOWN_CODE.to_bytes(1, 'little'))
        byte_buffer.write(message['x'].to_bytes(4, 'little'))
        byte_buffer.write(message['y'].to_bytes(4, 'little'))
    elif message['type'] == RIGHT_MOUSE_UP_CODE:
        byte_buffer.write(RIGHT_MOUSE_UP_CODE.to_bytes(1, 'little'))
        byte_buffer.write(message['x'].to_bytes(4, 'little'))
        byte_buffer.write(message['y'].to_bytes(4, 'little'))
    elif message['type'] == MOUSE_MOVE_CODE:
        byte_buffer.write(MOUSE_MOVE_CODE.to_bytes(1, 'little'))
        byte_buffer.write(message['x'].to_bytes(4, 'little'))
        byte_buffer.write(message['y'].to_bytes(4, 'little'))
    return byte_buffer.getvalue()


def deserialize_messages(bs: bytes):
    byte_buffer = io.BytesIO(bs)
    messages = []
    seek_index = 0
    while True:
        message_type = byte_buffer.read(1)
        if message_type == b'':
            break
        # TODO

        message = {'type': byte_buffer.read(1)[0]}
        if message['type'] == KEY_PRESS_CODE:
            message['key'] = byte_buffer.read(1)
        elif message['type'] == KEY_RELEASE_CODE:
            message['key'] = byte_buffer.read(1)
        elif message['type'] == LEFT_MOUSE_DOWN_CODE:
            message['x'] = byte_buffer.read(4)
            message['y'] = byte_buffer.read(4)
        elif message['type'] == LEFT_MOUSE_UP_CODE:
            message['x'] = byte_buffer.read(4)
            message['y'] = byte_buffer.read(4)
        elif message['type'] == RIGHT_MOUSE_DOWN_CODE:
            message['x'] = byte_buffer.read(4)
            message['y'] = byte_buffer.read(4)
        elif message['type'] == RIGHT_MOUSE_UP_CODE:
            message['x'] = byte_buffer.read(4)
            message['y'] = byte_buffer.read(4)
        elif message['type'] == MOUSE_MOVE_CODE:
            message['x'] = byte_buffer.read(4)
            message['y'] = byte_buffer.read(4)
        elif message['type'] == SCREEN_INFO_CODE:
            message['width'] = byte_buffer.read(4)
            message['height'] = byte_buffer.read(4)
        messages.append(message)


class MirrorInputClient:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.message_queue = []
        self.alive = True
        self.daemon_thread_handle = None

    def send_messages(self):
        print(time.time(), len(self.message_queue), self.alive)
        if len(self.message_queue) == 0:
            time.sleep(0.01)
            return

        current_message_queue = self.message_queue
        self.message_queue = []

        byte_buffer = io.BytesIO()
        for message in current_message_queue:
            byte_buffer.write(serialize_message(message))
        self.socket.send(byte_buffer.getvalue())

    def daemon_thread(self):
        while self.alive:
            try:
                self.send_messages()
            except Exception as e:
                self.alive = False
                traceback_str = traceback.format_exc()
                print(e)
                print(traceback_str)

        # try to clean up the socket
        try:
            self.socket.close()
        except Exception as e:
            traceback_str = traceback.format_exc()
            print(e)
            print(traceback_str)
