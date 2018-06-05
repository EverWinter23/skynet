'''
tuesday 5th june 2108
'''

import arg_actions
import lib.logger as log
from lib.mapper import Mapper
from lib.sftpcon import SFTPCon
from lib.watcher import Watcher
from lib.handler import Handler
from lib.parser import Parser

class SkyNet:
    """
    """
    def __init__():
        pass

# generate config file using command-line interface
def main():
    parser = Parser(description='Syncs a local folder to a remote folder\
                                 on the SFTP server.')

    args = parser.parse_args()

    if args.config: 
        arg_actions._config()
    if args.version:
        arg_actions._version()

if __name__ == '__main__':
    main()