import time

def convDoorTime(time_string):
	local_time = time.strptime(time_string)
	gmt_time = time.gmtime(time.mktime(local_time))
	return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmt_time)

def my_sleep(secs):
	outfile = open('sleeper.log', 'a')
	outfile.write('\nStarted at: ' + time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + '\n')
	time.sleep(float(secs))
	outfile.write('Finished at: ' + time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + '\n')
	outfile.close()
