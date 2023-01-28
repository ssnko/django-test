from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import auth
import cal.views
from django.urls import reverse

# Create your views here.

def signup(request):
    if request.method == "POST":
        if request.POST['password1']==request.POST['password2']:
            user=User.objects.create_user(request.POST['username'], password=request.POST['password1'])
            auth.login(request,user)
            return render(request,'login.html')
            # return redirect('accounts/login')
    else:
        user_name = request.user.username
        if user_name == '':
            return render(request, 'signup.html')
        else:
            return HttpResponseRedirect(reverse('cal:calendar'))
    return render(request, 'signup.html')

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('cal:calendar')
        else:
            return render(request,'login.html', {'error':'username or password is incorrect'})
    else:
        user_name = request.user.username
        if user_name == '':
            return render(request,'login.html')
        else:
            return HttpResponseRedirect(reverse('cal:calendar'))

def logout(request):
    if request.method == "POST":
        auth.logout(request)
        return render(request,'login.html')
    return render(request,'login.html')