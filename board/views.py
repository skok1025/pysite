from django.db.models import F
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from board.models import Board
from user.models import User
import math

list_size = 5
page_size = 5


def no_auth_redirect(request, user_id='0'):

    try:
        print(request.session['authuser'])

        if user_id != request.session['authuser']['id']:
            raise KeyError

    except KeyError:
        return HttpResponseRedirect('/board/list')



def list(request):
    boards = Board.objects.all()

    currentpage = int(1 if request.GET.get('currentpage') is None else request.GET.get('currentpage'))

    totalcount = boards.count()
    pagecount = math.ceil(totalcount/list_size)
    blockcount = math.ceil(pagecount/page_size)
    currentblock = math.ceil(currentpage/page_size)

    if currentpage > pagecount:
        currentpage = pagecount
        currentblock = math.ceil(currentpage/page_size)

    if currentpage < 1:
        currentpage = 1
        currentblock = 1

    beginpage = 1 if currentblock ==1 else (currentblock-1)*page_size + 1
    prevpage =(currentblock-1) if currentblock > 1 else 0
    nextpage = currentblock*page_size+1 if currentblock < blockcount else 0
    endpage = beginpage-1+list_size if nextpage > 0 else pagecount
    start = (currentpage - 1) * page_size

    boardlist = Board.objects.all().order_by('-groupno','-orderno')[start:start + page_size]
    type(range(1,4))
    data = {
        'boardlist':boardlist,
        'totalcount':totalcount,
        'listsize':list_size,
        'currentpage':currentpage,
        'beginpage':beginpage,
        'endpage':endpage,
        'prevpage':prevpage,
        'nextpage':nextpage,
        'rangelist':range(beginpage,beginpage+list_size)
    }

    return render(request,'board/list.html',data)


def modify(request,board_id):
    board = Board.objects.get(id=board_id)
    data = {
        'board': board
    }
    return render(request,'board/modify.html',data)


def update(request):
    board = Board.objects.get(id=request.POST['id'])

    board.title = request.POST['title']
    board.content = request.POST['content']
    board.save()

    return HttpResponseRedirect('/board/list')


def view(request,board_id):
    board = Board.objects.get(id=board_id)
    Board.objects.filter(id=board_id).update(hit = F('hit')+1)
    data = {
        'board':board
    }
    return render(request,'board/view.html',data)


def writeform(request):
    replyno =0 if request.GET.get('replyno') is None else request.GET.get('replyno')

    no_auth_redirect(request)

    data = {
        'replyno': replyno
    }
    return render(request,'board/write.html',data)


def write(request):
    user = User.objects.get(id=request.session['authuser']['id'])
    board = Board()
    board.user = user
    board.title = request.POST['title']
    board.content = request.POST['content']
    print('-------------',request.POST['replyno'])
    if int(request.POST['replyno']) != 0:
        # 답글인 경우
        originboard = Board.objects.get(id=request.POST['replyno'])
        Board.objects\
            .filter(groupno=originboard.groupno)\
            .filter(orderno__gte=originboard.orderno)\
            .update(orderno=F('orderno')+1)
        board.groupno = originboard.groupno
        board.orderno = originboard.orderno
        board.depth = originboard.depth + 1
    board.save()

    return HttpResponseRedirect('/board/list')


def delete(request,board_id):
    board = Board.objects.get(id=board_id)
    print("delete: ",board.user.id)
    no_auth_redirect(request,board.user.id)

    if request.session['authuser'] == model_to_dict(board.user):
        board.isexist = 0
        board.save()

    return HttpResponseRedirect('/board/list')
