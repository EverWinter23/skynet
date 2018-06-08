'''
tuesday 5th june 2108
'''

import sys
from time import sleep
import lib.logger as log
from configparser import ConfigParser
from watchdog.observers import Observer
from lib.mapper import Mapper
from threading import Thread
from lib.sftpcon import SFTPCon
from lib.watcher import Watcher
from lib.handler import Handler
from datetime import datetime

# string literals for convenience --DO NOT REMOVE
SERVER = 'SERVER'
SYNC = 'SYNC'


class SkyNet:
    """
    parameters
        config_file: str
            path to the config file

        logging_lvl: str
            sets the logging level of the logger, logging messages
            which are less severe than level will be ignored.
    """

    def __init__(self, config_file, logging_lvl):

        # setup logging
        self.logger = log.get_logger(log.lvl_mapping[logging_lvl])

        # get the configuration from the config file
        self.config = ConfigParser(allow_no_value=True)
        self.config.read(config_file)
        self.logger.info('Parsed the configuration file.')

        # static configuration --the mappings will not change
        self.logger.info('Init. Mapper.')
        self.mapper = self._get_mapper()
        self.logger.info('Initialized Mapper.')

        # watcher will notify us of any file system events
        self.logger.info('Init. Watcher.')
        self.watcher = self._get_watcher()
        self.logger.info('Initialized Mapper.')

        # observer to monitor the directory --and notify watcher
        self.logger.info('Init. Observer thread.')
        self._thread_observer_ = Observer()
        self.logger.info('Initialized Observer thread.')

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
            self.logger.info('Starting _thread_observer_')
            self._thread_observer_.start()
            self.logger.info('Started _thread_observer_')
        except Exception as error:
            logging.info('exiting...')
            logging.info('Cause: {}'.format(error))
            sys.exit()

        # also need a handler to handle the actual transfers
        self.handler = None
        self._thread_handler_ = None
        # start the daemon
        self.logger.info('Daemon started.')
        self._start_execution()

    def _stop_execution(self):
        """
        TODO: Add desc
        """
        self.logger.info('Stopping _thread_observer_')
        self._thread_observer_.stop()

        if self._thread_handler_ is not None:
            self.logger.info('Stopping _thread_handler_')
            self._thread_handler_.stop()

        self.logger.info('Waiting for threads to join in.')
        self._thread_observer_.join()
        self._thread_handler_.join()

        self.logger.info('Exiting gracefully.')

    def _start_execution(self):
        """
        TODO: Add desc
        """
        # dynamic configuration --guard against conn drop,restablishing conn
        self.sftpcon = self._get_connection()

        # while conn exists
        # TODO: Add control flow desc --also we're looping too much
        while self.sftpcon is not None:
            if self.handler is None:
                # init handler --to execute actions recorded by the watcher
                self.logger.info('Init. Handler.')
                self.handler = Handler(
                    sftp_con=self.sftpcon, mapper=self.mapper)
                self.logger.info('Initialized Handler.')

                self._thread_handler_ = Thread(target=self.handler.runner)

                try:
                    self.logger.info('Starting _thread_handler_')
                    self._thread_handler_.start()
                    self.logger.info('Started _thread_handler_')
                except Exception as error:
                    logger.error('Cause: {}'.format(error))
                    self.sftpcon = self._get_connection()
                    # need to get a new handler, this handler's done
                    self.logger.info('Discarding the current handler.')
                    self.handler = None
            else:
                self.logger.info('_start_exec sleeping at {}'.format(now()))
                sleep(5)  # if we have a handler --sleep for 5 minutes
                self.logger.info('_start_exec woke up. at {}'.format(now()))

    def _get_connection(self):
        """
        TODO: Add desc
        """
        sftpcon = None
        while True:
            try:
                # try to connect
                self.logger.info('Init SFTPCon.')
                sftpcon = SFTPCon(host=self.config[SERVER]['remote_host'],
                                  port=int(self.config[SERVER]['remote_port']),
                                  # Ignore LineLengthBear, PyCodeStyleBear
                                  username=self.config[SERVER]['remote_username'],
                                  password=self.config[SERVER]['remote_password'])  # Ignore LineLengthBear, PyCodeStyleBear

                # must've obtained the connection
                self.logger.info('Initialized SFTPCon.')
                return sftpcon

            except Exception as error:
                self.logger.error('Cause: {}'.format(error))
                self.logger.info('_get_conn sleeping at {}'.format(now()))
                sleep(5)  # check every five minutes TODO: testing for 5sec
                self.logger.info('_get_conn woke up at {}'.format(now()))
                continue

    def _get_watcher(self):
        """
        TODO: Add desc
        """
        # logs params passed to the Watcher --useful for debugging
        self.logger.info('ignore_patterns={}'.format(
            self.config[SYNC]['ignore_patterns']))
        self.logger.info('complete_sync={}'.format(
            self.config[SYNC]['complete_sync']))

        ignore_patterns = list(self.config[SYNC]['ignore_patterns'].split(' '))
        return Watcher(complete_sync=self.config[SYNC]['complete_sync'],
                       ignore_patterns=ignore_patterns)

    def _get_mapper(self):
        """
        TODO: Add desc
        """
        # logs params passed to the Mapper --useful for debugging
        self.logger.info('local_dir={}'.format(
            self.config[SYNC]['local_dir']))
        self.logger.info('local_root={}'.format(
            self.config[SYNC]['local_root']))
        self.logger.info('remote_root={}'.format(
            self.config[SYNC]['remote_root']))
        self.logger.info('remote_dir={}'.format(
            self.config[SYNC]['remote_dir']))

        return Mapper(local_root=self.config[SYNC]['local_root'],
                      local_dir=self.config[SYNC]['local_dir'],
                      remote_root=self.config[SYNC]['remote_root'],
                      remote_dir=self.config[SYNC]['remote_dir'])
