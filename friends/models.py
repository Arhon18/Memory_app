from django.db import models
from django.conf import settings
from django.db.models import Q


class FriendRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_ACCEPTED, 'Aceptada'),
        (STATUS_REJECTED, 'Rechazada'),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_friend_requests'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Solicitud de Amistad'
        verbose_name_plural = 'Solicitudes de Amistad'
        unique_together = ('sender', 'receiver')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.get_status_display()})"

    @classmethod
    def are_friends(cls, user1, user2):
        """Verifica si dos usuarios son amigos aceptados."""
        if not user1 or not user2 or user1 == user2:
            return False
        return cls.objects.filter(
            (Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1)),
            status=cls.STATUS_ACCEPTED
        ).exists()

    @classmethod
    def get_relationship_status(cls, user1, user2):
        """
        Devuelve el estado de relación entre user1 y user2 desde la perspectiva de user1:
        'self', 'friends', 'sent_pending', 'received_pending', 'none'
        """
        if user1 == user2:
            return 'self'
        req = cls.objects.filter(
            (Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1))
        ).first()
        if not req:
            return 'none'
        if req.status == cls.STATUS_ACCEPTED:
            return 'friends'
        if req.status == cls.STATUS_PENDING:
            if req.sender == user1:
                return 'sent_pending'
            else:
                return 'received_pending'
        return 'none'

    @classmethod
    def get_friends_queryset(cls, user):
        """Devuelve un QuerySet con los usuarios que son amigos de 'user'."""
        User = user.__class__
        sent = cls.objects.filter(sender=user, status=cls.STATUS_ACCEPTED).values_list('receiver_id', flat=True)
        received = cls.objects.filter(receiver=user, status=cls.STATUS_ACCEPTED).values_list('sender_id', flat=True)
        friend_ids = set(sent).union(set(received))
        return User.objects.filter(id__in=friend_ids)


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.follower} sigue a {self.following}'
