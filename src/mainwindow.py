#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dboperator import dboperator
import dialog
import fileoperator
import workers

import sys
import os
from math import ceil
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QKeySequence

from config import LIBRARY_DIRECTORY, DATABASE_DIRECTORY, BASIC_DATABASE_NAME, CLASSIFICATION_DATA, RESULT_NUMBER

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # 载入UI
        loadUi(sys.path[0] + '/ui/main_window.ui', self)
        self.setWindowTitle(self.tr("Yet Another Librarian 絶賛開発中"))

        # 分类法侧边栏相关
        self.classification_tree_init()
        # 先暂且关闭
        self.treeClassification.close()

        # 各种类型的缓存
        self.search_text = ""
        self.result_page_now = 1
        self.result_page_all = 1
        self.search_method = ""
        self.search_history_list = [[]]
        self.directory_to_scan = os.path.expanduser("~")

        # Database Connection (Global, used by the main search component)
        global db_connection
        db_connection = dboperator(DATABASE_DIRECTORY, BASIC_DATABASE_NAME)
        db_connection.start_connect()

        # Default Behavior（其它未在ui文件中定义的行为）
        self.linetextSearch.setFocus()
        self.buttonResultPrev.setEnabled(False)
        self.buttonResultNext.setEnabled(False)
        # 在搜索结果中右键打开菜单
        self.treeShowResult.customContextMenuRequested.connect(
            self.openResultContextMenu)

        # Flags
        self.treeClassificationToggle = 0
        self.scan_flag = 0

        # Shortcuts
        # QtWidgets.QShortcut(QKeySequence("Ctrl+Q"), self, self.close)

    #################
    # 改变界面风格，会导致段错误(Core Dump)，未找到原因
    #################
    def set_default_style(self):
        pass

    ###################################
    ###################################
    #       初始化图书分类法侧边栏        #
    ###################################
    ###################################
    # 初始化图书分类法侧边栏
    def classification_tree_init(self):
        self.class_model = QStandardItemModel()
        self.class_model.setHorizontalHeaderLabels([self.tr("Classification")])
        self.__classification_addItems(self.class_model, CLASSIFICATION_DATA)
        self.treeClassification.setModel(self.class_model)
        self.treeClassification.setCurrentIndex(self.class_model.index(0, 0))
        self.treeClassification.header().close()
        self.treeClassification.setFixedWidth(200)
        # self.treeClassification.expandAll()

    # 仅用于classification使用，设为私有
    def __classification_addItems(self, parent, elements):
        for text, children in elements:
            item = QStandardItem(text)
            parent.appendRow(item)
            if children:
                self.__classification_addItems(item, children)

    # 得到目前选中的图书分类树项目，并组成完整路径
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

    # 图书分类树开关
    @pyqtSlot()
    def on_buttonClassToggle_clicked(self):
        if self.treeClassificationToggle:
            self.treeClassificationToggle = 0
            self.treeClassification.hide()
        else:
            self.treeClassificationToggle = 1
            self.treeClassification.show()



    ###################################
    ###################################
    #            搜索功能模块           #
    ###################################
    ###################################
    # 搜索按钮
    @pyqtSlot()
    def on_buttonSearch_clicked(self):
        keyword = self.search_text = self.linetextSearch.text()
        self.search_by_keyword(keyword, 1, "init")

    # 回车搜索，与按下搜索按钮效果完全一样
    @pyqtSlot()
    def on_linetextSearch_returnPressed(self):
        self.on_buttonSearch_clicked()

    # 下一页
    @pyqtSlot()
    def on_buttonResultNext_clicked(self):
        keyword = self.search_text
        self.search_by_keyword(keyword, self.result_page_now + 1)
        # self.result_page_now += 1
        # if self.result_page_now == 2:
        #     self.buttonResultPrev.setEnabled(True)
        # if self.result_page_now == self.result_page_all:
        #     self.buttonResultNext.setEnabled(False)

    # 上一页
    @pyqtSlot()
    def on_buttonResultPrev_clicked(self):
        keyword = self.search_text
        self.search_by_keyword(keyword, self.result_page_now - 1)
        # self.result_page_now -= 1
        # if self.result_page_now == 1:
        #     self.buttonResultPrev.setEnabled(False)
        # if self.result_page_now == self.result_page_all - 1:
        #     self.buttonResultNext.setEnabled(True)

    # 与搜索结果相关的两个功能函数，分别为构造结果的QTreeModel和addItem
    def __add_search_result(self, model, file_name, file_path, file_size, file_id, file_hash):
        model.insertRow(0)
        model.setData(model.index(0, 0), file_name)
        model.setData(model.index(0, 1), file_path)
        model.setData(model.index(0, 2), file_size)
        model.setData(model.index(0, 3), file_id)
        model.setData(model.index(0, 4), file_hash)

    def __create_search_result_model(self, query_result):
        model = QStandardItemModel(0, 5, self)

        model.setHeaderData(0, Qt.Horizontal, "File Name")
        model.setHeaderData(1, Qt.Horizontal, "File Path")
        model.setHeaderData(2, Qt.Horizontal, "File Size")
        model.setHeaderData(3, Qt.Horizontal, "File ID")
        model.setHeaderData(4, Qt.Horizontal, "File HASH")

        for i in query_result:
            self.__add_search_result(
                model, str(i[1]), str(i[2]), int(i[4]), int(i[0]), str(i[5]))
        return model

    # 看起来更加精准高效的搜索方式，迭代器真牛逼
    def search_by_keyword(self, keyword, page=1, option=""):
        # 定义搜索方式，多种方式并存时
        self.search_method = "keyword_search"
        self.result_page_now = page
        if option == "init":
            # 连接数据库
            self.dbcursor = db_connection.retrieve_file_table_by_keyword(
                max(keyword.split(" "), key=len))
            a = self.dbcursor[0]
            # 为分页数据申请存储空间
            self.search_history_list = [[]]
            for i in range(ceil(a / RESULT_NUMBER)):
                self.search_history_list.append([])
            if len(keyword.split(" ")) <= 1:
                self.statusBar.showMessage(str(a) + " result(s) found")

        if self.search_history_list[page - 1] == []:
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
                        self.statusBar.showMessage(str(a) + " result(s) found")
                    else:
                        self.statusBar.showMessage(
                            "more than " + str(a) + " result(s) found")
            else:
                for i in range(RESULT_NUMBER):
                    b = self.dbcursor[1].fetchone()
                    if b:
                        c.append(b)
            self.search_history_list[page - 1] = c
        if self.result_page_now > 1:
            self.buttonResultPrev.setEnabled(True)
        else:
            self.buttonResultPrev.setEnabled(False)
        if len(self.search_history_list[page - 1]) == RESULT_NUMBER:
            self.buttonResultNext.setEnabled(True)
        else:
            self.buttonResultNext.setEnabled(False)
        self.treeShowResult.setModel(
            self.__create_search_result_model(self.search_history_list[page - 1]))
        self.treeShowResult.setColumnWidth(0, 250)
        self.treeShowResult.setColumnWidth(1, 400)
        self.treeShowResult.resizeColumnToContents(3)

    ###################################
    ##      搜索结果框中的右键菜单       ##
    ###################################

    def openResultContextMenu(self, position):
        indexes = self.treeShowResult.selectedIndexes()
        menu = QtWidgets.QMenu()
        if indexes:
            actionOpenFile = menu.addAction(self.tr("Open File"))
            actionOpenContainingFolder = menu.addAction(
                self.tr("Open Containing Folder"))
            actionFindDuplicates = menu.addAction(self.tr("Find Duplicate(s)"))
            menu.addSeparator()
            menuSearchInMore = menu.addMenu(self.tr("Search in"))
            # actionSearchInDouban = menuSearchInMore.addAction(self.tr("Douban"))
            # actionSearchInSHL = menuSearchInMore.addAction(self.tr("SH Library"))
            action = menu.exec_(
                self.treeShowResult.viewport().mapToGlobal(position))
            if action == actionOpenFile:
                current_index_file_path = indexes[
                    1].data() + "/" + indexes[0].data()
                fileoperator.open_file(current_index_file_path)
            elif action == actionOpenContainingFolder:
                current_index_folder_path = indexes[1].data()
                fileoperator.open_file(current_index_folder_path)
            elif action == actionFindDuplicates:
                db_buffer = dboperator(
                    DATABASE_DIRECTORY, BASIC_DATABASE_NAME)
                db_buffer.start_connect()
                duplicate_file_list = []
                for i in db_buffer.find_file_table_by_hash(file_hash=indexes[4].data()):
                    duplicate_file_list.append(i)
                a = len(duplicate_file_list)
                if a == 1:
                    self.statusBar.showMessage("No Duplicates Found")
                else:
                    self.statusBar.showMessage(str(a) + " Duplicates Found")
                    self.treeShowResult.setModel(
                        self.__create_search_result_model(duplicate_file_list))
                    self.treeShowResult.setColumnWidth(0, 250)
                    self.treeShowResult.setColumnWidth(1, 400)
                    self.treeShowResult.resizeColumnToContents(3)
                    self.clear_search_buffer()
                db_buffer.end_connect()
        else:
            actionNull = menu.addAction(self.tr("Nothing Selected"))
            actionNull.setEnabled(False)
            action = menu.exec_(
                self.treeShowResult.viewport().mapToGlobal(position))

    # 清除搜索缓存
    def clear_search_buffer(self):
        self.buttonResultPrev.setEnabled(False)
        self.buttonResultNext.setEnabled(False)
        self.search_history_list = [[]]

    ###################################
    ###################################
    #            扫描功能模块           #
    ###################################
    ###################################
    @pyqtSlot()
    def on_toolSelectScanDir_clicked(self):
        t = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", self.directory_to_scan)
        if t != "":
            self.lineDirSelected.setText(t)
            self.directory_to_scan = t

    @pyqtSlot()
    def on_buttonScan_clicked(self):
        self.scan_flag = 0
        db_connection.end_connect()
        self.clear_search_buffer()
        a = self.lineDirSelected.text()
        x = object()
        if os.path.exists(a) and os.path.isdir(a):
            if self.checkboxInitScan.isChecked():
                self.scan_warning_dialog = dialog.WarningDialog(title="Hello",
                                                                    message="This operation will RESET the database and ALL your data will be lost.\n\nConfirmed?")
                self.scan_warning_dialog.show()
                if self.scan_warning_dialog.exec_() == QtWidgets.QDialog.Accepted:
                    self.scan_directory(a, "FULL")
            elif os.path.exists(DATABASE_DIRECTORY + "/" + BASIC_DATABASE_NAME):
                self.scan_directory(a, "")
            else:
                self.scan_directory(a, "FULL")
            db_connection.start_connect()
        else:
            self.statusBar.showMessage("Not an available dir path.")

    def scan_directory(self, dir_path, option):
        self.scan_progressbar_dialog = dialog.ProgressDialog(
            title="Scanning...")
        self.scan_progressbar_dialog.show()
        self.scan_thread = workers.ScannerWorker(self)
        self.scan_thread.setup(dir_path, option)
        # a = self.scan_thread.get_file_num()
        self.scan_thread.trigger2.connect(
            self.scan_progressbar_dialog.setup_progress_bar)
        # self.scan_progressbar_dialog.setup_progress_bar(a)
        self.scan_thread.trigger.connect(self.scan_thread_update_info)
        self.scan_thread.start()
        if self.scan_progressbar_dialog.exec_() == QtWidgets.QDialog.rejected:
            self.scan_thread.stop()

    def scan_thread_update_info(self, x):
        if x == ["END", "SIGNAL"]:
            self.scan_flag = 1
        if not self.scan_flag:
            self.scan_progressbar_dialog.update_status(x[0], x[1])
        else:
            self.scan_progressbar_dialog.close()
            self.statusBar.showMessage(
                str(x[0] + x[1]) + " files scanned." + str(x[0]) + " imported and " + str(x[1]) + " ignored")

    ###################################
    ###################################
    #            其他功能模块           #
    ###################################
    ###################################
    @pyqtSlot()
    def on_actionPreference_triggered(self):
        # tabdialog = dialog.PreferenceDialog()
        pass

    @pyqtSlot()
    def on_buttonFileProcess_clicked(self):
        self.stackQueue.setCurrentIndex(1)
        pass

    # 右下角退出按钮
    @pyqtSlot()
    def on_buttonExit_clicked(self):
        self.close()

# Go Test
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
