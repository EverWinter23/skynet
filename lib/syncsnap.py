'''
20th june 2018 tuesday
'''

import logging
from watchdog.utils.dirsnapshot import DirectorySnapshot
from persistqueue import UniqueQ as Q


class SyncSnap():
    """
    TODO
    attributes
    _q: UniqueQ
        retrieves actions stored by the wathcer in the
        Q and executes them when the connection exists.
    """

    def __init__(self, dir_path):
        # taking a snapshot of the current directory
        self._snap_dir = DirectorySnapshot(dir_path)

    def _first_sync(self, db_path):
        self._q = Q(path=db_path, auto_commit=True, multithreading=True)
        logging.info("Syncing folders already present in the dir.")
        for path in self._snap_dir.paths:
            logging.info("Recorded resource: {}".format(path))
            self._q.put({'action': 'send', 'src_path': path})

    def sync(self):
        print(self.snap_dir.paths)
