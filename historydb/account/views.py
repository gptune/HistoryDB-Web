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
                    password = request.POST["password1"],
                    is_active = False)

            user.first_name = request.POST["firstname"]
            user.last_name = request.POST["lastname"]
            user.profile.position = request.POST["position"]
            user.profile.affiliation = request.POST["affiliation"]
            user.profile.ecp_member = request.POST["ecp_member"]

            try:
                from django.contrib.sites.shortcuts import get_current_site
                current_site = get_current_site(request)

                email = EmailMessage('Greetings from GPTune History Database', 'Greetings from GPTune History Database\nYou are now registered in the GPTune History Database Web!', to=[request.POST["email"]])
                email.send()
            except:
                print ("Something went wrong with email sending")

            user.save()

            #auth.login(request, user)

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
