#################################################################
## wattsup.py Energy CSV Parsing Script for MicroFaaS Project  ##
## Boston University PEACLAB 2021                              ##
#################################################################
import csv
from datetime import datetime
import os
import time
import sys

def update_meters(meters):
			meters[row['Meter']]['WH'] = float(row[' WH'])
			meters[row['Meter']]['total_W'] += float(row[' W'])
			meters[row['Meter']]['count'] += 1
			meters[row['Meter']]['average_watts'] = meters[row['Meter']]['total_W'] / meters[row['Meter']]['count']
			
with open(sys.argv[1], newline='') as csvfile:
	r = csv.DictReader(csvfile)
	meters = dict()
	err_count = 0
	err_count_w = 0
	line_number = 2
	
	for row in r:

		try:
			update_meters(meters)
			
		except KeyError:
			err_count += 1
			#print("Workloads:: Key Error: {count} on line {line}".format(count=err_count, line=line_number))
			#print(row['function_id'], row['exec_time'])
			meters[row['Meter']] = {'WH': 0, 'total_W': 0, 'count' : 0, 'average_watts' : 0}
			update_meters(meters)
			
		line_number += 1

	print()
	print("Log File: {f}".format(f=os.path.basename(sys.argv[1])))

	for meter in sorted (meters.keys()):
		print("Watt-hours consumed: {total_WH:.3f} WH \nAverage wattage: {avg:.3f} W \n{count} datapoints".format(total_WH=meters[meter]['WH'], meter = meter, avg = meters[meter]['average_watts'], count=meters[meter]['count']))
	print("--------------------------------------------------------------------------------\n")