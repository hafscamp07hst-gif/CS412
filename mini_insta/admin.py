# File: mini_insta/admin.py
# Name: Sung Tae Hwang
# BU Email: sthwang@bu.edu
# Description: Make profiles available in the Django admin application.

from django.contrib import admin
from .models import Profile

admin.site.register(Profile)
