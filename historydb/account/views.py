from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib import auth

from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.core.mail import EmailMessage

# Create your views here.
def signup(request):
    if request.method == "POST":
        if request.POST["password1"] == request.POST["password2"]:
            #print (request.POST["password1"])
            user = User.objects.create_user(
                    username = request.POST["username"],
                    email = request.POST["email"],
                    password = request.POST["password1"])
            auth.login(request, user)

            try:
                email = EmailMessage('Greetings from GPTune History Database', 'Greetings from GPTune History Database\nYou are now registered in the GPTune History Database Web!', to=[request.POST["email"]])
                email.send()
            except:
                print ("Something went wrong with email sending")

            return redirect(reverse_lazy('main:index'))
        return render(request, 'account/signup.html')

    return render(request, 'account/signup.html')

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect(reverse_lazy('main:index'))
        else:
            return render(request, 'login.html', {'error': 'username or password is incorrect'})
    else:
        return render(request, 'account/login.html')

def logout(request):
    auth.logout(request)
    return redirect(reverse_lazy('main:index'))
