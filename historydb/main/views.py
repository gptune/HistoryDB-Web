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

        tuning_problems_avail_per_category = historydb.load_tuning_problems_per_category()
        print ("tuning_problems_avail_per_category: ", tuning_problems_avail_per_category)

        user_email = ""
        if request.user.is_authenticated:
            user_email = request.user.email

        context = {
                "tuning_problems_avail_per_category": tuning_problems_avail_per_category,
                }

        return render(request, 'main/index.html', context)

    def post(self, request, **kwargs):
        historydb = HistoryDB_MongoDB()

        tuning_problem_unique_name = request.POST["tuning_problem_unique_name"]

        tuning_problems_avail = historydb.load_all_tuning_problems()
        machine_configurations_avail = historydb.get_machine_configurations_avail()
        software_configurations_avail = historydb.get_software_configurations_avail()
        user_configurations_avail = historydb.get_user_configurations_avail()

        machine_configurations_list = machine_configurations_avail[tuning_problem_unique_name]
        software_configurations_list = software_configurations_avail[tuning_problem_unique_name]
        user_configurations_list = user_configurations_avail[tuning_problem_unique_name]

        user_email = ""
        if request.user.is_authenticated:
            user_email = request.user.email

        search_options = ['func_eval']

        if "func_eval" in search_options:
            func_eval_list = historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    user_configurations_list = user_configurations_list,
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

        if "model_data" in search_options:
            model_data = historydb.load_model_data_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    user_configurations_list = user_configurations_list,
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
                "model_data_list" : model_data_web,
                "num_model_data" : num_model_data,
                "num_pages_model_data" : range(num_pages_model_data),
                "current_page_model_data" : current_page_model_data,
                "machine_configurations_list" : json.dumps(machine_configurations_list),
                "software_configurations_list" : json.dumps(software_configurations_list),
                "user_configurations_list" : json.dumps(user_configurations_list),
                "search_options" : json.dumps(search_options)
                }

        return render(request, 'repo/dashboard.html', context)

def about(request):
    return render(request, 'main/about.html')

def publications(request):
    return render(request, 'main/publications.html')

def acknowledgement(request):
    return render(request, 'main/acknowledgement.html')

def membership(request):
    return render(request, 'main/membership.html')

def base(request):
    return render(request, 'main/base.html')
