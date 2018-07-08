'''
8th july 2018 sunday
Just Icon names here for system tray.
'''
# for os independent paths
import os
from PyQt5.QtGui import QIcon

ICON_DIR = 'icons'
# string literals for ease
S3_BUCKET = 'S3_BUCKET'
SKYNET_ICON = 'SKYNET_ICON'
UPLOAD_ICON = 'UPLOAD_ICON'
STOP_UPLOAD = 'STOP_UPLOAD'
EDIT_CONFIG = 'EDIT_CONFIG'
SHOW_STATUS = 'SHOW_STATUS'
SYNC_FOLDER = 'SYNC_FOLDER'
DEBUG_ERROR = 'DEBUG_ERROR'
SFTP_SERVER = 'SFTP_SERVER'
EXIT_SKYNET = 'EXIT_SKYNET'

# NOTE: Symmetry without trying ;-) 
ICONS = {S3_BUCKET : 's3_bucket.svg',
         SKYNET_ICON : 'skynet.svg',
         UPLOAD_ICON : 'upload.svg',
         STOP_UPLOAD : 'stop_upload.svg',
         EDIT_CONFIG : 'edit_config.svg',
         SHOW_STATUS : 'show_status.svg',
         SYNC_FOLDER : 'sync_folder.svg',
         DEBUG_ERROR : 'debug_error.svg',
         SFTP_SERVER : 'sftp_server.svg',
         EXIT_SKYNET : 'exit_skynet.svg',
        }

def getIcon(key):
    return QIcon(os.path.join(ICON_DIR, ICONS[key]))