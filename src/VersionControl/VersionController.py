# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import os
from db_pool import *
from Utils.test import test
# versioning controller of executed plugins.


class VersionController:

    def __init__(self):
        self.collection = db_ver.version_container
        # print(self.collection)

    def __delete__(self):
        pass

    def updateVersion(self, file_id, ver_dic):
        if len(file_id) != 40:
            raise ValueError("VersionController: file_id not sha1")
        command = {"$set": ver_dic}
        self.collection.update_one({"file_id": file_id}, command, upsert=True)

    def searchVersion(self, file_id):
        f = self.collection.find_one({"file_id": file_id})
        return f


# ****************TEST_CODE******************
def testCode():
    db = DBVersion()
    ver = {}
    for i in range(0, 10):
        ver[str(i)] = i + 10
    # db.updateVersion("0000",ver)
    lver = db.loadVersion("0000")
    n = lver["3"]
    print(type(n))


# ****************TEST_EXECUTE******************
test("-test_VersionController", testCode)
