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
        import os
        import json

        from dbmanager import HistoryDB
        historydb = HistoryDB()

        applications_avail = historydb.get_applications_avail()
        print (applications_avail)
        machine_deps_avail = historydb.get_machine_deps_avail()
        #print (machine_deps_avail)
        software_deps_avail = historydb.get_software_deps_avail()
        users_avail = historydb.get_users_avail()

        application = request.GET.get("application", "")

        values = (request.GET.getlist('machine_deps_list'))
        print ("========!!@#!@#!@#!@#!@#!@#!@#")
        print (values)
        #print (request.POST.getlist('software_deps_list'))

        if application != "":
            print ("APPLICATION GIVEN: ", application)

            applications_avail = []
            perf_data = {}

            json_path = "../json"
            for application_file in os.listdir(json_path):
                applications_avail.append(application_file.split('.')[0])
                application_path = json_path + "/" + application_file
                print (application_path)
                with open(application_path) as f_in:
                    json_data = json.loads(f_in.read())
                    func_eval_data = json_data["func_eval"]
                    perf_data[application_file.split('.')[0]] = func_eval_data

            num_func_eval = len(perf_data[application])
            print ("num_func_eval: ", num_func_eval)
            num_evals_per_page = 15
            if (num_func_eval%num_evals_per_page) == 0:
                num_pages = num_func_eval/num_evals_per_page
            else:
                num_pages = int(num_func_eval/num_evals_per_page)+1
            print ("num_pages: ", num_pages)

            current_page = int(request.GET.get("current_page", 0))
            print ("current_page: ", current_page)
            start_index = (current_page)*num_evals_per_page
            end_index = (current_page+1)*num_evals_per_page
            if end_index > num_func_eval:
                end_index = num_func_eval

            perf_data_web = perf_data[application][start_index:end_index]
            for i in range(len(perf_data_web)):
                perf_data_web[i]["id"] = start_index+i

            print (perf_data_web)

            context = {
                    "application_info" : json.dumps({"application":application}),
                    "application" : application,
                    "applications_avail" : applications_avail,
                    "perf_data" : perf_data_web,
                    "num_func_eval" : num_func_eval,
                    "num_pages" : range(num_pages),
                    "machine_deps_avail" : json.dumps(machine_deps_avail),
                    "software_deps_avail" : json.dumps(software_deps_avail),
                    "users_avail" : json.dumps(users_avail),
                    "machine_deps_list" : json.dumps(machine_deps_avail),
                    "software_deps_list" : json.dumps(software_deps_avail),
                    "users_list" : json.dumps(users_avail),
                    #"machine_deps_avail" : json.dumps({"PDGEQRF":["cori","nersc","3"],"ij":["cori","intel72"]}),
                    #"software_deps_avail" : json.dumps({"PDGEQRF":[str({"a":"a"}),"!","#"],"ij":[]}),
                    #"users_avail" : json.dumps({"PDGEQRF":["user1","user2"],"ij":["user3"]}),
                    "current_page" : current_page
                    }

            return render(request, 'repo/dashboard.html', context)

        else:
            import os
            import json

            from dbmanager import HistoryDB
            historydb = HistoryDB()

            print ("APPLICATION NOT GIVEN: ", application)

            #applications_avail = historydb.get_applications_avail()
            #machine_deps_avail = historydb.get_machine_deps_avail()
            #print (machine_deps_avail)
            #software_deps_avail = historydb.get_software_deps_avail()
            #users_avail = historydb.get_users_avail()

            perf_data = {}

            perf_data_web = []
            num_func_eval = 0
            num_pages = 0
            current_page = 0
            context = {
                    "application_info" : json.dumps({"application":application}),
                    "application" : application,
                    "applications_avail" : applications_avail,
                    "perf_data" : perf_data_web,
                    "num_func_eval" : num_func_eval,
                    "num_pages" : range(num_pages),
                    "machine_deps_avail" : json.dumps(machine_deps_avail),
                    "software_deps_avail" : json.dumps(software_deps_avail),
                    "users_avail" : json.dumps(users_avail),
                    "machine_deps_list" : json.dumps(machine_deps_avail),
                    "software_deps_list" : json.dumps(software_deps_avail),
                    "users_list" : json.dumps(users_avail),
                    "current_page" : current_page
                    }

            return render(request, 'repo/dashboard.html', context)

    def post(self, request, **kwargs):
        import os
        import json

        from dbmanager import HistoryDB
        historydb = HistoryDB()

        applications_avail = historydb.get_applications_avail()
        print (applications_avail)
        machine_deps_avail = historydb.get_machine_deps_avail()
        #print (machine_deps_avail)
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

        perf_data = historydb.load_func_eval(application_name = application,
                machine_deps_list = machine_deps_list,
                software_deps_list = software_deps_list)

        #applications_avail = []
        #json_path = "../json"
        #for application_file in os.listdir(json_path):
        #    applications_avail.append(application_file.split('.')[0])

        num_func_eval = len(perf_data)
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

        perf_data_web = perf_data[start_index:end_index]
        for i in range(len(perf_data_web)):
            perf_data_web[i]["id"] = start_index+i

        context = {
                "application_info" : json.dumps({"application":application}),
                "applications_avail" : applications_avail,
                "application" : application,
                "perf_data" : perf_data_web,
                "num_func_eval" : num_func_eval,
                "num_pages" : range(num_pages),
                "current_page" : current_page,
                "machine_deps_avail" : json.dumps(machine_deps_avail),
                "software_deps_avail" : json.dumps(software_deps_avail),
                "users_avail" : json.dumps(users_avail),
                "machine_deps_list" : json.dumps(machine_deps_list),
                "software_deps_list" : json.dumps(software_deps_list),
                "users_list" : json.dumps(users_list)
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
    from dbmanager import HistoryDB

    historydb = HistoryDB()
    func_eval = historydb.load_func_eval_by_uid(perf_data_uid)
    context = { "func_eval" : func_eval, }

    return render(request, 'repo/detail.html', context)

class Export(TemplateView):

    def get(self, request, **kwargs):
        import os
        import json
        from dbmanager import HistoryDB

        application = request.GET.get("application", "")
        machine_deps_list = json.loads(request.GET.get("machine_deps_list", "{}"))
        software_deps_list = json.loads(request.GET.get("software_deps_list", "{}"))
        users_list = json.loads(request.GET.get("users_list", "{}"))

        historydb = HistoryDB()
        perf_data = historydb.load_func_eval(application_name = application,
                machine_deps_list = machine_deps_list,
                software_deps_list = software_deps_list)

        context = { "perf_data" : perf_data, }

        return render(request, 'repo/export.html', context)

def examples(request):
    return render(request, 'repo/examples.html')

def base(request):
    return render(request, 'repo/base.html')

