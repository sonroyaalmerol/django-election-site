from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F
import datetime
from random import randint
from django.contrib import messages
from electionvote.models import Candidate
from django.contrib.auth.models import User
from electionsite.settings import SECRET_KEY, EMAIL_FROM
from django.core.mail import send_mail
from .models import Setting
import hashlib

# Create your views here.

@staff_member_required(login_url='/login/')
@login_required
def dashboard(request):
    candidates = Candidate.objects.all().order_by('-votes')
    voters = User.objects.filter(is_staff=False)
    started = Setting.objects.get(name="started").value
    return render(request, "dashboard.html", {'candidates':candidates, 'voters':voters, 'started':started})

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

        user = User.objects.create_user(username, email, password)
        user.save()

    send_mail('Voter Account Credentials', 'Here are your credentials for voting<br>Please be reminded that you can only vote once using this account.<br><br>Username: %s<br>Password: %s<br><br>Use these credentials to login! Thank you!<br>' % (username, password), EMAIL_FROM, emails, fail_silently=False)

    messages.success(request, 'Successfully added voters!')
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
        new = Candidate(name=request.POST['name'], nickname=request.POST['nickname'], description=request.POST['description'])
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
    messages.success(request, 'Successfully reset election!')
    return redirect("/admin/")
