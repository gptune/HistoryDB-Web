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

class HistoryDB(dict):

    def __init__(self, **kwargs):
        self.init_value = 0
        self.json_path = "../json"

    def load_func_eval(self, application, **kwargs):
        application_path = self.json_path + "/" + application + ".json"
        print (application_path)
        with open(application_path) as f_in:
            json_data = json.loads(f_in.read())
            func_eval_data = json_data["func_eval"]
            return (func_eval_data)

    def get_applications_avail(self, **kwargs):
        applications_avail = []

        for application_file in os.listdir(self.json_path):
            applications_avail.append(application_file.split('.')[0])
            #application_path = self.json_path + "/" + application_file
            #print (application_path)
            #with open(application_path) as f_in:
            #    json_data = json.loads(f_in.read())
            #    func_eval_data = json_data["func_eval"]
            #    perf_data[application_file.split('.')[0]] = func_eval_data

        return applications_avail

    def get_machine_deps_avail(self, **kwargs):
        machine_deps_avail = {}

        for application_file in os.listdir(self.json_path):
            application_path = self.json_path + "/" + application_file
            with open(application_path) as f_in:
                application_name = application_file.split('.')[0]
                machine_deps_avail_givenapp = []
                machine_deps_avail_givenapp_str = []

                json_data = json.loads(f_in.read())
                func_eval_data = json_data["func_eval"]
                for func_eval in func_eval_data:
                    machine_deps = func_eval["machine_deps"]
                    machine_deps_str = str(func_eval["machine_deps"])
                    if machine_deps_str not in machine_deps_avail_givenapp_str:
                        machine_deps_avail_givenapp.append(machine_deps)
                        machine_deps_avail_givenapp_str.append(machine_deps_str)

                #print (machine_deps_avail_givenapp)
                #print (application_name)
                machine_deps_avail[application_name] = machine_deps_avail_givenapp

        print (machine_deps_avail)

        return machine_deps_avail

    def get_software_deps_avail(self, **kwargs):
        software_deps_avail = {}

        for application_file in os.listdir(self.json_path):
            application_path = self.json_path + "/" + application_file
            with open(application_path) as f_in:
                application_name = application_file.split('.')[0]
                software_deps_avail_givenapp = []
                software_deps_avail_givenapp_str = []

                json_data = json.loads(f_in.read())
                func_eval_data = json_data["func_eval"]
                for func_eval in func_eval_data:
                    #software_deps = func_eval["software_deps"]
                    software_deps = func_eval["compile_deps"]
                    software_deps_str = str(func_eval["compile_deps"])
                    if software_deps_str not in software_deps_avail_givenapp_str:
                        software_deps_avail_givenapp.append(software_deps)
                        software_deps_avail_givenapp_str.append(software_deps_str)

                print (software_deps_avail_givenapp)

                software_deps_avail[application_name] = software_deps_avail_givenapp

        return software_deps_avail

    def get_users_avail(self, **kwargs):
        users_avail = {}

        for application_file in os.listdir(self.json_path):
            application_path = self.json_path + "/" + application_file
            with open(application_path) as f_in:
                application_name = application_file.split('.')[0]
                users_avail_givenapp = []

                json_data = json.loads(f_in.read())
                func_eval_data = json_data["func_eval"]
                for func_eval in func_eval_data:
                    try:
                        users = func_eval["user"]
                    except:
                        users = "placeholder"
                    if users not in users_avail_givenapp:
                        users_avail_givenapp.append(users)

                print (users_avail_givenapp)

                users_avail[application_name] = users_avail_givenapp

        return users_avail

    def load_func_eval(self,
            application_name,
            machine_deps_list,
            software_deps_list,
            **kwargs):
        func_eval_filtered = []

        machine_deps_str_list = []
        software_deps_str_list = []
        for i in range(len(machine_deps_list)):
            machine_deps_str_list.append(str(machine_deps_list[i]))
        for i in range(len(software_deps_list)):
            software_deps_str_list.append(str(software_deps_list[i]))

        with open(self.json_path+"/"+application_name+".json") as f_in:
            json_data = json.loads(f_in.read())
            func_eval_list = json_data["func_eval"]
            for func_eval in func_eval_list:
                machine_deps_str = str(func_eval["machine_deps"])
                software_deps_str = str(func_eval["compile_deps"])
                if (machine_deps_str in machine_deps_str_list):
                   if (software_deps_str in software_deps_str_list):
                        func_eval_filtered.append(func_eval)

        return func_eval_filtered

if __name__ == "__main__":
    historydb = HistoryDB()
    print (historydb.load_func_eval("PDGEQRF"))
