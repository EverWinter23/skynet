'''
3rd june 2018 friday
'''
from logger import logger
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
        TODO: Add desc ;-)
        sftp_con

        mapper
    """

    def __init__(self, sftp_con, mapper):
        self.sftp_con = sftp_con
        self.mapper = mapper

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
        logger.info("Executed: {}".format(cmd))


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
        cmd = 'rm "' + remote_path + '"' 
        # self.sftp_con.ssh_conn.execute(cmd)
        logger.info("Executed: {}".format(cmd))


    """
    Moves a resource on the remote SFTP server.

    parameters
        src_path
            local path of the resource before it was moved
        
        des_path
            local path of the resource after it was moved
    """
    def move_resource(self, src_path, dest_path):
        remote_src_path = self.mapper.map_to_remote_path(src_path)
        remote_des_path = self.mapper.map_to_remote_path(dest_path)

        cmd = 'mv "' + remote_src_path + '" ' +  remote_des_path + '"'
        self.sftp_con.ssh_conn.execute(cmd)
        logger.info("Executed: {}".format(cmd))

# test module
def main():
    import time
    from watcher import Watcher
    from mapper import Mapper
    from sftpcon import SFTPCon
    from watchdog.observers import Observer

    # test settings    
    hostname = 'localhost'
    username = 'frost'
    password = 'finch75'

    local_root = '/home/frost/Code'
    local_dir = 'test'
    remote_dir = 'Stuff'
    remote_root = '/home/frost'
    ignore_patterns = ['*.swp', '*.tmp']

    conn = SFTPCon(host=hostname, username=username, password=password)

    mapper = Mapper(local_root, local_dir, remote_root, remote_dir)
    handler = Handler(conn, mapper)
    watcher = Watcher(handler, complete_sync=False,ignore_patterns=ignore_patterns)

    observer = Observer()
    # NOTE: Please be aware of local_root and local_base
    observer.schedule(watcher, path=mapper.local_base, recursive=True)

    # TODO: Please be aware of inotify exception
    """
    You can set a new limit temporary with:
        $ sudo sysctl fs.inotify.max_user_watches=524288
        $ sudo sysctl -p

    If you like to make your limit permanent, use:
        $ echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
        $ sudo sysctl -p
    """
    try:
        observer.start()
    except Exception as error:
        logger.info('exiting...')
        logger.info('Cause: {}'.format(error))
        exit()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    
if __name__ == '__main__':
    main()