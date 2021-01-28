from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

from django.views.generic import TemplateView
from dbmanager import HistoryDB_MongoDB
import json

class Index(TemplateView):
    def get(self, request, **kwargs):
        print ("======== Examples GET ========")

        historydb = HistoryDB_MongoDB()

        applications_avail = historydb.get_applications_avail()
        applications_avail_per_library = historydb.get_applications_avail_per_library()
        machine_deps_avail = historydb.get_machine_deps_avail()
        software_deps_avail = historydb.get_software_deps_avail()
        users_avail = historydb.get_users_avail()

        user_email = ""
        if request.user.is_authenticated:
            user_email = request.user.email

        context = {
                "applications_avail" : applications_avail,
                "applications_avail_per_library" : applications_avail_per_library,
                "machine_deps_avail" : json.dumps(machine_deps_avail),
                "software_deps_avail" : json.dumps(software_deps_avail),
                "users_avail" : json.dumps(users_avail),
                }

        return render(request, 'main/index.html', context)

    def post(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()

        application = request.POST["application"]

        applications_avail = historydb.get_applications_avail()
        machine_deps_avail = historydb.get_machine_deps_avail()
        software_deps_avail = historydb.get_software_deps_avail()
        users_avail = historydb.get_users_avail()

        user_email = ""
        if request.user.is_authenticated:
            user_email = request.user.email

        machine_deps_list = machine_deps_avail[application]
        software_deps_list = software_deps_avail[application]
        users_list = users_avail[application]

        search_data = ["func_eval"]

        if "func_eval" in search_data:
            perf_data = historydb.load_func_eval_filtered(application_name = application,
                    machine_deps_list = machine_deps_list,
                    software_deps_list = software_deps_list,
                    users_list = users_list,
                    user_email = user_email)
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

def about(request):
    return render(request, 'main/about.html')

def acknowledgement(request):
    return render(request, 'main/acknowledgement.html')

def membership(request):
    return render(request, 'main/membership.html')

def base(request):
    return render(request, 'main/base.html')
