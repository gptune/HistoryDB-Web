from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib import auth

from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.core.mail import EmailMessage

from django.conf import settings
from django.contrib import messages

import requests
import json

# Create your views here.
def signup(request):
    if request.method == "POST":
        if request.POST["password1"] == request.POST["password2"]:
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()

            if result['success']:
                print ("recaptcah success!")

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
                print ("user activation code: ", activation_code)
                user.profile.activation_code = activation_code

                try:
                    from django.contrib.sites.shortcuts import get_current_site
                    current_site = get_current_site(request)

                    email_subject = "Thanks for Joining GPTune History Database!"
                    email_message = "Hello " + user.first_name + " " + user.last_name + ",\n\n" + \
                            "You are receiving this message because someone is trying to register in the GPTune history database.\n" + \
                            "Please use this code to verify this email and confirm your registration.\n" + \
                            "Code: " + activation_code + "\n\n" + \
                            "Best Regards,\nGPTune-Dev"
                    email = EmailMessage(email_subject, email_message, to=[request.POST["email"]], bcc=['gptune-dev@lbl.gov'], reply_to=['gptune-dev@lbl.gov'])
                    email.send()
                except:
                    print ("Something went wrong with email sending")

                user.save()

                return redirect(reverse_lazy('account:activate', kwargs={'username': user.username}))
            else:
                print ("Invalid reCAPTCHA.")
                return render(request, 'account/signup.html')

        return render(request, 'account/signup.html')

    else:
        context = {
            "GOOGLE_RECAPTCHA_SITE_KEY": settings.GOOGLE_RECAPTCHA_SITE_KEY,
        }

        return render(request, 'account/signup.html', context)

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        #print ("username: ", username)
        #print ("password: ", password)
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
            user.save()

            context = {
                    "header": "Registeration Completed",
                    "message": "Your registration is completed, but please wait for our approval to use our history database!"
                    }
            return render(request, 'account/return.html', context)
            #return redirect(reverse_lazy('main:index'))
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

from django.views.generic import TemplateView

class ProfileDashboard(TemplateView):
    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            user.profile.first_name = request.POST['firstname']
            user.profile.last_name = request.POST['lastname']
            user.profile.position = request.POST['position']
            user.profile.affiliation = request.POST['affiliation']
            user.profile.ecp_member = request.POST['ecp_member']

            print ("firstname: ", request.POST['firstname'])
            print ("lastname: ", request.POST['lastname'])
            print ("position: ", request.POST['position'])
            print ("affiliation: ", request.POST['affiliation'])
            print ("ecp_member: ", request.POST['ecp_member'])

            user.save()

            return redirect(reverse_lazy('main:index'))
        else:
            return render(request, 'account/profile.html', {'error': 'username or password is incorrect'})

        return render(request, 'account/profile.html')

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        #user = User.objects.get(username=request.user.username)
        username = request.user.username
        email = request.user.email
        firstname = request.user.first_name
        lastname = request.user.last_name
        position = request.user.profile.position
        affiliation = request.user.profile.affiliation
        ecp_member = request.user.profile.ecp_member

        context = {
                "username":username,
                "email":email,
                "firstname":firstname,
                "lastname":lastname,
                "position":position,
                "affiliation":affiliation,
                "ecp_member":ecp_member,
                }

        return render(request, 'account/profile.html', context)

class GroupDashboard(TemplateView):
    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        return render(request, 'account/group.html')

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        if not request.user.profile.is_certified:
            context = {
                    "header": "Please Wait!",
                    "message": "You don't have permission to upload (Please wait for our approval)"
                    }
            return render(request, 'repo/return.html', context)

        collaboration_groups_str = request.user.profile.collaboration_groups
        print (collaboration_groups_str)
        context = {
                "collaboration_groups": json.loads(collaboration_groups_str)
                }

        return render(request, 'account/group.html', context)

class AddGroupDashboard(TemplateView):
    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        print ("group_name: ", request.POST['group_name'])
        print ("group_invites: ", request.POST.getlist('group_invites'))
        print ("group_description: ", request.POST['group_description'])

        group_name = request.POST['group_name']
        group_invites = request.POST.getlist('group_invites')
        group_description = request.POST['group_description']

        import random
        activation_code = ""
        for i in range(6):
            activation_code += random.choice('1234567890')

        try:
            #from django.contrib.sites.shortcuts import get_current_site
            #current_site = get_current_site(request)

            for invite in group_invites:
                print (invite)
                if (invite != ''):
                    message = 'Greetings from GPTune-Dev!\n'
                    message += 'You are now invited to a collaboration group in GPTune History Database.\n'
                    message += 'Inviter: ' + request.user.username + '\n'
                    message += 'Inviter Email: ' + request.user.email + '\n'
                    message += 'Collaboration Group: ' + group_name + '\n'
                    message += 'Group Description: ' + group_description + '\n'
                    message += 'Please use this code to confirm.\n'
                    message += 'Code: ' + activation_code

                    email = EmailMessage('Invitation to GPTune Collaboration Group!', message, to=[invite])
                    email.send()
        except:
            print ("Something went wrong with email sending")

        return render(request, 'account/group.html')

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        if not request.user.profile.is_certified:
            context = {
                    "header": "Please Wait!",
                    "message": "You don't have permission to upload (Please wait for our approval)"
                    }
            return render(request, 'repo/return.html', context)

        collaboration_groups_str = request.user.profile.collaboration_groups
        print (collaboration_groups_str)
        context = {
                "collaboration_groups": json.loads(collaboration_groups_str)
                }

        return render(request, 'account/group.html', context)

class UpdateGroupDashboard(TemplateView):
    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        return render(request, 'account/group.html')

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        if not request.user.profile.is_certified:
            context = {
                    "header": "Please Wait!",
                    "message": "You don't have permission to upload (Please wait for our approval)"
                    }
            return render(request, 'repo/return.html', context)

        collaboration_groups_str = request.user.profile.collaboration_groups
        print (collaboration_groups_str)
        context = {
                "collaboration_groups": json.loads(collaboration_groups_str)
                }

        return render(request, 'account/group.html', context)

class DataDashboard(TemplateView):
    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        return render(request, 'account/data.html')

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        return render(request, 'account/data.html')

