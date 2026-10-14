from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import RegisterForm, LoginForm, ProfileEditForm
from friends.models import FriendRequest, Follow
from memories.models import Memory


def register_view(request):
    if request.user.is_authenticated:
        return redirect('memories:feed')

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido a Memory, {user.first_name}! Tu cuenta ha sido creada exitosamente.')
            return redirect('memories:feed')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('memories:feed')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            next_url = request.GET.get('next', 'memories:feed')
            messages.success(request, f'¡Hola de nuevo, {user.first_name}!')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('accounts:login')


@login_required
def profile_view(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    is_self = (request.user == profile_user)
    
    # Comprobar estado de amistad
    relationship_status = FriendRequest.get_relationship_status(request.user, profile_user)
    is_friend = (relationship_status == 'friends')
    
    # Amigos del usuario
    friends = FriendRequest.get_friends_queryset(profile_user)
    friends_count = friends.count()

    # Si es el propio usuario o es amigo, ve los recuerdos
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    can_view_content = is_self or is_friend or profile_user.profile_privacy == User.PRIVACY_PUBLIC
    user_memories = []
    
    if can_view_content:
        user_memories = Memory.objects.filter(author=profile_user, group__isnull=True).select_related('author').prefetch_related('likes', 'comments')
    map_memories = [
        {
            'id': memory.id,
            'title': memory.title or 'Recuerdo',
            'location': memory.location,
            'latitude': float(memory.latitude),
            'longitude': float(memory.longitude),
        }
        for memory in user_memories
        if memory.location and memory.latitude is not None and memory.longitude is not None
    ]
    memories_without_coordinates = [
        memory for memory in user_memories
        if memory.location and (memory.latitude is None or memory.longitude is None)
    ]

    context = {
        'profile_user': profile_user,
        'is_self': is_self,
        'is_friend': is_friend,
        'is_following': is_following,
        'profile_is_public': profile_user.profile_privacy == User.PRIVACY_PUBLIC,
        'relationship_status': relationship_status,
        'friends': friends[:6],
        'friends_count': friends_count,
        'can_view_content': can_view_content,
        'memories': user_memories,
        'memories_count': Memory.objects.filter(author=profile_user).count(),
        'map_memories': map_memories,
        'memories_without_coordinates': memories_without_coordinates,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil se ha actualizado correctamente.')
            return redirect('accounts:settings')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def account_settings_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tus datos de cuenta se actualizaron correctamente.')
            return redirect('accounts:settings')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'accounts/settings.html', {'form': form})
