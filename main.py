#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import hzg_window
from PyQt5 import QtWidgets

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = hzg_window.MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
