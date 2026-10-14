from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Manager para CustomUser donde el email es el identificador único."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Modelo de usuario personalizado con email único como identificador de inicio de sesión.
    """
    username = None
    email = models.EmailField('Correo Electrónico', unique=True)
    first_name = models.CharField('Nombre', max_length=100)
    last_name = models.CharField('Apellido', max_length=100)
    bio = models.TextField('Biografía', max_length=300, blank=True)
    avatar = models.ImageField('Foto de Perfil', upload_to='avatars/', blank=True, null=True)
    cover_image = models.ImageField('Portada', upload_to='covers/', blank=True, null=True)
    birth_date = models.DateField('Fecha de Nacimiento', blank=True, null=True)
    PRIVACY_PRIVATE = 'private'
    PRIVACY_PUBLIC = 'public'
    PRIVACY_CHOICES = [
        (PRIVACY_PRIVATE, 'Perfil privado'),
        (PRIVACY_PUBLIC, 'Perfil público'),
    ]
    profile_privacy = models.CharField(
        'Privacidad del perfil',
        max_length=10,
        choices=PRIVACY_CHOICES,
        default=PRIVACY_PRIVATE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.email.split('@')[0]

    @property
    def display_name(self):
        return self.get_full_name()

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        # Avatar predeterminado elegante generado con iniciales
        initials = (self.first_name[:1] + self.last_name[:1]).upper() or self.email[:2].upper()
        return f"https://ui-avatars.com/api/?name={initials}&background=6366f1&color=ffffff&bold=true&size=128"
