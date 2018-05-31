# JOURNAL
Internship Journal.

### Monday 28th May 2018
+ Briefed about the assignment.

+ Learnt a little about GIS and photogrammetry.

+ Recevied a tutorial on git.

### Tuesday 29th May 2018
+ Researched on different ways to implement the module -- gui, cli.
+ Formed the basic arhitecture of the module. (will be using cli to implement the module)
+ Received a tutorial on photogrammetry.

    #### MODULE ARCHITECTURE
    
    RULES will be contained in a separate moduled named rules.py. Each rule will be implemented as a fucntion, with a decorator to register the rule with the the main module.
    Each function name will also being with 'rule_' prefix. (rule_type, rule_size)
    
        rules = []
        @register_rule
        def register_rule(function):
            rules.append(function)
    PROCESSES will follow a similar layout. Processes will also have a similar decorator, and will be registered with a similar function.

    FILE TRANSFER will be handled using 'sftp' (SSH FTP) module.
