# File: mini_insta/urls.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Connect profile and post URLs to their views.

from django.urls import path
from .views import PostDetailView, ProfileDetailView, ProfileListView


# Keep these URL names separate from the other applications.
app_name = 'mini_insta'

# Use pk to select the profile or post shown by each detail view.
urlpatterns = [
    path('', ProfileListView.as_view(), name='show_all_profiles'),
    path('profile/<int:pk>', ProfileDetailView.as_view(), name='show_profile'),
    path('post/<int:pk>', PostDetailView.as_view(), name='show_post'),
]
