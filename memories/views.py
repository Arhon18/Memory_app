from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from .models import Memory, MemoryLike, MemoryComment, Story
from .forms import MemoryCreateForm, MemoryCommentForm, StoryCreateForm
from .geocoding import geocode_location
from friends.models import FriendRequest
from groups.models import MemoryGroup


@login_required
def feed_view(request):
    """
    Feed social: muestra los recuerdos propios, los recuerdos de amigos confirmados
    y recuerdos de grupos a los que pertenece el usuario.
    """
    friends = FriendRequest.get_friends_queryset(request.user)
    user_groups = MemoryGroup.objects.filter(members=request.user)

    # Filtrar recuerdos visibles:
    # 1. Del propio usuario
    # 2. De amigos (recuerdos públicos/personales sin grupo restringido)
    # 3. De los grupos donde el usuario es miembro
    memories = Memory.objects.filter(
        Q(author=request.user) |
        (Q(author__in=friends) & Q(group__isnull=True)) |
        Q(group__in=user_groups)
    ).distinct().select_related('author', 'group').prefetch_related('likes', 'comments', 'tagged_friends', 'comments__author')
    visible_videos = memories.filter(media_type=Memory.TYPE_VIDEO)
    active_stories = Story.objects.filter(
        expires_at__gt=timezone.now(),
        author__in=list(friends) + [request.user],
    ).select_related('author')

    # Identificar IDs de recuerdos a los que el usuario dio like
    user_liked_memory_ids = set(
        MemoryLike.objects.filter(user=request.user, memory__in=memories).values_list('memory_id', flat=True)
    )

    comment_form = MemoryCommentForm()

    context = {
        'memories': memories,
        'user_liked_memory_ids': user_liked_memory_ids,
        'comment_form': comment_form,
        'friends': friends[:5],
        'user_groups': user_groups[:5],
        'active_stories': active_stories,
        'recommended_videos': visible_videos[:6],
        'story_form': StoryCreateForm(),
    }
    return render(request, 'memories/feed.html', context)


@login_required
def create_story_view(request):
    if request.method == 'POST':
        form = StoryCreateForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.expires_at = timezone.now() + timedelta(hours=24)
            story.save()
            messages.success(request, 'Tu historia estará disponible durante 24 horas.')
        else:
            messages.error(request, 'No se pudo publicar la historia. Revisa el archivo seleccionado.')
    return redirect('memories:feed')


@login_required
def story_detail_view(request, story_id):
    story = get_object_or_404(
        Story.objects.select_related('author'),
        id=story_id,
        expires_at__gt=timezone.now(),
    )
    if story.author != request.user and not FriendRequest.are_friends(request.user, story.author):
        messages.error(request, 'Solo los amigos del autor pueden ver esta historia.')
        return redirect('memories:feed')
    return render(request, 'memories/story_detail.html', {'story': story})


@login_required
def create_memory_view(request, group_id=None):
    group = None
    if group_id:
        group = get_object_or_404(MemoryGroup, id=group_id)
        if not group.is_member(request.user):
            messages.error(request, 'Debes ser miembro de este grupo para añadir recuerdos.')
            return redirect('groups:detail', group_id=group.id)

    if request.method == 'POST':
        form = MemoryCreateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            memory = form.save(commit=False)
            memory.author = request.user
            if group:
                memory.group = group
            memory.save()
            coordinates = geocode_location(memory.location)
            if coordinates:
                memory.latitude, memory.longitude = coordinates
                memory.save(update_fields=['latitude', 'longitude'])
            form.save_m2m() # Guarda tagged_friends

            messages.success(request, '¡Tu recuerdo ha sido compartido exitosamente!')
            if group:
                return redirect('groups:detail', group_id=group.id)
            return redirect('memories:feed')
    else:
        form = MemoryCreateForm(user=request.user)

    return render(request, 'memories/create.html', {
        'form': form,
        'group': group
    })


@login_required
def memory_detail_view(request, memory_id):
    memory = get_object_or_404(
        Memory.objects.select_related('author', 'group').prefetch_related(
            'comments__author',
            'comments__replies__author',
            'likes__user',
            'tagged_friends',
        ),
        id=memory_id,
    )
    
    # Comprobar permisos para ver este recuerdo:
    # Si tiene grupo: debe ser miembro
    if memory.group:
        if not memory.group.is_member(request.user):
            messages.error(request, 'Este recuerdo pertenece a un grupo privado.')
            return redirect('memories:feed')
    else:
        # Si no tiene grupo: debe ser el autor o amigo del autor
        if (
            memory.author != request.user
            and not FriendRequest.are_friends(request.user, memory.author)
            and memory.author.profile_privacy != memory.author.PRIVACY_PUBLIC
        ):
            messages.error(request, 'Debes ser amigo del autor para ver este recuerdo.')
            return redirect('accounts:profile', user_id=memory.author.id)

    is_liked = memory.likes.filter(user=request.user).exists()
    comment_form = MemoryCommentForm()

    return render(request, 'memories/detail.html', {
        'memory': memory,
        'is_liked': is_liked,
        'comment_form': comment_form,
        'root_comments': memory.comments.filter(parent__isnull=True),
    })


@login_required
def toggle_like_view(request, memory_id):
    memory = get_object_or_404(Memory, id=memory_id)
    
    # Validar permisos
    if memory.group and not memory.group.is_member(request.user):
        return JsonResponse({'error': 'Sin permiso'}, status=403)
    if not memory.group and memory.author != request.user and not FriendRequest.are_friends(request.user, memory.author):
        return JsonResponse({'error': 'Sin permiso'}, status=403)

    like, created = MemoryLike.objects.get_or_create(memory=memory, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': memory.likes.count()
        })

    next_url = request.META.get('HTTP_REFERER') or redirect('memories:detail', memory_id=memory.id).url
    return redirect(next_url)


@login_required
def add_comment_view(request, memory_id):
    memory = get_object_or_404(Memory, id=memory_id)
    
    # Validar permisos
    if memory.group and not memory.group.is_member(request.user):
        messages.error(request, 'No tienes permiso para comentar en este recuerdo.')
        return redirect('memories:feed')
    if not memory.group and memory.author != request.user and not FriendRequest.are_friends(request.user, memory.author):
        messages.error(request, 'Debes ser amigo del autor para comentar.')
        return redirect('accounts:profile', user_id=memory.author.id)

    if request.method == 'POST':
        form = MemoryCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.memory = memory
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comentario añadido.')

    next_url = request.META.get('HTTP_REFERER') or redirect('memories:detail', memory_id=memory.id).url
    return redirect(next_url)


@login_required
def reply_comment_view(request, memory_id, comment_id):
    memory = get_object_or_404(Memory, id=memory_id)
    parent = get_object_or_404(MemoryComment, id=comment_id, memory=memory)

    if memory.group and not memory.group.is_member(request.user):
        messages.error(request, 'No tienes permiso para responder en este recuerdo.')
        return redirect('memories:feed')
    if not memory.group and memory.author != request.user and not FriendRequest.are_friends(request.user, memory.author):
        messages.error(request, 'Debes ser amigo del autor para responder.')
        return redirect('accounts:profile', user_id=memory.author.id)

    if request.method == 'POST':
        form = MemoryCommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.memory = memory
            reply.author = request.user
            reply.parent = parent
            reply.save()
            messages.success(request, 'Respuesta añadida.')

    next_url = request.META.get('HTTP_REFERER') or redirect('memories:detail', memory_id=memory.id).url
    return redirect(next_url)


@login_required
def delete_memory_view(request, memory_id):
    memory = get_object_or_404(Memory, id=memory_id)
    if memory.author != request.user and not (memory.group and memory.group.is_admin(request.user)):
        messages.error(request, 'No tienes permiso para eliminar este recuerdo.')
        return redirect('memories:feed')

    redirect_to_group = memory.group.id if memory.group else None
    memory.delete()
    messages.info(request, 'Recuerdo eliminado.')

    if redirect_to_group:
        return redirect('groups:detail', group_id=redirect_to_group)
    return redirect('memories:feed')
