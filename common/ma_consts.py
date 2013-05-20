import os

HOME_DIR = os.path.expanduser('~')

USERS_DIR = HOME_DIR + '/MailAct/users/'

CFG_EXT = '/cfg/'
CFG_FILE = 'mailact.cfg'

PY_EXT = '/src/'
PY_FILE = 'ma_user_funcs.py'
INIT_FILE = '__init__.py'

NIMBITS_CFG = 'nimbits.cfg'
NIMBITS_ADDR = 'http://cloud.nimbits.com'
COSM_CFG = 'cosm.cfg'

PROCMAIL_RC = HOME_DIR + '/.procmailrc'
PROCMAIL_DIR = HOME_DIR + '/.procmail/'

FETCHMAIL_RC = HOME_DIR + '/.fetchmailrc'

HEAD_NAMES = ['From', 'Subject', 'Body']
EMPTY_DICT = {}
for i, name in enumerate(HEAD_NAMES):
	EMPTY_DICT[HEAD_NAMES[i]] = ''

COSM_APIKEY = ''
EMAIL_TIME = ''

MA_LOG = 'MAILACT.log'

PROC_TIMEOUT = 600 # default 600 sec timeout (10 mins)

PROC_LOG = 'process_'
LOG_EXT = '.log'
UNFINISHED_LOG = 'unfinished_'
