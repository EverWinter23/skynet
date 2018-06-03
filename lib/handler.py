'''
3rd june 2018 friday
'''
from logger import logger

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

    def __init__(sftp_con, mapper):
        self.sftp_con = sftp_con
        self.mapper = mapper

    """
    Transfers a resource(file) to the remote SFTP server.

    parameters
        src_path
            local path of the resource to be sent
    """
    def send_resource(src_path):
        remote_path = mapper.map_to_remote_path(src_path)

        cmd = 'mkdir -p "' + remote_path + '"'
        # TODO: Instead of executing, right away store the command
        #       Add thread to execute the commands
        
        self.sftp_con.ssh_conn.execute(cmd)
        logger.info("executed: {}".format(cmd))


    """
    Deletes a resource on the remote SFTP server.
    
    parameters
        src_path
            local path of the resource to be deleted
    """
    def delete_resource(src_path):
        remote_path = mapper.map_to_remote_path(src_path)

        # NOTE: Very dangerous cmd, can delete everything inside a dir
        #       Use with CAUTION!
        # TODO: Will not use rm -rf for testing purposes
        # cmd = 'rm -rf "' + remote_path + '"'
        cmd = 'rm "' + remote_path + '"' 
        self.sftp_con.ssh_conn.execute(cmd)
        logger.info("executed: {}".format(cmd))


    """
    Moves a resource on the remote SFTP server.

    parameters
        src_path
            local path of the resource before it was moved
        
        des_path
            local path of the resource after it was moved
    """
    def move_resource(src_path, dest_path):
        remote_src_path = mapper.map_to_remote_path(src_path)
        remote_des_path = mapper.map_to_remote_path(dest_path)

        cmd = 'mv "' + remote_src_path + '" ' +  remote_des_path + '"'
        self.sftp_con.ssh_conn.execute(cmd)
        logger.info("executed: {}".format(cmd))