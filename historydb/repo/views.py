from django.shortcuts import render

# Create your views here.
from django.views import View
from django.http import HttpResponse
from django.http import JsonResponse

##from django.template import loader
##from .models import PerfFile
##from django.shortcuts import render
##
##class UploadView(View):
##    def get(self, request):
##        #latest_perf_file_list = PerfFile.objects.order_by('-pub_date')[:50]
##        #context = {
##        #        'latest_perf_file_list': latest_perf_file_list,
##        #        }
##        #return render(request, 'repo/index.html', context)
##
##        dummy_data = {
##            'name': 'HistoryDB',
##            'type': 'Repo',
##            'job': 'Service'
##        }
##        return JsonResponse(dummy_data)
##
##    def post(self, request):
##        #perfdata = PerfFile()
##        #perfdata.app_name = "1234" #request.GET['app_name']
##        #perfdata.user_name = "5678" #request.GET['user_name']
##        #perfdata.perf_data = "asdf" #request.GET['perf_data']
##        #perfdata.pub_date = datetime.now()
##        #perfdata.save()
##
##        #print (request.body)
##
##        request_json = json.loads(request.body)
##        print (request_json)
##
##        perfdata = PerfFile()
##        perfdata.app_name = request_json["app_name"]
##        perfdata.user_name = request_json["user_name"]
##        perfdata.perf_data = request_json["perf_data"]
##        perfdata.pub_date = datetime.now()
##        perfdata.save()
##
##        return HttpResponse("Post request")
##
##    def put(self, request):
##        print (request.data)
##        return HttpResponse("Put request")
##
##    def delete(self, request):
##        return HttpResponse("Delete request")
##
##
##def index(request):
##    latest_perf_file_list = PerfFile.objects.order_by('-pub_date')[:50]
##    context = {
##            'latest_perf_file_list': latest_perf_file_list,
##            }
##    return render(request, 'repo/index.html', context)
##
###    latest_question_list = Question.objects.order_by('-pub_date')[:5]
###    template = loader.get_template('polls/index.html')
###    context = {
###            'latest_question_list': latest_question_list,
###            }
###    return HttpResponse(template.render(context, request))
##
##from repo.models import *
##from datetime import datetime
##import json
##from django.forms.models import model_to_dict
##from django.shortcuts import redirect
##from django.urls import reverse_lazy
##
##def query(request, perf_file_id):
##    obj = PerfFile.objects.get(pk = perf_file_id)
##    print (model_to_dict(obj))
##
##    context = {
##        "json_detail": model_to_dict(obj)
##        }
##
##    return render(request, 'repo/detail.html', context)
##    #return JsonResponse(model_to_dict(obj))
##
##    #all_entries = PerfFile.objects.all()
##    #print (model_to_dict(all_entries[0]))
##
##    #fb = PerfFile(name = '####', perf_data = json.dumps('{"a":"b"}'), pub_date = datetime.now())
##    ##fb = PerfFile(name = '####', pub_date = datetime.now())
##    #fb.save()
##
##    #return HttpResponse("SASDFASDF question %s." % perf_file_id)
##
##def upload(request):
##    return render(request, 'repo/upload.html')
##
##def perf_upload(request):
##    perfdata = PerfFile()
##    perfdata.app_name = request.GET['app_name']
##    perfdata.user_name = request.GET['user_name']
##    perfdata.perf_data = request.GET['perf_data']
##    perfdata.pub_date = datetime.now()
##    perfdata.save()
##
##    #fb = PerfFile(app_name = '########', perf_data = json.dumps('{"a":"b"}'), pub_date = datetime.now())
##    #fb.save()
##
##    return redirect(reverse_lazy('repo:index'))


def carousel(request):
    return render(request, 'repo/carousel.html')

#def archive(request):
#    return render(request, 'repo/archive.html')

#def dashboard(request):
#    import os
#    import json
#
#    json_path = "../json"
#    libraries_avail = os.listdir("../json")
#    print (libraries_avail)
#
#    perf_data = {}
#
#    for library_avail in libraries_avail:
#        perf_data[library_avail] = {}
#
#        library_json_path = json_path + "/" + library_avail
#        for application in os.listdir(library_json_path):
#            application_path = library_json_path + "/" + application
#            print (application_path)
#            with open(application_path) as f_in:
#                json_data = json.loads(f_in.read())
#                func_eval_data = json_data["func_eval"]
#
#                perf_data[library_avail][application.split('.')[0]] = func_eval_data
#
#    perf_data_web = perf_data['ScaLAPACK']['PDGEQRF'][:15]
#    print (perf_data_web)
#
#    context = {
#            "libraries_avail" : libraries_avail,
#            "perf_data" : perf_data_web,
#            }
#
#    return render(request, 'repo/dashboard.html', context)

#def dashboard(request):
#    import os
#    import json
#
#    json_path = "../json"
#    libraries_avail = os.listdir("../json")
#    print (libraries_avail)
#    applications_avail = []
#
#    perf_data = {}
#
#    for library_avail in libraries_avail:
#        perf_data[library_avail] = {}
#
#        library_json_path = json_path + "/" + library_avail
#        for application in os.listdir(library_json_path):
#            applications_avail.append(application.split('.')[0])
#            application_path = library_json_path + "/" + application
#            print (application_path)
#            with open(application_path) as f_in:
#                json_data = json.loads(f_in.read())
#                func_eval_data = json_data["func_eval"]
#
#                perf_data[library_avail][application.split('.')[0]] = func_eval_data
#
#    num_func_eval = len(perf_data['ScaLAPACK']['PDGEQRF'])
#    print ("num_func_eval: ", num_func_eval)
#    num_evals_per_page = 15
#    if (num_func_eval%num_evals_per_page) == 0:
#        num_pages = num_func_eval/num_evals_per_page
#    else:
#        num_pages = int(num_func_eval/num_evals_per_page)+1
#    print ("num_pages: ", num_pages)
#
#    current_page = 0
#    start_index = (current_page)*num_evals_per_page
#    end_index = (current_page+1)*num_evals_per_page
#    if end_index > num_func_eval:
#        end_index = num_func_eval
#
#    perf_data_web = perf_data['ScaLAPACK']['PDGEQRF'][start_index:end_index]
#    print (perf_data_web)
#
#    context = {
#            "libraries_avail" : libraries_avail,
#            "applications_avail" : applications_avail,
#            "perf_data" : perf_data_web,
#            "num_func_eval" : num_func_eval,
#            "num_pages" : range(num_pages),
#            "current_page" : current_page
#            }
#
#    return render(request, 'repo/dashboard.html', context)

from django.views.generic import TemplateView
class Dashboard(TemplateView):

    def get(self, request, **kwargs):
        import os
        import json

        application = request.GET.get("application", "")

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

        if application != "":
            num_func_eval = len(perf_data['PDGEQRF'])
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

            perf_data_web = perf_data['PDGEQRF'][start_index:end_index]
            for i in range(len(perf_data_web)):
                perf_data_web[i]["id"] = start_index+i

            print (perf_data_web)

            context = {
                    "application" : application,
                    "applications_avail" : applications_avail,
                    "perf_data" : perf_data_web,
                    "num_func_eval" : num_func_eval,
                    "num_pages" : range(num_pages),
                    "machine_deps_json" : json.dumps({"PDGEQRF":["cori","nersc","3"],"B":["a"]}),
                    "software_deps_json" : json.dumps({"PDGEQRF":[str({"a":"a"}),"!","#"],"B":["a"]}),
                    "users_json" : json.dumps({"PDGEQRF":["user1","user2"],"B":["a"]}),
                    "tempjson" : json.dumps({"PDGEQRF":["1","2","3"],"B":["a"]}),
                    "tempdict" : {"PDGEQRF":["1"],"B":["2"]},
                    "current_page" : current_page
                    }

            return render(request, 'repo/dashboard.html', context)

        else:
            perf_data_web = []
            num_func_eval = 0
            num_pages = 0
            current_page = 0
            context = {
                    "application" : application,
                    "applications_avail" : applications_avail,
                    "perf_data" : perf_data_web,
                    "num_func_eval" : num_func_eval,
                    "num_pages" : range(num_pages),
                    "machine_deps_json" : json.dumps({"PDGEQRF":["cori","nersc","3"],"B":["a"]}),
                    "software_deps_json" : json.dumps({"PDGEQRF":[str({"a":"a"}),"!","#"],"B":["a"]}),
                    "users_json" : json.dumps({"PDGEQRF":["user1","user2"],"B":["a"]}),
                    "tempjson" : json.dumps({"PDGEQRF":["1","2","3"],"B":["a"]}),
                    "tempdict" : {"PDGEQRF":["1"],"B":["2"]},
                    "current_page" : current_page
                    }

            return render(request, 'repo/dashboard.html', context)

        #context = {}
        #return render(request, 'repo/dashboard.html', context)

    def post(self, request, **kwargs):
        application = request.POST["application"]

        if application == "PDGEQRF":
            machines_avail = ["cori", "nersc", "3"]
            for machine in machines_avail:
                if machine in request.POST:
                    print (machine + " has been selected")

            software_deps_avail = [str({"a":"a"}),"!","#"]
            for software_deps in software_deps_avail:
                if software_deps in request.POST:
                    print (software_deps + " has been selected")

            users_avail = ["user1", "user2"]
            for users in users_avail:
                if users in request.POST:
                    print (users + " has been selected")

        import os
        import json

        json_path = "../json"

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

        num_func_eval = len(perf_data['PDGEQRF'])
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

        perf_data_web = perf_data['PDGEQRF'][start_index:end_index]
        print (perf_data_web)

        perf_data_web = perf_data['PDGEQRF'][start_index:end_index]
        for i in range(len(perf_data_web)):
            perf_data_web[i]["id"] = start_index+i

        context = {
                "applications_avail" : applications_avail,
                "application" : application,
                "perf_data" : perf_data_web,
                "num_func_eval" : num_func_eval,
                "num_pages" : range(num_pages),
                "current_page" : current_page,
                "machine_deps_json" : json.dumps({"PDGEQRF":["cori","nersc","3"],"B":["a"]}),
                "software_deps_json" : json.dumps({"PDGEQRF":[str({"a":"a"}),"!","#"],"B":["a"]}),
                "users_json" : json.dumps({"PDGEQRF":["user1","user2"],"B":["a"]})
                }

        return render(request, 'repo/dashboard.html', context)
        #form = LocationForm(request.POST)
        #if form.is_valid():
        #    pass  # do something with form.cleaned_data
        #return render(request, self.template_name, {"form": form})

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
    print ("!!!!")
    print (perf_data_uid)

    perf_data = {}

    json_path = "../json"
    libraries_avail = os.listdir(json_path)
    for library_avail in libraries_avail:
        library_json_path = json_path + "/" + library_avail
        for application in os.listdir(library_json_path):
            application_path = library_json_path + "/" + application
            with open(application_path) as f_in:
                json_data = json.loads(f_in.read())
                func_eval_data = json_data["func_eval"]
                for func_eval in func_eval_data:
                    if func_eval["uid"] == perf_data_uid:
                        perf_data = func_eval

    obj = {} #PerfFile.objects.get(pk = perf_file_id)
    #print (model_to_dict(obj))

    context = {
        "json_detail": perf_data
        }

    return render(request, 'repo/detail.html', context)
    #return JsonResponse(model_to_dict(obj))

    #all_entries = PerfFile.objects.all()
    #print (model_to_dict(all_entries[0]))

    #fb = PerfFile(name = '####', perf_data = json.dumps('{"a":"b"}'), pub_date = datetime.now())
    ##fb = PerfFile(name = '####', pub_date = datetime.now())
    #fb.save()

    #return HttpResponse("SASDFASDF question %s." % perf_file_id)

def examples(request):
    return render(request, 'repo/examples.html')


def base(request):
    return render(request, 'repo/base.html')


