#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-12-13 15:53:09
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import time
import apsw
from config import DATABASE_DIRECTORY, BASIC_DATABASE_NAME
import hashlib


class dboperator:

    def __init__(self, db_dir, db_name):
        super(dboperator, self).__init__()
        self.db_dir = db_dir
        self.db_name = db_name

    def start_connect(self):
        self.connection = apsw.Connection(self.db_dir + "/" + self.db_name)
        self.cursor = self.connection.cursor()

    def end_connect(self):
        self.connection.close(True)
        return 1

    # 建表
    def __create_table(self, table_name):
        if table_name == "file":
            self.cursor.execute("DROP TABLE IF EXISTS file_table")
            self.cursor.execute("CREATE TABLE file_table (\
                    file_id INTEGER PRIMARY KEY ASC,\
                    file_name TEXT, \
                    file_path TEXT, \
                    file_type TEXT, \
                    file_size INTEGER, \
                    file_hash TEXT, \
                    file_crt_time INTEGER, \
                    file_mdf_time INTEGER \
                    );")
            self.cursor.execute("DROP TABLE IF EXISTS file_uniq_check_table")
            self.cursor.execute("CREATE TABLE file_uniq_check_table (\
                    file_uniq_check_id INTEGER PRIMARY KEY ASC,\
                    file_uniq_check_hash TEXT UNIQUE NOT NULL \
                    );")
        elif table_name == "book":
            self.cursor.execute("DROP TABLE IF EXISTS book_table")
            self.cursor.execute("CREATE TABLE book_table (\
                    book_id INTEGER PRIMARY KEY ASC,\
                    book_title TEXT, \
                    book_subtitle TEXT, \
                    book_author TEXT, \
                    book_translator TEXT, \
                    book_publisher TEXT, \
                    book_page_no INTEGER, \
                    book_language TEXT, \
                    book_isbn TEXT, \
                    book_class_1 TEXT, \
                    book_class_2 TEXT, \
                    book_class_3 TEXT, \
                    book_status TEXT, \
                    book_tags TEXT, \
                    book_crt_time INTEGER, \
                    book_mdf_time INTEGER \
                    );")
        elif table_name == "bookmap":
            self.cursor.execute("DROP TABLE IF EXISTS bookmap_table")
            self.cursor.execute("CREATE TABLE bookmap_table (\
                    bookmap_id INTEGER PRIMARY KEY ASC,\
                    bookmap_filehash TEXT, \
                    bookmap_bookid TEXT, \
                    bookmap_crt_time INTEGER, \
                    bookmap_mdf_time INTEGER \
                    );")
        elif table_name == "search":
            self.cursor.execute("DROP TABLE IF EXISTS search_file")
            self.cursor.execute(
                "CREATE VIRTUAL TABLE search_file USING fts4(file_id, file_name,file_hash, book_content)")
        elif table_name == "reading":
            self.cursor.execute("DROP TABLE IF EXISTS reading_table")
            self.cursor.execute("CREATE TABLE reading_table (\
                    reading_id INTEGER PRIMARY KEY ASC,\
                    reading_bookname TEXT, \
                    reading_progress TEXT, \
                    reading_comment TEXT, \
                    reading_start_time INTEGER, \
                    reading_end_time INTEGER \
                    reading_crt_time INTEGER, \
                    reading_mdf_time INTEGER \
                    );")
        else:
            print ("argument not defined")
            return 0

    def __truncate_table(self, table_name):
        if table_name == "file":
            self.cursor.execute("DELETE FROM file_table; VACUUM;")
            self.cursor.execute("DELETE FROM file_uniq_check_table; VACUUM;")
            return 1
        else:
            print ("argument not defined")
            return 0

    def rebuild_database(self):
        # self.start_connect()
        self.__create_table("file")
        # self.__create_table("book")
        # self.__create_table("bookmap")
        # self.__create_table("reading")
        # self.end_connect()

    def reset_file_table(self):
        self.__create_table("file")
        self.cursor.execute("VACUUM;")
        return 1

    # 写表-插入
    def insert_into_file_table_single(self, file_name, file_path, file_type, file_size, file_hash):
        string = file_name + file_path + file_type + str(file_size) + file_hash
        hashcheck = hashlib.md5(string.encode('utf-8')).hexdigest()
        a = self.cursor.execute(
            "SELECT COUNT(*) FROM file_uniq_check_table WHERE file_uniq_check_hash = ?;", (hashcheck,))
        a = [i for i in a][0][0]
        if not a:
            self.cursor.execute(
                "INSERT INTO file_uniq_check_table (file_uniq_check_hash) values (?)", (hashcheck,))
            self.cursor.execute("INSERT INTO file_table (file_name, file_path, file_type, file_size, file_hash, file_crt_time, file_mdf_time) values(?,?,?,?,?,?,?)",
                                (file_name, file_path, file_type, file_size, file_hash, int(time.time()), int(time.time())))
            yield (file_path + "/" + file_name + " processed")
            print (file_path + "/" + file_name + " processed")
        else:
            yield (file_path + "/" + file_name + " ignored")
            print (file_path + "/" + file_name + " ignored")
            pass

    def insert_into_file_table_trans(self, file_info_list):
        # print ("breakpoint")
        file_info_list_new = []
        for file_info in file_info_list:
            # time.sleep(5)
            string = file_info[0] + file_info[1] + \
                file_info[2] + str(file_info[3]) + file_info[4]
            hashcheck = hashlib.md5(string.encode('utf-8')).hexdigest()
            a = self.cursor.execute(
                "SELECT COUNT(*) FROM file_uniq_check_table WHERE file_uniq_check_hash = ?;", (hashcheck,))
            a = [i for i in a][0][0]
            if not a:
                file_info.append(hashcheck)
                file_info_list_new.append(file_info)
            else:
                yield (file_info[1] + "/" + file_info[0] + " ignored")
                # print (file_info[1]+"/"+file_info[0]+" ignored")
                pass
        self.cursor.execute("BEGIN")
        for file_info in file_info_list_new:
            self.cursor.execute(
                "INSERT INTO file_uniq_check_table (file_uniq_check_hash) values (?)", (file_info[5],))
            self.cursor.execute("INSERT INTO file_table (file_name, file_path, file_type, file_size, file_hash, file_crt_time, file_mdf_time) values(?,?,?,?,?,?,?)",
                                (file_info[0], file_info[1], file_info[2], file_info[3], file_info[4], int(time.time()), int(time.time())))
            yield (file_info[1] + "/" + file_info[0] + " processed")
            # print (file_info[1]+"/"+file_info[0]+" processed")
        self.cursor.execute("COMMIT")

    # def insert_into_reading_table_single(self, reading_bookname, reading_progress, reading_start_time, reading_end_time):
    #     self.cursor.execute("INSERT INTO file_table (reading_bookname, reading_progress, reading_start_time, reading_end_time, reading_crt_time, reading_mdf_time) values(?,?,?,?,?,?,?)",
    #                         (reading_bookname, reading_progress, reading_start_time, reading_end_time, int(time.time()),int(time.time())))

    # def update_reading_table_single(self, reading_bookname, reading_progress, reading_start_time, reading_end_time):
    #     self.cursor.execute("UPDATE file_table SET reading_bookname = ?, reading_progress = ?, reading_start_time = ?, reading_end_time = ?, reading_crt_time = ?, reading_mdf_time = ?",
    #                         (reading_bookname, reading_progress, reading_start_time, reading_end_time, int(time.time()),int(time.time())))

    # 删除单条记录
    def delete_file_table_single(self, file_id):
        self.cursor.execute(
            "DELETE FROM file_table WHERE file_id = ?;", (file_id,))
        return 1

    # def delete_reading_table_single(self, reading_id):
    #     self.cursor.execute("DELETE FROM reading_table WHERE reading_id = ?;", (reading_id,))
    #     return 1

    # 新搜索方式，完全依赖生成器，将总数a和游标b直接返回
    def retrieve_file_table_by_keyword(self, keyword=""):
        if keyword == "":
            a = self.cursor.execute("SELECT count(*) from file_table;")
            a = [i for i in a][0][0]
            b = self.cursor.execute("SELECT * from file_table;")
            return [a, b]
        else:
            keyword = "%" + keyword.split(" ")[0] + "%"
            a = self.cursor.execute(
                "SELECT count(*) from file_table WHERE file_name LIKE ?;", (keyword,))
            a = [i for i in a][0][0]
            b = self.cursor.execute(
                "SELECT * from file_table WHERE file_name LIKE ?;", (keyword,))
            return [a, b]

    # 总体查重，感觉没什么用
    def get_file_table_dupes(self):
        a = self.cursor.execute("SELECT * \
            FROM file_table \
            WHERE file_hash IN (SELECT file_hash \
                FROM file_table \
                GROUP BY file_hash \
                HAVING count(*) > 1);")
        return a

    # 各种查询
    def find_file_table_by_hash(self, file_hash):
        a = self.cursor.execute(
            "SELECT * from file_table WHERE file_hash = ?;", (file_hash,))
        return a

    def is_dir_existing(self, text):
        keyword = text + "%"
        a = self.cursor.execute(
            "SELECT COUNT(*) from file_table WHERE file_path LIKE ?;", (keyword,))
        b = [i for i in a][0][0]
        return b

    # 与搜索相关功能
    def rebuild_search_table(self):
        self.cursor.execute(
            "INSERT INTO search_book (SELECT file_hash, COALESCE(book_title, book_subtitle, book_author, book_translator, book_tags) FROM Source);")

    # 建立和删除索引
    def build_index(self):
        # self.cursor.execute("CREATE INDEX file_hash_idx ON file_table ( 'file_hash' );")
        pass

    def release_index(self):
        # self.cursor.execute("DROP INDEX file_table.file_hash_idx;")
        pass




if __name__ == "__main__":
    pass