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

            # 6-digit activation code
            import random
            random.seed()
            activation_code = ""
            for i in range(6):
                activation_code += random.choice('1234567890')
            user.profile.activation_code = activation_code

            try:
                #from django.contrib.auth.tokens import default_token_generator
                #user_token = default_token_generator.make_token(user)
                #print ("token: ", user_token)

                from django.contrib.sites.shortcuts import get_current_site
                current_site = get_current_site(request)

                message = 'Greetings from GPTune History Database!\n'
                message += 'You are registered in the GPTune History Database Web.\n'
                message += 'Please use this code to activate your account.\n'
                message += 'Code: ' + activation_code

                email = EmailMessage('Greetings from GPTune History Database', message, to=[request.POST["email"]])
                email.send()
            except:
                print ("Something went wrong with email sending")

            user.save()

            return redirect(reverse_lazy('account:activate', kwargs={'username': user.username}))
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

def activate(request, username):
    if request.method == "POST":
        print ("POST")

        activation_code = ""
        activation_code += request.POST['n1']
        activation_code += request.POST['n2']
        activation_code += request.POST['n3']
        activation_code += request.POST['n4']
        activation_code += request.POST['n5']
        activation_code += request.POST['n6']
        print (activation_code)

        print ("username: ", username)
        user = User.objects.get(username=username)
        print ("user's code: ", user.profile.activation_code)

        if (activation_code == user.profile.activation_code):
            user.is_active = True
            return redirect(reverse_lazy('main:index'))
        else:
            return redirect(reverse_lazy('account:activate', kwargs={'username': user.username}))

    elif request.method == "GET":
        try:
            user = User.objects.get(username=username)
            if (user.is_active == True):
                return redirect(reverse_lazy('main:index'))

            context = { "username": username }
            return render(request, 'account/activate.html', context)
        except:
            return redirect(reverse_lazy('main:index'))

