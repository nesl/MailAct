import sys
import os
import re

import time
import json
import httplib
import email
import calendar


from ma_sensor import SensorObject
from ma_consts import *

# Functions for converting strings to numbers

def maStrToIndex(*args):
	""" Returns the index of the first argument found in the remaining arguments
		where index starts at 0 and increments for each additoinal argument
		e.g. if 'Armed' is the first arg, then 'Disarmed' then 'Armed'
			 1 will be returned ('Disarmed' is 0)"""
	
	for num, arg in enumerate(args):
		if num != 0 and arg == args[0]:
			return num-1

	return None

def maStrToInt(*args):
	""" First argument is string to convert
		Arguments that follow are pairs of strings and values (ints)
		Function returns the value corresponding to the string in the first argument """

	for num, arg in enumerate(args):
		if num % 2 == 1 and arg == args[0]:
			return args[num+1]

	return None

# Functions for creating datapoints

def maCreateDatapoint(timestamp, value):
	return [{"at": timestamp, "value": value}]

def maAppendDatapoint(datapoints, timestamp, value):
	datapoints.append({"at": timestamp, "value": value})
	return datapoints

# Functions for getting current time

def maGetTimeStruct():
	''' Returns time_struct of UTC time '''
	return time.gmtime()

def maGetTimeEpoch():
	''' Returns time since epoch '''
	return time.time()

def maGetTimeAsc():
	''' Returns standard ascii format of UTC time '''
	return time.asctime(time.gmtime())

def maGetTimeCosm():
	''' Returns Cosm format of current UTC time '''
	return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

# Functions for getting email header 'Date' time

def maGetEmailDateTimeStruct(email_date):
	''' Returns time_struct of email Date header time '''
	return time.gmtime(email.utils.mktime_tz(email.utils.parsedate_tz(email_date)))

def maGetEmailDateTimeEpoch(email_date):
	''' Returns time since epoch of email Date header time '''
	return calendar.timegm(maGetEmailDateTimeStruct(email_date))

def maGetEmailDateTimeAsc(email_date):
	''' Returns standard ascii format of email Date header time '''
	return time.asctime(maGetEmailDateTimeStruct(email_date))

def maGetEmailDateTimeCosm(email_date):
	''' Returns Cosm format of email Date header time '''
	return time.strftime("%Y-%m-%dT%H:%M:%SZ", maGetEmailDateTimeStruct(email_date))	

# Functions for adding time

def maAddSecsToStruct(orig_time, sec):
	return time.gmtime(calendar.timegm(orig_time) + sec)

def maAddSecsToEpoch(orig_time, sec):
	return orig_time + sec

def maAddSecsToAsc(orig_time, sec):
	return time.asctime(maAddSecsToStruct(time.strptime(orig_time), sec))

def maAddSecsToCosm(orig_time, sec):
	return time.strftime("%Y-%m-%dT%H:%M:%SZ", maAddSecsToStruct(time.strptime(orig_time, "%Y-%m-%dT%H:%M:%SZ"), sec))

# variable assignment

def maSet(data):
	''' Used for variable assignment, since each line has an action '''
	return data

def maPrintArgs(*args):
	for arg in args:
		print arg

# Cosm

def maCosmSend(feedid, datastream, datapoints, apikey=None):
	# build datastream
	datastreams = []
	datastreams.append({"id": datastream, "datapoints": datapoints})

	# build body for cosm upload
	body = {"version": "1.0.0", "datastreams": datastreams}
	body_text = json.dumps(body)

	# create header with apikey
	if apikey:
		headers = {"X-ApiKey": apikey}
	else:
		headers = {"X-ApiKey": COSM_APIKEY}

	# Try uploading every 5 seconds
	uploaded = False
	while uploaded == False:
		try:
			# create connection and url params with feedid
			http_conn = httplib.HTTPConnection("api.cosm.com")
			params = "/v2/feeds/" + str(feedid)
			http_conn.request("PUT", params, body_text, headers)

			try:
				response = http_conn.getresponse()
			except:
				response = None

			if response:
				http_conn.close()
				if response.status == 200:
					uploaded = True
		except:
			pass

		time.sleep(5)

	return response
