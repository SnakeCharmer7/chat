import pytest
from model_bakery import baker
from chat.models import ChatGroup, GroupMessage
from django.contrib.auth.models import User
from django.utils import timezone


@pytest.mark.django_db
def test_create_chat_group():
    group = baker.make(ChatGroup)
    
    assert group.pk is not None
    assert group.group_name is not None
    assert ChatGroup.objects.count() == 1

@pytest.mark.django_db
def test_create_chat_group_with_users():
    user1 = baker.make(User)
    user2 = baker.make(User)

    group = baker.make(ChatGroup)

    group.members.add(user1, user2)
    group.save()

    assert group.members.count() == 2
    assert user1 in group.members.all()
    assert user2 in group.members.all()

@pytest.mark.django_db
def test_user_online_in_group():
    user1 = baker.make(User)
    user2 = baker.make(User)

    group = baker.make(ChatGroup)

    group.users_online.add(user1)
    group.users_online.add(user2)

    assert user1 in group.users_online.all()
    assert user2 in group.users_online.all()

@pytest.mark.django_db
def test_create_group_message():
    user = baker.make(User)
    group = baker.make(ChatGroup)

    message = baker.make(GroupMessage, group=group, author=user)

    assert message.pk is not None
    assert message.group == group
    assert message.author == user
    assert message.text is not None

@pytest.mark.django_db
def test_group_message_ordering():
    user = baker.make(User)
    group = baker.make(ChatGroup)

    message1 = baker.make(GroupMessage, group=group, author=user, created=timezone.make_aware(timezone.datetime(2025, 1, 1, 0, 0, 0)))
    message2 = baker.make(GroupMessage, group=group, author=user, created=timezone.make_aware(timezone.datetime(2025, 1, 2, 0, 0, 0)))

    messages = group.chat_messages.all()
    assert messages.first() == message2
    assert messages.last() == message1
