'''
3rd june 2018 friday
'''

from threading import Thread
import logging
from persistqueue import FIFOSQLiteQueue as Q


# NOTE: We will duck the responsibility of handling exceptions, and
#       will pass that responsibility to the module using this class,
#       so that it can handle them the way it wants without anything
#       holding it back.
# Handling conn. exceptions becomes very important here.


class Handler(Thread):
    """
    The Handler class actually handles the transfers
    between the local storage and the remote storage.

    NOTE: Resource in this context refers to file or dir
    unless explicitly specified.

    parameters
        mapper: Mapper
            an instance of Mapper class to map local files
            to their respective paths on the SFTP server.

        db_path: str
            path to the database where actions are
            stored.

    attributes
        _is_running: boolean
            indicates the current status of the thread

        _q: FFIOSQLiteQueue
            retrieves actions stored by the wathcer in the
            Q and executes them when the connection exists.
    """

    def __init__(self, mapper, db_path):
        Thread.__init__(self)
        self._is_running = False
        self.mapper = mapper
        # NOTE:
        #   auto_commit = False in this declaration, this ensures that
        #   when we deQ something from the Q, the change is not committed
        #   until and unless the action is completed.
        self._q = Q(path=db_path, auto_commit=False, multithreading=True)
        self.con = None

    def _schedule(self, con):
        """
        parameters
            sftpcon: SFTPCon | S3Con
                An instance of SFTPCon or S3Con class to
                transfer files and interact with the remote
                storage.
        """
        self.con = con

    def _update_status(self):
        """
        Changes the current status of the handler.
        """
        self._is_running = not self._is_running

    def send_resource(self, src_path):
        """
        Transfers a resource(file) to the remote SFTP server.

        parameters
            src_path
                local path of the resource to be sent
        """
        remote_path = self.mapper.map_to_remote_path(src_path)
        self.con._send(src_path, remote_path)

    def delete_resource(self, src_path):
        """
        Deletes a resource on the remote SFTP server.

        parameters
            src_path
                local path of the resource to be deleted
        """
        remote_path = self.mapper.map_to_remote_path(src_path)
        self.con._delete(remote_path)

    def move_resource(self, src_path, dest_path):
        """
        Moves a resource on the remote SFTP server.

        parameters
            src_path
                local path of the resource before it was moved

            dest_path
                local path of the resource after it was moved
        """
        remote_src_path = self.mapper.map_to_remote_path(src_path)
        remote_dest_path = self.mapper.map_to_remote_path(dest_path)
        self.con._move(remote_src_path, remote_dest_path)

    def run(self):
        """
        Retrieves actions stored by the Watcher and execute them one by one.
        """
        self._update_status()

        while True:
            entry = self._q.get()
            try:
                if entry['action'] == 'send':
                    logging.info('Sending resource.')
                    self.send_resource(entry['src_path'])
                    logging.info('Resource sent.')

                elif entry['action'] == 'delete':
                    logging.info('Deleting resource.')
                    self.delete_resource(entry['src_path'])
                    logging.info('Deleting resource.')

                elif entry['action'] == 'move':
                    logging.info('Moving resource.')
                    self.move_resource(entry['src_path'], entry['dest_path'])
                    logging.info('Moving resource.')

                # commit changes, i.e. commit deQ
                self._q.task_done()
                logging.info("Commited change to the DB.")

            except FileNotFoundError as error:
                '''
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
                '''
                # self._q.put(entry)
                logging.error('ERROR: {}'.format(error))
                logging.info('Continuing gracefully.')

            except IsADirectoryError as error:
                logging.error('ERROR: {}'.format(error))
                logging.info('Continuing gracefully.')

            except Exception as error:
                # mostly connection errors
                logging.error('ERROR: {}'.format(error))
                logging.info('Handler stopping thread.')
                self._update_status()
                return


def main():
    pass


if __name__ == '__main__':
    main()
