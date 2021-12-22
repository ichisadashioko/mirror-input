import io
import socket
import traceback

import mss

DEFAULT_SERVER_PORT = 43567

START_KEY = 'o'
PAUSE_KEY = 'p'

ALLOWED_KEYS = [
    'w', 'a', 's', 'd',
    'q', 'e', 'r', ' ',
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


class MirrorInputClient:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.message_queue = []
        self.alive = True

    def send_messages(self):
        if len(self.message_queue) == 0:
            return

        current_message_queue = self.message_queue
        self.message_queue = []

        byte_buffer = io.BytesIO()
        for message in current_message_queue:
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
