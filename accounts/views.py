from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import RegisterForm, LoginForm, ProfileEditForm
from friends.models import FriendRequest
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
    can_view_content = is_self or is_friend
    user_memories = []
    
    if can_view_content:
        user_memories = Memory.objects.filter(author=profile_user, group__isnull=True).select_related('author').prefetch_related('likes', 'comments')

    context = {
        'profile_user': profile_user,
        'is_self': is_self,
        'is_friend': is_friend,
        'relationship_status': relationship_status,
        'friends': friends[:6],
        'friends_count': friends_count,
        'can_view_content': can_view_content,
        'memories': user_memories,
        'memories_count': Memory.objects.filter(author=profile_user).count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil se ha actualizado correctamente.')
            return redirect('accounts:profile', user_id=request.user.id)
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})
