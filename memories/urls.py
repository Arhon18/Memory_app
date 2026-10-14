from django.urls import path
from . import views

app_name = 'memories'

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('create/', views.create_memory_view, name='create'),
    path('create/group/<int:group_id>/', views.create_memory_view, name='create_group_memory'),
    path('<int:memory_id>/', views.memory_detail_view, name='detail'),
    path('<int:memory_id>/like/', views.toggle_like_view, name='like'),
    path('<int:memory_id>/comment/', views.add_comment_view, name='comment'),
    path('<int:memory_id>/delete/', views.delete_memory_view, name='delete'),
]
