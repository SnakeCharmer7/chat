from django.shortcuts import get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import Profile
from .forms import ProfileForm


class ProfileDetailView(generic.DetailView):
    model = Profile
    template_name = 'users/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        if self.kwargs.get('username'):
            return get_object_or_404(User, username=self.kwargs['username'])
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object.profile
        return context


class ProfileEditView(LoginRequiredMixin, generic.UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'users/profile_edit.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user.profile 
        return kwargs

    def get_success_url(self):
        return reverse_lazy('profile')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
