from django.shortcuts import render

import markdown
from django.utils.safestring import mark_safe

from pathlib import Path
import os

def markdown_to_html(value):
    #extensions = ["nl2br", "fenced_code"]
    extensions = ["fenced_code"]
    return mark_safe(markdown.markdown(value, extensions=extensions))

# Create your views here.
def query(request, document_name):
    documentation_dir = Path(__file__).resolve().parent.parent.parent
    documentation_file = os.path.join(documentation_dir, 'documentation/'+document_name+'.md')
    with open(documentation_file) as f_in:
        markdown_string = f_in.read()
        markdown_html = markdown_to_html(markdown_string)

    context = {
            "document_name" : document_name,
            "markdown_html" : markdown_html
            }

    print (context)

    return render(request, 'documentation/query.html', context)

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

def gptune_user_guide(request):
    fs = FileSystemStorage()

    with fs.open('GPTune_UsersGuide.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
        return response

def gptune_tutorial_slides_ecp2021(request):
    fs = FileSystemStorage()

    with fs.open('GPTune_Tutorial.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
        return response

def gptune_tutorial_slides_cass2026(request):
    fs = FileSystemStorage()

    with fs.open('GPTune_Tutorial-CASS_BoF_2026_compact.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
        return response

def gptune_hands_on(request):
    fs = FileSystemStorage()

    with fs.open('GPTune_HandsOnInstructions.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
        return response

def gptune_crowd_tuning(request):
    fs = FileSystemStorage()

    with fs.open('Crowd_tuning_with_GPTune.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
        return response

from django.shortcuts import redirect
def historydb_user_guide(request):
    return redirect('https://gptune-history-database.readthedocs.io/en/latest/')
