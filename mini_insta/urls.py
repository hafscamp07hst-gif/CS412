# File: mini_insta/urls.py
# Name: Sung Tae Hwang
# BU Email: sthwang@bu.edu
# Description: Connect the profile list and detail URLs to their views.

from django.urls import path
from .views import ProfileListView, ProfileDetailView

urlpatterns = [
    path('', ProfileListView.as_view(), name='show_all_profiles'),
    path('profile/<int:pk>', ProfileDetailView.as_view(), name='show_profile'),
]
