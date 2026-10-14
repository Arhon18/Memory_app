from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import User
from friends.models import FriendRequest
from .models import Conversation, Message


@login_required
def inbox_view(request):
    """Bandeja de entrada de chats privados."""
    user_conversations = request.user.conversations.all().prefetch_related('participants', 'messages')
    
    # Lista de amigos para poder iniciar un nuevo chat rápido
    friends = FriendRequest.get_friends_queryset(request.user)

    # Añadir metadata a cada conversación
    conversation_data = []
    for conv in user_conversations:
        other_user = conv.get_other_participant(request.user)
        last_message = conv.messages.last()
        unread_count = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
        conversation_data.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })

    return render(request, 'chat/inbox.html', {
        'conversation_data': conversation_data,
        'friends': friends
    })


@login_required
def start_or_open_chat(request, user_id):
    """Inicia o abre el chat privado con un amigo."""
    other_user = get_object_or_404(User, id=user_id)

    # Validar que sean amigos para poder chatear en privado
    if not FriendRequest.are_friends(request.user, other_user):
        messages.error(request, f'Debes ser amigo de {other_user.get_full_name()} para enviarle mensajes privados.')
        return redirect('accounts:profile', user_id=other_user.id)

    conversation, _ = Conversation.get_or_create_for_users(request.user, other_user)
    return redirect('chat:conversation', conversation_id=conversation.id)


@login_required
def conversation_view(request, conversation_id):
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related('participants', 'messages__sender'),
        id=conversation_id
    )

    # Verificar que el usuario sea participante
    if not conversation.participants.filter(id=request.user.id).exists():
        messages.error(request, 'No tienes acceso a esta conversación.')
        return redirect('chat:inbox')

    other_user = conversation.get_other_participant(request.user)

    # Marcar mensajes del otro usuario como leídos
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        attachment = request.FILES.get('attachment')

        if content or attachment:
            msg = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
                attachment=attachment
            )
            conversation.save() # actualiza updated_at

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'ok',
                    'message_id': msg.id,
                    'content': msg.content,
                    'created_at': msg.created_at.strftime('%H:%M'),
                    'sender_name': msg.sender.first_name,
                    'attachment_url': msg.attachment.url if msg.attachment else None
                })
            return redirect('chat:conversation', conversation_id=conversation.id)

    messages_list = conversation.messages.all()

    # Si es petición AJAX de refresco de mensajes
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get('poll') == '1':
        data = [{
            'id': m.id,
            'sender_id': m.sender_id,
            'sender_name': m.sender.first_name,
            'content': m.content,
            'attachment_url': m.attachment.url if m.attachment else None,
            'created_at': m.created_at.strftime('%H:%M'),
            'is_me': (m.sender_id == request.user.id)
        } for m in messages_list]
        return JsonResponse({'messages': data})

    return render(request, 'chat/conversation.html', {
        'conversation': conversation,
        'other_user': other_user,
        'messages_list': messages_list
    })
