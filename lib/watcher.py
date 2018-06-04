'''
1st june 2018 friday
'''
from logger import logger
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import DirCreatedEvent
from watchdog.events import DirModifiedEvent

# watcher on the wall
class Watcher(PatternMatchingEventHandler):
    """
    Watches a dir for any changes within that dir for any
    file system event (create, delete, rename, move etc...)
    and takes appropriate action.

    parameters
        handler: Handler
            to actually handle the transfers, and mimic them 
            on the SFTP server.
        complete_sync: boolean
            when True, files deleted in the local folder will
            also be deleted in the remote folder.
            when False, files deleted in the local folder will
            be retained in the remote folder.
    """
    def __init__(self, handler, complete_sync = False, **kwargs):
        super(Watcher, self).__init__(**kwargs)
        logger.info("Night gathers, and now my watch begins.")  
          
        self.handler = handler
        self.complete_sync = complete_sync
    
    """
    Called when a file or dir is created.
    NOTE:
        If a dir is created in the dir being monitored, there is no
        need to take any action for it.
        It will automatically be created on the remote SFTP server
        if it contains any file.          
    """
    def on_created(self, event):
        if not isinstance(event, DirCreatedEvent):
            logger.info("Recorded creation: {}".format(event.src_path))
            self.handler.send_resource(event.src_path)

    """
    Called when a file or dir is deleted.
    NOTE:
        It will only delete the files present on the remote dir
        which are not present in the local dir only if complete-sync
        is set to True.
    """ 
    def on_deleted(self, event):        
        if self.complete_sync:
            logger.info("Recorded deletion: {}".format(event.src_path))
            self.handler.delete_resource(event.src_path)
    
    """
    Called when a file or dir is modified.
    NOTE:
        The mtime (modification time) of the directory changes
        only when a file or a subdirectory is added, removed or 
        renamed.

        Modifying the contents of a file within the directory
        does not change the directory itself, nor does updating 
        the modified times of a file or a subdirectory.

        Thus, if a dir is modified , no action will be taken.
        However, if a file is modified, we will send a the whole
        file, which will be overwritten in the remote dir.

        Sending the whole file is a viable option, because:
            1. Images have small sizes.
            2. Videos will not be modified - processing will be done
               by the processing team. 
    """
    def on_modified(self, event):
        if not isinstance(event, DirModifiedEvent):
            logger.info("Recorded modification: {}".format(event.src_path))
            self.handler.send_resource(event.src_path)
    
    """
    Called when a file or dir is renamed or moved.
    """
    def on_moved(self, event):
        logger.info("Recorded move: \'{}\'->\'{}\'".format(
            event.src_path, event.dest_path))
        self.handler.move_resource(event._src_path, event.dest_path)
        