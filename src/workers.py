#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import os
import fileoperator
from dboperator import dboperator
from PyQt5 import QtCore

from config import DATABASE_DIRECTORY, BASIC_DATABASE_NAME, ADMIT_FILE_LIST, SCAN_BUFFER_MAX


class DirectoryProcess(object):

    def __init__(self):
        # super(dirscan, self).__init__(parent)
        self.breakpoint = 0

    def stop(self):
        self.breakpoint = 1

    def scan(self, dir_name, option=""):
        num_files_scanned = 0
        num_files_imported = 0
        num_files_ignored = 0
        buffer_list = []
        db_connection = dboperator(DATABASE_DIRECTORY, BASIC_DATABASE_NAME)
        db_connection.start_connect()
        if option == "FULL" or option == "FULLwithoutHASH":
            db_connection.reset_file_table()
        else:
            pass
        for root, dirs, files in os.walk(dir_name):
            if self.breakpoint:
                break
            for i in files:
                num_files_scanned += 1
                file_type = fileoperator.get_type(i).lower()
                if file_type in ADMIT_FILE_LIST:
                    # File Hash
                    if option == "FULLwithoutHASH":
                        file_hash = ""
                    else:
                        file_hash = fileoperator.get_hash(root + "/" + i)
                    # File Size
                    file_size = fileoperator.get_size(root + "/" + i)
                    # Process with Buffer
                    if len(buffer_list) < SCAN_BUFFER_MAX:
                        buffer_list.append(
                            [i, root, file_type, file_size, file_hash])
                    else:
                        for k in db_connection.insert_into_file_table_trans(buffer_list):
                            if k.split(" ")[-1] == "processed":
                                num_files_imported += 1
                            else:
                                num_files_ignored += 1
                        yield ([num_files_scanned, k])
                        buffer_list = []
                        buffer_list.append(
                            [i, root, file_type, file_size, file_hash])
                else:
                    pass
        for k in db_connection.insert_into_file_table_trans(buffer_list):
            if k.split(" ")[-1] == "processed":
                num_files_imported += 1
            else:
                num_files_ignored += 1
        yield ([num_files_scanned, k])
        yield (["END", "SIGNAL"])
        db_connection.end_connect()
        yield [num_files_imported, num_files_ignored]


class ScannerWorker(QtCore.QThread):
    trigger = QtCore.pyqtSignal(list)
    trigger2 = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(ScannerWorker, self).__init__(parent)

    def setup(self, dir_path, option=""):
        self.dir_path = dir_path
        self.option = option
        self.breakpoint = 0

    def get_file_num(self):
        num_files = 0
        for root, dirs, files in os.walk(self.dir_path):
            for i in files:
                num_files += 1
                yield num_files
        # self.trigger2.emit(num_files)
        # return num_files

    def run(self):
        self.a = DirectoryProcess()
        for i in self.get_file_num():
            if self.breakpoint:
                break
            self.trigger2.emit(i)
        for i in self.a.scan(self.dir_path, self.option):
            if self.breakpoint:
                break
            self.trigger.emit(i)

    def stop(self):
        self.a.stop()
        self.breakpoint = 1


if __name__ == '__main__':
    from PyQt5 import QtWidgets

    class Main(QtWidgets.QMainWindow):

        def __init__(self, parent=None):
            super(Main, self).__init__(parent)
            self.text_area = QtWidgets.QTextBrowser()
            self.thread_button = QtWidgets.QPushButton('Start threads')
            self.thread_button.clicked.connect(self.start_threads)

            central_widget = QtWidgets.QWidget()
            central_layout = QtWidgets.QHBoxLayout()
            central_layout.addWidget(self.text_area)
            central_layout.addWidget(self.thread_button)
            central_widget.setLayout(central_layout)
            self.setCentralWidget(central_widget)

        def start_threads(self):
            thread = ScannerWorker(self)    # create a thread
            thread.trigger.connect(self.update_text)  # connect to it's signal
            # just setting up a parameter
            thread.setup("/home/enotx/BookTemp", "FULL")
            thread.start()             # start the thread

        def update_text(self, msg):
            self.text_area.append(str(msg))

    app = QtWidgets.QApplication(sys.argv)

    mainwindow = Main()
    mainwindow.show()

    sys.exit(app.exec_())
