from django.db import models
from django.conf import settings
from django.db.models import Count


class Conversation(models.Model):
    """
    Conversación privada 1 a 1 entre dos amigos.
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conversación Privada'
        verbose_name_plural = 'Conversaciones Privadas'
        ordering = ['-updated_at']

    def __str__(self):
        usernames = ", ".join([str(u) for u in self.participants.all()])
        return f"Chat ({usernames})"

    def get_other_participant(self, user):
        """Obtiene el otro usuario en la conversación."""
        return self.participants.exclude(id=user.id).first()

    @classmethod
    def get_or_create_for_users(cls, user1, user2):
        """Busca o crea una conversación privada única entre dos usuarios."""
        # Buscar conversación existente con exactamente estos 2 participantes
        conversations = cls.objects.annotate(
            num_participants=Count('participants')
        ).filter(
            num_participants=2,
            participants=user1
        ).filter(
            participants=user2
        )

        if conversations.exists():
            return conversations.first(), False
        
        # Crear nueva conversación
        new_conv = cls.objects.create()
        new_conv.participants.add(user1, user2)
        return new_conv, True


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField('Mensaje', blank=True)
    attachment = models.FileField('Archivo Adjunto', upload_to='chat_files/%Y/%m/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['created_at']

    def __str__(self):
        return f"De {self.sender} ({self.created_at.strftime('%H:%M')})"
