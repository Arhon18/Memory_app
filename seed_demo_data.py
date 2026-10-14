"""
Script para inicializar datos de prueba en la base de datos local de Memory App.
Crea 2 usuarios amigos entre sí, 1 usuario no amigo (para probar el bloqueo de perfil privado),
un grupo colaborativo y un recuerdo de prueba.
"""

import os
import django
from django.core.files.base import ContentFile
import io
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memory_project.settings')
django.setup()

from accounts.models import User
from friends.models import FriendRequest
from memories.models import Memory
from groups.models import MemoryGroup, GroupMembership


def create_dummy_image(name='memory.jpg', color=(99, 102, 241)):
    """Crea una imagen válida en memoria para pruebas."""
    file = io.BytesIO()
    image = Image.new('RGB', (800, 600), color=color)
    image.save(file, 'JPEG')
    file.seek(0)
    return ContentFile(file.read(), name=name)


def run():
    print("Iniciando creación de datos de demostración...")

    # 1. Crear Usuario Principal
    user1, created = User.objects.get_or_create(
        email='usuario@memory.com',
        defaults={
            'first_name': 'Lucas',
            'last_name': 'Silva',
            'bio': 'Amante de la fotografía, viajes y los momentos con amigos ✨',
        }
    )
    if created:
        user1.set_password('Memory123!')
        user1.save()
        print(f"Usuario 1 creado: {user1.email} / Clave: Memory123!")

    # 2. Crear Amigo (Camila)
    user2, created = User.objects.get_or_create(
        email='camila@memory.com',
        defaults={
            'first_name': 'Camila',
            'last_name': 'Rojas',
            'bio': 'Coleccionando recuerdos felices 📸',
        }
    )
    if created:
        user2.set_password('Memory123!')
        user2.save()
        print(f"Usuario 2 creado: {user2.email} / Clave: Memory123!")

    # 3. Crear Usuario No Amigo (Ignacio)
    user3, created = User.objects.get_or_create(
        email='ignacio@memory.com',
        defaults={
            'first_name': 'Ignacio',
            'last_name': 'Gómez',
            'bio': 'Programador y aventurero.',
        }
    )
    if created:
        user3.set_password('Memory123!')
        user3.save()
        print(f"Usuario 3 (No amigo para probar privacidad): {user3.email} / Clave: Memory123!")

    # 4. Establecer amistad entre Lucas y Camila
    FriendRequest.objects.get_or_create(
        sender=user1,
        receiver=user2,
        defaults={'status': FriendRequest.STATUS_ACCEPTED}
    )

    # 5. Crear Grupo Colaborativo
    group, created = MemoryGroup.objects.get_or_create(
        name='Viaje al Sur 2026',
        defaults={
            'description': 'Fotos y momentos épicos de nuestras vacaciones juntos 🌲🏔️',
            'creator': user1,
        }
    )
    if created:
        GroupMembership.objects.get_or_create(group=group, user=user1, defaults={'role': 'admin'})
        GroupMembership.objects.get_or_create(group=group, user=user2, defaults={'role': 'member'})
        print(f"Grupo colaborativo creado: {group.name}")

    # 6. Crear recuerdos de ejemplo con imágenes reales generadas
    if not Memory.objects.filter(author=user1).exists():
        mem1 = Memory.objects.create(
            author=user1,
            title='Atardecer en la montaña',
            description='Un atardecer inolvidable con la mejor compañía.',
            location='Cordillera de los Andes',
            file=create_dummy_image('atardecer.jpg', color=(244, 63, 94))
        )
        mem1.tagged_friends.add(user2)
        print(f"Recuerdo creado: {mem1.title}")

    if not Memory.objects.filter(group=group).exists():
        mem2 = Memory.objects.create(
            author=user2,
            group=group,
            title='Llegando a la cabaña',
            description='¡Por fin llegamos después de horas de viaje! Aquí comienza lo bueno.',
            location='Pucón, Chile',
            file=create_dummy_image('cabana.jpg', color=(16, 185, 129))
        )
        print(f"Recuerdo grupal creado: {mem2.title}")

    print("\n[OK] Datos de prueba creados exitosamente.")
    print("Credenciales de prueba:")
    print(" - Email: usuario@memory.com | Clave: Memory123!")
    print(" - Email: camila@memory.com  | Clave: Memory123!")
    print(" - Email: ignacio@memory.com | Clave: Memory123! (Perfil privado)")

if __name__ == '__main__':
    run()
