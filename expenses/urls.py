from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('groups/new/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/member/new/', views.add_member, name='add_member'),
    path('groups/<int:group_id>/currency/new/', views.add_currency, name='add_currency'),
    path('groups/<int:group_id>/expense/new/', views.add_expense, name='add_expense'),
]
