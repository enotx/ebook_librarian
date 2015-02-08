#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle
import configparser
from os import path


try:
    config = configparser.ConfigParser()
    config.read(path.expanduser("~")+"/"+".hzgrc")
    LIBRARY_DIRECTORY = config.get("ENV_PATH","library")
    DATABASE_DIRECTORY = sys.path[0] + "/" + config.get("ENV_PATH","dbfolder")
    BASIC_DATABASE_NAME = config.get("ENV_PATH","dbname")+".db"
    CLASSIFICATION_FILE_NAME = config.get("ENV_PATH","classification")+".pkl"

    ADMIT_FILE_LIST = config.get("FILE_TYPE","filetype").split(',')

except Exception as e:
    print (e)
    print ("RC File not found.")
    print ("Default Setting will be loaded instead.")

    # LIBRARY_DIRECTORY = "/run/media/enotx/Elements/图书馆"
    LIBRARY_DIRECTORY = "/run/media/enotx/Seagate Expansion Drive/图书馆"
    DATABASE_DIRECTORY = sys.path[0] + "/data"
    BASIC_DATABASE_NAME = "hzg_db.db"
    CLASSIFICATION_FILE_NAME = "classification.pkl"
    ADMIT_FILE_LIST = ["txt", "doc", "docx", "pdf",
                       "djvu", "epub", "chm", "zip", "rar", "uvz"]

# MAGIC NUM
RESULT_NUMBER = 100
SCAN_BUFFER_MAX = 1000

if path.exists(DATABASE_DIRECTORY+"/"+CLASSIFICATION_FILE_NAME):
    with open(DATABASE_DIRECTORY+"/"+CLASSIFICATION_FILE_NAME,"rb") as f:
        CLASSIFICATION_DATA = pickle.load(f)
else:
    CLASSIFICATION_DATA = []