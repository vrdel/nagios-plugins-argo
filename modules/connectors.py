#!/usr/bin/python

import sys, os, ipdb
import argparse

from datetime import datetime, timedelta
from pprint import pprint
from argo_egi_connectors.config import Global, CustomerConf
from NagiosResponse import NagiosResponse

def check_file_ok(fname):
	if os.path.isfile(fname):
		fh = open(fname, 'r')
		if fh.read().strip() == 'True':
			return 0
		else:
			return 2

	else:
		return 1

def process_customer_jobs(files, cust_header, cust_conf, root_dir, date_sufix, nagios):
	file_names=['downtimes-ok', 'poem-ok', 'topology-ok', 'weights-ok']
	if files is not None:
		file_names = files

	customer_jobs = cust_conf.get_jobs(cust_header)
	for job in customer_jobs:
		for filename in file_names:
			false_count = 0
			for sufix in date_sufix:
				full_name = cust_conf.get_fullstatedir(root_dir, cust_header, job)+ '/' + filename + '_' + sufix
				ret_val = check_file_ok(full_name)

				if ret_val != 0:
					false_count += 1
					if (false_count == len(date_sufix)):
						nagios.setCode(nagios.CRITICAL)
						nagios.writeCriticalMessage("Customer: " + cust_conf.get_custname(cust_header) + ", Job: " + job + ", File: " + filename.replace("-ok", "").upper() + " not ok for last " + str(len(date_sufix)) + " days!")
					elif (false_count == 1 and nagios.getCode() <= nagios.WARNING):
						nagios.setCode(nagios.WARNING)
						nagios.writeWarningMessage("Customer: " + cust_conf.get_custname(cust_header) + ", Job: " + job + ", File: " + filename.replace("-ok", "").upper() + " not ok.")

	
def process_customer(cmd_options, root_directory, date_sufix, nagios):
	customer_conf = CustomerConf(sys.argv[0], cmd_options.config, jobattrs='')
	customer_conf.parse()
	
	for cust_header in customer_conf.get_customers():
		process_customer_jobs(cmd_options.filename, cust_header, customer_conf, root_directory, date_sufix, nagios)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', dest='config', required=True, type=str, help='config file')
	parser.add_argument('-f', dest='filename', required=False, type=str, nargs='+', help='file names to monitor. Default: downtimes-ok poem-ok topology-ok weights-ok')
	cmd_options = parser.parse_args()
	
	opts =  {"InputState": ["SaveDir", "Days"]}
	global_conf = Global(None, opts)
	
	options = global_conf.parse();
	root_directory = options.values()[0]
	days_num = int(options.values()[1])
	todays_date = datetime.today()
	
	days = []
	for i in range(1, days_num + 1):
		days.append(todays_date + timedelta(days=-i))
	
	date_sufix = []
	for day in days:
		date_sufix.append(day.strftime("%Y_%m_%d"))
	
	nagios = NagiosResponse()
	process_customer(cmd_options, root_directory, date_sufix, nagios)
	
	print(nagios.getMsg())
	raise SystemExit(nagios.getCode())

if __name__ == "__main__":
	main()

#ipdb.set_trace()

