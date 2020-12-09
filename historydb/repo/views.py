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

def archive(request):
    return render(request, 'repo/archive.html')

def dashboard(request):
    return render(request, 'repo/dashboard.html')

def examples(request):
    return render(request, 'repo/examples.html')
