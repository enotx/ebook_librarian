#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle
import configparser
from os import path


try:
    config = configparser.ConfigParser()
    config.read(path.expanduser("~") + "/.herzog_ebook/.hzgrc")
    LIBRARY_DIRECTORY = config.get("ENV_PATH", "library")
    ADMIT_FILE_LIST = config.get("FILE_TYPE", "filetype").split(',')
    RESULT_NUMBER = int(config.get("DISPLAY", "result_number"))
    SCAN_BUFFER_MAX = int(config.get("SYSTEM", "scan_buffer"))

except Exception as e:
    print (e)
    print ("RC File not found.")
    print ("Default Setting will be loaded instead.")

    LIBRARY_DIRECTORY = path.expanduser("~")
    ADMIT_FILE_LIST = ["txt", "doc", "docx", "pdf",
                       "djvu", "epub", "chm", "zip", "rar", "uvz","azw3"]
    RESULT_NUMBER = 100
    SCAN_BUFFER_MAX = 1000


# Constants
CLASSIFICATION_FILE_NAME = path.expanduser("~") + "/.herzog_ebook/classification.txt"
DATABASE_DIRECTORY = path.expanduser("~") + "/.herzog_ebook/database"
BASIC_DATABASE_NAME = "book.db"


# 图书分类法
# if path.exists(DATABASE_DIRECTORY + "/" + CLASSIFICATION_FILE_NAME):
#     with open(DATABASE_DIRECTORY + "/" + CLASSIFICATION_FILE_NAME, "rb") as f:
#         CLASSIFICATION_DATA = pickle.load(f)
# else:
#     CLASSIFICATION_DATA = []

# CLASSIFICATION_DATA = []

def test():
    print (LIBRARY_DIRECTORY)
    print (DATABASE_DIRECTORY)
    print (BASIC_DATABASE_NAME)
    print (CLASSIFICATION_FILE_NAME)
    print (ADMIT_FILE_LIST)

if __name__ == '__main__':
    test()