import os
from subprocess import Popen
from signal import SIGTERM

from stem import Signal
from stem.control import Controller
from fastapi import FastAPI
from uvicorn import run
import psutil as psutil


app = FastAPI()


def is_port_open(port):
    connection = get_connection_by_port(port)
    return not connection


def get_pid_by_port(port):
    connection = get_connection_by_port(port)
    return connection.pid


def get_connection_by_port(port):
    connections = psutil.net_connections()
    for connection in connections:
        if getattr(connection.laddr, 'port', None) == port:
            return connection


def request_new_identity():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)


@app.get('/proxy/status')
def status():
    return {'is_running': not is_port_open(9050)}


@app.post('/proxy')
def start():
    print('Starting proxy...')
    Popen('/usr/bin/tor -f /etc/tor/torrc', shell=True)


@app.post('/proxy/identity')
def refresh_identity():
    print('Requesting new identity...')
    request_new_identity()


@app.delete('/proxy')
def terminate():
    print('Stopping proxy...')
    pid = get_pid_by_port(9050)
    if pid:
        print(f'PID retrieved: {pid}. Stopping proxy now ...')
        os.kill(pid, SIGTERM)
        print('Process stopped!')


if __name__ == '__main__':
    run('main:app', host='0.0.0.0', port=7995, reload=True)
