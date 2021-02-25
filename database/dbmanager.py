# GPTune Copyright (c) 2019, The Regents of the University of California,
# through Lawrence Berkeley National Laboratory (subject to receipt of any
# required approvals from the U.S.Dept. of Energy) and the University of
# California, Berkeley.  All rights reserved.
#
# If you have questions about your rights to use or distribute this software,
# please contact Berkeley Lab's Intellectual Property Office at IPO@lbl.gov.
#
# NOTICE. This Software was developed under funding from the U.S. Department
# of Energy and the U.S. Government consequently retains certain rights.
# As such, the U.S. Government has been granted for itself and others acting
# on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in
# the Software to reproduce, distribute copies to the public, prepare
# derivative works, and perform publicly and display publicly, and to permit
# other to do so.
#

import os
import json
import os.path
#import numpy as np
import uuid
import sys
from pathlib import Path

import pymongo
class HistoryDB_MongoDB(dict):

    def __init__(self, **kwargs):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        print ("DB NAMES: ", self.client.list_database_names())
        if not "gptune-db" in self.client.list_database_names():
            print ("the database not exist.")
        self.db = self.client["gptune-db"]
        print (self.db)

    def load_json_data(self, application_name, **kwargs):
        json_data = {}
        json_data["name"] = application_name
        json_data["application_info"] = []
        json_data["model_data"] = []
        json_data["func_eval"] = []

        collection = self.db[application_name]
        for document in collection.find():
            document["_id"] = str(document["_id"])
            if document["document_type"] == "application_info":
                json_data["application_info"].append(document)
            elif document["document_type"] == "model_data":
                json_data["model_data"].append(document)
            elif document["document_type"] == "func_eval":
                json_data["func_eval"].append(document)

        return json_data

    def load_model_data(self, application_name, **kwargs):
        model_data_list = []

        collection = self.db[application_name]
        model_data_list = collection.find({"document_type":{"$eq":"model_data"}})

        return model_data_list

    def load_user_collaboration_groups(self, user_email, **kwargs):
        user_groups = []

        groups_db = self.db["group"]
        groups_list = groups_db.find()

        for group_data in groups_list:
            try:
                group_members = group_data["members"]
                for member_data in group_members:
                    if (member_data['email'] == user_email):
                        user_groups.append(group_data)
                        break
            except:
                continue

        return user_groups

    def add_collaboration_group(self, group_details, **kwargs):
        groups_db = self.db["group"]
        if groups_db.count_documents({"group_name":{"$eq":group_details['group_name']}}) == 0:
            groups_db.insert_one(group_details)
            return 0
        else:
            return -1

    def add_group_member(self, group_uid, invite_email, invite_role):
        groups_db = self.db["group"]
        try:
            group_data = groups_db.find({"uid":{"$eq":group_uid}})[0]
            group_members = group_data["members"]
            group_members.append({"email":invite_email, "role":invite_role})
            groups_db.update_one({"uid":group_uid}, {"$set":{"members":group_members}})
            return 0
        except:
            return -1

    def update_group_members(self, group_uid, group_members):
        groups_db = self.db["group"]
        try:
            group_data = groups_db.find({"uid":{"$eq":group_uid}})[0]
            groups_db.update_one({"uid":group_uid}, {"$set":{"members":group_members}})
            return 0
        except:
            return -1

    def load_application_info(self, application_name, **kwargs):
        collection = self.db[application_name]
        application_info = collection.find({"document_type":{"$eq":"application_info"}})[0]
        application_info["_id"] = str(application_info["_id"])
        return application_info

    def get_applications_avail(self, **kwargs):
        applications_avail = []

        collist = self.db.list_collection_names()
        for application_name in collist:
            try:
                collection = self.db[application_name]
                application_info_list = self.db[application_name].find({"document_type":{"$eq":"application_info"}})
                application_info = application_info_list[0]
                applications_avail.append(application_info)
            except:
                # probably there is no document for application_info
                continue

        print ("APPLICATIONS_AVAIL")
        print (applications_avail)

        return applications_avail

    def get_applications_avail_per_library(self, **kwargs):
        applications_avail_per_library = {}

        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            try:
                application_db = self.db[application_name]
                application_info_list = application_db.find({"document_type":{"$eq":"application_info"}})
                application_info = application_info_list[0]
                application_library = application_info["library"]
                if not application_library in applications_avail_per_library:
                    applications_avail_per_library[application_library] = []
                application_name = application_info["name"]
                applications_avail_per_library[application_library].append(application_name)
            except:
                # probably there is no document for application_info
                continue

        return applications_avail_per_library

    def get_user_applications_avail(self, username, **kwargs):
        applications_avail = []

        collist = self.db.list_collection_names()
        for application_name in collist:
            try:
                collection = self.db[application_name]
                application_info_list = self.db[application_name].find({"document_type":{"$eq":"application_info"}})
                application_info = application_info_list[0]
                applications_avail.append(application_info)
            except:
                # probably there is no document for application_info
                continue

        print ("APPLICATIONS_AVAIL")
        print (applications_avail)

        return applications_avail

    def get_user_applications_avail_per_library(self, username, **kwargs):
        applications_avail_per_library = {}

        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            try:
                application_db = self.db[application_name]
                application_info_list = application_db.find({"document_type":{"$eq":"application_info"}})
                application_info = application_info_list[0]
                application_library = application_info["library"]
                if not application_library in applications_avail_per_library:
                    applications_avail_per_library[application_library] = []
                application_name = application_info["name"]
                applications_avail_per_library[application_library].append(application_name)
            except:
                # probably there is no document for application_info
                continue

        return applications_avail_per_library

    def get_machine_deps_avail(self, **kwargs):
        machine_deps_avail = {}

        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            application_db = self.db[application_name]
            machine_deps_avail_givenapp = []
            machine_deps_avail_givenapp_str = []
            func_eval_list = application_db.find({"document_type":{"$eq":"func_eval"}})
            for func_eval in func_eval_list:
                try:
                    machine_deps = func_eval["machine_deps"]
                    machine_deps_str = str(func_eval["machine_deps"])
                    if machine_deps_str not in machine_deps_avail_givenapp_str:
                        machine_deps_avail_givenapp.append(machine_deps)
                        machine_deps_avail_givenapp_str.append(machine_deps_str)
                except:
                    continue
            machine_deps_avail[application_name] = machine_deps_avail_givenapp

        return machine_deps_avail

    def get_software_deps_avail(self, **kwargs):
        software_deps_avail = {}

        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            application_db = self.db[application_name]
            software_deps_avail_givenapp = []
            software_deps_avail_givenapp_str = []
            func_eval_list = application_db.find({"document_type":{"$eq":"func_eval"}})
            for func_eval in func_eval_list:
                try:
                    software_deps = func_eval["compile_deps"]
                    software_deps_str = str(func_eval["compile_deps"])
                    if software_deps_str not in software_deps_avail_givenapp_str:
                        software_deps_avail_givenapp.append(software_deps)
                        software_deps_avail_givenapp_str.append(software_deps_str)
                except:
                    continue
            software_deps_avail[application_name] = software_deps_avail_givenapp

        return software_deps_avail

    def get_users_avail(self, **kwargs):
        users_avail = {}

        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            application_db = self.db[application_name]
            users_avail_givenapp = []
            users_avail_givenapp_str = []
            func_eval_list = application_db.find({"document_type":{"$eq":"func_eval"}})
            for func_eval in func_eval_list:
                users = func_eval["user_info"]
                users_str = str(func_eval["user_info"])
                if users_str not in users_avail_givenapp_str:
                    users_avail_givenapp.append(users)
                    users_avail_givenapp_str.append(users_str)
            users_avail[application_name] = users_avail_givenapp

        return users_avail

    def get_search_data_avail(self, **kwargs):
        search_data_avail = {}

        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            search_data_avail[application_name]  = ["func_eval", "model_data"]
            # TODO: collect available search data type from database

        return search_data_avail

    def check_perf_data_accessibility(self,
            perf_data,
            user_email):
        if "accessibility" in perf_data:
            print (perf_data)

            if perf_data['user_info']['email'] == user_email:
                return True
            elif perf_data['accessibility']['type'] == 'public':
                return True
            elif perf_data['accessibility']['type'] == 'private':
                if perf_data['user_info']['email'] == user_email:
                    return True
                else:
                    return False
            elif perf_data['accessibility']['type'] == 'group':
                for invite in perf_data['accessibility']['group']:
                    if invite == user_email:
                        return True

        return False

    def load_func_eval_filtered(self,
            application_name,
            machine_deps_list,
            software_deps_list,
            users_list,
            user_email,
            **kwargs):
        func_eval_filtered = []

        machine_deps_str_list = []
        software_deps_str_list = []
        users_str_list = []
        for i in range(len(machine_deps_list)):
            machine_deps_str_list.append(str(machine_deps_list[i]))
        for i in range(len(software_deps_list)):
            software_deps_str_list.append(str(software_deps_list[i]))
        for i in range(len(users_list)):
            users_str_list.append(str(users_list[i]))

        print ("machine_deps_str_list: ", machine_deps_str_list)
        print ("software_deps_str_list: ", software_deps_str_list)
        print ("users_str_list: ", users_str_list)

        application_db = self.db[application_name]
        func_eval_list = application_db.find({"document_type":{"$eq":"func_eval"}})

        for func_eval in func_eval_list:
            try:
                func_eval["application"] = application_name
                machine_deps_str = str(func_eval["machine_deps"])
                software_deps_str = str(func_eval["compile_deps"])
                user_str = str(func_eval["user_info"])
                if (machine_deps_str in machine_deps_str_list):
                    if (software_deps_str in software_deps_str_list):
                        if (user_str in users_str_list):
                            if self.check_perf_data_accessibility(func_eval, user_email):
                                func_eval_filtered.append(func_eval)
            except:
                continue

        return func_eval_filtered

    def load_func_eval_by_uid(self, func_eval_uid):
        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            application_db = self.db[application_name]
            func_eval_list = application_db.find({"document_type":{"$eq":"func_eval"}})
            for func_eval in func_eval_list:
                if func_eval["uid"] == func_eval_uid:
                    return func_eval

        return None

    def load_func_eval_by_user(self, user_email):
        func_eval_by_user = []

        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            application_db = self.db[application_name]
            func_eval_list = application_db.find({"document_type":{"$eq":"func_eval"}})
            for func_eval in func_eval_list:
                if func_eval["user_info"]["email"] == user_email:
                    func_eval["application"] = application_name
                    func_eval_by_user.append(func_eval)

        return func_eval_by_user

    def load_perf_data_by_uid(self, perf_data_uid, user_email):
        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            application_db = self.db[application_name]
            func_eval_list = application_db.find({"document_type":{"$eq":"func_eval"}})
            for func_eval in func_eval_list:
                if func_eval["uid"] == perf_data_uid:
                    if self.check_perf_data_accessibility(func_eval, user_email):
                        return func_eval
            model_data_list = application_db.find({"document_type":{"$eq":"model_data"}})
            for model_data in model_data_list:
                if model_data["uid"] == perf_data_uid:
                    if self.check_perf_data_accessibility(model_data, user_email):
                        return model_data

        return None

    def upload_application_info(self, user_info, application_info):
        print ("Upload function evaluation data")
        collist = self.db.list_collection_names()
        print ("Collection List: ", collist)
        application_name = application_info["name"]
        if not application_name in collist:
            print (application_name + " is not exist in the database; create one.")
        collection = self.db[application_name]

        application_info["document_type"] = "application_info"
        application_info["user_info"] = user_info
        if not application_name in collist:
            collection.insert_one(application_info)
        elif collection.count_documents({}) == 0:
            collection.insert_one(application_info)

        return None

    def upload_func_eval(self, json_data, user_info, application_name, accessibility):
        print ("Upload function evaluation data")
        collist = self.db.list_collection_names()
        print ("Collection List: ", collist)
        if not application_name in collist:
            print (application_name + " is not exist in the database; create one.")
        collection = self.db[application_name]

        print (json_data)
        num_added_func_eval = 0
        if "func_eval" in json_data:
            print ("func_eval exist")
            func_eval_list = json_data["func_eval"]
            for func_eval in func_eval_list:
                func_eval["document_type"] = "func_eval"
                func_eval["user_info"] = user_info
                func_eval["accessibility"] = accessibility
                if (collection.count_documents({"uid": { "$eq": func_eval["uid"]}}) == 0):
                    collection.insert_one(func_eval)
                    num_added_func_eval += 1
                else:
                    print ("func_eval: " + func_eval["uid"] + " already exist")

        return num_added_func_eval

    def load_model_data_filtered(self,
            application_name,
            machine_deps_list,
            software_deps_list,
            users_list,
            user_email,
            **kwargs):
        model_data_filtered = []

        machine_deps_str_list = []
        software_deps_str_list = []
        users_str_list = []
        for i in range(len(machine_deps_list)):
            machine_deps_str_list.append(str(machine_deps_list[i]))
        for i in range(len(software_deps_list)):
            software_deps_str_list.append(str(software_deps_list[i]))
        for i in range(len(users_list)):
            users_str_list.append(str(users_list[i]))

        print ("machine_deps_str_list: ", machine_deps_str_list)
        print ("software_deps_str_list: ", software_deps_str_list)
        print ("users_str_list: ", users_str_list)

        application_db = self.db[application_name]
        model_data_list = application_db.find({"document_type":{"$eq":"model_data"}})

        for model_data in model_data_list:
            model_data["application"] = application_name
            func_eval_sample = self.load_func_eval_by_uid(model_data["func_eval"][0])
            machine_deps_str = str(func_eval_sample["machine_deps"])
            software_deps_str = str(func_eval_sample["compile_deps"])
            user_str = str(func_eval_sample["user_info"])
            if (machine_deps_str in machine_deps_str_list):
               if (software_deps_str in software_deps_str_list):
                   if (user_str in users_str_list):
                        model_data_filtered.append(model_data)

        return model_data_filtered

    def load_model_data_by_uid(self, model_data_uid):
        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            application_db = self.db[application_name]
            model_data_list = application_db.find({"document_type":{"$eq":"model_data"}})
            for model_data in model_data_list:
                if model_data["uid"] == model_data_uid:
                    return model_data

        return None

    def load_model_data_by_user(self, user_email):
        model_data_by_user = []

        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            application_db = self.db[application_name]
            model_data_list = application_db.find({"document_type":{"$eq":"model_data"}})
            for model_data in model_data_list:
                if model_data["user_info"]["email"] == user_email:
                    model_data["application"] = application_name
                    model_data_by_user.append(model_data)

        return model_data_by_user

    def upload_model_data(self, json_data, user_info, application_name, accessibility):
        print ("Upload surrogate model data")
        collist = self.db.list_collection_names()
        print ("Collection List: ", collist)
        if not application_name in collist:
            print (application_name + " is not exist in the database; create one.")
        collection = self.db[application_name]

        print (json_data)
        num_added_model_data = 0
        if "model_data" in json_data:
            print ("model_data exist")
            model_data_list = json_data["model_data"]
            for model_data in model_data_list:
                model_data["document_type"] = "model_data"
                model_data["user_info"] = user_info
                model_data["accessibility"] = accessibility
                if (collection.count_documents({"uid": {"$eq":model_data["uid"]}}) == 0):
                    collection.insert_one(model_data)
                    num_added_model_data += 1
                else:
                    print ("model_data: " + model_data["uid"] + " already exist")

        return num_added_model_data

    def delete_perf_data_by_uid(self, application_name, entry_uid):
        application_db = self.db[application_name]
        application_db.delete_one({"uid": entry_uid})

        return None

    def update_entry_accessibility(self, application_name, entry_uid, accessibility):
        application_db = self.db[application_name]
        application_db.update_one({"uid": entry_uid}, {"$set": {"accessibility":accessibility}})

        return None

    def add_machine_info(self, machine_info, user_info):
        machine_db = self.db["machine_db"]

        machine_document = {}
        machine_document["machine_info"] = machine_info
        machine_document["user_info"] = user_info

        import time
        now = time.localtime()

        machine_document["update_time"] = {
                "tm_year":now.tm_year,
                "tm_mon":now.tm_mon,
                "tm_mday":now.tm_mday,
                "tm_hour":now.tm_hour,
                "tm_min":now.tm_min,
                "tm_sec":now.tm_sec,
                "tm_wday":now.tm_wday,
                "tm_yday":now.tm_yday,
                "tm_isdst":now.tm_isdst
                }

        import uuid
        machine_document["uid"] = str(uuid.uuid1())

        machine_db.insert_one(machine_document)

        return None

    def load_all_machine_info(self, **kwargs):
        machine_info_list = []

        for machine_info in self.db["machine_db"].find():
            machine_info_list.append(machine_info)

        return machine_info_list

    def add_tuning_problem(self, tuning_problem_info, user_info, **kwargs):
        tuning_problem_db = self.db["tuning_problem_db"]

        tuning_problem_document = {}
        tuning_problem_document["tuning_problem_info"] = tuning_problem_info
        tuning_problem_document["user_info"] = user_info

        import time
        now = time.localtime()

        tuning_problem_document["update_time"] = {
                "tm_year":now.tm_year,
                "tm_mon":now.tm_mon,
                "tm_mday":now.tm_mday,
                "tm_hour":now.tm_hour,
                "tm_min":now.tm_min,
                "tm_sec":now.tm_sec,
                "tm_wday":now.tm_wday,
                "tm_yday":now.tm_yday,
                "tm_isdst":now.tm_isdst
                }

        import uuid
        tuning_problem_document["uid"] = str(uuid.uuid1())

        tuning_problem_db.insert_one(tuning_problem_document)

        return None

    def load_all_tuning_problems(self, **kwargs):
        tuning_problem_list = []

        for tuning_problem in self.db["tuning_problem_db"].find():
            tuning_problem_list.append(tuning_problem)

        return tuning_problem_list

if __name__ == "__main__":
    import sys
    import json

    #print (sys.argv[1])
    historydb = HistoryDB_MongoDB()
#    with open(sys.argv[1], "r") as f_in:
#        data = f_in.read()
#        json_data = json.loads(data)
#    historydb.upload_func_eval(json_data, {"name":"younghyun"}, {"name:":"PDGEQRF", "library":"ScaLAPACK"}, {"type":"public"})
#    historydb.upload_model_data(json_data, {"name":"younghyun"}, {"name":"PDGEQRF", "library":"ScaLAPACK"}, {"type":"public"})
#
#    json_data = historydb.load_json_data("PDGEQRF")
#    with open("asdf.json", "w") as f_out:
#        json.dump(json_data, f_out, indent=2)

    #group_details = {
    #        "group_name": "mygroup",
    #        "members" : [
    #            {
    #                "email": "member1@example.com",
    #                "level": "edit"
    #            },
    #            {
    #                "email": "member2@example.com",
    #                "level": "view"
    #            }
    #            ]
    #        }
    #historydb.add_collaboration_group(group_details)
