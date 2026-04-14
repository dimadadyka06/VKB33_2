from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('users/', views.user_list, name='user_list'),
    path('users/<str:username>/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('friend/request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('friend/accept/<str:username>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend/remove/<str:username>/', views.remove_friend, name='remove_friend'),
    path('friend/requests/', views.incoming_requests, name='incoming_requests'),
]
