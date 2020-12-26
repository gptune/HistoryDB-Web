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

if __name__ == "__main__":
    historydb = HistoryDB()
    print (historydb.load_func_eval("PDGEQRF"))
