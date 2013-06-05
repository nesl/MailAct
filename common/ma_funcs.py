import sys
import os
import re

from ma_sensor import SensorObject
from ma_consts import *
from ma_acts import * # maybe remove

def appendToProcmail(email_name):
	''' Adds email account to Procmail '''
	# Open file for reading and look for email
	line_to_add = 'INCLUDERC=$PMDIR/' + email_name + '.rc'
	with open(PROCMAIL_RC, 'r') as infile:
		lines = infile.readlines()

	for i, line in enumerate(lines):
		lines[i] = line.strip()

	# if line not found, append
	if line_to_add not in lines:
		with open(PROCMAIL_RC, 'a') as outfile:
			outfile.write(line_to_add)

def parseAccounts(config_lines):
	''' Gets Account Information and Sets up Accounts (directories + files)  '''
	line = ''
	line_itr = iter(config_lines)

	# Read Email / Account name
	while line.find('Email:') != 0:
		try:
			line = line_itr.next().strip()
		except StopIteration:
			print 'CONFIG_FILE_ERROR: First line should contain email'
			return ['', '']

	email = line.partition(':')[2].lstrip()

	# Replace all non-alphanumeric characters with _
	email_name = re.sub('[^0-9a-zA-Z]+', '_', email)

	# create email account directories
	email_path = USERS_DIR + email_name
	if not os.path.exists(email_path):
		os.makedirs(email_path)
	if not os.path.exists(email_path + CFG_EXT):
		os.makedirs(email_path + CFG_EXT)
	if not os.path.exists(email_path + PY_EXT):
		os.makedirs(email_path + PY_EXT)

	# Get IMAP Server Name
	while line.find('Server:') != 0:
		try:
			line = line_itr.next().strip()
		except StopIteration:
			print 'CONFIG_FILE_ERROR: Second line should contain IMAP Server'
			return ['', '']

	server = line.partition(':')[2].lstrip()
	
	# Look for any Nimbits / Cosm accounts
	while line.find('Sensor:') < 0:
		try:
			line = line_itr.next().strip()
		except StopIteration:
			return email, server
		account = ''
		api_key = ''
		addr = ''

		# Nimbits
		if line.find('Nimbits:') == 0:
			while line.strip():
				try:
					line = line_itr.next().strip()
				except StopIteration:
					print 'CONFIG_FILE_ERROR: Should be blank line after Nimbits account'
					return email, server
				if line.find('account:') == 0:
					account = line.partition(':')[2].lstrip()
				if line.find('api_key:') == 0:
					api_key = line.partition(':')[2].lstrip()
				if line.find('address:') == 0:
					addr = line.partition(':')[2].lstrip()

			if account != '':
				with open(email_path + CFG_EXT + NIMBITS_CFG, 'w') as nimbits_file:
					nimbits_file.write(account + '\n')
					if addr == '':
						nimbits_file.write(NIMBITS_ADDR + '\n')
					else:
						nimbits_file.write(addr + '\n')
					nimbits_file.write(api_key + '\n')

		# Cosm
		if line.find('Cosm:') == 0:
			while line.strip():
				try:
					line = line_itr.next().strip()
				except StopIteration:
					print 'CONFIG_FILE_ERROR: Should be blank line after Cosm account'
					return email, server
				if line.find('api_key:') == 0:
					api_key = line.partition(':')[2].strip()

			if api_key != '':
				with open(email_path + CFG_EXT + COSM_CFG, 'w') as cosm_file:
					cosm_file.write(api_key + '\n')

	return email, server

def parseSensors(config_lines):
	itr = iter(config_lines)
	line = ''
	EOF = False
	sensor_list = []

	while EOF != True:
		# Find "Sensor:" line, which marks new sensor def
		while line.find('Sensor:') != 0:
			try:
				line = itr.next().strip()
			except StopIteration:
				# EOF: no more sensors
				EOF = True
				break
		
		if EOF == True:
			break

		# Now 'line' contains "Sensor:" line -- get sensor name
		sensor_name = line.partition(':')[2].lstrip()

		# Get filtering minterms
		minterm_list = []
		# While we are not at '^' (extraction section), more minterms
		#while line.split()[0] != '^':
		while line.find('^') != 0:
			minterm = {}
			# Find beginning of new minterm
			while line.find('*') != 0:
				try:
					line = itr.next().strip()
				except StopIteration:
					# Reached EOF in middle of a sensor, return FAIL
					return -1

			# Now 'line' contains '*' line -- get first literal in minterm
			#eader = line.split()[1].strip(':')
			header = line.partition(':')[0].partition('*')[2].strip()

			minterm[header] = line.partition(':')[2].strip()

			# Get all other literals in minterm
			while True:
				try:
					line = itr.next().strip()
				except StopIteration:
					break

				# If non-'&' term, we finished minterm
				if line.find('&') != 0:
					break

				# Else, we have new literal to add
				header = line.partition(':')[0].partition('&')[2].strip()

				minterm[header] = line.partition(':')[2].strip()

			# Finished getting minterm literals, add to 'minterm_list'
			minterm_list.append(minterm)

		# Finished getting all minterms (got '^')
		extract = {}
		while line.find('^') == 0:
			header = line.partition(':')[0].partition('^')[2].strip()
			
			extract[header] = line.partition(':')[2].strip()

			try:
				line = itr.next().strip()
			except StopIteration:
				break


		# ACTIONS Section
		actions_list = []
		action_list = []
		while line.find('!') == 0:
			# Append first action to action_list
			action_list = []
			action = line.partition('!')[2].strip()
			action_list.append(action)
			
			try:
				line = itr.next().strip()
			except StopIteration:
				actions_list.append(action_list)
				break

			while line.find('+') == 0:
				action = line.partition('+')[2].strip()
				action_list.append(action)

				try:
					line = itr.next().strip()
				except StopIteration:
					break

			actions_list.append(action_list)

		# Finished processing ONE Sensor
		sensor = SensorObject(sensor_name, minterm_list, extract, actions_list)
		sensor_list.append(sensor)


	# Finished processing ALL Sensors
	return sensor_list

def createProcmailRC(pmrclines):
	outlines = []

	outlines.append('VERBOSE=yes')
	outlines.append('SHELL=/bin/bash')
	outlines.append('MAILDIR=$HOME/mail')
	outlines.append('PMDIR=$HOME/.procmail')
	outlines.append('LOGFILE=$PMDIR/log')
	outlines.append('')
	outlines.append('PYTHON=/usr/bin/python')
	outlines.append('EMAIL_PROC=$HOME/MailAct/EmailProcessor/EmailProcessor.py')
	outlines.append('')

	for line in pmrclines:
		outlines.append(line)
	
	with open(PROCMAIL_RC, 'w') as outfile:
		for line in outlines:
			outfile.write(line + '\n')
		

def createIncludeRC(email, sensor_list, type=1):
	''' Creates include.rc file based on sensor list
		type=1 means create new procmailrc
		type-0 means create include rc only '''

	outlines = []
	SENSOR_SET = 'SENSOR='
	PYTHON_CALL = '| $PYTHON $EMAIL_PROC $ACCOUNT $SENSOR'

	email_name = re.sub('[^0-9a-zA-Z]+', '_', email)
	outlines.append('ACCOUNT=' + email_name)
	outlines.append('')
	#outlines.append(':0c')	# maybe change this to ':0Bc'
	# NOTE: '.*' as gap after 'To:' may be too insecure (could match other emails)
	# NOTE: modified this so 'To:' restriction is removed -- since tied to indiv account now
	#outlines.append('* ^To:.*' + email)
	#outlines.append('{')

	# ITERATE THROUGH SENSOR_LIST
	for sensor in sensor_list:
		# Set SENSOR
		outlines.append(SENSOR_SET + sensor.name)

		# Iterate through minterms
		for match in sensor.match_crit:
			# Set flags (check if need body flag)
			if 'Body' in match or 'body' in match: 
				 outlines.append(':0Bc')
			else:
				 outlines.append(':0c')
			# Iterate through matching headers
			for header, value in match.items():
				if value != '':
					# TODO: in docs, note that '.*' is assumed before header's value
					# NOTE: this may be similar to perl, since matches any part of line
					outlines.append('* ^' + header + ':.*' + value)

			# Python call
			outlines.append(PYTHON_CALL)
			outlines.append('')

	# Unconditionally put all email for this account into 'all_mail' file in mail dir
	outlines.append(':0')
	outlines.append('all_mail')
	#outlines.append('}')

	if type == 0:
		# Write lines to include RC file
		with open(PROCMAIL_DIR + email_name + '.rc', 'w') as outfile:
			for line in outlines:
				outfile.write(line + '\n')
		# Add INCLUDERC to procmailrc file
		appendToProcmail(email_name)
	else:
		createProcmailRC(outlines)

# email, pw, imap server, linux account name
def createFetchmailRC(email, pw, server, user):
	''' Creates .fetchmailrc file '''
	outlines = []

	outlines.append('set postmaster "' + user + '"')
	outlines.append('set daemon 600')
	outlines.append('')
	outlines.append('poll ' + server + ' with proto IMAP')
	outlines.append('\tuser \'' + email + '\' there with password \'' + pw + 
					'\' is ' +	user + ' here options ssl keep idle')
	outlines.append('mda \'/usr/bin/procmail -d %T\'')

	with open(FETCHMAIL_RC, 'w') as fmrc:
		for line in outlines:
			fmrc.write(line + '\n')

def configureActions(action_list, extractions):
	''' Takes in action_list and email extractions to build list of configured actions
		That is, actions that can be compiled by python '''

	VAR_TAG = 'var_'
	final_action_list = []
	for action in action_list:
		assignment = ''
		action_name = ''
		action_args = []

		# NOTE: assuming every line has a function
		func_part = action.partition('(')[0]
		# If '=' found, then there is an assignment
		if '=' in func_part:
			assignment = VAR_TAG + func_part.partition('=')[0].strip() + ' = '
			action_name = func_part.partition('=')[2].strip()
		else:
			action_name = func_part.strip()

		# Get function arguments (between first '(' and last ')'
		action_args_str = action.rstrip(')').partition('(')[2]
		# Put arguments in a list
		# NOTE: could use csv module instead but has issues with quotes in quotes
		if ',' in action_args_str:
			action_args =  action_args_str.split(',')
		elif action_args_str: # single argument
			action_args =  [action_args_str]
		# NOTE: arguments are not split properly yet, since there could be comma in quotes

		# Parse arguments and prepare function call
		# All arguments are either 1. string, 2. number, 3. extraction reference, 4. variable
		for num in range(len(action_args)):
			# Added this check, since we may remove items in the args list
			if num >= len(action_args):
				break
			# remove leading spaces (after a comma)
			a_arg = action_args[num].lstrip()

			# 1. Check for COMPLETE string
			str_match = re.search('^\'.*\'$', a_arg)
			if str_match:
				print 'COMPLETE STR: ' + a_arg
				# NOTE: may need to execute the string to eliminate additional \ characters
				#exec compile('arg_str = ' + a_arg, '<string>', 'exec')
				#action_args[num] = '\'' + arg_str + '\''
				action_args[num] = a_arg
				continue

			# 1.5 Check for string with no end (has comma in string) by checking start quote
			p_str_match = re.search('^\'', a_arg)
			if p_str_match:
				p_str_end = num + 1 # look for end, starting with +1
				p_str_end_match = None
				while p_str_end_match == None:
					if p_str_end >= len(action_args):
						break
					#NOTE: Possible Bug -- arg that ends in a single quote may not mean end of quote
					# i.e. user could just have a single quote in their string
					# --> Need to check for \' (\\') vs. '
					# ********* SHOULD BE FIXED NOW *********
					# '([^\\\\]{1}\'$|^\'$)'
					#p_str_end_match = re.search('[^\\\\]{1}\'$', action_args[p_str_end].rstrip())
					p_str_end_match = re.search('([^\\\\]{1}\'$|^\'$)', action_args[p_str_end].rstrip())
					p_str_end += 1

				# NOTE: Should have found end by now, so make sure checker function checks for this

				# Join the strings by commas
				joined_str = ','.join(action_args[num:p_str_end]).strip()
				print 'JOINED STR: ' + joined_str
				# NOTE: may need to execute the string to eliminate additional \ characters
				#exec compile('arg_str = ' + joined_str, '<string>', 'exec')
				#action_args[num] = '\'' + arg_str + '\''
				action_args[num] = joined_str

				# Delete merged items in list
				del action_args[num+1:p_str_end]

				continue

			# 2. Check for number
			# NOTE: could do these with try/except as well -- more pythonic
			try:
				x = float(a_arg.strip())
				action_args[num] = a_arg.strip()
				continue
			except ValueError:
				pass
			
			# If int
			#if a_arg.strip().isdigit():
			#	action_args[num] = a_arg.strip()
			#	continue
			# Else if float
			#if re.search('^\d+(\.\d+)?$', a_arg.strip()):
			#	action_args[num] = a_arg.strip()
			#	continue

			# 3. Check for extraction reference (starts with '$')
			ext_match = re.search('^\$(.*)', a_arg)
			if ext_match:
				# Get header name
				ext_part = ext_match.group(1).partition('.')
				header = ext_part[0]
				
				# Get extractions tuple from extractions dictionary
				# NOTE: assuming header was in extractions dictionary
				ext_tup = extractions[header]

				# Get reference number from ext_part[2]
				# NOTE: assuming this is valid int
				ref_num = int(ext_part[2])

				# Get extraction from email (ext_tup) and put it in argument list
				try:
					arg_text = ext_tup[ref_num-1].strip()
				except IndexError:
					DEBUG.write('ERROR: Out of index error in header "' + header + '": ' + str(refnum))
					arg_text = ''

				action_args[num] = '\'' + arg_text + '\''

				continue

			# 4. Else, it should be a variable reference, so add VAR_TAG
			# NOTE: assuming variable has already been mentioned
			action_args[num] = VAR_TAG + a_arg.strip()

		# Done parsing action, can group parts together to create action
		# NOTE: Handle special actions:
		# If COSM_SEND, check if api-key provided, if not, use master key provided
		if action_name == 'maCosmSend':
			# If 3 arguments, need to append api-key
			if len(action_args) == 3:
				action_args.append('COSM_APIKEY')
		elif action_name.find('maGetEmailDateTime') == 0:
			if len(action_args) == 0:
				action_args.append('EMAIL_DATE')

		final_action = assignment + action_name + '(' + ', '.join(action_args) + ')'
		print final_action
		#exec compile('result = ' + final_action, '<string>', 'exec')
		#print result

		final_action_list.append(final_action)

	return final_action_list

def get_cosm_apikey(config_lines):
	line = ''
	line_itr = iter(config_lines)

	while line.find('Cosm:') != 0:
		try:
			line = line_itr.next().strip()
		except StopIteration:
			return None

	while line.find('api_key:') != 0:
		try:
			line = line_itr.next().strip()
		except StopIteration:
			return None

	return line.partition(':')[2].strip()

def get_timeout(config_lines):
	line = ''
	line_itr = iter(config_lines)

	while line.find('Timeout:') != 0:
		try:
			line = line_itr.next().strip()
		except StopIteration:
			return PROC_TIMEOUT

	try:
		timeout = float(line.partition(':')[2].strip())
	except:
	#except ValueError:
		return PROC_TIMEOUT

	return timeout
