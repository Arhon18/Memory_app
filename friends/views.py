from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.models import User
from .models import FriendRequest


@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    if receiver == request.user:
        messages.warning(request, 'No puedes enviarte una solicitud de amistad a ti mismo.')
        return redirect('accounts:profile', user_id=user_id)

    # Verificar si ya existe relación
    existing = FriendRequest.objects.filter(
        (Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user))
    ).first()

    if existing:
        if existing.status == FriendRequest.STATUS_ACCEPTED:
            messages.info(request, f'Ya eres amigo de {receiver.get_full_name()}.')
        elif existing.status == FriendRequest.STATUS_PENDING:
            if existing.sender == request.user:
                messages.info(request, 'Ya tienes una solicitud pendiente enviada a este usuario.')
            else:
                # El otro ya nos había mandado solicitud -> la aceptamos automáticamente
                existing.status = FriendRequest.STATUS_ACCEPTED
                existing.save()
                messages.success(request, f'¡Ahora tú y {receiver.get_full_name()} son amigos!')
        elif existing.status == FriendRequest.STATUS_REJECTED:
            # Reintentar solicitud
            existing.sender = request.user
            existing.receiver = receiver
            existing.status = FriendRequest.STATUS_PENDING
            existing.save()
            messages.success(request, f'Solicitud de amistad enviada a {receiver.get_full_name()}.')
    else:
        FriendRequest.objects.create(sender=request.user, receiver=receiver, status=FriendRequest.STATUS_PENDING)
        messages.success(request, f'Solicitud de amistad enviada a {receiver.get_full_name()}.')

    next_url = request.META.get('HTTP_REFERER') or redirect('accounts:profile', user_id=user_id).url
    return redirect(next_url)


@login_required
def accept_friend_request(request, request_id):
    req = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status=FriendRequest.STATUS_PENDING)
    req.status = FriendRequest.STATUS_ACCEPTED
    req.save()
    messages.success(request, f'¡Has aceptado la solicitud de amistad de {req.sender.get_full_name()}!')
    next_url = request.META.get('HTTP_REFERER') or redirect('friends:requests').url
    return redirect(next_url)


@login_required
def reject_friend_request(request, request_id):
    req = get_object_or_404(FriendRequest, id=request_id, receiver=request.user, status=FriendRequest.STATUS_PENDING)
    req.status = FriendRequest.STATUS_REJECTED
    req.save()
    messages.info(request, 'Has rechazado la solicitud de amistad.')
    next_url = request.META.get('HTTP_REFERER') or redirect('friends:requests').url
    return redirect(next_url)


@login_required
def cancel_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    req = FriendRequest.objects.filter(sender=request.user, receiver=receiver, status=FriendRequest.STATUS_PENDING).first()
    if req:
        req.delete()
        messages.info(request, 'Solicitud de amistad cancelada.')
    next_url = request.META.get('HTTP_REFERER') or redirect('accounts:profile', user_id=user_id).url
    return redirect(next_url)


@login_required
def remove_friend(request, user_id):
    friend = get_object_or_404(User, id=user_id)
    req = FriendRequest.objects.filter(
        (Q(sender=request.user, receiver=friend) | Q(sender=friend, receiver=request.user)),
        status=FriendRequest.STATUS_ACCEPTED
    ).first()
    if req:
        req.delete()
        messages.info(request, f'Has eliminado a {friend.get_full_name()} de tus amigos.')
    return redirect('accounts:profile', user_id=user_id)


@login_required
def friend_requests_list(request):
    received_requests = FriendRequest.objects.filter(
        receiver=request.user,
        status=FriendRequest.STATUS_PENDING
    ).select_related('sender')

    sent_requests = FriendRequest.objects.filter(
        sender=request.user,
        status=FriendRequest.STATUS_PENDING
    ).select_related('receiver')

    return render(request, 'friends/requests.html', {
        'received_requests': received_requests,
        'sent_requests': sent_requests
    })


@login_required
def friends_list(request, user_id=None):
    target_user = get_object_or_404(User, id=user_id) if user_id else request.user
    
    # Comprobar si puede ver la lista de amigos
    is_self = (request.user == target_user)
    is_friend = FriendRequest.are_friends(request.user, target_user)
    
    if not is_self and not is_friend:
        messages.error(request, 'Debes ser amigo de este usuario para ver su lista de amigos.')
        return redirect('accounts:profile', user_id=target_user.id)

    friends = FriendRequest.get_friends_queryset(target_user)

    return render(request, 'friends/friends_list.html', {
        'target_user': target_user,
        'friends': friends,
        'is_self': is_self
    })


@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=request.user.id)[:20]

        for u in users:
            status = FriendRequest.get_relationship_status(request.user, u)
            results.append({
                'user': u,
                'status': status
            })

    return render(request, 'friends/search.html', {
        'query': query,
        'results': results
    })
