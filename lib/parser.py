'''
tuesday 5th june 2018
'''

from argparse import ArgumentParser

class Parser(ArgumentParser):
    def __init__(self, **kwargs):
        super(Parser, self).__init__(**kwargs)

        # display version
        self.add_argument("--version", action='store_true',
                          help="^ why is this lowercase? ;-)")

        # for configuring logging level
        self.add_argument("-loglvl", default='INFO',
                          choices=lvls,
                          help=help_log,
                          metavar='')

        # storage services supported
        self.add_argument("--with",
                          choices=services,
                          help=help_with,
                          metavar='')

        # for changing or generating config
        self.add_argument("--config",
                          help='Generate config file for the storage service.',
                          metavar='')

        # for specifying a specific config file for sftp
        self.add_argument("--sftp-file",
                          help='Specify a sftp-config file.',
                          metavar='')

        # for specifying a specific config file for aws-s3
        self.add_argument("--s3-file",
                          help='Specify a aws-s3 config file.',
                          metavar='')
                          
# parser help msgs, from here on out
lvls=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
help_log="""
Set logging level for the logger, logging messages 
which are less severe than the "specified level will 
be ignored. Valid options are """  + ', '.join(lvls) + "."

services = ['SFTP', 'AWS-S3']      
help_with="""
Select the remote storage service for syncing,
supported services are """ + ', '.join(services) + "."