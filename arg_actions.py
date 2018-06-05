'''
5th june 2018 tuesday
'''

import os
import configparser
from pathlib import Path


# any changes to the version made here
SKYNET = 'skynet'
VERSION = '1.0'
CONFIG_FILE = 'config.ini'
# TODO: for now, later will change the dir path
DIR_PATH = os.path.join(HOME, SKYNET)
# path for config file
HOME = str(Path.home())
# should work for both windows as well as linux, hopefully ;-)
FILE_PATH = os.path.join(DIR_PATH, CONFIG_FILE)

"""
Looks for a 'config.ini' file in ->
    Linux/Mac:
    Windows:
If the file is already present, it asks the user 
before it overwrites the file with new configuration.
"""
def _config():
    # TODO: Absolute path for windows?
    file = Path(FILE_PATH)
    if file.exists():
        print('A configuration file already exists.')
        print('Do you want to overwrite the existing configuration?')
        ans = input('[yes/no]> ')
        if ans == 'no':
            exit()
    if not Path(DIR_PATH).exists():
        os.makedirs(DIR_PATH)

    with open(file, 'w') as config_file:
        # actual configuration starts here...
        print('================= Sever Configuration =================')
        print('Hostname or IP address of the remote server.')
        remote_host = input('remote_host = ')       
        
        print('SSH username for the remote server.')
        remote_username = input('remote_username = ')
        
        print('TCP port for the SSH server on the remote machine')
        print('NOTE: The default port is 22: ')
        remote_port = input('remote_port = ')

        print('SSH password for the remote server.')
        remote_password = input('remote_password = ')

        print('================= Sync Configuration =================')
        print('NOTE:\n\tTrailing slashes are optional.\n\
              \tThe local path specified here should be relative to the top lvl dir.\n\
              \tPlease see LOG.md for further details on configuration settings.')

        print('\n\nNOTE:\n\tPath of the top level dir location on the local machine.\n\
              \tShould be an absolute path, relative paths may lead to errors.\n\
              \tTilde notation is acceptable.')
        local_root = input('local_root = ')

        print('\n\nFiles matching these patterns will be not be uploaded to the server.\n\
               NOTE:\n\tTemporary files --swap files should be ignored.\n\
               \tExample input> *.swp, *.tmp\n\
               \----------------------^Please separate multiple entries with a single\
                space.')
        ignore_patterns = list(input.split(', '))

        print('\n\nNOTE:\n\tTop level directory location on the remote server.\n\
              \tShould be an absolute path -- without tilde notation.\n\
              \tShould start with leading slashes.\n\
              \tShould use UNIX-style forward slashes, since the remote server will be \
               accessed via SFTP.')
        remote_root = input('remote root = ')
        
        print ('\n\nNOTE:\n\tThe following paths should not contain leading slashes.\n\
                \tlocal_dir should be located relative to the local_root path.\n\
                \tremote_dir should be located relative to the remote_root path')
        local_dir = input('local dir = ')
        remote_dir = input('remote_dir = ')

def _version():
    author= 'Rishabh Mehta'
    email = 'eternal.blizzard23@gmail.com'
    print("{} v{}".format(SKYNET, VERSION))
    print("\n@author\n{}\n{}".format(author, email))