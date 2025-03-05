from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.chat_view, name="home"),
    path('chat/<username>', views.get_or_create_chatroom, name="start-chat"),
    path('chat/room/<chatroom_name>', views.chat_view, name="chatroom"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.SingUpView.as_view(), name='register'),
]
