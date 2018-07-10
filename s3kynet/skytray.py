'''
7th july 2018 saturday
background process as tray
'''
import os
import sys
import signal
import subprocess
import webbrowser
from time import sleep
from pathlib import Path
from PyQt5.QtWidgets import *

# pckg imports
from . import skyconf
from .skynet import SkyNet
from .skylib.trayicons import *
from .skylib import logger as log
from .skynet import SkyNetServiceExit

# string literals
START_UPLOADING, STOP_UPLOADING = 'Start Uploading', 'Stop Uploading'


class Skytray(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self._dir_path = skyconf.DIR_PATH
        self._log_file = skyconf.LOG_PATH
        self._sync_dir = None
        self._config_file = None
        self._default_service = None

        # create process entry in the system tray
        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(getIcon(SKYNET_ICON))

        self._logger = log.get_logger(skyconf.DIR_PATH,
                                      log.lvl_mapping['INFO'])
        self._logger.info('Logger Intialized.')

        # setup skynet
        self._thread_skynet_ = None
        self._build_menu()

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

        # parse config for remote storage service, and sync dir
        try:
            from configparser import ConfigParser
            _config = ConfigParser(allow_no_value=True)
            _config.read(self._config_file)

            for service in skyconf.SERVICES:
                if service in _config:
                    self._default_service = service

            self._sync_dir = os.path.join(_config['SYNC']['local_root'],
                                          _config['SYNC']['local_dir'])

        except Exception as error:
            self._logger.info('Improper Config. Could not parse config file.')
            self._logger.error('Cause: {}'.format(error))
            return False
        # '''
        self._thread_skynet_ = SkyNet(config=self._config_file,
                                      service=self._default_service,
                                      db_path=skyconf.DB_PATH)
        signal.signal(signal.SIGINT, self._thread_skynet_._service_shutdown)
        # '''

        if self._default_service is None:
            self._logger.info('Improper Config. No service configured.')
            return False
        else:
            return True

    def _restart_skynet(self):
        if self._validate_config():
            self._open_folder.setEnabled(True)
            self._upload_action.setEnabled(True)
        else:
            self._open_folder.setEnabled(False)
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
        self._quit_action = QAction(getIcon(EXIT_SKYNET),
                                    'Exit Skynet', self)
        self._quit_action.triggered.connect(qApp.quit)

        self._restart_action = QAction(getIcon(RELOAD_ICON),
                                       'Restart', self)
        self._restart_action.triggered.connect(self._restart_skynet)

        self._upload_action = QAction(getIcon(UPLOAD_ICON),
                                      START_UPLOADING, self)
        self._upload_action.triggered.connect(self._upload_start_stop)

        self._edit_action = QAction(getIcon(EDIT_CONFIG),
                                    'Edit Config', self)
        self._edit_action.triggered.connect(self._edit_config)

        self._open_folder = QAction(getIcon(SYNC_FOLDER),
                                    'Skynet Folder', self)
        self._open_folder.triggered.connect(self._open_skynetdir)

        self._status_action = QAction(getIcon(SHOW_STATUS),
                                      'Show Progress', self)
        self._status_action.triggered.connect(self._open_website)

        self._debug_action = QAction(getIcon(DEBUG_ERROR),
                                     'Debug Errors', self)
        self._debug_action.triggered.connect(self._open_log)

        # build menu and add actions to it
        self._menu.addAction(self._open_folder)
        self._menu.addAction(self._upload_action)
        self._menu.addAction(self._status_action)
        self._menu.addAction(self._edit_action)
        self._menu.addAction(self._debug_action)
        self._menu.addAction(self._restart_action)
        self._menu.addAction(self._quit_action)

        self._menu.insertSeparator(self._edit_action)
        self._menu.insertSeparator(self._restart_action)

        # validate actions
        self._restart_skynet()

    def _upload_start_stop(self):
        if self._upload_action.text() == START_UPLOADING:
            self._upload_action.setText(STOP_UPLOADING)
            self._upload_action.setIcon(getIcon(STOP_UPLOAD))
            self._upload_start()
        else:
            self._upload_action.setText(START_UPLOADING)
            self._upload_action.setIcon(getIcon(UPLOAD_ICON))
            self._upload_stop()

    def _upload_start(self):
        self._thread_skynet_.start()

    def _upload_stop(self):
        try:
            # signal skynet to stop
            self._thread_skynet_._service_shutdown(signal.SIGINT, None)

            # signal all other threads spawned by skynet to stop
            self._thread_skynet_._service_shutdown(signal.SIGINT, None)
        except SkyNetServiceExit as service_exit:
            self._thread_skynet_._shutdown_flag.set()
            self._logger.info('SkyNet Stopped.')

    def _edit_config(self):
        self._open_path(self._config_file)

    def _open_skynetdir(self):
        self._open_path(self._sync_dir)

    def _open_log(self):
        print(self._log_file)
        self._open_path(self._log_file)

    def _open_website(self):
        self._open_path(skyconf.WEBSITE_URL)
        # print(skyconf.WEBSITE_URL)

        # webbrowser.open(skyconf.WEBSITE_URL)

    def _open_path(self, path):
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', path))
        elif os.name == 'nt':
            os.startfile(path)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', path))


def main():
    #  must construct a QGuiApplication before a QPixmap
    app = QApplication(sys.argv)
    mw = Skytray()
    app.exec()


if __name__ == "__main__":
    main()
