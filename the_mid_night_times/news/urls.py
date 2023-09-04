
from django.contrib import admin
from django.urls import path
from news import views


urlpatterns = [
    path('', views.news, name='news'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('history/',views.history,name='history'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),


]
