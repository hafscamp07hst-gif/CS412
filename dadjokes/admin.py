# File: dadjokes/admin.py
# Author: Sung Tae Hwang (sthwang@bu.edu), 11/13/2026
# Description: Register jokes and pictures for managing sample data.

from django.contrib import admin
from .models import Joke, Picture


admin.site.register(Joke)
admin.site.register(Picture)
