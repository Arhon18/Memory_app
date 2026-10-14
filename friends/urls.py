from django.urls import path
from . import views

app_name = 'friends'

urlpatterns = [
    path('requests/', views.friend_requests_list, name='requests'),
    path('request/send/<int:user_id>/', views.send_friend_request, name='send_request'),
    path('request/accept/<int:request_id>/', views.accept_friend_request, name='accept_request'),
    path('request/reject/<int:request_id>/', views.reject_friend_request, name='reject_request'),
    path('request/cancel/<int:user_id>/', views.cancel_friend_request, name='cancel_request'),
    path('remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
    path('list/', views.friends_list, name='my_friends'),
    path('list/<int:user_id>/', views.friends_list, name='user_friends'),
    path('search/', views.search_users, name='search'),
]
