from django.contrib import admin
from .models import GroupMembership, MemoryGroup

admin.site.register([MemoryGroup, GroupMembership])
