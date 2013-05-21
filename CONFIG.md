MailAct Configuration File
==========================

This file describes the format of the configuration file that is passed to the MailAct Configurator Module.

It also provides a list of Actions that are provided by MailAct for use in the configuration file.

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

Actions Included with MailAct
-----------------------------

There are many helper functions provided by MailAct to help users get started with performing actions. 
Of course, users can create their own functions in the optional Python file that is passed to the Configurator. 

### Converting Strings to Values

#### _maStrToIndex(str_to_match, str1, [str2, …])_

Convert a string to a value based on an indexing scheme that starts from 0.

##### Examples

    >>> maStrToIndex('Keychain', 'Keychain', 'Password', 'Garage Opener')
    0
    
    >>> maStrToIndex('Password', 'Keychain', 'Password', 'Garage Opener')
    1
    
#### _maStrToInt(str_to_match, str1, value1, [str2, value2, …])_

Convert a string to a value based on one or more key-value pairs.

##### Examples

    >>> maStrToInt('Armed', 'Armed', 1, 'Disarmed', 0, 'Unknown', -1)
    1
    
    >>> maStrToInt('Disarmed', 'Armed', 1, 'Disarmed', 0, 'Unknown', -1)
    0
    
### Timestamps

There are four formats of time that operations can be performed on

- __Struct__: Time expressed in the _struct_time_ format of the Python _time_ module
- __Epoch__: Time in seconds since the Unix Epoch (midnight UTC on January 1, 1970)
- __Asc__: Time as an ascii string as returned by Python time.ctime()
- __Cosm__: Time as an ascii string formatted in the format accepted by Cosm (ISO 8601)

#### _maGetTime*()_

Get current time (system's time)

##### Examples
    >>> maGetTimeEpoch()
    1369170987.880371
    
    >>> maGetTimeAsc()
    'Tue May 21 21:16:30 2013'
    
    >>> maGetTimeCosm()
    '2013-05-21T21:16:31Z'

#### _maGetEmailDateTime*()_

Get time from email's "date" header

#### _maAddSecsTo*(time, secs)_

Add _secs_ seconds to _time_. Note that _time_ must be in the same format as *.

##### Examples
    >>> x = 1369170987.880371
    >>> maAddSecsToEpoch(x, 5)
    1369170992.880371
    
    >>> y = 'Tue May 21 21:16:30 2013'
    >>> maAddSecsToAsc(y, 8)
    'Tue May 21 21:16:38 2013'
    
    >>> z = '2013-05-21T21:16:31Z'
    >>> maAddSecsToCosm(z, 600)
    '2013-05-21T21:26:31Z'

### Cosm

These functions can be used to upload data to Cosm.

#### _maCreateDatapoint(timestamp, value)_

Create a Cosm Datapoint by providing a timestamp and value

#### _maAppendDatapoint(datapoints, timestamp, value)_

Append a new timestamp and value pair to a previously created Datapoint that was created using _maCreateDatapoint_.

#### _maCosmSend(feedid, datastream, datapoints, [apikey])_

Upload Datapoints to Cosm by providing the Feed ID, Datastream, Datapoints and API key. API key is optional. 
If no API key is provided, the global API key (provided in the configuration file) will be used. 
Datapoints should be created by using the _maCreateDatapoint_ and _maAppendDatapoint_ helper functions. 
User can create their own if desired as it is just a list of timestamp and value pairs.

#### Example

The following is an example of using many of the actions above to upload a door event to Cosm. 
The email arrival date is used as the timestamp for the door event and a value of 1 is used for this time. 
The timestamp one second before and one second after are set to 0 to create a clean edge. Thus, 3 datapoints 
are uploaded to Cosm.

    date0 = maGetEmailDateTimeCosm()
    datapoints = maCreateDatapoint(date0, 1)
    date1 = maAddSecsToCosm(date0, -1)
    datapoints = maAppendDatapoint(datapoints, date1, 0)
    date2 = maAddSecsToCosm(date0, 1)
    datapoints = maAppendDatapoint(datapoints, date2, 0)
    maCosmSend(123456, 'Door', datapoints, 'OPTIONAL_APIKEY')
    


