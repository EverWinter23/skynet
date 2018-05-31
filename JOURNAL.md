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
    
    RULES will be contained in a separate moduled named rules.py. Each rule will be implemented as a function, with a decorator to register the rule with the the main module.
    Each function name will also being with 'rule_' prefix. (rule_type, rule_size)
    
        rules = []
        @register_rule
        def register_rule(function):
            rules.append(function)
    PROCESSES will follow a similar layout. Processes will also have a similar decorator, and will be registered with a similar function.

    FILE TRANSFER will be handled using 'sftp' (SSH FTP) module.

### Wednesday 30th May 2018
+ Attended the general meeting.
+ Redesigned the module.

    #### MODULE ARCHITECTURE

    Watchdog module can be used to monitor any file/directory events, such as modification, deletion, creation.

    Using watchdog and sftp we could even make the process resume, from the position where it was last paused/terminated (Similar to dropbox sync).
    
    Also, to provide a control from skylark app, to pause the upload, we could use the concept of shared memory between the two processes, which would not only allow the module to work independently as a daemon/process, but will also allow the skylark app to gain access to the pause functionality.

### Thursday 31st May 2018
+ Implemented SFTP protocol and tested it on localhost SFTP server.
+ Was able to upload and download files on the SFTP server.
+ Implemented [sftpconn.py](https://bitbucket.org/EverWinter23/skynet/src/dev/lib/sftpcon.py) module to maintain SSH connection to the remote SFTP server.
+ Started working on **mapping** a local foler to a remote folder on SFTP server.
+ Finished the [mapper.py](https://bitbucket.org/EverWinter23/skynet/src/dev/lib/mapper.py) module.