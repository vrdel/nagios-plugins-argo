#!/usr/bin/env python

import argparse
import socket
from nagios_plugins_argo.NagiosResponse import NagiosResponse

maxcmdlength = 128
timeout = 10


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='socket', required=True, type=str, help='AMS inspection socket')
    parser.add_argument('-q', dest='query', action='append', required=True, type=str, help='Query')
    parser.add_argument('-t', dest='threshold', action='append', required=True, type=str, help='Threshold')
    arguments = parser.parse_args()

    nr = NagiosResponse()

    if len(arguments.threshold) != len(arguments.query):
        nr.setCode(2)
        nr.writeCriticalMessage('Wrong arguments')
        print nr.getMsg()
        raise SystemExit(nr.getCode())

    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.setblocking(0)
        sock.settimeout(timeout)

        sock.connect(arguments.socket)
        sock.send(' '.join(arguments.query), maxcmdlength)
        data = sock.recv(maxcmdlength)

        print data

    except socket.timeout as e:
        nr.setCode(2)
        nr.writeCriticalMessage('Socket response timeout after {0}s'.format(timeout))
        print nr.getMsg()
        raise SystemExit(nr.getCode())

    except socket.error as e:
        nr.setCode(2)
        nr.writeCriticalMessage('Socket error: {0}'.format(str(e)))
        print nr.getMsg()
        raise SystemExit(nr.getCode())

    finally:
        sock.close()

if __name__ == "__main__":
    main()
