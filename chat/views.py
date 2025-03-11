from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic, View
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

        if chat_group.groupchat_name and self.request.user not in chat_group.members.all():
            chat_group.members.add(self.request.user)

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
            'chat_group': chat_group,
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


class GetOrCreateChatroomView(LoginRequiredMixin, View):
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


class CreateGroupChatView(View):
    template_name = "chat/create_groupchat.html"

    def get(self, request):
        form = NewGroupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = NewGroupForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect('chatroom', new_groupchat.group_name)
        
        return render(request, self.template_name, {'form': form})


class ChatroomEditView(generic.FormView):
    template_name = 'chat/chatroom_edit.html'
    form_class = ChatroomEditForm

    def dispatch(self, request, *args, **kwargs):
        self.chat_group = get_object_or_404(ChatGroup, group_name=self.kwargs['chatroom_name'])
        if request.user != self.chat_group.admin:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.chat_group
        return kwargs

    def form_valid(self, form):
        form.save()
        remove_members = self.request.POST.getlist('remove_members')
        for member_id in remove_members:
            member = User.objects.get(id=member_id)
            self.chat_group.members.remove(member)
        return redirect('chatroom', self.chat_group.group_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_group'] = self.chat_group
        return context


class ChatroomDeleteView(generic.DeleteView):
    model = ChatGroup
    template_name = 'chat/chatroom_delete.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        chat_group = get_object_or_404(ChatGroup, group_name=self.kwargs['chatroom_name'])
        if self.request.user != chat_group.admin:
            raise Http404()
        return chat_group
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_group'] = self.get_object()
        return context


def chatroom_leave_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()
    
    if request.user == chat_group.admin:
        chat_group.delete()
    else:
        chat_group.members.remove(request.user)
    
    return redirect('home')


class SingUpView(generic.CreateView):
    template_name = "registration/register.html"
    success_url = reverse_lazy('profile_edit')
    form_class = UserCreationForm
