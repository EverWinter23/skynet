'''
2nd july 2018 monday
'''
import os
import shelve
import logging
import queries
import psycopg2
from threading import Thread
from persistqueue import UniqueQ as Q

# read database connection url from the env variable
DATABASE_URL = os.environ.get('DATABASE_URL')
CURSOR = 'cursor'


class Notifier(Thread):
    """
    parameters
        db_path: str
            path to the database where actions are stored.

        cursor_path: str
            path to the cursor file which stores the cursor
            into the notification database

    attributes
        TODO
    """

    def __init__(self, db_path, cursor_path):
        Thread.__init__(self)
        self._q = Q(path=db_path, auto_commit=False, multithreading=True)

        self._cursor = shelve.open(cursor_path, flag='c', protocol=None,
                                   writeback=True)
        self._is_running = False

    def _update_status(self):
        """
        Changes the current status of the notifier.
        """
        self._is_running = not self._is_running

    def run(self):
        self._update_status()

        con = psycopg2.connect(DATABASE_URL)
        # turn on autocommit, so we don't have to commit each query we execute
        con.autocommit = True
        cur = con.cursor()

        # skip already pushed notifications
        for i in range(self._cursor[CURSOR]):
            self._q.get()

        # push notifications which have not been pushed yet
        while True:
            entry = self._q.get()
            if entry['action'] == 'send':
                cur.execute(queries._send(entry))
                self._increment_cursor()

            elif entry['action'] == 'delete':
                cur.execute(queries._delete(entry))
                self._increment_cursor()

            elif entry['action'] == 'move':
                cur.execute(queries._move(entry))
                self._increment_cursor()

            else:
                # only 3 types of actions available
                pass

    def _increment_cursor(self):
        try:
            self._cursor[CURSOR] += 1
        except KeyError as error:
            logging.info("Error: No notifcation cursor found.")
            self._cursor['CURSOR'] = 0
            logging.info("Initialized cursor to 0.")

    def _decrement_cursor(self):
        self._cursor[CURSOR] -= 1
