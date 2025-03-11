#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow
from app.gui.ui.creepyai_mainwindow_ui import Ui_CreepyAIMainWindow

# Setup logging
log_dir = os.path.join(os.path.expanduser("~"), '.creepyai', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'creepy_main.log')

logging.basicConfig(
    level=logging.INFO,
    filename=log_file,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Ensure Qt paths are correct
def setup_qt_paths():
    conda_prefix = os.environ.get('CONDA_PREFIX')
    if conda_prefix:
        qt_lib_path = os.path.join(conda_prefix, 'lib')
        qt_plugin_path = os.path.join(conda_prefix, 'lib/qt/plugins')

        os.environ['QT_PLUGIN_PATH'] = qt_plugin_path
        os.environ['DYLD_FRAMEWORK_PATH'] = qt_lib_path
        os.environ.pop('DYLD_LIBRARY_PATH', None)

        sys.path.insert(0, qt_lib_path)
        return True
    return False

# Initialize Qt paths
if not setup_qt_paths():
    logger.warning("Could not set up Qt paths automatically. Using default environment paths.")

# Define Main Window Class
class CreepyAIMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_CreepyAIMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("CreepyAI - Geolocation OSINT AI Tool")
        logger.info("CreepyAI Main Window initialized.")

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        main_window = CreepyAIMain()
        main_window.show()
        logger.info("CreepyAI application started successfully.")
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)
