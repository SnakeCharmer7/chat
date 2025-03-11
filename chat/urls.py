from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.ChatView.as_view(), name="home"),
    path('chat/<username>', views.GetOrCreateChatroomView.as_view(), name="start-chat"),
    path('chat/room/<chatroom_name>', views.ChatView.as_view(), name="chatroom"),
    path('chat/new_groupchat/', views.CreateGroupChatView.as_view(), name="new_groupchat"),
    path('chat/edit/<chatroom_name>', views.ChatroomEditView.as_view(), name="edit_chatroom"),
    path('chat/delete/<chatroom_name>', views.ChatroomDeleteView.as_view(), name="delete_chatroom"),
    path('chat/leave/<chatroom_name>', views.chatroom_leave_view, name="leave_chatroom"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.SingUpView.as_view(), name='register'),
]
