#!/usr/bin/env python3
import flask
import requests
from flask_uwsgi_websocket import WebSocket
import datetime
import os
import uuid
import time
import threading

app = flask.Flask(__name__)
ws = WebSocket(app)


class SocketHandler:

    def __init__(self, socket):
        self.socket = socket
        self.listeners = []

    def receive(self):
        while True:
            data = self.socket.receive()
            if data is not None:
                print(data)
                for listener in self.listeners:
                    listener.handle(data)
            else:
                return

    def add_listener(self, listener):
        self.listeners.append(listener)


class FileListener:

    def __init__(self, path):
        self.fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)

    def handle(self, data):
        os.write(self.fd, data)
        os.fsync(self.fd)

script = [
    'ifconfig',
    'sleep 5',
    'apk add python3',
    'ping 8.8.8.8 -c 20',
]


@app.route('/', methods=['GET'])
def index():
    secret = uuid.uuid4().hex.replace('-', '')
    build = {
        'secret': secret,
        'script': script,
    }

    def async_request(_build):
        requests.post('http://localhost:5555/task', json=_build)

    threading.Thread(target=async_request, kwargs={'_build': build}).start()

    return flask.render_template('build.html', secret=secret)


@ws.route('/write-build-log')
def write_build_log(socket):
    with app.request_context(socket.environ):
        args = flask.request.args
        secret = args['secret']
        idx = args['idx']

    handler = SocketHandler(socket)
    file_listener = FileListener(os.path.join('build', secret + '.' + idx))
    handler.add_listener(file_listener)
    handler.receive()


@ws.route('/read-build-log')
def read_build_log(socket):
    with app.request_context(socket.environ):
        args = flask.request.args
        secret = args['secret']

    idx = 0
    fd = None

    # TMP hack: wait for first file
    while True:
        try:
            path = os.path.join('build', '{}.{}'.format(secret, idx))
            fd = os.open(path, os.O_RDONLY)
            break
        except OSError as e:
            print(e)
            time.sleep(.1)
            continue

    socket.send('{} {}\n'.format('$', script[idx]))

    while True:
        time.sleep(.1)
        output = os.read(fd, 1000)
        if output == b'':
            path = os.path.join('build', '{}.{}'.format(secret, idx + 1))
            if os.path.isfile(path):
                idx += 1
                os.close(fd)
                fd = os.open(path, os.O_RDONLY)
                socket.send('{} {}\n'.format('$', script[idx]))
            continue
        socket.send(output.decode('utf-8'))
