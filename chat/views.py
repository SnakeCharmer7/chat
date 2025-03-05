from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.urls import reverse_lazy
from .models import *
from .forms import *


@login_required
def chat_view(request):
    chat_group = get_object_or_404(ChatGroup, group_name="public-chat")
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatmessageCreateForm()

    if request.htmx:
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {
                'message': message,
                'user': request.user
            }
            return render(request, 'chat/partials/chat_message_p.html', context)

    return render(request, "chat/chat.html", {'chat_messages': chat_messages, 'form': form})


class SingUpView(generic.CreateView):
    template_name = "registration/register.html"
    success_url = reverse_lazy('profile_edit')
    form_class = UserCreationForm
