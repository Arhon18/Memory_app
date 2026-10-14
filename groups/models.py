from django.db import models
from django.conf import settings


class MemoryGroup(models.Model):
    """
    Grupo o álbum colaborativo donde varios amigos comparten fotos y videos juntos.
    """
    name = models.CharField('Nombre del Grupo', max_length=150)
    description = models.TextField('Descripción o Propósito', blank=True, max_length=400)
    cover_image = models.ImageField('Portada del Grupo', upload_to='group_covers/', blank=True, null=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_memory_groups'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='GroupMembership',
        related_name='memory_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Grupo de Recuerdos'
        verbose_name_plural = 'Grupos de Recuerdos'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def cover_url(self):
        if self.cover_image and hasattr(self.cover_image, 'url'):
            return self.cover_image.url
        return "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=800&q=80"

    def is_member(self, user):
        return self.members.filter(id=user.id).exists()

    def is_admin(self, user):
        return self.creator == user or self.memberships.filter(user=user, role=GroupMembership.ROLE_ADMIN).exists()


class GroupMembership(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_MEMBER = 'member'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrador'),
        (ROLE_MEMBER, 'Miembro'),
    ]

    group = models.ForeignKey(MemoryGroup, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Membresía de Grupo'
        verbose_name_plural = 'Membresías de Grupo'
        unique_together = ('group', 'user')

    def __str__(self):
        return f"{self.user} en {self.group.name} ({self.get_role_display()})"
