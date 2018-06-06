'''
tuesday 5th june 2108
'''

import arg_actions
import lib.logger as log
from lib.mapper import Mapper
from lib.parser import Parser
from lib.sftpcon import SFTPCon
from lib.watcher import Watcher
from lib.handler import Handler

class SkyNet:
    """
    """
    def __init__():
        pass

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