from django import forms
from .models import Memory, MemoryComment, Story
from friends.models import FriendRequest


class MemoryCreateForm(forms.ModelForm):
    class Meta:
        model = Memory
        fields = ['title', 'description', 'file', 'location', 'tagged_friends']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej. Tarde de playa con amigos'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': '¿Qué hizo especial este momento?'}),
            'file': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*,video/*',
                'capture': 'environment',
            }),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej. Viña del Mar, Chile'}),
            'tagged_friends': forms.SelectMultiple(attrs={
                'class': 'form-select friend-selector',
                'size': 6,
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Solo permitir etiquetar a amigos confirmados
            self.fields['tagged_friends'].queryset = FriendRequest.get_friends_queryset(user)
            self.fields['tagged_friends'].label = 'Etiquetar Amigos'
            self.fields['tagged_friends'].required = False


class MemoryCommentForm(forms.ModelForm):
    class Meta:
        model = MemoryComment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-input comment-input',
                'placeholder': 'Escribe un recuerdo o comentario...',
                'autocomplete': 'off'
            })
        }
        labels = {
            'content': ''
        }


class StoryCreateForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['file', 'caption']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*,video/*',
                'capture': 'environment',
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Agrega un texto a tu historia (opcional)',
            }),
        }
