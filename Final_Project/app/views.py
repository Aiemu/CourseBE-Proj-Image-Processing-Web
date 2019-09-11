from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Record
from nn import Segmentation, Detection, StyleTransition
from django.http import JsonResponse, HttpResponse
from tempfile import TemporaryFile
from os.path import basename
from urllib.parse import urlsplit
from django.core.files import File
import json
import requests

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
    messages.success(request,"Please log in")
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
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, 'home.html')

def history(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    username = request.user.username
    get_data(request)
    record_list = Record.objects.filter(username=username).order_by("id")
    paginator = Paginator(record_list, 1)
    page = request.POST.get('page', 1)
    current_page = int(page)
    upload_path = ""
    try:
        record_list = paginator.page(page)
        for i in record_list:
            upload_path = '/media/'+str(i.upload)
            dispose_path = '/media/out/'+i.seg+i.sty+i.det
    except PageNotAnInteger:
        record_list = paginator.page(1)
    except EmptyPage:
        record_list = paginator.page(paginator.num_pages)
    return render(request, 'history.html', locals())

def get_data(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    username = request.user.username
    dataset =[]
    record_list = Record.objects.filter(username=username)
    i = 0
    for record in record_list:
        i +=  1
        output = record.seg + record.det + record.sty
        dataset.append({'id': record.id, 'time': str(record.time), 'operation': record.operation, 'upload': str(record.upload), 'output': output})
    js = json.dumps({"total": i, "totalNotFiltered": i, "rows": dataset}, sort_keys=True, indent=4, separators=(',', ': '))
    return HttpResponse(js)

def upload(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if request.method == 'POST':
        img = request.FILES.get('img')
        username = request.user.username
        Record.objects.create(upload=img, username=username)
        return render(request, 'home.html')

def download_to_file_field(url, field):   
    with TemporaryFile() as tf:        
        r = requests.get(url, stream=True)        
        for chunk in r.iter_content(chunk_size=4096):            
            tf.write(chunk)        
        tf.seek(0)        
        field.save(basename(urlsplit(url).path), File(tf))


def seg(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if request.method == 'POST':
        img = request.FILES.get('img')
        if not img:
            return render(request, 'home.html')
        username = request.user.username
        operation = "Segmentation"
        record = Record.objects.create(upload=img, username=username, operation=operation)
        path = str(record.upload)
        ret = Segmentation.segmentation(path)
        record.seg = ret
        upload_path_1 = '/media/' + str(record.upload)
        seg_path = '/media/' + record.seg + record.sty + record.det
        if not seg_path:
            return render(request, 'home.html')
        record.save()
        return render(request, 'home.html',locals())


def segurl(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if request.method == 'POST':
        username = request.user.username
        operation = "Segmentation"
        record = Record.objects.create(username=username, operation=operation)
        url = request.POST.get('imgurl')
        download_to_file_field(url, record.upload)
        path = str(record.upload)
        ret = Segmentation.segmentation(path)
        record.seg = ret
        upload_path_1 = '/media/' + str(record.upload)
        seg_path = '/media/' + record.seg + record.sty + record.det
        if not seg_path:
            return render(request, 'home.html')
        record.save()
        return render(request, 'home.html',locals())


def det(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if request.method == 'POST':
        img = request.FILES.get('img')
        if not img:
            return render(request, 'home.html')
        username = request.user.username
        operation = "Detection"
        record = Record.objects.create(upload=img, username=username, operation=operation)
        path = str(record.upload)
        ret = Detection.detection(path)
        record.det = ret
        upload_path_2 = '/media/' + str(record.upload)
        det_path = '/media/' + record.seg + record.sty + record.det
        if not det_path:
            return render(request, 'home.html')
        record.save()
        return render(request, 'home.html', locals())

def deturl(request):
    if not request.user.is_authenticated:
            return redirect('/login/')
    if request.method == 'POST':
        username = request.user.username
        operation = "Detection"
        record = Record.objects.create(username=username, operation=operation)
        url = request.POST.get('imgurl')
        download_to_file_field(url, record.upload)
        path = str(record.upload)
        ret = Detection.detection(path)
        record.det = ret
        upload_path_2 = '/media/' + str(record.upload)
        det_path = '/media/' + record.seg + record.sty + record.det
        if not det_path:
            return render(request, 'home.html')
        record.save()
        return render(request, 'home.html', locals())


def sty(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if request.method == 'POST':
        img = request.FILES.get('img')
        if not img:
            return render(request, 'home.html')
        username = request.user.username
        operation = "StyleTransition"
        record = Record.objects.create(upload=img, username=username, operation=operation)
        path = str(record.upload)
        ret = StyleTransition.styletransition(path)
        record.sty = ret
        upload_path_3 = '/media/' + str(record.upload)
        sty_path = '/media/' + record.seg + record.sty + record.det
        if not sty_path:
            return render(request, 'home.html')
        record.save()
        return render(request, 'home.html', locals())

def styurl(request):
    if not request.user.is_authenticated:
            return redirect('/login/')
    if request.method == 'POST':
        username = request.user.username
        operation = "StyleTransition"
        record = Record.objects.create(username=username, operation=operation)
        url = request.POST.get('imgurl')
        download_to_file_field(url, record.upload)
        path = str(record.upload)
        ret = StyleTransition.styletransition(path)
        record.sty = ret
        upload_path_3 = '/media/' + str(record.upload)
        sty_path = '/media/' + record.seg + record.sty + record.det
        if not sty_path:
            return render(request, 'home.html')
        record.save()
        return render(request, 'home.html', locals())

def delete(request):
    if request.user.is_authenticated:
        if request.method != "POST":
            return JsonResponse({'error': 'require POST'})
        ids = request.POST.get('ids')
        ids_list = ids.split(',')
        print("ids: ", ids_list)
        for ID in ids_list:
            if Record.objects.filter(id=ID):
                record = Record.objects.get(id=ID)          
                record.delete()
        return redirect('/history/')
    else:
        return JsonResponse({'error': 'please login'})




