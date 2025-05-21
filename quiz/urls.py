from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('get_questions/', views.get_questions, name='get_questions'),
    path('get_wrong_questions/', views.get_wrong_questions, name='get_wrong_questions'),
    path('save_wrong_question/', views.save_wrong_question, name='save_wrong_question'),
    path('record_attempt/', views.record_attempt, name='record_attempt'),
    path('clear_data/', views.clear_user_data, name='clear_data'),
]