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

def _get_config():
    """
    Return the path of the config file
    """
    return FILE_PATH


def _check_config():
    """
    Check whether the config file exists or not
    """
    return Path(FILE_PATH).exists()


def _config():
    """
    TODO: Add paths
    Looks for a 'config.ini' file in ->
        Linux/Mac:
        Windows:
    If the file is already present, it asks the user
    before it overwrites the file with new configuration.
    """
    # TODO: Absolute path for windows?
    if _check_config():
        print('A configuration file already exists.')
        print('Do you want to overwrite the existing configuration?')
        # ans = input('[yes/no]> ')
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
    ignore_patterns = (input('ignore_patterns = '))

    print(path_msg)
    local_dir = input('local dir = ')
    remote_dir = input('remote_dir = ')

    print(end_msg)
    print('\n\nSaving your configuration to \'{}\''.format(FILE_PATH))

    # start making the config.ini file from the input
    config = ConfigParser(allow_no_value=True)

    # NOTE:
    #   Every key-value pair that is of the form:
    #       Key: None
    #   are their to write the comments to the configuration file.
    #   Just makes the conifg while easier to edit.
    config['SERVER'] = {server_config: None,
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

    with open(FILE_PATH, 'w') as config_file:
        config.write(config_file)
    print('All done...')


def _version():
    """
    TODO: Add desc
    """
    author = 'Rishabh Mehta'
    email = 'eternal.blizzard23@gmail.com'
    print("{} v{}".format(SKYNET, VERSION))
    print("\n@author\n{}\n{}".format(author, email))
