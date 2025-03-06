from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
from django.http import Http404
from .models import *
from .forms import *


class ChatView(LoginRequiredMixin, generic.DetailView):
    model = ChatGroup
    template_name = 'chat/chat.html'
    context_object_name = 'chat_group'

    def get_object(self, queryset=None):
        try:
            chatroom_name = self.kwargs['chatroom_name']
        except:
            chatroom_name = "public-chat"
        
        chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
        if chat_group.is_private and self.request.user not in chat_group.members.all():
            raise Http404()
        return chat_group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chat_group = context['chat_group']
        chat_messages = chat_group.chat_messages.all()[:30]
        form = ChatmessageCreateForm()
        
        other_user = None
        if chat_group.is_private:
            for member in chat_group.members.all():
                if member != self.request.user:
                    other_user = member
                    break
        
        context.update({
            'chat_messages': chat_messages,
            'form': form,
            'other_user': other_user,
            'chatroom_name': chat_group.group_name,
        })
        return context

    def post(self, request, *args, **kwargs):
        chat_group = self.get_object()
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
            if request.htmx:
                return render(request, 'chat/partials/chat_message_p.html', context)
            else:
                return redirect('chatroom', chatroom_name=chat_group.group_name)
        return self.get(request, *args, **kwargs)


class GetOrCreateChatroomView(LoginRequiredMixin, generic.View):
    def get(self, request, username):
        if request.user.username == username:
            return redirect('home')

        other_user = get_object_or_404(User, username=username)
        my_chatrooms = request.user.chat_groups.filter(is_private=True)

        chatroom = None
        for chat in my_chatrooms:
            if other_user in chat.members.all():
                chatroom = chat
                break
        if not chatroom:
            chatroom = ChatGroup.objects.create(is_private=True)
            chatroom.members.add(other_user, request.user)

        return redirect('chatroom', chatroom_name=chatroom.group_name)


class SingUpView(generic.CreateView):
    template_name = "registration/register.html"
    success_url = reverse_lazy('profile_edit')
    form_class = UserCreationForm
