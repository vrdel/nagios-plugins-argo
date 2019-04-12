#!/usr/bin/env python

from argparse import ArgumentParser
from NagiosResponse import NagiosResponse
import requests
from requests import exceptions


def main():

    parser = ArgumentParser(description="Nagios probe for monitoring the authentication service")

    parser.add_argument('--authn-host', dest='authn_host', type=str, required=True,
                        help='THe host of the authentication service')

    parser.add_argument('--authn-port', dest='authn_port', type=int, required=True,
                        help='THe port of the authentication service')

    parser.add_argument('--cert', dest='cert', type=str, required=True,
                        help='Path to the certificate')

    parser.add_argument('--key', dest='key', type=str, required=True,
                        help='Path to the certificate\'s key')

    parser.add_argument("--verify", dest='verify', help="SSL verification for requests", action="store_true")

    parser.add_argument("--verbose", dest='verbose', help="Error verbosity", action="store_true")

    subparsers = parser.add_subparsers(dest="service")

    # ams service arguments
    ams_parser = subparsers.add_parser("ams")

    ams_parser.add_argument('--ams-token', dest='ams_token', type=str, help='Expected ams token')

    ams_parser.add_argument('--ams-service', dest='ams_service', type=str, default="ams",
                            help='The name of the service in authn')

    ams_parser.add_argument('--ams-host', dest='ams_host', type=str, required=True, help='The ams host')

    # web-api service arguments
    webapi_parser = subparsers.add_parser("web-api")

    webapi_parser.add_argument('--webapi-token', dest='web_api_token', type=str,
                               help='Expected web-api token')

    webapi_parser.add_argument('--webapi-service', dest='web_api_service', type=str, default="web-api",
                               help='The name of the service in authn')

    webapi_parser.add_argument('--webapi-host', dest='web_api_host', type=str, required=True, help='The web-api host')

    # all services arguments
    all_parser = subparsers.add_parser("all")
    all_parser.add_argument('--ams-token', dest='ams_token', type=str, help='Expected ams token')

    all_parser.add_argument('--ams-service', dest='ams_service', type=str, default="ams",
                            help='The name of the service in authn')

    all_parser.add_argument('--ams-host', dest='ams_host', type=str, required=True, help='The ams host')

    all_parser.add_argument('--webapi-token', dest='web_api_token', type=str,
                            help='Expected web-api token')

    all_parser.add_argument('--webapi-service', dest='web_api_service', type=str, default="web-api",
                            help='The name of the service in authn')

    all_parser.add_argument('--webapi-host', dest='web_api_host', type=str, required=True, help='The web-api host')

    cmd_options = parser.parse_args()

    nagios = NagiosResponse("Mappings for both ams and web-api completed successfully")

    if cmd_options.service == "ams":
        nagios = NagiosResponse("Mapping for AMS completed successfully")
        ams_map(cmd_options, nagios)

    if cmd_options.service == "web-api":
        nagios = NagiosResponse("Mapping for WEB-API completed successfully")
        web_api_map(cmd_options, nagios)

    if cmd_options.service == "all":
        nagios = NagiosResponse("Mappings for both ams and web-api completed successfully")
        ams_map(cmd_options, nagios)
        web_api_map(cmd_options, nagios)

    # return successful message and status code
    print(nagios.getMsg())
    raise SystemExit(nagios.getCode())


def ams_map(cmd_options, nagios):
    '''
        ams_map checks to see if authn and ams communicate properly between each other,
        by performing a mapping for one of the registered bindings under the ams service.
    '''

    # authn url for the ams mapping
    u1 = "https://{0}:{1}/v1/service-types/{2}/hosts/{3}:authx509".format(
        cmd_options.authn_host,
        cmd_options.authn_port,
        cmd_options.ams_service,
        cmd_options.ams_host
    )

    # create the certificate tuple needed by the requests library and pass the ssl verify options
    reqkwargs = {
        "cert": (cmd_options.cert, cmd_options.key),
        "verify": cmd_options.verify
    }

    # perform the mapping for the ams binding
    try:
        authn_ams_resp = _get_request(u1, cmd_options.verbose, **reqkwargs)
    except Exception as e:
        nagios_report(nagios, "critical", e.message)

    if authn_ams_resp.status_code != 200:
        resp_json = authn_ams_resp.json()
        if "error" not in resp_json:
            nagios_report(nagios, "critical", resp_json.text)
        if "message" not in resp_json["error"]:
                nagios_report(nagios, "critical", resp_json.text)

        nagios_report(nagios, "critical",
                      "Authn(AMS) returned {}".format(authn_ams_resp.json()["error"]["message"]))

    if cmd_options.ams_token is not None:
        if "token" not in authn_ams_resp.json():
            nagios_report(nagios, "critical", "Authn(AMS) expected token but returned {}".format(authn_ams_resp.text))

        if authn_ams_resp.json()["token"] != cmd_options.ams_token:
            nagios_report(nagios, "critical",
                          "Authn(AMS) token mismatch. Expected {0} and got {1}".format(
                              cmd_options.ams_token, authn_ams_resp.json()["token"]))


def web_api_map(cmd_options, nagios):
    '''
        web_api_map checks to see if authn and web-api communicate properly between each other,
        by performing a mapping for one of the registered bindings under the web-api service.
    '''

    # authn url for the web-api mapping
    u1 = "https://{0}:{1}/v1/service-types/{2}/hosts/{3}:authx509".format(
        cmd_options.authn_host,
        cmd_options.authn_port,
        cmd_options.web_api_service,
        cmd_options.web_api_host
    )

    # create the certificate tuple needed by the requests library and pass the ssl verify options
    reqkwargs = {
        "cert": (cmd_options.cert, cmd_options.key),
        "verify": cmd_options.verify
    }

    # perform the mapping for the web-api binding
    try:
        authn_web_api_resp = _get_request(u1, cmd_options.verbose, **reqkwargs)
    except Exception as e:
        nagios_report(nagios, "critical", e.message)

    if authn_web_api_resp.status_code != 200:
        resp_json = authn_web_api_resp.json()
        if "error" not in resp_json:
            nagios_report(nagios, "critical", resp_json.text)
        if "message" not in resp_json["error"]:
                nagios_report(nagios, "critical", resp_json.text)

        nagios_report(nagios, "critical",
                      "Authn(WEB-API) returned {}".format(authn_web_api_resp.json()["error"]["message"]))

    if cmd_options.web_api_token is not None:
        if "token" not in authn_web_api_resp.json():
            nagios_report(nagios, "critical",
                          "Authn(WEB-API) expected token but returned {}".format(authn_web_api_resp.text))

        if authn_web_api_resp.json()["token"] != cmd_options.web_api_token:
            nagios_report(nagios, "critical",
                          "Authn(WEB-API) token mismatch. Expected {0} and got {1}".format(
                              cmd_options.web_api_token, authn_web_api_resp.json()["token"]))


def _get_request(url, verbose, **reqkwargs):
    '''
        Generic wrapper function that performs a get request on the given url.
    '''
    try:
        return requests.get(url, **reqkwargs)
    except exceptions.ConnectionError as ce:
        if verbose:
            raise Exception("Authn Connection error. {}".format(ce.message))
        else:
            raise Exception("Authn Connection error")
    except exceptions.HTTPError as he:
        if verbose:
            raise Exception("Authn HTTP error. {}".format(he.message))
        else:
            raise Exception("Authn HTTP error")
    except exceptions.SSLError as ssle:
        if verbose:
            raise Exception("Authn SSL error. {}".format(ssle.message))
        else:
            raise Exception("Authn SSL error")
    except exceptions.Timeout as te:
        if verbose:
            raise Exception("Authn TIMEOUT error. {}".format(te.message))
        else:
            raise Exception("Authn TIMEOUT error")
    except Exception as e:
        raise Exception("Authn error {}".format(e.message))


def nagios_report(nagios, status, msg):
    nagios_method = getattr(nagios, "write{0}Message".format(status.capitalize()))
    nagios_method(msg)
    nagios_status = getattr(nagios, status.upper())
    nagios.setCode(nagios_status)
    if status == 'critical':
        print(nagios.getMsg())
        raise SystemExit(nagios.getCode())


if __name__ == '__main__':
    main()
