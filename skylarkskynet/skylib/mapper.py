'''
31st may 2018 thursday
'''

# for remote SFTP server, path should be UNIX-style
import posixpath
# for native os
import os
import sys
import logging

# checks wheather native os is Windows
IS_WIN = sys.platform.startswith('win')


class Mapper:
    """
    Maps a local dir to a remote dir on the SFTP server.

    parameters
        local_root: str
            top level dir location on the local machine
        local_dir: str
            dir to sync with the remote dir
        remote_root: str
            top level dir location on the remote server
            NOTE:
                1. should start with a leading forward slash
                2. should be an absolute path, no tilde(~) notation
        remote_dir: str
            dir which will be synced to the local_dir

    attributes
        local_base: str
            the absolute path obtained using local_root and
            local_dir's relative path
        remote_base: str
            the absolute path obtained using remote_root
            and remote_dir's relative path
            NOTE:
                use POSIX path, because remote server will
                always use UNIX-style paths for SFTP
    """

    def __init__(self, local_root, local_dir, remote_root, remote_dir):
        self.local_base = os.path.join(local_root, local_dir)
        self.remote_base = posixpath.join(remote_root, remote_dir)

        logging.info("local_base: {}".format(self.local_base))
        logging.info("remote_base: {}".format(self.remote_base))
        logging.info("Changes in-> \'{}\' will reflect here-> \'{}\'".format(
            self.local_base, self.remote_base))

    def map_to_remote_path(self, local_path):
        """
        Maps a local path in the dir being monitored to a remote path
        on the SFTP server to reflect the changes.

        parameters
            local_path: str
                the FULL path of the resource on the local filesystem

        returns
            remote_path: str
                the FULL path of the resource on the remote filesystem
        """
        # strips the local_base from the local_path to get the relative path
        # Example->
        #   local_base = Stuff
        #   remote_base = Sync
        #   local_path = Stuff/tech-crunch/file.txt
        #   relative_path = tech-crunch/file.txt
        #   remote_path = Sync/tech-crunch/file.txt
        relative_path = local_path[len(self.local_base):]

        if IS_WIN:  # for windows
            relative_path = relative_path.replace('\\', '/')

        remote_path = self.remote_base + relative_path

        logging.info("Mapped local_path->\'{}\' to remote_path->\'{}\'".format(
            local_path, remote_path))

        return remote_path


def main():
    pass


# test module
if __name__ == '__main__':
    main()
