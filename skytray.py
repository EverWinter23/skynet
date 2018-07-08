'''
7th july 2018 saturday
background process as tray
'''

import arg_actions
from time import sleep
import lib.logger as log
from skynet import SkyNet
import arg_actions
from lib.trayicons import *
from PyQt5.QtWidgets import *


class Skytray(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
    
        # create process entry in the system tray
        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(getIcon(SKYNET_ICON))
        
        self._logger = log.get_logger(log.lvl_mapping['INFO'])

        # setup skynet <-- Later
        '''
        self._skynet = SkyNet(config=arg_actions.FILE_PATH,
                              service='SFTP',
                              db_path=arg_actions.DB_PATH)
        '''
        # menu actions
        _quit_action = QAction(getIcon(EXIT_SKYNET), 'Exit', self)
        _quit_action.triggered.connect(qApp.quit)
        
        _start_action = QAction(getIcon(UPLOAD_ICON), 'Start Upload', self)
        #_start_action.triggered.connect(self._skynet._start_execution)

        _edit_config = QAction(getIcon(EDIT_CONFIG), 'Edit Config', self)
        _edit_config.triggered.connect(self._edit_config)

        _stop_upload = QAction(getIcon(STOP_UPLOAD), 'Stop Upload', self)
        _show_status = QAction(getIcon(SHOW_STATUS), 'Show Status', self)
        _sync_folder = QAction(getIcon(SYNC_FOLDER), 'Skynet Folder', self)
        _debug_error = QAction(getIcon(DEBUG_ERROR), 'Debug Errors', self)
        #_edit_config = QAction(getIcon(EDIT_CONFIG), 'Config', self)

        # build menu and add actions to it
        self._menu = QMenu('Skynet')
        
        self._menu.addAction(_sync_folder)
        self._menu.addAction(_start_action)
        self._menu.addAction(_show_status)
        self._menu.addAction(_edit_config)
        self._menu.addAction(_debug_error)
        self._menu.addAction(_quit_action)

        self._menu.insertSeparator(_edit_config)
        self._menu.insertSeparator(_quit_action)
        
        self._tray.setContextMenu(self._menu)
        self._tray.setVisible(True)
        
        # show the entry in the system tray
        self._tray.show()
        # display startup notification
        # self._tray.showMessage('Skynet', 'Uploading files.')
    
    def _start(self):
        pass

    def _edit_config(self):
        filepath = arg_actions.FILE_PATH
        
        import subprocess, sys
        # platform independent Windows, Mac, Linux
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))

if __name__ == "__main__":
    import sys
    #  must construct a QGuiApplication before a QPixmap
    app = QApplication(sys.argv)
    mw = Skytray()
    app.exec()
