# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import pathmagic
import hashlib
import gridfs
import logging
from db_pool import *

# Writes binaries on the DB


class PackageController():

    def __init__(self):
        self.fs = gridfs.GridFS(db_fs)
        self.collection = db_fs["fs.files"]
        if(envget('temporal_files_db')):
            self.fs_temp = gridfs.GridFS(db_temp)
            self.collection_tmp = db_temp["fs.files"]

    def __delete__(self):
        pass

    # adds a file to the file database.
    def append(self, file_id, data, vt_blocked=False):
        if(envget('temporal_files_db')):
            self.fs_temp.put(data, filename=file_id, metadata={
                             "vt_blocked": vt_blocked})
        else:
            self.fs.put(data, filename=file_id, metadata={
                        "vt_blocked": vt_blocked})

    # returns searched file
    # returns None if it does not exist.
    def getFile(self, file_id):
        if(len(file_id) == 40):
            f = self.fs.find_one({"filename": file_id})
        elif(len(file_id) == 32):
            f = self.fs.find_one({"md5": file_id})
        else:
            logging.warning("PackageController: invalid file_id:" +
                            str(file_id) + "(len=" + str(len(file_id)) + ")")
            f = None
        if f is None:
            if envget('temporal_files_db') is False:
                return None
            else:
                if(len(file_id) == 40):
                    f = self.fs_temp.find_one({"filename": file_id})
                elif(len(file_id) == 32):
                    f = self.fs_temp.find_one({"md5": file_id})
                else:
                    f = None
                    logging.warning(
                        "PackageController tmp: invalid file_id" + str(file_id))
                if f is None:
                    return None
        return f.read()

    def md5_to_sha1(self, md5):
        if len(md5) != 32:
            raise ValueError("not a valid md5")
        f = self.collection.find_one({"md5": md5})
        if f is None:
            if envget('temporal_files_db') is False:
                logging.debug("md5_to_sha1= none")
                return None
            else:
                f = self.collection_tmp.find_one({"md5": md5})
                if f is None:
                    logging.debug("md5_to_sha1= none")
                    return None
        return f["filename"]

    def last_updated(self, number):
        if(envget('temporal_files_db')):
            db_files = db_temp
        else:
            db_files = db_fs
        collection_files = db_files["fs.files"].find().sort(
            [("_id", -1)]).limit(number)
        result = []
        for document in collection_files:
            sha1 = document.get('filename')
            md5 = document.get('md5')
            tmp_doc = {}
            tmp_doc["hash"] = {"sha1": sha1, "md5": md5}
            tmp_doc["upload_date"] = document.get('uploadDate')
            result.append(tmp_doc)
        return result

    # returns None if the file can't be found on the DB.
    # 0 if the file exists.
    # 1 if the file exists but can't be downloaded.
    # (Check if it is being used)
    def searchFile(self, file_id):
        ret = self.fs.find_one({"filename": file_id})
        if(ret is None):
            if(envget('temporal_files_db') is False):
                return None
            else:
                ret = self.fs_temp.find_one({"filename": file_id})
                if(ret is None):
                    return None
        if(ret.metadata is not None and ret.metadata.get("vt_blocked") is True):
            return 1
        else:
            return 0

# ****************TEST_CODE******************


def testCode():
    pc = PackageController(host="192.168.0.45", db_name="DATABASE_TEST")

    for dato in ["test_vt1", "test_vt2"]:
        hs = hashlib.sha1(dato).hexdigest()
        res = pc.searchFile(hs)
        if(res is None):
            print("appending: " + dato)
            if(dato == "test_vt1"):
                pc.append(hs, dato, True)
            else:
                pc.append(hs, dato)
        if(res == 0):
            print(dato + " already exists with:" + str(res))
        if(res == 1):
            print(dato + " blocked:" + str(res))

    for dato in ["test_vt1", "test_vt2", "test_vt3"]:
        hs = hashlib.sha1(dato).hexdigest()
        res = pc.searchFile(hs)
        if(res is None):
            print("File does not exist: " + dato)
        if(res == 0):
            print(dato + " File already exist:" + str(res))
        if(res == 1):
            print(dato + " blocked:" + str(res))

# ****************TEST_EXECUTE******************
# from Utils.test import test
# test("-test_PackageController",testCode)


if __name__ == "__main__":
    testCode()
