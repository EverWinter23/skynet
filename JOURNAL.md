# JOURNAL

### Monday 28th May 2018
+ Briefed about the assignment.
+ Learnt a little about GIS and photogrammetry.
+ Recevied a tutorial on git.

### Tuesday 29th May 2018
+ Researched on different ways to implement the module (gui, cli?).
+ Formed the basic arhitecture of the module.
+ Received a tutorial on photogrammetry.

    #### MODULE ARCHITECTURE
    
    RULES will be contained in a separate moduled named rules.py. Each rule will be
     implemented as a function, with a decorator to register the rule with the the main module.
    Each function name will also being with 'rule_' prefix. (rule_type, rule_size)
    
        rules = []
        @register_rule
        def register_rule(function):
            rules.append(function)
    PROCESSES will follow a similar layout. Processes will also have a similar decorator,
     and will be registered with a similar function.

    FILE TRANSFER will be handled using 'sftp' (SSH FTP) module.

### Wednesday 30th May 2018
+ Attended the general meeting.
+ Redesigned the module.

    #### MODULE ARCHITECTURE

    Watchdog module can be used to monitor any file/directory events, such as modification,
     deletion, creation.

    Using watchdog and sftp we could even make the process resume, from the position where
     it was last paused/terminated (Similar to dropbox sync).
    
    Also, to provide a control from skylark app, to pause the upload, we could use the concept
     of shared memory between the two processes, which would not only allow the module to work
     independently as a daemon/process, but will also allow the skylark app to gain access to
     the pause functionality.

### Thursday 31st May 2018
+ Implemented SFTP protocol and tested it on localhost SFTP server.
+ Was able to upload and download files on the SFTP server.
+ Implemented [sftpconn.py](https://bitbucket.org/EverWinter23/skynet/src/dev/lib/sftpcon.py) 
  module to maintain SSH connection to the remote SFTP server.
+ Started working on **mapping** a local foler to a remote folder on SFTP server.
+ Finished the [mapper.py](https://bitbucket.org/EverWinter23/skynet/src/dev/lib/mapper.py) 
  module.


### Friday 1st June 2018
+ Implemented [watcher.py](https://bitbucket.org/EverWinter23/skynet/src/dev/lib/watcher.py) 
  module - to watch over the local dir for any changes and take necessary action.
+ Implemented [handler.py](https://bitbucket.org/EverWinter23/skynet/src/dev/lib/handler.py) 
  module - to actually handle the transfers, and mimic them on the SFTP server.
+ Added support for ignoring the monitoring and trasnfer of some files like - swap files etc.

### Monday 4th June 2018
+ Started working on integrating persist-queue with handler.py module to make the module
  thread-safe, recoverable and disk based.
+ Integrated the persist-queue with the handler.py and the watcher.py module.
+ watcher.py and handler.py modules run independently of each other.
+ Syncing process is fault tolerant and recoverable now due to the above changes.
+ Attended a presentation on Drones and Data Acquistion

### Tuesday 5th June 2018
+ Started working on the main module -- 
  [skynet.py](https://bitbucket.org/EverWinter23/skynet/src/dev/lib/skynet.py) and its process
  flow.
+ Working on cli for generating config files using command line.
+ Attended a presentation on Color space and Digital photography.

### Wednesday 6th June 2018
+ Added support for the  for configuration of the SFTP connection using config.ini file.
+ Implemented a cli to generate the config file.
+ Started working on re-establishing connection b/w the local m/c and the SFTP server.
+ Learnt about Image Segmentation of GCP points.

### Thursday 7th June 2018
+ Ran coala --code linter, over the project. Made it compatible with pep8 guidelines.
+ Completed the skynet.py module.
+ When the connection is lost - the daemon keeps on trying to re-establish conn with the 
  SFTP server.

### Frdiay 8th June 2018
+ Add detailed decription about the changes made to incorporate recoverability to LOG.md.
+ Started working on adding support for port forwarding --because android's SFTP server runs
  on port 2222.
+ Test skynet.py --to check whether or not it works as expected using SFTP server.

### Monday 11th June 2018
+ skynet now supports port forwarding. 
+ Also added the capability to recover from conn loss mid-transfer, or mid-execution.
+ After the connection is lost, the daemon keeps on trying to re-establish the conn and
  is also able to resume from the state the during which the action was halted.
+ To further extend skynet, will start working on incorporating it with cloud storage services.

### 12th-13th June 2018
+ Leave of absence

### Thursday 14th June 2018
+ Started working on cloud integration.
+ Separated skynet from the underlying architecture, by making handler.py and sftpcon.py
  modules abstract, so that cloud services can be integrated easily.

### Friday 15th June 2018
+ started working on aws-s3 handler module.
+ started working on aws-s3 connection module.

### Monday 18th June 2018
+ Started working on syncing files already present in the folder, when the process is
  executed of the first time.
+ aws --uploaded a directory to a bucket
+ aws --downloaded a file from the same bucket

### Tuesday 19th June 2018
+ Now, when the module is executed for the very first time, it syncs the files already
  present in that folder --syncsnap.py.
+ Working on optimizing the Q, so that multiple actions corresponding to the same file
  are not recorded multiple times.
+ Went on a field trip and got to see how drones collected data.

### Wendnesday 20th June 2018
+ Finished s3con.py --handles connection and ops like move, delete, send to s3-bucket.
+ Started working on a cli for configurin s3-bucket service.
+ Attended weekly programming feedback session. 

### Thursday 21st June 2018
+ Started seperating skynet.py from sftpcon.py so that it can pretty much run with
  any cloud service.
+ skynet.py can now run with any cloud service, provided a 'XCon' class with methods
  _delete, _move and _send.

### Friday 22nd June 2018
+ Leave of absence

### 25th June 2018 Monday
+ Optimized the Q, no two actions, which are the same, cannot reside in
  the Q at the same time. Saves a lot of time, for big video files, mods
  during conn. loss.
+ Started porting code to windows.

### 26th June 2018 Tuesday
+ Ported the code to windows, everything works as expected ;-). A couple of changes had
  to be made.
+ Started working on README.md
+ Demo and Presentation of the main module.

### 27th June 2018 Wednesday
+ Researched on multi-part resumable uploads and how to implement them with the existing
  architecture.
+ Weekly Progress Meeting

### 28th June 2018 Thursday
+ Concept of chunking big files and assembling them at the storage side.
+ aws s3 multi-part uploads using boto3

### 29th June 2018 Friday
+ Worked on remote progress monitoring using local DB and hosted DB
+ Hosted a notification server on Heroku with Postgres

### 2nd July 2018 Monday
+ Django-app for notification and remote progress monitoring complete.
+ Working on notifier.py which will push the notifications to the DB server.

### 3rd July 2018 Tuesday
+ Completed notifier.py, now when an action is recorded in the Q, it also sends
  a notification to the remote DB using which we can monitor the progress.
+ The schema of the Database is [action, file(primary), status, not_time].
+ The contention b/w handler.py and notifier.py was resolved using sleep() method and
  will work for real-events in most cases.
+ Resumed working on multi-part resumable uploads.