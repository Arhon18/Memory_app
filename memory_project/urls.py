from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('memories:feed') if request.user.is_authenticated else redirect('accounts:login'), name='root'),
    path('accounts/', include('accounts.urls')),
    path('friends/', include('friends.urls')),
    path('memories/', include('memories.urls')),
    path('groups/', include('groups.urls')),
    path('chat/', include('chat.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
