#!/usr/bin/env python
# -*- coding: utf-8 -*-

from hzg_config import *
from hzg_database import hzg_database
import sys
import os
import pickle
from math import ceil
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

# Load Classification Tree Data
if os.path.exists(DATABASE_DIRECTORY+"/"+CLASSIFICATION_FILE_NAME):
    with open(DATABASE_DIRECTORY+"/"+CLASSIFICATION_FILE_NAME,"rb") as f:
        CLASSIFICATION_DATA = pickle.load(f)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        loadUi(sys.path[0]+'/ui/hzg_main_window.ui', self)
        self.init_classification_tree()
        self.setWindowTitle("Yet Another Terrible Librarian")
        self.search_text = ""
        self.result_page_now = 1
        self.result_page_all = 1
        self.search_method = ""
        self.search_history_list = [[]]

        # Connect Database
        global db_connection
        db_connection = hzg_database(DATABASE_DIRECTORY, BASIC_DATABASE_NAME)
        db_connection.start_connect()

        # Default Behavior
        # Close Sidebar
        self.treeClassification.close()

        self.linetextSearch.setFocus()
        self.buttonResultPrev.setEnabled(False)
        self.buttonResultNext.setEnabled(False)

        # Flags
        self.treeClassificationToggle = 0

    # def __del__(self):
    #     db_connection.end_connect()
    #     print ("Bye")

    def set_default_style(self):
        pass

    def init_classification_tree(self):
        self.class_model = QStandardItemModel()
        self.class_model.setHorizontalHeaderLabels([self.tr("Classification")])
        self.classification_addItems(self.class_model, CLASSIFICATION_DATA)
        self.treeClassification.setModel(self.class_model)
        self.treeClassification.setCurrentIndex(self.class_model.index(0, 0))
        self.treeClassification.header().close()
        self.treeClassification.setFixedWidth(200)
        # self.treeClassification.expandAll()

    def classification_addItems(self, parent, elements):
        for text, children in elements:
            item = QStandardItem(text)
            parent.appendRow(item)
            if children:
                self.classification_addItems(item, children)

    @pyqtSlot()
    def on_buttonClassToggle_clicked(self):
        if self.treeClassificationToggle:
            self.treeClassificationToggle = 0
            self.treeClassification.hide()
        else:
            self.treeClassificationToggle = 1
            self.treeClassification.show()

    def get_current_selected_class(self):
        current_class = self.treeClassification.selectedIndexes()[0]
        a = current_class.data()
        current_class_path = ""
        while current_class.parent().data():
            current_class_path = current_class.parent().data() + "/" + \
                current_class_path
            current_class = current_class.parent()
        current_class_path = LIBRARY_DIRECTORY + "/" + current_class_path + a
        return current_class_path

    @pyqtSlot()
    def on_buttonExit_clicked(self):
        self.close()
        # self.statusBar.showMessage(self.get_current_selected_class())

    @pyqtSlot()
    def on_buttonSearch_clicked(self):
        keyword = self.search_text = self.linetextSearch.text()
        # self.search_by_keyword(keyword,1,"init")
        self.search_by_keyword_2nd(keyword,1,"init")

    @pyqtSlot()
    def on_buttonResultNext_clicked(self):
        keyword = self.search_text
        self.search_by_keyword_2nd(keyword, self.result_page_now+1)
        # self.result_page_now += 1
        # if self.result_page_now == 2:
        #     self.buttonResultPrev.setEnabled(True)
        # if self.result_page_now == self.result_page_all:
        #     self.buttonResultNext.setEnabled(False)

    @pyqtSlot()
    def on_buttonResultPrev_clicked(self):
        keyword = self.search_text
        self.search_by_keyword_2nd(keyword, self.result_page_now-1)
        # self.result_page_now -= 1
        # if self.result_page_now == 1:
        #     self.buttonResultPrev.setEnabled(False)
        # if self.result_page_now == self.result_page_all - 1:
        #     self.buttonResultNext.setEnabled(True)

    @pyqtSlot()
    def on_linetextSearch_returnPressed(self):
        self.on_buttonSearch_clicked()

    # 简单粗暴的搜索方式，放弃它吧
    def search_by_keyword(self, keyword, page = 1, option = ""):
        self.search_method = "keyword_search"
        dbcursor = db_connection.retrieve_file_table_by_keyword(keyword, (page-1)*RESULT_NUMBER)
        if option == "init":
            a = dbcursor[0]
            if len(keyword.split(" ")) <= 1:
                self.statusBar.showMessage(str(a)+" result(s) found")
            # Pagination
            self.result_page_all = ceil(a/RESULT_NUMBER)
            self.result_page_now = 1
            if self.result_page_all > 1:
                self.buttonResultNext.setEnabled(True)
        b = [i for i in dbcursor[1]]
        c = []
        if len(keyword.split(" ")) > 1:
            for i in b:
                k = 1
                for j in keyword.split(" "):
                    if j.lower() not in i[1].lower():
                        k *= 0
                if k == 1:
                    c.append(i)
            a = len(c)
            if option == "init":
                 self.statusBar.showMessage("about "+str(a)+" result(s) found")
        else:
            c = b
        self.treeShowResult.setModel(create_search_result_model(self, c))
        self.treeShowResult.setColumnWidth(0,200)
        self.treeShowResult.setColumnWidth(1,300)

    # 看起来更加精准高效的搜索方式，迭代器真牛逼
    def search_by_keyword_2nd(self, keyword, page = 1, option = ""):
        # 定义搜索方式，多种方式并存时
        self.search_method = "keyword_search"
        self.result_page_now = page
        if option == "init":
            # 连接数据库
            self.dbcursor = db_connection.retrieve_file_table_by_keyword_2nd(keyword)
            a = self.dbcursor[0]
            # 为分页数据申请存储空间
            self.search_history_list = [[]]
            for i in range(ceil(a/RESULT_NUMBER)):
                self.search_history_list.append([])
            if len(keyword.split(" ")) <= 1:
                self.statusBar.showMessage(str(a)+" result(s) found")
                # if a > RESULT_NUMBER:
                #     self.result_page_all = ceil(a/RESULT_NUMBER)
                #     self.result_page_now = 1
                #     self.buttonResultNext.setEnabled(True)

        if self.search_history_list[page-1] == []:
            c = []
            if len(keyword.split(" ")) > 1:
                i = 0
                while i < RESULT_NUMBER:
                    b = self.dbcursor[1].fetchone()
                    if b:
                        k = 1
                        for j in keyword.split(" "):
                            if j.lower() not in b[1].lower():
                                k *= 0
                        if k == 1:
                            c.append(b)
                            i += 1
                    else:
                        break
                a = len(c)
                if option == "init":
                    if a < RESULT_NUMBER: 
                        self.statusBar.showMessage(str(a)+" result(s) found")
                    else:
                        self.statusBar.showMessage("more than "+str(a)+" result(s) found")
                        # self.buttonResultNext.setEnabled(True)
            else:
                for i in range(RESULT_NUMBER):
                    b = self.dbcursor[1].fetchone()
                    if b:
                        c.append(b)
            self.search_history_list[page-1] = c
        if self.result_page_now > 1:
            self.buttonResultPrev.setEnabled(True)
        else:
            self.buttonResultPrev.setEnabled(False)
        if len(self.search_history_list[page-1]) == RESULT_NUMBER:
            self.buttonResultNext.setEnabled(True)
        else:
            self.buttonResultNext.setEnabled(False)
        self.treeShowResult.setModel(create_search_result_model(self, self.search_history_list[page-1]))
        self.treeShowResult.setColumnWidth(0,200)
        self.treeShowResult.setColumnWidth(1,300)


def add_search_result(model, file_name, file_path, file_size):
    model.insertRow(0)
    model.setData(model.index(0, 0), file_name)
    model.setData(model.index(0, 1), file_path)
    model.setData(model.index(0, 2), file_size)


def create_search_result_model(parent, query_result):
    model = QStandardItemModel(0, 3, parent)

    model.setHeaderData(0, Qt.Horizontal, "File Name")
    model.setHeaderData(1, Qt.Horizontal, "File Path")
    model.setHeaderData(2, Qt.Horizontal, "File Size")

    for i in query_result:
        add_search_result(model, str(i[1]), str(i[2]), str(i[4]))

    return model


# Go Test
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
