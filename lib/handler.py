'''
3rd june 2018 friday
'''

import logging
from persistqueue import FIFOSQLiteQueue as Q

# TODO: Support for windows
import os

# NOTE: We will duck the responsibility of handling exceptions, and
#       will pass that responsibility to the module using this class,
#       so that it can handle them the way it wants without anything
#       holding it back.
# Handling conn. exceptions becomes very important here.
class Handler:
    """
    Handles the transfers, and mimics them on the SFTP server.
    NOTE: Resource in this context refers to file or dir unless
          explicitly specified.

    parameters
        sftp_con
            An instance of SFTPCon class to transfer files and interact
            with the remote SFTP server.
        mapper
            An instance of Mapper class to map local files to their
            respective paths on the SFTP server.
    """

    def __init__(self, sftp_con, mapper):
        self.sftp_con = sftp_con
        self.mapper = mapper
        # NOTE: 
        #   auto_commit = False in this declaration, this ensures that
        #   when we deQ something from the Q, the change is not committed
        #   until and unless the action is completed.
        self._q = Q(path='skynet_db', auto_commit=False, multithreading=True)

    """
    Retrieve actions stored by watcher.py and execute them one by one.
    """
    def runner(self):
        while True:
            entry = self._q.get()
            try:
                if entry['action'] == 'send':
                    self.send_resource(entry['src_path'])
                elif entry['action'] == 'delete':
                    self.delete_resource(entry['src_path'])
                elif entry['action'] == 'move':
                    self.move_resource(entry['src_path'], entry['dest_path'])
                
                # commit changes, i.e. commit deQ
                self._q.task_done()
            except Exception as error:
                """
                NOTE:  Need for auto_commit to be False
                    This was what I was doing previously->which can lead to
                    an unforseen error.
                        Since,  I was enQing the action --at the end of the Q,
                        what if a 'send' action failed, and there was a 'move'/
                        'delete' action on the same file. 

                    Because an exception occured, while executing the action
                    we'll add it to the queue so that it may be re-executed 
                    again. This ensures that change is reflected in the remote
                    dir and not lost due to an error in connectivity.
                """
                # self._q.put(entry)
                logging.error('ERROR: {}'.format(error))
                logging.info('Exiting...')
                exit()

    """
    Transfers a resource(file) to the remote SFTP server.

    parameters
        src_path
            local path of the resource to be sent
    """
    def send_resource(self, src_path):
        remote_path = self.mapper.map_to_remote_path(src_path)
        # NOTE: For transferring any file, make sure all parent dir
        #       exist, if not make them.
        # mkdir -p: no errors if existing, make parent dirs as needed
        parent_path = os.path.split(remote_path)[0]
        cmd = 'mkdir -p "' + parent_path + '"'
        # TODO: Instead of executing, right away store the command
        #       Add thread to execute the commands
        
        self.sftp_con.ssh_conn.execute(cmd)
        self.sftp_con.ssh_conn.put(src_path, remote_path)
        logging.info("Executed: {}".format(cmd))


    """
    Deletes a resource on the remote SFTP server.
    
    parameters
        src_path
            local path of the resource to be deleted
    """
    def delete_resource(self, src_path):
        remote_path = self.mapper.map_to_remote_path(src_path)

        # NOTE: Very dangerous cmd, can delete everything inside a dir
        #       Use with CAUTION!
        # TODO: Will not use rm -rf for testing purposes
        # cmd = 'rm -rf "' + remote_path + '"'
        cmd = 'rm -rf "' + remote_path + '"' 
        self.sftp_con.ssh_conn.execute(cmd)
        logging.info("Executed: {}".format(cmd))


    """
    Moves a resource on the remote SFTP server.

    parameters
        src_path
            local path of the resource before it was moved
        
        dest_path
            local path of the resource after it was moved
    """
    def move_resource(self, src_path, dest_path):
        remote_src_path = self.mapper.map_to_remote_path(src_path)
        remote_dest_path = self.mapper.map_to_remote_path(dest_path)

        cmd = 'mv "' + remote_src_path + '" ' +  remote_dest_path + '"'
        self.sftp_con.ssh_conn.execute(cmd)
        logging.info("Executed: {}".format(cmd))

def main():
    pass
    
if __name__ == '__main__':
    main()