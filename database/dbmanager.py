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
import copy

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
        json_data["surrogate_model"] = []
        json_data["func_eval"] = []

        collection = self.db[application_name]
        for document in collection.find():
            document["_id"] = str(document["_id"])
            if document["document_type"] == "application_info":
                json_data["application_info"].append(document)
            elif document["document_type"] == "surrogate_model":
                json_data["surrogate_model"].append(document)
            elif document["document_type"] == "func_eval":
                json_data["func_eval"].append(document)

        return json_data

    def load_surrogate_models(self, tuning_problem_name, **kwargs):
        surrogate_model_list = []

        for document in self.db[tuning_problem_name].find({"document_Tyep":{"$eq":"surrogate_model"}}):
            surrogate_model_list.append(document)

        return surrogate_model_list

    def get_num_tuning_problems(self):
        return self.db["tuning_problem_db"].count_documents({})

    def get_num_function_evaulations(self):
        num_function_evaluations = 0
        applications_list = self.db.list_collection_names()
        for application_name in applications_list:
            application_db = self.db[application_name]
            num_function_evaluations += application_db.count_documents({"document_type":{"$eq":"func_eval"}})
        return num_function_evaluations

    def load_user_collaboration_groups(self, user_email, **kwargs):
        user_groups = []

        groups_db = self.db["collaboration_groups"]
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
        groups_db = self.db["collaboration_groups"]
        if groups_db.count_documents({"group_name":{"$eq":group_details['group_name']}}) == 0:
            groups_db.insert_one(group_details)
            return 0
        else:
            return -1

    def add_group_member(self, group_uid, invite_email, invite_role):
        groups_db = self.db["collaboration_groups"]
        try:
            group_data = groups_db.find({"uid":{"$eq":group_uid}})[0]
            group_members = group_data["members"]
            group_members.append({"email":invite_email, "role":invite_role})
            groups_db.update_one({"uid":group_uid}, {"$set":{"members":group_members}})
            return 0
        except:
            return -1

    def update_group_members(self, group_uid, group_members):
        groups_db = self.db["collaboration_groups"]
        try:
            group_data = groups_db.find({"uid":{"$eq":group_uid}})[0]
            groups_db.update_one({"uid":group_uid}, {"$set":{"members":group_members}})
            return 0
        except:
            return -1

    def load_access_tokens(self, user_name):

        access_token_documents = []
        token_db = self.db["access_tokens_db"]

        for document in token_db.find({"user_info_real.user_name":{"$eq":user_name}}):
            access_token_documents.append(document)

        return access_token_documents

    def add_access_token(self, access_token, user_info_real, user_info_display, accessibility, expiration):
        #token_db = self.db["access_tokens_"+user_info_real["user_name"]]
        token_db = self.db["access_tokens_db"]
        try:
            if token_db.count_documents({"access_token":{"$eq":access_token}}) == 0:
                import datetime
                creation_time = datetime.datetime.now()
                if expiration == "7days":
                    expiration_time = creation_time+datetime.timedelta(days=7)
                elif expiration == "30days":
                    expiration_time = creation_time+datetime.timedelta(days=30)
                elif expiration == "60days":
                    expiration_time = creation_time+datetime.timedelta(days=60)
                elif expiration == "90days":
                    expiration_time = creation_time+datetime.timedelta(days=90)

                creation_time = creation_time.timetuple()
                expiration_time = expiration_time.timetuple()

                token_db.insert_one({
                        "access_token" : access_token,
                        "user_info_real" : user_info_real,
                        "user_info_display" : user_info_display,
                        "accessibility" : accessibility,
                        "creation_time" : {
                            "tm_year":creation_time.tm_year,
                            "tm_mon":creation_time.tm_mon,
                            "tm_mday":creation_time.tm_mday,
                            "tm_hour":creation_time.tm_hour,
                            "tm_min":creation_time.tm_min,
                            "tm_sec":creation_time.tm_sec,
                            "tm_wday":creation_time.tm_wday,
                            "tm_yday":creation_time.tm_yday,
                            "tm_isdst":creation_time.tm_isdst
                        },
                        "expiration_time" : {
                            "tm_year":expiration_time.tm_year,
                            "tm_mon":expiration_time.tm_mon,
                            "tm_mday":expiration_time.tm_mday,
                            "tm_hour":expiration_time.tm_hour,
                            "tm_min":expiration_time.tm_min,
                            "tm_sec":expiration_time.tm_sec,
                            "tm_wday":expiration_time.tm_wday,
                            "tm_yday":expiration_time.tm_yday,
                            "tm_isdst":expiration_time.tm_isdst
                        }
                    })
            return 0
        except:
            return -1

    def add_access_token_rsa(self, public_key, user_info_real, user_info_display, accessibility):
        access_token = public_key
        #token_db = self.db["access_tokens_"+user_info_real["user_name"]]
        token_db = self.db["access_tokens_db"]
        try:
            if token_db.count_documents({"access_token":{"$eq":access_token}}) == 0:
                import datetime
                creation_time = datetime.datetime.now()
                if expiration == "7days":
                    expiration_time = creation_time+datetime.timedelta(days=7)
                elif expiration == "30days":
                    expiration_time = creation_time+datetime.timedelta(days=30)
                elif expiration == "60days":
                    expiration_time = creation_time+datetime.timedelta(days=60)
                elif expiration == "90days":
                    expiration_time = creation_time+datetime.timedelta(days=90)

                creation_time = creation_time.timetuple()
                expiration_time = expiration_time.timetuple()

                token_db.insert_one({
                        "access_token" : access_token,
                        "user_info_real" : user_info_real,
                        "user_info_display" : user_info_display,
                        "accessibility" : accessibility,
                        "creation_time" : {
                            "tm_year":creation_time.tm_year,
                            "tm_mon":creation_time.tm_mon,
                            "tm_mday":creation_time.tm_mday,
                            "tm_hour":creation_time.tm_hour,
                            "tm_min":creation_time.tm_min,
                            "tm_sec":creation_time.tm_sec,
                            "tm_wday":creation_time.tm_wday,
                            "tm_yday":creation_time.tm_yday,
                            "tm_isdst":creation_time.tm_isdst
                        },
                        "expiration_time" : {
                            "tm_year":expiration_time.tm_year,
                            "tm_mon":expiration_time.tm_mon,
                            "tm_mday":expiration_time.tm_mday,
                            "tm_hour":expiration_time.tm_hour,
                            "tm_min":expiration_time.tm_min,
                            "tm_sec":expiration_time.tm_sec,
                            "tm_wday":expiration_time.tm_wday,
                            "tm_yday":expiration_time.tm_yday,
                            "tm_isdst":expiration_time.tm_isdst
                        }
                    })
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

    def get_machine_configurations_avail(self, **kwargs):
        machine_configurations_avail = {}

        for tuning_problem in self.db["tuning_problem_db"].find():
            collection_name = tuning_problem["unique_name"]

            machine_configurations_avail[collection_name] = []

            func_eval_list = self.db[collection_name].find({"document_type":{"$eq":"func_eval"}})
            for func_eval in func_eval_list:
                try:
                    machine_configuration = func_eval["machine_configuration"]
                    for key in machine_configuration:
                        try:
                            if "node_list" in machine_configuration[key]:
                                machine_configuration[key].pop("node_list")
                        except:
                            pass

                    if machine_configuration not in machine_configurations_avail[collection_name]:
                        machine_configurations_avail[collection_name].append(machine_configuration)
                except:
                    print ("not able to load machine configuration of func_eval: ", func_eval["uid"])
                    continue

        return machine_configurations_avail

    def get_software_configurations_avail(self, **kwargs):
        software_configurations_avail = {}

        for tuning_problem in self.db["tuning_problem_db"].find():
            collection_name = tuning_problem["unique_name"]

            software_configurations_avail[collection_name] = []

            func_eval_list = self.db[collection_name].find({"document_type":{"$eq":"func_eval"}})
            for func_eval in func_eval_list:
                try:
                    software_configuration = func_eval["software_configuration"]
                    if software_configuration not in software_configurations_avail[collection_name]:
                        software_configurations_avail[collection_name].append(software_configuration)
                except:
                    print ("not able to load software configuration of func_eval: ", func_eval["uid"])
                    continue

        return software_configurations_avail

    def get_outputs_avail(self, **kwargs):
        outputs_avail = {}

        for tuning_problem in self.db["tuning_problem_db"].find():
            collection_name = tuning_problem["unique_name"]

            outputs_avail[collection_name] = []
            outputs = tuning_problem["tuning_problem_info"]["output_info"]
            for output in outputs:
                outputs_avail[collection_name].append(output["output_name"])

        return outputs_avail

    def get_user_configurations_avail(self, **kwargs):
        user_configurations_avail = {}

        for tuning_problem in self.db["tuning_problem_db"].find():
            collection_name = tuning_problem["unique_name"]

            user_configurations_avail[collection_name] = []

            func_eval_list = self.db[collection_name].find({"document_type":{"$eq":"func_eval"}})
            for func_eval in func_eval_list:
                try:
                    user_configuration = func_eval["user_info"]
                    if user_configuration not in user_configurations_avail[collection_name]:
                        user_configurations_avail[collection_name].append(user_configuration)
                except:
                    print ("not able to load software configuration of func_eval: ", func_eval["uid"])
                    continue

        return user_configurations_avail

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

    #def get_search_data_avail(self, **kwargs):
    #    search_data_avail = {}

    #    applications_list = self.db.list_collection_names()
    #    for application_name in applications_list:
    #        search_data_avail[application_name]  = ["func_eval", "model_data"]
    #        # TODO: collect available search data type from database

    #    return search_data_avail

    def check_perf_data_accessibility(self,
            perf_data,
            user_email):
        if "accessibility" in perf_data:
            #print (perf_data)
            #print ("user_email: ", user_email)

            if perf_data['user_info']['user_email'] == user_email:
                return True
            elif perf_data['accessibility']['type'] == 'public':
                return True
            elif perf_data['accessibility']['type'] == 'registered':
                if user_email != "":
                    return True
                else:
                    return False
            elif perf_data['accessibility']['type'] == 'private':
                if perf_data['user_info']['user_email'] == user_email:
                    return True
                else:
                    return False
            elif perf_data['accessibility']['type'] == 'group':
                for invite in perf_data['accessibility']['group']:
                    if invite == user_email:
                        return True

        return False

    def get_tuning_problem_type(self, tuning_problem_unique_name):
        document = list(self.db["tuning_problem_db"].find({"unique_name":{"$eq":tuning_problem_unique_name}}))
        print ("document: ", len(document))
        if len(document) > 0:
            return "regular"
        else:
            document = list(self.db["flexible_tuning_problem_db"].find({"unique_name":{"$eq":tuning_problem_unique_name}}))
            if len(document) > 0:
                return "flexible"
            else:
                return "unknown"

    def get_tuning_problem_simple_name(self, tuning_problem_unique_name, tuning_problem_type="regular"):
        if tuning_problem_type == "regular":
            document = self.db["tuning_problem_db"].find({"unique_name":{"$eq":tuning_problem_unique_name}})[0]
        elif tuning_problem_type == "flexible":
            document = self.db["flexible_tuning_problem_db"].find({"unique_name":{"$eq":tuning_problem_unique_name}})[0]
        else:
            return None
        return document["tuning_problem_name"]

    def get_tuning_problem_info(self, tuning_problem_unique_name, tuning_problem_type="regular"):
        if tuning_problem_type == "regular":
            document = self.db["tuning_problem_db"].find({"unique_name":{"$eq":tuning_problem_unique_name}})[0]
        elif tuning_problem_type == "flexible":
            document = self.db["flexible_tuning_problem_db"].find({"unique_name":{"$eq":tuning_problem_unique_name}})[0]
        else:
            return None
        return document #["tuning_problem_info"]

    def load_func_eval_filtered(self,
            tuning_problem_unique_name,
            machine_configurations_list,
            software_configurations_list,
            output_options,
            user_configurations_list,
            user_email,
            tuning_problem_type="regular",
            **kwargs):
        func_eval_filtered = []

        application_db = self.db[tuning_problem_unique_name]
        func_eval_list = application_db.find({"document_type":{"$eq":"func_eval"}})

        tuning_problem_simple_name = self.get_tuning_problem_simple_name(tuning_problem_unique_name, tuning_problem_type)

        for func_eval in func_eval_list:
            try:
                func_eval["tuning_problem_name"] = tuning_problem_simple_name
                machine_configuration = copy.deepcopy(func_eval["machine_configuration"])
                for key in machine_configuration:
                    try:
                        if "node_list" in machine_configuration[key]:
                            machine_configuration[key].pop("node_list")
                    except:
                        pass
                software_configuration = func_eval["software_configuration"]
                user_information = func_eval["user_info"]

                #print ("output_options: ", output_options)
                #print ("evaluation_result_keys: ", list(func_eval["evaluation_result"].keys()))

                if (machine_configuration in machine_configurations_list) and\
                   (software_configuration in software_configurations_list) and\
                   all(elem in list(func_eval["evaluation_result"].keys()) for elem in output_options) and\
                   (user_information in user_configurations_list):
                    if self.check_perf_data_accessibility(func_eval, user_email):
                        func_eval_filtered.append(func_eval)
            except:
                print ("func_eval load failed")
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

        for tuning_problem in self.db["tuning_problem_db"].find():
            collection_name = tuning_problem["unique_name"]
            application_db = self.db[collection_name]
            func_eval_list = application_db.find({"document_type":{"$eq":"func_eval"}})
            for func_eval in func_eval_list:
                if func_eval["user_info"]["user_email"] == user_email:
                    func_eval["tuning_problem_name"] = self.get_tuning_problem_simple_name(collection_name)
                    func_eval["tuning_problem_unique_name"] = collection_name
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
            surrogate_model_list = application_db.find({"document_type":{"$eq":"surrogate_model"}})
            for surrogate_model in surrogate_model_list:
                if surrogate_model["uid"] == perf_data_uid:
                    if self.check_perf_data_accessibility(surrogate_model, user_email):
                        return surrogate_model

        return None

    def check_problem_space(self,
            func_eval,
            problem_space,
            **kwargs):

        if "parameter_space" in problem_space:
            for parameter_space in problem_space["parameter_space"]:
                parameter_name = parameter_space["name"]
                if parameter_name not in func_eval["tuning_parameter"]:
                    return False

                parameter_type = parameter_space["type"]
                if parameter_type == "integer" or parameter_type == "real":
                    param_value = func_eval["tuning_parameter"][parameter_name]
                    if param_value < parameter_space["lower_bound"] or\
                       param_value > parameter_space["upper_bound"]:
                        return False
                elif parameter_type == "categorical":
                    param_value = func_eval["tuning_parameter"][parameter_name]
                    if param_value not in parameter_space["categories"]:
                        return False

        if "input_space" in problem_space:
            for input_space in problem_space["input_space"]:
                parameter_name = input_space["name"]
                if parameter_name not in func_eval["task_parameter"]:
                    return False

                parameter_type = input_space["type"]
                if parameter_type == "integer" or parameter_type == "real":
                    param_value = func_eval["task_parameter"][parameter_name]
                    if param_value < input_space["lower_bound"] or\
                       param_value > input_space["upper_bound"]:
                        return False
                elif parameter_type == "categorical":
                    param_value = func_eval["task_parameter"][parameter_name]
                    if param_value not in input_space["categories"]:
                        return False

        if "constants" in problem_space:
            constants_checked = False
            for constants in problem_space["constants"]:
                var_match = True
                for constant_name in constants:
                    if constant_name not in func_eval["constants"]:
                        var_match = False
                    if constants[constant_name] != func_eval["constants"][constant_name]:
                        var_match = False
                if var_match == True:
                    constants_checked = True
            if constants_checked == False:
                return False

        if "output_space" in problem_space:
            for output_space in problem_space["output_space"]:
                parameter_name = output_space["name"]
                if parameter_name not in func_eval["evaluation_result"]:
                    return False

                parameter_type = output_space["type"]
                if parameter_type == "integer" or parameter_type == "real":
                    param_value = func_eval["evaluation_result"][parameter_name]
                    if param_value < output_space["lower_bound"] or\
                       param_value > output_space["upper_bound"]:
                        return False
                elif parameter_type == "categorical":
                    param_value = func_eval["evaluation_result"][parameter_name]
                    if param_value not in output_space["categories"]:
                        return False

        return True

    def load_func_eval_with_token(self,
            access_token,
            tuning_problem_name,
            problem_space,
            configuration_space,
            **kwargs):

        if configuration_space == {}: # if not provided
            func_eval_list = []

            for tuning_problem_document in self.db["tuning_problem_db"].find({"tuning_problem_name":{"$eq":tuning_problem_name}}):
                tuning_problem_unique_name = tuning_problem_document["unique_name"]

                application_db = self.db[tuning_problem_unique_name]

                for func_eval in application_db.find({"document_type":{"$eq":"func_eval"}}):
                    func_eval.pop("_id")
                    func_eval.pop("accessibility")
                    func_eval.pop("document_type")

                    if (self.check_problem_space(func_eval, problem_space)):
                        func_eval_list.append(func_eval)

            return func_eval_list
        else:
            machine_configurations_list = configuration_space["machine_configurations"]
            software_configurations_list = configuration_space["software_configurations"]
            user_configurations_list = configuration_space["user_configurations"]

            func_eval_list = []

            for tuning_problem_document in self.db["tuning_problem_db"].find({"tuning_problem_name":{"$eq":tuning_problem_name}}):
                tuning_problem_unique_name = tuning_problem_document["unique_name"]

                application_db = self.db[tuning_problem_unique_name]

                for func_eval in application_db.find({"document_type":{"$eq":"func_eval"}}):
                    func_eval.pop("_id")
                    func_eval.pop("accessibility")
                    func_eval.pop("document_type")

                    if (self.check_problem_space(func_eval, problem_space)) == False:
                        continue
                    if "machine_configurations" in configuration_space:
                        machine_configuration = copy.deepcopy(func_eval["machine_configuration"])
                        for key in machine_configuration:
                            try:
                                if "node_list" in machine_configuration[key]:
                                    machine_configuration[key].pop("node_list")
                            except:
                                pass
                        if machine_configuration not in configuration_space["machine_configuration"]:
                            continue
                    if "software_configurations" in configuration_space:
                        if func_eval["software_configuration"] not in configuration_space["software_configurations"]:
                            continue
                    if "user_configurations" in configuration_space:
                        user_information = func_eval["user_info"]
                        if user_information not in configuration_space["user_configurations"]:
                            continue

                    func_eval_list.append(func_eval)

            return func_eval_list

    def load_user_info_by_access_token(self, access_token):
        try:
            import sys
            if sys.version_info < (3,9):
                from Cryptodome.PublicKey import RSA
            else:
                from Crypto.PublicKey import RSA
            rsa_key_input = "-----BEGIN RSA PRIVATE KEY-----\n"
            rsa_key_input += access_token.replace("\\n","\n")
            rsa_key_input += "\n-----END RSA PRIVATE KEY-----"
            rsa_key_input = str(rsa_key_input)
            key = RSA.import_key(rsa_key_input)
            private_key = key.export_key()
            public_key = str(key.publickey().export_key())
            public_key = public_key.replace("b'-----BEGIN PUBLIC KEY-----\\n","").replace("\\n-----END PUBLIC KEY-----'","").replace("\n","\\n")
            #print ("rsa_key_input: ", rsa_key_input)
            #print ("public_key: ", public_key)
            access_token = public_key
        except:
            print ("This may not be an RSA key")

        access_token_info_list = []
        for access_token_info in self.db["access_tokens_db"].find({"access_token":{"$eq":access_token}}):
            access_token_info_list.append(access_token_info)
        return access_token_info_list[0]

    def store_func_eval_with_token(self,
            access_token,
            tuning_problem_name,
            function_evaluation,
            **kwargs):

        # TODO: fill in this info based on the access token
        function_evaluation["tuning_problem_name"] = tuning_problem_name
        #function_evaluation["access_token"] = access_token

        access_token_info = self.load_user_info_by_access_token(access_token)

        function_evaluation["user_info"] = access_token_info["user_info_real"]
        function_evaluation["user_info_display"] = access_token_info["user_info_display"]
        function_evaluation["document_type"] = "func_eval"
        function_evaluation["accessibility"] = access_token_info["accessibility"]
        function_evaluation["how_submitted"] = "direct_upload_with_token"

        for tuning_problem_document in self.db["tuning_problem_db"].find({"tuning_problem_name":{"$eq":tuning_problem_name}}):
            tuning_problem_unique_name = tuning_problem_document["unique_name"]

            application_db = self.db[tuning_problem_unique_name]
            # TODO: more check routines
            if (application_db.count_documents({"uid": { "$eq": function_evaluation["uid"]}}) == 0):
                print ("tuning_problem_unique_name: ", tuning_problem_unique_name, " insert one: ", function_evaluation)
                application_db.insert_one(function_evaluation)

        return 0

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

    def check_tuning_problem_matching(self, tuning_problem_unique_name, func_eval):
        tuning_problem_info = self.db["tuning_problem_db"].find({"unique_name":{"$eq":tuning_problem_unique_name}})[0]["tuning_problem_info"]
        print ("tuning_problem_info: ", tuning_problem_info)

        # check task information matching
        task_info = {}
        for task in tuning_problem_info["task_info"]:
            task_info[task["task_name"]] = task["task_type"]

        for task in func_eval["task_parameter"]:
            if task not in task_info:
                print ("task: " + str(task) + " not exists in the task definition")
                return False
            if type(func_eval["task_parameter"][task]) is int and task_info[task] != "integer":
                print ("task: " + str(task) + " type does not match")
                return False
            if type(func_eval["task_parameter"][task]) is float and task_info[task] != "real":
                print ("task: " + str(task) + " type does not match")
                return False
            if type(func_eval["task_parameter"][task]) is str and task_info[task] != "categorical":
                print ("task: " + str(task) + " type does not match")
                return False
            print ("task: " + str(task) + " information matches")

        # check parameter information matching
        tuning_parameter_info = {}
        for tuning_parameter in tuning_problem_info["parameter_info"]:
            tuning_parameter_info[tuning_parameter["parameter_name"]] = tuning_parameter["parameter_type"]

        for tuning_parameter in func_eval["tuning_parameter"]:
            if tuning_parameter not in tuning_parameter_info:
                print ("tuning_parameter: " + str(tuning_parameter) + " not exists in the parameter definition")
                return False
            if type(func_eval["tuning_parameter"][tuning_parameter]) is int and tuning_parameter_info[tuning_parameter] != "integer":
                print ("parameter: " + str(tuning_parameter) + " type does not match")
                return False
            if type(func_eval["tuning_parameter"][tuning_parameter]) is float and tuning_parameter_info[tuning_parameter] != "real":
                print ("parameter: " + str(tuning_parameter) + " type does not match")
                return False
            if type(func_eval["tuning_parameter"][tuning_parameter]) is str and tuning_parameter_info[tuning_parameter] != "categorical":
                print ("parameter: " + str(tuning_parameter) + " type does not match")
                return False
            print ("tuning_parameter: " + str(tuning_parameter) + " information matches")

        # check output information matching
        output_info = {}
        for output in tuning_problem_info["output_info"]:
            output_info[output["output_name"]] = output["output_type"]

        for output in func_eval["evaluation_result"]:
            if output not in output_info:
                print ("output: " + str(output) + " not exists in the output definition")
                return False
            if type(func_eval["evaluation_result"][output]) is int and output_info[output] != "integer":
                print ("output: " + str(output) + " type does not match")
                return False
            if type(func_eval["evaluation_result"][output]) is float and output_info[output] != "real":
                print ("output: " + str(output) + " type does not match")
                return False
            if type(func_eval["evaluation_result"][output]) is str and output_info[output] != "categorical":
                print ("output: " + str(output) + " type does not match")
                return False
            print ("output: " + str(output) + " information matches")

        return True

    def check_software_information_matching(self, tuning_problem_unique_name, func_eval):
        tuning_problem_info = self.db["tuning_problem_db"].find({"unique_name":{"$eq":tuning_problem_unique_name}})[0]["tuning_problem_info"]
        print ("tuning_problem_info: ", tuning_problem_info)

        # check required software information is given
        required_software_list = tuning_problem_info["required_software_info"]
        for required_software in required_software_list:
            software_name_tags = []
            software_name_tags.append(required_software["software_name"])
            for name_tag in required_software["software_tags"]:
                software_name_tags.append(name_tag)

            software_information_type = required_software["software_type"]
            software_information_type_given = ""

            for name_tag in software_name_tags:
                if name_tag in func_eval["software_configuration"]:
                    software_information_type_given = func_eval["software_configuration"][name_tag]

            if software_information_type_given == "":
                print ("software information (" + required_software["software_name"] + ") is not given")
                return False
            elif software_information_type not in software_information_type_given:
                print ("software information type (" + software_information_type + ") is not given")
                return False

        return True

    def check_machine_information_matching(self, machine_unique_name, func_eval):
        machine_info = self.db["machine_db"].find({"unique_name": {"$eq": machine_unique_name}})[0]["machine_info"]
        print ("check_machine_information_matching: ", machine_info)

        # check processor information is given
        processor_list = machine_info["processor_model"]
        if (len(processor_list) == 0): # no processor info is given (no need to check)
            return True
        processors_found = []

        for processor in processor_list:
            processor_name_tags = []
            processor_name_tags.append(processor["processor_model_name"])
            for name_tag in processor["processor_model_tags"]:
                processor_name_tags.append(name_tag)

            for name_tag in processor_name_tags:
                print ("name_tag: ", name_tag)
                if name_tag in func_eval["machine_configuration"]:
                    processors_found.append(processor_name_tags[0])
                    break

        print ("processors_found: ", processors_found)
        if (len(processors_found) > 0):
            return True
        else:
            print ("processor (" + str(processor_list) + ") information is not given")
            return False

    def upload_func_eval(self, tuning_problem_unique_name, machine_unique_name, json_data, user_info, accessibility, tuning_problem_type="regular"):
        collection_name = tuning_problem_unique_name
        collist = self.db.list_collection_names()
        if not collection_name in collist:
            print (collection_name + " is not exist in the database; create one.")
        collection = self.db[collection_name]

        num_added_func_eval = 0
        if "func_eval" in json_data:
            func_eval_list = json_data["func_eval"]
            for func_eval in func_eval_list:
                func_eval["document_type"] = "func_eval"
                func_eval["user_info"] = user_info
                func_eval["accessibility"] = accessibility

                if (tuning_problem_type == "flexible"):
                    if "uid" in func_eval:
                        if (collection.count_documents({"uid": { "$eq": func_eval["uid"]}}) == 0):
                            collection.insert_one(func_eval)
                            num_added_func_eval += 1
                        else:
                            print ("func_eval: " + func_eval["uid"] + " already exist")
                    else:
                        collection.insert_one(func_eval)
                        num_added_func_eval += 1
                else:
                    if (self.check_tuning_problem_matching(tuning_problem_unique_name, func_eval)):
                        if (self.check_software_information_matching(tuning_problem_unique_name, func_eval)):
                            if (self.check_machine_information_matching(machine_unique_name, func_eval)):
                                if (collection.count_documents({"uid": { "$eq": func_eval["uid"]}}) == 0):
                                    collection.insert_one(func_eval)
                                    num_added_func_eval += 1
                                else:
                                    print ("func_eval: " + func_eval["uid"] + " already exist")
                            else:
                                print ("func_eval: " + func_eval["uid"] + " does not match the machine information")
                        else:
                            print ("func_eval: " + func_eval["uid"] + " does not match the software information")
                    else:
                        print ("func_eval: " + func_eval["uid"] + " does not match the tuning problem")

        return num_added_func_eval

    def load_surrogate_models_filtered(self,
            tuning_problem_unique_name,
            machine_configurations_list,
            software_configurations_list,
            output_options,
            user_configurations_list,
            user_email,
            tuning_problem_type="regular",
            **kwargs):
        surrogate_model_list_filtered = {}
        for output_option in output_options:
            surrogate_model_list_filtered[output_option] = []

        application_db = self.db[tuning_problem_unique_name]
        surrogate_model_list = application_db.find({"document_type":{"$eq":"surrogate_model"}})

        tuning_problem_simple_name = self.get_tuning_problem_simple_name(tuning_problem_unique_name, tuning_problem_type)

        for surrogate_model in surrogate_model_list:
            try:
                surrogate_model["tuning_problem_name"] = tuning_problem_simple_name
                func_eval = self.load_func_eval_by_uid(surrogate_model["function_evaluations"][0])
                machine_configuration = func_eval["machine_configuration"]
                software_configuration = func_eval["software_configuration"]
                user_information = surrogate_model["user_info"]

                if (machine_configuration in machine_configurations_list) and\
                   (software_configuration in software_configurations_list) and\
                   (user_information in user_configurations_list):
                    if self.check_perf_data_accessibility(surrogate_model, user_email):
                        surrogate_model_list_filtered[surrogate_model["objective"]["name"]].append(surrogate_model)
            except:
                continue

        return surrogate_model_list_filtered

    def load_surrogate_model_by_uid(self, surrogate_model_uid):
        for collection_name in self.db.list_collection_names():
            application_db = self.db[collection_name]
            surrogate_model_list = application_db.find({"document_type":{"$eq":"surrogate_model"}})
            for surrogate_model in surrogate_model_list:
                if surrogate_model["uid"] == surrogate_model_uid:
                    tuning_problem_simple_name = self.get_tuning_problem_simple_name(collection_name)
                    surrogate_model["tuning_problem_name"] = tuning_problem_simple_name
                    return surrogate_model

        return None

    def load_surrogate_models_by_uids(self, surrogate_model_uids):
        surrogate_models = []
        for collection_name in self.db.list_collection_names():
            application_db = self.db[collection_name]
            surrogate_model_list = application_db.find({"document_type":{"$eq":"surrogate_model"}})
            for surrogate_model in surrogate_model_list:
                if surrogate_model["uid"] in surrogate_model_uids:
                    tuning_problem_simple_name = self.get_tuning_problem_simple_name(collection_name)
                    surrogate_model["tuning_problem_name"] = tuning_problem_simple_name
                    surrogate_models.append(surrogate_model)

        return surrogate_models

#    def load_surrogate_model_function(self, surrogate_model_uid):
#
#        applications_list = self.db.list_collection_names()
#        for application_name in applications_list:
#            application_db = self.db[application_name]
#            surrogate_model_list = application_db.find({"document_type":{"$eq":"surrogate_model"}})
#            for surrogate_model in surrogate_model_list:
#                if surrogate_model["uid"] == surrogate_model_uid:
#                    gt = CreateGPTuneFromModelData(surrogate_model)
#                    (models, model_function) = gt.LoadSurrogateModel(model_data = surrogate_model)
#
#                    return (model_function)
#
#        return None

    def load_surrogate_models_by_user(self, user_email):
        surrogate_model_by_user = []

        for tuning_problem in self.db["tuning_problem_db"].find():
            collection_name = tuning_problem["unique_name"]
            application_db = self.db[collection_name]
            surrogate_model_list = application_db.find({"document_type":{"$eq":"surrogate_model"}})
            for surrogate_model in surrogate_model_list:
                if surrogate_model["user_info"]["user_email"] == user_email:
                    surrogate_model["tuning_problem_name"] = self.get_tuning_problem_simple_name(collection_name)
                    surrogate_model["tuning_problem_unique_name"] = collection_name
                    surrogate_model_by_user.append(surrogate_model)

        return surrogate_model_by_user

    def upload_surrogate_models(self, tuning_problem_unique_name, machine_unique_name, json_data, user_info, accessibility):
        collection_name = tuning_problem_unique_name
        collist = self.db.list_collection_names()
        if not collection_name in collist:
            print (collection_name + " is not exist in the database; create one.")
        collection = self.db[collection_name]

        num_added_surrogate_models = 0
        if "surrogate_model" in json_data:
            surrogate_model_list = json_data["surrogate_model"]
            for surrogate_model in surrogate_model_list:
                surrogate_model["document_type"] = "surrogate_model"
                surrogate_model["user_info"] = user_info
                surrogate_model["accessibility"] = accessibility
                if (collection.count_documents({"uid": {"$eq":surrogate_model["uid"]}}) == 0):
                    collection.insert_one(surrogate_model)
                    num_added_surrogate_models += 1
                else:
                    print ("surrogate_model: " + surrogate_model["uid"] + " already exist")
        if "model_data" in json_data:
            surrogate_model_list = json_data["model_data"]
            for surrogate_model in surrogate_model_list:
                surrogate_model["document_type"] = "surrogate_model"
                surrogate_model["user_info"] = user_info
                surrogate_model["accessibility"] = accessibility
                if (collection.count_documents({"uid": {"$eq":surrogate_model["uid"]}}) == 0):
                    collection.insert_one(surrogate_model)
                    num_added_surrogate_models += 1
                else:
                    print ("surrogate_model: " + surrogate_model["uid"] + " already exist")

        return num_added_surrogate_models

    def delete_perf_data_by_uid(self, tuning_problem_unique_name, entry_uid):
        application_db = self.db[tuning_problem_unique_name]
        application_db.delete_one({"uid": entry_uid})

        return None

    def update_entry_accessibility(self, tuning_problem_unique_name, entry_uid, accessibility):
        application_db = self.db[tuning_problem_unique_name]
        application_db.update_one({"uid": entry_uid}, {"$set": {"accessibility":accessibility}})

        return None

    def add_machine_info(self, machine_name, machine_info, user_info):
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

        machine_document["machine_name"] = machine_name
        machine_document["unique_name"] = (machine_name+"_"+machine_document["uid"]).replace("-","_")

        machine_db.insert_one(machine_document)

        return None

    def load_all_machine_info(self, **kwargs):
        machine_info_list = []

        for machine_info in self.db["machine_db"].find():
            machine_info_list.append(machine_info)

        return machine_info_list

    def add_tuning_problem(self, tuning_problem_name, tuning_problem_info, user_info, **kwargs):
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

        unique_name = tuning_problem_name+"_"+tuning_problem_document["uid"]
        unique_name = unique_name.replace("-","_")

        tuning_problem_document["tuning_problem_name"] = tuning_problem_name
        tuning_problem_document["unique_name"] = unique_name

        tuning_problem_db.insert_one(tuning_problem_document)

        return None

    def add_tuning_problem_flexible(self, tuning_problem_name, tuning_problem_info, user_info, **kwargs):
        tuning_problem_db = self.db["flexible_tuning_problem_db"]

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

        unique_name = tuning_problem_name+"_"+tuning_problem_document["uid"]
        unique_name = unique_name.replace("-","_")

        tuning_problem_document["tuning_problem_name"] = tuning_problem_name
        tuning_problem_document["unique_name"] = unique_name

        tuning_problem_db.insert_one(tuning_problem_document)

        return None

    def load_all_tuning_problems(self, **kwargs):
        tuning_problem_list = []

        for tuning_problem in self.db["tuning_problem_db"].find():
            tuning_problem["tuning_problem_type"] = "regular"
            tuning_problem_list.append(tuning_problem)

        for tuning_problem in self.db["flexible_tuning_problem_db"].find():
            tuning_problem["tuning_problem_type"] = "flexible"
            tuning_problem_list.append(tuning_problem)

        return tuning_problem_list

    def load_all_regular_tuning_problems(self, **kwargs):
        tuning_problem_list = []

        for tuning_problem in self.db["tuning_problem_db"].find():
            tuning_problem["tuning_problem_type"] = "regular"
            tuning_problem_list.append(tuning_problem)

        return tuning_problem_list

    def load_all_flexible_tuning_problems(self, **kwargs):
        tuning_problem_list = []

        for tuning_problem in self.db["flexible_tuning_problem_db"].find():
            tuning_problem["tuning_problem_type"] = "flexible"
            tuning_problem_list.append(tuning_problem)

        return tuning_problem_list

    def load_tuning_problem_by_unique_name(self, tuning_problem_unique_name, **kwargs):

        tuning_problem_document = self.db["tuning_problem_db"].find({"unique_name":{"$eq":tuning_problem_unique_name}})

        return tuning_problem_document[0]

    def load_tuning_problems_per_category(self, **kwargs):
        tuning_problems_avail_per_category = {}

        for tuning_problem in self.db["tuning_problem_db"].find():
            for category in tuning_problem["tuning_problem_info"]["category"]:
                category_name = category["category_name"]

                if category_name not in tuning_problems_avail_per_category:
                    tuning_problems_avail_per_category[category_name] = []

                tuning_problems_avail_per_category[category_name].append({
                    "tuning_problem_name": tuning_problem["tuning_problem_name"],
                    "user_info": tuning_problem["user_info"],
                    "update_time": tuning_problem["update_time"],
                    "unique_name": tuning_problem["unique_name"]
                    })

        return tuning_problems_avail_per_category

    def load_all_analytical_models(self, user_email, **kwargs):
        db = self.db["analytical_model_db"]

        analytical_model_list = []

        for document in self.db['analytical_model_db'].find():
            if 'accessibility' in document:
                if document['user_info']['user_email'] == user_email:
                    analytical_model_list.append(document)
                elif document['accessibility']['type'] == 'public':
                    analytical_model_list.append(document)
                elif document['accessibility']['type'] == 'registered':
                    if user_email != "":
                        analytical_model_list.append(document)
                elif document['accessibility']['type'] == 'private':
                    if document['user_info']['user_email'] == user_email:
                        analytical_model_list.append(document)
                elif document['accessibility']['type'] == 'group':
                    if user_email in document['accessibility']['group']:
                        analytical_model_list.append(document)

        return analytical_model_list

    def upload_analytical_model(self, model_name, model_data, user_info, accessibility, **kwargs):
        try:
            db = self.db["analytical_model_db"]

            document = {}
            document["model_name"] = model_name
            document["model_data"] = model_data
            document["user_info"] = user_info
            document["accessibility"] = accessibility

            import uuid
            document["uid"] = str(uuid.uuid1())

            unique_name = model_name+"_"+document["uid"]
            unique_name = unique_name.replace("-","_")

            document["unique_name"] = unique_name

            import time
            now = time.localtime()

            document["update_time"] = {
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

            document["upload_time"] = {
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

            db.insert_one(document)

            return True
        except:
            return False

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
