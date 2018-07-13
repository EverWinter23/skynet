'''
20th june 2018 tuesday
'''

import logging
import os
from watchdog.utils.dirsnapshot import DirectorySnapshot
from persistqueue import UniqueQ as Q


class SyncSnap():
    """
    The SyncSnap class records all the files present in
    the directory initially and pushes them onto the Q.

    parameters
        _dir_path: Mapper
            the path to the dir which is to be uploaded
            to the remote storage.

    attributes
        _q: UniqueQ
            retrieves actions stored by the wathcer in the
            Q and executes them when the connection exists.
    """

    def __init__(self, dir_path):
        # taking a snapshot of the current directory
        self._snap_dir = DirectorySnapshot(dir_path)

    def _first_sync(self, db_path):
        """
        This method records all the files present in the
        directory initially and pushes them onto the Q.
        It is only called once for each mapping, and never
        again after the database for that path has been
        established.

        parameters:
            db_path: str
                path to the database where actions are
                stored.
        """
        self._q = Q(path=db_path, auto_commit=True, multithreading=True)
        logging.info("Syncing folders already present in the dir.")
        for path in self._snap_dir.paths:
            if os.path.isdir(path) is False:
                logging.info("Recorded resource: {}".format(path))
                self._q.put({'action': 'send', 'src_path': path})

    def sync(self):
        print(self.snap_dir.paths)
