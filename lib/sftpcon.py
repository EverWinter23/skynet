'''
31st may 2018 thursday
'''

import pysftp, logging, os

# setup logging
logFormat='%(levelname)s: %(message)s'
logging.basicConfig(filename='skynet.log',level=logging.DEBUG, 
                    filemode='a', format=logFormat)

logger = logging.getLogger('skynet')

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
            password to use, if private_key is encrypted.

        compression:boolean
            default False, use True to enable compression

        default_path
            set a default path upon connection.
    """
    def __init__(self, host, username = None, password = None, port = 22, 
                 private_key_file = None, private_key_password = None,
                 compression = False, default_path = None):
        
        self.ssh_prefix = None
        self.ssh_conn = None

        # connection options
        cnopts = pysftp.CnOpts()
        cnopts.compression = compression
        # set hostkeys to None, if not provided
        if private_key_file is None:
            cnopts.hostkeys = None

        logger.info('Initializing connection with the following information...')
        logger.info('hostname: {}'.format(host))
        logger.info('username: {}'.format(username))
        logger.info('password: {}'.format(password))
        logger.info('port: {}'.format(port))
        logger.info('private_key_file: {}'.format(private_key_file))
        logger.info('private_key_password: {}'.format(private_key_password))
        logger.info('compression: {}'.format(compression))
        logger.info('defaultpath: {}'.format(default_path))

        self.ssh_prefix = username + '@' + password
        
        if password == '':
            logger.debug('No password provided, using key auth...')
            try:
                self.ssh_conn = pysftp.Connection(host, username=username, port=port, 
                                                  private_key_file = private_key_file,
                                                  private_key_password = private_key_password,
                                                  cnopts=cnopts, default_path = default_path)

            except Exception as error:
                logger.debug('Key auth failed...')
                logger.error('Cause: {}'.format(error))
                logger.info('Please check the config file...')
                exit()

        if self.ssh_conn is None:
            try:
                self.ssh_conn = pysftp.Connection(host, username=username, port=port,
                                                  password = password,
                                                  cnopts=cnopts, default_path = default_path)
            except Exception as error:
                logger.debug('Failed to connect to SFTP server...')
                logger.error('Cause: {}'.format(error))
                logger.info('Please check the config file...')
                logger.info('Please ensure that SFTP server is running...')
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
    except:
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






