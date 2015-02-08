#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog,
        QDialogButtonBox, QFrame, QGroupBox, QLabel, QLineEdit, QListWidget,
        QTabWidget, QVBoxLayout, QWidget, qApp)

from PyQt5.uic import loadUi

class PreferenceDialog(QDialog):
    def __init__(self):
        super(PreferenceDialog, self).__init__(None)
        loadUi(sys.path[0]+'/ui/hzg_pref_dialog.ui', self)



class WarningDialog(QDialog):
    def __init__ (self, title, message):
        super(WarningDialog, self).__init__(None)
        loadUi(sys.path[0]+'/ui/hzg_warning_dialog.ui', self)
        self.setWindowTitle(self.tr(title))
        self.label.setText(message)

class ProgressDialog(QDialog):
    def __init__(self,title):
        super(ProgressDialog, self).__init__(None)
        loadUi(sys.path[0]+'/ui/hzg_progressbar_dialog.ui', self)
        self.setWindowTitle(self.tr(title))
        self.label.setText("Processing Now...")

    def setup_progress_bar(self,total):
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(total)

    def update_status(self, value, msg):
        self.label.setText(msg)
        self.progressBar.setValue(value)
        qApp.processEvents()
        # if value >= self.progressbar.maximum():
        #     break



if __name__ == '__main__':
    app = QApplication(sys.argv)
    tabdialog = PreferenceDialog()
    tabdialog.show()
    if tabdialog.exec_() == QDialog.Accepted:
        print ("yes")
    sys.exit(app.exec_())
