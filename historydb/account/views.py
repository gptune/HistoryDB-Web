from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib import auth

from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.core.mail import EmailMessage

from django.conf import settings
from django.contrib import messages

from dbmanager import HistoryDB_MongoDB

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

class UserGroups(TemplateView):

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))
        else:
            historydb = HistoryDB_MongoDB()
            user_groups = historydb.load_user_collaboration_groups(request.user.email)
            for i in range(len(user_groups)):
                user_groups[i]['no'] = i+1
                for member in user_groups[i]['members']:
                    if member['email'] == request.user.email:
                        user_groups[i]['my_role'] = member['role']
                        break
            print ("USER GROUPS")
            print (user_groups)
            context = { "user_groups" : user_groups }
            return render(request, 'account/user-groups.html', context)

class AddGroup(TemplateView):

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))
        else:
            historydb = HistoryDB_MongoDB()
            context = {
                    "user_email" : request.user.email
                    }
            return render(request, 'account/add-group.html', context)

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))
        else:
            group_name = request.POST['group_name']

            invites_emails = request.POST.getlist('invites_emails')
            invites_roles = request.POST.getlist('invites_roles')

            print ("invites_emails: ", invites_emails)
            print ("invites_roles: ", invites_roles)

            group_details = {}
            group_details['group_name'] = group_name
            group_details['submitter'] = {
                    'user_name': request.user.username,
                    'user_email': request.user.email
                    }
            group_members = []
            for i in range(len(invites_emails)):
                group_members.append({"email":invites_emails[i], "role":invites_roles[i]})
            group_details['members'] = group_members

            import uuid
            group_details["uid"] = str(uuid.uuid1())

            historydb = HistoryDB_MongoDB()
            ret = historydb.add_collaboration_group(group_details)
            if ret == 0:
                context = {
                        "header": "Adding a collaboration group",
                        "message": "Your collaboration group has been added successfully."
                        }
                return render(request, 'account/add-group-return.html', context)
            elif ret == -1:
                context = {
                        "header": "Adding a collaboration group",
                        "message": "Failed: The same group number already exists"
                        }
                return render(request, 'account/add-group-return.html', context)

class UpdateRoles(TemplateView):

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))
        else:
            group_uid = request.POST['group_uid']
            invites_emails = request.POST.getlist('invites_emails')
            invites_roles = request.POST.getlist('invites_roles')

            print ("group_uid: ", group_uid)
            print ("invites_emails: ", invites_emails)
            print ("invites_roles: ", invites_roles)

            group_members = []
            for i in range(len(invites_emails)):
                group_members.append({"email":invites_emails[i], "role":invites_roles[i]})

            historydb = HistoryDB_MongoDB()
            ret = historydb.update_group_members(group_uid, group_members)
            if ret == 0:
                user_groups = historydb.load_user_collaboration_groups(request.user.email)
                for i in range(len(user_groups)):
                    user_groups[i]['no'] = i+1
                    for member in user_groups[i]['members']:
                        if member['email'] == request.user.email:
                            user_groups[i]['my_role'] = member['role']
                            break
                print ("USER GROUPS")
                print (user_groups)
                context = { "user_groups" : user_groups }
                return render(request, 'accunt/user-groups.html', context)
            elif ret == -1:
                context = {
                        "header": "Updating group members",
                        "message": "Updating group members was unsuccessful."
                        }
                return render(request, 'account/add-group-return.html', context)
            else:
                context = {
                        "header": "Updating group members",
                        "message": "Updating group members was unsuccessful."
                        }
                return render(request, 'account/add-group-return.html', context)

class InviteMember(TemplateView):

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))
        else:
            group_uid = request.POST['group_uid']
            invite_email = request.POST['invite_email']
            invite_role = request.POST['invite_role']

            print ("group_uid: ", group_uid)
            print ("invite_email: ", invite_email)
            print ("invite_role: ", invite_role)

            historydb = HistoryDB_MongoDB()

            ret = historydb.add_group_member(group_uid, invite_email, invite_role)
            if ret == 0:
                user_groups = historydb.load_user_collaboration_groups(request.user.email)
                for i in range(len(user_groups)):
                    user_groups[i]['no'] = i+1
                    for member in user_groups[i]['members']:
                        if member['email'] == request.user.email:
                            user_groups[i]['my_role'] = member['role']
                            break
                print ("USER GROUPS")
                print (user_groups)
                context = { "user_groups" : user_groups }
                return render(request, 'account/user-groups.html', context)
            elif ret == -1:
                context = {
                        "header": "Adding a group member",
                        "message": "Additing a group member was unsuccessful."
                        }
                return render(request, 'account/add-group-return.html', context)

class DataDashboard(TemplateView):
    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        return render(request, 'account/data.html')

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('account:login'))

        return render(request, 'account/data.html')

