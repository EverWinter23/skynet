'''
tuesday 5th june 2018
'''

from argparse import ArgumentParser

# NOTE: Enter string literals for all services here
SFTP, S3 = 'SFTP', 'S3'

# parser help msgs, from here on out
lvls = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
help_log = """
Set logging level for the logger, logging messages
which are less severe than the "specified level will
be ignored. Valid options are """ + ', '.join(lvls) + "."

services = [SFTP, S3]
help_with = """
Select the remote storage service for syncing,
supported services are """ + ', '.join(services) + "."

help_config = """
Generates config file for the specified service using cli.
Supported services are
""" + ', '.join(services) + "."


class Parser(ArgumentParser):
    def __init__(self, **kwargs):
        super(Parser, self).__init__(**kwargs)

        # display version
        self.add_argument("--version", action='store_true',
                          help="^--- Why is this lowercase? ;(")

        # for configuring logging level
        self.add_argument("--loglvl", default='INFO',
                          choices=lvls,
                          help=help_log,
                          metavar='LEVEL')

        # storage services supported
        self.add_argument("--run-with",
                          choices=services,
                          help=help_with,
                          metavar='SERVICE')

        # for changing or generating config
        self.add_argument("--config",
                          help=help_config,
                          metavar='SERVICE')

        # for specifying a specific config file for sftp
        self.add_argument("--config-file",
                          help='One file to rule them all ;p',
                          metavar='FILE')
