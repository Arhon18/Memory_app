from django.urls import path
from . import views

app_name = 'memories'

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('create/', views.create_memory_view, name='create'),
    path('stories/create/', views.create_story_view, name='create_story'),
    path('stories/<int:story_id>/', views.story_detail_view, name='story_detail'),
    path('create/group/<int:group_id>/', views.create_memory_view, name='create_group_memory'),
    path('<int:memory_id>/', views.memory_detail_view, name='detail'),
    path('<int:memory_id>/like/', views.toggle_like_view, name='like'),
    path('<int:memory_id>/comment/', views.add_comment_view, name='comment'),
    path('<int:memory_id>/comment/<int:comment_id>/reply/', views.reply_comment_view, name='reply_comment'),
    path('<int:memory_id>/delete/', views.delete_memory_view, name='delete'),
]
