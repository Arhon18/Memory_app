from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MemoryGroup, GroupMembership
from .forms import MemoryGroupForm, AddGroupMemberForm
from memories.models import Memory


@login_required
def group_list_view(request):
    groups = request.user.memory_groups.all().prefetch_related('members', 'memories')
    return render(request, 'groups/list.html', {'groups': groups})


@login_required
def create_group_view(request):
    if request.method == 'POST':
        form = MemoryGroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            # Añadir al creador como admin
            GroupMembership.objects.create(group=group, user=request.user, role=GroupMembership.ROLE_ADMIN)
            messages.success(request, f'¡Grupo "{group.name}" creado con éxito! Ahora puedes invitar a tus amigos.')
            return redirect('groups:detail', group_id=group.id)
    else:
        form = MemoryGroupForm()

    return render(request, 'groups/create.html', {'form': form})


@login_required
def group_detail_view(request, group_id):
    group = get_object_or_404(MemoryGroup.objects.prefetch_related('members', 'memberships__user'), id=group_id)
    
    if not group.is_member(request.user):
        messages.error(request, 'No tienes acceso a este grupo. Pídele a un miembro que te agregue.')
        return redirect('groups:list')

    # Recuerdos subidos por cualquier miembro del grupo
    memories = group.memories.all().select_related('author').prefetch_related('likes', 'comments')
    memberships = group.memberships.select_related('user')
    is_admin = group.is_admin(request.user)
    add_member_form = AddGroupMemberForm(user=request.user, group=group)

    context = {
        'group': group,
        'memories': memories,
        'memberships': memberships,
        'is_admin': is_admin,
        'add_member_form': add_member_form,
    }
    return render(request, 'groups/detail.html', context)


@login_required
def add_member_view(request, group_id):
    group = get_object_or_404(MemoryGroup, id=group_id)
    if not group.is_member(request.user):
        messages.error(request, 'No eres miembro de este grupo.')
        return redirect('groups:list')

    if request.method == 'POST':
        form = AddGroupMemberForm(request.POST, user=request.user, group=group)
        if form.is_valid():
            selected_friends = form.cleaned_data['friends']
            for friend in selected_friends:
                GroupMembership.objects.get_or_create(group=group, user=friend, defaults={'role': GroupMembership.ROLE_MEMBER})
            messages.success(request, f'{len(selected_friends)} amigos agregados al grupo.')
        else:
            messages.error(request, 'Error al agregar amigos.')

    return redirect('groups:detail', group_id=group.id)


@login_required
def leave_group_view(request, group_id):
    group = get_object_or_404(MemoryGroup, id=group_id)
    membership = GroupMembership.objects.filter(group=group, user=request.user).first()
    
    if membership:
        # Si es el único admin y creador y quedan otros miembros, se previene o se transfiere
        if group.creator == request.user and group.members.count() > 1:
            messages.warning(request, 'Como creador del grupo, asigna a otro administrador antes de salir.')
            return redirect('groups:detail', group_id=group.id)
        membership.delete()
        messages.info(request, f'Has salido del grupo {group.name}.')

    return redirect('groups:list')
