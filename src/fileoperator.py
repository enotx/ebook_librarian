#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import hashlib
import platform
import subprocess

HASH_STARTPOINT = 262144
HASH_BLOCKSIZE = 131072

def get_hash(file_path, hasher=hashlib.md5, blocksize=65536):
    # afile = open(root + "/" + i, 'rb')
    # buf = afile.read(blocksize)
    # while len(buf) > 0:
    #     hasher.update(buf)
    #     buf = afile.read(blocksize)
    # return hasher.hexdigest()
    f = open(file_path,'rb')
    fsize = os.path.getsize(file_path)
    if fsize > HASH_STARTPOINT:
        f.seek(fsize-HASH_STARTPOINT, 0)
    else:
        pass
    return (hasher(f.read(HASH_BLOCKSIZE)).hexdigest())

def get_type(file_name):
    if file_name.count("."):
        file_type = file_name.split(".")[-1]
    else:
        file_type = "plain"
    return file_type

def get_size(file_path):
    return os.path.getsize(file_path)

def move_file(source_path, destination_path):
    pass

def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def get_pdf_metadata(file_path):
    pass
