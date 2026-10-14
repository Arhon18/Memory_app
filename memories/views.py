from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Memory, MemoryLike, MemoryComment
from .forms import MemoryCreateForm, MemoryCommentForm
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
    }
    return render(request, 'memories/feed.html', context)


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
    memory = get_object_or_404(Memory.objects.select_related('author', 'group').prefetch_related('comments__author', 'likes__user', 'tagged_friends'), id=memory_id)
    
    # Comprobar permisos para ver este recuerdo:
    # Si tiene grupo: debe ser miembro
    if memory.group:
        if not memory.group.is_member(request.user):
            messages.error(request, 'Este recuerdo pertenece a un grupo privado.')
            return redirect('memories:feed')
    else:
        # Si no tiene grupo: debe ser el autor o amigo del autor
        if memory.author != request.user and not FriendRequest.are_friends(request.user, memory.author):
            messages.error(request, 'Debes ser amigo del autor para ver este recuerdo.')
            return redirect('accounts:profile', user_id=memory.author.id)

    is_liked = memory.likes.filter(user=request.user).exists()
    comment_form = MemoryCommentForm()

    return render(request, 'memories/detail.html', {
        'memory': memory,
        'is_liked': is_liked,
        'comment_form': comment_form,
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
