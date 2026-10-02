# File: mini_insta/admin.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 9/28/2026
# Description: Register profiles, posts, and photos in the admin.

from django.contrib import admin
from .models import Photo, Post, Profile


# Allow sample data to be created and edited through the admin site.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Photo)
