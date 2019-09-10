from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Record

# Create your views here.


def logon(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            filter_result = User.objects.filter(username=username)
            if filter_result:
                message = "Error : The username already exists"
                return render(request, 'logon.html', {"message": message})
            else:
                User.objects.create_user(username=username, password=password)
                return redirect('/login/')
        elif not username:
            message = "Require a username"
            return render(request, 'logon.html', {"message": message})
        elif not password:
            message = "Require a password"
            return render(request, 'logon.html', {"message": message})
    return render(request, 'logon.html')


def login(request):
    if request.method == "POST":
        password = request.POST.get('password')
        username = request.POST.get('username')
        if username and password:
            user = User.objects.filter(username=username).first()
            if not user:
                message = "Error : This user doesn't exist"
                return render(request, 'login.html', {"message": message})
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return redirect('/home/')
            else:
                message = "Error : Wrong password"
                return render(request, 'login.html', {"message": message})
        elif not username:
            message = "Require a username"
            return render(request, 'login.html', {"message": message})
        elif not password:
            message = "Require a password"
            return render(request, 'login.html', {"message": message})
    return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return redirect('/login/')


def home(request):
    return render(request, 'home.html')


def history(request):
    record_list = Record.objects.all()
    #需要给record_list排个序
    #models中的datatime属性还要改一改
    paginator = Paginator(record_list, 1)

    page = request.GET.get('page', 1)
    current_page = int(page)
    upload_path = ""
    try:
        record_list = paginator.page(page)
        for i in record_list:
            upload_path = '/media/'+str(i.upload)
    except PageNotAnInteger:
        record_list = paginator.page(1)
    except EmptyPage:
        record_list = paginator.page(paginator.num_pages)
    return render(request, 'history.html', locals())


def upload(request):
    if request.method == 'POST':
        img = request.FILES.get('img')
        Record.objects.create(upload=img)
        return render(request, 'home.html')

def seg():
    pass

def det():
    pass

def sty():
    pass






