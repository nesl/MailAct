MailAct
=======

A service for performing actions based on emails.

Setup
-----

See SETUP.md for instructions to Install and Setup MailAct

[SETUP.md](SETUP.md)

Configurator
------------

Module for setting up MailAct for a user.

### Configuration File

See CONFIG.md for information on the format of the configuration file that is passed to the Configurator module.

[CONFIG.md](CONFIG.md)

### Usage

    ./Configurator.py [-h] [-py PYFILE] [-nop] config

#### Required (positional) arguments:

__config__: Configuration file (e.g. mailact.cfg)

#### Optional arguments:

__-h, --help__: show help message and exit
  
__-py PYFILE, --pyfile PYFILE__: Provide Python file of user-defined functions
                        
__-nop, --nopass__: Run without specifying password (uses previously stored password and does NOT restart Fetchmail)


Email Processor
---------------

Module that receives emails, extracts content from them and performs actions.

### Note

This module is called by Procmail, so a typical user should not run this module on its own.

### Usage

    ./EmailProcessor.py USER_ACCOUNT_NAME SENSOR_NAME
    
#### Required (positional) arguments:

__USER_ACCOUNT_NAME__: This is the user's email address with non-alphanumeric characters replaced with underscores

__SENSOR_NAME__: A particular sensor that is defined in the configuration file passed to the Configurator module

#### Additional notes:

Note that the email should be passed to the module via standard input, so typical manual usage is performed as follows:

    cat email.txt | ./EmailProcessor.py user_account_name sensor_name


Common
------

Common modules that may be used by the main modules.

__ma_consts.py__:  common constants

__ma_funcs.py__: common functions

__ma_acts.py__: provided actions (e.g. maCosmSend)

__ma_sensor.py__: MailAct sensor object.


Other Files
-----------

#### addmauser.sh

Bash shell script for adding a new Linux user account in a MailAct VM

#### .procmailrc

Default Procmail RC file before modified to include filtering criteria

#### .fetchmailrc

Blank Fetchmail RC file
