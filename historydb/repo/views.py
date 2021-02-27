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

import os
import json
import ast

class Dashboard(TemplateView):
    def get(self, request, **kwargs):
        print ("======== Dashboard GET ========")

        historydb = HistoryDB_MongoDB()

        applications_avail = historydb.get_applications_avail()
        machine_deps_avail = historydb.get_machine_deps_avail()
        software_deps_avail = historydb.get_software_deps_avail()
        users_avail = historydb.get_users_avail()

        user_email = ""
        if request.user.is_authenticated:
            user_email = request.user.email

        application = request.GET.get("application", "")

        if application != "":
            print ("APPLICATION GIVEN: ", application)

            machine_deps_list = ast.literal_eval(request.GET.get("machine_deps_list", ""))
            software_deps_list = ast.literal_eval(request.GET.get("software_deps_list", ""))
            users_list = ast.literal_eval(request.GET.get("users_list", ""))

            historydb = HistoryDB_MongoDB()

            search_data = ast.literal_eval(request.GET.get("search_data", ""))

            application_info = historydb.load_application_info(application_name = application)

            if "func_eval" in search_data:
                func_eval_list = historydb.load_func_eval_filtered(application_name = application,
                        machine_deps_list = machine_deps_list,
                        software_deps_list = software_deps_list,
                        users_list = users_list,
                        user_email = user_email)
                num_func_eval = len(func_eval_list)
                print ("num_func_eval: ", num_func_eval)
                num_evals_per_page = 15
                if (num_func_eval%num_evals_per_page) == 0:
                    num_pages_func_eval = num_func_eval/num_evals_per_page
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

            if "model_data" in search_data:
                model_data = historydb.load_model_data_filtered(
                        application_name = application,
                        machine_deps_list = machine_deps_list,
                        software_deps_list = software_deps_list,
                        users_list = users_list,
                        user_email = user_email)
                num_model_data = len(model_data)
                num_model_data_per_page = 15
                if (num_model_data %num_model_data_per_page) == 0:
                    num_pages_model_data = num_model_data/num_model_data_per_page
                else:
                    num_pages_model_data = int(num_model_data/num_model_data_per_page)+1
                if (num_pages_model_data == 0):
                    num_pages_model_data = 1
                current_page_model_data = int(request.GET.get("current_page_model_data", 0))
                start_index_model_data = (current_page_model_data)*num_model_data_per_page
                end_index_model_data = (current_page_model_data+1)*num_model_data_per_page
                if end_index_model_data > num_model_data:
                    end_index_model_data = num_model_data
                model_data_web = model_data[start_index_model_data:end_index_model_data]
                for i in range(len(model_data_web)):
                    model_data_web[i]["id"] = start_index_model_data+i
                    model_data_web[i]["num_func_eval"] = len(model_data_web[i]["func_eval"])
                    model_data_web[i]["num_task_parameters"] = len(model_data_web[i]["task_parameters"])
                    model_data_web[i]["num_func_eval_per_task"] = \
                            int(len(model_data_web[i]["func_eval"])/len(model_data_web[i]["task_parameters"]))
            else:
                model_data_web = []
                num_model_data = 0
                num_pages_model_data = 0
                current_page_model_data = 0

            context = {
                    "application_info" : json.dumps(application_info),
                    "application" : application,
                    "applications_avail" : applications_avail,
                    "func_eval_list" : func_eval_web,
                    "num_func_eval" : num_func_eval,
                    "num_pages_func_eval" : range(num_pages_func_eval),
                    "current_page_func_eval" : current_page_func_eval,
                    "model_data_list" : model_data_web,
                    "num_model_data" : num_model_data,
                    "num_pages_model_data" : range(num_pages_model_data),
                    "current_page_model_data" : current_page_model_data,
                    "machine_deps_avail" : json.dumps(machine_deps_avail),
                    "software_deps_avail" : json.dumps(software_deps_avail),
                    "users_avail" : json.dumps(users_avail),
                    "machine_deps_list" : json.dumps(machine_deps_list),
                    "software_deps_list" : json.dumps(software_deps_list),
                    "users_list" : json.dumps(users_list),
                    "search_data" : json.dumps(search_data)
                    }

            return render(request, 'repo/dashboard.html', context)

        else:
            historydb = HistoryDB_MongoDB()

            print ("APPLICATION NOT GIVEN: ", application)

            func_eval_web = []
            num_func_eval = 0
            num_pages_func_eval = 0
            current_page_func_eval = 0

            model_data_web = []
            num_model_data = 0
            num_pages_model_data = 0
            current_page_model_data = 0

            context = {
                    "application_info" : json.dumps({"application":application}),
                    "application" : application,
                    "applications_avail" : applications_avail,
                    "func_eval_list" : func_eval_web,
                    "num_func_eval" : num_func_eval,
                    "num_pages_func_eval" : range(num_pages_func_eval),
                    "current_page_func_eval" : current_page_func_eval,
                    "model_data_list" : model_data_web,
                    "num_model_data" : num_model_data,
                    "num_pages_model_data" : range(num_pages_model_data),
                    "current_page_model_data" : current_page_model_data,
                    "machine_deps_avail" : json.dumps(machine_deps_avail),
                    "software_deps_avail" : json.dumps(software_deps_avail),
                    "users_avail" : json.dumps(users_avail),
                    "machine_deps_list" : json.dumps(machine_deps_avail),
                    "software_deps_list" : json.dumps(software_deps_avail),
                    "users_list" : json.dumps(users_avail),
                    "search_data" : json.dumps({})
                    }

            return render(request, 'repo/dashboard.html', context)

    def post(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()

        applications_avail = historydb.get_applications_avail()
        print (applications_avail)
        machine_deps_avail = historydb.get_machine_deps_avail()
        print (machine_deps_avail)
        software_deps_avail = historydb.get_software_deps_avail()
        users_avail = historydb.get_users_avail()

        application = request.POST["application"]

        application_info = historydb.load_application_info(application_name = application)
        print ("APPLICATION_INFO")
        print (application_info)

        machine_deps_list = []
        post_values = request.POST.getlist('machine_deps_list')
        for i in range(len(post_values)):
            machine_deps_list.append(json.loads(post_values[i]))
        print ("machine_deps_list")
        print (machine_deps_list)

        software_deps_list = []
        post_values = request.POST.getlist('software_deps_list')
        for i in range(len(post_values)):
            software_deps_list.append(json.loads(post_values[i]))
        print ("software_deps_list")
        print (software_deps_list)

        users_list = []
        post_values = request.POST.getlist('users_list')
        for i in range(len(post_values)):
            users_list.append(json.loads(post_values[i]))
        print ("users_list")
        print (users_list)

        search_data = request.POST.getlist("search_data")
        print ("search_data")
        print (search_data)

        user_email = ""
        if request.user.is_authenticated:
            user_email = request.user.email

        if "func_eval" in search_data:
            func_eval_list = historydb.load_func_eval_filtered(application_name = application,
                    machine_deps_list = machine_deps_list,
                    software_deps_list = software_deps_list,
                    users_list = users_list,
                    user_email = user_email)
            num_func_eval = len(func_eval_list)
            num_evals_per_page = 15
            if (num_func_eval%num_evals_per_page) == 0:
                num_pages_func_eval = num_func_eval/num_evals_per_page
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

        if "model_data" in search_data:
            model_data = historydb.load_model_data_filtered(
                    application_name = application,
                    machine_deps_list = machine_deps_list,
                    software_deps_list = software_deps_list,
                    users_list = users_list,
                    user_email = user_email)
            num_model_data = len(model_data)
            num_model_data_per_page = 15
            if (num_model_data %num_model_data_per_page) == 0:
                num_pages_model_data = num_model_data/num_model_data_per_page
            else:
                num_pages_model_data = int(num_model_data/num_model_data_per_page)+1
            if (num_pages_model_data == 0):
                num_pages_model_data = 1
            current_page_model_data = 0
            start_index_model_data = (current_page_model_data)*num_model_data_per_page
            end_index_model_data = (current_page_model_data+1)*num_model_data_per_page
            if end_index_model_data > num_model_data:
                end_index_model_data = num_model_data
            model_data_web = model_data[start_index_model_data:end_index_model_data]
            for i in range(len(model_data_web)):
                model_data_web[i]["id"] = start_index_model_data+i
                model_data_web[i]["num_func_eval"] = len(model_data_web[i]["func_eval"])
                model_data_web[i]["num_task_parameters"] = len(model_data_web[i]["task_parameters"])
                model_data_web[i]["num_func_eval_per_task"] = \
                        int(len(model_data_web[i]["func_eval"])/len(model_data_web[i]["task_parameters"]))
        else:
            model_data_web = []
            num_model_data = 0
            num_pages_model_data = 0
            current_page_model_data = 0

        context = {
                "application_info" : json.dumps(application_info),
                "applications_avail" : applications_avail,
                "application" : application,
                "func_eval_list" : func_eval_web,
                "num_func_eval" : num_func_eval,
                "num_pages_func_eval" : range(num_pages_func_eval),
                "current_page_func_eval" : current_page_func_eval,
                "model_data_list" : model_data_web,
                "num_model_data" : num_model_data,
                "num_pages_model_data" : range(num_pages_model_data),
                "current_page_model_data" : current_page_model_data,
                "machine_deps_avail" : json.dumps(machine_deps_avail),
                "software_deps_avail" : json.dumps(software_deps_avail),
                "users_avail" : json.dumps(users_avail),
                "machine_deps_list" : json.dumps(machine_deps_list),
                "software_deps_list" : json.dumps(software_deps_list),
                "users_list" : json.dumps(users_list),
                "search_data" : json.dumps(search_data)
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

        model_data = historydb.load_model_data_by_user(user_email = user_email)
        num_model_data = len(model_data)
        num_model_data_per_page = 30
        if (num_model_data %num_model_data_per_page) == 0:
            num_pages_model_data = num_model_data/num_model_data_per_page
        else:
            num_pages_model_data = int(num_model_data/num_model_data_per_page)+1
        if (num_pages_model_data == 0):
            num_pages_model_data = 1
        current_page_model_data = int(request.GET.get("current_page_model_data", 0))
        start_index_model_data = (current_page_model_data)*num_model_data_per_page
        end_index_model_data = (current_page_model_data+1)*num_model_data_per_page
        if end_index_model_data > num_model_data:
            end_index_model_data = num_model_data
        model_data_web = model_data[start_index_model_data:end_index_model_data]
        for i in range(len(model_data_web)):
            model_data_web[i]["id"] = start_index_model_data+i
            model_data_web[i]["num_func_eval"] = len(model_data_web[i]["func_eval"])
            model_data_web[i]["num_task_parameters"] = len(model_data_web[i]["task_parameters"])
            model_data_web[i]["num_func_eval_per_task"] = \
                    int(len(model_data_web[i]["func_eval"])/len(model_data_web[i]["task_parameters"]))

        context = {
                "func_eval_list" : func_eval_web,
                "num_func_eval" : num_func_eval,
                "num_pages_func_eval" : range(num_pages_func_eval),
                "current_page_func_eval" : current_page_func_eval,
                "model_data_list" : model_data_web,
                "num_model_data" : num_model_data,
                "num_pages_model_data" : range(num_pages_model_data),
                "current_page_model_data" : current_page_model_data,
                }

        return render(request, 'repo/user-dashboard.html', context)

    def post(self, request, **kwargs):
        context = {}

        return render(request, 'repo/user-dashboard.html', context)

class EntryAccess(TemplateView):
    def get(self, request, **kwargs):
        context = {}

        return render(request, 'repo/user-dashboard.html', context)

    def post(self, request, **kwargs):
        entry_uid = request.POST["entry_uid"]
        application_name = request.POST["application_name"]

        accessibility_type = request.POST['accessibility']
        access_group_given = request.POST['group_invites']
        print ('access group: ', access_group_given)
        access_group = access_group_given.split(';')

        accessibility = {}
        accessibility["type"] = accessibility_type
        if (accessibility_type == "group"):
            accessibility["group"] = access_group

        historydb = HistoryDB_MongoDB()
        historydb.update_entry_accessibility(application_name, entry_uid, accessibility)

        return redirect(reverse_lazy('repo:user-dashboard')) #, kwargs={'username': user.username}))

class EntryDel(TemplateView):
    def get(self, request, **kwargs):
        context = {}

        return render(request, 'repo/user-dashboard.html', context)

    def post(self, request, **kwargs):
        entry_uid = request.POST["entry_uid"]
        application_name = request.POST["application_name"]

        historydb = HistoryDB_MongoDB()
        historydb.delete_perf_data_by_uid(application_name, entry_uid)

        return redirect(reverse_lazy('repo:user-dashboard')) #, kwargs={'username': user.username}))

class Export(TemplateView):

    def get(self, request, **kwargs):
        application = request.GET.get("application", "")
        machine_deps_list = json.loads(request.GET.get("machine_deps_list", "{}"))
        software_deps_list = json.loads(request.GET.get("software_deps_list", "{}"))
        users_list = json.loads(request.GET.get("users_list", "{}"))
        user_email = ""
        if request.user.is_authenticated:
            user_email = request.user.email

        historydb = HistoryDB_MongoDB()
        perf_data = historydb.load_func_eval_filtered(application_name = application,
                machine_deps_list = machine_deps_list,
                software_deps_list = software_deps_list,
                users_list = users_list,
                user_email = user_email)

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

        applications_avail = historydb.get_applications_avail()
        applications_avail_per_library = historydb.get_applications_avail_per_library()
        machine_deps_avail = historydb.get_machine_deps_avail()
        software_deps_avail = historydb.get_software_deps_avail()
        users_avail = historydb.get_users_avail()

        context = {
                "applications_avail" : applications_avail,
                "applications_avail_per_library" : applications_avail_per_library,
                "machine_deps_avail" : json.dumps(machine_deps_avail),
                "software_deps_avail" : json.dumps(software_deps_avail),
                "users_avail" : json.dumps(users_avail),
                }

        return render(request, 'repo/upload.html', context)

    def post(self, request, **kwargs):
        print ("======== Upload POST ========")

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        print ("user name: ", request.user.username)
        print ("user email: ", request.user.email)
        print ("group invites: ", request.POST['group_invites'])

        user_info = {}
        user_info["name"] = request.user.username
        user_info["email"] = request.user.email
        user_info["affiliation"] = request.user.profile.affiliation

        application_name = request.POST["application"]
        print ("application_name: ", application_name)

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
        print ('access group: ', access_group_given)
        access_group = access_group_given.split(';')

        accessibility = {}
        accessibility["type"] = accessibility_type
        if (accessibility_type == "group"):
            accessibility["group"] = access_group

        historydb = HistoryDB_MongoDB()
        try:
            num_added_func_eval = historydb.upload_func_eval(json_data, user_info, application_name, accessibility)
            num_added_model_data = historydb.upload_model_data(json_data, user_info, application_name, accessibility)
        except:
            print ("Not able to upload the given data")
            context = {
                    "header": "Something Went Wrong",
                    "message": "Not able to upload the given data"
                    }
            return render(request, 'repo/return.html', context)

        print ("Your data has been uploaded")
        context = {
                "header": "Success",
                "message": "Your data has been uploaded",
                "num_added_func_eval": num_added_func_eval,
                "num_added_model_data": num_added_model_data
                }
        return render(request, 'repo/return.html', context)

class TuningProblems(TemplateView):

    def get(self, request, **kwargs):

        historydb = HistoryDB_MongoDB()
        tuning_problem_list = historydb.load_all_tuning_problems()
        for i in range(len(tuning_problem_list)):
            tuning_problem_list[i]["id"] = i

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

        def get_list_from_file(filename):
            items = []
            with open(filename, "r") as f_in:
                lines = f_in.readlines()
                for line in lines:
                    items.append(line)
            return items

        category_list = ["SuperLU","ScaLAPACK","LAPACK","Desktop Application"]

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

        category_jstree = convert_to_jstree_json(get_data_from_file(os.environ["HISTORYDB_JSON_DATA"]+"/software_data.json", "category_tree"))
        category_tree = get_data_from_file(os.environ["HISTORYDB_JSON_DATA"]+"/software_data.json", "category_tree")
        software_jstree = convert_to_jstree_json(get_data_from_file(os.environ["HISTORYDB_JSON_DATA"]+"/software_data.json", "software_tree"))
        print ("category_tree: ", category_tree)
        print ("category_jstree: ", category_jstree)
        print ("software_jstree: ", software_jstree)

        context = {
                "category_jstree": category_jstree,
                "software_jstree": software_jstree,
                "category_list": category_list,
                }

        return render(request, 'repo/add-tuning-problem.html', context)

    def post(self, request, **kwargs):
        tuning_problem = {}

        tuning_problem["tuning_problem_name"] = request.POST['tuning_problem_name']
        tuning_problem["category"] = request.POST['category_name']
        tuning_problem["description"] = request.POST['tuning_problem_description']

        task_names = request.POST.getlist('task_name')
        task_types = request.POST.getlist('task_type')
        task_descriptions = request.POST.getlist('task_description')
        num_tasks = len(task_names)

        tuning_problem["task_info"] = []
        for i in range(num_tasks):
            tuning_problem["task_info"].append({
                "task_name": task_names[i],
                "task_type": task_types[i],
                "task_description": task_descriptions[i],
                })

        parameter_names = request.POST.getlist('parameter_name')
        parameter_types = request.POST.getlist('parameter_type')
        parameter_descriptions = request.POST.getlist('parameter_description')
        num_parameters = len(parameter_names)

        tuning_problem["parameter_info"] = []
        for i in range(num_parameters):
            tuning_problem["parameter_info"].append({
                "parameter_name": parameter_names[i],
                "parameter_type": parameter_types[i],
                "parameter_description": parameter_descriptions[i]
                })

        output_names = request.POST.getlist('output_name')
        output_types = request.POST.getlist('output_type')
        output_descriptions = request.POST.getlist('output_description')
        num_outputs = len(output_names)

        tuning_problem["output_info"] = []
        for i in range(num_outputs):
            tuning_problem["output_info"].append({
                "output_name": output_names[i],
                "output_type": output_types[i],
                "output_description": output_descriptions[i]
                })

        required_software_names = request.POST.getlist('software_name')
        required_software_types = request.POST.getlist('software_type')
        num_software_packages = len(required_software_names)

        tuning_problem["required_software_info"] = []
        for i in range(num_software_packages):
            tuning_problem["required_software_info"].append({
                "software_name": required_software_names[i],
                "software_type": required_software_types[i]
                })

        print ("tuning_problem: ", tuning_problem)

        user_info = {}
        user_info["user_name"] = request.user.username
        user_info["email"] = request.user.email
        user_info["affiliation"] = request.user.profile.affiliation

        historydb = HistoryDB_MongoDB()
        historydb.add_tuning_problem(tuning_problem, user_info)

        return redirect(reverse_lazy('repo:tuning-problems'))

class AddReproducibleWorkflow(TemplateView):

    def get(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()

        tuning_problem_list = {
                "PDGEQRF": {
                    "task_space": {
                        "m":{
                            }

                        }
                    }
                }

        def get_list_from_file(filename):
            items = []
            with open(filename, "r") as f_in:
                lines = f_in.readlines()
                for line in lines:
                    items.append(line)
            return items

        category_list = ["SuperLU","ScaLAPACK","LAPACK","Desktop Application"]

        context = {
                "category_list": category_list,
                }

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

        print ("user name: ", request.user.username)
        print ("user email: ", request.user.email)

        user_info = {}
        user_info["name"] = request.user.username
        user_info["email"] = request.user.email
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
        #if not request.user.is_authenticated:
        #    return redirect(reverse_lazy('account:login'))

        historydb = HistoryDB_MongoDB()
        machine_info_list = historydb.load_all_machine_info()
        for i in range(len(machine_info_list)):
            machine_info_list[i]["id"] = i

        num_machines = len(machine_info_list)

        context = {
                "machine_info_list" : machine_info_list
                }

        return render(request, 'repo/machines.html', context)

class AddMachine(TemplateView):

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        historydb = HistoryDB_MongoDB()

        def get_list_from_file(filename):
            items = []
            with open(filename, "r") as f_in:
                lines = f_in.readlines()
                for line in lines:
                    items.append(line)
            return items

        country_list = []
        import pycountry
        for country in list(pycountry.countries):
            country_list.append(country.name)
        country_list.sort()

        print (country_list)

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
                "country_list" : country_list,
                }

        return render(request, 'repo/add-machine.html', context)

    def post(self, request, **kwargs):
        machine_info = {}

        machine_name = request.POST['machine_name']
        system_models = request.POST.getlist('system_model_name')
        processor_model_names = request.POST.getlist('processor_model_name')
        num_processor_models = len(processor_model_names)
        num_nodes = request.POST.getlist('num_nodes')
        num_cores = request.POST.getlist('num_cores')
        num_sockets = request.POST.getlist('num_sockets')
        memory_size = request.POST.getlist('memory_size')
        interconnects = request.POST.getlist('interconnect_name')

        print ("machine_name: ", machine_name)
        print ("processor_models: ", processor_model_names)
        print ("interconnects: ", interconnects)

        machine_info["machine_name"] = machine_name
        machine_info["system_model"] = system_models
        machine_info["processor_model"] = {}
        for i in range(num_processor_models):
            processor_model_info = {}
            processor_model_info["num_nodes"] = num_nodes[i]
            processor_model_info["num_cores"] = num_cores[i]
            processor_model_info["num_sockets"] = num_sockets[i]
            processor_model_info["memory_size"] = memory_size[i]
            machine_info["processor_model"][processor_model_names[i]] = processor_model_info
        machine_info["interconnect"] = interconnects

        user_info = {}
        user_info["user_name"] = request.user.username
        user_info["email"] = request.user.email
        user_info["affiliation"] = request.user.profile.affiliation

        historydb = HistoryDB_MongoDB()
        historydb.add_machine_info(machine_info, user_info)

        return redirect(reverse_lazy('repo:machines'))

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

