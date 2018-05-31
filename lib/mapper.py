'''
31st may 2018 thursday
'''

# for remote SFTP server, whose path should be UNIX-style
import posixpath
# for native os
import os

import logger

class Mapper:
    """
    Maps a local dir to a remote dir on the SFTP server.

    parameters
        local_root:str
            top level dir location on the local machine
        
        local_dir:str
            dir to sync with the remote dir
        
        remote_root:str
            top level dir location on the remote server 
            NOTE:
                1. should start with a leading forward slash
                2. should be an absolute path, no tilde(~) notation
            
        remote_dir:str
            dir which will be synced to the local_dir
    
    attributes
        local_base:str
            the absolute path obtained using local_root and 
            local_dir's relative path
        
        remote_base:str
            the absolute path obtained using remote_root
            and remote_dir's relative path
            NOTE:
                use POSIX path, because remote server will 
                always use UNIX-style paths for SFTP      
    """
    def __init__(self, local_root, local_dir, remote_root, remote_dir):
        self.local_base = os.path.join(local_root, local_dir)
        
        if not os.path.isdir(self.local_base):
            logger.error("{} is not a vaild path.".format(self.local_base))
            exit()

        self.remote_base = posixpath.join(remote_base, remote_dir)
        
        logger.info("local base: {}".format(local_base))
        logger.info("remote base: {}".format(remote_base))
        logger.info("Changes in-> \'{}\' will be reflected in here-> \'{}\'".format(
            local_base, remote_base))
                