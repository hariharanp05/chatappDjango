from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RoomForm, MessageForm
from .models import Message

@login_required
def chat_home(request):
    form = RoomForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        room_name = form.cleaned_data['room_name']
        messages.success(request, f"Joined: {room_name}")
        return redirect('chat_room', room_name=room_name)

    return render(request, 'chat/index.html', {'form': form})


@login_required
def chat_room(request, room_name):
    db_messages = Message.objects.filter(room=room_name)

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message_content = form.cleaned_data.get('content')  # Get the content from the form
            file = form.cleaned_data.get('file')

            message = Message(
                username=request.user.username,
                room=room_name,
                message_content=message_content,  # Use the correct field name
                file=file
            )
            message.save()
            return redirect('chat_room', room_name=room_name)
    else:
        form = MessageForm()

    return render(request, 'chat/chatroom.html', {
        'room_name': room_name,
        'title': room_name,
        'db_messages': db_messages,
        'form': form,
    })
