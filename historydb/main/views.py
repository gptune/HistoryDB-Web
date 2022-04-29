from django.shortcuts import render
from django.views.generic import TemplateView
from dbmanager import HistoryDB_MongoDB
from django.contrib.auth import get_user_model
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

        User = get_user_model()
        user_count = len(User.objects.all())

        context = {
                "tuning_problems_avail_per_category": tuning_problems_avail_per_category,
                "stats": {
                        "num_tuning_problems": historydb.get_num_tuning_problems(),
                        "num_function_evaluations": historydb.get_num_function_evaulations(),
                        "num_users": user_count
                    }
                }

        return render(request, 'main/index.html', context)

    def post(self, request, **kwargs):

        historydb = HistoryDB_MongoDB()

        tuning_problems_avail = historydb.load_all_tuning_problems()

        tuning_problem_unique_name = request.POST["tuning_problem_unique_name"]
        if tuning_problem_unique_name == "":
            context = {
                "header": "Something went wrong",
                "message": "Please choose a tuning problem to search"
            }
            return render(request, 'main/error.html', context)

        machine_configurations_avail = historydb.get_machine_configurations_avail()
        software_configurations_avail = historydb.get_software_configurations_avail()
        outputs_avail = historydb.get_outputs_avail()
        user_configurations_avail = historydb.get_user_configurations_avail()
        tuning_problem_info = historydb.get_tuning_problem_info(tuning_problem_unique_name)

        machine_configurations_list = machine_configurations_avail[tuning_problem_unique_name]
        software_configurations_list = software_configurations_avail[tuning_problem_unique_name]
        output_options = outputs_avail[tuning_problem_unique_name]
        user_configurations_list = user_configurations_avail[tuning_problem_unique_name]

        user_email = request.user.email if request.user.is_authenticated else ""

        search_options = ['func_eval']

        if "func_eval" in search_options:
            func_eval_list = historydb.load_func_eval_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    output_options = output_options,
                    user_configurations_list = user_configurations_list,
                    user_email = user_email)
            num_func_eval = len(func_eval_list)
            for i in range(num_func_eval):
                func_eval_list[i]["id"] = i
        else:
            func_eval_list = []
            num_func_eval = 0

        if "surrogate_model" in search_options:
            surrogate_model_list = historydb.load_surrogate_models_filtered(tuning_problem_unique_name = tuning_problem_unique_name,
                    machine_configurations_list = machine_configurations_list,
                    software_configurations_list = software_configurations_list,
                    output_options = output_options,
                    user_configurations_list = user_configurations_list,
                    user_email = user_email)
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

        print ("machine_configurations_avail: ", machine_configurations_avail)
        print ("software_configurations_avail: ", software_configurations_avail)
        print ("outputs_avail: ", outputs_avail)
        print ("user_configurations_avail: ", user_configurations_avail)

        print ("tuning_problem_unique_name: ", tuning_problem_unique_name)
        print ("tuning_problem_info: ", tuning_problem_info)
        print ("machine_configurations_list: ", machine_configurations_list)
        print ("software_configurations_list: ", software_configurations_list)
        print ("user_configurations_list: ", user_configurations_list)
        print ("output_options: ", output_options)
        print ("search_options: ", search_options)

        print ("num_surrogate_models: ", num_surrogate_models)

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

def about(request):
    return render(request, 'main/about.html')

def publications(request):
    return render(request, 'main/publications.html')

def acknowledgement(request):
    return render(request, 'main/acknowledgement.html')

def membership(request):
    return render(request, 'main/membership.html')

def gptune_tutorial_ecp2021(request):
    return render(request, 'main/ecp2021.html')

def gptune_tutorial_ecp2022(request):
    return render(request, 'main/ecp2022.html')

def release(request):
    return render(request, 'main/release.html')

def base(request):
    return render(request, 'main/base.html')
