'''
7th july 2018 saturday
background process as tray
'''

import skyconf
from time import sleep
import lib.logger as log
from skynet import SkyNet
import skyconf
from lib.trayicons import *
from PyQt5.QtWidgets import *

import subprocess, sys, os
from pathlib import Path

class Skytray(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        self._dir_path = skyconf.DIR_PATH
        self._config_file = None
        self._default_service = None

        # create process entry in the system tray
        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(getIcon(SKYNET_ICON))
        
        self._logger = log.get_logger(skyconf.DIR_PATH,
                                      log.lvl_mapping['INFO'])
        self._logger.info('Logger Intialized.')

        # setup skynet <-- Later
        '''
        self._skynet = SkyNet(config=skyconf.FILE_PATH,
                              service='SFTP',
                              db_path=skyconf.DB_PATH)
        '''
        self._build_menu()
        
        # build menu and add actions to it
        
        self._tray.setContextMenu(self._menu)
        self._tray.setVisible(True)
        
        # show the entry in the system tray
        self._tray.show()
        # display startup notification
        # self._tray.showMessage('Skynet', 'Uploading files.')
    
    def _start(self):
        pass
    
    def _validate_config(self):
        if Path(skyconf.FILE_PATH).exists():
            self._config_file = skyconf.FILE_PATH
        else:
            self._config_file = None
            return False
                        
        # parse config for remote storage service
        from configparser import ConfigParser
        _config = ConfigParser(allow_no_value=True)
        _config.read(self._config_file)

        for service in skyconf.SERVICES:
            if service in _config:
                self._default_service = service
                break

        if self._default_service is None:
            self._logger.info('No service configured.')
            return False
        else:
            return True
        
    def _restart_skynet(self):
        if self._validate_config():
            self._upload_action.setEnabled(True)
        else:
            self._upload_action.setEnabled(False)

        if self._config_file is not None:
            self._edit_action.setEnabled(True)
        else:
            self._edit_action.setEnabled(False)        

    def _build_menu(self):
        self._menu = QMenu('Skynet')

        # read config file
        if Path(skyconf.FILE_PATH).exists():
            self._config_file = skyconf.FILE_PATH
        
        # menu actions
        self._quit_action = QAction(getIcon(EXIT_SKYNET), 'Exit Skynet', self)
        self._quit_action.triggered.connect(qApp.quit)

        self._restart_action = QAction('Restart' ,self)
        self._restart_action.triggered.connect(self._restart_skynet)

        self._upload_action = QAction(getIcon(UPLOAD_ICON), 'Start Upload', self)
        self._upload_action.triggered.connect(self.dummy)
                    
        self._edit_action = QAction(getIcon(EDIT_CONFIG), 'Edit Config', self)
        self._edit_action.triggered.connect(self._edit_config)
        
        '''

        #_stop_upload = QAction(getIcon(STOP_UPLOAD), 'Stop Upload', self)

        '''
        _show_status = QAction(getIcon(SHOW_STATUS), 'Show Status', self)

        _open_folder = QAction(getIcon(SYNC_FOLDER), 'Skynet Folder', self)
        #_open_folder.triggered.connect(self._open_path(self._dir_path))


        _debug_error = QAction(getIcon(DEBUG_ERROR), 'Debug Errors', self)
        #_edit_config = QAction(getIcon(EDIT_CONFIG), 'Config', self)
        
        #_menu.addAction(_open_folder)
        self._menu.addAction(self._upload_action)
        #_menu.addAction(_show_status)
        self._menu.addAction(self._edit_action)
        #_menu.addAction(_debug_error)
        self._menu.addAction(self._restart_action)
        self._menu.addAction(self._quit_action)

        self._menu.insertSeparator(self._edit_action)
        self._menu.insertSeparator(self._restart_action)
        
        # validate actions
        self._restart_skynet()
        
    def dummy(self):
        print('dummy')

    def _edit_config(self):
        self._open_path(skyconf.FILE_PATH)

      
    def _open_folder(self):
        from configparser import ConfigParser
        SYNC = 'SYNC'
        
        config = ConfigParser(allow_no_value=True)
        config.read(skyconf.FILE_PATH)

        dirpath = os.path.join(config[SYNC]['local_root'],
                               config[SYNC]['local_dir'],)
        self._open_path(dirpath)

    def _open_path(self, path):
        if not Path(path).exists():
            self._tray.showMessage('Error', 'No config found.')

        if sys.platform.startswith('darwin'):
            subprocess.call(('open', path))
        elif os.name == 'nt':
            os.startfile(path)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', path))

if __name__ == "__main__":
    #  must construct a QGuiApplication before a QPixmap
    app = QApplication(sys.argv)
    mw = Skytray()
    app.exec()
