#!/usr/bin/python

import sys
import os
import re
import shutil
import argparse
import getpass
import subprocess

#sys.path.append(os.path.abspath('../common/'))
sys.path.append(os.path.abspath(os.path.expanduser('~') + '/MailAct/common/'))

from ma_sensor import SensorObject
from ma_consts import *
import ma_funcs


if __name__ == "__main__":

	print '\nStarting MailAct Configurator!\n'
	
	parser = argparse.ArgumentParser()

	parser.add_argument("-py", "--pyfile",  metavar="PYFILE", help="Python file of defined functions")
	parser.add_argument("config", help="Configuration file")
	parser.add_argument("-nop", "--nopass", action='store_true', help="Run without specifying password (uses previously stored password)")

	args = parser.parse_args()

	config_filename = args.config
	
	if args.pyfile:
		pyfile_filename = args.pyfile
	else:
		pyfile_filename = ''

	with open(config_filename, 'r') as infile:
		config_lines = infile.readlines()

	# Parse config file to set up account directory, etc.
	email, server = ma_funcs.parseAccounts(config_lines)

	if email == '' or server == '':
		sys.exit()

	# copy config file to account directory
	email_name = re.sub('[^0-9a-zA-Z]+', '_', email)
	config_file =  USERS_DIR + email_name + CFG_EXT + CFG_FILE
	shutil.copyfile(config_filename, config_file)

	# copy python file to account directory
	pyfile_copy_path = USERS_DIR + email_name + PY_EXT + PY_FILE
	if pyfile_filename != '':
		shutil.copyfile(pyfile_filename, pyfile_copy_path)
	else:
		with open(pyfile_copy_path, 'w') as outfile:
			outfile.write('# EMPTY PYTHON FILE CREATED BY MAILACT')
	init_file_path = USERS_DIR + email_name + PY_EXT + INIT_FILE
	initfile = open(init_file_path, 'w')
	initfile.close()

	if args.nopass == False:
		# get password for email account from user
		user = getpass.getuser()
		print 'Enter Password for the following email account: ' + email
	
		pw1 = getpass.getpass()
		pw2 = getpass.getpass('Retype Password: ')

		while pw1 != pw2:
			print 'Passwords did not match. Please try again'
			pw1 = getpass.getpass()
			pw2 = getpass.getpass('Retype Password: ')

		# Create fetchmailrc file for imap server connection
		ma_funcs.createFetchmailRC(email, pw1, server, user)

		# Restart (Start) fetchmail
		subprocess.call("fetchmail --quit", shell=True)
		subprocess.call("fetchmail", shell=True)
	
	print 'Account directory set up at ' + USERS_DIR + email_name

	# Parse config files for sensors to create procmail.rc file
	sensor_list = ma_funcs.parseSensors(config_lines)

	if (sensor_list == -1):
		print 'ERROR PROCESSING SENSOR LIST'
	else:
		print '\nList of Sensors:'
		for sensor in sensor_list:
			print sensor.name

	# Create procmail.rc file with sensor list
	ma_funcs.createIncludeRC(email, sensor_list)

	# Done
	print '\nMailAct Configurator Complete!\n'



