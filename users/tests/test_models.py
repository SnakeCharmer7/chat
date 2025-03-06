import pytest
from model_bakery import baker
from users.models import Profile
from django.contrib.auth.models import User
from django.templatetags.static import static


@pytest.mark.django_db
def test_profile_creation():
    user = baker.make(User)
    Profile.objects.filter(user=user).delete()  # Usuń automatyczny profil
    profile = baker.make(Profile, user=user, displayname="Janek", bio="Testowy bio")
    
    assert profile.user == user
    assert profile.displayname == "Janek"
    assert profile.bio == "Testowy bio"

@pytest.mark.django_db
def test_profile_name_with_displayname():
    user = baker.make(User)
    Profile.objects.filter(user=user).delete()
    profile = baker.make(Profile, user=user, displayname="JanekTest")

    assert profile.name == "JanekTest"

@pytest.mark.django_db
def test_profile_name_without_displayname():
    user = baker.make(User, username="testuser")
    Profile.objects.filter(user=user).delete()
    profile = baker.make(Profile, user=user, displayname=None)

    assert profile.name == user.username

@pytest.mark.django_db
def test_avatar_without_image():
    user = baker.make(User)
    Profile.objects.filter(user=user).delete()
    profile = baker.make(Profile, user=user, image=None)

    expected_avatar = static('images/avatar.svg')
    assert profile.avatar == expected_avatar
