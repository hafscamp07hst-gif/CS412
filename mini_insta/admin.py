# File: mini_insta/admin.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Register Mini Insta models for managing sample data.

from django.contrib import admin
from .models import Comment, Follow, Like, Photo, Post, Profile


# Allow sample data to be created and edited through the admin site.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Photo)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(Like)
