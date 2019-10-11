#!/usr/bin/env python

from OpenSSL.SSL import TLSv1_METHOD, Context, Connection
from OpenSSL.SSL import VERIFY_PEER
from OpenSSL.SSL import Error as PyOpenSSLError
from OpenSSL.SSL import WantReadError as SSLWantReadError

import requests
import argparse

import datetime
import socket

from time import sleep

HOSTCERT = "/etc/grid-security/hostcert.pem"
HOSTKEY = "/etc/grid-security/hostkey.pem"
CAPATH = "/etc/grid-security/certificates/"

MIP_API = '/api/v2/metrics'

strerr = ''
num_excp_expand = 0
server_expire = None


def errmsg_from_excp(e):
    global strerr, num_excp_expand
    if isinstance(e, Exception) and getattr(e, 'args', False):
        num_excp_expand += 1
        if not errmsg_from_excp(e.args):
            return strerr
    elif isinstance(e, dict):
        for s in e.iteritems():
            errmsg_from_excp(s)
    elif isinstance(e, list):
        for s in e:
            errmsg_from_excp(s)
    elif isinstance(e, tuple):
        for s in e:
            errmsg_from_excp(s)
    elif isinstance(e, str):
        if num_excp_expand <= 5:
            strerr += e + ' '
    elif isinstance(e, int):
        if num_excp_expand <= 5:
            strerr += str(e) + ' '


def verify_servercert(host, timeout, capath):
    server_ctx = Context(TLSv1_METHOD)
    server_ctx.load_verify_locations(None, capath)
    server_cert_chain = []

    def verify_cb(conn, cert, errnum, depth, ok):
        server_cert_chain.append(cert)
        return ok
    server_ctx.set_verify(VERIFY_PEER, verify_cb)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(1)
    sock.settimeout(timeout)
    sock.connect((host, 443))

    server_conn = Connection(server_ctx, sock)
    server_conn.set_connect_state()

    def iosock_try():
        ok = True
        try:
            server_conn.do_handshake()
            sleep(0.5)
        except SSLWantReadError as e:
            ok = False
            pass
        except Exception as e:
            raise e
        return ok

    try:
        while True:
            if iosock_try():
                break

        global server_expire
        server_expire = server_cert_chain[-1].get_notAfter()

    except PyOpenSSLError as e:
        raise e
    finally:
        server_conn.shutdown()
        server_conn.close()

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', dest='hostname', required=True, type=str, help='hostname')
    parser.add_argument('-r', dest='profile', required=True, type=str, help='profile name')
    parser.add_argument('--cert', dest='cert', default=HOSTCERT, type=str, help='Certificate')
    parser.add_argument('--key', dest='key', default=HOSTKEY, type=str, help='Certificate key')
    parser.add_argument('--capath', dest='capath', default=CAPATH, type=str, help='CA directory')
    parser.add_argument('--token', dest='token', required=True, type=str, help='API token')
    parser.add_argument('-t', dest='timeout', required=True, type=int, default=180)
    arguments = parser.parse_args()

    # verify server certificate
    try:
        verify_servercert(arguments.hostname, arguments.timeout, arguments.capath)
    except PyOpenSSLError as e:
        print "CRITICAL - Server certificate verification failed: %s" % errmsg_from_excp(e)
        raise SystemExit(2)
    except socket.error as e:
        print "CRITICAL - Connection error: %s" % errmsg_from_excp(e)
        raise SystemExit(2)
    except socket.timeout as e:
        print "CRITICAL - Connection timeout after %s seconds" % arguments.timeout
        raise SystemExit(2)

    # verify client certificate
    try:
        requests.get('https://' + arguments.hostname + '/poem/', cert=(arguments.cert, arguments.key), verify=True)
    except requests.exceptions.RequestException as e:
        print "CRITICAL - Client certificate verification failed: %s" % errmsg_from_excp(e)
        raise SystemExit(2)

    try:
        headers = {'x-api-key': arguments.token}
        metrics = requests.get('https://' + arguments.hostname + MIP_API,
                               headers=headers, cert=(arguments.cert,
                                                      arguments.key),
                               verify=True)
        metrics.json()
    except requests.exceptions.RequestException as e:
        print 'CRITICAL - cannot connect to %s: %s' % ('https://' + arguments.hostname + MIP_API,
                                                       errmsg_from_excp(e))
        raise SystemExit(2)
    except ValueError as e:
        print 'CRITICAL - %s - %s' % (MIP_API, errmsg_from_excp(e))
        raise SystemExit(2)

    global server_expire
    dte = datetime.datetime.strptime(server_expire, '%Y%m%d%H%M%SZ')
    dtn = datetime.datetime.now()
    if (dte - dtn).days <= 15:
        print 'WARNING - Server certificate will expire in %i days' % (dte - dtn).days
        raise SystemExit(1)

    raise SystemExit(0)

if __name__ == "__main__":
    main()
