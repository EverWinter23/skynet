'''
5th june 2018 tuesday
'''

import os
from configparser import ConfigParser
from pathlib import Path
from printmsgs import *

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

# TODO: Remove port -> no port forwarding? ANDROID???

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

    print(warning)
    # SERVER settings
    print(server_config)
    print(host_msg)
    remote_host = input('remote_host = ')       
    
    print(uid_msg)
    remote_username = input('remote_username = ')
    
    print(port_msg)
    remote_port = input('remote_port = ')

    print(passwd_msg)
    remote_password = input('remote_password = ')

    # SYNC settings
    print(sync_msg)
    print(complete_sync_msg)
    complete_sync = input('complete_sync = ')

    print(local_root_msg)    
    local_root = input('local_root = ')

    print(remote_root_msg)
    remote_root = input('remote root = ')
    
    print(ignore_msg)
    ignore_patterns = list(input('ignore_patterns = ').split(' '))

    print(path_msg)
    local_dir = input('local dir = ')
    remote_dir = input('remote_dir = ')

    print(end_msg)
    print('\n\nSaving your configuration to \'{}\''.format(FILE_PATH))
    
    # start making the config.ini file from the input
    config = ConfigParser(allow_no_value=True)
    
    config['SERVER'] = {server_config: None,    # writes comments to config file
                        host_msg: None,
                        'remote_host': remote_host,
                        uid_msg: None,
                        'remote_username': remote_username,
                        port_msg: None,
                        'remote_port': remote_port,
                        passwd_msg: None,
                        'remote_password': remote_password}

    config['SYNC'] = {sync_msg: None, 
                      local_root_msg: None,
                      'local_root': local_root,
                      ignore_msg: None,
                      'ignore_patterns': ignore_patterns,
                      remote_root_msg: None,
                      'remote_root': remote_root,
                      path_msg: None,
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