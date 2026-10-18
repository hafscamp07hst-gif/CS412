# File: mini_insta/urls.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Connect profile and post URLs to their views.

from django.urls import path
from .views import (
    CreatePostView,
    DeletePostView,
    PostDetailView,
    ProfileDetailView,
    ProfileListView,
    UpdatePostView,
    UpdateProfileView,
)


# Keep these URL names separate from the other applications.
app_name = 'mini_insta'

# Use pk to select the profile or post for each view.
urlpatterns = [
    path('', ProfileListView.as_view(), name='show_all_profiles'),
    path('profile/<int:pk>', ProfileDetailView.as_view(), name='show_profile'),
    path(
        'profile/<int:pk>/update',
        UpdateProfileView.as_view(),
        name='update_profile',
    ),
    path('post/<int:pk>', PostDetailView.as_view(), name='show_post'),
    path('post/<int:pk>/update', UpdatePostView.as_view(), name='update_post'),
    path('post/<int:pk>/delete', DeletePostView.as_view(), name='delete_post'),
    path(
        'profile/<int:pk>/create_post',
        CreatePostView.as_view(),
        name='create_post',
    ),
]
