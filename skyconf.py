'''
5th june 2018 tuesday
'''

import os
import sys
from configparser import ConfigParser
from pathlib import Path
from printmsgs import *

# any changes to the version made here
SKYNET = 'skynet'
# TODO: Always mark version --1.5 marks resumable multipart uploads
VERSION = '1.5'
# name of config file
CONFIG_FILE = 'config.ini'
LOG_FILE = 'skynet.log'

HOME = str(Path.home())

DIR_PATH = os.path.join(HOME, SKYNET)

# database path
SKYNET_DB = 'skynet_db'
DB_PATH = os.path.join(DIR_PATH, SKYNET_DB)

# path for config file
# should work for both windows as well as linux, hopefully ;-)
FILE_PATH = os.path.join(DIR_PATH, CONFIG_FILE)

LOG_PATH = os.path.join(DIR_PATH, LOG_FILE)

# TODO: url of website which displays status updates.
# must start with https://
WEBSITE_URL = 'https://www.youtube.com'

# NOTE: Enter string literals for all services here
SFTP, S3 = 'SFTP', 'S3'
SERVICES = [SFTP, S3]


def _get_config():
    """
    Returns the path of the config file.
    """
    return FILE_PATH


def _check_config():
    """
    Check whether the config file exists or not.
    """
    return Path(FILE_PATH).exists()


def _load_config(file_path):
    """
    Change the default file path to the file specified.
    """
    global FILE_PATH
    FILE_PATH = file_path


def _db_path():
    """
    Returns the path of the database.
    """
    return DB_PATH


def _config(service):
    """
    TODO: Add paths
    Looks for a 'config.ini' file in ->
        Linux/Mac: ~/.skynet/config.ini
        Windows: TODO
    If the file is already present, it asks the user
    before it overwrites the file with new configuration.
    """
    if _check_config():
        print('A configuration file already exists.')
        print('Do you want to overwrite the existing configuration?')
        # ans = input('[yes/no]> ')
        ans = 'yes'
        if ans == 'no':
            sys.exit()
    if not Path(DIR_PATH).exists():
        os.makedirs(DIR_PATH)

    print(warning)
    if (service == S3):
        _s3_config()
    elif (service == SFTP):
        _sftp_config()
    _sync_config()

    print(end_msg)
    print('\n\nSaving your config to \'{}\''.format(FILE_PATH))


def _s3_config():
    print(s3config_msg)
    print(bucket_msg)
    bucket = input('bucket = ')

    print(keyid_msg)
    key_id = input('key_id = ')

    print(secret_msg)
    aws_secret = input('aws_secret = ')

    print(region_msg)
    region = (input('region = '))

    # start making the config.ini file from the input
    config = ConfigParser(allow_no_value=True)

    config['S3'] = {s3config_msg: None,
                    bucket_msg: None,
                    'bucket': bucket,
                    keyid_msg: None,
                    'key_id': key_id,
                    secret_msg: None,
                    'aws_secret': aws_secret,
                    region_msg: None,
                    'region': region}

    with open(FILE_PATH, 'w') as config_file:
        config.write(config_file)


def _sync_config():
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

    # append sync settings to config.ini file
    config = ConfigParser(allow_no_value=True)

    config['SYNC'] = {sync_msg: None,
                      complete_sync_msg: None,
                      'complete_sync': complete_sync,
                      local_root_msg: None,
                      'local_root': local_root,
                      ignore_msg: None,
                      'ignore_patterns': ignore_patterns,
                      remote_root_msg: None,
                      'remote_root': remote_root,
                      path_msg: None,
                      'local_dir': local_dir,
                      'remote_dir': remote_dir}

    with open(FILE_PATH, 'a') as config_file:
        config.write(config_file)


def _sftp_config():
    # SERVER settings
    print(sftp_config_msg)
    print(host_msg)
    remote_host = input('remote_host = ')

    print(uid_msg)
    remote_username = input('remote_username = ')

    print(port_msg)
    remote_port = input('remote_port = ')

    print(passwd_msg)
    remote_password = input('remote_password = ')

    # start making the config.ini file from the input
    config = ConfigParser(allow_no_value=True)

    # NOTE:
    #   Every key-value pair that is of the form:
    #       Key: None
    #   are their to write the comments to the configuration file.
    #   Just makes the conifg while easier to edit.
    config['SFTP'] = {sftp_config_msg: None,
                      host_msg: None,
                      'remote_host': remote_host,
                      uid_msg: None,
                      'remote_username': remote_username,
                      port_msg: None,
                      'remote_port': remote_port,
                      passwd_msg: None,
                      'remote_password': remote_password}

    with open(FILE_PATH, 'w') as config_file:
        config.write(config_file)


def _version():
    """
    TODO: Add desc
    """
    author = 'Rishabh Mehta'
    email = 'eternal.blizzard23@gmail.com'
    print("{} v{}".format(SKYNET, VERSION))
    print("\n@author\n{}\n{}".format(author, email))
