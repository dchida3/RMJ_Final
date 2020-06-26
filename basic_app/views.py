





from django.shortcuts import render
from basic_app.forms import UserForm,UserProfileInfoForm,DeleteForm,EditForm,AddForm,SearchForm,PollForm,EditPollForm,ChoiceForm

# Create your views here.
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from basic_app.models import UserProfileInfo,Company,Position,Review,DeleteID,EditID,AddID,Poll,Choice,Vote

from django.db.models import Count
from django.db import connection
from django.views.generic import View
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
import datetime



# from django.views.generic import CreateView
# try:
#     from django.core.urlresolvers import reverse_lazy
# except ImportError:
#     from django.urls import reverse
#     from django.utils.functional import lazy
#     reverse_lazy = lambda *args, **kwargs: lazy(reverse, str)(*args, **kwargs)

from basic_app import forms
from django.contrib.postgres.search import SearchVector

cursor=connection.cursor()

# def post_list(request):
#     # object_list = page.all()
#     # paginator = Paginator(object_list, 8) # 3 posts in each page
#
#     page = request.GET.get('page')
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer deliver the first page
#         posts = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range deliver last page of results
#         posts = paginator.page(paginator.num_pages)
#     return render(request,
#                   'basic_app/search_company.html',
#                   {'page': page,
#                    'posts': posts})

def index(request):
     cur=connection.cursor()
     cur.execute('''select c.name, round(avg(to_number(r.overall_ratings,'99999999999999999D99')),0),round(avg(to_number(r.work_balance_stars,'99999999999999999D99')),0),round(avg(to_number(r.culture_values_stars,'99999999999999999D99')),0),round(avg(to_number(r.career_opportunities_stars,'99999999999999999D99')),0),round(avg(to_number(r.company_benefit_stars,'99999999999999999D99')),0),round(avg(to_number(r.senior_management_stars,'99999999999999999D99')),0)'''+
'from basic_app_review r join basic_app_company c on r.cid_id=c.cid '+
'''where r.overall_ratings not in ('none') and r.work_balance_stars not in ('none') and r.culture_values_stars not in ('none') and r.career_opportunities_stars not in ('none') and r.company_benefit_stars not in ('none') and r.senior_management_stars not in ('none')'''+
'group by c.name')
     arr=cur.fetchall()

     return render(request,'basic_app/index.html',{'arr':arr})

@login_required
def special(request):
    return HttpResponse("You are logged in, Nice!")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    registered = False
    if request.method=="POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        #valid
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request,'basic_app/registration.html',
            {'user_form':user_form,'profile_form':profile_form,
            'registered':registered})


def search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            results = Review.objects.annotate(
                    search=SearchVector('summary', 'pros','cons','advices_to_management'),
                    ).filter(search=query)

    return render(request,
                  'basic_app/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})

def search_company(request):
    companyname = request.POST.get('companyname')
    cur=connection.cursor()
    cur.execute('select * '+
                'from basic_app_review r join basic_app_company c on r.cid_id=c.cid join basic_app_position p on p.pid =r.pid_id '+
                'where c.name=%s ORDER BY r.helpful_count DESC',[companyname])

    cur_review_info=cur.fetchall()


    return render(request,'basic_app/search_company.html',{"cur_review_info":cur_review_info})

def software_engineer(request):

    cur=connection.cursor()
    cur.execute('select * '+
                'from basic_app_review r join basic_app_company c on r.cid_id=c.cid join basic_app_position p on p.pid =r.pid_id '+
                'where p.title like %s ORDER BY r.helpful_count DESC',['%Software%'])

    arr=cur.fetchall()

    cur_dict = {"cur_review_info":arr}

    return render(request,'basic_app/software_engineer.html',context=cur_dict)

def intern(request):

    cur=connection.cursor()
    cur.execute('select * '+
                'from basic_app_review r join basic_app_company c on r.cid_id=c.cid join basic_app_position p on p.pid =r.pid_id '+
                'where p.title like %s ORDER BY r.helpful_count DESC',['%Intern%'])

    arr=cur.fetchall()

    cur_dict = {"cur_review_info":arr}

    return render(request,'basic_app/intern.html',context=cur_dict)

def cloud(request):

    cur=connection.cursor()
    cur.execute('select * '+
                'from basic_app_review r join basic_app_company c on r.cid_id=c.cid join basic_app_position p on p.pid =r.pid_id '+
                'where p.title like %s ORDER BY r.helpful_count DESC',['%Cloud%'])

    arr=cur.fetchall()

    cur_dict = {"cur_review_info":arr}

    return render(request,'basic_app/cloud.html',context=cur_dict)

def network(request):

    cur=connection.cursor()
    cur.execute('select * '+
                'from basic_app_review r join basic_app_company c on r.cid_id=c.cid join basic_app_position p on p.pid =r.pid_id '+
                'where p.title like %s ORDER BY r.helpful_count DESC',['%Network%'])

    arr=cur.fetchall()

    cur_dict = {"cur_review_info":arr}

    return render(request,'basic_app/network.html',context=cur_dict)

def hardware(request):

    cur=connection.cursor()
    cur.execute('select * '+
                'from basic_app_review r join basic_app_company c on r.cid_id=c.cid join basic_app_position p on p.pid =r.pid_id '+
                'where p.title like %s ORDER BY r.helpful_count DESC',['%Hardware%'])

    arr=cur.fetchall()

    cur_dict = {"cur_review_info":arr}

    return render(request,'basic_app/hardware.html',context=cur_dict)

def web(request):

    cur=connection.cursor()
    cur.execute('select * '+
                'from basic_app_review r join basic_app_company c on r.cid_id=c.cid join basic_app_position p on p.pid =r.pid_id '+
                'where p.title like %s ORDER BY r.helpful_count DESC',['%Web%'])

    arr=cur.fetchall()

    cur_dict = {"cur_review_info":arr}

    return render(request,'basic_app/web.html',context=cur_dict)

def data(request):

    cur=connection.cursor()
    cur.execute('select * '+
                'from basic_app_review r join basic_app_company c on r.cid_id=c.cid join basic_app_position p on p.pid =r.pid_id '+
                'where p.title like %s ORDER BY r.helpful_count DESC',['%Data%'])

    arr=cur.fetchall()

    cur_dict = {"cur_review_info":arr}

    return render(request,'basic_app/data.html',context=cur_dict)

def review(request):
    return render(request,'basic_app/review.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")
        else:
            print("Someone tried to login and failed")
            print("Username: {} and password: {}".format(username,password))
            return HttpResponse("invalid login details supplied")
    else:
        return render(request,'basic_app/login.html',{})


def add_helpful(request,rid):
    rid=request.POST['choice']

    cur=connection.cursor()
    cur.execute('UPDATE basic_app_review SET helpful_count+=1 WHERE rid=%s',[rid])

    return render(request,'basic_app/add_helpful.html')




'''
    pass Review and corresponding Position and Company information
    into single object to be transferred to template
'''
class Cur_review_info():
    def __init__(self,Review,Position,Company):
        self.Review = Review
        self.Position = Position
        self.Company = Company

@login_required
def manage_review(request):

    if request.user.is_authenticated:
        cur_userid = request.user.id #raw userid
        cur_userprofileid = cur_userid - 6

    cur=connection.cursor()
    cur.execute('select r.rid,c.name,c.country,c.state,c.city,ap.title,r.summary '+
                'from basic_app_review r join basic_app_company c on r.cid_id=c.cid '+
                'join basic_app_position ap on ap.pid=r.pid_id '+
                 'where r.uid_id =%s',[request.user.id])
    arr=cur.fetchall()
    cur_dict = {"cur_review_info":arr}

    return render(request,'basic_app/managereview.html',context=cur_dict)

@login_required
def delete_review(request):
    if request.method=="POST":
        delete_form = DeleteForm(data=request.POST)
        #valid
        aaa = delete_form.save()
        this_rid = aaa.did;
        print(this_rid)
        cur=connection.cursor()
        cur.execute('DELETE from basic_app_review WHERE rid=%s',[this_rid] )

        #Review.objects.filter(rid=this_rid).delete()

    else:
        delete_form = DeleteForm()
    return render(request,'basic_app/delete.html',
            {'delete_form':delete_form})


@login_required
def edit_review(request):
    if request.method=="POST":
        edit_form = EditForm(data=request.POST)
        #valid
        aaa = edit_form.save()
        this_rid = aaa.eid;
        this_summary = aaa.summary;
        print(this_rid)
        print(this_summary)

        cur=connection.cursor()
        cur.execute('UPDATE basic_app_review SET summary =%s WHERE rid=%s',[this_summary,this_rid] )


    else:
        edit_form = EditForm()
    return render(request,'basic_app/edit.html',
            {'edit_form':edit_form})


@login_required
def add_review(request):
    if request.method=="POST":
        add_form = AddForm(data=request.POST)
        #valid
        aaa = add_form.save()
        new_company = Company(aaa.cid,aaa.name,aaa.country,aaa.state,aaa.city)
        new_company.save()

        print("adddinnngngggg")
    else:
        add_form = AddForm()
    return render(request,'basic_app/add.html',
            {'add_form':add_form})

@login_required
def polls_list(request):
    polls=Poll.objects.all()

    paginator = Paginator(polls, 5)

    page = request.GET.get('page')
    polls = paginator.get_page(page)

    return render(request, 'basic_app/polls_list.html',{'polls':polls})

@login_required
def poll_detail(request, poll_id):
    """
    Render the poll_detail.html template which allows a user to vote
    on the choices of a poll
    """
    # poll = Poll.objects.get(id=poll_id)
    poll = get_object_or_404(Poll, id=poll_id)
    user_can_vote = poll.user_can_vote(request.user)
    results = poll.get_results_dict()
    context = {'poll': poll, 'user_can_vote': user_can_vote, 'results': results}
    return render(request, 'basic_app/poll_detail.html', context)

@login_required
def poll_vote(request, poll_id):

    poll = get_object_or_404(Poll, id=poll_id)

    if not poll.user_can_vote(request.user):
        messages.error(request, 'You have already voted on this poll')
        return redirect('basic_app:poll_detail', poll_id=poll_id)

    choice_id = request.POST.get('choice')
    if choice_id:
        choice = Choice.objects.get(id=choice_id)
        new_vote = Vote(user=request.user, poll=poll, choice=choice)
        new_vote.save()
    else:
        messages.error(request, 'No Choice Was Found!')
        return redirect('basic_app:poll_detail', poll_id=poll_id)

    return redirect('basic_app:poll_detail', poll_id=poll_id)


@login_required
def add_poll(request):
    if request.method == "POST":
        form = PollForm(request.POST)
        if form.is_valid():
            new_poll = form.save(commit=False)
            new_poll.pub_date = datetime.datetime.now()
            new_poll.owner = request.user
            new_poll.save()
            new_choice1 = Choice(
                                    poll = new_poll,
                                    choice_text=form.cleaned_data['choice1']
                                ).save()
            new_choice2 = Choice(
                                    poll = new_poll,
                                    choice_text=form.cleaned_data['choice2']
                                ).save()
            messages.success(
                            request,
                            'Poll and Choices added!',
                            extra_tags='alert alert-success alert-dismissible fade show'
                            )
            return redirect('basic_app:polls_list')
    else:
        form = PollForm()
    context = {'form': form}
    return render(request, 'basic_app/add_poll.html', context)
