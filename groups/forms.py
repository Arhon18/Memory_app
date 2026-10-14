from django import forms
from .models import MemoryGroup
from friends.models import FriendRequest


class MemoryGroupForm(forms.ModelForm):
    class Meta:
        model = MemoryGroup
        fields = ['name', 'description', 'cover_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej. Viaje al Sur 2026, Amigos de la U'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describe este grupo o álbum de recuerdos compartido...'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
        }


class AddGroupMemberForm(forms.Form):
    friends = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        label='Selecciona Amigos para Agregar'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        group = kwargs.pop('group')
        super().__init__(*args, **kwargs)
        # Amigos del usuario que aún no están en el grupo
        user_friends = FriendRequest.get_friends_queryset(user)
        existing_members = group.members.all()
        self.fields['friends'].queryset = user_friends.exclude(id__in=existing_members.values_list('id', flat=True))
