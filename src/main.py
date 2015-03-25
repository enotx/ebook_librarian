#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mainwindow
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = mainwindow.MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
