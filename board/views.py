from django.db.models import F, Max
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from board.models import Board
from user.models import User
import math

list_size = 5  # 페이징 리스트 수
page_size = 5  # 한 페이지의 게시물 수


def no_auth_redirect(request, user_id='0'):
    try:
        if user_id != request.session['authuser']['id']:
            raise KeyError

    except KeyError:
        return HttpResponseRedirect('/board/list')


def list(request):
    currentpage = int(1 if request.GET.get('currentpage') is None else request.GET.get('currentpage'))
    kwd = '' if request.GET.get('kwd') is None else request.GET.get('kwd')
    boards = Board.objects.filter(title__icontains = kwd)

    totalcount = boards.count()
    pagecount = math.ceil(totalcount/page_size)
    print('-----------',totalcount)

    if currentpage > pagecount:
        currentpage = pagecount

    if currentpage < 1:
        currentpage = 1

    list_num = math.ceil(currentpage / list_size) # 페이지 리스트 인덱스
    beginpage = list_size*list_num - list_size+1 # 첫번째 페이지번호
    nextpage = 1 + list_size * list_num # 현재 페이지 리스트의 다음 페이지 (다음 페이지 리스트의 첫번째 페이지)
    prevpage = 1 if list_num == 1 else nextpage - list_size - 1
    endpage = math.ceil(totalcount/page_size) # 마지막 페이지
    start = (currentpage - 1) * page_size # 시작 컨텐츠 인덱스
    print(totalcount,page_size,endpage)
    boardlist = Board.objects.filter(title__icontains = kwd).order_by('-groupno','-orderno')[start:start + page_size]
    type(range(1,4))
    data = {
        'boardlist':boardlist,
        'currentpage':currentpage,
        'endpage':endpage,
        'prevpage':prevpage,
        'nextpage':nextpage,
        'rangelist':range(beginpage,beginpage+list_size),
        'kwd':kwd
    }

    return render(request,'board/list.html',data)


def modify(request,board_id):

    board = Board.objects.get(id=board_id)

    try:
        if board.user.id != request.session['authuser']['id']:
            raise KeyError

    except KeyError:
        return HttpResponseRedirect('/board/list')

    
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
    if 'authuser' in request.session.keys():
        pass
    else:
        return HttpResponseRedirect('/board/list')

    replyno =0 if request.GET.get('replyno') is None else request.GET.get('replyno')



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

    else:
        insert_groupno = Board.objects.aggregate(groupno=Max('groupno'))['groupno'] + 1
        print(insert_groupno,type(insert_groupno))
        board.groupno = insert_groupno

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
