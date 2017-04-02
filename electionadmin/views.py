from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F
from django.db import IntegrityError
import datetime
from random import randint
from django.contrib import messages
from electionvote.models import Candidate
from django.contrib.auth.models import User
from electionsite.settings import SECRET_KEY, EMAIL_FROM
from django.core.mail import send_mail
from .models import Setting
import hashlib
import requests
from django.template import loader
from django.core.files.storage import FileSystemStorage

# Create your views here.

@staff_member_required(login_url='/login/')
@login_required
def dashboard(request):
    candidates = Candidate.objects.all().order_by('-votes')
    voters = User.objects.filter(is_staff=False)
    voted = User.objects.filter(is_active=False)
    voterscount = voters.count()
    votedcount = voted.count()
    if voterscount > 0:
        turnout = votedcount * 100.00 / voterscount
    else:
        turnout = 0.0
    started = Setting.objects.get(name="started").value
    return render(request, "dashboard.html", {'candidates':candidates, 'voters':voters, 'started':started, 'voterscount':voterscount, 'votedcount':votedcount, 'turnout':turnout})

@staff_member_required(login_url='/login/')
@login_required
def generate(request):
    emails = request.POST['emails'].splitlines()
    for i, val in enumerate(emails):
        email = val.replace(" ", "")
        hasher = hashlib.md5()
        seed = SECRET_KEY
        uname = "%s%s" % (email, seed)
        hasher.update(uname)
        username = hasher.hexdigest()[:8]
        password = hasher.hexdigest()[-8:]

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            if email.isdigit():
                #messages.success(request, 'SMS Sent!')
                message = "Hi MAG Member! Here are your credentials for MAG Elections 2017. You can vote at http://%s only once using this account. Thank you and have a good day! - MAG Comelec \nUsername: %s \nPassword: %s\n" % (request.get_host(), username, password)
                post_data = {'message_type':'SEND', 'mobile_number':"63%s" % (email), 'shortcode': '29290469148',
                            'message_id':hasher.hexdigest(), 'message':message, 'client_id':'f3be0f5b7d2abc0ce6fc0dccf7ecc049272af5679fbf5a547429cbaddb0391ff',
                            'secret_key':'757f94e11c41b07a8eb846c20ad1db7fcb98b07a57b85ebe7092c3e4c457f87b'
                            }
                response = requests.post('https://post.chikka.com/smsapi/request', data=post_data)
                content = response.json()
                if int(content['status']) != 200:
                    messages.error(request, 'SMS (%s) Error code: %s, %s. Please try again.' % (email, content['status'], content['message']))
                    user.delete()
            else:
                html_message = loader.render_to_string(
                        'email.html',
                        {
                            'username': username,
                            'password': password,
                            'current_domain': request.get_host(),
                        }
                    )
                status = send_mail('Voter Account Credentials', '', 'MAG Comelec <2017>', [email], html_message=html_message)
                # Need to detect if a sent email was bounced / not sent
                if status == 0:
                    messages.error(request, 'Sending email to %s resulted to an error. Please try again.' % (email))
                    user.delete()
        except IntegrityError as e:
            messages.error(request, '%s is already a voter and not given credentials! If you still want to generate new credentials for it, remove it from the list and add it again.' % (email))

    messages.success(request, 'Successfully added voters.')
    # Get email addresses then hash them to username and password then send to email
    return redirect("/admin/")

@staff_member_required(login_url='/login/')
@login_required
def deletevoter(request, pk):
    edit = User.objects.get(pk=pk)
    edit.delete()
    messages.success(request, 'Successfully deleted voter!')
    return redirect("/admin/")

@staff_member_required(login_url='/login/')
@login_required
def addcandidate(request):
    if request.method == 'POST':
        uploaded_file_url = ''
        if request.FILES['photo']:
            myfile = request.FILES['photo']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
        new = Candidate(name=request.POST['name'], nickname=request.POST['nickname'], description=request.POST['description'], photourl=uploaded_file_url)
        new.save()
        messages.success(request, 'Successfully added candidate!')
    return redirect("/admin/")

@staff_member_required(login_url='/login/')
@login_required
def editcandidate(request):
    if request.method == 'POST':
        edit = Candidate.objects.get(pk=request.POST['pk'])
        edit.name = request.POST['name']
        edit.nickname = request.POST['nickname']
        edit.description = request.POST['description']
        if request.FILES['photo']:
            myfile = request.FILES['photo']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            edit.photourl = fs.url(filename)
        edit.save()
        messages.success(request, 'Successfully updated candidate!')
    return redirect("/admin/")

@staff_member_required(login_url='/login/')
@login_required
def deletecandidate(request, pk):
    edit = Candidate.objects.get(pk=pk)
    edit.delete()
    messages.success(request, 'Successfully deleted candidate!')
    return redirect("/admin/")

@staff_member_required(login_url='/login/')
@login_required
def electionstart(request):
    setting = Setting.objects.get(name="started")
    if int(setting.value) == 1:
        messages.warning(request, 'Election is already running!')
    else:
        setting.value = "1"
        setting.save()
        messages.success(request, 'Successfully started election!')
    return redirect("/admin/")

@staff_member_required(login_url='/login/')
@login_required
def electionstop(request):
    setting = Setting.objects.get(name="started")
    if int(setting.value) == 0:
        messages.warning(request, 'Election is not running!')
    else:
        setting.value = "0"
        setting.save()
        messages.success(request, 'Successfully stopped election!')
    return redirect("/admin/")

@staff_member_required(login_url='/login/')
@login_required
def electionreset(request):
    candidates = Candidate.objects.all().update(votes=0)
    voters = User.objects.all().update(is_active=True)
    setting = Setting.objects.get(name="started")
    setting.value = "0"
    setting.save()
    messages.success(request, 'Successfully reset election!')
    return redirect("/admin/")

@staff_member_required(login_url='/login/')
@login_required
def electionfinalize(request):
    setting = Setting.objects.get(name="started")
    setting.value = "2"
    setting.save()
    messages.success(request, 'Election finalized!')
    return redirect("/admin/")
