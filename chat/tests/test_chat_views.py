import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import Http404
from chat.models import ChatGroup, GroupMessage


@pytest.mark.django_db
class TestChatView:
    # tworzymy środowisko
    @pytest.fixture
    def setup_users_and_chatrooms(self, client):
        user1 = User.objects.create_user(username='user1', password='password')
        user2 = User.objects.create_user(username='user2', password='password')

        chat_group_public = ChatGroup.objects.create(group_name='public-chat')
        chat_group_private = ChatGroup.objects.create(group_name='private-chat', is_private=True)
        chat_group_private.members.add(user1, user2)

        GroupMessage.objects.create(author=user1, group=chat_group_public, text="Hello from user1")
        GroupMessage.objects.create(author=user2, group=chat_group_public, text="Hello from user2")

        return client, user1, user2, chat_group_public, chat_group_private

    def test_chat_view_public_chat(self, setup_users_and_chatrooms):
        client, user1, _, chat_group_public, _ = setup_users_and_chatrooms
        url = reverse('chatroom', kwargs={'chatroom_name': 'public-chat'})

        client.login(username='user1', password='password')
        response = client.get(url)

        assert response.status_code == 200
        assert "Hello from user1" in response.content.decode()
        assert "Hello from user2" in response.content.decode()

    def test_message_redirect_on_success(self, setup_users_and_chatrooms):
        client, user1, _, chat_group_public, _ = setup_users_and_chatrooms
        url = reverse('chatroom', kwargs={'chatroom_name': 'public-chat'})

        # Login and post a message, check for redirect
        client.login(username='user1', password='password')
        response = client.post(url, {'text': 'New message from user1'})
        assert response.status_code == 302
        assert response.url == url
