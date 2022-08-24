import os
import time
from subprocess import Popen, PIPE
from signal import SIGTERM

from stem import Signal
from stem.control import Controller
from fastapi import FastAPI
from uvicorn import run
import psutil as psutil


app = FastAPI()
popen = None
popen_logs = []


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


@app.get('/proxy/logs')
def logs():
    return {'logs': popen_logs}


@app.post('/proxy')
def start():
    global popen
    print('Starting proxy...')
    popen = Popen(
        '/usr/bin/tor -f /etc/tor/torrc',
        stdout=PIPE,
        stderr=PIPE,
        shell=True
    )

    i = 0
    while i < 30:
        output = popen.stdout.readline().decode('utf-8')
        if output == '':
            continue

        print(output)
        popen_logs.append(output)
        if 'Bootstrapped 100%' in output:
            print('Proxy started')
            return {'status': 'ok'}

    # for i in range(10):
    #     res = popen.communicate()
    #     print(f'POPEN COMMUNICATE :: {res}')
    #     time.sleep(1)


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
    run('main:app', host='0.0.0.0', port=9000, reload=True)

