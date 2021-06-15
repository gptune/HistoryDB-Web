from django.shortcuts import render

# Create your views here.
from django.views import View
from django.http import HttpResponse
from django.http import JsonResponse

from django.views.generic import TemplateView

from datetime import datetime
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.contrib.auth.models import User
from django.contrib import auth

from dbmanager import HistoryDB_MongoDB

from django.conf import settings
#from django.contrib import messages

import requests
import os
import json
import ast
import re

from gptune import *

class Dashboard(TemplateView):

    def get(self, request, **kwargs):
        print ("======== Dashboard GET ========")

        historydb = HistoryDB_MongoDB()

        tuning_problems_avail = historydb.load_all_tuning_problems()
        machine_configurations_avail = historydb.get_machine_configurations_avail()
        software_configurations_avail = historydb.get_software_configurations_avail()
        user_configurations_avail = historydb.get_user_configurations_avail()

        print ("machine_configurations_avail: ", machine_configurations_avail)
        print ("software_configurations_avail: ", software_configurations_avail)
        print ("user_configurations_avail: ", user_configurations_avail)

        user_email = ""
        if request.user.is_authenticated:
            user_email = request.user.email

        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")

        if tuning_problem_unique_name != "":
            machine_configurations_list = ast.literal_eval(request.GET.get("machine_configurations_list", ""))
            software_configurations_list = ast.literal_eval(request.GET.get("software_configurations_list", ""))
            user_configurations_list = ast.literal_eval(request.GET.get("user_configurations_list", ""))

            historydb = HistoryDB_MongoDB()

            search_options = ast.literal_eval(request.GET.get("search_options", ""))

            if "func_eval" in search_options:
                func_eval_list = historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                        machine_configurations_list = machine_configurations_list,
                        software_configurations_list = software_configurations_list,
                        user_configurations_list = user_configurations_list,
                        user_email = user_email)
                num_func_eval = len(func_eval_list)
                print ("num_func_eval: ", num_func_eval)
                num_evals_per_page = 15
                if (num_func_eval%num_evals_per_page) == 0:
                    num_pages_func_eval = int(num_func_eval/num_evals_per_page)
                else:
                    num_pages_func_eval = int(num_func_eval/num_evals_per_page)+1
                print ("num_pages_func_eval: ", num_pages_func_eval)
                if (num_pages_func_eval == 0):
                    num_pages_func_eval = 1
                current_page_func_eval = int(request.GET.get("current_page_func_eval", 0))
                print ("current_page_func_eval: ", current_page_func_eval)
                start_index = (current_page_func_eval)*num_evals_per_page
                end_index = (current_page_func_eval+1)*num_evals_per_page
                if end_index > num_func_eval:
                    end_index = num_func_eval
                func_eval_web = func_eval_list[start_index:end_index]
                for i in range(len(func_eval_web)):
                    func_eval_web[i]["id"] = start_index+i
                print (func_eval_web)
            else:
                func_eval_web = []
                num_func_eval = 0
                num_pages_func_eval = 0
                current_page_func_eval = 0

            if "surrogate_model" in search_options:
                surrogate_model = historydb.load_surrogate_models_filtered(
                        tuning_problem_unique_name = tuning_problem_unique_name,
                        machine_configurations_list = machine_configurations_list,
                        software_configurations_list = software_configurations_list,
                        user_configurations_list = user_configurations_list,
                        user_email = user_email)
                num_surrogate_models = len(surrogate_model)
                num_surrogate_model_per_page = 15
                if (num_surrogate_models %num_surrogate_model_per_page) == 0:
                    num_pages_surrogate_models = int(num_surrogate_models/num_surrogate_model_per_page)
                else:
                    num_pages_surrogate_models = int(num_surrogate_models/num_surrogate_model_per_page)+1
                if (num_pages_surrogate_models == 0):
                    num_pages_surrogate_models = 1
                current_page_surrogate_models = int(request.GET.get("current_page_surrogate_models", 0))
                start_index_surrogate_model = (current_page_surrogate_models)*num_surrogate_model_per_page
                end_index_surrogate_model = (current_page_surrogate_models+1)*num_surrogate_model_per_page
                if end_index_surrogate_model > num_surrogate_models:
                    end_index_surrogate_model = num_surrogate_models
                surrogate_model_web = surrogate_model[start_index_surrogate_model:end_index_surrogate_model]
                for i in range(len(surrogate_model_web)):
                    surrogate_model_web[i]["id"] = start_index_surrogate_model+i
                    surrogate_model_web[i]["num_func_eval"] = len(surrogate_model_web[i]["function_evaluations"])
                    surrogate_model_web[i]["num_task_parameters"] = len(surrogate_model_web[i]["task_parameters"])
                    surrogate_model_web[i]["num_func_eval_per_task"] = \
                            int(len(surrogate_model_web[i]["function_evaluations"])/len(surrogate_model_web[i]["task_parameters"]))
            else:
                surrogate_model_web = []
                num_surrogate_models = 0
                num_pages_surrogate_models = 0
                current_page_surrogate_models = 0

            context = {
                    "tuning_problems_avail" : tuning_problems_avail,
                    "machine_configurations_avail" : machine_configurations_avail,
                    "software_configurations_avail" : software_configurations_avail,
                    "user_configurations_avail" : user_configurations_avail,
                    "tuning_problem_unique_name" : tuning_problem_unique_name,
                    "func_eval_list" : func_eval_web,
                    "num_func_eval" : num_func_eval,
                    "num_pages_func_eval" : range(num_pages_func_eval),
                    "current_page_func_eval" : current_page_func_eval,
                    "surrogate_model_list" : surrogate_model_web,
                    "num_surrogate_models" : num_surrogate_models,
                    "num_pages_surrogate_models" : range(num_pages_surrogate_models),
                    "current_page_surrogate_models" : current_page_surrogate_models,
                    "machine_configurations_list" : json.dumps(machine_configurations_list),
                    "software_configurations_list" : json.dumps(software_configurations_list),
                    "user_configurations_list" : json.dumps(user_configurations_list),
                    "search_options" : json.dumps(search_options)
                    }

            return render(request, 'repo/dashboard.html', context)

        else:
            historydb = HistoryDB_MongoDB()

            func_eval_web = []
            num_func_eval = 0
            num_pages_func_eval = 0
            current_page_func_eval = 0

            surrogate_model_web = []
            num_surrogate_models = 0
            num_pages_surrogate_models = 0
            current_page_surrogate_models = 0

            context = {
                    "tuning_problems_avail" : tuning_problems_avail,
                    "machine_configurations_avail" : machine_configurations_avail,
                    "software_configurations_avail" : software_configurations_avail,
                    "user_configurations_avail" : user_configurations_avail,
                    "tuning_problem_unique_name" : tuning_problem_unique_name,
                    "func_eval_list" : func_eval_web,
                    "num_func_eval" : num_func_eval,
                    "num_pages_func_eval" : range(num_pages_func_eval),
                    "current_page_func_eval" : current_page_func_eval,
                    "surrogate_model_list" : surrogate_model_web,
                    "num_surrogate_models" : num_surrogate_models,
                    "num_pages_surrogate_models" : range(num_pages_surrogate_models),
                    "current_page_surrogate_models" : current_page_surrogate_models,
                    "machine_configurations_list" : json.dumps(machine_configurations_avail),
                    "software_configurations_list" : json.dumps(software_configurations_avail),
                    "user_configurations_list" : json.dumps(user_configurations_avail),
                    "search_options" : json.dumps({})
                    }

            return render(request, 'repo/dashboard.html', context)

    def post(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()

        tuning_problems_avail = historydb.load_all_tuning_problems()
        machine_configurations_avail = historydb.get_machine_configurations_avail()
        software_configurations_avail = historydb.get_software_configurations_avail()
        user_configurations_avail = historydb.get_user_configurations_avail()

        tuning_problem_unique_name = request.POST["tuning_problem"]
        print ("tuning_problem_unique_name: ", tuning_problem_unique_name)

        machine_configurations_list = []
        post_values = request.POST.getlist('machine_configurations_list')
        for i in range(len(post_values)):
            machine_configurations_list.append(json.loads(post_values[i]))
        print ("machine_configurations_list")
        print (machine_configurations_list)

        software_configurations_list = []
        post_values = request.POST.getlist('software_configurations_list')
        for i in range(len(post_values)):
            software_configurations_list.append(json.loads(post_values[i]))
        print ("software_configurations_list")
        print (software_configurations_list)

        user_configurations_list = []
        post_values = request.POST.getlist('user_configurations_list')
        for i in range(len(post_values)):
            user_configurations_list.append(json.loads(post_values[i]))
        print ("user_configurations_list")
        print (user_configurations_list)

        search_options = request.POST.getlist("search_options")
        print ("search_options")
        print (search_options)

        user_email = ""
        if request.user.is_authenticated:
            user_email = request.user.email

        if "func_eval" in search_options:
            func_eval_list = historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    user_configurations_list = user_configurations_list,
                    user_email = user_email)
            num_func_eval = len(func_eval_list)
            num_evals_per_page = 15
            if (num_func_eval%num_evals_per_page) == 0:
                num_pages_func_eval = int(num_func_eval/num_evals_per_page)
            else:
                num_pages_func_eval = int(num_func_eval/num_evals_per_page)+1
            if (num_pages_func_eval == 0):
                num_pages_func_eval = 1
            current_page_func_eval = 0
            start_index = (current_page_func_eval)*num_evals_per_page
            end_index = (current_page_func_eval+1)*num_evals_per_page
            if end_index > num_func_eval:
                end_index = num_func_eval
            func_eval_web = func_eval_list[start_index:end_index]

            for i in range(len(func_eval_web)):
                func_eval_web[i]["id"] = start_index+i
        else:
            func_eval_web = []
            num_func_eval = 0
            num_pages_func_eval = 0
            current_page_func_eval = 0

        if "surrogate_model" in search_options:
            surrogate_model = historydb.load_surrogate_models_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    user_configurations_list = user_configurations_list,
                    user_email = user_email)
            num_surrogate_models = len(surrogate_model)
            num_surrogate_model_per_page = 15
            if (num_surrogate_models %num_surrogate_model_per_page) == 0:
                num_pages_surrogate_models = int(num_surrogate_models/num_surrogate_model_per_page)
            else:
                num_pages_surrogate_models = int(num_surrogate_models/num_surrogate_model_per_page)+1
            if (num_pages_surrogate_models == 0):
                num_pages_surrogate_models = 1
            current_page_surrogate_models = 0
            start_index_surrogate_model = (current_page_surrogate_models)*num_surrogate_model_per_page
            end_index_surrogate_model = (current_page_surrogate_models+1)*num_surrogate_model_per_page
            if end_index_surrogate_model > num_surrogate_models:
                end_index_surrogate_model = num_surrogate_models
            surrogate_model_web = surrogate_model[start_index_surrogate_model:end_index_surrogate_model]
            for i in range(len(surrogate_model_web)):
                surrogate_model_web[i]["id"] = start_index_surrogate_model+i
                surrogate_model_web[i]["num_func_eval"] = len(surrogate_model_web[i]["function_evaluations"])
                surrogate_model_web[i]["num_task_parameters"] = len(surrogate_model_web[i]["task_parameters"])
                surrogate_model_web[i]["num_func_eval_per_task"] = \
                        int(len(surrogate_model_web[i]["function_evaluations"])/len(surrogate_model_web[i]["task_parameters"]))
        else:
            surrogate_model_web = []
            num_surrogate_models = 0
            num_pages_surrogate_models = 0
            current_page_surrogate_models = 0


        print ("func_eval_list: ", func_eval_web)

        context = {
                "tuning_problem_unique_name" : tuning_problem_unique_name,
                "tuning_problems_avail" : tuning_problems_avail,
                "machine_configurations_avail" : machine_configurations_avail,
                "software_configurations_avail" : software_configurations_avail,
                "user_configurations_avail" : user_configurations_avail,
                "func_eval_list" : func_eval_web,
                "num_func_eval" : num_func_eval,
                "num_pages_func_eval" : range(num_pages_func_eval),
                "current_page_func_eval" : current_page_func_eval,
                "surrogate_model_list" : surrogate_model_web,
                "num_surrogate_models" : num_surrogate_models,
                "num_pages_surrogate_models" : range(num_pages_surrogate_models),
                "current_page_surrogate_models" : current_page_surrogate_models,
                "machine_configurations_list" : json.dumps(machine_configurations_list),
                "software_configurations_list" : json.dumps(software_configurations_list),
                "user_configurations_list" : json.dumps(user_configurations_list),
                "search_options" : json.dumps(search_options)
                }

        return render(request, 'repo/dashboard.html', context)

class UserDashboard(TemplateView):

    def get(self, request, **kwargs):
        print ("======== User Dashboard GET ========")

        historydb = HistoryDB_MongoDB()

        user_email = request.user.email

        func_eval_list = historydb.load_func_eval_by_user(user_email = user_email)
        num_func_eval = len(func_eval_list)
        print ("num_func_eval: ", num_func_eval)
        num_evals_per_page = 30
        if (num_func_eval%num_evals_per_page) == 0:
            num_pages_func_eval = int(num_func_eval/num_evals_per_page)
        else:
            num_pages_func_eval = int(num_func_eval/num_evals_per_page)+1
        if (num_pages_func_eval == 0):
            num_pages_func_eval = 1
        current_page_func_eval = int(request.GET.get("current_page_func_eval", 0))
        print ("current_page_func_eval: ", current_page_func_eval)
        start_index = (current_page_func_eval)*num_evals_per_page
        end_index = (current_page_func_eval+1)*num_evals_per_page
        if end_index > num_func_eval:
            end_index = num_func_eval
        func_eval_web = func_eval_list[start_index:end_index]
        for i in range(len(func_eval_web)):
            func_eval_web[i]["id"] = start_index+i
        print (func_eval_web)

        surrogate_models = historydb.load_surrogate_models_by_user(user_email = user_email)
        num_surrogate_models = len(surrogate_models)
        num_surrogate_model_per_page = 30
        if (num_surrogate_models %num_surrogate_model_per_page) == 0:
            num_pages_surrogate_models = num_surrogate_models/num_surrogate_model_per_page
        else:
            num_pages_surrogate_models = int(num_surrogate_models/num_surrogate_model_per_page)+1
        if (num_pages_surrogate_models == 0):
            num_pages_surrogate_models = 1
        current_page_surrogate_models = int(request.GET.get("current_page_surrogate_models", 0))
        start_index_surrogate_model = (current_page_surrogate_models)*num_surrogate_model_per_page
        end_index_surrogate_model = (current_page_surrogate_models+1)*num_surrogate_model_per_page
        if end_index_surrogate_model > num_surrogate_models:
            end_index_surrogate_model = num_surrogate_models
        surrogate_model_web = surrogate_models[start_index_surrogate_model:end_index_surrogate_model]
        for i in range(len(surrogate_model_web)):
            surrogate_model_web[i]["id"] = start_index_surrogate_model+i
            surrogate_model_web[i]["num_func_eval"] = len(surrogate_model_web[i]["function_evaluations"])
            surrogate_model_web[i]["num_task_parameters"] = len(surrogate_model_web[i]["task_parameters"])
            surrogate_model_web[i]["num_func_eval_per_task"] = \
                    int(len(surrogate_model_web[i]["function_evaluations"])/len(surrogate_model_web[i]["task_parameters"]))

        context = {
                "func_eval_list" : func_eval_web,
                "num_func_eval" : num_func_eval,
                "num_pages_func_eval" : range(num_pages_func_eval),
                "current_page_func_eval" : current_page_func_eval,
                "surrogate_model_list" : surrogate_model_web,
                "num_surrogate_models" : num_surrogate_models,
                "num_pages_surrogate_models" : range(num_pages_surrogate_models),
                "current_page_surrogate_models" : current_page_surrogate_models,
                }

        return render(request, 'repo/user-dashboard.html', context)

    def post(self, request, **kwargs):
        context = {}

        return render(request, 'repo/user-dashboard.html', context)

class SurrogateModel(TemplateView):

    def get(self, request, **kwargs):
        print ("======== Surrogate Model Dashboard ========")
        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")
        surrogate_model_uid = request.GET.get("surrogate_model_uid", "")
        print ("tuning_problem_unique_name: ", tuning_problem_unique_name)
        print ("Surrogate Model UID: ", surrogate_model_uid)

        historydb = HistoryDB_MongoDB()
        tuning_problem = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
        surrogate_model = historydb.load_surrogate_model_by_uid(surrogate_model_uid)
        print ("tuning_problem: ", tuning_problem)

        print ("SURROGATE_MODEL")
        print (surrogate_model)

        model_data = {}

        model_data["surrogate_model_uid"] = surrogate_model_uid

        model_data["tuning_problem_name"] = tuning_problem["tuning_problem_name"]
        model_data["tuning_problem_unique_name"] = tuning_problem["unique_name"]
        model_data["hyperparameters"] = surrogate_model["hyperparameters"]
        model_data["model_stats"] = surrogate_model["model_stats"]
        model_data["model_stats"]["num_samples"] = len(surrogate_model["function_evaluations"])

        model_data["function_evaluations"] = []
        func_eval_id = 1
        for func_eval_uid in surrogate_model["function_evaluations"]:
            func_eval_document = historydb.load_func_eval_by_uid(func_eval_uid)
            func_eval_document["id"] = func_eval_id
            func_eval_id += 1
            model_data["function_evaluations"].append(func_eval_document)

        model_data["task_parameters"] = []
        for i in range(len(surrogate_model["input_space"])):
            task_space = surrogate_model["input_space"][i]

            task_parameter = {}
            task_parameter["name"] = task_space["name"]
            task_parameter["type"] = task_space["type"]
            task_parameter["lower_bound"] = task_space["lower_bound"]
            task_parameter["upper_bound"] = task_space["upper_bound"]
            for task_info in tuning_problem["tuning_problem_info"]["task_info"]:
                if task_info["task_name"] == task_parameter["name"]:
                    task_parameter["description"] = task_info["task_description"]
            task_parameter["options"] = []
            for j in range(len(surrogate_model["task_parameters"])):
                task_parameter["options"].append(surrogate_model["task_parameters"][j][i])
            task_parameter["value"] = task_parameter["options"][0]

            model_data["task_parameters"].append(task_parameter)

        model_data["tuning_parameters"] = []
        for parameter_space in surrogate_model["parameter_space"]:
            tuning_parameter = {}
            tuning_parameter["name"] = parameter_space["name"]
            tuning_parameter["type"] = parameter_space["type"]
            tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
            tuning_parameter["upper_bound"] = parameter_space["upper_bound"]

            for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                if parameter_info["parameter_name"] == tuning_parameter["name"]:
                    tuning_parameter["description"] = parameter_info["parameter_description"]
            tuning_parameter["value"] = tuning_parameter["lower_bound"]

            model_data["tuning_parameters"].append(tuning_parameter)

        model_data["output_parameters"] = []
        for output_space in surrogate_model["output_space"]:
            output_parameter = {}
            output_parameter["name"] = output_space["name"]
            output_parameter["type"] = output_space["type"]
            output_parameter["lower_bound"] = output_space["lower_bound"]
            output_parameter["upper_bound"] = output_space["upper_bound"]

            for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                if output_info["output_name"] == output_parameter["name"]:
                    output_parameter["description"] = output_info["output_description"]
            output_parameter["result"] = "-"

            model_data["output_parameters"].append(output_parameter)

        sobol_analysis = {}
        sobol_analysis["task_parameters"] = []
        for i in range(len(surrogate_model["task_parameters"])):
            task_parameter = {}
            for j in range(len(surrogate_model["input_space"])):
                #task_parameter["name"] = surrogate_model["input_space"][j]["name"]
                #task_parameter["value"] = surrogate_model["task_parameters"][i][j]
                task_parameter[surrogate_model["input_space"][j]["name"]] = surrogate_model["task_parameters"][i][j]
            sobol_analysis["task_parameters"].append(task_parameter)
        sobol_analysis["num_samples"] = 1000

#        model_data["input_space"] = surrogate_model["input_space"]
#        #model_data["task_parameters"] = surrogate_model["task_parameters"]
#        print ("model task parameters: ", model_data["task_parameters"])
#        for input_parameter in model_data["input_space"]:
#            task_parameter_name = input_parameter["name"]
#            print (task_parameter_name)
#            print (input_parameter)
#            print (tuning_problem["tuning_problem_info"]["task_info"])
#
#            for task_info in tuning_problem["tuning_problem_info"]["task_info"]:
#                if task_info["task_name"] == task_parameter_name:
#                    input_parameter["description"] = "task_desc: " + task_info["task_description"]
#
#        model_data["parameter_space"] = surrogate_model["parameter_space"]
#        for tuning_parameter in model_data["parameter_space"]:
#            tuning_parameter_name = tuning_parameter["name"]
#            print (tuning_problem["tuning_problem_info"]["parameter_info"])
#
#            for tuning_parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
#                if tuning_parameter_info["parameter_name"] == tuning_parameter_name:
#                    input_parameter["description"] = "parameter_desc: " + tuning_parameter_info["parameter_description"]
#
#        model_data["output_space"] = surrogate_model["output_space"]

        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(model_data)
        pp.pprint(sobol_analysis)
        print ("MODEL_DATA: ", model_data)
        #pp.pprint("MODEL_DATA: ", model_data)

        context = {
                "model_data" : model_data,
                "sobol_analysis" : sobol_analysis
                }

        return render(request, 'repo/surrogate-model.html', context)

class ModelPrediction(TemplateView):

    def get(self, request, **kwargs):
        print ("======== Surrogate Model Dashboard ========")
        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")
        surrogate_model_uid = request.GET.get("surrogate_model_uid", "")
        print ("tuning_problem_unique_name: ", tuning_problem_unique_name)
        print ("Surrogate Model UID: ", surrogate_model_uid)

        historydb = HistoryDB_MongoDB()
        tuning_problem = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
        surrogate_model = historydb.load_surrogate_model_by_uid(surrogate_model_uid)
        print ("tuning_problem: ", tuning_problem)

        print ("SURROGATE_MODEL")
        print (surrogate_model)

        model_data = {}

        model_data["surrogate_model_uid"] = surrogate_model_uid

        model_data["tuning_problem_name"] = tuning_problem["tuning_problem_name"]
        model_data["tuning_problem_unique_name"] = tuning_problem["unique_name"]
        model_data["hyperparameters"] = surrogate_model["hyperparameters"]
        model_data["model_stats"] = surrogate_model["model_stats"]
        model_data["model_stats"]["num_samples"] = len(surrogate_model["function_evaluations"])

        model_data["function_evaluations"] = []
        func_eval_id = 1
        for func_eval_uid in surrogate_model["function_evaluations"]:
            func_eval_document = historydb.load_func_eval_by_uid(func_eval_uid)
            func_eval_document["id"] = func_eval_id
            func_eval_id += 1
            model_data["function_evaluations"].append(func_eval_document)

        model_data["task_parameters"] = []
        for i in range(len(surrogate_model["input_space"])):
            task_space = surrogate_model["input_space"][i]

            task_parameter = {}
            task_parameter["name"] = task_space["name"]
            task_parameter["type"] = task_space["type"]
            task_parameter["lower_bound"] = task_space["lower_bound"]
            task_parameter["upper_bound"] = task_space["upper_bound"]
            for task_info in tuning_problem["tuning_problem_info"]["task_info"]:
                if task_info["task_name"] == task_parameter["name"]:
                    task_parameter["description"] = task_info["task_description"]
            task_parameter["options"] = []
            for j in range(len(surrogate_model["task_parameters"])):
                task_parameter["options"].append(surrogate_model["task_parameters"][j][i])
            task_parameter["value"] = task_parameter["options"][0]

            model_data["task_parameters"].append(task_parameter)

        model_data["tuning_parameters"] = []
        for parameter_space in surrogate_model["parameter_space"]:
            tuning_parameter = {}
            tuning_parameter["name"] = parameter_space["name"]
            tuning_parameter["type"] = parameter_space["type"]
            tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
            tuning_parameter["upper_bound"] = parameter_space["upper_bound"]

            for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                if parameter_info["parameter_name"] == tuning_parameter["name"]:
                    tuning_parameter["description"] = parameter_info["parameter_description"]
            tuning_parameter["value"] = tuning_parameter["lower_bound"]

            model_data["tuning_parameters"].append(tuning_parameter)

        model_data["output_parameters"] = []
        for output_space in surrogate_model["output_space"]:
            output_parameter = {}
            output_parameter["name"] = output_space["name"]
            output_parameter["type"] = output_space["type"]
            output_parameter["lower_bound"] = output_space["lower_bound"]
            output_parameter["upper_bound"] = output_space["upper_bound"]

            for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                if output_info["output_name"] == output_parameter["name"]:
                    output_parameter["description"] = output_info["output_description"]
            output_parameter["result"] = "-"

            model_data["output_parameters"].append(output_parameter)

        sobol_analysis = {}
        sobol_analysis["task_parameters"] = []
        for i in range(len(surrogate_model["task_parameters"])):
            task_parameter = {}
            for j in range(len(surrogate_model["input_space"])):
                #task_parameter["name"] = surrogate_model["input_space"][j]["name"]
                #task_parameter["value"] = surrogate_model["task_parameters"][i][j]
                task_parameter[surrogate_model["input_space"][j]["name"]] = surrogate_model["task_parameters"][i][j]
            sobol_analysis["task_parameters"].append(task_parameter)
        sobol_analysis["num_samples"] = 1000

        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(model_data)
        pp.pprint(sobol_analysis)
        print ("MODEL_DATA: ", model_data)
        #pp.pprint("MODEL_DATA: ", model_data)

        context = {
                "model_data" : model_data,
                "sobol_analysis" : sobol_analysis
                }

        return render(request, 'repo/surrogate-model.html', context)

    def post(self, request, **kwargs):
        context = {}

        surrogate_model_uid = request.POST["surrogate_model_uid"]
        task_parameter_names = request.POST.getlist('task_parameter_name')
        task_parameter_types = request.POST.getlist('task_parameter_type')
        task_parameters = request.POST.getlist('task_parameter')
        tuning_parameter_names = request.POST.getlist('tuning_parameter_name')
        tuning_parameter_types = request.POST.getlist('tuning_parameter_type')
        tuning_parameters = request.POST.getlist('tuning_parameter')
        #output_names = request.POST.getlist('output_name')
        output_name = request.POST['output_parameter_name']
        #output = request.POST.getlist('output')

        print ("surrogate_model_uid: ", surrogate_model_uid)
        print ("TASK parameter names: ", task_parameter_names)
        print ("TASK parameter types: ", task_parameter_types)
        print ("TASK parameters: ", task_parameters)
        print ("TUNING parameter names: ", tuning_parameter_names)
        print ("TUNING parameter types: ", tuning_parameter_types)
        print ("TUNING parameters: ", tuning_parameters)
        #print ("output: ", output_names)

        point = {}
        for i in range(len(task_parameter_names)):
            if task_parameter_types[i] == "int":
                point[task_parameter_names[i]] = int(task_parameters[i])
            elif task_parameter_types[i] == "float":
                point[task_parameter_names[i]] = float(task_parameters[i])
        for i in range(len(tuning_parameter_names)):
            if tuning_parameter_types[i] == "int":
                point[tuning_parameter_names[i]] = int(tuning_parameters[i])
            elif tuning_parameter_types[i] == "float":
                point[tuning_parameter_names[i]] = float(tuning_parameters[i])

        print ("MODEL POINT: ", point)

        historydb = HistoryDB_MongoDB()
        surrogate_model = historydb.load_surrogate_model_by_uid(surrogate_model_uid)
        #model_function = historydb.load_surrogate_model_function(surrogate_model)
        #output = model_function(point)

        tuning_problem_name = surrogate_model["tuning_problem_name"]
        os.system("rm -rf .gptune")
        os.system("mkdir -p .gptune")
        json_data = {}
        json_data["tuning_problem_name"] = tuning_problem_name
        with open(".gptune/meta.json", "w") as f_out:
            json.dump(json_data, f_out, indent=2)

        gt = CreateGPTuneFromModelData(surrogate_model)
        print (surrogate_model)
        print ("GPTune data: ", gt.data.P)

        func_eval_list = []
        for func_eval_uid in surrogate_model["function_evaluations"]:
            func_eval = historydb.load_func_eval_by_uid(func_eval_uid)
            del(func_eval["_id"])
            func_eval_list.append(func_eval)
        #print ("func_eval_list: ", func_eval_list)

        os.system("rm -rf gptune.db")
        os.system("mkdir -p gptune.db")
        json_data = {}
        json_data["func_eval"] = func_eval_list
        with open("gptune.db/"+tuning_problem_name+".json", "w") as f_out:
            json.dump(json_data, f_out, indent=2)

        (model, model_function) = gt.LoadSurrogateModel(model_data=surrogate_model)
        ret = model_function(point)
        print ("ret: ", ret)

        #surrogate_model["model_stats"]["num_samples"] = len(surrogate_model["function_evaluations"])

        #print ("SURROGATE_MODEL")
        #print (surrogate_model)

        #historydb = HistoryDB_MongoDB()
        tuning_problem_unique_name = request.POST["tuning_problem_unique_name"]
        tuning_problem = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
        surrogate_model = historydb.load_surrogate_model_by_uid(surrogate_model_uid)
        print ("tuning_problem: ", tuning_problem)

        print ("SURROGATE_MODEL")
        print (surrogate_model)

        model_data = {}

        model_data["surrogate_model_uid"] = surrogate_model_uid

        model_data["tuning_problem_name"] = tuning_problem["tuning_problem_name"]
        model_data["tuning_problem_unique_name"] = tuning_problem["unique_name"]
        model_data["hyperparameters"] = surrogate_model["hyperparameters"]
        model_data["model_stats"] = surrogate_model["model_stats"]
        model_data["model_stats"]["num_samples"] = len(surrogate_model["function_evaluations"])

        model_data["function_evaluations"] = []
        func_eval_id = 1
        for func_eval_uid in surrogate_model["function_evaluations"]:
            func_eval_document = historydb.load_func_eval_by_uid(func_eval_uid)
            func_eval_document["id"] = func_eval_id
            func_eval_id += 1
            model_data["function_evaluations"].append(func_eval_document)

        model_data["task_parameters"] = []
        for i in range(len(surrogate_model["input_space"])):
            task_space = surrogate_model["input_space"][i]

            task_parameter = {}
            task_parameter["name"] = task_space["name"]
            task_parameter["type"] = task_space["type"]
            task_parameter["lower_bound"] = task_space["lower_bound"]
            task_parameter["upper_bound"] = task_space["upper_bound"]
            for task_info in tuning_problem["tuning_problem_info"]["task_info"]:
                if task_info["task_name"] == task_parameter["name"]:
                    task_parameter["description"] = task_info["task_description"]
            task_parameter["options"] = []
            for j in range(len(surrogate_model["task_parameters"])):
                task_parameter["options"].append(surrogate_model["task_parameters"][j][i])
            task_parameter["value"] = task_parameters[i]

            model_data["task_parameters"].append(task_parameter)

        model_data["tuning_parameters"] = []
        for i in range(len(surrogate_model["parameter_space"])):
            parameter_space = surrogate_model["parameter_space"][i]
            tuning_parameter = {}
            tuning_parameter["name"] = parameter_space["name"]
            tuning_parameter["type"] = parameter_space["type"]
            tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
            tuning_parameter["upper_bound"] = parameter_space["upper_bound"]

            for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                if parameter_info["parameter_name"] == tuning_parameter["name"]:
                    tuning_parameter["description"] = parameter_info["parameter_description"]
            tuning_parameter["value"] = tuning_parameters[i]

            model_data["tuning_parameters"].append(tuning_parameter)

        model_data["output_parameters"] = []
        for output_space in surrogate_model["output_space"]:
            output_parameter = {}
            output_parameter["name"] = output_space["name"]
            output_parameter["type"] = output_space["type"]
            output_parameter["lower_bound"] = output_space["lower_bound"]
            output_parameter["upper_bound"] = output_space["upper_bound"]

            for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                if output_info["output_name"] == output_parameter["name"]:
                    output_parameter["description"] = output_info["output_description"]

            #output_parameter["result"] = ret[output_parameter["name"]]
            output_parameter["result"] = round(ret[output_parameter["name"]][0][0],3)
            output_parameter["result_std"] = round(math.sqrt(ret[output_parameter["name"]+"_var"][0][0]),3)

            model_data["output_parameters"].append(output_parameter)
            #model_data["output_parameters"].append(output_parameter)

        sobol_analysis = {}
        sobol_analysis["task_parameters"] = []
        for i in range(len(surrogate_model["task_parameters"])):
            task_parameter = {}
            for j in range(len(surrogate_model["input_space"])):
                #task_parameter["name"] = surrogate_model["input_space"][j]["name"]
                #task_parameter["value"] = surrogate_model["task_parameters"][i][j]
                task_parameter[surrogate_model["input_space"][j]["name"]] = surrogate_model["task_parameters"][i][j]
            sobol_analysis["task_parameters"].append(task_parameter)
        sobol_analysis["num_samples"] = 1000

#        sobol_analysis = {}
#        sobol_analysis["task_parameters"] = []
#        for i in range(len(surrogate_model["task_parameters"])):
#            task_parameter = {}
#            for j in range(len(surrogate_model["input_space"])):
#                #task_parameter["name"] = surrogate_model["input_space"][j]["name"]
#                #task_parameter["value"] = surrogate_model["task_parameters"][i][j]
#                task_parameter[surrogate_model["input_space"][j]["name"]] = surrogate_model["task_parameters"][i][j]
#            sobol_analysis["task_parameters"].append(task_parameter)
#        sobol_analysis["num_samples"] = 1000
#
#        si = SensitivityAnalysis(model_data=surrogate_model, task_parameters=surrogate_model["task_parameters"][0], num_samples=1000)
#        print (si)

        context = {
                "model_data" : model_data,
                "sobol_analysis" : sobol_analysis
                }

        return render(request, 'repo/surrogate-model.html', context)

class SobolAnalysis(TemplateView):

    def get(self, request, **kwargs):
        print ("======== Surrogate Model Dashboard ========")
        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")
        surrogate_model_uid = request.GET.get("surrogate_model_uid", "")
        print ("tuning_problem_unique_name: ", tuning_problem_unique_name)
        print ("Surrogate Model UID: ", surrogate_model_uid)

        historydb = HistoryDB_MongoDB()
        tuning_problem = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
        surrogate_model = historydb.load_surrogate_model_by_uid(surrogate_model_uid)
        print ("tuning_problem: ", tuning_problem)

        print ("SURROGATE_MODEL")
        print (surrogate_model)

        model_data = {}

        model_data["surrogate_model_uid"] = surrogate_model_uid

        model_data["tuning_problem_name"] = tuning_problem["tuning_problem_name"]
        model_data["tuning_problem_unique_name"] = tuning_problem["unique_name"]
        model_data["hyperparameters"] = surrogate_model["hyperparameters"]
        model_data["model_stats"] = surrogate_model["model_stats"]
        model_data["model_stats"]["num_samples"] = len(surrogate_model["function_evaluations"])

        model_data["function_evaluations"] = []
        func_eval_id = 1
        for func_eval_uid in surrogate_model["function_evaluations"]:
            func_eval_document = historydb.load_func_eval_by_uid(func_eval_uid)
            func_eval_document["id"] = func_eval_id
            func_eval_id += 1
            model_data["function_evaluations"].append(func_eval_document)

        model_data["task_parameters"] = []
        for i in range(len(surrogate_model["input_space"])):
            task_space = surrogate_model["input_space"][i]

            task_parameter = {}
            task_parameter["name"] = task_space["name"]
            task_parameter["type"] = task_space["type"]
            task_parameter["lower_bound"] = task_space["lower_bound"]
            task_parameter["upper_bound"] = task_space["upper_bound"]
            for task_info in tuning_problem["tuning_problem_info"]["task_info"]:
                if task_info["task_name"] == task_parameter["name"]:
                    task_parameter["description"] = task_info["task_description"]
            task_parameter["options"] = []
            for j in range(len(surrogate_model["task_parameters"])):
                task_parameter["options"].append(surrogate_model["task_parameters"][j][i])
            task_parameter["value"] = task_parameter["options"][0]

            model_data["task_parameters"].append(task_parameter)

        model_data["tuning_parameters"] = []
        for parameter_space in surrogate_model["parameter_space"]:
            tuning_parameter = {}
            tuning_parameter["name"] = parameter_space["name"]
            tuning_parameter["type"] = parameter_space["type"]
            tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
            tuning_parameter["upper_bound"] = parameter_space["upper_bound"]

            for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                if parameter_info["parameter_name"] == tuning_parameter["name"]:
                    tuning_parameter["description"] = parameter_info["parameter_description"]
            tuning_parameter["value"] = tuning_parameter["lower_bound"]

            model_data["tuning_parameters"].append(tuning_parameter)

        model_data["output_parameters"] = []
        for output_space in surrogate_model["output_space"]:
            output_parameter = {}
            output_parameter["name"] = output_space["name"]
            output_parameter["type"] = output_space["type"]
            output_parameter["lower_bound"] = output_space["lower_bound"]
            output_parameter["upper_bound"] = output_space["upper_bound"]

            for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                if output_info["output_name"] == output_parameter["name"]:
                    output_parameter["description"] = output_info["output_description"]
            output_parameter["result"] = "-"

            model_data["output_parameters"].append(output_parameter)

        sobol_analysis = {}
        sobol_analysis["task_parameters"] = []
        for i in range(len(surrogate_model["task_parameters"])):
            task_parameter = {}
            for j in range(len(surrogate_model["input_space"])):
                #task_parameter["name"] = surrogate_model["input_space"][j]["name"]
                #task_parameter["value"] = surrogate_model["task_parameters"][i][j]
                task_parameter[surrogate_model["input_space"][j]["name"]] = surrogate_model["task_parameters"][i][j]
            sobol_analysis["task_parameters"].append(task_parameter)
        sobol_analysis["num_samples"] = 1000

        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(model_data)
        pp.pprint(sobol_analysis)
        print ("MODEL_DATA: ", model_data)
        #pp.pprint("MODEL_DATA: ", model_data)

        context = {
                "model_data" : model_data,
                "sobol_analysis" : sobol_analysis
                }

        return render(request, 'repo/surrogate-model.html', context)

    def post(self, request, **kwargs):
        tuning_problem_unique_name = request.POST["tuning_problem_unique_name"]
        surrogate_model_uid = request.POST["surrogate_model_uid"]
        sobol_analysis_task_parameter = request.POST["sobol_analysis_task_parameter"]
        sobol_analysis_num_samples = int(request.POST["sobol_analysis_num_samples"])
        historydb = HistoryDB_MongoDB()
        tuning_problem = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
        surrogate_model = historydb.load_surrogate_model_by_uid(surrogate_model_uid)
        print ("tuning_problem: ", tuning_problem)
        print ("sobol_analysis_task_parameter: ", sobol_analysis_task_parameter)
        print ("sobol_analysis_num_samples: ", sobol_analysis_num_samples)

        print ("SURROGATE_MODEL")
        print (surrogate_model)

        tuning_problem_name = surrogate_model["tuning_problem_name"]
        os.system("rm -rf .gptune")
        os.system("mkdir -p .gptune")
        json_data = {}
        json_data["tuning_problem_name"] = tuning_problem_name
        with open(".gptune/meta.json", "w") as f_out:
            json.dump(json_data, f_out, indent=2)

        func_eval_list = []
        for func_eval_uid in surrogate_model["function_evaluations"]:
            func_eval = historydb.load_func_eval_by_uid(func_eval_uid)
            del(func_eval["_id"])
            func_eval_list.append(func_eval)
        #print ("func_eval_list: ", func_eval_list)

        os.system("rm -rf gptune.db")
        os.system("mkdir -p gptune.db")
        json_data = {}
        json_data["func_eval"] = func_eval_list
        with open("gptune.db/"+tuning_problem_name+".json", "w") as f_out:
            json.dump(json_data, f_out, indent=2)

        model_data = {}

        model_data["surrogate_model_uid"] = surrogate_model_uid

        model_data["tuning_problem_name"] = tuning_problem["tuning_problem_name"]
        model_data["tuning_problem_unique_name"] = tuning_problem["unique_name"]
        model_data["hyperparameters"] = surrogate_model["hyperparameters"]
        model_data["model_stats"] = surrogate_model["model_stats"]
        model_data["model_stats"]["num_samples"] = len(surrogate_model["function_evaluations"])

        model_data["function_evaluations"] = []
        func_eval_id = 1
        for func_eval_uid in surrogate_model["function_evaluations"]:
            func_eval_document = historydb.load_func_eval_by_uid(func_eval_uid)
            func_eval_document["id"] = func_eval_id
            func_eval_id += 1
            model_data["function_evaluations"].append(func_eval_document)

        model_data["task_parameters"] = []
        for i in range(len(surrogate_model["input_space"])):
            task_space = surrogate_model["input_space"][i]

            task_parameter = {}
            task_parameter["name"] = task_space["name"]
            task_parameter["type"] = task_space["type"]
            task_parameter["lower_bound"] = task_space["lower_bound"]
            task_parameter["upper_bound"] = task_space["upper_bound"]
            for task_info in tuning_problem["tuning_problem_info"]["task_info"]:
                if task_info["task_name"] == task_parameter["name"]:
                    task_parameter["description"] = "task_desc: " + task_info["task_description"]
            task_parameter["options"] = []
            for j in range(len(surrogate_model["task_parameters"])):
                task_parameter["options"].append(surrogate_model["task_parameters"][j][i])
            task_parameter["value"] = task_parameter["options"][0]

            model_data["task_parameters"].append(task_parameter)

        model_data["tuning_parameters"] = []
        for parameter_space in surrogate_model["parameter_space"]:
            tuning_parameter = {}
            tuning_parameter["name"] = parameter_space["name"]
            tuning_parameter["type"] = parameter_space["type"]
            tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
            tuning_parameter["upper_bound"] = parameter_space["upper_bound"]

            for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                if parameter_info["parameter_name"] == tuning_parameter["name"]:
                    tuning_parameter["description"] = "tuning_desc: " + parameter_info["parameter_description"]
            tuning_parameter["value"] = tuning_parameter["lower_bound"]

            model_data["tuning_parameters"].append(tuning_parameter)

        model_data["output_parameters"] = []
        for output_space in surrogate_model["output_space"]:
            output_parameter = {}
            output_parameter["name"] = output_space["name"]
            output_parameter["type"] = output_space["type"]
            output_parameter["lower_bound"] = output_space["lower_bound"]
            output_parameter["upper_bound"] = output_space["upper_bound"]

            for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                if output_info["output_name"] == output_parameter["name"]:
                    output_parameter["description"] = "output_desc: " + output_info["output_description"]
            output_parameter["result"] = "-"

            model_data["output_parameters"].append(output_parameter)

        sobol_analysis = {}
        sobol_analysis["task_parameters"] = []
        for i in range(len(surrogate_model["task_parameters"])):
            task_parameter = {}
            for j in range(len(surrogate_model["input_space"])):
                #task_parameter["name"] = surrogate_model["input_space"][j]["name"]
                #task_parameter["value"] = surrogate_model["task_parameters"][i][j]
                task_parameter[surrogate_model["input_space"][j]["name"]] = surrogate_model["task_parameters"][i][j]
            sobol_analysis["task_parameters"].append(task_parameter)
        sobol_analysis["num_samples"] = 1000

        sobol_analysis_task_parameter = ast.literal_eval(request.POST["sobol_analysis_task_parameter"])
        print ("SOBEL_ANALYSIS_TASK_PARAMETER: ", sobol_analysis_task_parameter)
        sobol_analysis_task_parameter_arr = [sobol_analysis_task_parameter[key] for key in sobol_analysis_task_parameter.keys()]
        print ("SOBEL_ANALYSIS_TASK_PARAMETER_ARR: ", sobol_analysis_task_parameter_arr)

        si = SensitivityAnalysis(model_data=surrogate_model, task_parameters=sobol_analysis_task_parameter_arr, num_samples=sobol_analysis_num_samples)

        sobol_analysis["s1_parameters"] = []

        S1_array = si["S1"]
        S1_conf_array = si["S1_conf"]
        for i in range(len(surrogate_model["parameter_space"])):
            parameter_space = surrogate_model["parameter_space"][i]
            tuning_parameter = {}
            tuning_parameter["name"] = parameter_space["name"]
            tuning_parameter["S1"] = round(S1_array[i],3)
            tuning_parameter["S1_conf"] = round(S1_conf_array[i],3)

            sobol_analysis["s1_parameters"].append(tuning_parameter)

        sobol_analysis["st_parameters"] = []

        ST_array = si["ST"]
        ST_conf_array = si["ST_conf"]
        for i in range(len(surrogate_model["parameter_space"])):
            parameter_space = surrogate_model["parameter_space"][i]
            tuning_parameter = {}
            tuning_parameter["name"] = parameter_space["name"]
            tuning_parameter["ST"] = round(ST_array[i],3)
            tuning_parameter["ST_conf"] = round(ST_conf_array[i],3)

            sobol_analysis["st_parameters"].append(tuning_parameter)

        sobol_analysis["s2_parameters"] = []

        S2_array = si["S2"]
        S2_conf_array = si["S2_conf"]
        num_parameters = len(surrogate_model["parameter_space"])
        for i in range(num_parameters):
            for j in range(i+1, num_parameters):
                tuning_parameter = {}
                tuning_parameter["name1"] = surrogate_model["parameter_space"][i]["name"]
                tuning_parameter["name2"] = surrogate_model["parameter_space"][j]["name"]
                tuning_parameter["S2"] = round(S2_array[i][j],3)
                tuning_parameter["S2_conf"] = round(S2_conf_array[i][j],3)

                sobol_analysis["s2_parameters"].append(tuning_parameter)

        #import pprint
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(si)

        context = {
                "model_data" : model_data,
                "sobol_analysis" : sobol_analysis
                }

        return render(request, 'repo/surrogate-model.html', context)

class EntryAccess(TemplateView):
    def get(self, request, **kwargs):
        context = {}

        return render(request, 'repo/user-dashboard.html', context)

    def post(self, request, **kwargs):
        entry_uid = request.POST["entry_uid"]
        tuning_problem_unique_name = request.POST["tuning_problem_unique_name"]

        accessibility_type = request.POST['accessibility']
        access_group_given = request.POST['group_invites']
        print ('access group: ', access_group_given)
        access_group = access_group_given.split(';')

        accessibility = {}
        accessibility["type"] = accessibility_type
        if (accessibility_type == "group"):
            accessibility["group"] = access_group

        historydb = HistoryDB_MongoDB()
        historydb.update_entry_accessibility(tuning_problem_unique_name, entry_uid, accessibility)

        return redirect(reverse_lazy('repo:user-dashboard')) #, kwargs={'username': user.username}))

class EntryAccess(TemplateView):
    def get(self, request, **kwargs):
        context = {}

        return render(request, 'repo/user-dashboard.html', context)

    def post(self, request, **kwargs):
        entry_uid = request.POST["entry_uid"]
        tuning_problem_unique_name = request.POST["tuning_problem_unique_name"]

        accessibility_type = request.POST['accessibility']
        access_group_given = request.POST['group_invites']
        print ('access group: ', access_group_given)
        access_group = access_group_given.split(';')

        accessibility = {}
        accessibility["type"] = accessibility_type
        if (accessibility_type == "group"):
            accessibility["group"] = access_group

        historydb = HistoryDB_MongoDB()
        historydb.update_entry_accessibility(tuning_problem_unique_name, entry_uid, accessibility)

        return redirect(reverse_lazy('repo:user-dashboard')) #, kwargs={'username': user.username}))

class EntryDel(TemplateView):
    def get(self, request, **kwargs):
        context = {}

        return render(request, 'repo/user-dashboard.html', context)

    def post(self, request, **kwargs):
        entry_uid = request.POST["entry_uid"]
        tuning_problem_unique_name = request.POST["tuning_problem_unique_name"]

        historydb = HistoryDB_MongoDB()
        historydb.delete_perf_data_by_uid(tuning_problem_unique_name, entry_uid)

        return redirect(reverse_lazy('repo:user-dashboard')) #, kwargs={'username': user.username}))

class Export(TemplateView):

    def get(self, request, **kwargs):
        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")
        machine_configurations_list = json.loads(request.GET.get("machine_configurations_list", "{}"))
        software_configurations_list = json.loads(request.GET.get("software_configurations_list", "{}"))
        user_configurations_list = json.loads(request.GET.get("user_configurations_list", "{}"))
        user_email = ""
        if request.user.is_authenticated:
            user_email = request.user.email

        search_options = json.loads(request.GET.get("search_options", "[]"))

        #print ("machine_configurations_list: ", machine_configurations_list)
        #print ("software_configurations_list: ", software_configurations_list)
        #print ("user_configurations_list: ", user_configurations_list)

        historydb = HistoryDB_MongoDB()

        perf_data = []

        if "func_eval" in search_options:
            perf_data.extend(historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                machine_configurations_list = machine_configurations_list,
                software_configurations_list = software_configurations_list,
                user_configurations_list = user_configurations_list,
                user_email = user_email))
        if "surrogate_model" in search_options:
            perf_data.extend(historydb.load_surrogate_models_filtered(
                tuning_problem_unique_name = tuning_problem_unique_name,
                machine_configurations_list = machine_configurations_list,
                software_configurations_list = software_configurations_list,
                user_configurations_list = user_configurations_list,
                user_email = user_email))

        context = { "perf_data" : perf_data, }

        return render(request, 'repo/export.html', context)

class Upload(TemplateView):

    def get(self, request, **kwargs):
        print ("======== Upload GET ========")

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        if not request.user.profile.is_certified:
            context = {
                    "header": "Please Wait!",
                    "message": "You have no permission to upload (Please wait for our approval)"
                    }
            return render(request, 'repo/return.html', context)

        historydb = HistoryDB_MongoDB()

        tuning_problems_avail = historydb.load_all_tuning_problems()
        for tuning_problem in tuning_problems_avail:
            tuning_problem.pop('_id')
        machines_avail = historydb.load_all_machine_info()
        for machine in machines_avail:
            machine.pop('_id')

        context = {
                "tuning_problems_avail" : tuning_problems_avail,
                "machines_avail" : machines_avail,
                "GOOGLE_RECAPTCHA_SITE_KEY": settings.GOOGLE_RECAPTCHA_SITE_KEY,
                }

        return render(request, 'repo/upload.html', context)

    def post(self, request, **kwargs):
        print ("======== Upload POST ========")

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        if not request.user.profile.is_certified:
            context = {
                    "header": "Please Wait!",
                    "message": "You have no permission to upload (Please wait for our approval)"
                    }
            return render(request, 'repo/return.html', context)

        user_info = {}
        user_info["user_name"] = request.user.username
        user_info["user_email"] = request.user.email
        user_info["affiliation"] = request.user.profile.affiliation

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if result['success']:
            tuning_problem_unique_name = request.POST["tuning_problem"]
            machine_unique_name = request.POST["machine"]

            json_data = {}

            upload_type = "file"
            try:
                f = request.FILES["file_upload_form"]
                data = f.read()
            except:
                upload_type = "text"

            if upload_type == "text":
                try:
                    json_text = request.POST["text_upload_form"]
                    data = json_text
                except:
                    data = {}

            try:
                json_data = json.loads(data)
            except:
                print ("Not able to convert to dictionary")
                context = {
                        "header": "Something Went Wrong",
                        "message": "Not able to convert data to dictionary"
                        }
                return render(request, 'repo/return.html', context)

            accessibility_type = request.POST['accessibility']
            access_group_given = request.POST['group_invites']
            access_group = re.split(', |,', access_group_given)

            accessibility = {}
            accessibility["type"] = accessibility_type
            if (accessibility_type == "group"):
                accessibility["group"] = access_group

            historydb = HistoryDB_MongoDB()
            try:
                num_added_func_eval = historydb.upload_func_eval(tuning_problem_unique_name, machine_unique_name, json_data, user_info, accessibility)
                num_added_surrogate_models = historydb.upload_surrogate_models(tuning_problem_unique_name, machine_unique_name, json_data, user_info, accessibility)
            except:
                print ("Not able to upload the given data")
                context = {
                        "header": "Something Went Wrong",
                        "message": "Not able to upload the given data"
                        }
                return render(request, 'repo/return.html', context)

            print ("Submitted data has been uploaded")
            context = {
                    "header": "Success",
                    "message": "Your data has been uploaded",
                    "num_added_func_eval": num_added_func_eval,
                    "num_added_surrogate_models": num_added_surrogate_models
                    }

            return render(request, 'repo/return.html', context)
        else:
            context = {
                "header": "Something went wrong",
                "message": "Failed to upload the performance data"
            }
            return render(request, 'repo/return.html', context)

class TuningProblems(TemplateView):

    def get(self, request, **kwargs):

        historydb = HistoryDB_MongoDB()
        tuning_problem_list_ = historydb.load_all_tuning_problems()

        tuning_problem_list = [{} for i in range(len(tuning_problem_list_))]
        for i in range(len(tuning_problem_list_)):
            tuning_problem_list[i]["id"] = i
            tuning_problem_list[i]["uid"] = tuning_problem_list_[i]["uid"]
            tuning_problem_list[i]["tuning_problem_info"] = tuning_problem_list_[i]["tuning_problem_info"]
            tuning_problem_list[i]["tuning_problem_name"] = tuning_problem_list_[i]["tuning_problem_name"]
            tuning_problem_list[i]["unique_name"] = tuning_problem_list_[i]["unique_name"]
            tuning_problem_list[i]["user_name"] = tuning_problem_list_[i]["user_info"]["user_name"]
            tuning_problem_list[i]["update_time"] = tuning_problem_list_[i]["update_time"]

        context = {
                "tuning_problem_list" : tuning_problem_list
                }

        return render(request, 'repo/tuning-problems.html', context)

class AddTuningProblemSelect(TemplateView):

    def get(self, request, **kwargs):

        historydb = HistoryDB_MongoDB()

        context = {}

        return render(request, 'repo/add-tuning-problem-select.html', context)

class AddTuningProblem(TemplateView):

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        historydb = HistoryDB_MongoDB()

        def get_data_from_file(filename, keyword):
            with open(filename, "r") as f_in:
                data = json.load(f_in)
                return data[keyword]

        def convert_to_jstree_json(tree_json):
            jstree_json = {}
            node_array = []

            def walk(parent, node):
                for key, value in node.items():
                    if isinstance(value, dict):
                        node_array.append({"id": key, "parent": parent, "text": key})
                        walk(key, value)
                    elif isinstance(value, list):
                        node_array.append({"id": key, "parent": parent, "text": key})
                        for item in value:
                            node_array.append({"id": item, "parent": key, "text": item, "icon": "jstree-file"})

            walk("#", tree_json)

            jstree_json["core"] = {"data": node_array}

            return jstree_json

        category_jstree = convert_to_jstree_json(get_data_from_file(os.environ["HISTORYDB_JSON_DATA"]+"/software_data.json", "category_tree"))
        software_jstree = convert_to_jstree_json(get_data_from_file(os.environ["HISTORYDB_JSON_DATA"]+"/software_data.json", "software_tree"))

        context = {
                "category_jstree": category_jstree,
                "software_jstree": software_jstree,
                "GOOGLE_RECAPTCHA_SITE_KEY": settings.GOOGLE_RECAPTCHA_SITE_KEY,
                }

        return render(request, 'repo/add-tuning-problem.html', context)

    def post(self, request, **kwargs):

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        if not request.user.profile.is_certified:
            context = {
                    "header": "Please Wait!",
                    "message": "You have no permission to upload (Please wait for our approval)"
                    }
            return render(request, 'repo/return.html', context)

        user_info = {}
        user_info["user_name"] = request.user.username
        user_info["user_email"] = request.user.email
        user_info["affiliation"] = request.user.profile.affiliation

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if result['success']:
            tuning_problem_name = request.POST['tuning_problem_name']

            tuning_problem_info = {}

            category_names = request.POST.getlist('category_name')
            category_tags = request.POST.getlist('category_tags')
            tuning_problem_info["category"] = []
            for i in range(len(category_names)):
                tuning_problem_info["category"].append({
                    "category_name": category_names[i],
                    "category_tags": re.split(', |,', category_tags[i])
                    })

            tuning_problem_info["description"] = request.POST['tuning_problem_description']

            task_names = request.POST.getlist('task_name')
            task_types = request.POST.getlist('task_type')
            task_descriptions = request.POST.getlist('task_description')
            num_tasks = len(task_names)

            tuning_problem_info["task_info"] = []
            for i in range(num_tasks):
                tuning_problem_info["task_info"].append({
                    "task_name": task_names[i],
                    "task_type": task_types[i],
                    "task_description": task_descriptions[i],
                    })

            parameter_names = request.POST.getlist('parameter_name')
            parameter_types = request.POST.getlist('parameter_type')
            parameter_descriptions = request.POST.getlist('parameter_description')
            num_parameters = len(parameter_names)

            tuning_problem_info["parameter_info"] = []
            for i in range(num_parameters):
                tuning_problem_info["parameter_info"].append({
                    "parameter_name": parameter_names[i],
                    "parameter_type": parameter_types[i],
                    "parameter_description": parameter_descriptions[i]
                    })

            output_names = request.POST.getlist('output_name')
            output_types = request.POST.getlist('output_type')
            output_descriptions = request.POST.getlist('output_description')
            num_outputs = len(output_names)

            tuning_problem_info["output_info"] = []
            for i in range(num_outputs):
                tuning_problem_info["output_info"].append({
                    "output_name": output_names[i],
                    "output_type": output_types[i],
                    "output_description": output_descriptions[i]
                    })

            constant_names = request.POST.getlist('constant_name')
            constant_types = request.POST.getlist('constant_type')
            constant_descriptions = request.POST.getlist('constant_description')
            num_constants = len(constant_names)

            tuning_problem_info["constant_info"] = []
            for i in range(num_constants):
                tuning_problem_info["constant_info"].append({
                    "constant_name": constant_names[i],
                    "constant_type": constant_types[i],
                    "constant_description": constant_descriptions[i]
                    })

            required_software_names = request.POST.getlist('software_name')
            required_software_types = []
            for i in range(len(required_software_names)):
                required_software_types.append(request.POST['software_type'+str(i)])
            required_software_tags = request.POST.getlist('software_tags')

            tuning_problem_info["required_software_info"] = []
            for i in range(len(required_software_names)):
                tuning_problem_info["required_software_info"].append({
                    "software_name": required_software_names[i],
                    "software_type": required_software_types[i],
                    "software_tags": re.split(', |,', required_software_tags[i])
                    })

            print ("tuning_problem_info: ", tuning_problem_info)

            historydb = HistoryDB_MongoDB()
            historydb.add_tuning_problem(tuning_problem_name, tuning_problem_info, user_info)

            return redirect(reverse_lazy('repo:tuning-problems'))
        else:
            context = {
                "header": "Something went wrong",
                "message": "Failed to add the tuning problem"
            }
            return render(request, 'repo/return.html', context)

class AddReproducibleWorkflow(TemplateView):

    def get(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()

        context = {}

        return render(request, 'repo/add-reproducible-workflow.html', context)

class AddTuningCategory(TemplateView):

    def get(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()

        context = {}

        return render(request, 'repo/add-tuning-category.html', context)

class Applications(TemplateView):

    def get(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()

        context = {}

        return render(request, 'repo/applications.html', context)

class AddApplications(TemplateView):

    def get(self, request, **kwargs):
        print ("======== Upload GET ========")

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        if not request.user.profile.is_certified:
            context = {
                    "header": "Please Wait!",
                    "message": "You have no permission to upload (Please wait for our approval)"
                    }
            return render(request, 'repo/return.html', context)

        historydb = HistoryDB_MongoDB()
        applications_avail = historydb.get_applications_avail()
        applications_avail_per_library = historydb.get_applications_avail_per_library()

        context = {
                "applications_avail" : applications_avail,
                "applications_avail_per_library" : applications_avail_per_library,
                }

        return render(request, 'repo/add-applications.html', context)

    def post(self, request, **kwargs):
        print ("======== Upload POST ========")

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        user_info = {}
        user_info["user_name"] = request.user.username
        user_info["user_email"] = request.user.email
        user_info["affiliation"] = request.user.profile.affiliation

        application_name = request.POST["application_name"]
        library_name = request.POST["application_category"]
        application_description = request.POST["application_description"]

        application_info = {}
        application_info["name"] = application_name
        application_info["library"] = library_name
        application_info["description"] = application_description

        print ("application_name: ", application_name)
        print ("library_name: ", library_name)
        print ("application_description: ", application_description)

        historydb = HistoryDB_MongoDB()
        try:
            historydb.upload_application_info(user_info, application_info)
        except:
            print ("Not able to add the application")
            context = {
                    "header": "Something Went Wrong",
                    "message": "Not able to add the application"
                    }
            return render(request, 'repo/return.html', context)

        print ("Added the application")
        context = {
                "header": "Success",
                "message": "The application information has been added"
                }
        return render(request, 'repo/return.html', context)

class Architectures(TemplateView):

    def get(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()

        context = {}

        return render(request, 'repo/architectures.html', context)

class AddArchitectures(TemplateView):

    def get(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()

        context = {}

        return render(request, 'repo/add-architectures.html', context)

class Machines(TemplateView):

    def get(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()
        machine_info_list = historydb.load_all_machine_info()
        for i in range(len(machine_info_list)):
            machine_info_list[i]["id"] = i

        context = {
                "machine_info_list" : machine_info_list
                }

        return render(request, 'repo/machines.html', context)

class AddMachine(TemplateView):

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        historydb = HistoryDB_MongoDB()

        def get_data_from_file(filename, keyword):
            print (filename)
            with open(filename, "r") as f_in:
                data = json.load(f_in)
                return data[keyword]

        def convert_to_jstree_json(tree_json):
            jstree_json = {}
            node_array = []

            def walk(parent, node):
                for key, value in node.items():
                    if isinstance(value, dict):
                        print ("parent: ", parent, " key: ", key)
                        node_array.append({"id": key, "parent": parent, "text": key})
                        walk(key, value)
                    elif isinstance(value, list):
                        node_array.append({"id": key, "parent": parent, "text": key})
                        for item in value:
                            node_array.append({"id": item, "parent": key, "text": item, "icon": "jstree-file"})
                        print ("parent: ", parent, " value: ", value)

            walk("#", tree_json)
            print (json.dumps(node_array))

            jstree_json["core"] = {"data": node_array}

            return jstree_json

        system_models_jstree = convert_to_jstree_json(get_data_from_file(os.environ["HISTORYDB_JSON_DATA"]+"/hardware_data.json", "system_models_tree"))
        processors_jstree = convert_to_jstree_json(get_data_from_file(os.environ["HISTORYDB_JSON_DATA"]+"/hardware_data.json", "processors_tree"))
        interconnect_jstree = convert_to_jstree_json(get_data_from_file(os.environ["HISTORYDB_JSON_DATA"]+"/hardware_data.json", "interconnect_tree"))

        context = {
                "system_models_jstree" : system_models_jstree,
                "processors_jstree" : processors_jstree,
                "interconnect_jstree" : interconnect_jstree,
                "GOOGLE_RECAPTCHA_SITE_KEY": settings.GOOGLE_RECAPTCHA_SITE_KEY,
                }

        return render(request, 'repo/add-machine.html', context)

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        user_info = {}
        user_info["user_name"] = request.user.username
        user_info["user_email"] = request.user.email
        user_info["affiliation"] = request.user.profile.affiliation

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if result['success']:
            machine_name = request.POST['machine_name']
            system_model_names = request.POST.getlist('system_model_name')
            system_model_tags = request.POST.getlist('system_model_tags')
            processor_model_names = request.POST.getlist('processor_model_name')
            processor_model_tags = request.POST.getlist('processor_model_tags')
            num_nodes = request.POST.getlist('num_nodes')
            num_cores = request.POST.getlist('num_cores')
            num_sockets = request.POST.getlist('num_sockets')
            memory_size = request.POST.getlist('memory_size')
            interconnect_names = request.POST.getlist('interconnect_name')
            interconnect_tags = request.POST.getlist('interconnect_tags')

            machine_info = {}
            machine_info["system_model"] = []
            for i in range(len(system_model_names)):
                machine_info["system_model"].append({
                    "system_model_name": system_model_names[i],
                    "system_model_tags": re.split(', |,', system_model_tags[i])
                    })

            machine_info["processor_model"] = []
            for i in range(len(processor_model_names)):
                machine_info["processor_model"].append({
                    "processor_model_name": processor_model_names[i],
                    "processor_model_tags": re.split(', |,', processor_model_tags[i]),
                    "num_nodes": num_nodes[i],
                    "num_cores": num_cores[i],
                    "num_sockets": num_sockets[i],
                    "memory_size": memory_size[i]
                    })

            machine_info["interconnect"] = []
            for i in range(len(interconnect_names)):
                machine_info["interconnect"].append({
                    "interconnect_name": interconnect_names[i],
                    "interconnect_tags": re.split(', |,', interconnect_tags[i])
                    })

            historydb = HistoryDB_MongoDB()
            historydb.add_machine_info(machine_name, machine_info, user_info)

            return redirect(reverse_lazy('repo:machines'))
        else:
            context = {
                "header": "Something went wrong",
                "message": "Failed to upload the machine information"
            }
            return render(request, 'repo/return.html', context)

class AnalyticalModels(TemplateView):

    def get(self, request, **kwargs):

        historydb = HistoryDB_MongoDB()

        user_email = ""
        if request.user.is_authenticated:
            user_email = request.user.email

        analytical_model_list = historydb.load_all_analytical_models(user_email)
        for i in range(len(analytical_model_list)):
            analytical_model_list[i]["id"] = i

        print (analytical_model_list)

        context = {
            "analytical_model_list" : analytical_model_list
        }

        return render(request, 'repo/analytical-models.html', context)

class AddAnalyticalModel(TemplateView):

    def get(self, request, **kwargs):

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        context = {
            "GOOGLE_RECAPTCHA_SITE_KEY": settings.GOOGLE_RECAPTCHA_SITE_KEY,
        }

        return render(request, 'repo/add-analytical-model.html', context)

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        if not request.user.profile.is_certified:
            context = {
                    "header": "Please Wait!",
                    "message": "You have no permission to upload (Please wait for our approval)"
                    }
            return render(request, 'repo/return.html', context)

        user_info = {}
        user_info["user_name"] = request.user.username
        user_info["user_email"] = request.user.email
        user_info["affiliation"] = request.user.profile.affiliation

        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if result['success']:
            model_name = request.POST['model_name']
            model_description = request.POST['model_description']

            print ("model_name: ", model_name)
            print ("model_description: ", model_description)

            model_data = {}
            model_data['model_name'] = model_name
            model_data['model_description'] = model_description

            data_type_list = request.POST.getlist('data_type')
            for data_type in data_type_list:
                print ("data_type: ", data_type)

                if data_type == "data_type_python_code":
                    model_data['model_code_python'] = request.POST['model_code_python']
                elif data_type == "data_type_any_code":
                    model_data['model_code_any'] = request.POST['model_code_any']
                elif data_type == "data_type_pointer_to_code":
                    model_data['model_pointer'] = request.POST['model_pointer']

            update_type_list = request.POST.getlist('update_type')
            if len(update_type_list) > 0:
                model_data['update_required'] = 'yes'
            else:
                model_data['update_required'] = 'no'

            for update_type in update_type_list:
                print ("update_type: ", update_type)

                if update_type == "update_type_python_code":
                    model_data['model_update_code_python'] = request.POST['model_update_code_python']
                elif update_type == "update_type_any_code":
                    model_data['model_update_code_any'] = request.POST['model_update_code_any']
                elif update_type == "update_type_pointer_to_code":
                    model_data['model_update_pointer'] = request.POST['model_update_pointer']

            task_names = request.POST.getlist('task_name')
            task_types = request.POST.getlist('task_type')
            task_descriptions = request.POST.getlist('task_description')
            num_tasks = len(task_names)

            model_data["task_info"] = []
            for i in range(num_tasks):
                model_data["task_info"].append({
                    "task_name": task_names[i],
                    "task_type": task_types[i],
                    "task_description": task_descriptions[i],
                    })

            parameter_names = request.POST.getlist('parameter_name')
            parameter_types = request.POST.getlist('parameter_type')
            parameter_descriptions = request.POST.getlist('parameter_description')
            num_parameters = len(parameter_names)

            model_data["parameter_info"] = []
            for i in range(num_parameters):
                model_data["parameter_info"].append({
                    "parameter_name": parameter_names[i],
                    "parameter_type": parameter_types[i],
                    "parameter_description": parameter_descriptions[i]
                    })

            output_names = request.POST.getlist('output_name')
            output_types = request.POST.getlist('output_type')
            output_descriptions = request.POST.getlist('output_description')
            num_outputs = len(output_names)

            model_data["output_info"] = []
            for i in range(num_outputs):
                model_data["output_info"].append({
                    "output_name": output_names[i],
                    "output_type": output_types[i],
                    "output_description": output_descriptions[i]
                    })

            constant_names = request.POST.getlist('constant_name')
            constant_types = request.POST.getlist('constant_type')
            constant_descriptions = request.POST.getlist('constant_description')
            num_constants = len(constant_names)

            model_data["constant_info"] = []
            for i in range(num_constants):
                model_data["constant_info"].append({
                    "constant_name": constant_names[i],
                    "constant_type": constant_types[i],
                    "constant_description": constant_descriptions[i]
                    })

            check_update_required = request.POST['check_update_required']
            print ("check_update_required: ", check_update_required)

            accessibility_type = request.POST['accessibility']
            access_group_given = request.POST['group_invites']
            print ("accessibility_type: ", accessibility_type)
            print ('access group: ', access_group_given)
            access_group = access_group_given.split(';')

            accessibility = {}
            accessibility["type"] = accessibility_type
            if (accessibility_type == "group"):
                accessibility["group"] = access_group

            historydb = HistoryDB_MongoDB()
            if (historydb.upload_analytical_model(model_name, model_data, user_info, accessibility) == True):
                return redirect(reverse_lazy('repo:analytical-models'))
            else:
                context = {
                    "header": "Something went wrong",
                    "message": "Failed to upload the analytical model"
                }
                return render(request, 'repo/return.html', context)
        else:
            context = {
                "header": "Something went wrong",
                "message": "Failed to upload the analytical model"
            }
            return render(request, 'repo/return.html', context)

class UserGroups(TemplateView):

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))
        else:
            historydb = HistoryDB_MongoDB()
            user_groups = historydb.load_user_collaboration_groups(request.user.email)
            for i in range(len(user_groups)):
                user_groups[i]['no'] = i+1
                for member in user_groups[i]['members']:
                    if member['email'] == request.user.email:
                        user_groups[i]['my_role'] = member['role']
                        break
            print ("USER GROUPS")
            print (user_groups)
            context = { "user_groups" : user_groups }
            return render(request, 'repo/user-groups.html', context)

class AddGroup(TemplateView):

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))
        else:
            historydb = HistoryDB_MongoDB()
            context = {
                    "user_email" : request.user.email
                    }
            return render(request, 'repo/add-group.html', context)

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))
        else:
            group_name = request.POST['group_name']

            invites_emails = request.POST.getlist('invites_emails')
            invites_roles = request.POST.getlist('invites_roles')

            print ("invites_emails: ", invites_emails)
            print ("invites_roles: ", invites_roles)

            group_details = {}
            group_details['group_name'] = group_name
            group_details['submitter'] = {
                    'user_name': request.user.username,
                    'user_email': request.user.email
                    }
            group_members = []
            for i in range(len(invites_emails)):
                group_members.append({"email":invites_emails[i], "role":invites_roles[i]})
            group_details['members'] = group_members

            import uuid
            group_details["uid"] = str(uuid.uuid1())

            historydb = HistoryDB_MongoDB()
            ret = historydb.add_collaboration_group(group_details)
            if ret == 0:
                context = {
                        "header": "Adding a collaboration group",
                        "message": "Your collaboration group has been added successfully."
                        }
                return render(request, 'repo/add-group-return.html', context)
            elif ret == -1:
                context = {
                        "header": "Adding a collaboration group",
                        "message": "Failed: The same group number already exists"
                        }
                return render(request, 'repo/add-group-return.html', context)

class UpdateRoles(TemplateView):

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))
        else:
            group_uid = request.POST['group_uid']
            invites_emails = request.POST.getlist('invites_emails')
            invites_roles = request.POST.getlist('invites_roles')

            print ("group_uid: ", group_uid)
            print ("invites_emails: ", invites_emails)
            print ("invites_roles: ", invites_roles)

            group_members = []
            for i in range(len(invites_emails)):
                group_members.append({"email":invites_emails[i], "role":invites_roles[i]})

            historydb = HistoryDB_MongoDB()
            ret = historydb.update_group_members(group_uid, group_members)
            if ret == 0:
                user_groups = historydb.load_user_collaboration_groups(request.user.email)
                for i in range(len(user_groups)):
                    user_groups[i]['no'] = i+1
                    for member in user_groups[i]['members']:
                        if member['email'] == request.user.email:
                            user_groups[i]['my_role'] = member['role']
                            break
                print ("USER GROUPS")
                print (user_groups)
                context = { "user_groups" : user_groups }
                return render(request, 'repo/user-groups.html', context)
            elif ret == -1:
                context = {
                        "header": "Updating group members",
                        "message": "Updating group members was unsuccessful."
                        }
                return render(request, 'repo/add-group-return.html', context)
            else:
                context = {
                        "header": "Updating group members",
                        "message": "Updating group members was unsuccessful."
                        }
                return render(request, 'repo/add-group-return.html', context)

class InviteMember(TemplateView):

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))
        else:
            group_uid = request.POST['group_uid']
            invite_email = request.POST['invite_email']
            invite_role = request.POST['invite_role']

            print ("group_uid: ", group_uid)
            print ("invite_email: ", invite_email)
            print ("invite_role: ", invite_role)

            historydb = HistoryDB_MongoDB()

            ret = historydb.add_group_member(group_uid, invite_email, invite_role)
            if ret == 0:
                user_groups = historydb.load_user_collaboration_groups(request.user.email)
                for i in range(len(user_groups)):
                    user_groups[i]['no'] = i+1
                    for member in user_groups[i]['members']:
                        if member['email'] == request.user.email:
                            user_groups[i]['my_role'] = member['role']
                            break
                print ("USER GROUPS")
                print (user_groups)
                context = { "user_groups" : user_groups }
                return render(request, 'repo/user-groups.html', context)
            elif ret == -1:
                context = {
                        "header": "Adding a group member",
                        "message": "Additing a group member was unsuccessful."
                        }
                return render(request, 'repo/add-group-return.html', context)

def query(request, perf_data_uid):
    historydb = HistoryDB_MongoDB()

    user_email = ""
    if request.user.is_authenticated:
        user_email = request.user.email

    perf_data = historydb.load_perf_data_by_uid(perf_data_uid, user_email)
    if perf_data is not None:
        context = {
                "return" : "success",
                "perf_data" : perf_data, }
    else:
        context = {
                "return" : "failure",
                "message" : "cannot access the performance data"
                }

    return render(request, 'repo/detail.html', context)

