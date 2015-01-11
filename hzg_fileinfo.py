#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import hashlib

def get_hash(file_path, hasher=hashlib.md5, blocksize=65536):
    # afile = open(root + "/" + i, 'rb')
    # buf = afile.read(blocksize)
    # while len(buf) > 0:
    #     hasher.update(buf)
    #     buf = afile.read(blocksize)
    # return hasher.hexdigest()
    f = open(file_path,'rb')
    fsize = os.path.getsize(file_path)
    if fsize > 262144:
        f.seek(fsize-262144, 0)
    else:
        pass
    return (hasher(f.read(131072)).hexdigest())

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