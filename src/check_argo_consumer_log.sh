#!/bin/bash

CURR_DATE=`date -u +%Y-%m-%d`
ARGO_CONSUMER_DIR=/var/lib/argo-egi-consumer

# pull in sysconfig settings
[ -f /etc/sysconfig/check_argo_consumer_log ] && . /etc/sysconfig/check_argo_consumer_log

/usr/lib64/nagios/plugins/check_file_age -w 1800 -c 3600 $ARGO_CONSUMER_DIR/argo-consumer_log_$CURR_DATE.avro
