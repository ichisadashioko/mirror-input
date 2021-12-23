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

KEY_EVENT_CODE_LIST = [KEY_PRESS_CODE, KEY_RELEASE_CODE]
MOUSE_EVENT_CODE_LIST = [
    LEFT_MOUSE_DOWN_CODE, LEFT_MOUSE_UP_CODE,
    RIGHT_MOUSE_DOWN_CODE, RIGHT_MOUSE_UP_CODE,
    MOUSE_MOVE_CODE,
]


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


def deserialize_messages(input_bs: bytes):
    # loop through each byte in the buffer
    # if the remaining bytes is not enough to deserialize a message, return the remaining bytes

    byte_buffer = io.BytesIO(input_bs)
    messages = []
    processing_buffer = io.BytesIO()

    while True:
        if byte_buffer.tell() >= len(input_bs):
            break

        bs = byte_buffer.read(1)
        if len(bs) == 0:
            break

        processing_buffer.write(bs)
        message_type = int.from_bytes(bs, 'little')

        if message_type == SCREEN_INFO_CODE:
            bs = byte_buffer.read(4)
            processing_buffer.write(bs)
            if len(bs) < 4:
                break
            width = int.from_bytes(bs, 'little')
            bs = byte_buffer.read(4)
            processing_buffer.write(bs)
            if len(bs) < 4:
                break
            height = int.from_bytes(bs, 'little')
            messages.append({
                'type': message_type,
                'width': width,
                'height': height,
            })
            processing_buffer = io.BytesIO()
        elif message_type in KEY_EVENT_CODE_LIST:
            bs = byte_buffer.read(1)
            processing_buffer.write(bs)
            if len(bs) < 1:
                break
            key = bs.decode('utf-8')
            messages.append({
                'type': message_type,
                'key': key,
            })
            processing_buffer = io.BytesIO()
        elif message_type in MOUSE_EVENT_CODE_LIST:
            bs = byte_buffer.read(4)
            processing_buffer.write(bs)
            if len(bs) < 4:
                break
            x = int.from_bytes(bs, 'little')
            bs = byte_buffer.read(4)
            processing_buffer.write(bs)
            if len(bs) < 4:
                break
            y = int.from_bytes(bs, 'little')
            messages.append({
                'type': message_type,
                'x': x,
                'y': y,
            })
            processing_buffer = io.BytesIO()
        else:
            # TODO: handle error
            print('unknown message type', message_type)
            break
    remaining_bytes = processing_buffer.getvalue()
    remaining_bytes += byte_buffer.read()
    return messages, remaining_bytes


class MirrorInputClient:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.message_queue = []
        self.alive = True
        self.daemon_thread_handle = None

    def send_messages(self):
        print(time.time(), len(self.message_queue), self.alive, end='\r')
        if len(self.message_queue) == 0:
            time.sleep(0.01)
            return

        current_message_queue = self.message_queue
        self.message_queue = []

        byte_buffer = io.BytesIO()
        for message in current_message_queue:
            byte_buffer.write(serialize_message(message))
        self.socket.send(byte_buffer.getvalue())


def handle_client_thread(client: MirrorInputClient):
    while client.alive:
        try:
            client.send_messages()
        except Exception as e:
            client.alive = False
            traceback_str = traceback.format_exc()
            print(e)
            print(traceback_str)

    # try to clean up the socket
    try:
        client.socket.close()
    except Exception as e:
        traceback_str = traceback.format_exc()
        print(e)
        print(traceback_str)
