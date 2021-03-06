'''
tuesday 5th june 2108
'''

import sys
import logging
from time import sleep
from pathlib import Path
from threading import Event
from threading import Thread
from datetime import datetime
from configparser import ConfigParser
from watchdog.observers import Observer

# lib pckg imports
# NOTE: Keep the imports relative, easier for
# distribution and installation on other computers
# Install the module in editable mode. Then you
# can make changes without caring about distribution
# and other plaatforms.

from .skylib.s3con import S3Con
from .skylib.mapper import Mapper
from .skylib.sftpcon import SFTPCon
from .skylib.watcher import Watcher
from .skylib.handler import Handler
from .skylib.syncsnap import SyncSnap

# string literals for convenience --DO NOT REMOVE
SFTP, S3, SYNC = 'SFTP', 'S3', 'SYNC'
SERVICES = [SFTP, S3]


class SkyNet(Thread):
    """
    The SkyNet class makes use of Observer to monitor
    dir for changes, Watcher to record all file system
    events, Handler to execute corresponding actions
    --mostly upload the files, and a Notifier to send the
    notifications.

    parameters
        config_path: str
            path to the config file

        service: str
            remote storage service, supported services
            are S3, SFTP

        db_path: str
            path to the database where actions are
            stored.
    """

    def __init__(self, config, service, db_path):
        Thread.__init__(self)

        # the shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self._shutdown_flag = Event()

        # get the configuration from the config file
        self.config = ConfigParser(allow_no_value=True)
        self.config.read(config)
        logging.info('Parsed the config_file->{}'.format(config))

        # static configuration --the mappings will not change
        logging.info('Init. Mapper.')
        self.mapper = self._get_mapper()
        logging.info('Initialized Mapper.')

        # path to database
        self.db_path = db_path

        # for comparing dir snapshots
        self.syncsnap = SyncSnap(dir_path=self.mapper.local_base)

        # sync files already present in the folder on first run
        if self._first_run() is not True:
            logging.info('===============First Run==============')
            self.syncsnap._first_sync(db_path)

        # watcher will notify us of any file system events
        logging.info('Init. Watcher.')
        self.watcher = self._get_watcher()
        logging.info('Initialized Watcher.')

        # observer to monitor the directory --and notify watcher
        logging.info('Init. Observer thread.')
        self._thread_observer_ = Observer()
        logging.info('Initialized Observer thread.')

        # NOTE:
        #   Please be aware of local_root and local_base, they're DIFFERENT
        #   event_handler is diff from our handler --totally different CONTEXT
        self._thread_observer_.schedule(event_handler=self.watcher,
                                        path=self.mapper.local_base,
                                        recursive=True)

        # NOTE:
        #   If inotify exception occurs during execution
        #   that probably means that their are too many
        #   files to be monitored.
        #   We just need to raise the limit of files that
        #   can be monitored --see LOG.md for details on
        #   how to do that.
        try:
            logging.info('Starting _thread_observer_')
            self._thread_observer_.start()
            logging.info('Started _thread_observer_')
        except Exception as error:
            logging.info('exiting...')
            logging.info('Cause: {}'.format(error))
            sys.exit()

        # also need a handler to handle the actual transfers
        self._thread_handler_ = Handler(_mapper=self.mapper, db_path=db_path)

        # service type, one of the supported service
        self._service_type = service
        logging.info('Running with service {}.'.format(self._service_type))
        # connection to storage service
        self._con_service = None

        # self._start_execution()

    def run(self):
        self._start_execution()

    def _first_run(self):
        """
        Returns true if skynet is running for the first time.
        """
        return Path(self.db_path).exists()

    def _stop_execution(self):
        """
        Only for testing purposes, when you're running the
        service using python and not the command-line-interface.
        """
        logging.info('Stopping _thread_observer_')
        # self._thread_observer_.stop()

        if self._thread_handler_ is not None:
            logging.info('Stopping _thread_handler_')
            # self._thread_handler_.stop()
            logging.info('Stopped _thread_handler_')

        logging.info('Waiting for _thread_handler_ to join in.')
        # self._thread_observer_.join()
        self._thread_handler_.join()

        logging.info('Execution Paused.')

    def _start_execution(self):
        """
        Starts uploading files to the remote storage. If the connection
        drops mid-transfer, it keeps on checking for the connection to
        come back and when it does, it carries out the recorded actions.
        """
        # start the daemon
        logging.info('Daemon started.')

        # while conn exists
        # TODO: Add control flow desc --also we're looping too much
        while not self._shutdown_flag.is_set():
            if self._thread_handler_._is_running is False:
                # dynamic configuration --guard against conn drop, re-estd conn
                self._con_service = self._get_connection()
                logging.info('Connection Obtained.')

                self._thread_handler_ = Handler(_mapper=self.mapper,
                                                db_path=self.db_path)
                self._thread_handler_.setDaemon(True)
                # try-catch seems redundant
                try:
                    # init handler --to execute actions recorded by the watcher
                    logging.info(
                        'Notifying _thread_handler_ of the connection.')
                    self._thread_handler_._schedule(con=self._con_service)
                    logging.info('Actions for handler have been shceduled.')

                    logging.info('Starting _thread_handler_')
                    self._thread_handler_.start()
                    logging.info('Started _thread_handler_')
                except Exception as error:
                    logging.error('Cause: {}'.format(error))
                    self._con_service = self._get_connection()
                    # need to get a new handler, this handler's done
                    logging.info('_thread_handler_ halted.')
                    logging.info('The scheduled actions have been paused.')
            else:
                logging.info('_exec slept->{}'.format(datetime.now()))
                sleep(60)  # if we have a handler --sleep for 5 minutes
                logging.info('_exec got up->{}'.format(datetime.now()))

    def _get_connection(self):
        """
        Returns an instance of XCon class, --X stands for
        services supported
        """
        logging.info('Obtaining Connection.')
        if self._service_type == SFTP:
            return self._get_sftp_con()

        elif self._service_type == S3:
            return self._get_s3con()

    def _get_sftp_con(self):
        """
        Returns instance of SFTPCon class. Uses polling to
        until connection is established.
        """
        sftpcon = None
        while True:
            try:
                # try to connect
                logging.info('Init SFTPCon.')
                sftpcon = SFTPCon(host=self.config[SFTP]['remote_host'],
                                  port=int(self.config[SFTP]['remote_port']),
                                  # Ignore LineLengthBear, PyCodeStyleBear
                                  username=self.config[SFTP]['remote_username'],
                                  # Ignore LineLengthBear, PyCodeStyleBear
                                  password=self.config[SFTP]['remote_password'])
                # must've obtained the connection
                logging.info('Initialized SFTPCon.')
                return sftpcon

            except Exception as error:
                logging.error('Cause: {}'.format(error))
                logging.info('_get_con slept->{}'.format(datetime.now()))
                sleep(120)  # check every 2 minutes TODO: testing for 5sec
                logging.info('_get_con got up->{}'.format(datetime.now()))
                continue

    def _get_s3con(self):
        """
        Returns instance of S3Con class. Uses polling to
        until connection is established.
        """
        s3con = None
        while True:
            try:
                # try to connect
                logging.info('Init S3Con.')
                s3con = S3Con(bucket_name=self.config[S3]['bucket'],
                              key_id=self.config[S3]['key_id'],
                              secret_key=self.config[S3]['aws_secret'],
                              region=self.config[S3]['region'],
                              db_path=self.db_path)

                # must've obtained the connection
                logging.info('Initialized S3Con.')
                return s3con

            except Exception as error:
                logging.error('Cause: {}'.format(error))
                logging.info('_get_s3con slept->{}'.format(datetime.now()))
                sleep(120)  # check every 2 minutes TODO: testing for 5sec
                logging.info('_get_s3con got up->{}'.format(datetime.now()))
                continue

    def _get_watcher(self):
        """
        Returns an instance of Watcher class.
        """
        # logs params passed to the Watcher --useful for debugging
        # logging.info('ignore_patterns={}'.format(
        #    self.config[SYNC]['ignore_patterns']))
        # logging.info('complete_sync={}'.format(
        #    self.config[SYNC]['complete_sync']))

        ignore_patterns = list(self.config[SYNC]['ignore_patterns'].split(' '))
        return Watcher(complete_sync=self.config[SYNC]['complete_sync'],
                       ignore_patterns=ignore_patterns,
                       db_path=self.db_path)

    def _get_mapper(self):
        """
        Return an isntance of Mapper class
        """
        # logs params passed to the Mapper --useful for debugging
        # logging.info('local_dir={}'.format(
        #     self.config[SYNC]['local_dir']))
        # logging.info('local_root={}'.format(
        #     self.config[SYNC]['local_root']))
        # logging.info('remote_root={}'.format(
        #     self.config[SYNC]['remote_root']))
        # logging.info('remote_dir={}'.format(
        #     self.config[SYNC]['remote_dir']))

        return Mapper(local_root=self.config[SYNC]['local_root'],
                      local_dir=self.config[SYNC]['local_dir'],
                      remote_root=self.config[SYNC]['remote_root'],
                      remote_dir=self.config[SYNC]['remote_dir'])

    def _service_shutdown(self, signum, frame):
        """
        This shuts down SkyNet when it receves SIGINT signal
        from an external wrapper. However, the observer keeps
        on monitoring the directory for changes until that
        external process is stopped. It may take some time to
        shutdown all services.
        """
        logging.info('Caught Signal: {}'.format(signum))

        # NOTE: SkyNet keeps monitoring the directory for changes
        # self._thread_observer_.stop()
        # logging.info('Observer Stopped.')

        # however, if it is set and _thread_handler_ is running
        self._thread_handler_._is_running = False
        logging.info('Handler Stopped.')
        logging.info('Notifier Stopped.')

        self._shutdown_flag.set()

        raise SkyNetServiceExit


class SkyNetServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and skynet.
    """
    pass
