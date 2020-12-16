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
def index(request):
    return render(request, 'documentation/index.html')

def query(request, document_name):
    documentation_dir = Path(__file__).resolve().parent.parent.parent
    documentation_file = os.path.join(documentation_dir, 'documentation/'+document_name+'.md')
    with open(documentation_file) as f_in:
        markdown_string = f_in.read()
        markdown_html = markdown_to_html(markdown_string)

    context = {
            "markdown_html" : markdown_html
            }

    print (context)

    return render(request, 'documentation/query.html', context)

