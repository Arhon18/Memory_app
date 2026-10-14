from .models import FriendRequest

def friend_requests_count(request):
    """Context processor para mostrar en la barra de navegación las solicitudes de amistad pendientes."""
    if request.user.is_authenticated:
        pending_count = FriendRequest.objects.filter(
            receiver=request.user,
            status=FriendRequest.STATUS_PENDING
        ).count()
        return {'pending_friend_requests_count': pending_count}
    return {'pending_friend_requests_count': 0}
