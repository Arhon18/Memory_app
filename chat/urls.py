from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('with/<int:user_id>/', views.start_or_open_chat, name='start_chat'),
    path('<int:conversation_id>/', views.conversation_view, name='conversation'),
]
