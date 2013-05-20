import sys
import os
import re
import email
import csv
from multiprocessing import Process

sys.path.append(os.path.abspath(os.path.expanduser('~') + '/MailAct/common/'))

from ma_sensor import SensorObject
from ma_consts import *
from ma_acts import *
import ma_funcs

# set debug mode to 1 to read an email from file and set account / sensor manually
debug_mode = 0

if debug_mode == 0:
	email_lines = sys.stdin.readlines()
	account_name = sys.argv[1]
	sensor_name = sys.argv[2]
else:
	with open('email.txt', 'r') as email_file:
		email_lines = email_file.readlines()
	account_name = 'amir_vajid_gmail_com'
	sensor_name = 'alarm_disarm'

pyfile_path = USERS_DIR + account_name + PY_EXT
sys.path.append(os.path.abspath(pyfile_path))
from ma_user_funcs import *

def maDebugPrint(text, debug=1):
	if debug == 1:
		print text
		with open(MA_LOG, 'a') as debug_log:
			debug_log.write(text + '\n')

def maExecuteAction(actions_list):
	''' Function to be called as individual process to execute actions '''
	
	outfile = open(PROC_LOG + str(os.getpid()) + LOG_EXT, 'w')
	
	#outfile.write('Starting New Process: ' + __name__ + '\n')
	#outfile.write('Parent Process: ' + str(os.getppid()) + '\n')
	#outfile.write('New Process ID: ' + str(os.getpid()) + '\n\n')

	for action in actions_list:
		#outfile.write('Performing Action: ' + action + '\n')
		try:
			exec compile(action, '<string>', 'exec')
			outfile.write('Completed  Action: ' + action + '\n')
		except:
		#except SyntaxError:
			outfile.write('* FAILED Action *: ' + action + '\n')
			outfile.write('\t' + str(sys.exc_info()[0]) + '\n')

	outfile.close()
	
maDebugPrint('\n\n\nGot an email at: ' + time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + '\n')

if __name__ == "__main__":

	whole_email = ''
	for line in email_lines:
		whole_email += line
	email_msg = email.message_from_string(whole_email)

	# Get Email Date
	EMAIL_DATE = email_msg.get('Date')

	# Use account name to find config file
	config_path = USERS_DIR + account_name + CFG_EXT + CFG_FILE

	with open(config_path, 'r') as config_file:
		config_lines = config_file.readlines()

	# Get Cosm API Key (if provided, None otherwise)
	COSM_APIKEY = ma_funcs.get_cosm_apikey(config_lines)

	# Get actions timeout (default is PROC_TIMEOUT)
	act_timeout = ma_funcs.get_timeout(config_lines)

	# Get sensor list from sensor file
	sensor_list = ma_funcs.parseSensors(config_lines)

	# Find sensor in sensor list
	for sensor in sensor_list:
		if sensor.name == sensor_name:
			break
	
	# if didn't find sensor, exit
	if sensor.name != sensor_name:
		maDebugPrint('ERROR: Could not find SENSOR: ' + sensor_name)
		sys.exit()
	
	maDebugPrint('Performing actions for ' + sensor.name)

	
	# Extract items from email -- filling dictionary with entry as a list of return values
	extractions = {}
	for header, regex in sensor.extract.items():
		content_str = None
		# If NOT in the body, we can get line with corresponding header	
		#TODO: maybe these replaces should replace '\n' with '' (instead of ' ')
		if header.lower() == 'body':
			content_str = email_msg.get_payload().replace('\n', ' ')
		else:
			content_str = email_msg.get(header).replace('\n', ' ')

		# If we found the content, extract info
		if content_str != None:
			re_tup = re.match(regex, content_str).groups()
			extractions[header] = re_tup

	# At this point, extractions are complete
	# They are in the 'extractions' dictionary stored as tuples

	maDebugPrint('\nALL EXTRACTIONS')
	for header, extract_tup in extractions.items():
		maDebugPrint('HEADER: ' + header)
		maDebugPrint('EXTRACTIONS: ')
		for item in extract_tup:
			maDebugPrint(item)


	# Iterate through actions lists and configure/compile actions
	new_list_of_action_lists = []
	for action_list in sensor.actions:
		# Get action list with action lines ready to be executed
		#NOTE: Assumes action list has already been checked and verified
		cfg_action_list = ma_funcs.configureActions(action_list, extractions)
		new_list_of_action_lists.append(list(cfg_action_list))


	# Run each configured action list in its own process
	plist = []
	for action_list in new_list_of_action_lists:

		p = Process(target=maExecuteAction, args=(action_list,))
		plist.append(p)
		p.start()
		
		maDebugPrint('\nStarting Process: PID = ' + str(p.pid))
		maDebugPrint('\n'.join(action_list))
		#maDebugPrint('')

	# Wait for actions to finish (up to 'act_timeout' -- default PROC_TIMEOUT)
	tend = time.time() + act_timeout
	num_alive_procs = len(plist)
	while num_alive_procs > 0 and time.time() < tend:
		# split timeout per process among remaining alive processes
		timeout_split = (tend - time.time()) / num_alive_procs

		# wait for processes to finish or timeout
		for p in plist:
			p.join(timeout_split)

		# find remaining processes alive
		num_alive_procs = 0
		for p in plist:
			if p.is_alive():
				num_alive_procs += 1

	# handle unfinished actions (terminate and print to log)
	for num, p in enumerate(plist):
		if p.is_alive():
			p.terminate()
			maDebugPrint('\nUnfinished Process: PID = ' + str(p.pid))
			# print actions to log file
			unf_actions = '\n'.join(new_list_of_action_lists[num])
			with open(UNFINISHED_LOG + str(p.pid) + LOG_EXT, 'w') as unf_log:
				unf_log.write(unf_actions)
	
	# finished
	maDebugPrint('\nFinished Processing Email at: ' + time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + '\n')
