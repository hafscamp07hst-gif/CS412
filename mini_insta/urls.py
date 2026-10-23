# File: mini_insta/urls.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Connect profile and post URLs to their views.

from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView
from .views import (
    CreatePostView,
    CreateProfileView,
    DeleteFollowView,
    DeleteLikeView,
    DeletePostView,
    FollowProfileView,
    LikePostView,
    OwnProfileDetailView,
    PostDetailView,
    ProfileDetailView,
    ProfileListView,
    SearchView,
    ShowFeedView,
    ShowFollowersDetailView,
    ShowFollowingDetailView,
    UpdatePostView,
    UpdateProfileView,
)


# Keep these URL names separate from the other applications.
app_name = 'mini_insta'

# Public pages use pk; private profile actions use the signed-in account.
urlpatterns = [
    path('', ProfileListView.as_view(), name='show_all_profiles'),
    path('create_profile', CreateProfileView.as_view(), name='create_profile'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='mini_insta/login.html',
            next_page='mini_insta:show_all_profiles',
        ),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='mini_insta:logout_confirmation'),
        name='logout',
    ),
    path(
        'logout_confirmation/',
        TemplateView.as_view(template_name='mini_insta/logged_out.html'),
        name='logout_confirmation',
    ),
    path('profile/<int:pk>', ProfileDetailView.as_view(), name='show_profile'),
    path('profile/<int:pk>/follow', FollowProfileView.as_view(), name='follow'),
    path('profile/<int:pk>/delete_follow', DeleteFollowView.as_view(),
         name='delete_follow'),
    path('profile', OwnProfileDetailView.as_view(), name='show_own_profile'),
    path(
        'profile/update',
        UpdateProfileView.as_view(),
        name='update_profile',
    ),
    path(
        'profile/<int:pk>/followers',
        ShowFollowersDetailView.as_view(),
        name='show_followers',
    ),
    path(
        'profile/<int:pk>/following',
        ShowFollowingDetailView.as_view(),
        name='show_following',
    ),
    path('profile/search', SearchView.as_view(), name='search'),
    path('profile/feed', ShowFeedView.as_view(), name='show_feed'),
    path('post/<int:pk>', PostDetailView.as_view(), name='show_post'),
    path('post/<int:pk>/like', LikePostView.as_view(), name='like'),
    path('post/<int:pk>/delete_like', DeleteLikeView.as_view(), name='delete_like'),
    path('post/<int:pk>/update', UpdatePostView.as_view(), name='update_post'),
    path('post/<int:pk>/delete', DeletePostView.as_view(), name='delete_post'),
    path(
        'profile/create_post',
        CreatePostView.as_view(),
        name='create_post',
    ),
]
