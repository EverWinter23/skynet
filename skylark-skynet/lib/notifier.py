'''
2nd july 2018 monday
'''
import os
import shelve
import logging
from . import queries
import psycopg2
from threading import Thread
from persistqueue import UniqueQ as Q

# read database connection url from the env variable
DATABASE_URL = os.environ.get('DATABASE_URL')
CURSOR = 'cursor'
CURSOR_FILE = 'do_not_remove'


class Notifier(Thread):
    """
    Sends updates to a remote DB for progress
    monitoring.

    parameters
        db_path: str
            path to the database where actions are stored.

    attributes
        _q: UniqueQ
            retrieves actions stored by the wathcer in the
            Q and executes them when the connection exists.
    """

    def __init__(self, db_path):
        Thread.__init__(self)
        self._q = Q(path=db_path, auto_commit=False, multithreading=True)
        self._cursor = shelve.open(os.path.join(db_path, CURSOR_FILE),
                                   flag='c', protocol=None, writeback=True)

        self._is_running = False
        self._con = psycopg2.connect(DATABASE_URL)

        # turn on autocommit, so we don't have to commit each query we execute
        self._con.autocommit = True

    def _update_status(self):
        """
        Changes the current status of the notifier.
        """
        self._is_running = not self._is_running

    def run(self):
        """
        Reads actions stored by the Watcher and sends a
        corresponding notification for each one.
        """
        self._update_status()

        cur = self._con.cursor()

        # skip already pushed notifications
        self._load_cursor()
        for i in range(self._cursor[CURSOR]):
            self._q.get()

        logging.info('Pushing notifs.')
        # push notifications which have not been pushed yet
        while True:
            entry = self._q.get()
            try:    # avoids duplicate entries corresponding to a file
                cur.execute(queries._new_notif(
                    entry['action'], entry['src_path'],
                    os.stat(entry['src_path']).st_size))

                logging.info(
                    'New Notification: \'{}\''.format(entry['src_path']))
            except psycopg2.IntegrityError as error:
                logging.info('Notif exists, updating notif: \'{}\''.format(
                    entry['src_path'], os.stat(entry['src_path']).st_size))
                cur.execute(queries._update_notif(entry['src_path']))
            self._increment_cursor()

    def _mark_complete(self, entry):
        """
        Updates 'status' of a notification to COMPLETE.
        """
        logging.info('Marking COMPLETE:\'{}\''.format(entry['src_path']))
        with self._con.cursor() as cursor:
            cursor.execute(queries._mark_complete(entry['src_path']))

    def _mark_processing(self, entry):
        """
        Updates 'status' of a notification to PROCESSING.
        """
        logging.info('Marking PROCESSING:\'{}\''.format(entry['src_path']))
        with self._con.cursor() as cursor:
            cursor.execute(queries._mark_processing(entry['src_path']))

    def _mark_part(self, entry):
        """
        Updates number of 'parts' uploaded of mulitpart uploads.
        """
        with self._con.cursor() as cursor:
            cursor.execute(queries._mark_part)

    def _load_cursor(self):
        """
        Loads the cursor which points to the action
        for which notification.
        """
        if CURSOR not in self._cursor:
            self._cursor[CURSOR] = 0
            self._cursor.sync()
            logging.info("Initialized cursor to 0.")

    def _increment_cursor(self):
        """
        Increment the cursor, indicating that the notification
        for the event has been sent.
        """
        self._cursor[CURSOR] += 1
        self._cursor.sync()

    def _decrement_cursor(self):
        """
        Decrement the cursor, for relative positioning as
        items from the Q are also being deQ'd at the same
        time.
        """
        self._cursor[CURSOR] -= 1
        self._cursor.sync()
