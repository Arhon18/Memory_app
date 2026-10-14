from django.contrib import admin
from .models import Memory, MemoryComment, MemoryLike, Story

admin.site.register([Memory, MemoryComment, MemoryLike, Story])
