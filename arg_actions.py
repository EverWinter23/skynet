'''
5th june 2018 tuesday
'''

import os
from configparser import ConfigParser
from pathlib import Path


# any changes to the version made here
SKYNET = 'skynet'
VERSION = '1.0'
# name of config file
CONFIG_FILE = 'config.ini'
HOME = str(Path.home())

# TODO: for now, later will change the dir path
DIR_PATH = os.path.join(HOME, SKYNET)

# path for config file
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
        #ans = input('[yes/no]> ')
        ans = 'yes'
        if ans == 'no':
            exit()
    if not Path(DIR_PATH).exists():
        os.makedirs(DIR_PATH)

    print("WARNING: We're assuming that the user knows what he's doing,\n\
         and thus there are no IO checks for empty/wrong inputs.\n\n")
    # actual configuration starts here...
    print('================= Sever Configuration =================')
    print('Hostname or IP address of the remote server.')
    remote_host = input('remote_host = ')       
    
    print('\nSSH username for the remote server.')
    remote_username = input('remote_username = ')
    
    print('\nTCP port for the SSH server on the remote machine')
    print('The default port is 22: ')
    remote_port = input('remote_port = ')

    print('\nSSH password for the remote server.')
    remote_password = input('remote_password = ')

    print('\n\n================= Sync Configuration =================')
    print('Trailing slashes are optional.')
    print('The local path specified here should be relative to the top lvl dir.')
    print('Please see LOG.md for further details on configuration settings.')

    print('\n\nPath of the top level dir location on the local machine.')
    print('Should be an absolute path, relative paths may lead to errors.')
    print('Tilde notation is acceptable.')
    local_root = input('local_root = ')


    print('\n\nTop level directory location on the remote server.')
    print('Should be an absolute path -- without tilde notation.')
    print('Should start with leading slashes.')
    print('Should use UNIX-style forward slashes, since the remote server')
    print('will be accessed via SFTP.')
    remote_root = input('remote root = ')
    
    print('\n\nFiles matching these patterns will be not be uploaded to the server.')
    print('Temporary files --swap files should be ignored.')
    print('Example input> *.swp *.tmp')
    print('WARNING-------------^-PLEASE separate multiple entries with a single space.')
    ignore_patterns = list(input('ignore_patterns = ').split(' '))

    print('\n\nThe following paths should not contain leading slashes.')
    print('local_dir should be located relative to the local_root path.')
    print('remote_dir should be located relative to the remote_root path')
    local_dir = input('local dir = ')
    remote_dir = input('remote_dir = ')

    print('\n\nSaving your configuration to \'{}\''.format(FILE_PATH))
    print('NOTE: If you have made any mistake during the configuration,')
    print('you can edit this file or use the cli to generate a new one for you.')
    
    # start making the config.ini file from the input
    config = ConfigParser(allow_no_value=True)
    
    config['SERVER'] = {'remote_host': remote_host,
                        'remote_username': remote_username,
                        'remote_port': remote_port,
                        'remote_password': remote_password}

    config['SYNC'] = {'local_root': local_root,
                      'ignore_patterns': ignore_patterns,
                      'remote_root': remote_root,
                      'local_dir': local_dir,
                      'remote_dir': remote_dir}
    """
    config.add_section('SERVER')
    config.set('SERVER', '# rabid')    
    """
    with open(FILE_PATH, 'w') as config_file:
        config.write(config_file)
    print('All done...')



def _version():
    author= 'Rishabh Mehta'
    email = 'eternal.blizzard23@gmail.com'
    print("{} v{}".format(SKYNET, VERSION))
    print("\n@author\n{}\n{}".format(author, email))