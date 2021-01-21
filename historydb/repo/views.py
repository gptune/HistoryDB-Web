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
                perf_data = historydb.load_func_eval_filtered(application_name = application,
                        machine_deps_list = machine_deps_list,
                        software_deps_list = software_deps_list,
                        users_list = users_list)
                num_func_eval = len(perf_data)
                print ("num_func_eval: ", num_func_eval)
                num_evals_per_page = 15
                if (num_func_eval%num_evals_per_page) == 0:
                    num_pages = num_func_eval/num_evals_per_page
                else:
                    num_pages = int(num_func_eval/num_evals_per_page)+1
                print ("num_pages: ", num_pages)
                if (num_pages == 0):
                    num_pages = 1
                current_page = int(request.GET.get("current_page", 0))
                print ("current_page: ", current_page)
                start_index = (current_page)*num_evals_per_page
                end_index = (current_page+1)*num_evals_per_page
                if end_index > num_func_eval:
                    end_index = num_func_eval
                perf_data_web = perf_data[start_index:end_index]
                for i in range(len(perf_data_web)):
                    perf_data_web[i]["id"] = start_index+i
                print (perf_data_web)
            else:
                perf_data_web = []
                num_func_eval = 0
                num_pages = 0
                current_page = 0

            if "model_data" in search_data:
                model_data = historydb.load_model_data_filtered(
                        application_name = application,
                        machine_deps_list = machine_deps_list,
                        software_deps_list = software_deps_list,
                        users_list = users_list)
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
                    "perf_data" : perf_data_web,
                    "num_func_eval" : num_func_eval,
                    "num_pages" : range(num_pages),
                    "model_data" : model_data_web,
                    "num_model_data" : num_model_data,
                    "num_pages_model_data" : range(num_pages_model_data),
                    "current_page_model_data" : current_page_model_data,
                    "machine_deps_avail" : json.dumps(machine_deps_avail),
                    "software_deps_avail" : json.dumps(software_deps_avail),
                    "users_avail" : json.dumps(users_avail),
                    "machine_deps_list" : json.dumps(machine_deps_list),
                    "software_deps_list" : json.dumps(software_deps_list),
                    "users_list" : json.dumps(users_list),
                    "current_page" : current_page,
                    "search_data" : json.dumps(search_data)
                    }

            return render(request, 'repo/dashboard.html', context)

        else:
            historydb = HistoryDB_MongoDB()

            print ("APPLICATION NOT GIVEN: ", application)

            perf_data_web = []
            num_func_eval = 0
            num_pages = 0
            current_page = 0

            model_data_web = []
            num_model_data = 0
            num_pages_model_data = 0
            current_page_model_data = 0

            context = {
                    "application_info" : json.dumps({"application":application}),
                    "application" : application,
                    "applications_avail" : applications_avail,
                    "perf_data" : perf_data_web,
                    "num_func_eval" : num_func_eval,
                    "num_pages" : range(num_pages),
                    "model_data" : model_data_web,
                    "num_model_data" : num_model_data,
                    "num_pages_model_data" : range(num_pages_model_data),
                    "current_page_model_data" : current_page_model_data,
                    "machine_deps_avail" : json.dumps(machine_deps_avail),
                    "software_deps_avail" : json.dumps(software_deps_avail),
                    "users_avail" : json.dumps(users_avail),
                    "machine_deps_list" : json.dumps(machine_deps_avail),
                    "software_deps_list" : json.dumps(software_deps_avail),
                    "users_list" : json.dumps(users_avail),
                    "current_page" : current_page,
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

        if "func_eval" in search_data:
            perf_data = historydb.load_func_eval_filtered(application_name = application,
                    machine_deps_list = machine_deps_list,
                    software_deps_list = software_deps_list,
                    users_list = users_list)
            num_func_eval = len(perf_data)
            num_evals_per_page = 15
            if (num_func_eval%num_evals_per_page) == 0:
                num_pages = num_func_eval/num_evals_per_page
            else:
                num_pages = int(num_func_eval/num_evals_per_page)+1
            if (num_pages == 0):
                num_pages = 1
            current_page = 0
            start_index = (current_page)*num_evals_per_page
            end_index = (current_page+1)*num_evals_per_page
            if end_index > num_func_eval:
                end_index = num_func_eval
            perf_data_web = perf_data[start_index:end_index]
            for i in range(len(perf_data_web)):
                perf_data_web[i]["id"] = start_index+i
        else:
            perf_data_web = []
            num_func_eval = 0
            num_pages = 0
            current_page = 0

        if "model_data" in search_data:
            model_data = historydb.load_model_data_filtered(
                    application_name = application,
                    machine_deps_list = machine_deps_list,
                    software_deps_list = software_deps_list,
                    users_list = users_list)
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
                "perf_data" : perf_data_web,
                "num_func_eval" : num_func_eval,
                "num_pages" : range(num_pages),
                "current_page" : current_page,
                "model_data" : model_data_web,
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

class Export(TemplateView):

    def get(self, request, **kwargs):
        application = request.GET.get("application", "")
        machine_deps_list = json.loads(request.GET.get("machine_deps_list", "{}"))
        software_deps_list = json.loads(request.GET.get("software_deps_list", "{}"))
        users_list = json.loads(request.GET.get("users_list", "{}"))

        historydb = HistoryDB_MongoDB()
        perf_data = historydb.load_func_eval_filtered(application_name = application,
                machine_deps_list = machine_deps_list,
                software_deps_list = software_deps_list,
                users_list = users_list)

        context = { "perf_data" : perf_data, }

        return render(request, 'repo/export.html', context)

class Examples(TemplateView):
    def get(self, request, **kwargs):
        print ("======== Examples GET ========")

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

        return render(request, 'repo/examples.html', context)

    def post(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()

        application = request.POST["application"]

        applications_avail = historydb.get_applications_avail()
        machine_deps_avail = historydb.get_machine_deps_avail()
        software_deps_avail = historydb.get_software_deps_avail()
        users_avail = historydb.get_users_avail()

        machine_deps_list = machine_deps_avail[application]
        software_deps_list = software_deps_avail[application]
        users_list = users_avail[application]

        search_data = ["func_eval"]

        if "func_eval" in search_data:
            perf_data = historydb.load_func_eval_filtered(application_name = application,
                    machine_deps_list = machine_deps_list,
                    software_deps_list = software_deps_list,
                    users_list = users_list)
            num_func_eval = len(perf_data)
            num_evals_per_page = 15
            if (num_func_eval%num_evals_per_page) == 0:
                num_pages = num_func_eval/num_evals_per_page
            else:
                num_pages = int(num_func_eval/num_evals_per_page)+1
            if (num_pages == 0):
                num_pages = 1
            current_page = 0
            start_index = (current_page)*num_evals_per_page
            end_index = (current_page+1)*num_evals_per_page
            if end_index > num_func_eval:
                end_index = num_func_eval
            perf_data_web = perf_data[start_index:end_index]
            for i in range(len(perf_data_web)):
                perf_data_web[i]["id"] = start_index+i
        else:
            perf_data_web = []
            num_func_eval = 0
            num_pages = 0
            current_page = 0

        if "model_data" in search_data:
            model_data = historydb.load_model_data_filtered(
                    application_name = application,
                    machine_deps_list = machine_deps_list,
                    software_deps_list = software_deps_list,
                    users_list = users_list)
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
                "application_info" : json.dumps({"application":application}),
                "applications_avail" : applications_avail,
                "application" : application,
                "perf_data" : perf_data_web,
                "num_func_eval" : num_func_eval,
                "num_pages" : range(num_pages),
                "current_page" : current_page,
                "model_data" : model_data_web,
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

        user_info = {}
        user_info["name"] = request.user.username
        user_info["email"] = request.user.email

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

        historydb = HistoryDB_MongoDB()
        try:
            num_added_func_eval = historydb.upload_func_eval(user_info, application_name, json_data)
            num_added_model_data = historydb.upload_model_data(user_info, application_name, json_data)
        except:
            print ("Not able to upload the given data")
            context = {
                    "header": "Something Went Wrong",
                    "message": "Not able to upload the given data"
                    }
            return render(request, 'repo/return.html', context)

        print ("Your data has been uploaded")
        context = {
                "message": "Your data has been uploaded",
                "num_added_func_eval": num_added_func_eval,
                "num_added_model_data": num_added_model_data
                }
        return render(request, 'repo/return.html', context)

class AddApp(TemplateView):
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

        return render(request, 'repo/addapp.html', context)

    def post(self, request, **kwargs):
        print ("======== Upload POST ========")

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        print ("user name: ", request.user.username)
        print ("user email: ", request.user.email)

        user_info = {}
        user_info["name"] = request.user.username
        user_info["email"] = request.user.email

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
                "header": "Something Went Wrong",
                "message": "The application information has been added"
                }
        return render(request, 'repo/return.html', context)

def query(request, perf_data_uid):
    historydb = HistoryDB_MongoDB()
    perf_data = historydb.load_perf_data_by_uid(perf_data_uid)
    context = { "perf_data" : perf_data, }

    return render(request, 'repo/detail.html', context)

def base(request):
    return render(request, 'repo/base.html')

