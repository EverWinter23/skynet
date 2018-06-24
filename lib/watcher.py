'''
1st june 2018 friday
'''

import logging
from persistqueue import UniqueQ as Q
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import DirCreatedEvent
from watchdog.events import DirModifiedEvent
from watchdog.events import DirMovedEvent

class Watcher(PatternMatchingEventHandler):  # watcher on the wall
    """
    Watches a dir for any changes within that dir for any
    file system event (create, delete, rename, move etc...)
    and takes appropriate action.

    parameters
        complete_sync: boolean
            When True, files deleted in the local
            folder will also be deleted in the remote folder.
            When False, files deleted in the local
            folder will be retained in the remote folder.

        db_path: str
            path to the database where actions are
            stored.

    attributes
        _q: UniqueQ
            stores actions onto the disk using SQLiteDB
            for recoverability and fault tolerance.
    """

    def __init__(self,  db_path, complete_sync=False, **kwargs):
        super(Watcher, self).__init__(**kwargs)
        logging.info("Night gathers, and now my watch begins.")

        self.complete_sync = complete_sync
        # TODO: Path for database
        self._q = Q(path=db_path, auto_commit=True, multithreading=True)

    def on_created(self, event):
        """
        Called when a file or dir is created.

        NOTE: If a dir is created in the dir being monitored, there is no
        need to take any action for it.

        It will automatically be created on the remote SFTP server
        if it contains any file.
        """

        if not isinstance(event, DirCreatedEvent):
            logging.info("Recorded creation: {}".format(event.src_path))
            self._q.put({'action': 'send', 'src_path': event.src_path})

    def on_deleted(self, event):
        """
        Called when a file or dir is deleted.

        NOTE: It will only delete the files present on the remote dir
        which are not present in the local dir only if complete-sync
        is set to True.
        """

        if self.complete_sync:
            logging.info("Recorded deletion: {}".format(event.src_path))
            self._q.put({'action': 'delete', 'src_path': event.src_path})

    def on_modified(self, event):
        """
        Called when a file or dir is modified.

        NOTE: The mtime (modification time) of the directory
        changes only when a file or a subdirectory is added,
        removed or renamed.

        Modifying the contents of a file within the directory
        does not change the directory itself, nor does updating
        the mtime of a file or a subdirectory.

        Thus, if a dir is modified , no action will be taken.
        However, if a file is modified, we will send a the whole
        file, which will be overwritten in the remote dir.

        Sending the whole file is a viable option, because:
            1. Images have small sizes.
            2. Videos will not be modified.
        """

        if not isinstance(event, DirModifiedEvent):
            logging.info("Recorded modification: {}".format(event.src_path))
            self._q.put({'action': 'send', 'src_path': event.src_path})

    def on_moved(self, event):
        """
        Called when a file or dir is renamed or moved.
        """

        if not isinstance(event, DirMovedEvent):
            logging.info("Recorded move: \'{}\'->\'{}\'".format(
                event.src_path, event.dest_path))
            self._q.put({'action': 'move', 'src_path': event.src_path,
                        'dest_path': event.dest_path})
