#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import apsw
import pickle
import ast
from hzg_config import *

conn = apsw.Connection(DATABASE_DIRECTORY + "/" + BASIC_DATABASE_NAME)
cursor = conn.cursor()
a = cursor.execute("SELECT DISTINCT(file_path) FROM file_table;")

ax = []  # Origin
ay = []  # Cache
a1 = []
a2 = []
a3 = []
a4 = []

for i in a:
    ax.append(i[0])
    # print (i[0].split("/")

conn.close(True)


for i in ax:
    j = i.split("/")
    if len(j) >= 7:
        if j[6] not in a1:
            a1.append(j[6])


ay = []

for i in ax:
    j = i.split("/")
    if len(j) >= 8:
        if (j[6] + "/" + j[7]) not in ay:
            ay.append(j[6] + "/" + j[7])

for m in range(len(a1)):
    a2.append([])


for i in ay:
    j = i.split("/")
    for m in range(len(a1)):
        if j[0] == a1[m]:
            if j[1] not in a2[m]:
                a2[m].append(j[1])


for m in range(len(a1)):
    a3.append([])
    for n in range(len(a2[m])):
        a3[m].append([])


ay = []

for i in ax:
    j = i.split("/")
    if len(j) >= 9:
        if (j[6] + "/" + j[7] + "/" + j[8]) not in ay:
            ay.append(j[6] + "/" + j[7] + "/" + j[8])

for i in ay:
    j = i.split("/")
    for m in range(len(a1)):
        for n in range(len(a2[m])):
            if j[0] == a1[m] and j[1] == a2[m][n]:
                if j[2] not in a3[m][n]:
                    a3[m][n].append(j[2])

string = ""
string += ("[")
for i in range(len(a1)):
    string += ("(\"" + a1[i] + "\", [")
    for j in range(len(a2[i])):
        string += ("(\"" + a2[i][j] + "\", [")
        for k in range(len(a3[i][j])):
            string += ("(\"" + a3[i][j][k] + "\", [")
            string += ("]),")
        string += ("]),")
    string += ("]),")
string += ("]")

s = ast.literal_eval(string)

f = open(DATABASE_DIRECTORY+"/"+CLASSIFICATION_FILE_NAME, "wb")
pickle.dump(s, f)
f.close()
