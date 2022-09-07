from asyncore import write
from ctypes import util
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

from plotly.offline import plot
import pandas as pd

from dashing.driver import driver

import requests
import os
import json
import ast
import re
import copy

class Dashboard(TemplateView):

    def get(self, request, **kwargs):

        historydb = HistoryDB_MongoDB()

        tuning_problems_avail = historydb.load_all_tuning_problems()
        machine_configurations_avail = historydb.get_machine_configurations_avail()
        software_configurations_avail = historydb.get_software_configurations_avail()
        outputs_avail = historydb.get_outputs_avail()
        user_configurations_avail = historydb.get_user_configurations_avail()

        user_email = request.user.email if request.user.is_authenticated else ""

        print ("======== Dashboard GET ========")
        print ("machine_configurations_avail: ", machine_configurations_avail)
        print ("software_configurations_avail: ", software_configurations_avail)
        print ("outputs_avail: ", outputs_avail)
        print ("user_configurations_avail: ", user_configurations_avail)
        print ("user_email: ", user_email)

        context = {
                "tuning_problems_avail" : tuning_problems_avail,
                "machine_configurations_avail" : machine_configurations_avail,
                "software_configurations_avail" : software_configurations_avail,
                "outputs_avail" : outputs_avail,
                "user_configurations_avail" : user_configurations_avail
                }

        return render(request, 'repo/dashboard.html', context)

    def post(self, request, **kwargs):

        historydb = HistoryDB_MongoDB()

        tuning_problems_avail = historydb.load_all_tuning_problems()
        machine_configurations_avail = historydb.get_machine_configurations_avail()
        software_configurations_avail = historydb.get_software_configurations_avail()
        outputs_avail = historydb.get_outputs_avail()
        user_configurations_avail = historydb.get_user_configurations_avail()

        tuning_problem_unique_name = request.POST["tuning_problem"]
        if tuning_problem_unique_name == "":
            context = {
                "header": "Something went wrong",
                "message": "Please choose a tuning problem to search"
            }
            return render(request, 'main/error.html', context)

        tuning_problem_type = historydb.get_tuning_problem_type(tuning_problem_unique_name)
        tuning_problem_info = historydb.get_tuning_problem_info(tuning_problem_unique_name, tuning_problem_type)
        print ("tuning_problem_info: ", tuning_problem_info)

        machine_configurations_list = [ json.loads(val) for val in request.POST.getlist("machine_configurations_list") ]
        software_configurations_list = [ json.loads(val) for val in request.POST.getlist("software_configurations_list") ]
        output_options = request.POST.getlist("output_options")
        user_configurations_list = [ json.loads(val) for val in request.POST.getlist("user_configurations_list") ]
        search_options = request.POST.getlist("search_options")

        user_email = request.user.email if request.user.is_authenticated else ""

        if "func_eval" in search_options:
            func_eval_list = historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    output_options = output_options,
                    user_configurations_list = user_configurations_list,
                    user_email = user_email,
                    tuning_problem_type = tuning_problem_type)
            num_func_eval = len(func_eval_list)
            for i in range(num_func_eval):
                func_eval_list[i]["id"] = i
        else:
            func_eval_list = []
            num_func_eval = 0

        print ("FUNC_EVAL_LIST: ", func_eval_list)

        if "surrogate_model" in search_options:
            surrogate_model_list = historydb.load_surrogate_models_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    output_options = output_options,
                    user_configurations_list = user_configurations_list,
                    user_email = user_email,
                    tuning_problem_type = tuning_problem_type)
            num_surrogate_models = {}
            for output_option in output_options:
                num_surrogate_models[output_option] = len(surrogate_model_list[output_option])

            for output_option in output_options:
                i = 0
                for surrogate_model in surrogate_model_list[output_option]:
                    surrogate_model["id"] = i
                    i += 1
                    surrogate_model["num_func_eval"] = len(surrogate_model["function_evaluations"])
                    surrogate_model["num_task_parameters"] = len(surrogate_model["task_parameters"])
                    surrogate_model["num_func_eval_per_task"] = \
                            int(len(surrogate_model["function_evaluations"])/len(surrogate_model["task_parameters"]))
        else:
            surrogate_model_list = {}
            for output_option in output_options:
                surrogate_model_list[output_option] = []

            num_surrogate_models = {}
            for output_option in output_options:
                num_surrogate_models[output_option] = 0

        #print ("machine_configurations_avail: ", machine_configurations_avail)
        #print ("software_configurations_avail: ", software_configurations_avail)
        #print ("outputs_avail: ", outputs_avail)
        #print ("user_configurations_avail: ", user_configurations_avail)

        #print ("tuning_problem_unique_name: ", tuning_problem_unique_name)
        #print ("tuning_problem_info: ", tuning_problem_info)
        #print ("machine_configurations_list: ", machine_configurations_list)
        #print ("software_configurations_list: ", software_configurations_list)
        #print ("user_configurations_list: ", user_configurations_list)
        #print ("output_options: ", output_options)
        #print ("search_options: ", search_options)

        #print ("num_surrogate_models: ", num_surrogate_models)

        context = {
                "tuning_problem_unique_name" : tuning_problem_unique_name,
                "tuning_problem_info" : tuning_problem_info,
                "tuning_problems_avail" : tuning_problems_avail,
                "machine_configurations_avail" : machine_configurations_avail,
                "software_configurations_avail" : software_configurations_avail,
                "outputs_avail" : outputs_avail,
                "user_configurations_avail" : user_configurations_avail,
                "func_eval_list" : func_eval_list,
                "num_func_eval" : num_func_eval,
                "surrogate_model_list" : surrogate_model_list,
                "num_surrogate_models" : num_surrogate_models,
                "machine_configurations_list" : json.dumps(machine_configurations_list),
                "software_configurations_list" : json.dumps(software_configurations_list),
                "output_options" : json.dumps(output_options),
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

        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")
        surrogate_model_uids = request.GET.get("surrogate_model_uids", "").split(",")
        historydb = HistoryDB_MongoDB()
        tuning_problem = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
        surrogate_models = historydb.load_surrogate_models_by_uids(surrogate_model_uids)
        num_surrogate_models = len(surrogate_models)

        print ("======== Surrogate Model Dashboard ========")
        print ("tuning_problem_unique_name: ", tuning_problem_unique_name)
        print ("tuning_problem: ", tuning_problem)
        print ("Surrogate Model UIDs: ", surrogate_model_uids)
        print ("SURROGATE_MODEL")
        print (surrogate_models)

        model_data_list = []

        for surrogate_model in surrogate_models:
            model_data = {}

            model_data["surrogate_model_uid"] = surrogate_model["uid"]

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
                if task_parameter["type"] == "int" or task_parameter["type"] == "real":
                    task_parameter["lower_bound"] = task_space["lower_bound"]
                    task_parameter["upper_bound"] = task_space["upper_bound"]
                elif task_parameter["type"] == "categorical":
                    task_parameter["categories"] = task_space["categories"]
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
                if tuning_parameter["type"] == "int" or tuning_parameter["type"] == "real":
                    tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
                    tuning_parameter["upper_bound"] = parameter_space["upper_bound"]
                    tuning_parameter["value"] = tuning_parameter["lower_bound"]
                elif tuning_parameter["type"] == "categorical":
                    tuning_parameter["categories"] = parameter_space["categories"]
                    tuning_parameter["value"] = str(tuning_parameter["categories"][0])
                for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                    if parameter_info["parameter_name"] == tuning_parameter["name"]:
                        tuning_parameter["description"] = parameter_info["parameter_description"]

                model_data["tuning_parameters"].append(tuning_parameter)

            model_data["output_parameters"] = []
            for output_space in surrogate_model["output_space"]:
                output_parameter = {}
                output_parameter["name"] = output_space["name"]
                output_parameter["type"] = output_space["type"]
                if output_parameter["type"] == "int" or output_parameter["type"] == "real":
                    output_parameter["lower_bound"] = output_space["lower_bound"]
                    output_parameter["upper_bound"] = output_space["upper_bound"]
                elif output_parameter["type"] == "categorical":
                    output_parameter["categories"] = output_space["categories"]
                for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                    if output_info["output_name"] == output_parameter["name"]:
                        output_parameter["description"] = output_info["output_description"]
                output_parameter["result"] = "-"

                model_data["output_parameters"].append(output_parameter)

            model_data_list.append(model_data)

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

        #import pprint
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(model_data)
        #pp.pprint(sobol_analysis)
        #print ("MODEL_DATA: ", model_data)
        ##pp.pprint("MODEL_DATA: ", model_data)

        context = {
                "model_data" : model_data,
                "sobol_analysis" : sobol_analysis
                }

        return render(request, 'repo/surrogate-model.html', context)

class ModelPrediction(TemplateView):

    def get(self, request, **kwargs):

        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")
        surrogate_model_uids = request.GET.get("surrogate_model_uids", "")

        if surrogate_model_uids == "":
            print ("No surrogate model is given. Need to build a surrogate model.")
            historydb = HistoryDB_MongoDB()

            tuning_problem_loaded = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
            tuning_problem = copy.deepcopy(tuning_problem_loaded)
            tuning_problem_info = tuning_problem["tuning_problem_info"]

            machine_configurations_list = json.loads(request.GET.get("machine_configurations_list", "{}"))
            software_configurations_list = json.loads(request.GET.get("software_configurations_list", "{}"))
            output_options = json.loads(request.GET.get("output_options", "[]"))
            user_configurations_list = json.loads(request.GET.get("user_configurations_list", "{}"))
            user_email = request.user.email if request.user.is_authenticated else ""
            search_options = json.loads(request.GET.get("search_options", "[]"))

            input_task_avail = []

            func_eval_list = historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    output_options = output_options,
                    user_configurations_list = user_configurations_list,
                    user_email = user_email)
            num_func_eval = len(func_eval_list)
            for i in range(num_func_eval):
                func_eval_list[i]["id"] = i

                for parameter_info in tuning_problem_info["parameter_info"]:
                    parameter_name = parameter_info["parameter_name"]
                    parameter_type = parameter_info["parameter_type"]

                    if parameter_type == "integer" or parameter_type == "real":
                        value = func_eval_list[i]["tuning_parameter"][parameter_name]
                        if "lower_bound" not in parameter_info:
                            parameter_info["lower_bound"] = value
                        else:
                            if value < parameter_info["lower_bound"]:
                                parameter_info["lower_bound"] = value
                                parameter_info["given_value"] = value
                        if "upper_bound" not in parameter_info:
                            parameter_info["upper_bound"] = value
                        else:
                            if value > parameter_info["upper_bound"]:
                                parameter_info["upper_bound"] = value
                    elif parameter_type == "categorical":
                        category = func_eval_list[i]["tuning_parameter"][parameter_name]
                        if "categories" not in parameter_info:
                            parameter_info["categories"] = [category]
                            parameter_info["given_value"] = category
                        else:
                            if category not in parameter_info["categories"]:
                                parameter_info["categories"].append(category)
                    else:
                        pass

                for output_info in tuning_problem_info["output_info"]:
                    output_name = output_info["output_name"]
                    output_type = output_info["output_type"]

                    if output_type == "integer":
                        value = func_eval_list[i]["evaluation_result"][output_name]
                        if "lower_bound" not in output_info:
                            output_info["lower_bound"] = value
                        else:
                            if value < output_info["lower_bound"]:
                                output_info["lower_bound"] = value
                        if "upper_bound" not in output_info:
                            output_info["upper_bound"] = value
                        else:
                            if value > output_info["upper_bound"]:
                                output_info["upper_bound"] = value
                    if output_type == "real":
                        value = func_eval_list[i]["evaluation_result"][output_name]
                        if "lower_bound" not in output_info:
                            output_info["lower_bound"] = round(value-0.005,2)
                        else:
                            if round(value-0.005, 2) < output_info["lower_bound"]:
                                output_info["lower_bound"] = round(value-0.005, 2)
                        if "upper_bound" not in output_info:
                            output_info["upper_bound"] = round(value+0.005, 2)
                        else:
                            if round(value+0.005, 2) > output_info["upper_bound"]:
                                output_info["upper_bound"] = round(value+0.005, 2)

                    elif output_type == "categorical":
                        category = func_eval_list[i]["evaluation_result"][output_name]
                        if "categories" not in output_info:
                            output_info["categories"] = [category]
                        else:
                            if category not in output_info["categories"]:
                                output_info["categories"].append(category)
                    else:
                        pass

                input_task = {}
                input_task.update(func_eval_list[i]["task_parameter"])
                if "constants" in func_eval_list[i]:
                    input_task.update(func_eval_list[i]["constants"])

                if input_task not in input_task_avail:
                    input_task_avail.append(input_task)

            context = {
                "tuning_problem_unique_name": tuning_problem_unique_name,
                "tuning_problem": tuning_problem,
                "output_options" : output_options,
                "input_task_avail" : input_task_avail,
                "function_evaluations" : func_eval_list,
                "num_func_eval" : num_func_eval,
                "machine_configurations_list" : json.dumps(machine_configurations_list),
                "software_configurations_list" : json.dumps(software_configurations_list),
                "output_options" : json.dumps(output_options),
                "user_configurations_list" : json.dumps(user_configurations_list)
            }

            return render(request, 'repo/model-build-prediction.html', context)
        else:
            surrogate_model_uids = surrogate_model_uids.split(",")
            historydb = HistoryDB_MongoDB()
            tuning_problem = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
            tuning_problem_info = historydb.get_tuning_problem_info(tuning_problem_unique_name)
            surrogate_models = historydb.load_surrogate_models_by_uids(surrogate_model_uids)
            num_surrogate_models = len(surrogate_models)

            print ("======== Surrogate Model Dashboard ========")
            print ("tuning_problem_unique_name: ", tuning_problem_unique_name)
            print ("tuning_problem: ", tuning_problem)
            print ("Surrogate Model UIDs: ", surrogate_model_uids)
            print ("SURROGATE_MODEL")
            print (surrogate_models)

            model_data_list = {}

            for surrogate_model in surrogate_models:
                model_data = {}

                model_data["surrogate_model_uid"] = surrogate_model["uid"]

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
                    if task_parameter["type"] == "int" or task_parameter["type"] == "real":
                        task_parameter["lower_bound"] = task_space["lower_bound"]
                        task_parameter["upper_bound"] = task_space["upper_bound"]
                    elif task_parameter["type"] == "categorical":
                        task_parameter["categories"] = task_space["categories"]
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
                    if tuning_parameter["type"] == "int" or tuning_parameter["type"] == "real":
                        tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
                        tuning_parameter["upper_bound"] = parameter_space["upper_bound"]
                        tuning_parameter["value"] = tuning_parameter["lower_bound"]
                    elif tuning_parameter["type"] == "categorical":
                        tuning_parameter["categories"] = parameter_space["categories"]
                        tuning_parameter["value"] = str(tuning_parameter["categories"][0])
                    for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                        if parameter_info["parameter_name"] == tuning_parameter["name"]:
                            tuning_parameter["description"] = parameter_info["parameter_description"]

                    model_data["tuning_parameters"].append(tuning_parameter)

                model_output = {}
                model_output["name"] = surrogate_model["objective"]["name"]
                model_output["type"] = surrogate_model["objective"]["type"]
                if model_output["type"] == "int" or model_output["type"] == "real":
                    model_output["lower_bound"] = surrogate_model["objective"]["lower_bound"]
                    model_output["upper_bound"] = surrogate_model["objective"]["upper_bound"]
                elif model_output["type"] == "categorical":
                    model_output["categories"] = surrogate_model["objective"]["categories"]
                for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                    if output_info["output_name"] == model_output["name"]:
                        model_output["description"] = output_info["output_description"]
                model_output["result"] = "-"
                model_data["model_output"] = model_output

                model_data["output_parameters"] = []
                for output_space in surrogate_model["output_space"]:
                    output_parameter = {}
                    output_parameter["name"] = output_space["name"]
                    output_parameter["type"] = output_space["type"]
                    if output_parameter["type"] == "int" or output_parameter["type"] == "real":
                        output_parameter["lower_bound"] = output_space["lower_bound"]
                        output_parameter["upper_bound"] = output_space["upper_bound"]
                    elif output_parameter["type"] == "categorical":
                        output_parameter["categories"] = output_space["categories"]
                    for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                        if output_info["output_name"] == output_parameter["name"]:
                            output_parameter["description"] = output_info["output_description"]
                    model_data["output_parameters"].append(output_parameter)

                model_data["constants"] = []
                for constant_variable in tuning_problem_info["tuning_problem_info"]["constant_info"]:
                    model_data["constants"].append({
                                "name": constant_variable["constant_name"],
                                "type": constant_variable["constant_type"],
                                "description": constant_variable["constant_description"]})

                model_data["objective"] = surrogate_model["objective"]

                model_data_list[model_data["objective"]["name"]] = model_data

            context = {
                    "tuning_problem_unique_name" : tuning_problem_unique_name,
                    "surrogate_model_uids" : surrogate_model_uids,
                    "model_data" : model_data_list
                    }

            return render(request, 'repo/model-prediction.html', context)

    def post(self, request, **kwargs):

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")
        surrogate_model_uids = request.GET.get("surrogate_model_uids", "")

        if surrogate_model_uids == "":
            tuning_problem = request.GET.get("tuning_problem", "{}")
            modeler = request.POST["modeler"]
            tuning_parameter_range = request.POST.getlist("tuning_parameter_range")
            tuning_parameter_given = request.POST.getlist("tuning_parameter_given")
            output_parameter_range = request.POST.getlist("output_parameter_range")

            historydb = HistoryDB_MongoDB()

            tuning_problem_loaded = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
            tuning_problem = copy.deepcopy(tuning_problem_loaded)
            tuning_problem_info = tuning_problem["tuning_problem_info"]

            machine_configurations_list = json.loads(request.GET.get("machine_configurations_list", "{}"))
            software_configurations_list = json.loads(request.GET.get("software_configurations_list", "{}"))
            output_options = json.loads(request.GET.get("output_options", "[]"))
            user_configurations_list = json.loads(request.GET.get("user_configurations_list", "{}"))
            user_email = request.user.email if request.user.is_authenticated else ""
            search_options = json.loads(request.GET.get("search_options", "[]"))

            input_task_avail = []
            input_task_avail.append(ast.literal_eval(request.POST["input_task"]))

            func_eval_list = historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    output_options = output_options,
                    user_configurations_list = user_configurations_list,
                    user_email = user_email)
            num_func_eval = len(func_eval_list)
            for i in range(num_func_eval):
                func_eval_list[i]["id"] = i

                for parameter_info in tuning_problem_info["parameter_info"]:
                    parameter_name = parameter_info["parameter_name"]
                    parameter_type = parameter_info["parameter_type"]

                    if parameter_type == "integer" or parameter_type == "real":
                        value = func_eval_list[i]["tuning_parameter"][parameter_name]
                        if "lower_bound" not in parameter_info:
                            parameter_info["lower_bound"] = value
                        else:
                            if value < parameter_info["lower_bound"]:
                                parameter_info["lower_bound"] = value
                        if "upper_bound" not in parameter_info:
                            parameter_info["upper_bound"] = value
                        else:
                            if value > parameter_info["upper_bound"]:
                                parameter_info["upper_bound"] = value
                    elif parameter_type == "categorical":
                        category = func_eval_list[i]["tuning_parameter"][parameter_name]
                        if "categories" not in parameter_info:
                            parameter_info["categories"] = [category]
                        else:
                            if category not in parameter_info["categories"]:
                                parameter_info["categories"].append(category)
                    else:
                        pass

                for output_info in tuning_problem_info["output_info"]:
                    output_name = output_info["output_name"]
                    output_type = output_info["output_type"]

                    if output_type == "integer":
                        value = func_eval_list[i]["evaluation_result"][output_name]
                        if "lower_bound" not in output_info:
                            output_info["lower_bound"] = value
                        else:
                            if value < output_info["lower_bound"]:
                                output_info["lower_bound"] = value
                        if "upper_bound" not in output_info:
                            output_info["upper_bound"] = value
                        else:
                            if value > output_info["upper_bound"]:
                                output_info["upper_bound"] = value
                    if output_type == "real":
                        value = func_eval_list[i]["evaluation_result"][output_name]
                        if "lower_bound" not in output_info:
                            output_info["lower_bound"] = round(value-0.005,2)
                        else:
                            if round(value-0.005, 2) < output_info["lower_bound"]:
                                output_info["lower_bound"] = round(value-0.005, 2)
                        if "upper_bound" not in output_info:
                            output_info["upper_bound"] = round(value+0.005, 2)
                        else:
                            if round(value+0.005, 2) > output_info["upper_bound"]:
                                output_info["upper_bound"] = round(value+0.005, 2)

                    elif output_type == "categorical":
                        category = func_eval_list[i]["evaluation_result"][output_name]
                        if "categories" not in output_info:
                            output_info["categories"] = [category]
                        else:
                            if category not in output_info["categories"]:
                                output_info["categories"].append(category)
                    else:
                        pass

                input_task = {}
                input_task.update(func_eval_list[i]["task_parameter"])
                if "constants" in func_eval_list[i]:
                    input_task.update(func_eval_list[i]["constants"])

                if input_task not in input_task_avail:
                    input_task_avail.append(input_task)

            print ("input_task_avail: ", input_task_avail)
            print ("machine_configurations: ", machine_configurations_list)
            print ("software_configurations: ", software_configurations_list)
            print ("tuning_parameter_range: ", tuning_parameter_range)
            print ("tuning_parameter_given: ", tuning_parameter_given)
            print ("tuning_parameter_range_type: ", type(tuning_parameter_range))
            print ("tuning_parameter_given_type: ", type(tuning_parameter_given))
            print ("tuning_problem: ", tuning_problem)

            input_task = ast.literal_eval(request.POST["input_task"])
            Igiven = []
            print ("input_task: ", input_task)
            print ("input_task_type: ", type(input_task))

            problem_space = {
                "input_space": [],
                "parameter_space": [],
                "output_space": [],
                "constants": []
            }

            for task_info in tuning_problem_info["task_info"]:
                task_name = task_info["task_name"]
                task_type = task_info["task_type"]
                print ("task_name: ", task_name)

                task_value = input_task[task_name]
                Igiven.append(task_value)
                input_task.pop(task_name)
                print ("task_chosen: name: ", task_name, " vaule: ", task_value)

                if task_type == "integer" or task_type == "real":
                    problem = {
                        "name": task_name,
                        "type": task_type,
                        "transformer": "normalize",
                        "lower_bound": task_value,
                        "upper_bound": task_value+1
                    }
                    problem_space["input_space"].append(problem)
                elif task_type == "categorical":
                    problem = {
                        "name": task_name,
                        "type": task_type,
                        "transformer": "onehot",
                        "categories": [task_value]
                    }
                    problem_space["input_space"].append(problem)
            constants = input_task
            problem_space["constants"].append(constants)

            pGiven = {}

            for i in range(len(tuning_problem_info["parameter_info"])):
                parameter_info = tuning_problem_info["parameter_info"][i]

                parameter_name = parameter_info["parameter_name"]
                parameter_type = parameter_info["parameter_type"]

                parameter_range = ast.literal_eval(tuning_parameter_range[i])
                parameter_given = ast.literal_eval(tuning_parameter_given[i])

                pGiven[parameter_name] = parameter_given

                tuning_problem["tuning_problem_info"]["parameter_info"][i]["given_value"] = parameter_given

                if parameter_type == "integer" or parameter_type == "real":
                    problem = {
                        "name": parameter_name,
                        "type": parameter_type,
                        "transformer": "normalize",
                        "lower_bound": parameter_range[0],
                        "upper_bound": parameter_range[-1]
                    }
                    problem_space["parameter_space"].append(problem)

                elif parameter_type == "categorical":
                    problem = {
                        "name": parameter_name,
                        "type": parameter_type,
                        "transformer": "onehot",
                        "categories": parameter_range
                    }
                    problem_space["parameter_space"].append(problem)

            #for output_info in tuning_problem_info["output_info"]:
            for i in range(len(tuning_problem_info["output_info"])):
                output_info = tuning_problem_info["output_info"][i]
                output_name = output_info["output_name"]
                output_type = output_info["output_type"]
                if output_type == "integer" or output_type == "real":
                    problem = {
                        "name": output_name,
                        "type": output_type,
                        "transformer": "normalize",
                        "lower_bound": output_info["lower_bound"],
                        "upper_bound": output_info["upper_bound"]
                    }
                    problem_space["output_space"].append(problem)
                else:
                    problem = {
                        "name": output_name,
                        "type": output_type,
                        "transformer": "onehot",
                        "categories": output_info["categories"]
                    }
                    problem_space["output_space"].append(problem)

                output_parameter_range = ast.literal_eval(output_parameter_range[i])
                func_eval_list_filtered = []
                #copy.deepcopy(func_eval_list)
                for func_eval in func_eval_list:
                    if output_type == "integer" or output_type == "real":
                        if func_eval["evaluation_result"][output_name] >= output_parameter_range[0] and\
                           func_eval["evaluation_result"][output_name] <= output_parameter_range[-1]:
                            func_eval_list_filtered.append(func_eval)
                        #else:
                        #    print ("filtered: ", func_eval)
                    elif output_type == "categorical":
                        if func_eval["evaluation_result"][output_name] in output_parameter_range:
                            func_eval_list_filtered.append(func_eval)
                        #else:
                        #    print ("filtered: ", func_eval)

                # import gptune
                # ret = gptune.PredictOutput(problem_space=problem_space,
                #         modeler=modeler,
                #         input_task=Igiven,
                #         input_parameter=pGiven,
                #         function_evaluations=func_eval_list)
                # print("ret: ", ret)
                # output_info["result"] = ret[output_name][0][0] #parameter_given
                # output_info["result_std"] = ret[output_name+"_var"][0][0] #parameter_given

            context = {
                "tuning_problem_unique_name": tuning_problem_unique_name,
                "tuning_problem": tuning_problem,
                "output_options" : output_options,
                "input_task_avail" : input_task_avail,
                "function_evaluations" : func_eval_list,
                "num_func_eval" : num_func_eval,
                "machine_configurations_list" : json.dumps(machine_configurations_list),
                "software_configurations_list" : json.dumps(software_configurations_list),
                "output_options" : json.dumps(output_options),
                "user_configurations_list" : json.dumps(user_configurations_list)
            }

            return render(request, 'repo/model-build-prediction.html', context)

        else:
            tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name")
            surrogate_model_uids = request.GET.get('surrogate_model_uids')
            print ("tuning_problem_unique_name: ", tuning_problem_unique_name)
            print ("Surrogate Model UIDs: ", surrogate_model_uids)

            historydb = HistoryDB_MongoDB()
            tuning_problem = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
            tuning_problem_info = historydb.get_tuning_problem_info(tuning_problem_unique_name)

            task_parameter_names = request.POST.getlist('task_parameter_name')
            task_parameter_types = request.POST.getlist('task_parameter_type')
            task_parameters = request.POST.getlist('task_parameter')
            tuning_parameter_names = request.POST.getlist('tuning_parameter_name')
            tuning_parameter_types = request.POST.getlist('tuning_parameter_type')
            tuning_parameters = request.POST.getlist('tuning_parameter')
            #output_names = request.POST.getlist('output_name')
            output_name = request.POST['output_parameter_name']
            #output = request.POST.getlist('output')

            print ("surrogate_model_uids: ", surrogate_model_uids)
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
                elif task_parameter_types[i] == "real":
                    point[task_parameter_names[i]] = float(task_parameters[i])
                elif task_parameter_types[i] == "categorical":
                    point[task_parameter_names[i]] = task_parameters[i]
            for i in range(len(tuning_parameter_names)):
                if tuning_parameter_types[i] == "int":
                    point[tuning_parameter_names[i]] = int(tuning_parameters[i])
                elif tuning_parameter_types[i] == "float":
                    point[tuning_parameter_names[i]] = float(tuning_parameters[i])
                elif tuning_parameter_types[i] == "real":
                    point[tuning_parameter_names[i]] = float(tuning_parameters[i])
                elif tuning_parameter_types[i] == "categorical":
                    point[tuning_parameter_names[i]] = tuning_parameters[i]

            print ("MODEL POINT: ", point)

            surrogate_models = historydb.load_surrogate_models_by_uids(surrogate_model_uids)

            model_data_list = {}

            for surrogate_model in surrogate_models:
                tuning_problem_name = surrogate_model["tuning_problem_name"]
                os.system("rm -rf .gptune")
                os.system("mkdir -p .gptune")
                json_data = {}
                json_data["tuning_problem_name"] = tuning_problem_name
                with open(".gptune/meta.json", "w") as f_out:
                    json.dump(json_data, f_out, indent=2)

                from gptune import CreateGPTuneFromModelData
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

                print ("SURROGATE_MODEL")
                print (surrogate_model)

                model_data = {}

                #model_data["surrogate_model_uid"] = surrogate_model["uid"]

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
                    if task_parameter["type"] == "int" or task_parameter["type"] == "real":
                        task_parameter["lower_bound"] = task_space["lower_bound"]
                        task_parameter["upper_bound"] = task_space["upper_bound"]
                    elif task_parameter["type"] == "categorical":
                        task_parameter["categories"] = task_space["categories"]
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
                    if tuning_parameter["type"] == "int" or tuning_parameter["type"] == "real":
                        tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
                        tuning_parameter["upper_bound"] = parameter_space["upper_bound"]
                        tuning_parameter["value"] = tuning_parameter["lower_bound"]
                    elif tuning_parameter["type"] == "categorical":
                        tuning_parameter["categories"] = parameter_space["categories"]
                        tuning_parameter["value"] = str(tuning_parameter["categories"][0])
                    for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                        if parameter_info["parameter_name"] == tuning_parameter["name"]:
                            tuning_parameter["description"] = parameter_info["parameter_description"]

                    model_data["tuning_parameters"].append(tuning_parameter)

                model_output = {}
                model_output["name"] = surrogate_model["objective"]["name"]
                model_output["type"] = surrogate_model["objective"]["type"]
                if model_output["type"] == "int" or model_output["type"] == "real":
                    model_output["lower_bound"] = surrogate_model["objective"]["lower_bound"]
                    model_output["upper_bound"] = surrogate_model["objective"]["upper_bound"]
                elif model_output["type"] == "categorical":
                    model_output["categories"] = surrogate_model["objective"]["categories"]
                for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                    if output_info["output_name"] == model_output["name"]:
                        model_output["description"] = output_info["output_description"]
                model_output["result"] = round(ret[model_output["name"]][0][0],3)
                import math
                model_output["result_std"] = round(math.sqrt(ret[model_output["name"]+"_var"][0][0]),3)
                model_data["model_output"] = model_output

                model_data["output_parameters"] = []
                for output_space in surrogate_model["output_space"]:
                    output_parameter = {}
                    output_parameter["name"] = output_space["name"]
                    output_parameter["type"] = output_space["type"]
                    if output_parameter["type"] == "int" or output_parameter["type"] == "real":
                        output_parameter["lower_bound"] = output_space["lower_bound"]
                        output_parameter["upper_bound"] = output_space["upper_bound"]
                    elif output_parameter["type"] == "categorical":
                        output_parameter["categories"] = output_space["categories"]
                    for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                        if output_info["output_name"] == output_parameter["name"]:
                            output_parameter["description"] = output_info["output_description"]
                    model_data["output_parameters"].append(output_parameter)

                model_data["constants"] = []
                for constant_variable in tuning_problem_info["tuning_problem_info"]["constant_info"]:
                    model_data["constants"].append({
                                "name": constant_variable["constant_name"],
                                "type": constant_variable["constant_type"],
                                "description": constant_variable["constant_description"]})

                model_data["objective"] = surrogate_model["objective"]

                model_data_list[model_data["objective"]["name"]] = model_data

            print ("MODEL_DATA: ", model_data_list)

            context = {
                    "tuning_problem_unique_name" : tuning_problem_unique_name,
                    "surrogate_model_uids" : surrogate_model_uids,
                    "model_data" : model_data_list,
                    }

            return render(request, 'repo/model-prediction.html', context)

class AnalysisDashingParameter(TemplateView):

    def write_config_file(self,file_name,targets,arch,chart_type = 'sunburst'):
        config_dir = 'dashing/configs'
        if not os.path.isdir(config_dir):
            os.mkdir(config_dir)
        with open(config_dir + '/' + file_name, 'w') as txtfile:
            for target in targets:
                s = 'tuning_problem' + str(targets.index(target)) + ':'
                txtfile.write(s + '\n')
                s = '  data: '
                txtfile.write(s + '\n')
                s = '  tasks:'
                txtfile.write(s + '\n')
                s = '    - dashing.modules.resource_score.compute_rsm_task_all_regions'
                txtfile.write(s + '\n')
                s = '    - dashing.viz.sunburst3.sunburst'
                txtfile.write(s + '\n')
                s = '    - dashing.viz.linechart.raw_values_per_proc_config'
                txtfile.write(s + '\n')
                s = '  name:  \'' + target +'\''
                txtfile.write(s + '\n')
                s = '  target:  \'' + target +'\''
                txtfile.write(s + '\n')
                s = '  compute_target: dashing.modules.compute_target.compute_runtime'
                txtfile.write(s + '\n')
            s = '##############################'
            txtfile.write(s + '\n')

            txtfile.write('\n')

            s = 'main:'
            txtfile.write(s + '\n')  
            s = '  tasks:'
            txtfile.write(s + '\n')
            for target in targets:
                s = '    - tuning_problem' + str(targets.index(target))
                txtfile.write(s + '\n')
            s = '  arch: ' + arch + '\n'
            s += '  data_rescale: true\n'
            s += '  rsm_iters: 5000\n'
            s += '  rsm_print: false\n'
            s += '  rsm_use_nn_solver: true\n'
            s += '  use_belief: true\n'
            s += '  compat_labels: true\n'
            s += '  shorten_event_name: false\n'
            s += '  port: 7603\n'
            txtfile.write(s)

    def read_task_or_tuning_parameter(self, parameters, name):
        rows2 = []
        for parameter in parameters:
            row_dict = {}
            row_dict[''] = parameter
            for phase in self.phases:
                temp_list = []
                for function_eval in self.function_evaluations:
                    temp_list.append(function_eval[name][parameter])
                # print(type(temp_list[0]))
                if type(temp_list[0]) == str:
                    unique_values = list(set(temp_list))
                    new_list = []
                    for item in temp_list:
                        new_list.append(unique_values.index(item))
                    temp_list = []
                    temp_list.extend(new_list)
                temp_list_2 = [str(val) for val in temp_list]
                temp_row = ','.join(temp_list_2)
                row_dict[phase] = temp_row
            rows2.append(row_dict)
        return rows2

    def get(self, request, **kwargs):

        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")
        machine_configurations_list = json.loads(request.GET.get("machine_configurations_list", "{}"))
        software_configurations_list = json.loads(request.GET.get("software_configurations_list", "{}"))
        output_options = json.loads(request.GET.get("output_options", "[]"))
        user_configurations_list = json.loads(request.GET.get("user_configurations_list", "{}"))
        user_email = request.user.email if request.user.is_authenticated else ""
        search_options = json.loads(request.GET.get("search_options", "[]"))

        historydb = HistoryDB_MongoDB()

        self.function_evaluations = historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                machine_configurations_list = machine_configurations_list,
                software_configurations_list = software_configurations_list,
                output_options = output_options,
                user_configurations_list = user_configurations_list,
                user_email = user_email)
        
        has_counter_info = 'additional_output' in self.function_evaluations[0] and 'pmu' in self.function_evaluations[0]['additional_output']
        has_group_info = False
        if has_counter_info:
            tks = list(self.function_evaluations[0]['additional_output']['pmu'].keys())
            has_group_info = type(self.function_evaluations[0]['additional_output']['pmu'][tks[0]]) is dict

        self.phases = set()
 
        if has_counter_info and has_group_info:
            # Read about counter and grouping
            counter_classes = list((self.function_evaluations[0])['additional_output'].keys())
            for counter_class in counter_classes:
                temp_phase = list(self.function_evaluations[0]['additional_output'][counter_class].keys())
                self.phases.update(temp_phase)            

        task_params = []
        tuning_params = []
        # Read data about tuning and task parameters
        evaluation_results = list((self.function_evaluations[0])['evaluation_result'].keys())
        for task_param in list(self.function_evaluations[0]['task_parameter'].keys()):
            if type(self.function_evaluations[0]['task_parameter'][task_param]) is not str:
                task_params.append(task_param)
        for tuning_param in list(self.function_evaluations[0]['tuning_parameter'].keys()):
            if type(self.function_evaluations[0]['tuning_parameter'][tuning_param]) is not str:
                tuning_params.append(tuning_param)
        all_task_params = list(self.function_evaluations[0]['task_parameter'].keys())
        all_tuning_parmas = list(self.function_evaluations[0]['tuning_parameter'].keys())
        removed_task_params = list(set(all_task_params) - set(task_params))
        removed_tuning_params = list(set(all_tuning_parmas) - set(tuning_params))

        if not self.phases:
            self.phases.add("Single Phase")


        # print("Zayed evaluations" , evaluation_results)
        # Transformation countre data to dashing data format
        coloumns = ['']
        coloumns.extend(self.phases)

        new_dashing_df_2 = pd.DataFrame(columns=coloumns)

        # Read the tuning and task parameters
        rows2 = []
        rows2.extend(self.read_task_or_tuning_parameter(task_params, 'task_parameter'))
        rows2.extend(self.read_task_or_tuning_parameter(tuning_params,'tuning_parameter'))
        
        # Read the target metrices
        # n_n = []
        # n_n.append(evaluation_results[1])
        # evaluation_row = self.read_task_or_tuning_parameter(n_n,'evaluation_result')

        evaluation_row = self.read_task_or_tuning_parameter(evaluation_results,'evaluation_result')
        rows2.extend(evaluation_row)

        new_dashing_df_2 = pd.DataFrame(rows2)
        # for cols in new_dashing_df_2.columns:
        #     print("Zayed types: ")
        #     print(cols, type(cols))

        # Deciding on which architecture to use


        #####################################################################################
        self.write_config_file('tuning_task_params_problem' + '.yml',evaluation_results,'haswell-user')
        #####################################################################################

        #Architecture setup for user paramater analysis 
        resources_path = 'dashing/resources/haswell-user' 
        if not os.path.isdir(resources_path):
            os.mkdir(resources_path)

        with open(resources_path + '/native_all_filtered.txt', 'w') as txtfile:
            for tuning_param in tuning_params:
                txtfile.write(tuning_param + '\n')

        with open(resources_path + '/native_all_filtered.txt', 'a') as txtfile:
            for task_param in task_params:
                txtfile.write(task_param + '\n')
            for evaluation_result in evaluation_results:
                txtfile.write(evaluation_result + '\n')

        mapping = {}
        with open(resources_path + '/event_map.txt', 'w') as txtfile:
            mapping['TASK_PARAMS'] = []
            for task_param in task_params:
                txtfile.write(task_param + '=>' + 'TASK_PARAMS\n')
                mapping['TASK_PARAMS'].append(task_param)
            mapping['TUNING_PARAMS'] = []
            for tuning_param in tuning_params:
                txtfile.write(tuning_param + '=>' + 'TUNING_PARAMS\n')
                mapping['TUNING_PARAMS'].append(tuning_param)
                

        with open(resources_path + '/event_desc.csv', 'w') as txtfile:
                txtfile.write('')


        drvr = driver()

        # Calling the visualization for parameters analysis
        transformed_charts = []
        charts, group_imps_params, event_imps_params = drvr.main(os.getcwd() + '/dashing/configs/tuning_task_params_problem.yml', True, dataframe= new_dashing_df_2)
        
        # print('Zayed Here1 ', charts)

        for chart in charts:
            # print('Zayed Here1 ', len(charts))
            if chart is not None:
                chart3 = plot(chart,output_type="div")
                transformed_charts.append(chart3)
                # break
            # else:
            #     self.write_config_file('tuning_task_params_problem' + '.yml',[evaluation_results[charts.index(chart)]],'haswell-user', chart_type='linechart')
            #     charts2, null__, null_ = drvr.main(os.getcwd() + '/dashing/configs/tuning_task_params_problem.yml', True, dataframe= new_dashing_df_2)
            #     for chart_ in charts2:
            #         print('Zayed Here2 ', len(charts2))
            #         if chart_ is not None:
            #             chart3 = plot(chart_,output_type="div")
            #             transformed_charts.append(chart3)
            #             break



        # Reading event importances
        event_importances = []
        # for region in event_imps_params:
        #     for group in event_imps_params[region]:
        #         for event in event_imps_params[region][group]:
        #             row_dict = {}
        #             row_dict['counter_name'] = event
        #             row_dict['value'] = str(round(event_imps_params[region][group][event] * 100, 2)) + '%' 
        #             row_dict['region'] = region
        #             row_dict['groups'] = group
        #             event_importances.append(row_dict)

        # print("Zayed whoooooo ", self.phases, event_imps_params)
        for region in self.phases:
            for group in mapping:
                for event in mapping[group]:
                    row_dict = {}
                    row_dict['counter_name'] = event
                    if group in event_imps_params[region].keys() and event in event_imps_params[region][group].keys():
                        row_dict['value'] = str(round(event_imps_params[region][group][event] * 100, 2)) + '%' 
                    else:
                        row_dict['value'] = '0.0%'
                    row_dict['region'] = region
                    row_dict['groups'] = group
                    event_importances.append(row_dict)               

        context = { "function_evaluations" : self.function_evaluations,
                    "tuning_problem_name" : tuning_problem_unique_name,
                    "chart2" : transformed_charts,
                    "counters" : event_importances,
                    "removed_task_params" : removed_task_params,
                    "removed_tuning_params" : removed_tuning_params,
                    "all_task_params" : all_task_params,
                    "all_tuning_params" : all_tuning_parmas
        }

        return render(request, 'repo/analysis-dashing-parameter.html', context)
        
    def post(self, request, **kwargs):

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        # placeholder
        context = {}
        return render(request, 'repo/analysis-dashing-parameter.html', context)

class AnalysisDashingCounter(TemplateView):

    def write_config_file(self,file_name,targets,arch):
        # print("Zayeddddddddddddddddd ", targets)
        config_dir = 'dashing/configs'
        if not os.path.isdir(config_dir):
            os.mkdir(config_dir)
        with open(config_dir + '/' + file_name, 'w') as txtfile:
            for target in targets:
                s = 'tuning_problem' + str(targets.index(target)) + ':'
                txtfile.write(s + '\n')
                s = '  data: '
                txtfile.write(s + '\n')
                s = '  tasks:'
                txtfile.write(s + '\n')
                s = '    - dashing.modules.resource_score.compute_rsm_task_all_regions'
                txtfile.write(s + '\n')
                s = '    - dashing.viz.sunburst3.sunburst'
                txtfile.write(s + '\n')
                s = '  name:  \'' + target +'\''
                txtfile.write(s + '\n')
                s = '  target:  \'' + target +'\''
                txtfile.write(s + '\n')
                s = '  compute_target: dashing.modules.compute_target.compute_runtime'
                txtfile.write(s + '\n')
                s = '##############################'
                txtfile.write(s + '\n')

            txtfile.write('\n')

            s = 'main:'
            txtfile.write(s + '\n')  
            s = '  tasks:'
            txtfile.write(s + '\n')
            # s = '    - tuning_problem'
            # txtfile.write(s + '\n')
            for target in targets:
                s = '    - tuning_problem' + str(targets.index(target))
                txtfile.write(s + '\n')
            s = '  arch: ' + arch + '\n'
            s += '  data_rescale: true\n'
            s += '  rsm_iters: 500\n'
            s += '  rsm_print: false\n'
            s += '  rsm_use_nn_solver: true\n'
            # s += '  save_compat: true\n'
            s += '  use_belief: true\n'
            s += '  compat_labels: true\n'
            s += '  shorten_event_name: false\n'
            s += '  port: 7603\n'
            s += '  rsm_cpu_count: 4\n' 
            txtfile.write(s)

    def read_target_rows(self, parameters, name):
        rows2 = []
        for parameter in parameters:
            row_dict = {}
            row_dict[''] = parameter
            for phase in self.phases:
                temp_list = []
                for function_eval in self.function_evaluations:
                    temp_list.append(function_eval[name][parameter])
                temp_list_2 = [str(val) for val in temp_list]
                temp_row = ','.join(temp_list_2)
                row_dict[phase] = temp_row
            rows2.append(row_dict)
        return rows2

    def get(self, request, **kwargs):

        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")
        machine_configurations_list = json.loads(request.GET.get("machine_configurations_list", "{}"))
        software_configurations_list = json.loads(request.GET.get("software_configurations_list", "{}"))
        output_options = json.loads(request.GET.get("output_options", "[]"))
        user_configurations_list = json.loads(request.GET.get("user_configurations_list", "{}"))
        user_email = request.user.email if request.user.is_authenticated else ""
        search_options = json.loads(request.GET.get("search_options", "[]"))

        historydb = HistoryDB_MongoDB()

        self.function_evaluations = historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                machine_configurations_list = machine_configurations_list,
                software_configurations_list = software_configurations_list,
                output_options = output_options,
                user_configurations_list = user_configurations_list,
                user_email = user_email)
        
        has_counter_info = 'additional_output' in self.function_evaluations[0] and 'pmu' in self.function_evaluations[0]['additional_output']
        has_group_info = False
        if has_counter_info:
            tks = list(self.function_evaluations[0]['additional_output']['pmu'].keys())
            has_group_info = type(self.function_evaluations[0]['additional_output']['pmu'][tks[0]]) is dict

        self.phases = set()
        counter_groups = set()
        counters = set()
        mapping_set = set()
        mapping = {}
 
        if has_counter_info and has_group_info:
            # Read about counter and grouping
            counter_classes = list((self.function_evaluations[0])['additional_output'].keys())
            for counter_class in counter_classes:
                temp_phase = list(self.function_evaluations[0]['additional_output'][counter_class].keys())
                self.phases.update(temp_phase)
                for phase in temp_phase:
                    temp_counter_groups = list(self.function_evaluations[0]['additional_output'][counter_class][phase].keys())
                    counter_groups.update(temp_counter_groups)
                    for counter_group in temp_counter_groups:
                        temp_counters = list(self.function_evaluations[0]['additional_output'][counter_class][phase][counter_group].keys())
                        counters.update(temp_counters)
                        for counter in temp_counters:
                            mapping_set.add(counter + '=>' + counter_group)
                            if counter_group not in mapping.keys():
                                mapping[counter_group] = []
                            mapping[counter_group].append(counter)
        if has_counter_info and (not has_group_info):
            counter_classes = list((self.function_evaluations[0])['additional_output'].keys())
            counters = tks


        # Read data about tuning and task parameters
        evaluation_results = list((self.function_evaluations[0])['evaluation_result'].keys())
        
        if not self.phases:
            self.phases.add("Single Phase")

        # Transformation countre data to dashing data format
        coloumns = ['']
        coloumns.extend(self.phases)
        if has_counter_info and has_group_info:
            new_dashing_df = pd.DataFrame(columns=coloumns)
            rows = []
            for feat in counters:
                row_dict = {}
                row_dict[''] = feat
                for phase in self.phases:
                    temp_list = []
                    for function_eval in self.function_evaluations:
                        for counter_class in counter_classes:
                            for counter_group in counter_groups:
                                if feat in function_eval['additional_output'][counter_class][phase][counter_group].keys():
                                    temp_list.append(function_eval['additional_output'][counter_class][phase][counter_group][feat])
                    temp_list_2 = [str(val) for val in temp_list]
                    temp_row = ','.join(temp_list_2)
                    row_dict[phase] = temp_row
                rows.append(row_dict)
        
        if has_counter_info and (not has_group_info):
            new_dashing_df = pd.DataFrame(columns=coloumns)
            rows = []
            for feat in counters:
                row_dict = {}
                row_dict[''] = feat
                for phase in self.phases:
                    temp_list = []
                    for function_eval in self.function_evaluations:
                        for counter_class in counter_classes:
                                if feat in function_eval['additional_output'][counter_class].keys():
                                    temp_list.append(function_eval['additional_output'][counter_class][feat])
                    temp_list_2 = [str(val) for val in temp_list]
                    temp_row = ','.join(temp_list_2)
                    row_dict[phase] = temp_row
                rows.append(row_dict)

        
        # Read the target metrices
        evaluation_row = self.read_target_rows(evaluation_results,'evaluation_result')
        if has_counter_info:
            rows.extend(evaluation_row)

        # Covert to use
        if has_counter_info: 
            new_dashing_df = pd.DataFrame(rows)

        # Deciding on which architecture to use
        if has_counter_info:
            arch_file = 'haswell3'
            if len(counter_groups) > 1:
                arch_file = 'defined'
            self.write_config_file('counter_importance_problem' + '.yml',evaluation_results,arch_file)

        #Architecture setup for counter analysis 
        if has_counter_info:
            resources_path = 'dashing/resources/' + arch_file 
            with open(resources_path + '/native_all_filtered.txt', 'w') as txtfile:
                for counter in counters:
                    txtfile.write(counter + '\n')
        
            if arch_file == 'defined':
                with open(resources_path + '/architecture_groups.txt', 'w') as txtfile:
                    s = 'UNDEFINED,0\n'
                    for counter_group in counter_groups:
                        s+= counter_group + ',0\n'
                    txtfile.write(s)

                with open(resources_path + '/event_map.txt', 'w') as txtfile:
                    mapping = '\n'.join(list(mapping_set))
                    txtfile.write(mapping + '\n')

        drvr = driver()

        # Calling the visualization for counter analysis 
        transformed_charts = []
        if has_counter_info:
            charts, group_imps_counter, event_imps_counter = drvr.main(os.getcwd() + '/dashing/configs/counter_importance_problem.yml', True, dataframe= new_dashing_df)
            for chart in charts:
                if chart is not None:
                    chart2 = plot(chart,output_type="div")
                    transformed_charts.append(chart2)         
                else:
                    chart2 = None
        else:
            transformed_charts = None

        # Reading the group importances
        group_importances = []
        if has_counter_info:
            for region in group_imps_counter:
                for resource in group_imps_counter[region]:
                    row_dict = {}
                    row_dict['group_name'] = resource
                    row_dict['value'] = str(round(group_imps_counter[region][resource] * 100 , 2)) + '%'
                    row_dict['region'] = region
                    group_importances.append(row_dict)

        # if has_counter_info:
        #     for region in self.phases:
        #         for counter_group in counter_groups:
        #             print(" Zayed zeros ", region, counter_group)
        #             row_dict = {}
        #             row_dict['group_name'] = counter_group
        #             if region in group_imps_counter.keys() and counter_group in group_imps_counter[region].keys(): 
        #                 row_dict['value'] = str(round(group_imps_counter[region][counter_group] * 100 , 2)) + '%'
        #             else:
        #                 row_dict['value'] = '0.0%'
        #             row_dict['region'] = region
        #             group_importances.append(row_dict)


        # Reading event importances
        event_importances = []
        if has_counter_info:
            for region in event_imps_counter:
                for group in event_imps_counter[region]:
                    for event in event_imps_counter[region][group]:
                        row_dict = {}
                        row_dict['counter_name'] = event
                        row_dict['value'] = str(round(event_imps_counter[region][group][event] * 100, 2)) + '%' 
                        row_dict['region'] = region
                        row_dict['groups'] = group
                        event_importances.append(row_dict)

        context = { "function_evaluations" : self.function_evaluations,
                    "tuning_problem_name" : tuning_problem_unique_name,
                    "chart" : transformed_charts,
                    "groups" : group_importances,
                    "counters" : event_importances
        }

        return render(request, 'repo/analysis-dashing-counter.html', context)
        
    def post(self, request, **kwargs):

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        # placeholder
        context = {}
        return render(request, 'repo/analysis-dashing-counter.html', context)

class SADashboard(TemplateView):

    def get(self, request, **kwargs):

        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")
        surrogate_model_uids = request.GET.get("surrogate_model_uids", "")

        if surrogate_model_uids == "":
            print ("No surrogate model is given. Need to build a surrogate model.")
            historydb = HistoryDB_MongoDB()

            tuning_problem_loaded = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
            tuning_problem = copy.deepcopy(tuning_problem_loaded)
            tuning_problem_info = tuning_problem["tuning_problem_info"]

            machine_configurations_list = json.loads(request.GET.get("machine_configurations_list", "{}"))
            software_configurations_list = json.loads(request.GET.get("software_configurations_list", "{}"))
            output_options = json.loads(request.GET.get("output_options", "[]"))
            user_configurations_list = json.loads(request.GET.get("user_configurations_list", "{}"))
            user_email = request.user.email if request.user.is_authenticated else ""
            search_options = json.loads(request.GET.get("search_options", "[]"))

            input_task_avail = []

            func_eval_list = historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    output_options = output_options,
                    user_configurations_list = user_configurations_list,
                    user_email = user_email)
            num_func_eval = len(func_eval_list)
            for i in range(num_func_eval):
                func_eval_list[i]["id"] = i

                for parameter_info in tuning_problem_info["parameter_info"]:
                    parameter_name = parameter_info["parameter_name"]
                    parameter_type = parameter_info["parameter_type"]

                    if parameter_type == "integer" or parameter_type == "real":
                        value = func_eval_list[i]["tuning_parameter"][parameter_name]
                        if "lower_bound" not in parameter_info:
                            parameter_info["lower_bound"] = value
                        else:
                            if value < parameter_info["lower_bound"]:
                                parameter_info["lower_bound"] = value
                        if "upper_bound" not in parameter_info:
                            parameter_info["upper_bound"] = value
                        else:
                            if value > parameter_info["upper_bound"]:
                                parameter_info["upper_bound"] = value
                    elif parameter_type == "categorical":
                        category = func_eval_list[i]["tuning_parameter"][parameter_name]
                        if "categories" not in parameter_info:
                            parameter_info["categories"] = [category]
                        else:
                            if category not in parameter_info["categories"]:
                                parameter_info["categories"].append(category)
                    else:
                        pass

                for output_info in tuning_problem_info["output_info"]:
                    output_name = output_info["output_name"]
                    output_type = output_info["output_type"]

                    if output_type == "integer":
                        value = func_eval_list[i]["evaluation_result"][output_name]
                        if "lower_bound" not in output_info:
                            output_info["lower_bound"] = value
                        else:
                            if value < output_info["lower_bound"]:
                                output_info["lower_bound"] = value
                        if "upper_bound" not in output_info:
                            output_info["upper_bound"] = value
                        else:
                            if value > output_info["upper_bound"]:
                                output_info["upper_bound"] = value
                    if output_type == "real":
                        value = func_eval_list[i]["evaluation_result"][output_name]
                        if "lower_bound" not in output_info:
                            output_info["lower_bound"] = round(value-0.005,2)
                        else:
                            if round(value-0.005, 2) < output_info["lower_bound"]:
                                output_info["lower_bound"] = round(value-0.005, 2)
                        if "upper_bound" not in output_info:
                            output_info["upper_bound"] = round(value+0.005, 2)
                        else:
                            if round(value+0.005, 2) > output_info["upper_bound"]:
                                output_info["upper_bound"] = round(value+0.005, 2)

                    elif output_type == "categorical":
                        category = func_eval_list[i]["evaluation_result"][output_name]
                        if "categories" not in output_info:
                            output_info["categories"] = [category]
                        else:
                            if category not in output_info["categories"]:
                                output_info["categories"].append(category)
                    else:
                        pass

                input_task = {}
                input_task.update(func_eval_list[i]["task_parameter"])
                if "constants" in func_eval_list[i]:
                    input_task.update(func_eval_list[i]["constants"])

                if input_task not in input_task_avail:
                    input_task_avail.append(input_task)

            context = {
                "tuning_problem_unique_name": tuning_problem_unique_name,
                "tuning_problem": tuning_problem,
                "output_options" : output_options,
                "input_task_avail" : input_task_avail,
                "function_evaluations" : func_eval_list,
                "num_func_eval" : num_func_eval,
                "machine_configurations_list" : json.dumps(machine_configurations_list),
                "software_configurations_list" : json.dumps(software_configurations_list),
                "output_options" : json.dumps(output_options),
                "user_configurations_list" : json.dumps(user_configurations_list)
            }

            return render(request, 'repo/model-build-sadashboard.html', context)
        else:
            surrogate_model_uids = surrogate_model_uids.split(",")

            historydb = HistoryDB_MongoDB()
            tuning_problem = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
            tuning_problem_info = historydb.get_tuning_problem_info(tuning_problem_unique_name)
            surrogate_models = historydb.load_surrogate_models_by_uids(surrogate_model_uids)
            num_surrogate_models = len(surrogate_models)

            print ("======== Surrogate Model Dashboard ========")
            print ("tuning_problem_unique_name: ", tuning_problem_unique_name)
            print ("tuning_problem: ", tuning_problem)
            print ("Surrogate Model UIDs: ", surrogate_model_uids)
            print ("SURROGATE_MODEL")
            print (surrogate_models)

            model_data_list = {}

            for surrogate_model in surrogate_models:
                model_data = {}

                model_data["surrogate_model_uid"] = surrogate_model["uid"]

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
                    if task_parameter["type"] == "int" or task_parameter["type"] == "real":
                        task_parameter["lower_bound"] = task_space["lower_bound"]
                        task_parameter["upper_bound"] = task_space["upper_bound"]
                    elif task_parameter["type"] == "categorical":
                        task_parameter["categories"] = task_space["categories"]
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
                    if tuning_parameter["type"] == "int" or tuning_parameter["type"] == "real":
                        tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
                        tuning_parameter["upper_bound"] = parameter_space["upper_bound"]
                        tuning_parameter["value"] = tuning_parameter["lower_bound"]
                    elif tuning_parameter["type"] == "categorical":
                        tuning_parameter["categories"] = parameter_space["categories"]
                        tuning_parameter["value"] = str(tuning_parameter["categories"][0])
                    for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                        if parameter_info["parameter_name"] == tuning_parameter["name"]:
                            tuning_parameter["description"] = parameter_info["parameter_description"]

                    model_data["tuning_parameters"].append(tuning_parameter)

                model_output = {}
                model_output["name"] = surrogate_model["objective"]["name"]
                model_output["type"] = surrogate_model["objective"]["type"]
                if model_output["type"] == "int" or model_output["type"] == "real":
                    model_output["lower_bound"] = surrogate_model["objective"]["lower_bound"]
                    model_output["upper_bound"] = surrogate_model["objective"]["upper_bound"]
                elif model_output["type"] == "categorical":
                    model_output["categories"] = surrogate_model["objective"]["categories"]
                for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                    if output_info["output_name"] == model_output["name"]:
                        model_output["description"] = output_info["output_description"]
                model_output["result"] = "-"
                model_data["model_output"] = model_output

                model_data["output_parameters"] = []
                for output_space in surrogate_model["output_space"]:
                    output_parameter = {}
                    output_parameter["name"] = output_space["name"]
                    output_parameter["type"] = output_space["type"]
                    if output_parameter["type"] == "int" or output_parameter["type"] == "real":
                        output_parameter["lower_bound"] = output_space["lower_bound"]
                        output_parameter["upper_bound"] = output_space["upper_bound"]
                    elif output_parameter["type"] == "categorical":
                        output_parameter["categories"] = output_space["categories"]
                    for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                        if output_info["output_name"] == output_parameter["name"]:
                            output_parameter["description"] = output_info["output_description"]
                    model_data["output_parameters"].append(output_parameter)

                model_data["constants"] = []
                for constant_variable in tuning_problem_info["tuning_problem_info"]["constant_info"]:
                    model_data["constants"].append({
                                "name": constant_variable["constant_name"],
                                "type": constant_variable["constant_type"],
                                "description": constant_variable["constant_description"]})

                model_data["objective"] = surrogate_model["objective"]

                model_data_list[model_data["objective"]["name"]] = model_data

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

                model_data_list[model_data["objective"]["name"]]["sobol_analysis"] = sobol_analysis

            context = {
                    "tuning_problem_unique_name" : tuning_problem_unique_name,
                    "surrogate_model_uids" : surrogate_model_uids,
                    "model_data" : model_data_list
                    }

            return render(request, 'repo/sadashboard.html', context)

    def post(self, request, **kwargs):

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        historydb = HistoryDB_MongoDB()

        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name")
        surrogate_model_uids = request.GET.get("surrogate_model_uids", "")

        if surrogate_model_uids == "":
            tuning_problem = request.GET.get("tuning_problem", "{}")
            modeler = request.POST["modeler"]
            tuning_parameter_range = request.POST.getlist("tuning_parameter_range")
            tuning_parameter_given = request.POST.getlist("tuning_parameter_given")
            output_range = request.POST.getlist("output_range")
            num_samples = int(request.POST["num_samples"])

            historydb = HistoryDB_MongoDB()

            tuning_problem_loaded = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
            tuning_problem = copy.deepcopy(tuning_problem_loaded)
            tuning_problem_info = tuning_problem["tuning_problem_info"]

            machine_configurations_list = json.loads(request.GET.get("machine_configurations_list", "{}"))
            software_configurations_list = json.loads(request.GET.get("software_configurations_list", "{}"))
            output_options = json.loads(request.GET.get("output_options", "[]"))
            user_configurations_list = json.loads(request.GET.get("user_configurations_list", "{}"))
            user_email = request.user.email if request.user.is_authenticated else ""
            search_options = json.loads(request.GET.get("search_options", "[]"))

            input_task_avail = []
            input_task_avail.append(ast.literal_eval(request.POST["input_task"]))

            func_eval_list = historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    output_options = output_options,
                    user_configurations_list = user_configurations_list,
                    user_email = user_email)
            num_func_eval = len(func_eval_list)
            for i in range(num_func_eval):
                func_eval_list[i]["id"] = i

                for parameter_info in tuning_problem_info["parameter_info"]:
                    parameter_name = parameter_info["parameter_name"]
                    parameter_type = parameter_info["parameter_type"]

                    if parameter_type == "integer" or parameter_type == "real":
                        value = func_eval_list[i]["tuning_parameter"][parameter_name]
                        if "lower_bound" not in parameter_info:
                            parameter_info["lower_bound"] = value
                        else:
                            if value < parameter_info["lower_bound"]:
                                parameter_info["lower_bound"] = value
                        if "upper_bound" not in parameter_info:
                            parameter_info["upper_bound"] = value
                        else:
                            if value > parameter_info["upper_bound"]:
                                parameter_info["upper_bound"] = value
                    elif parameter_type == "categorical":
                        category = func_eval_list[i]["tuning_parameter"][parameter_name]
                        if "categories" not in parameter_info:
                            parameter_info["categories"] = [category]
                        else:
                            if category not in parameter_info["categories"]:
                                parameter_info["categories"].append(category)
                    else:
                        pass

                for output_info in tuning_problem_info["output_info"]:
                    output_name = output_info["output_name"]
                    output_type = output_info["output_type"]

                    if output_type == "integer":
                        value = func_eval_list[i]["evaluation_result"][output_name]
                        if "lower_bound" not in output_info:
                            output_info["lower_bound"] = value
                        else:
                            if value < output_info["lower_bound"]:
                                output_info["lower_bound"] = value
                        if "upper_bound" not in output_info:
                            output_info["upper_bound"] = value
                        else:
                            if value > output_info["upper_bound"]:
                                output_info["upper_bound"] = value
                    if output_type == "real":
                        value = func_eval_list[i]["evaluation_result"][output_name]
                        if "lower_bound" not in output_info:
                            output_info["lower_bound"] = round(value,2)
                        else:
                            if round(value, 2) < output_info["lower_bound"]:
                                output_info["lower_bound"] = round(value, 2)
                        if "upper_bound" not in output_info:
                            output_info["upper_bound"] = round(value+0.005, 2)
                        else:
                            if round(value+0.005, 2) > output_info["upper_bound"]:
                                output_info["upper_bound"] = round(value+0.005, 2)

                    elif output_type == "categorical":
                        category = func_eval_list[i]["evaluation_result"][output_name]
                        if "categories" not in output_info:
                            output_info["categories"] = [category]
                        else:
                            if category not in output_info["categories"]:
                                output_info["categories"].append(category)
                    else:
                        pass

                input_task = {}
                input_task.update(func_eval_list[i]["task_parameter"])
                if "constants" in func_eval_list[i]:
                    input_task.update(func_eval_list[i]["constants"])

                if input_task not in input_task_avail:
                    input_task_avail.append(input_task)

            print ("input_task_avail: ", input_task_avail)
            print ("machine_configurations: ", machine_configurations_list)
            print ("software_configurations: ", software_configurations_list)
            print ("tuning_parameter_range: ", tuning_parameter_range)
            print ("tuning_parameter_given: ", tuning_parameter_given)
            print ("tuning_parameter_range_type: ", type(tuning_parameter_range))
            print ("tuning_parameter_given_type: ", type(tuning_parameter_given))
            print ("tuning_problem: ", tuning_problem)

            input_task = ast.literal_eval(request.POST["input_task"])
            Igiven = []
            print ("input_task: ", input_task)
            print ("input_task_type: ", type(input_task))

            problem_space = {
                "input_space": [],
                "parameter_space": [],
                "output_space": [],
                "constants": []
            }

            for task_info in tuning_problem_info["task_info"]:
                task_name = task_info["task_name"]
                task_type = task_info["task_type"]
                print ("task_name: ", task_name)

                task_value = input_task[task_name]
                Igiven.append(task_value)
                input_task.pop(task_name)
                print ("task_chosen: name: ", task_name, " vaule: ", task_value)

                if task_type == "integer" or task_type == "real":
                    problem = {
                        "name": task_name,
                        "type": task_type,
                        "transformer": "normalize",
                        "lower_bound": task_value,
                        "upper_bound": task_value+1
                    }
                    problem_space["input_space"].append(problem)
                elif task_type == "categorical":
                    problem = {
                        "name": task_name,
                        "type": task_type,
                        "transformer": "onehot",
                        "categories": [task_value]
                    }
                    problem_space["input_space"].append(problem)
            constants = input_task
            problem_space["constants"].append(constants)

            pGiven = {}

            for i in range(len(tuning_problem_info["parameter_info"])):
                parameter_info = tuning_problem_info["parameter_info"][i]

                parameter_name = parameter_info["parameter_name"]
                parameter_type = parameter_info["parameter_type"]

                parameter_range = ast.literal_eval(tuning_parameter_range[i])

                #tuning_problem["tuning_problem_info"]["parameter_info"][i]["given_value"] = parameter_given

                if parameter_type == "integer" or parameter_type == "real":
                    problem = {
                        "name": parameter_name,
                        "type": parameter_type,
                        "transformer": "normalize",
                        "lower_bound": parameter_range[0],
                        "upper_bound": parameter_range[-1]
                    }
                    problem_space["parameter_space"].append(problem)

                elif parameter_type == "categorical":
                    problem = {
                        "name": parameter_name,
                        "type": parameter_type,
                        "transformer": "onehot",
                        "categories": parameter_range
                    }
                    problem_space["parameter_space"].append(problem)

            for i in range(len(tuning_problem_info["output_info"])):
                output_info = tuning_problem_info["output_info"][i]

                output_name = output_info["output_name"]
                output_type = output_info["output_type"]

                if output_type == "integer" or output_type == "real":
                    problem = {
                        "name": output_name,
                        "type": output_type,
                        "transformer": "normalize",
                        "lower_bound": output_info["lower_bound"],
                        "upper_bound": output_info["upper_bound"]
                    }
                    problem_space["output_space"].append(problem)
                else:
                    problem = {
                        "name": output_name,
                        "type": output_type,
                        "transformer": "onehot",
                        "categories": output_info["categories"]
                    }
                    problem_space["output_space"].append(problem)

                output_range = ast.literal_eval(output_range[i])
                func_eval_list_filtered = []
                #copy.deepcopy(func_eval_list)
                for func_eval in func_eval_list:
                    if output_type == "integer" or output_type == "real":
                        if func_eval["evaluation_result"][output_name] >= output_range[0] and\
                           func_eval["evaluation_result"][output_name] <= output_range[-1]:
                            func_eval_list_filtered.append(func_eval)
                        #else:
                        #    print ("filtered: ", func_eval)
                    elif output_type == "categorical":
                        if func_eval["evaluation_result"][output_name] in output_range:
                            func_eval_list_filtered.append(func_eval)
                        #else:
                        #    print ("filtered: ", func_eval)
                # try:
                #     import gptune
                #     print ("problem_space: ", problem_space)
                #     print ("num_samples: ", num_samples, " type: ", type(num_samples))
                #     ret = gptune.SensitivityAnalysis(problem_space=problem_space,
                #             modeler=modeler,
                #             input_task=Igiven,
                #             function_evaluations=func_eval_list_filtered,
                #             num_samples=num_samples)
                #     print("ret: ", ret)
                #     #output_info["result"] = ret[output_name][0][0] #parameter_given
                #     #output_info["result_std"] = ret[output_name+"_var"][0][0] #parameter_given
                # except:
                #      ret = {'S1': {'nb':1,'ib':.2}, 'S1_conf': {'nb':.1,'ib':.2}, 'ST': {'nb':.1,'ib':.2}, 'ST_conf': {'nb':.1,'ib':.2}, 'S2': {'nb':{'ib':.1},'ib':{'nb':.2}}, 'S2_conf': {'nb':{'ib':.1},'ib':{'nb':.2}}}
                
                # try:
                import gptune
                print ("problem_space: ", problem_space)
                print ("num_samples: ", num_samples, " type: ", type(num_samples))
                ret = gptune.SensitivityAnalysis(problem_space=problem_space,
                    modeler=modeler,
                    input_task=Igiven,
                    function_evaluations=func_eval_list_filtered,
                    num_samples=num_samples)
                print("ret: ", ret)
                    #output_info["result"] = ret[output_name][0][0] #parameter_given
                    #output_info["result_std"] = ret[output_name+"_var"][0][0] #parameter_given
                # except:
                    # ret = {'S1': {'nb':1,'ib':.2}, 'S1_conf': {'nb':.1,'ib':.2}, 'ST': {'nb':.1,'ib':.2}, 'ST_conf': {'nb':.1,'ib':.2}, 'S2': {'nb':{'ib':.1},'ib':{'nb':.2}}, 'S2_conf': {'nb':{'ib':.1},'ib':{'nb':.2}}}
                
                
                # print('tuning problem info: ', tuning_problem_info)

                sobol_analysis = {}
                sobol_analysis["s1_parameters"] = []
                for param_name in ret["S1"]:
                    s1 = {
                        "name": param_name,
                        "S1": ret["S1"][param_name],
                        "S1_conf": ret["S1_conf"][param_name]
                    }
                    sobol_analysis["s1_parameters"].append(s1)
                sobol_analysis["st_parameters"] = []
                for param_name in ret["ST"]:
                    st = {
                        "name": param_name,
                        "ST": ret["ST"][param_name],
                        "ST_conf": ret["ST_conf"][param_name]
                    }
                    sobol_analysis["st_parameters"].append(st)
                sobol_analysis["s2_parameters"] = []
                if "S2" in ret:
                    S2_dict = ret["S2"]
                    S2_conf_array = ret["S2_conf"]
                    num_parameters = len(tuning_problem_info["parameter_info"])
                    for i in range(num_parameters):
                        for j in range(i+1, num_parameters):
                            tuning_parameter = {}
                            name1 = tuning_problem_info["parameter_info"][i]["parameter_name"]
                            name2 = tuning_problem_info["parameter_info"][j]["parameter_name"]
                            tuning_parameter["name1"] = name1
                            tuning_parameter["name2"] = name2
                            tuning_parameter["S2"] = round(S2_dict[name1][name2],3)
                            tuning_parameter["S2_conf"] = round(S2_conf_array[name1][name2],3)
                            sobol_analysis["s2_parameters"].append(tuning_parameter)

                from dashing.viz import callgraph
                fig = callgraph.gptune_callgraph2(sobol_analysis)
                chart = plot(fig,output_type="div")
                # chart = []

            context = {
                "tuning_problem_unique_name": tuning_problem_unique_name,
                "tuning_problem": tuning_problem,
                "output_options" : output_options,
                "input_task_avail" : input_task_avail,
                "function_evaluations" : func_eval_list,
                "sobol_analysis" : sobol_analysis,
                "num_func_eval" : num_func_eval,
                "machine_configurations_list" : json.dumps(machine_configurations_list),
                "software_configurations_list" : json.dumps(software_configurations_list),
                "output_options" : json.dumps(output_options),
                "user_configurations_list" : json.dumps(user_configurations_list),
                "sensitivity_analysis_chart" : chart
            }

            return render(request, 'repo/model-build-sadashboard.html', context)

        else:
            tuning_problem = historydb.load_tuning_problem_by_unique_name(tuning_problem_unique_name)
            tuning_problem_info = historydb.get_tuning_problem_info(tuning_problem_unique_name)
            surrogate_models = historydb.load_surrogate_models_by_uids(surrogate_model_uids)

            model_data_list = {}

            for surrogate_model in surrogate_models:
                model_data = {}

                model_data["surrogate_model_uid"] = surrogate_model["uid"]

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
                    if task_parameter["type"] == "int" or task_parameter["type"] == "real":
                        task_parameter["lower_bound"] = task_space["lower_bound"]
                        task_parameter["upper_bound"] = task_space["upper_bound"]
                    elif task_parameter["type"] == "categorical":
                        task_parameter["categories"] = task_space["categories"]
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
                    if tuning_parameter["type"] == "int" or tuning_parameter["type"] == "real":
                        tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
                        tuning_parameter["upper_bound"] = parameter_space["upper_bound"]
                        tuning_parameter["value"] = tuning_parameter["lower_bound"]
                    elif tuning_parameter["type"] == "categorical":
                        tuning_parameter["categories"] = parameter_space["categories"]
                        tuning_parameter["value"] = str(tuning_parameter["categories"][0])
                    for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                        if parameter_info["parameter_name"] == tuning_parameter["name"]:
                            tuning_parameter["description"] = parameter_info["parameter_description"]

                    model_data["tuning_parameters"].append(tuning_parameter)

                model_output = {}
                model_output["name"] = surrogate_model["objective"]["name"]
                model_output["type"] = surrogate_model["objective"]["type"]
                if model_output["type"] == "int" or model_output["type"] == "real":
                    model_output["lower_bound"] = surrogate_model["objective"]["lower_bound"]
                    model_output["upper_bound"] = surrogate_model["objective"]["upper_bound"]
                elif model_output["type"] == "categorical":
                    model_output["categories"] = surrogate_model["objective"]["categories"]
                for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                    if output_info["output_name"] == model_output["name"]:
                        model_output["description"] = output_info["output_description"]
                model_output["result"] = "-"
                model_data["model_output"] = model_output

                model_data["output_parameters"] = []
                for output_space in surrogate_model["output_space"]:
                    output_parameter = {}
                    output_parameter["name"] = output_space["name"]
                    output_parameter["type"] = output_space["type"]
                    if output_parameter["type"] == "int" or output_parameter["type"] == "real":
                        output_parameter["lower_bound"] = output_space["lower_bound"]
                        output_parameter["upper_bound"] = output_space["upper_bound"]
                    elif output_parameter["type"] == "categorical":
                        output_parameter["categories"] = output_space["categories"]
                    for output_info in tuning_problem["tuning_problem_info"]["output_info"]:
                        if output_info["output_name"] == output_parameter["name"]:
                            output_parameter["description"] = output_info["output_description"]
                    model_data["output_parameters"].append(output_parameter)

                model_data["constants"] = []
                for constant_variable in tuning_problem_info["tuning_problem_info"]["constant_info"]:
                    model_data["constants"].append({
                                "name": constant_variable["constant_name"],
                                "type": constant_variable["constant_type"],
                                "description": constant_variable["constant_description"]})

                model_data["objective"] = surrogate_model["objective"]

                model_data_list[model_data["objective"]["name"]] = model_data

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

                model_data_list[model_data["objective"]["name"]]["sobol_analysis"] = sobol_analysis

            sobol_analysis = {}
            surrogate_model_uid = request.POST["surrogate_model_uid"]
            sobol_analysis_task_parameter = request.POST["sobol_analysis_task_parameter"]
            sobol_analysis_num_samples = int(request.POST["sobol_analysis_num_samples"])
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

            from gptune import SensitivityAnalysis
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

            if "S2" in si:
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

            import pprint
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(si)

            context = {
                    "tuning_problem_unique_name" : tuning_problem_unique_name,
                    "surrogate_model_uids" : surrogate_model_uids,
                    "model_data" : model_data_list,
                    "sobol_analysis" : sobol_analysis
                    }

            return render(request, 'repo/sadashboard.html', context)

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
            if task_parameter["type"] == "int" or task_parameter["type"] == "real":
                task_parameter["lower_bound"] = task_space["lower_bound"]
                task_parameter["upper_bound"] = task_space["upper_bound"]
            elif task_parameter["type"] == "categorical":
                task_parameter["categories"] = task_space["categories"]
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
            if tuning_parameter["type"] == "int" or tuning_parameter["type"] == "real":
                tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
                tuning_parameter["upper_bound"] = parameter_space["upper_bound"]
                tuning_parameter["value"] = tuning_parameter["lower_bound"]
            elif tuning_parameter["type"] == "categorical":
                tuning_parameter["categories"] = parameter_space["categories"]
                tuning_parameter["value"] = str(tuning_parameter["categories"][0])
            for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                if parameter_info["parameter_name"] == tuning_parameter["name"]:
                    tuning_parameter["description"] = parameter_info["parameter_description"]

            model_data["tuning_parameters"].append(tuning_parameter)

        model_data["output_parameters"] = []
        for output_space in surrogate_model["output_space"]:
            output_parameter = {}
            output_parameter["name"] = output_space["name"]
            output_parameter["type"] = output_space["type"]
            if output_parameter["type"] == "int" or output_parameter["type"] == "real":
                output_parameter["lower_bound"] = output_space["lower_bound"]
                output_parameter["upper_bound"] = output_space["upper_bound"]
            elif output_parameter["type"] == "categorical":
                output_parameter["categories"] = output_space["categories"]
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
            if task_parameter["type"] == "int" or task_parameter["type"] == "real":
                task_parameter["lower_bound"] = task_space["lower_bound"]
                task_parameter["upper_bound"] = task_space["upper_bound"]
            elif task_parameter["type"] == "categorical":
                task_parameter["categories"] = task_space["categories"]
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
            if tuning_parameter["type"] == "int" or tuning_parameter["type"] == "real":
                tuning_parameter["lower_bound"] = parameter_space["lower_bound"]
                tuning_parameter["upper_bound"] = parameter_space["upper_bound"]
                tuning_parameter["value"] = tuning_parameter["lower_bound"]
            elif tuning_parameter["type"] == "categorical":
                tuning_parameter["categories"] = parameter_space["categories"]
                tuning_parameter["value"] = str(tuning_parameter["categories"][0])
            for parameter_info in tuning_problem["tuning_problem_info"]["parameter_info"]:
                if parameter_info["parameter_name"] == tuning_parameter["name"]:
                    tuning_parameter["description"] = parameter_info["parameter_description"]

            model_data["tuning_parameters"].append(tuning_parameter)

        model_data["output_parameters"] = []
        for output_space in surrogate_model["output_space"]:
            output_parameter = {}
            output_parameter["name"] = output_space["name"]
            output_parameter["type"] = output_space["type"]
            if output_parameter["type"] == "int" or output_parameter["type"] == "real":
                output_parameter["lower_bound"] = output_space["lower_bound"]
                output_parameter["upper_bound"] = output_space["upper_bound"]
            elif output_parameter["type"] == "categorical":
                output_parameter["categories"] = output_space["categories"]
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

        sobol_analysis_task_parameter = ast.literal_eval(request.POST["sobol_analysis_task_parameter"])
        print ("SOBEL_ANALYSIS_TASK_PARAMETER: ", sobol_analysis_task_parameter)
        sobol_analysis_task_parameter_arr = [sobol_analysis_task_parameter[key] for key in sobol_analysis_task_parameter.keys()]
        print ("SOBEL_ANALYSIS_TASK_PARAMETER_ARR: ", sobol_analysis_task_parameter_arr)

        from gptune import SensitivityAnalysis
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

        if "S2" in si:
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

        return redirect(reverse_lazy('repo:user-dashboard'))

class Export(TemplateView):

    def get(self, request, **kwargs):
        tuning_problem_unique_name = request.GET.get("tuning_problem_unique_name", "")
        machine_configurations_list = json.loads(request.GET.get("machine_configurations_list", "{}"))
        software_configurations_list = json.loads(request.GET.get("software_configurations_list", "{}"))
        output_options = json.loads(request.GET.get("output_options", "[]"))
        user_configurations_list = json.loads(request.GET.get("user_configurations_list", "{}"))
        user_email = request.user.email if request.user.is_authenticated else ""
        search_options = json.loads(request.GET.get("search_options", "[]"))

        historydb = HistoryDB_MongoDB()

        perf_data = []

        if "func_eval" in search_options:
            perf_data.extend(historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                machine_configurations_list = machine_configurations_list,
                software_configurations_list = software_configurations_list,
                output_options = output_options,
                user_configurations_list = user_configurations_list,
                user_email = user_email))

        if "surrogate_model" in search_options:
            surrogate_models = historydb.load_surrogate_models_filtered(
                tuning_problem_unique_name = tuning_problem_unique_name,
                machine_configurations_list = machine_configurations_list,
                software_configurations_list = software_configurations_list,
                output_options = output_options,
                user_configurations_list = user_configurations_list,
                user_email = user_email)

            for objective_name in surrogate_models:
                perf_data.extend(surrogate_models[objective_name])

        context = { "perf_data" : perf_data, }

        return render(request, 'repo/export.html', context)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def direct_download(request):

    if request.method == "POST":

        if "X-Api-Key" not in request.headers:
            response_data = {}
            response_data["result"] = "failed"
            return HttpResponse(json.dumps(response_data), status=404)

        api_key = request.headers["X-Api-Key"]
        print ("api_key: ", api_key)

        tuning_problem_name = request.POST.get("tuning_problem_name", "")
        problem_space = request.POST.get("problem_space", "{}")
        configuration_space = request.POST.get("configuration_space", "{}")

        historydb = HistoryDB_MongoDB()

        perf_data = historydb.load_func_eval_with_token(
                access_token = api_key,
                tuning_problem_name = tuning_problem_name,
                problem_space = json.loads(problem_space),
                configuration_space = json.loads(configuration_space))

        response_data = {}
        response_data['result'] = 'success'
        response_data['perf_data'] = perf_data

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    elif request.method == "GET":

        if "X-Api-Key" not in request.headers:
            response_data = {}
            response_data["result"] = "failed"
            return HttpResponse(json.dumps(response_data), status=404)

        api_key = request.headers["X-Api-Key"]
        print ("api_key: ", api_key)

        tuning_problem_name = request.GET.get("tuning_problem_name", "")
        problem_space = request.GET.get("problem_space", "{}")
        configuration_space = request.POST.get("configuration_space", "{}")

        historydb = HistoryDB_MongoDB()

        perf_data = historydb.load_func_eval_with_token(
                access_token = api_key,
                tuning_problem_name = tuning_problem_name,
                problem_space = json.loads(problem_space),
                configuration_space = json.loads(configuration_space))

        response_data = {}
        response_data['result'] = 'success'
        response_data['perf_data'] = perf_data

        return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def direct_upload(request):

    if request.method == "POST":

        if "X-Api-Key" not in request.headers:
            response_data = {}
            response_data["result"] = "failed"
            return HttpResponse(json.dumps(response_data), status=404)

        api_key = request.headers["X-Api-Key"]
        print ("api_key: ", api_key)

        if api_key != "":
            tuning_problem_name = request.POST.get("tuning_problem_name", "")
            print ("tuning_problem_name: ", tuning_problem_name)

            function_evaluation = json.loads(request.POST.get("function_evaluation_document", "{}"))
            print ("function_evaluation: ", function_evaluation)

            historydb = HistoryDB_MongoDB()
            ret = historydb.store_func_eval_with_token(
                    access_token = api_key,
                    tuning_problem_name = tuning_problem_name,
                    function_evaluation = function_evaluation)

            response_data = {}
            response_data["result"] = "success"
        else:
            response_data = {}
            response_data["result"] = "failed"
            response_data["message"] = "no access token is provided"

        return HttpResponse(json.dumps(response_data), content_type="application/json")

@csrf_exempt
def api_test(request):

    if request.method == "POST":

        if "X-Api-Key" not in request.headers:
            response_data = {}
            response_data["result"] = "failed"
            return HttpResponse(json.dumps(response_data), status=404)

        api_key = request.headers["X-Api-Key"]
        print (api_key)

        print (request.headers)
        print (request.POST)

        response_data = {}
        response_data['result'] = 'success'

        return HttpResponse(json.dumps(response_data))

    elif request.method == "GET":

        if "X-Api-Key" not in request.headers:
            response_data = {}
            response_data["result"] = "failed"
            return HttpResponse(json.dumps(response_data), status=404)

        api_key = request.headers["X-Api-Key"]
        print (api_key)

        print (request.headers)
        print (request.GET)

        response_data = {}
        response_data['result'] = 'success'

        return HttpResponse(json.dumps(response_data), content_type="application/json")

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

        if True:
            print ("upload")
            historydb = HistoryDB_MongoDB()
            tuning_problem_unique_name = request.POST["tuning_problem"]
            tuning_problem_type = historydb.get_tuning_problem_type(tuning_problem_unique_name)
            print ("tuning_problem_unique_name: ", tuning_problem_unique_name)
            machine_check_option = request.POST["machine_check_option"]
            print ("machine_check_option: ", machine_check_option)
            if machine_check_option == "machine_nocheck":
                machine_check = False
            else:
                machine_check = True
            machine_unique_name = request.POST["machine"]
            print ("machine_unique_name: ", machine_unique_name)

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
                num_added_func_eval = historydb.upload_func_eval(tuning_problem_unique_name, machine_unique_name, json_data, user_info, accessibility, tuning_problem_type=tuning_problem_type, machine_check=machine_check)
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

        tuning_problem_list_ = historydb.load_all_regular_tuning_problems()
        tuning_problem_list = [{} for i in range(len(tuning_problem_list_))]
        for i in range(len(tuning_problem_list_)):
            tuning_problem_list[i]["id"] = i
            tuning_problem_list[i]["uid"] = tuning_problem_list_[i]["uid"]
            tuning_problem_list[i]["tuning_problem_info"] = tuning_problem_list_[i]["tuning_problem_info"]
            tuning_problem_list[i]["tuning_problem_name"] = tuning_problem_list_[i]["tuning_problem_name"]
            tuning_problem_list[i]["unique_name"] = tuning_problem_list_[i]["unique_name"]
            tuning_problem_list[i]["user_name"] = tuning_problem_list_[i]["user_info"]["user_name"]
            tuning_problem_list[i]["update_time"] = tuning_problem_list_[i]["update_time"]

        flexible_tuning_problem_list_ = historydb.load_all_flexible_tuning_problems()
        flexible_tuning_problem_list = [{} for i in range(len(flexible_tuning_problem_list_))]
        for i in range(len(flexible_tuning_problem_list_)):
            flexible_tuning_problem_list[i]["id"] = i
            flexible_tuning_problem_list[i]["uid"] = flexible_tuning_problem_list_[i]["uid"]
            flexible_tuning_problem_list[i]["tuning_problem_info"] = flexible_tuning_problem_list_[i]["tuning_problem_info"]
            flexible_tuning_problem_list[i]["tuning_problem_name"] = flexible_tuning_problem_list_[i]["tuning_problem_name"]
            flexible_tuning_problem_list[i]["unique_name"] = flexible_tuning_problem_list_[i]["unique_name"]
            flexible_tuning_problem_list[i]["user_name"] = flexible_tuning_problem_list_[i]["user_info"]["user_name"]
            flexible_tuning_problem_list[i]["update_time"] = flexible_tuning_problem_list_[i]["update_time"]

        context = {
            "tuning_problem_list" : tuning_problem_list,
            "flexible_tuning_problem_list" : flexible_tuning_problem_list
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

        if True:
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
                if constant_names[i] != "":
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

class AddTuningProblemFlexible(TemplateView):

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

        return render(request, 'repo/add-tuning-problem-flexible.html', context)

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

            tuning_problem_info["task_info"] = "flexible"
            tuning_problem_info["parameter_info"] = "flexible"
            tuning_problem_info["output_info"] = "flexible"
            tuning_problem_info["constant_info"] = "flexible"

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
            historydb.add_tuning_problem_flexible(tuning_problem_name, tuning_problem_info, user_info)

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
                if constant_names[i] != "":
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

