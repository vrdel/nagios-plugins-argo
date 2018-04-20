#!/usr/bin/env python

from argparse import ArgumentParser
import datetime
import time
import json
from argo_ams_library import ArgoMessagingService, AmsException
from NagiosResponse import NagiosResponse


def main():
    TIMEOUT = 180
    INTERVAL = 300

    parser = ArgumentParser(description="Nagios probe for monitoring the compute engine's flow.")
    parser.add_argument('-H', dest='host', type=str, default='msg-devel.argo.grnet.gr', help='FQDN of AMS Service')
    parser.add_argument('--token', type=str, required=True, help='Given token')
    parser.add_argument('--project', type=str, required=True, help='Project registered in AMS Service')
    parser.add_argument('--push_topic', type=str, default='create_data', help='Given topic')
    parser.add_argument('--push_subscription', type=str, default='create_data_sub', help='Push_Subscription name')
    parser.add_argument('--pull_subscription', type=str, default='retrieve_data_sub', help='Push_Subscription name')
    parser.add_argument('-t', dest='timeout', type=int, default=TIMEOUT, help='Timeout for ams calls')
    parser.add_argument('-i', dest='interval', type=int, default=INTERVAL, help='The amount of time the probe should try to read from ams, beforing exiting')

    cmd_options = parser.parse_args()

    run_timestamp = str(datetime.datetime.now())

    nagios = NagiosResponse("System Dataflow at " + run_timestamp + " completed successfully.")
    ams = ArgoMessagingService(endpoint=cmd_options.host, token=cmd_options.token, project=cmd_options.project)
    try:
        # For both subscriptions move their offset to max
        move_sub_offset_to_max(ams, cmd_options.push_subscription, timeout=cmd_options.timeout)
        move_sub_offset_to_max(ams, cmd_options.pull_subscription, timeout=cmd_options.timeout)

        # publish a message with the current timestamp as its content
        req_data = {'message': run_timestamp, 'errors': []}
        d1 = {'data': json.dumps(req_data), 'attributes': {}}
        ams.publish(cmd_options.push_topic, d1, timeout=cmd_options.timeout)
        start = time.time()
        no_resp = True
        while no_resp:
            end = time.time()
            # check if the systsem has written to the retrieve topic
            resp = ams.pull_sub(cmd_options.pull_subscription, timeout=cmd_options.timeout)
            if len(resp) > 0:
                no_resp = False
                resp_data = json.loads(resp[0][1]._data)
                # check if the submitted and retrieved data differ
                if req_data != resp_data:
                    nagios_report(nagios, 'critical', "System Dataflow at " + run_timestamp + " completed with errors. Expected: " + str(req_data) + ". Found: " + str(resp_data)+".")
                # check if data was retrieved within the expected timeout period, BUT had some kind of delay
                elif req_data == resp_data and end-start > cmd_options.interval:
                    nagios_report(nagios, 'warning', "System Dataflow at " + run_timestamp + " completed successfully using an extra time of: " + str((end-start)-cmd_options.interval) + "s.")

            if (end-start) > 2 * cmd_options.interval:
                nagios_report(nagios, 'critical',  "System Dataflow at " + run_timestamp + " returned with no message from the systsem after " + str(2 * cmd_options.interval) + "s.")

            # check for a response every 10 seconds
            time.sleep(10)

        print(nagios.getMsg())
        raise SystemExit(nagios.getCode())

    except AmsException as e:
        nagios_report(nagios, 'critical', e.msg())


def nagios_report(nagios, status, msg):
    nagios_method = getattr(nagios, "write{0}Message".format(status.capitalize()))
    nagios_method(msg)
    nagios_status = getattr(nagios, status.upper())
    nagios.setCode(nagios_status)
    if status == 'critical':
        print(nagios.getMsg())
        raise SystemExit(nagios.getCode())


def move_sub_offset_to_max(ams, sub, **reqkwargs):
    # Retrieve the max offset for the given subscription
    max_sub_offset = ams.getoffsets_sub(sub, "max", **reqkwargs)
    # Move the current offset to the max position
    ams.modifyoffset_sub(sub, max_sub_offset, **reqkwargs)


if __name__ == "__main__":
    main()
