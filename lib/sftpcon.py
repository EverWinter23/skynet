'''
31st may 2018 thursday
'''

from pysftp import Connection, CnOpts
import os
import logging


class SFTPCon:
    """
    Maintains an SSH connection to a remote server using the pysftp lib.

    parameters
        host:str
            the hostname or IP of remote machine

        username:str
            your username at the remote machine

        password:str
            your password at the remote machine

        port:int
            the SSH port of the remote machine

        private_key
            path of the file containing the private SSH key

        private_key_pass:str
            password to use, if private_key is encrypted

        compression:boolean
            default False, use True to enable compression
    """

    def __init__(self, host, username=None, password=None, port=22,
                 private_key_file=None, private_key_password=None,
                 compression=False):

        self.ssh_prefix = None
        self.ssh_conn = None

        # connection options
        cnopts = CnOpts()
        cnopts.compression = compression
        # set hostkeys to None, if not provided
        if private_key_file is None:
            cnopts.hostkeys = None

        logging.info('hostname={}'.format(host))
        logging.info('username={}'.format(username))
        logging.info('password={}'.format(password))
        logging.info('port={}'.format(port))
        logging.info('private_key_file={}'.format(private_key_file))
        logging.info('private_key_password={}'.format(private_key_password))
        logging.info('compression={}'.format(compression))

        self.ssh_prefix = username + '@' + password

        if password == '':
            logging.debug('no password provided, using key auth...')
            try:
                self.ssh_conn = Connection(host, username=username,
                                           port=port,
                                           private_key_file=private_key_file,
                                           # Ignore LineLengthBear, PycodeStyleBear
                                           private_key_password=private_key_password,
                                           cnopts=cnopts)

            except Exception as error:
                logging.debug('key auth failed...')
                logging.error('cause: {}'.format(error))
                logging.info('please check the config file...')
                exit()

        if self.ssh_conn is None:
            try:
                self.ssh_conn = Connection(host, username=username, port=port,
                                           password=password, cnopts=cnopts)
            except Exception as error:
                logging.info('failed to connect to SFTP server...')
                logging.error('cause: {}'.format(error))
                logging.info('please check the config file...')
                logging.info('please ensure that SFTP server is running...')
                exit()


def main():
    # test settings
    import time
    start_time = time.time()

    hostname = 'localhost'
    username = 'frost'
    password = 'finch75'

    local_base = 'local_dir'
    remote_base = 'home/frost/remote_dir'
    conn = SFTPCon(host=hostname, username=username, password=password)

    try:
        conn.ssh_conn.put_r(local_path, remote_path)
    except Exception as error:
        conn.ssh_conn.mkdir(remote_path)
        conn.ssh_conn.put_r(local_path, remote_path)

    end_time = time.time()
    print('total time to transfer 12MB = {}s.'.format(end_time - start_time))


def get_remote_path(self, local_path):
    remote_relative = local_path[self._local_base_length:]
    return self._remote_base + remote_relative


# test module
if __name__ == '__main__':
    main()
