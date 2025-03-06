from django.urls import path
from .views import *


urlpatterns = [
    path("", ProfileDetailView.as_view(), name="profile"),
    path("edit/", ProfileEditView.as_view(), name="profile_edit"),
]
