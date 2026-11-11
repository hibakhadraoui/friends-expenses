from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('groups/new/', views.create_group, name='create_group'),
    path('group/', views.group_detail, name='group_detail'),
    path('member/', views.add_member, name='add_member'),
    path('currency/', views.add_currency, name='add_currency'),
    path('expense/', views.add_expense, name='add_expense'),
]
