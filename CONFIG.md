MailAct Config Format
=====================

This file describes the format of the configuration file that is passed to the MailAct Configurator Module.

Example Configuration File
---------------------------

The following is an example configuration file. A similar config was used to track when a door was opened in NESL.  

    Email: myemail@domain.com
    Server: imap.domain.com
    
    Timeout: 60
    
    Cosm:
      api_key: APIKEY
      
    Sensor: nesl_door
    * From: xxxxx@ucla.edu
    & Subject: NESL Door Event
    * From: yyyyy@gmail.com
    & Subject: NESL Door Event
    ^ Body: Current Time: (.*)
    ! date0 = convDoorTime($Body.1)
    + datapoints = maCreateDatapoint(date0, 1)
    + date1 = maAddSecsToCosm(date0, -1)
    + datapoints = maAppendDatapoint(datapoints, date1, 0)
    + date2 = maAddSecsToCosm(date0, 1)
    + datapoints = maAppendDatapoint(datapoints, date2, 0)
    + maCosmSend(FEEDID, DATASTREAM, datapoints)

Required Items
--------------

### Email Address

The first line ___must___ contain the email account that should be queried

### IMAP Mail Server

The second line ___must___ contain the IMAP mail server to query for emails

### Sensor Declarations

There ___must be at least one___ "Sensor" declaration. Each declaration includes the following:
- sensor name 
- filtering criteria 
- extractions 
- action list(s)

Optional Items
--------------

### Timeout

Used to provide a timeout for each action list (process) when executed by the Email Processor module

### Cosm Account

Used to provide master API key for a Cosm account. This will be used if an API key is not provided to maCosmSend.

Sensor Declarations
-------------------

### Sensor name

Each sensor declaration has a name ("nesl_door" in the example above).

### Filtering Criteria

After the name, filtering criteria is provided with regular expressions.

- The format is __"\<HEADER\>: \<REGEX\>"__
- The first filtering criterion is listed with an __asterisk (*)__ and any additional criteria are added with 
__ampersands (&)__.
- This filtering criteria is ANDed. 
- Another "minterm" can be created (an OR to the previous grouping of ANDs) by providing another asterisk line
and optionally ampersand lines. 
- In the example above, the sensor is triggered by emails from either "xxxxx@ucla.edu" OR
emails from "yyyyy@gmail.com" (both with subject "NESL Door Event").

### Extractions

After the filtering criteria is listed, the extractions to be made are provided with __carrots (^)__

- The format is __"\<HEADER\>: \<REGEX\>"__ (same as Filtering Criteria)
- Note that these regular expressions use parentheses to make extracted items. 
In the example above, all text that comes after "Current Time: " in the Body is extracted and stored.
- These extractions can then be referenced in the Actions section via their ___extraction reference___. 
The format of an extraction reference is __"$\<HEADER\>.\<NUM\>"__ 
(e.g. _$Body.1_ for the first reference in the Body header).

### Action Lists

Lastly, each sensor has one or more action lists. 

- Each new action list begins with an exclamation mark (!) and additional lines are added with pluses (+).
- Each action is basically a line of code with the current restriction that it must execute a function
- The arguments to functions can be numbers, strings, variables (if defined in a previous action line) or 
extraction references (defined above).

Provided Actions
----------------
