#!/usr/bin/env python

import json, requests
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', required=True, type=str, help='hostname')
    parser.add_argument('-r', required=True, type=str, help='profile name')
    arguments = parser.parse_args()

    try:
        data1=requests.get('http://'+arguments.H+'/poem/api/0.2/json/metrics_in_profiles?vo_name=ops')
        d1=data1.json()
    except (requests.ConnectionError, requests.HTTPError) as e:
        print('CRITICAL - cannot connect to %s. %s'
             %('\"http://'+arguments.H+'/poem/api/0.2/json/metrics_in_profiles?vo_name=ops\"', e.args))
        exit(2)

    try:
        data2=requests.get('http://'+arguments.H+'/poem/api/0.2/json/profiles')
        d2=data2.json()
    except (requests.ConnectionError, requests.HTTPError) as e:
        print('CRITICAL - cannot connect to %s. %s'
             %('\"http://'+arguments.H+'/poem/api/0.2/json/profiles\"', e.args))
        exit(2)


    flag=False
    try:
        for profiles in d1[0]['profiles']:
            if profiles['name'] == arguments.r:
                flag=True
    except KeyError:
        print ('CRITICAL - cannot retrieve a value from .../poem/api/0.2/json/metrics_in_profiles?vo_name=ops')
        exit(2)

    if flag==False:
        print ('CRITICAL - does not contain specified profile')
        exit(2)


    s1=set()
    s2=set()

    try:
        for profiles in d1[0]['profiles']:
            if profiles['name'] == arguments.r:
                for metrics in profiles['metrics']:
                    s1.add(metrics['name'])
    except KeyError:
        print ('CRITICAL - cannot retrieve a value from .../poem/api/0.2/json/metrics_in_profiles?vo_name=ops')
        exit(2)

    try:
        for i in d2:
            if (i['name'] == arguments.r):
                for metrics in i['metric_instances']:
                    s2.add(metrics['atp_service_type_flavour'])
    except KeyError:
        print ('CRITICAL - cannot retrieve a value from .../poem/api/0.2/json/profiles')
        exit (2)


    print ('OK - %s has %d distinct service types and %d distinct metrics'
        %(arguments.r, len(s1), len(s2)))

if __name__ == "__main__":
    main()