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
    parameters
        db_path: str
            path to the database where actions are stored.
    attributes
        TODO
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
                cur.execute(queries._new_notif(entry))
                logging.info('New Notification: \'{}\''.format(entry['src_path']))
            except psycopg2.IntegrityError as error:
                logging.info('Notif exists, updating notif: \'{}\''.format(
                    entry['src_path']))
                cur.execute(queries._update_notif(entry))
            self._increment_cursor()
    
    def _mark_complete(self, entry):
        logging.info('Marking COMPLETE:\'{}\''.format(entry['src_path']))
        with self._con.cursor() as cursor:
            cursor.execute(queries._mark_complete(entry))
    
    def _mark_processing(self, entry):
        logging.info('Marking PROCESSING:\'{}\''.format(entry['src_path']))
        with self._con.cursor() as cursor:
            cursor.execute(queries._mark_processing(entry))

    def _load_cursor(self):
        if CURSOR not in self._cursor:
            self._cursor[CURSOR] = 0
            self._cursor.sync()
            logging.info("Initialized cursor to 0.")

    def _increment_cursor(self):
        self._cursor[CURSOR] += 1
        self._cursor.sync()

        
    def _decrement_cursor(self):
        self._cursor[CURSOR] -= 1
        self._cursor.sync()
