from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

def acknowledgement(request):
    return render(request, 'main/acknowledgement.html')

def base(request):
    return render(request, 'main/base.html')
