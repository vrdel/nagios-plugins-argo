#!/usr/bin/env python

import argparse
import socket
from nagios_plugins_argo.NagiosResponse import NagiosResponse

maxcmdlength = 128
timeout = 10

def parse_result(query):
    try:
        w, r = query.split('+')

        w = w.split(':')[1]
        r = int(r.split(':')[1])

    except (ValueError, KeyError):
        return (w, 'error')

    return (w, r)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='socket', required=True, type=str, help='AMS inspection socket')
    parser.add_argument('-q', dest='query', action='append', required=True, type=str, help='Query')
    parser.add_argument('-c', dest='threshold', action='append', required=True, type=int, help='Threshold')
    parser.add_argument('-t', dest='timeout', required=False, type=int, help='Timeout')
    arguments = parser.parse_args()

    nr = NagiosResponse()

    if len(arguments.threshold) != len(arguments.query):
        nr.setCode(2)
        nr.writeCriticalMessage('Wrong arguments')
        print nr.getMsg()
        raise SystemExit(nr.getCode())

    if arguments.timeout:
        timeo = arguments.timeout
    else:
        timeo = timeout

    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.setblocking(0)
        sock.settimeout(timeo)

        sock.connect(arguments.socket)
        sock.send(' '.join(arguments.query), maxcmdlength)
        data = sock.recv(maxcmdlength)

        lr = list()
        for r in data.split():
            lr.append(parse_result(r))

        error = False
        for e in lr:
            if e[1] == 'error':
                nr.setCode(2)
                nr.writeCriticalMessage('Worker {0} {1}'.format(e[0], e[1]))
                error = True
        if error:
            print nr.getMsg()
            raise SystemExit(nr.getCode())

        error = False
        nr.setCode(0)
        i = 0
        while i < len(lr):
            e = lr[i]
            if e[1] < arguments.threshold[i]:
                nr.setCode(2)
                nr.writeCriticalMessage('Worker {0} published {1} (threshold {2})'.format(e[0], e[1], arguments.threshold[i]))
                error = True
            i+=1

        if error:
            print nr.getMsg()
            raise SystemExit(nr.getCode())
        else:
            i = 0
            nr.setCode(0)
            while i < len(lr):
                e = lr[i]
                nr.writeOkMessage('Worker {0} published {1} (threshold {2})'.format(e[0], e[1], arguments.threshold[i]))
                i+=1

            print nr.getMsg()
            raise SystemExit(nr.getCode())


    except socket.timeout as e:
        nr.setCode(2)
        nr.writeCriticalMessage('Socket response timeout after {0}s'.format(timeo))
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
