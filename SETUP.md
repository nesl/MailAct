MailAct Setup
=============

The typical method of installation is via the MailAct VM. However this is not required. 
Without the VM, you just need a Linux machine with Python, Fetchmail and Procmail installed.

1. Setup MailAct VM (optional but recommended)
-----------------

### Download MailAct VM

The MailAct VM can be downloaded from the following link:

[Download MailAct VM] (https://docs.google.com/file/d/0B9tAaOC0PhDNaVgxNXhwS3poX00/edit?usp=sharing)

It is a zipped VMware VMDK file intended for use in a VMware ESXi hypervisor but can be used in VirtualBox, 
etc. as well.


### Login and Perform Network Setup

The default login is:

__username__: mailact
__password__: mailact

Once logged in, you will need to modify the network settings to run in your particular environment.

### Setting Up User Accounts

Each user of MailAct gets their own Linux user account. You could create Linux accounts manually. 
However, the preferred method is to use the provided Bash shell script in the home directory.

#### Usage:

    ./addmauser.sh USERNAME
    
Note that the user will be asked to provide a password for the account. 

This script will create the user's home directory and create the necessary files with the required permissions 
to run MailAct

### Alternative Approach: Installing MailAct on an Existing Linux Machine

Make sure that you have Python, Fetchmail and Procmail installed. Next, download MailAct from https://github.com/nesl/MailAct/archive/master.zip. Unzip and move the resulting folder to your home directory with the name MailAct. The following sequence of commands will do the trick: 

    curl -O https://codeload.github.com/nesl/MailAct/zip/master
    mv master master.zip
    unzip master.zip
    mv MailAct-master $HOME/MailAct
    rm master.zip

2. Configure MailAct
----------------------

Once the MailAct VM is setup (or the source code is downladed to a Linux machine with required dependencies), 
the next step is to run the Configurator module.

### Configuration File

See CONFIG.md for information on the format of the configuration file that is passed to the Configurator module.

[CONFIG.md](CONFIG.md)

### Configurator Usage

    ./Configurator.py [-h] [-py PYFILE] [-nop] config

#### Required (positional) arguments:

__config__: Configuration file (e.g. mailact.cfg)

#### Optional arguments:

__-h, --help__: show help message and exit
  
__-py PYFILE, --pyfile PYFILE__: Provide Python file of user-defined functions
                        
__-nop, --nopass__: Run without specifying password (uses previously stored password and does NOT restart Fetchmail)

### Other Notes:

#### Updating Files

When you update your configuration file, Python file of functions, etc., __you must re-run the Configurator module__.

#### Using the -nop, --nopass option

When you run the Configurator module, you will be asked to provide the password to your email account. 
This is redundant when you are just updating the configuration file and/or Python code. Thus, use the __-nop, --nopass__ 
option when you want to just update the files. Note that this will not start / restart Fetchmail, so do not use this 
option if the machine or Fetchmail crashed, etc.

3. Track MailAct
-------------------

Once the Configurator is run, MailAct is running in the background and is communicating to your IMAP mail server.
You can keep track of emails that come in and, the extractions made and the actions that were performed via log files.

### MAILACT.log

The main log file is located at __~/mail/MAILACT.log__

Whenever an email is received, it will print a few blank lines followed by 

    Got an email at: <CURRENT_TIME>
    
    Performing actions for <SENSOR_NAME>
    
    ALL EXTRACTIONS
    HEADER: <HEADER>
    EXTRACTIONS:
    <EXTRACTIONS...>
    ...
    
    Starting Process, PID = <PID>
    <LIST OF ACTIONS TO BE PERFORMED BY THIS PROCESS>
    ...
    
    <LIST OF UNFINISHED PROCESSES>
    ...
    
    Finished Processing Email at: <CURRENT_TIME>

### process_\<PID\>.log

For each process (each action list), a log file is created for tracking. Its filename is "process_\<PID\>.log",
where <PID> is the PID of the process.

For each completed, action, the log file will state:

    Completed  Action: <ACTION>

If an action failed due to an exception (e.g. SyntaxError), the log file will state:

    * FAILED Action *: <ACTION>
        <EXCEPTION_TYPE>

### unfinished_\<PID\>.log

If a process (action list) did not complete by the timeout, this file will be created and will list all the actions. 
This way they can be re-run by another process later.


4. Making it work with GMail
----------------------------

MailAct uses Fetchmail to download emails. If you get authorization failure, you may need to enable IMAP access to GMail by less secure clients by visiting http://support.google.com/mail/accounts/bin/answer.py?answer=78754.
