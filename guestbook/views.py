from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from guestbook.models import Guestbook


def deleteform(request):

    return render(request,'guestbook/deleteform.html')


def list(request):
    guestbooklist= Guestbook.objects.all().order_by('-id')

    data = {
        'guestbooklist':guestbooklist
    }

    return render(request,'guestbook/list.html',data)


def add(request):
    guestbook = Guestbook()
    guestbook.name = request.POST['name']
    guestbook.contents = request.POST['contents']
    guestbook.password = request.POST['password']

    guestbook.save()

    return HttpResponseRedirect('/guestbook/')


def deleteform(request,guestbook_id):

    data = {
        'id':guestbook_id
    }

    return render(request, 'guestbook/deleteform.html',data)


def delete(request):
    guestbook =  Guestbook.objects.get(id=request.POST['delid'])
    guestbook.password == request.POST['inputpw']  and guestbook.delete()
    return HttpResponseRedirect('/guestbook/')
