from django.shortcuts import render

# Create your views here.
from django.views import View
from django.http import HttpResponse
from django.http import JsonResponse

def carousel(request):
    return render(request, 'repo/carousel.html')

from django.views.generic import TemplateView

class Dashboard(TemplateView):
    def get(self, request, **kwargs):
        print ("======== Dashboard GET ========")

        import os
        import json

        from dbmanager import HistoryDB_MongoDB
        historydb = HistoryDB_MongoDB()

        applications_avail = historydb.get_applications_avail()
        machine_deps_avail = historydb.get_machine_deps_avail()
        software_deps_avail = historydb.get_software_deps_avail()
        users_avail = historydb.get_users_avail()

        application = request.GET.get("application", "")

        if application != "":
            print ("APPLICATION GIVEN: ", application)

            import ast
            machine_deps_list = ast.literal_eval(request.GET.get("machine_deps_list", ""))
            software_deps_list = ast.literal_eval(request.GET.get("software_deps_list", ""))
            users_list = ast.literal_eval(request.GET.get("users_list", ""))

            import os
            import json
            from dbmanager import HistoryDB_MongoDB
            historydb = HistoryDB_MongoDB()

            search_data = ast.literal_eval(request.GET.get("search_data", ""))

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
                    "machine_deps_list" : json.dumps(machine_deps_list),
                    "software_deps_list" : json.dumps(software_deps_list),
                    "users_list" : json.dumps(users_list),
                    #"machine_deps_avail" : json.dumps({"PDGEQRF":["cori","nersc","3"],"ij":["cori","intel72"]}),
                    #"software_deps_avail" : json.dumps({"PDGEQRF":[str({"a":"a"}),"!","#"],"ij":[]}),
                    #"users_avail" : json.dumps({"PDGEQRF":["user1","user2"],"ij":["user3"]}),
                    "current_page" : current_page,
                    "search_data" : json.dumps(search_data)
                    }

            return render(request, 'repo/dashboard.html', context)

        else:
            import os
            import json

            from dbmanager import HistoryDB_MongoDB
            historydb = HistoryDB_MongoDB()

            print ("APPLICATION NOT GIVEN: ", application)

            #applications_avail = historydb.get_applications_avail()
            #machine_deps_avail = historydb.get_machine_deps_avail()
            #print (machine_deps_avail)
            #software_deps_avail = historydb.get_software_deps_avail()
            #users_avail = historydb.get_users_avail()

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
        import os
        import json

        from dbmanager import HistoryDB_MongoDB
        historydb = HistoryDB_MongoDB()

        applications_avail = historydb.get_applications_avail()
        print (applications_avail)
        machine_deps_avail = historydb.get_machine_deps_avail()
        print (machine_deps_avail)
        software_deps_avail = historydb.get_software_deps_avail()
        users_avail = historydb.get_users_avail()

        application = request.POST["application"]

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

def display(request):
    import os
    import json

    json_path = "../json"
    libraries_avail = os.listdir("../json")
    print (libraries_avail)

    applications_avail = []

    perf_data = {}

    for library_avail in libraries_avail:
        perf_data[library_avail] = {}

        library_json_path = json_path + "/" + library_avail
        for application in os.listdir(library_json_path):
            applications_avail.append(application.split('.')[0])
            application_path = library_json_path + "/" + application
            print (application_path)
            with open(application_path) as f_in:
                json_data = json.loads(f_in.read())
                func_eval_data = json_data["func_eval"]

                perf_data[library_avail][application.split('.')[0]] = func_eval_data

    num_func_eval = len(perf_data['ScaLAPACK']['PDGEQRF'])
    print ("num_func_eval: ", num_func_eval)
    num_evals_per_page = 15
    if (num_func_eval%num_evals_per_page) == 0:
        num_pages = num_func_eval/num_evals_per_page
    else:
        num_pages = int(num_func_eval/num_evals_per_page)+1
    print ("num_pages: ", num_pages)

    current_page = 0
    start_index = (current_page)*num_evals_per_page
    end_index = (current_page+1)*num_evals_per_page
    if end_index > num_func_eval:
        end_index = num_func_eval

    perf_data_web = perf_data['ScaLAPACK']['PDGEQRF'][start_index:end_index]
    print (perf_data_web)

    context = {
            "libraries_avail" : libraries_avail,
            "applications_avail" : applications_avail,
            "perf_data" : perf_data_web,
            "num_func_eval" : num_func_eval,
            "num_pages" : range(num_pages),
            "current_page" : current_page
            }

    return render(request, 'repo/display.html', context)

from datetime import datetime
import os
import json
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.urls import reverse_lazy

def query(request, perf_data_uid):
    import os
    import json
    from dbmanager import HistoryDB_MongoDB

    historydb = HistoryDB_MongoDB()
    perf_data = historydb.load_perf_data_by_uid(perf_data_uid)
    context = { "perf_data" : perf_data, }

    return render(request, 'repo/detail.html', context)

class Export(TemplateView):

    def get(self, request, **kwargs):
        import os
        import json
        from dbmanager import HistoryDB_MongoDB

        application = request.GET.get("application", "")
        machine_deps_list = json.loads(request.GET.get("machine_deps_list", "{}"))
        software_deps_list = json.loads(request.GET.get("software_deps_list", "{}"))
        users_list = json.loads(request.GET.get("users_list", "{}"))

        historydb = HistoryDB_MongoDB()
        perf_data = historydb.load_func_eval(application_name = application,
                machine_deps_list = machine_deps_list,
                software_deps_list = software_deps_list)

        context = { "perf_data" : perf_data, }

        return render(request, 'repo/export.html', context)


########

class Examples(TemplateView):
    def get(self, request, **kwargs):
        print ("======== Examples GET ========")

        import os
        import json
        from dbmanager import HistoryDB_MongoDB

        historydb = HistoryDB_MongoDB()

        #applications_avail = historydb.get_applications_avail()
        applications_avail_per_library = historydb.get_applications_avail_per_library()
        #print (applications_avail_per_library)
        machine_deps_avail = historydb.get_machine_deps_avail()
        software_deps_avail = historydb.get_software_deps_avail()
        users_avail = historydb.get_users_avail()

        context = {
                "applications_avail_per_library" : applications_avail_per_library,
                "machine_deps_avail" : json.dumps(machine_deps_avail),
                "software_deps_avail" : json.dumps(software_deps_avail),
                "users_avail" : json.dumps(users_avail),
                }

        return render(request, 'repo/examples.html', context)

    def post(self, request, **kwargs):
        import os
        import json
        from dbmanager import HistoryDB_MongoDB

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

def base(request):
    return render(request, 'repo/base.html')
