'''
31st may 2018 thursday
'''

from pysftp import Connection, CnOpts
import logging

import os


class SFTPCon:
    """
    Establishes SSH connection to a remote server and helps
    in sending, moving and deleting files on the remote server.

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
            default True, use True to disable compression
    """

    def __init__(self, host, username=None, password=None, port=22,
                 private_key_file=None, private_key_password=None,
                 compression=True):

        self._con = None

        # connection options
        cnopts = CnOpts()
        cnopts.compression = compression
        # set hostkeys to None, if not provided
        if private_key_file is None:
            cnopts.hostkeys = None

        if password is None:
            logging.debug('No password provided, using key auth.')
            # NOTE:
            #   Ducking exceptions, so that they can be handled
            #   by the main module however it wants.
            self._con = Connection(host=host, username=username,
                                   port=port,
                                   private_key_file=private_key_file,
                                   # Ignore LineLengthBear, PycodeStyleBear
                                   private_key_password=private_key_password,
                                   cnopts=cnopts)

        if self._con is None:
            self._con = Connection(host, username=username, port=port,
                                   password=password, cnopts=cnopts)

    def _send(self, src_path, remote_path):
        """
        Transfers a resource(file) to the remote SFTP server.

        parameters
            src_path
                local path of the resource to be sent

            remote_path
                mapped path of the src_path on the
                remote storage
        """
        # NOTE: For transferring any file, make sure all parent dir
        #       exist, if not make them.
        # mkdir -p: no errors if existing, make parent dirs as needed
        parent_path = os.path.split(remote_path)[0]
        cmd = 'mkdir -p "' + parent_path + '"'

        self._con.execute(cmd)
        self._con.put(src_path, remote_path)

    def _delete(self, remote_path):
        """
        Deletes a resource on the remote SFTP server.

        parameters
            remote_path
                path of the resource to be deleted on
                the remote storage
        """
        # NOTE: Very dangerous cmd, can delete everything inside a dir
        #       Use with CAUTION!
        cmd = 'rm -rf "' + remote_path + '"'
        self._con.execute(cmd)

    def _move(self, remote_src_path, remote_dest_path):
        """
        Moves a resource on the remote SFTP server.

        parameters
            remote_src_path
                remote path of the resource before it was moved

            remote_dest_path
                remote path of the resource after it was moved
        """
        # NOTE: For moving any file, make sure all parent dir
        #       exist, if not make them.
        # mkdir -p: no errors if existing, make parent dirs as needed
        parent_path = os.path.split(remote_dest_path)[0]
        cmd = 'mkdir -p "' + parent_path + '"'
        self._con.execute(cmd)

        cmd = 'mv "' + remote_src_path + '" "' + remote_dest_path + '"'
        self._con.execute(cmd)


def main():
    pass


if __name__ == '__main__':
    main()
