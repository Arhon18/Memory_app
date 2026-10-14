import os
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone


def memory_media_upload_path(instance, filename):
    return f"memories/user_{instance.author_id}/{filename}"


class Memory(models.Model):
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_CHOICES = [
        (TYPE_IMAGE, 'Foto'),
        (TYPE_VIDEO, 'Video'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memories'
    )
    title = models.CharField('Título o Momento', max_length=200, blank=True)
    description = models.TextField('Historia o Descripción', blank=True)
    file = models.FileField('Foto o Video', upload_to=memory_media_upload_path)
    media_type = models.CharField('Tipo de Archivo', max_length=10, choices=TYPE_CHOICES, default=TYPE_IMAGE)
    
    # Amigos etiquetados en el recuerdo
    tagged_friends = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='tagged_in_memories',
        blank=True
    )
    
    # Si pertenece a un grupo / álbum colaborativo
    group = models.ForeignKey(
        'groups.MemoryGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='memories'
    )
    
    location = models.CharField('Lugar', max_length=150, blank=True)
    latitude = models.DecimalField('Latitud', max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField('Longitud', max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Recuerdo'
        verbose_name_plural = 'Recuerdos'
        ordering = ['-created_at']

    def __str__(self):
        title_str = self.title if self.title else f"Recuerdo #{self.id}"
        return f"{title_str} por {self.author}"

    def save(self, *args, **kwargs):
        # Auto-detectar si es video o foto por la extensión
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext in ['.mp4', '.mov', '.avi', '.webm', '.mkv']:
                self.media_type = self.TYPE_VIDEO
            else:
                self.media_type = self.TYPE_IMAGE
        super().save(*args, **kwargs)

    @property
    def is_video(self):
        return self.media_type == self.TYPE_VIDEO

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()


def story_media_upload_path(instance, filename):
    return f"stories/user_{instance.author_id}/{filename}"


class Story(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stories'
    )
    file = models.FileField('Foto o Video', upload_to=story_media_upload_path)
    caption = models.CharField('Texto', max_length=180, blank=True)
    media_type = models.CharField(max_length=10, choices=Memory.TYPE_CHOICES, default=Memory.TYPE_IMAGE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Historia'
        verbose_name_plural = 'Historias'

    def save(self, *args, **kwargs):
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            self.media_type = Memory.TYPE_VIDEO if ext in ['.mp4', '.mov', '.avi', '.webm', '.mkv'] else Memory.TYPE_IMAGE
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_video(self):
        return self.media_type == Memory.TYPE_VIDEO


class MemoryLike(models.Model):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memory_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Me gusta'
        verbose_name_plural = 'Me gusta'
        unique_together = ('memory', 'user')

    def __str__(self):
        return f"{self.user} le gustó {self.memory_id}"


class MemoryComment(models.Model):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memory_comments')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
    )
    content = models.TextField('Comentario', max_length=600)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['created_at']

    def __str__(self):
        return f"Comentario de {self.author} en {self.memory_id}"
