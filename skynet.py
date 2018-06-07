'''
tuesday 5th june 2108
'''

import sys
from time import sleep
import lib.logger as log
from configparser import ConfigParser
from watchdog.observers import Observer
from lib.mapper import Mapper
from lib.parser import Parser
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
        config_file
            path to the config file

        logging_lvl
            sets the logging level of the logger, logging messages
            which are less severe than level will be ignored.
    """
    def __init__(self, config_file, logging_lvl):
        # setup logging
        self.logger = log.get_logger(log.lvl_mapping[logging_lvl])

        # get the configuration from the config file
        self.config = ConfigParser(allow_no_value=True)
        self.config.read(config_file)

        # static configuration --the mappings will not change
        self.mapper = self._get_mapper()
        
        # watcher will notify us of any file system events
        self.watcher = self._get_watcher()

        # observer to monitor the directory --and notify watcher
        self._thread_observer_ = Observer() 
        
        # NOTE: 
        #   Please be aware of local_root and local_base, they're DIFFERENT
        self._thread_observer_.schedule(watcher, path=mapper.local_base, 
                                        recursive=True)
        
        # NOTE: 
        #   If inotify exception occurs during execution
        #   that probably means that their are too many
        #   files to be monitored.
        #   We just need to raise the limit of files that
        #   can be monitored --see LOG.md for details on
        #   how to do that.
        try:
            self._thread_observer_.start()
        except Exception as error:
            logging.info('exiting...')
            logging.info('Cause: {}'.format(error))
            sys.exit()


        # dynamic configuration --guard against conn drop,restablishing conn
        self.sftpcon = self._get_connection()
        # also need a handler to handle the actual transfers
        self.handler = None
        self._thread_handler_ = None
        # start the daemon
        self._start_execution()
                    
    """
    TODO: Add desc
    """
    def _start_execution():
        # while conn exists
        # TODO: Add control flow desc
        while self.sftpcon is not None:            
            if self.handler is None:
                # init handler --to execute actions recorded by the watcher
                self.handler = Handler(sftp_con=sftpcon, mapper=mapper)
                self._thread_handler_ = Thread(target=handler.runner)
                
                try:
                    self._thread_handler_.start()
                except KeyboardInterrupt:
                    logger.info('Stopping handler --KeyboardInterrupt')
                    return
                except Exception as error:
                    logger.error('Cause: {}'.format(error))
                    self.sftpcon = self._get_connection()
                    # need to get a new handler, this handler's done
                    self.handler = None

    """
    TODO: Add desc
    """
    def _get_connection(self):
        sftpcon = None
        while True:
            try:
                # try to connect
                sftpcon = SFTPCon(host=self.config[SERVER]['remote_host'], 
                                  username=self.config[SERVER]['remote_username'],
                                  password=self.config[SERVER]['remote_password'])
                # must've obtained the connection
                return sftpcon
            except Exception as error:
                logger.error('Cause: {}'.format(error))
                logger.info('Sleeping... at {}'.format(now()))
                sleep(300)  # check every five minutes
                logger.info('Woke up... at {}'.format(now()))
                continue
            
    """
    TODO: Add desc
    """
    def _get_watcher(self):
        ignore_patterns = list(self.config[SYNC]['ignore_patterns']).split(' ')
        return Watcher(complete_sync=self.config[SYNC]['complete_sync'],
                       ignore_patterns=ignore_patterns)
               
    """
    TODO: Add desc
    """
    def _get_mapper(self):
        return Mapper(local_root=self.config[SYNC]['local_dir'],
                     local_dir=self.config[SYNC]['local_dir'],
                     remote_root=self.config[SYNC]['remote_root'],
                     remote_dir=self.config[SYNC]['remote_dir'])