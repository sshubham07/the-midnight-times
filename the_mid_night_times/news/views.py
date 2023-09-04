from django.shortcuts import render,redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
import requests
from .forms import SignupForm
from django.contrib.auth.forms import AuthenticationForm
from . models import *
from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from collections import Counter
import json

# Create your views here.
def make_history(user,q):
    """
    Create or update a search history record for a user.

    This function checks if a search history record for the given user and keyword 'q' already exists.
    If a record exists, it updates the timestamp to the current time.
    If no record exists, it creates a new history record with the user and keyword 'q'.

    :param user: The user for whom the search history is being created or updated.
    :type user: User (or equivalent) object
    :param q: The keyword or search query for which the history is being recorded.
    :type q: str
    """
    try:
        history = History.objects.get(user=user,keyword = q)
        history.timestamp = datetime.now()
        history.save()
    except Exception as e:
        history = History(user = user, keyword = q)
        history.save()
def check_last_query(user,query):
    try:
        history = History.objects.get(user=user,keyword = query)
        current_time = timezone.now()
        time_difference = current_time - history.timestamp
        fifteen_minutes = timedelta(minutes=15)
        return time_difference > fifteen_minutes
    except Exception:
        return True      
           

@login_required(login_url="signup")
def news(request):
    """
    View function for displaying news articles based on user input.

    This view handles news search functionality. It checks if the user is blocked, and if so,
    logs them out and redirects to the signup page with an error message. Otherwise, it processes
    the user's search query and fetches news articles from an external API. It also records the search
    query in the user's search history.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A rendered HTML page displaying news articles or an error message.
    :rtype: HttpResponse
    """
    user = Block.objects.get(name = request.user)
    if user.blocked:
        logout(request)
        messages.error(request, " The User has been blocked, try some another's account")
        return redirect('signup')
    q = request.GET.get('q').lower() if request.GET.get('q') !=None else ''
    if q!='':
        last_search =check_last_query(request.user,q)
        if last_search == False:
            messages.error(request, f"Keyword {q} was searched less than 15 minutes ago. Please wait for some more mintutes to search again")
            return render(request, 'news/home.html',{'news':{},'value':q,'last_search':False})
        #url = f"https://newsapi.org/v2/everything?q={q}&pageSize=4&from=2023-08-01&sortBy=publishedAt&apiKey=1089494e1d3d4f56a29235cfd149fa84"
        url = f"http://api.mediastack.com/v1/news?access_key=82c1ab2cd5a7db2c4839b65e67464e7a&keywords={q}"

        make_history(request.user,q)
        response = requests.get(url).json()
        print(f'RESPONSE==={response}')
        if(response.get('data') is None):
            messages.error(request,f"Could Not Find News on {q}")
            context = {'news' : {},'value':q,'last_search':True}
            return render(request, 'news/home.html',context)   
        response['data'] = sorted(response['data'], key=lambda x: x['published_at'], reverse=True)
        
        context = {'news' : response['data'],'value':q,'last_search':True}
    else:
        context ={'news':{},'value':'','last_search':True}
    return render(request, 'news/home.html',context)

def signup(request):
    """
    View function for user registration.

    This view handles the user registration process. It displays a signup form and processes user input.
    If the submitted form is valid, a new user is created, and they are automatically logged in. 
    If there are any form validation errors, an error message is displayed.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A rendered HTML page for user registration.
    :rtype: HttpResponse
    """
    form = SignupForm()
    if request.method=="POST":
        form=SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            block_instance = Block(name=user )
            block_instance.save()
            login(request, user)
            return redirect('news')
        else:
            messages.error(request, "An error occuured during registeration")
    return render(request, 'news/login_signup.html',{"form":form})

def login_view(request):
    """
    View function for user login.

    This view handles the user login process. It displays a login form and processes user input.
    If the submitted form is valid, the user is logged in and redirected to the news page.
    If there are any form validation errors, the login form is displayed with error messages.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A rendered HTML page for user login.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('news')
    form = AuthenticationForm()
    return render(request,'news/login.html',{'form':form})

def logout_view(request):
    """
    View function for user logout.

    This view handles user logout. It logs out the currently authenticated user and redirects them to the news page.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A redirection to the news page after logout.
    :rtype: HttpResponse
    """
    logout(request)
    return redirect('news')

@login_required(login_url="signup")
def history(request):
    """
    View function for displaying user search history.

    This view displays the search history of the currently authenticated user.
    It retrieves the search history records ordered by timestamp and passes them to the 'history.html' template for rendering.
    If no match in history is found, empty disct is sent.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A rendered HTML page displaying the user's search history.
    :rtype: HttpResponse
    """
    context = {'history':{}}
    try:
        history = History.objects.filter(user=request.user).order_by('-timestamp')
        context = {'history':history}
        return render(request,'news/history.html',context)
    except Exception as e:
        return render(request,'news/history.html',context)
    
@login_required(login_url="signup")
def admin_dashboard(request):
    """
    View function for the admin dashboard.

    This view is intended for administrators to view statistics related to user search history.
    It checks if the current user is a staff member (admin) and, if not, redirects them to the signup page with an error message.
    It retrieves all search history records, extracts keywords, and counts the frequency of each keyword.
    The word counts are then converted to JSON format and passed to the 'admin_dashboard.html' template for rendering.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A rendered HTML page displaying statistics on user search history.
    :rtype: HttpResponse
    """

    if not request.user.is_staff:
        messages.error(request,"You must be an admin to view this page")
        return redirect('signup')
    history_objects = History.objects.all()
    keywords = [obj.keyword for obj in history_objects]
    word_counts = Counter(keywords)
    word_counts = json.dumps(word_counts)
    return render(request,'news/admin_dashboard.html',{'word_counts':word_counts})



    
        
        
    
