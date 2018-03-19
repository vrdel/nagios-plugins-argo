#!/usr/bin/env python

import argparse
import sys, socket, select
from nagios_plugins_argo.NagiosResponse import NagiosResponse

maxcmdlength = 128


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='socket', required=True, type=str, help='AMS inspection socket')
    parser.add_argument('-q', dest='query', action='append', required=True, type=str, help='Query')
    arguments = parser.parse_args()

    nr = NagiosResponse()

    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(arguments.socket)
        sock.send(' '.join(arguments.query), maxcmdlength)
        data = sock.recv(maxcmdlength)
        print data
        sock.close()
    except socket.error as e:
        nr.setCode(2)
        nr.writeCriticalMessage(str(e))
        print nr.getMsg()
        raise SystemExit(nr.getCode())

if __name__ == "__main__":
    main()
