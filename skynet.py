'''
tuesday 5th june 2108
'''

import arg_actions
import lib.logger as log
from time import sleep
from watchdog.observers import Observer
from lib.mapper import Mapper
from lib.parser import Parser
from threading import Thread
from lib.sftpcon import SFTPCon
from lib.watcher import Watcher
from lib.handler import Handler
from datetime import datetime.now

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
        logger = log.get_logger(log.lvl_mapping[logging_lvl])

        # get the configuration from the config file
        config.read(config_file)

        # string literals for convenience
        SERVER = 'SERVER'
        SYNC = 'SYNC'

        # static configuration --the mappings will not change
        mapper = Mapper(local_root=config[SYNC]['local_dir'],
                        local_dir=config[SYNC]['local_dir'],
                        remote_root=config[SYNC]['remote_root'],
                        remote_dir=config[SYNC]['remote_dir'])
        
        # watcher will notify us of any file system events
        watcher = Watcher(complete_sync=config[SYNC]['complete_sync'],
                          ignore_patterns=config[SYNC]['ignore_patterns'])

        # observer to monitor the directory --and notify watcher
        _thread_observer_ = Observer() 
        
        # NOTE: 
        #   Please be aware of local_root and local_base, they're DIFFERENT
        #   If you get the inotify exception, please read the LOG.md
        _thread_observer_.schedule(watcher, path=mapper.local_base, 
                                  recursive=True)

        # dynamic configuration --guard against conn drop,restablishing conn
        sftpcon = self._get_connection()
        # start the daemon
        self._start_execution()
                  
    """
    TODO: Add desc
    """
    def _start_execution():
        # while conn exists
        # TODO: Add control flow desc
        while sftpcon not None:            
            if handler is None:
                # init handler --to execute actions recorded by the watcher
                handler = Handler(sftp_con=sftpcon, mapper=mapper)
                _thread_handler_ = Thread(target=handler.runner)
                
                try:
                    _thread_handler_.start()
                except Exception as error:
                    logger.error('Cause: {}'.format(error))
                    sftpcon = self._get_connection()
                    # need to get a new handler
                    handler = None

    """
    TODO: Add desc
    """
    def _get_connection(self):
        sftpcon = None
        while True:
            try:
                # try to connect
                sftpcon = SFTPCon(host=config[SERVER]['remote_host'], 
                                username=config[SERVER]['remote_username'],
                                password=config[SERVER]['remote_password'])
                # must've obtained the connection
                break
            except Exception as error:
                logger.error('Cause: {}'.format(error))
                logger.info('Sleeping... at {}'.format(now()))
                sleep(300)  # check every five minutes
                logger.info('Woke up... at {}'.format(now()))
                continue
        return sftpcon
        
                

# generate config file using command-line interface
def main():
    parser = Parser(description='Syncs a local folder to a remote folder, say\
                                 on the SFTP server.')
    args = parser.parse_args()

    if args.config: 
        arg_actions._config()
    if args.version:
        arg_actions._version()

def test():
    import time
    from watchdog.observers import Observer
    from threading import Thread

    logger = log.get_logger()
    # test settings    
    hostname = 'localhost'
    username = 'frost'
    password = 'finch75'

    local_root = '/home/frost/Code'
    local_dir = 'test'
    remote_dir = 'Stuff'
    remote_root = '/home/frost'
    ignore_patterns = ['*.swp', '*.tmp']

    conn = SFTPCon(host=hostname, username=username, password=password)
    mapper = Mapper(local_root, local_dir, remote_root, remote_dir)
    handler = Handler(conn, mapper)
    _thread_handler = Thread(target = handler.runner)
    _thread_handler.start()
    watcher = Watcher(complete_sync=True,ignore_patterns=ignore_patterns)
    _thread_observer = Observer()

    # NOTE: Please be aware of local_root and local_base
    _thread_observer.schedule(watcher, path=mapper.local_base, recursive=True)

    # TODO: Please be aware of inotify exception
    """
    You can set a new limit temporary with:
        $ sudo sysctl fs.inotify.max_user_watches=524288
        $ sudo sysctl -p

    If you like to make your limit permanent, use:
        $ echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
        $ sudo sysctl -p
    """
    try:
        _thread_observer.start()
    except Exception as error:
        logging.info('exiting...')
        logging.info('Cause: {}'.format(error))
        exit()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        _thread_observer.stop()
    _thread_observer.join()
    _thread_handler.join

if __name__ == '__main__':
    main()