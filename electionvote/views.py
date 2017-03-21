from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.contrib import messages
from .models import Candidate
from django.core.exceptions import ObjectDoesNotExist
from electionadmin.models import Setting

# Create your views here.

def login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active or user.is_staff:
                    try:
                        started = Setting.objects.get(name="started")
                    except ObjectDoesNotExist:
                        started = Setting(name="started", value="0")
                        started.save()
                    if int(started.value) == 1 or user.is_staff:
                        auth_login(request, user)
                        messages.success(request, 'Successfully logged in!')
                        if user.is_staff:
                            return redirect("/admin/")
                        else:
                            return redirect("/")
                    else:
                        messages.error(request, 'The application is currently not accepting any votes.')
                        return redirect("/")
                else:
                    try:
                        started = Setting.objects.get(name="started")
                    except ObjectDoesNotExist:
                        started = Setting(name="started", value="0")
                        started.save()
                    if int(started.value) == 2:
                        auth_login(request, user)
                        messages.success(request, 'Successfully logged in!')
                    else:
                        messages.error(request, 'You have already casted your vote. Kindly wait for the election to end to see the results.')
                    return redirect("/")
            else:
                messages.error(request, 'This account does not exist.')
                return redirect("vote:login")
        else:
            username = ''
            password = ''
            if request.method == 'GET' and 'u' in request.GET:
                username = request.GET['u']
            if request.method == 'GET' and 'p' in request.GET:
                password = request.GET['p']
            return render(request, "login.html", {'username':username, 'password':password})
    else:
        if request.user.is_staff:
            return redirect("/admin/")
        else:
            return redirect("/")

@login_required
def logout(request):
    auth_logout(request)
    return redirect("/")

@login_required
def list(request):
    if request.user.is_staff and not request.user.is_active:
        return redirect("/admin/")
    else:
        if request.user.is_active:
            candidates = Candidate.objects.all()
        else:
            candidates = Candidate.objects.all().order_by('-votes')
        return render(request, "vote.html", {'candidates':candidates, 'user':request.user})

@login_required
def submit(request):
    if request.method == "POST":
        votes = request.POST.getlist('votes[]')
        count = 0
        for i, val in enumerate(votes):
            count = count + 1
        if count <= 7:
            for i, val in enumerate(votes):
                candidate = Candidate.objects.get(pk=int(val))
                candidate.votes = candidate.votes+1
                candidate.save()
            request.user.is_active = False
            request.user.save()
            messages.success(request, 'Vote submitted! Thank you for voting!')
            return redirect("/logout/")
        else:
            messages.error(request, 'Please vote for at most 7 candidates!')
            return redirect("/")
    else:
        return redirect("/")
